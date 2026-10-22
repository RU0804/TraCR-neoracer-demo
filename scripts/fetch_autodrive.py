#!/usr/bin/env python3
"""Fetch the pinned upstream source into an ignored directory; no system installer."""
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
lock = json.loads((root/"upstream.lock.json").read_text())
entry = lock["simulator"]
target = root/"upstream"/"AutoDRIVE-Simulator"
if target.exists():
    raise SystemExit("Destination exists. Verify it manually; refusing to overwrite.")
target.mkdir(parents=True)
subprocess.run(["git", "init", str(target)], check=True)
subprocess.run(["git", "-C", str(target), "remote", "add", "origin", entry["url"]], check=True)
subprocess.run(["git", "-C", str(target), "fetch", "--depth", "1", "origin", entry["commit"]], check=True)
subprocess.run(["git", "-C", str(target), "checkout", "--detach", "FETCH_HEAD"], check=True)
head = subprocess.check_output(["git", "-C", str(target), "rev-parse", "HEAD"], text=True).strip()
if head != entry["commit"]:
    raise SystemExit("Upstream checkout does not match lock")
print("Pinned Unity project ready. Follow docs/UNITY.md; no NeoRacer build is bundled.")
