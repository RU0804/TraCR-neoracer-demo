# Hardware integration and spatial calibration

The field display combines onboard video with a virtual scene. **Onboard video is not a map-localization result.** Following the physical car requires continuous measurements of map position, heading and sampling time. The first version retains remote-controlled driving and only reads vehicle state.

## Reuse existing localization where available

Inspect the actual vehicle's operating system, ROS version, topics and image encodings. Upstream defaults are not evidence of this vehicle's configuration. These commands only inspect data:

```bash
ros2 topic list -t
ros2 topic info /camera/color -v
ros2 topic info /odom -v
ros2 topic hz /camera/color
```

The topic names above are candidates; use the actual topic list. Images may be JPEG bytes carried in `Image`, standard RGB/BGR images, or `CompressedImage`. The adapter supports these common formats and reports unsupported encodings.

Run the adapter in an environment with ROS 2 installed. For a virtual environment, use the same system Python and create it with `python3 -m venv --system-site-packages .venv-ros` so that `rclpy` remains visible, then install this repository. Do not run the NeoRacer system installer or service-enablement scripts directly on Gilbreth.

```bash
# Source /opt/ros/humble/setup.bash if it matches the vehicle's ROS version.
# For an existing map-localization PoseStamped topic:
python adapters/ros2_readonly.py --image-topic /camera/color --pose-topic /localization/pose
# For Odometry only, first measure the initial odom-to-map transform:
python adapters/ros2_readonly.py --image-topic /camera/color --pose-topic /odom \
  --odometry --transform configs/local.odom_to_map.json
```

By default, `PoseStamped` must use `frame_id=map`. Other frames require an explicit transform. A map pose does not necessarily contain a trustworthy quality signal; the source must detect its own tracking failures. The adapter does not infer SLAM confidence. If a failed localizer keeps publishing an old pose with new timestamps, add an adapter for that localizer's quality signal. The service cannot detect this condition automatically. An initially aligned `/odom` stream can still drift.

Receive data from the physical car without launching the official AutoDRIVE simulation ROS bridge. Do not create control publishers such as `/drive`, `/mux_out` or `/motor`. If simulation ROS must also run, isolate it with separate ROS_DOMAIN_ID values and namespaces/network boundaries so simulated `/odom` and `/scan` cannot enter the physical-data adapter.

## Optional overhead AprilTag localization

If reliable map localization is unavailable, install an AprilTag 36h11 marker on the roof. A fixed overhead camera supplies localization while the left panel continues to show the onboard camera. Coverage, occlusion and marker resolution across a 5 m x 5 m area require field measurements; one camera may not be sufficient.

1. Select a fixed origin, +x and +y directions, and meter units. Survey road centerlines, widths, intersections and boundaries into a separate map JSON file. Match the physical reference marks to the Unity origin.
2. Fix the overhead camera's focal length, resolution and position. Calibrate its intrinsics and distortion with a checkerboard, saving `camera_matrix` and `distortion` for the actual image resolution.
3. Place at least six control points with measured map XY coordinates on a **horizontal plane at the roof marker's height**. Record their raw image pixel coordinates. A floor-plane homography applied to a roof marker introduces parallax with an oblique camera.
4. Create a measurement JSON file containing `camera_matrix`, `distortion`, `image_size`, `pixels` (N x 2) and `map_xy` (N x 2), then run:

```bash
python scripts/calibrate_overhead.py measurements.json --output configs/local.overhead.json
```

5. Set the actual `tag_id`, `yaw_offset_rad`, `tag_to_base_xy_m` and `base_z_m` in the output. The printed top edge defines tag-forward; `yaw_offset_rad` corrects this to vehicle-forward. `tag_to_base_xy_m` is the vector from marker center to the vehicle reference point, expressed in vehicle coordinates. Keep the measurement records.
6. Start the onboard camera adapter separately, then start localization:

```bash
python adapters/apriltag.py --source 1 --calibration configs/local.overhead.json
```

The default marker-area threshold is an initial setting. If exactly one matching target ID is not detected, the adapter immediately reports localization loss. A disconnected camera becomes stale through the service timeout. Current detection-quality checks cover only ID uniqueness and area, not full reprojection confidence; acceptance requires independent check points and dynamic trials.

Examples with `calibrated=false` cannot be used directly. Fitting residuals measure error at control points, not field localization accuracy. Check independent vehicle locations, headings and road edges; report maximum and P95 errors. Uneven terrain, significant marker tilt or camera movement invalidates the planar assumption and requires recalibration or full 3D pose estimation.

Reference: [OpenCV marker detection documentation](https://docs.opencv.org/4.x/d5/dae/tutorial_aruco_detection.html).
