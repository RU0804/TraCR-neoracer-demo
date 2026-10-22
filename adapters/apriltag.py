#!/usr/bin/env python3
"""Optional overhead AprilTag localization with a measured tag-height plane homography."""
import argparse
import json
import math
import time
from pathlib import Path
import cv2
import numpy as np
from common import LatestCapture, LatestSender, metadata


def tag_pose(corners, calibration):
    points = np.asarray(corners, dtype=np.float64).reshape(4, 1, 2)
    k = np.asarray(calibration["camera_matrix"], dtype=np.float64)
    distortion = np.asarray(calibration["distortion"], dtype=np.float64)
    points = cv2.undistortPoints(points, k, distortion, P=k)
    h = np.asarray(calibration["pixel_to_map"], dtype=np.float64)
    world = cv2.perspectiveTransform(points, h).reshape(4,2)
    center = world.mean(axis=0)
    forward = (world[0]+world[1])/2-center  # printed top edge is tag-forward
    if np.linalg.norm(forward) < 1e-6:
        raise ValueError("degenerate marker projection")
    yaw = math.atan2(forward[1],forward[0])+calibration["yaw_offset_rad"]
    dx,dy = calibration["tag_to_base_xy_m"]
    center += [math.cos(yaw)*dx-math.sin(yaw)*dy, math.sin(yaw)*dx+math.cos(yaw)*dy]
    return {"x":float(center[0]),"y":float(center[1]),"z":calibration["base_z_m"],"yaw":yaw}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--calibration", type=Path, required=True)
    parser.add_argument("--server", default="http://127.0.0.1:8080")
    args = parser.parse_args()
    cal = json.loads(args.calibration.read_text())
    if not cal.get("calibrated"):
        parser.error("Calibration is a template; measure intrinsics + tag-height homography first")
    capture, sender = LatestCapture(args.source), LatestSender(args.server)
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)
    detector = cv2.aruco.ArucoDetector(dictionary, cv2.aruco.DetectorParameters())
    try:
        while True:
            result = capture.read()
            if not result:
                time.sleep(.01)
                continue
            timestamp, image = result
            meta = metadata("overhead-apriltag", timestamp)
            if list(image.shape[1::-1]) != cal["image_size"]:
                raise ValueError("camera resolution differs from calibration")
            corners, ids, _ = detector.detectMarkers(image)
            matches = [] if ids is None else [c for c,i in zip(corners,ids.ravel()) if int(i) == cal["tag_id"]]
            if len(matches) != 1 or abs(cv2.contourArea(matches[0])) < cal["minimum_area_px"]:
                sender.put("/api/pose", {**meta,"quality":"lost"})
                continue
            sender.put("/api/pose", {**meta,"quality":"localized","frame_id":"map",**tag_pose(matches[0],cal)})
    except KeyboardInterrupt:
        pass
    finally:
        capture.close()
        sender.close()


if __name__ == "__main__":
    main()
