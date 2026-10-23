#!/usr/bin/env python3
"""Capture the real UI layout with explicitly labeled, recorded Nigel images.

This documentation renderer does not run the bridge or simulate live inputs.
Requires Playwright/Chromium and FFmpeg. Run through Slurm on Gilbreth.
"""
import argparse
import base64
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
PHASES = {
    "INITIALIZING": "Starting",
    "APPROACH_RED": "Approach red",
    "WAIT_RED": "Wait at red",
    "TURN_AND_DRIVE": "Turn and drive",
    "GOAL_REACHED": "Goal reached",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Nigel run with telemetry.jsonl and frames/")
    parser.add_argument("--output", type=Path, default=ROOT / "docs/media")
    parser.add_argument("--ffmpeg", default="ffmpeg")
    args = parser.parse_args()
    if "gilbreth" in str(ROOT) and not os.environ.get("SLURM_JOB_ID"):
        parser.error("On Gilbreth, submit browser rendering and encoding through Slurm.")
    if os.environ.get("SLURM_JOB_PARTITION", "") not in ("", "a100-40gb", "a30"):
        parser.error("Use the allowed A100-40GB or A30 allocation on Gilbreth.")
    rows = [json.loads(line) for line in (args.source / "telemetry.jsonl").read_text().splitlines() if line.strip()]
    if len(rows) < 2 or any(b["t"] <= a["t"] for a, b in zip(rows, rows[1:])):
        parser.error("Expected at least two strictly increasing source timestamps.")
    args.output.mkdir(parents=True, exist_ok=True)
    html = (ROOT / "tracr_demo/static/index.html").read_text()
    html = html.replace('<script src="/static/app.js"></script>', "")
    html = html.replace('<link rel="stylesheet" href="/static/style.css">',
                        "<style>" + (ROOT / "tracr_demo/static/style.css").read_text() + "</style>")
    errors = []
    source_hash = hashlib.sha256()
    source_hash.update((args.source / "telemetry.jsonl").read_bytes())
    with tempfile.TemporaryDirectory(prefix="tracr-preview-") as temp, sync_playwright() as pw:
        work = Path(temp)
        browser = pw.chromium.launch(headless=True, args=["--disable-dev-shm-usage"])
        page = browser.new_page(viewport={"width": 1200, "height": 1000}, device_scale_factor=1)
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.set_content(html)
        page.add_style_tag(content="""
            header{height:76px}main{padding-top:24px}.intro{gap:16px}
            #notice{margin:18px 0 18px}.panel-head{height:50px;padding:0 16px}
            .panel-foot{padding:12px 16px}.metrics{padding:19px 0;margin-top:20px}
            .metrics>div{padding:0 18px}.metrics strong{font-size:22px}
            footer{padding:21px 0}button:disabled{opacity:1;cursor:default}
            .replay-progress{height:3px;background:#27333e;margin:0 0 8px}
            .replay-progress span{display:block;height:100%;background:var(--accent)}
        """)
        page.evaluate("""() => {
            const set = (q, text) => document.querySelector(q).textContent = text;
            set('.brand p', 'NeoRacer V1 / Poster demo preview');
            set('.thin', ' / DEMO PREVIEW');
            set('.eyebrow', 'RECORDED AUTODRIVE EXAMPLE');
            set('.subtitle', 'Field demo layout: onboard video on the left, a virtual vehicle on the right.');
            set('#mode', 'RECORDED SIMULATION');
            set('#fullscreen', '2x replay');
            document.querySelector('#fullscreen').disabled = true;
            set('#connection', 'Nigel / Tiny Town');
            set('#map-label', 'Example map / Field map pending');
            set('#notice', 'PREVIEW ONLY - Both views below are recorded Nigel simulation. Physical NeoRacer + Unity integration is pending.');
            const panels = document.querySelectorAll('.panel');
            panels[0].querySelector('h2').textContent = 'Onboard camera';
            panels[0].querySelector('.tag').textContent = 'SIMULATED / NIGEL';
            panels[1].querySelector('h2').textContent = 'AutoDRIVE view';
            panels[1].querySelector('.tag').textContent = 'CHASE CAMERA';
            set('#real-state', 'RECORDED / FRONT');
            set('#sim-state', 'RECORDED / THIRD PERSON');
            set('#camera-source', 'Preview: simulated onboard camera');
            set('#pose-source', 'Preview: recorded simulator scene');
            set('#camera-age', 'Not a live input');
            set('#pose-age', 'Not a live render');
            for (const id of ['real-placeholder', 'sim-placeholder']) document.getElementById(id).hidden = true;
            for (const id of ['real', 'sim']) document.getElementById(id).hidden = false;
            document.getElementById('real').alt = 'Recorded Nigel simulated front camera';
            document.getElementById('sim').alt = 'Recorded Nigel AutoDRIVE chase camera';
            const titles = ['RECORDING TIME', 'SIMULATED SPEED', 'SIMULATED POSITION', 'RECORDED SCENARIO'];
            const notes = ['46.4 s source / 2x playback', 'From historical telemetry', 'Tiny Town coordinates / m', 'No physical vehicle connected'];
            document.querySelectorAll('.metrics > div').forEach((metric, i) => {
                metric.querySelector('p').textContent = titles[i];
                metric.querySelector('span').textContent = notes[i];
            });
            set('footer > span:first-child', 'TraCR / Layout preview using AutoDRIVE Simulator 0.2.0');
            set('footer > span:last-child', 'Recorded example / Hardware sync unverified');
            const progress = document.createElement('div');
            progress.className = 'replay-progress';
            progress.innerHTML = '<span id="replay-progress"></span>';
            document.querySelector('footer').before(progress);
        }""")
        height = math.ceil(page.locator("body").bounding_box()["height"])
        clip = {"x": 0, "y": 0, "width": 1200, "height": height}
        still_index = min(range(len(rows)), key=lambda i: abs(rows[i]["t"] - 22))
        concat = []
        for index, row in enumerate(rows):
            images = []
            for view in ("front", "scene"):
                data = (args.source / "frames" / f"{row['frame']:05d}_{view}.jpg").read_bytes()
                source_hash.update(data)
                images.append("data:image/jpeg;base64," + base64.b64encode(data).decode("ascii"))
            page.evaluate("""async ({images, row, phase, total}) => {
                const decoded = await Promise.all(images.map(async src => {
                    const img = new Image(); img.src = src; await img.decode(); return img;
                }));
                document.querySelector('#real').src = images[0];
                // Crop only the simulator's native 58 px toolbar, keeping the scene intact.
                const scene = decoded[1], canvas = document.createElement('canvas');
                canvas.width = scene.width; canvas.height = scene.height - 58;
                canvas.getContext('2d').drawImage(scene, 0, 58, scene.width, scene.height - 58,
                                                0, 0, canvas.width, canvas.height);
                document.querySelector('#sim').src = canvas.toDataURL('image/png');
                await Promise.all(['real', 'sim'].map(id => document.getElementById(id).decode()));
                const set = (id, text) => document.getElementById(id).textContent = text;
                set('frame-label', `Source frame ${String(row.frame).padStart(3, '0')}`);
                set('pose-label', phase);
                set('skew', `${row.t.toFixed(1)} s`);
                set('latency', `${row.speed_mps.toFixed(2)} m/s`);
                set('position', `${row.x.toFixed(2)}, ${row.y.toFixed(2)}`);
                set('pairs', phase);
                document.getElementById('replay-progress').style.width = `${100 * row.t / total}%`;
            }""", {"images": images, "row": {k: row[k] for k in ("t", "frame", "x", "y", "speed_mps")},
                   "phase": PHASES.get(row["phase"], row["phase"]), "total": rows[-1]["t"]})
            path = work / f"{index:05d}.png"
            page.screenshot(path=str(path), clip=clip, animations="disabled")
            if index == still_index:
                shutil.copyfile(path, args.output / "autodrive-preview.png")
            duration = (rows[index + 1]["t"] - row["t"]) / 2 if index + 1 < len(rows) else 1.0
            concat.extend([f"file '{path.as_posix()}'", f"duration {duration:.6f}"])
        concat.append(f"file '{path.as_posix()}'")
        assert not errors, errors
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        assert "PREVIEW ONLY" in page.locator("#notice").inner_text()
        assert page.locator("#mode").inner_text() == "RECORDED SIMULATION"
        browser.close()
        (work / "frames.txt").write_text("\n".join(concat) + "\n")
        subprocess.run([
            args.ffmpeg, "-hide_banner", "-loglevel", "warning", "-y", "-threads", "2",
            "-filter_complex_threads", "1", "-f", "concat", "-safe", "0", "-i", str(work / "frames.txt"),
            "-filter_complex", "fps=6,split[a][b];[a]palettegen=max_colors=256:stats_mode=full[p];"
                               "[b][p]paletteuse=dither=bayer:bayer_scale=3:diff_mode=rectangle",
            "-loop", "0", str(args.output / "autodrive-preview.gif"),
        ], check=True)
    report = {
        "kind": "recorded_simulation_layout_preview", "simulator": "AutoDRIVE 0.2.0",
        "vehicle": "Nigel", "map": "Tiny Town", "physical_footage": False,
        "live_bridge_exercised": False, "new_unity_execution": False,
        "source_samples": len(rows), "source_duration_seconds": rows[-1]["t"] - rows[0]["t"],
        "playback_speed": 2, "gif_output_fps": 6, "final_hold_seconds": 1,
        "timing": "Source intervals preserved at 2x speed; resampled to 6 fps without interpolation.",
        "source_digest_sha256": source_hash.hexdigest(),
        "source_digest_order": "telemetry.jsonl bytes, then front and scene JPEG bytes for each row in order",
        "viewport": [1200, height], "browser_errors": errors, "horizontal_overflow": False,
        "slurm_job_id": os.environ.get("SLURM_JOB_ID"), "partition": os.environ.get("SLURM_JOB_PARTITION"),
        "artifacts": {},
    }
    for name in ("autodrive-preview.gif", "autodrive-preview.png"):
        data = (args.output / name).read_bytes()
        report["artifacts"][name] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    (args.output / "preview.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
