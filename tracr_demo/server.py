"""Local ingest + bounded WebSocket display + acknowledged Unity frame service."""
import argparse
import asyncio
import base64
import contextlib
import hmac
import io
import json
import math
import os
from pathlib import Path
import time

from aiohttp import web, WSMsgType
from PIL import Image, ImageDraw
from .core import Invalid, Pairer

DEFAULT = {"host": "127.0.0.1", "port": 8080, "buffer_size": 40,
           "max_age_s": 2.0, "stale_s": .75, "max_skew_s": .08,
           "render_timeout_s": .6, "clock_verified": False,
           "map_label": "5 m × 5 m · layout survey pending"}
STATIC = Path(__file__).with_name("static")


def jpeg_decode(encoded):
    if not isinstance(encoded, str) or len(encoded) > 2_800_000:
        raise Invalid("jpeg must be base64 text <=2.8 MB")
    try:
        raw = base64.b64decode(encoded, validate=True)
        with Image.open(io.BytesIO(raw)) as im:
            if im.format != "JPEG" or not (16 <= im.width <= 1920 and 16 <= im.height <= 1080):
                raise Invalid("expected JPEG, 16..1920 × 16..1080")
            im.verify()
        return raw
    except (ValueError, OSError, Image.DecompressionBombError) as exc:
        raise Invalid("invalid JPEG") from exc


def b64(raw):
    return base64.b64encode(raw).decode("ascii")


@web.middleware
async def guard(request, handler):
    if request.app["config"]["host"] in ("127.0.0.1", "localhost", "::1"):
        if request.url.host not in ("127.0.0.1", "localhost", "::1"):
            raise web.HTTPForbidden(text="unexpected Host for loopback service")
    origin = request.headers.get("Origin")
    if origin and origin != f"{request.scheme}://{request.host}":
        raise web.HTTPForbidden(text="cross-origin access disabled")
    if request.path.startswith("/api/"):
        expected = request.app["token"]
        supplied = request.headers.get("Authorization", "").removeprefix("Bearer ")
        if expected and not hmac.compare_digest(supplied.encode(), expected.encode()):
            raise web.HTTPUnauthorized(text="missing or invalid bearer token")
    try:
        return await handler(request)
    except (Invalid, json.JSONDecodeError, TypeError, KeyError) as exc:
        return web.json_response({"error": str(exc)}, status=400)


async def data(request):
    result = await request.json()
    if not isinstance(result, dict):
        raise Invalid("JSON object required")
    return result


async def index(request):
    return web.FileResponse(STATIC / "index.html")


async def static(request):
    name = request.match_info["name"]
    if name not in ("style.css", "app.js"):
        raise web.HTTPNotFound()
    return web.FileResponse(STATIC / name)


async def pose(request):
    if request.app["self_test"]:
        raise web.HTTPConflict(text="external input disabled in self-test")
    request.app["pairer"].add_pose(await data(request))
    return web.json_response({"ok": True})


async def camera(request):
    if request.app["self_test"]:
        raise web.HTTPConflict(text="external input disabled in self-test")
    d = await data(request)
    frame = request.app["pairer"].add_frame(d, jpeg_decode(d.get("jpeg")))
    request.app["display"]["video"] = frame
    return web.json_response({"ok": True})


async def next_render(request):
    if request.app["self_test"]:
        raise web.HTTPConflict(text="Unity disabled in self-test")
    result = request.app["pairer"].offer()
    return web.json_response(result) if result else web.Response(status=204)


async def rendered(request):
    if request.app["self_test"]:
        raise web.HTTPConflict(text="Unity disabled in self-test")
    d = await data(request)
    image = jpeg_decode(d.get("jpeg"))
    frame, p = request.app["pairer"].finish(d["ticket"], d["frame_id"], d["pose_id"])
    request.app["display"]["pair"] = pair_message(frame, p, image, "autodrive")
    return web.json_response({"ok": True})


def pair_message(frame, pose, image, renderer):
    return {"type": "pair", "frame_id": frame.id, "pose_id": pose.id,
            "capture_time": frame.capture_time, "pose_time": pose.capture_time,
            "time_basis": frame.time_basis, "renderer": renderer,
            "left": b64(frame.jpeg), "right": b64(image),
            "x": pose.x, "y": pose.y, "yaw": pose.yaw,
            "skew_ms": 1000*abs(frame.capture_time-pose.capture_time)}


def status_message(app):
    return {"type": "status", "server_time": time.time(),
            "mode": "self-test" if app["self_test"] else "live",
            "map_label": app["config"]["map_label"], "stale_s": app["config"]["stale_s"],
            **app["pairer"].status()}


async def status(request):
    return web.json_response(status_message(request.app))


async def websocket(request):
    ws = web.WebSocketResponse(heartbeat=10, max_msg_size=4096)
    await ws.prepare(request)
    reader = None
    request.app["sockets"].add(ws)
    try:
        auth = await asyncio.wait_for(ws.receive_json(), 5)
        if not isinstance(auth, dict) or not isinstance(auth.get("token", ""), str):
            await ws.close(code=1008, message=b"Invalid authentication")
            return ws
        if not hmac.compare_digest(auth.get("token", "").encode(), request.app["token"].encode()):
            await ws.close(code=1008, message=b"Authentication required")
            return ws
        async def drain():
            async for message in ws:
                if message.type == WSMsgType.ERROR:
                    break
        reader = asyncio.create_task(drain())
        last_pair, last_video = None, None
        while not ws.closed:
            app = request.app
            st = status_message(app)
            await asyncio.wait_for(ws.send_json(st), 1)
            pair = app["display"].get("pair")
            frame = app["display"].get("video")
            if pair and st["render_fresh"]:
                if pair["frame_id"] != last_pair:
                    await asyncio.wait_for(ws.send_json(pair), 1)
                    last_pair = pair["frame_id"]
            elif frame and frame.id != last_video:
                await asyncio.wait_for(ws.send_json({"type": "video", "frame_id": frame.id,
                    "capture_time": frame.capture_time, "left": b64(frame.jpeg)}), 1)
                last_video = frame.id
            # One send in flight per client; no per-client image backlog.
            await asyncio.sleep(.04)
    except (asyncio.TimeoutError, ConnectionError, RuntimeError, ValueError):
        pass
    finally:
        if reader:
            reader.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await reader
        request.app["sockets"].discard(ws)
        await ws.close()
    return ws


def test_image(t, virtual=False):
    im = Image.new("RGB", (960, 540), "#14212c")
    draw = ImageDraw.Draw(im)
    draw.text((28, 24), "SYNTHETIC SELF-TEST / NO REAL CAR / NO AUTODRIVE RENDER", fill="#ffc971")
    if virtual:
        draw.rectangle((245, 100, 715, 490), outline="#42586a", width=50)
        x, y = 480+200*math.cos(t), 290-155*math.sin(t)
        draw.ellipse((x-16, y-16, x+16, y+16), fill="#66e8ce")
        draw.text((28, 60), "Illustrative 5 m x 5 m map", fill="white")
    else:
        draw.polygon([(300, 180), (660, 180), (940, 540), (20, 540)], fill="#3c4852")
        for j in range(6):
            y = 200+((j*65+t*100)%340)
            draw.rectangle((476, y, 484, y+22), fill="#f5df85")
        draw.text((28, 60), "Generated camera placeholder", fill="white")
    draw.text((28, 505), f"Test trajectory t={t:.2f}s", fill="white")
    buff = io.BytesIO()
    im.save(buff, format="JPEG", quality=80)
    return buff.getvalue()


async def synthetic(app):
    start, seq = time.time(), 0
    while True:
        now = time.time()
        t = (now-start)*.4
        seq += 1
        p = app["pairer"]
        p.add_pose({"id": f"test-p-{seq}", "capture_time": now, "time_basis": "receipt",
                    "frame_id": "map", "x": 2.5+1.5*math.cos(t), "y": 2.5+1.5*math.sin(t),
                    "z": 0., "yaw": t+math.pi/2, "source": "synthetic", "quality": "test"})
        frame = p.add_frame({"id": f"test-f-{seq}", "capture_time": now,
                             "time_basis": "receipt", "source": "synthetic"}, test_image(t))
        app["display"]["video"] = frame
        offer = p.offer()
        if offer:
            frame, pose = p.finish(offer["ticket"], offer["frame_id"], offer["pose_id"])
            app["display"]["pair"] = pair_message(frame, pose, test_image(t, True), "synthetic")
        await asyncio.sleep(.1)


async def lifecycle(app):
    task = asyncio.create_task(synthetic(app)) if app["self_test"] else None
    yield
    if task:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task


async def shutdown(app):
    await asyncio.gather(*(ws.close(code=1001, message=b"Bridge shutting down")
                           for ws in list(app["sockets"])))


def create_app(config=None, token="", self_test=False):
    cfg = {**DEFAULT, **(config or {})}
    for key in ("max_age_s", "stale_s", "max_skew_s", "render_timeout_s"):
        value = cfg[key]
        if isinstance(value, bool) or not isinstance(value, (int,float)) or not math.isfinite(value) or value <= 0:
            raise Invalid(key + " must be positive and finite")
    if type(cfg["buffer_size"]) is not int or not 2 <= cfg["buffer_size"] <= 120:
        raise Invalid("buffer_size must be 2..120")
    if type(cfg["clock_verified"]) is not bool:
        raise Invalid("clock_verified must be boolean")
    if cfg["host"] not in ("127.0.0.1", "localhost", "::1") and len(token) < 20:
        raise Invalid("LAN binding requires TRACR_TOKEN of at least 20 characters")
    app = web.Application(middlewares=[guard], client_max_size=3_000_000)
    app["config"], app["token"], app["self_test"] = cfg, token, self_test
    app["pairer"], app["display"] = Pairer(cfg), {}
    app["sockets"] = set()
    app.router.add_get("/", index)
    app.router.add_get("/static/{name}", static)
    app.router.add_get("/ws", websocket)
    app.router.add_get("/api/status", status)
    app.router.add_post("/api/pose", pose)
    app.router.add_post("/api/camera", camera)
    app.router.add_get("/api/unity/next", next_render)
    app.router.add_post("/api/unity/frame", rendered)
    app.cleanup_ctx.append(lifecycle)
    app.on_shutdown.append(shutdown)
    return app


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--host")
    parser.add_argument("--port", type=int)
    parser.add_argument("--self-test", action="store_true", help="synthetic images, never real car or AutoDRIVE")
    args = parser.parse_args()
    cfg = json.loads(args.config.read_text()) if args.config else dict(DEFAULT)
    for k in ("host", "port"):
        if getattr(args, k) is not None:
            cfg[k] = getattr(args, k)
    if os.environ.get("SLURM_JOB_PARTITION", "").lower().startswith("a10") and not os.environ.get("SLURM_JOB_PARTITION", "").lower().startswith("a100"):
        parser.error("Full demo is not permitted on A10")
    app = create_app(cfg, os.environ.get("TRACR_TOKEN", ""), args.self_test)
    print("SYNTHETIC SELF-TEST" if args.self_test else "LIVE INPUT MODE — awaiting physical camera, map pose and Unity")
    web.run_app(app, host=app["config"]["host"], port=app["config"]["port"])


if __name__ == "__main__":
    main()
