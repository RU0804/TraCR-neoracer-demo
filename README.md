# TraCR-neoracer-demo

A NeoRacer V1 demonstration with **onboard video on the left and an AutoDRIVE view following measured vehicle poses on the right**. The intended deployment is the presenter's laptop on a local network, with an approximately 5 m x 5 m physical road layout.

**This is a working software prototype. Physical NeoRacer and Unity integration have not been validated.** Both images in self-test mode are synthetic, not physical vehicle footage or AutoDRIVE renders. The earlier Nigel offline simulation is a separate result.

## What the display will look like

![TraCR dual-view layout using the official NeoRacer model on an illustrative course; model preview, not live footage or a Unity run](docs/media/neoracer-preview.gif)

**Official NeoRacer model, scripted preview.** Both panels render the same NeoRacer geometry from the pinned AutoDRIVE source: a virtual onboard perspective on the left and a chase view on the right. This 20-second loop uses WebGL and an illustrative road layout. It is **not physical video, an executed Unity scene or a live synchronization test**.

At the poster session, the **left panel will show the NeoRacer's physical camera**, and the **right panel will show AutoDRIVE following its measured pose** on a surveyed copy of the foam-board roads. That hardware integration and matching map still need to be completed. The preview's course and camera placement are illustrative.

[Open the NeoRacer GIF](docs/media/neoracer-preview.gif) · [View the full-resolution still](docs/media/neoracer-preview.png) · [Model source and reproduction](docs/NEORACER_PREVIEW.md)

The earlier [Nigel / Tiny Town recorded Unity example](docs/PREVIEW.md) is retained separately. Nigel is a different vehicle; its geometry and experiment results are not presented as NeoRacer results.

## Current status

| Component | Status |
|---|---|
| Local dual-view display, timestamp pairing, stale indicators, fullscreen and mobile layout | Implemented; see [validation records](docs/VALIDATION.md) |
| Official NeoRacer geometry in a dual-view animation | Rendered with WebGL; illustrative scripted motion, not Unity or hardware integration |
| Bounded video/pose buffers, one outstanding render request, acknowledgement validation | Implemented and covered by protocol tests |
| USB / RTSP / HTTP MJPEG camera adapter | Implemented; physical camera integration pending |
| Read-only ROS 2 camera and pose adapter | Implemented; JPEG decoding tested, ROS runtime unverified |
| Optional overhead AprilTag localization and calibration tools | Implemented; geometry unit tests pass, physical camera and detection performance unverified |
| AutoDRIVE CoSim follower and render acknowledgement component | C# source provided; not compiled or run in Unity |
| Road importer for an approximately 5 m x 5 m layout | Source provided; the example does not reproduce the physical foam-board map |
| Physical NeoRacer synchronization, measured latency and spatial error | **Unverified; requires field hardware** |
| Autonomous driving control, SLAM and validation of new vehicle dynamics | Outside the current implementation |

## Run without hardware

Use Python 3.10 or 3.11 on the demonstration laptop. Local automated validation used Linux and Python 3.9; Windows and macOS have not been tested on physical machines. The frontend requires no CDN, Node installation or cloud service.

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# On Windows PowerShell, use: .venv\Scripts\Activate.ps1
python -m pip install -e ".[camera,test]"
tracr-demo --self-test
```

Open <http://127.0.0.1:8080>. The display continuously identifies this mode as **SYNTHETIC SELF-TEST**. Stop the service with Ctrl+C.

For live inputs:

```bash
tracr-demo --config configs/demo.json
```

Without physical data, the display shows a waiting state. It does not automatically substitute synthetic images or recorded footage.

## Connect field equipment

1. **Camera:** start an adapter in a second terminal. For a USB camera, use `python adapters/camera.py --source 0`. For an existing RTSP stream, use `python adapters/camera.py --source rtsp://CAMERA_HOST/STREAM`, replacing the placeholder with the actual address. Verify encoding, drivers and connectivity on site.
2. **Localization:** provide measured position and heading in map coordinates. Use `adapters/ros2_readonly.py` with an existing reliable ROS 2 localizer, or `adapters/apriltag.py` if an overhead camera can be installed. Onboard video alone does not automatically provide absolute pose. See [hardware integration and calibration](docs/CALIBRATION.md).
3. **AutoDRIVE:** follow [Unity integration](docs/UNITY.md) to fetch the pinned source and configure the NeoRacer prefab, camera, scene and `TraCRPoseFollower`. Run the Editor or a built player on the laptop.
4. **Map:** follow the [foam-board map workflow](docs/MAP_WORKFLOW.md) to survey the roads and build the matching Unity scene. The current importer supports straight rectangular road segments. The example is not a survey; curves, markings and raised boundaries still need to be modeled.
5. **Rehearsal:** follow the [field runbook](docs/RUNBOOK.md) to verify straight driving, turns, recovery after disconnection, spatial alignment and latency on both views.

The camera, localizer and Unity can start independently. A paired display requires timestamps within tolerance and a Unity acknowledgement matching the correct video and pose IDs. See the [protocol](docs/PROTOCOL.md).

## Repository layout

```text
tracr_demo/        Python service and browser interface without external resources
adapters/          Camera, read-only ROS 2 and overhead AprilTag adapters
unity/             AutoDRIVE follower, render acknowledgement and road importer
configs/           Configuration files and uncalibrated examples
scripts/           Calibration, metrics, upstream fetching and Slurm validation
tests/            Protocol, timestamp, disconnection and coordinate tests
docs/             Deployment, integration, validation, provenance and publishing
upstream.lock.json Pinned upstream source and Unity versions
```

Run `python -m pytest -q` to check software behavior. Browser checks are documented in `docs/VALIDATION.md`. `requirements-tested-linux-py39.txt` records the exact dependencies used for local Linux validation. Install from `pyproject.toml` and repeat acceptance checks on other platforms.

## Gilbreth and GitHub

Substantial computation and browser rendering on Gilbreth must run through Slurm. Prefer `sukkusur / a100-40gb / normal`; use `a30 / standby` only when the group allocation is occupied or committed to queued work. Full demonstrations must not use A10. `scripts/submit_validation.sh` checks group allocations before each submission and stops for review if A30 entitlement changes. See the [GPU constraints](docs/GILBRETH.md). These scheduling checks do not establish Unity Vulkan compatibility on A100/A30.

The repository excludes Unity binaries, large upstream assets, physical vehicle recordings, network credentials and fabricated hardware results. See [publishing and license status](docs/PUBLISH.md) and [provenance](docs/PROVENANCE.md). All repository content must be written in English.
