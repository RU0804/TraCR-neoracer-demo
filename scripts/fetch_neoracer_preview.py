#!/usr/bin/env python3
"""Download hash-pinned model and renderer dependencies into an ignored cache."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def fetch(entry):
    path = ROOT / "upstream/preview-assets" / entry["path"]
    if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"]:
        return
    data = urllib.request.urlopen(entry["url"], timeout=60).read()
    if hashlib.sha256(data).hexdigest() != entry["sha256"]:
        raise ValueError("Checksum mismatch: " + entry["path"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


if __name__ == "__main__":
    lock = json.loads((ROOT / "configs/preview-assets.lock.json").read_text())
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(fetch, lock["assets"]))
    print(f"Verified {len(lock['assets'])} preview assets. No Unity build was installed.")
