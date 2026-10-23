# Poster demonstration runbook

The presenter uses a laptop browser to show NeoRacer onboard video on the left and an AutoDRIVE view on the right. The physical car is remotely driven on an approximately 5 m x 5 m foam-board road layout. Use a stable local network rather than depending on Gilbreth queues or public-cloud rendering.

## Collect before rehearsal

- Laptop operating system, CPU, GPU and memory; whether the NeoRacer Unity build runs reliably.
- Current video viewing method, address or ROS topic, encoding, resolution and measured frame rate.
- Localization source: existing map localization, odometry only, or an overhead camera that can be installed.
- Surveyed road plan, vehicle reference point, roof marker and camera mounting parameters.
- A shared clock plan. If only receipt timestamps are available, retain the timing-unverified indication.

## Startup sequence

1. Connect to the demonstration LAN and verify onboard video is accessible from the laptop. Retain the existing remote-driving procedure.
2. Activate the Python environment and run `tracr-demo --config configs/demo.json` from the repository root. For HTTP inputs from another device, change `host` and set the same `TRACR_TOKEN` of at least 20 characters in every relevant process environment.
3. Start the onboard camera adapter and **one** physical localization source. Use one publisher per input timeline to avoid interleaving unrelated sources.
4. Open the configured AutoDRIVE NeoRacer application. Confirm the TraCR HTTP component is enabled, the original Socket.IO connection is disconnected, and no competing controller updates the vehicle.
5. Open `http://127.0.0.1:8080` in the browser. Check the waiting states as sources connect, verify source names and timing labels, and select Full screen.
6. Drive slowly in a straight line, turn left and right, and stop. Check that virtual position and heading match. Complete measurements before describing the system as a validated physical synchronization demonstration.

## Troubleshooting

| Symptom | Next check |
|---|---|
| Left panel keeps waiting | Check the video adapter, URL/topic, encoding, network and firewall; inspect its terminal |
| Video is available but the right panel waits | Check pose freshness, map coordinates and timestamp tolerance; video alone cannot provide a pose |
| Pose is available but no render arrives | Check Unity Console, component references, token, display camera and HTTP requests; confirm the application uses NeoRacer |
| Mirrored trajectory or reversed turns | Verify the origin, +x/+y axes, yaw sign, prefab orientation and whether an axis transform was applied twice |
| Alignment drifts over time | Check whether only odometry is available, and verify the map transform and marker height; display offsets do not correct drift |
| A panel is marked STALE | Identify whether video, localization or Unity stopped; preserve the stale warning and verify automatic updates after recovery |
| Timestamp errors | Check UTC, ROS use_sim_time, exposure/receipt semantics and device clock offsets before changing tolerances |
| Smooth animation but poor responsiveness | Measure camera buffering, encoding, network delay, Unity encoding and browser refresh; frame rate does not determine latency |

## Acceptance records

For each rehearsal, save the machine configuration, upstream commit, camera parameters, map/calibration versions, and start/end times. Capture service status with `python scripts/collect_metrics.py --seconds 120 --output recordings/run-001/status.jsonl`.

Report exposure-to-display video latency, pose age, video/pose timestamp difference, static and dynamic spatial error, frame rate, periods of data loss, and recovery time separately. Service P95 excludes screen display and cannot replace an end-to-end timing test using a shared visible timer or LED. With receipt timestamps, cross-stream sampling skew remains unknown. Keep failed and occluded segments in the records.

Test marker occlusion, camera disconnection, stopped Unity rendering and network loss at least once each. The interface must identify stale images rather than presenting them as live, and updates should resume when inputs recover. Finish with a continuous rehearsal covering the planned presentation duration plus a margin.

If the live pipeline does not pass field acceptance, the previous Nigel recording can be shown separately with an explicit historical Nigel simulation label. Do not describe self-test or offline playback as live NeoRacer state synchronization.
