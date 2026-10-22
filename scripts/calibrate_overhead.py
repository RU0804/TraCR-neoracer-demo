#!/usr/bin/env python3
"""Fit undistorted-pixel -> map XY using >=6 measured pairs on the tag-height plane."""
import argparse
import json
from pathlib import Path
import cv2
import numpy as np

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('measurements',type=Path,help='JSON: camera_matrix, distortion, pixels, map_xy, image_size')
parser.add_argument('--template',type=Path,default=Path('configs/overhead.example.json'))
parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--max-rmse-m',type=float,default=.03)
args=parser.parse_args()
if args.output.exists():
    parser.error('Output exists; choose a new calibration file')
m=json.loads(args.measurements.read_text());cal=json.loads(args.template.read_text())
pixels=np.asarray(m['pixels'],dtype=np.float64).reshape(-1,1,2)
world=np.asarray(m['map_xy'],dtype=np.float64).reshape(-1,1,2)
if len(pixels)<6 or len(pixels)!=len(world) or not np.isfinite(pixels).all() or not np.isfinite(world).all():
    parser.error('Need at least six finite matching points distributed over the map at tag height')
k=np.asarray(m['camera_matrix'],dtype=np.float64);d=np.asarray(m['distortion'],dtype=np.float64)
undistorted=cv2.undistortPoints(pixels,k,d,P=k)
h,inliers=cv2.findHomography(undistorted,world,cv2.RANSAC,args.max_rmse_m)
if h is None or inliers is None or int(inliers.sum())<6:
    parser.error('Degenerate or inconsistent measurements')
predicted=cv2.perspectiveTransform(undistorted,h)
rmse=float(np.sqrt(np.mean(np.sum((predicted-world)**2,axis=2))))
if rmse>args.max_rmse_m:
    parser.error(f'All-point fit RMSE {rmse:.4f} m exceeds threshold; inspect outliers')
for key in ('camera_matrix','distortion','image_size'):
    cal[key]=m[key]
cal.update(pixel_to_map=h.tolist(),calibrated=True,fit_rmse_m=rmse,
           note='Fit uses measured tag-height plane. Verify independent held-out points before demonstration.')
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(json.dumps(cal,indent=2)+'\n')
print(f'Calibration saved; fit RMSE={rmse:.4f} m. This is NOT held-out localization accuracy.')
