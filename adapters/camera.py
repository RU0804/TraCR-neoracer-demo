#!/usr/bin/env python3
"""USB / RTSP / HTTP MJPEG input. Timestamps are decode receipt, not exposure."""
import argparse
import base64
import time
import cv2
from common import LatestCapture, LatestSender, metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, help="USB index or RTSP/HTTP URL")
    parser.add_argument("--server", default="http://127.0.0.1:8080")
    parser.add_argument("--fps", type=float, default=20)
    args = parser.parse_args()
    if not 1 <= args.fps <= 60:
        parser.error("fps must be 1..60")
    if not (args.source.isdigit() or args.source.startswith(("rtsp://", "http://", "https://"))):
        parser.error("source must be USB index or live stream URL; replay is not a live camera")
    capture, sender = LatestCapture(args.source), LatestSender(args.server)
    print("Camera uses decode receipt timestamps; capture latency is NOT measured.")
    try:
        while True:
            result = capture.read()
            if result:
                timestamp, image = result
                h, w = image.shape[:2]
                scale = min(1280/w, 720/h, 1)
                if scale < 1:
                    image = cv2.resize(image, (int(w*scale), int(h*scale)))
                ok, encoded = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 80])
                if ok:
                    sender.put("/api/camera", {**metadata("onboard-camera", timestamp),
                                              "jpeg": base64.b64encode(encoded).decode()})
            time.sleep(1/args.fps)
    except KeyboardInterrupt:
        pass
    finally:
        capture.close()
        sender.close()


if __name__ == "__main__":
    main()
