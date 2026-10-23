#!/usr/bin/env python3
"""Render official NeoRacer geometry in the page layout, without running Unity."""
import argparse
import base64
import functools
import hashlib
import http.server
import json
import math
import os
from pathlib import Path
import re
import struct
import subprocess
import tempfile
import threading
import time

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "upstream/preview-assets"


def materials():
    directory = ASSETS / "autodrive/Assets/Models/Vehicle/NeoRacer"
    by_guid = {}
    for path in (directory / "Materials").glob("*.mat"):
        guid = re.search(r"guid: (\w+)", path.with_suffix(".mat.meta").read_text())[1]
        text = path.read_text()
        color = re.search(r"_BaseColor: \{r: ([^,]+), g: ([^,]+), b: ([^,]+),", text)
        by_guid[guid] = {
            "color": [float(v) for v in color.groups()],
            "metallic": float(re.search(r"_Metallic: ([^\n]+)", text)[1]),
            "smoothness": float(re.search(r"_Smoothness: ([^\n]+)", text)[1]),
        }
    result = {}
    for name, guid in re.findall(r"name: ([^\n]+)\n    second: \{fileID: 2100000, guid: (\w+)", (directory / "NeoRacer.fbx.meta").read_text()):
        if guid in by_guid:
            result[re.sub(r"[^a-z0-9]", "", name.lower())] = by_guid[guid]
    return result


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe", action="store_true")
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument("--fps", type=int, default=6)
    args = parser.parse_args()
    if not 1 <= args.fps <= 30:
        parser.error("Frame rate must be between 1 and 30.")
    if "gilbreth" in str(ROOT) and not os.environ.get("SLURM_JOB_ID"):
        parser.error("Use Slurm for browser rendering and media encoding on Gilbreth.")
    if os.environ.get("SLURM_JOB_PARTITION", "") not in ("", "a100-40gb", "a30"):
        parser.error("Use an allowed A100-40GB or A30 allocation.")
    lock = json.loads((ROOT / "configs/preview-assets.lock.json").read_text())
    for entry in lock["assets"]:
        data = (ASSETS / entry["path"]).read_bytes()
        assert hashlib.sha256(data).hexdigest() == entry["sha256"], entry["path"]
    work = ROOT / "runtime/neoracer-preview"
    work.mkdir(parents=True, exist_ok=True)
    frame_directory = Path(tempfile.mkdtemp(prefix="capture-", dir=work))
    (ROOT / "runtime/neoracer-materials.json").write_text(json.dumps(materials()))
    # The pinned FBX stores this double correctly, but FBXLoader r180 exposes NaN.
    # Read the exact binary property rather than silently assuming centimeters.
    fbx = (ASSETS / "autodrive/Assets/Models/Vehicle/NeoRacer/NeoRacer.fbx").read_bytes()
    marker = (b'S\x0f\x00\x00\x00UnitScaleFactorS\x06\x00\x00\x00double'
              b'S\x06\x00\x00\x00NumberS\x00\x00\x00\x00D')
    offset = fbx.index(marker) + len(marker)
    centimeters_per_unit = struct.unpack('<d', fbx[offset:offset + 8])[0]
    assert centimeters_per_unit == 2.54
    (ROOT / "runtime/neoracer-model-settings.json").write_text(json.dumps({
        "centimetersPerUnit": centimeters_per_unit, "metersPerUnit": centimeters_per_unit / 100,
        "sourceUpAxis": "+Y",
    }))
    html = (ROOT / "tracr_demo/static/index.html").read_text()
    html = html.replace('/static/style.css', '/tracr_demo/static/style.css')
    html = html.replace('<script src="/static/app.js"></script>', '''
<script type="importmap">{"imports":{"three":"/upstream/preview-assets/three/build/three.module.js"}}</script>
<script type="module" src="/scripts/preview/neoracer.js"></script>''')
    html = html.replace('</head>', '''<style>
header{height:76px}main{padding-top:24px}.intro{gap:16px}#notice{margin:18px 0}
.panel-head{height:50px;padding:0 16px}.panel-foot{padding:12px 16px}
.metrics{padding:19px 0;margin-top:20px}.metrics>div{padding:0 18px}
.metrics strong{font-size:22px}footer{padding:21px 0}button:disabled{opacity:1;cursor:default}
</style></head>''')
    (work / "index.html").write_text(html)
    handler = functools.partial(QuietHandler, directory=str(ROOT))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    errors, console = [], []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, args=["--disable-dev-shm-usage", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
            page = browser.new_page(viewport={"width": 1200, "height": 1000})
            page.on("pageerror", lambda error: (errors.append(str(error)), print("Browser error:", error, flush=True)))
            page.on("console", lambda event: console.append({"type": event.type, "text": event.text}))
            page.goto(f"http://127.0.0.1:{server.server_port}/runtime/neoracer-preview/index.html")
            page.wait_for_function("window.previewReady !== undefined", timeout=30000)
            page.evaluate("window.previewReady")
            info = page.evaluate("window.modelInfo")
            preview = page.evaluate("window.previewInfo")
            duration = preview["duration"]
            (work / "geometry-validation.json").write_text(json.dumps(preview, indent=2) + "\n")
            plan_page = browser.new_page(viewport={"width":1100,"height":880})
            plan_page.goto(f"http://127.0.0.1:{server.server_port}/docs/media/field-map-plan.svg")
            plan_page.screenshot(path=str(work / "map-plan.png"))
            plan_page.close()
            (work / "model-info.json").write_text(json.dumps(info, indent=2) + "\n")
            height = math.ceil(page.locator("body").bounding_box()["height"])
            clip = {"x": 0, "y": 0, "width": 1200, "height": height}
            output = ROOT / "docs/media"
            stats = None
            if args.probe:
                for index in range(4):
                    stats = page.evaluate("([t,a]) => window.renderFrame(t,a)", [0, index * math.pi / 2])
                    page.screenshot(path=str(work / f"probe-{index}.png"), clip=clip)
            else:
                overview = page.evaluate("window.renderMap()")
                (output / "field-map-overview.png").write_bytes(base64.b64decode(overview.split(",",1)[1]))
                started = time.monotonic()
                for index in range(duration * args.fps):
                    stats = page.evaluate("t => window.renderFrame(t)", index / args.fps)
                    page.screenshot(path=str(frame_directory / f"frame-{index:04d}.png"), clip=clip)
                    if index == round((preview["stages"][1]["start"] + 1) * args.fps):
                        page.screenshot(path=str(output / "neoracer-preview.png"), clip=clip)
                    if index % 20 == 0:
                        print(f"Captured {index + 1}/{duration * args.fps} frames in {time.monotonic() - started:.1f}s", flush=True)
            assert not errors, errors
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            assert page.locator('#mode').inner_text() == '3D MODEL PREVIEW'
            assert 'No physical video or Unity execution' in page.locator('#notice').inner_text()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        (work / "console.json").write_text(json.dumps({"errors": errors, "console": console}, indent=2) + "\n")
    print(json.dumps({k: v for k, v in info.items() if k != "meshes"}, indent=2), flush=True)
    print(json.dumps(stats), flush=True)
    if args.probe:
        return
    subprocess.run([
        args.ffmpeg, "-hide_banner", "-loglevel", "warning", "-y", "-threads", "2", "-filter_complex_threads", "1",
        "-framerate", str(args.fps), "-i", str(frame_directory / "frame-%04d.png"),
        "-filter_complex", "split[a][b];[a]palettegen=max_colors=256:stats_mode=full[p];[b][p]paletteuse=dither=bayer:bayer_scale=3:diff_mode=rectangle",
        "-loop", "0", str(output / "neoracer-preview.gif"),
    ], check=True)
    report = {
        "kind": "official_neoracer_geometry_preview", "autodrive_commit": lock["autodrive_commit"],
        "mesh": "Assets/Models/Vehicle/NeoRacer/NeoRacer.fbx", "renderer": "Three.js r180 / Chromium SwiftShader WebGL",
        "unity_executed": False, "physical_footage": False, "live_bridge_exercised": False,
        "vehicle_dynamics_simulated": False, "path": "Scripted outer-lane pass with stops at S2 and S6", "map_measured": False,
        "material_conversion": "Unity base color, metallic and smoothness mapped to WebGL; not shader-identical",
        "camera_calibrated": False, "fps": args.fps, "frames": duration * args.fps, "duration_seconds": duration,
        "map": "configs/map.photo-v1.geometry.json", "geometry_checks": preview,
        "size": [1200, height], "size_meters": info["sizeMeters"], "mesh_count": info["meshCount"],
        "source_units": "inches", "meters_per_source_unit": centimeters_per_unit / 100,
        "source_forward_vector": info["sourceForward"], "aligned_forward_vector": info["alignedForward"],
        "preview_forward_axis": "+Z", "alignment_method": "Rear-to-front axle geometry centers",
        "unmatched_materials": info["unmatchedMaterials"], "render_stats": stats,
        "javascript_errors": errors, "horizontal_overflow": False,
        "slurm_job_id": os.environ.get("SLURM_JOB_ID"), "partition": os.environ.get("SLURM_JOB_PARTITION"), "artifacts": {},
    }
    for name in ["neoracer-preview.png", "neoracer-preview.gif", "field-map-overview.png", "field-map-plan.svg"]:
        data = (output / name).read_bytes()
        report["artifacts"][name] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    (output / "neoracer-preview.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    main()
