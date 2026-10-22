"""Shared adapter transport: one latest item per channel, bounded network waits."""
import json
import os
import threading
import time
import urllib.error
import urllib.request
import uuid


def post(server, path, payload):
    headers = {"Content-Type": "application/json"}
    token = os.environ.get("TRACR_TOKEN", "")
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(server.rstrip("/")+path, data=json.dumps(payload).encode(), headers=headers)
    with urllib.request.urlopen(req, timeout=.7) as response:
        return response.read()


class LatestSender:
    def __init__(self, server):
        self.server, self.pending = server, {}
        self.condition, self.stopped = threading.Condition(), False
        self.worker = threading.Thread(target=self.run, daemon=True)
        self.worker.start()

    def put(self, path, payload):
        with self.condition:
            self.pending[path] = payload
            self.condition.notify()

    def run(self):
        while True:
            with self.condition:
                self.condition.wait_for(lambda: self.pending or self.stopped)
                if self.stopped:
                    return
                path = next(iter(self.pending))
                item = self.pending.pop(path)
            try:
                post(self.server, path, item)
            except (OSError, urllib.error.URLError) as exc:
                print(f"Adapter send failed ({type(exc).__name__}); dropping old sample", flush=True)

    def close(self):
        with self.condition:
            self.stopped = True
            self.condition.notify()
        self.worker.join(timeout=1)


def metadata(source, timestamp=None, basis="receipt"):
    return {"id": uuid.uuid4().hex, "capture_time": time.time() if timestamp is None else timestamp,
            "time_basis": basis, "source": source}


class LatestCapture:
    """OpenCV reader that continuously drains a source; consumers never form a FIFO."""
    def __init__(self, source):
        self.source, self.latest, self.error = source, None, None
        self.lock, self.stopped = threading.Lock(), False
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def run(self):
        import cv2
        source = int(self.source) if str(self.source).isdigit() else self.source
        while not self.stopped:
            cap = cv2.VideoCapture()
            if isinstance(source, int):
                opened = cap.open(source)
            else:
                opened = cap.open(source, cv2.CAP_FFMPEG,
                    [cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 3000, cv2.CAP_PROP_READ_TIMEOUT_MSEC, 2000])
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            if opened:
                while not self.stopped:
                    ok, image = cap.read()
                    if not ok:
                        break
                    with self.lock:
                        self.latest = (time.time(), image)
            cap.release()
            if not self.stopped:
                print("Camera unavailable; reconnecting", flush=True)
                time.sleep(1)

    def read(self):
        with self.lock:
            result, self.latest = self.latest, None
            return result

    def close(self):
        self.stopped = True
        self.thread.join(timeout=4)
