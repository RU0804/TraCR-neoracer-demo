# AutoDRIVE / NeoRacer Unity integration

**The deliverable is integration source code. Unity Editor is unavailable in the current environment, and the NeoRacer scene has not been compiled, built or run here.** HTTP protocol tests use a stand-in Unity client and do not replace the acceptance checks below.

## Versions and import

1. On the laptop, run `python scripts/fetch_autodrive.py` from the repository root. It downloads only the source pinned in `upstream.lock.json`; it does not install system packages or run vendor installers. Allow sufficient disk space and download time for Unity assets. After an interrupted download, preserve or manually move the incomplete directory and retry into an empty destination.
2. Open `upstream/AutoDRIVE-Simulator` with Unity **2022.3.52f1**, as required by the pinned source. If Git LFS assets are still pointers, run `git lfs pull` in that repository and verify the assets. Test the graphics API and driver on the actual demonstration laptop.
3. Copy `unity/TraCRPoseFollower.cs` into the upstream project's `Assets/TraCR/` directory and `unity/TraCRMapBuilder.cs` into `Assets/TraCR/Editor/`.
4. Select a NeoRacer scene, such as `NeoRacer - AuE-X930`, or place `Assets/Prefabs/NeoRacer/NeoRacer.prefab` in a separate scene copy. The older Nigel 0.2.0 binary is not a NeoRacer build.
5. Save a separate scene copy and preserve the upstream scene. Import surveyed roads using `TraCR / Import measured road layout JSON`. `configs/map.example.json` is **ILLUSTRATIVE ONLY** and must not be treated as the measured course. The importer adds only ground and road blocks; markings, foam-board boundaries, signs and curve details still require modeling from measurements.

## Follower configuration

Create a `TraCR Bridge` GameObject and attach `TraCRPoseFollower`:

- Assign the NeoRacer `CoSimManager` to `CoSim`, with its `VehicleRigidBody` pointing to the vehicle's actual rigidbody. If the prefab lacks this component, add it to the correct vehicle parent and assign the reference.
- Assign the actual right-panel Unity camera to `DisplayCamera`. Use an onboard camera for a similar viewpoint, or a third-person chase camera. Select one view and keep it consistent during rehearsal.
- Explicitly list the original Socket behavior, vehicle/drivetrain controllers and any other rigidbody writers in `DisableWhileFollowing`. The display pipeline does not start the physical vehicle command chain. Verify that no second program continues to overwrite the virtual pose.
- Disconnect the original Socket.IO connection and stop its server/client first. Disabling a MonoBehaviour does not automatically unregister existing Socket event callbacks; the component-disable list alone is insufficient.
- Set `ServerUrl=http://127.0.0.1:8080`. If a token is configured, set `TRACR_TOKEN` in the environment that launches Unity Hub/Editor or the Player, rather than saving it in the scene.
- Set `BodyOriginOffset` to the offset from the mapped vehicle reference point to the prefab rigidbody origin, in meters and vehicle coordinates: +x forward, +y left, +z up. `PrefabYawOffsetDegrees` only corrects model orientation. Verify the origin and cardinal headings before changing signs.
- After checking all references, enable `FollowMeasuredPose` in the Inspector. The component uses kinematic pose following, disables competing controllers and captures the camera after applying each target. Unchecking it or disabling the component restores controller enable states and rigidbody settings. Recheck the initial state before returning to dynamics-driven operation.

The component uses upstream CoSim target fields and direct rigidbody updates to avoid unspecified lag from default smoothing. It does not depend on legacy Socket.IO libraries or claim that legacy Bridge images have verified sampling-time associations. `core.cosim_payload()` is only a reference serializer for the native protocol; a complete scene-compatible Socket.IO server is not implemented.

Camera capture currently uses `Camera.Render()` in the built-in render pipeline. URP/HDRP requires the appropriate pipeline capture hook and separate validation. Chase-camera interpolation can affect the view; the vehicle itself performs no dynamics prediction. `WaitForEndOfFrame` requires normal rendered frames and is unsuitable for `-nographics` or an Editor state where the Game view does not update.

## Required practical checks

- Verify position and orientation at map (0,0), along +x and +y, and at yaw 0, +90 and 180 degrees. Check the body reference point and tire/ground height.
- Confirm that the right panel uses the selected camera on the NeoRacer prefab and responds to known inputs, rather than showing the earlier Tiny Town Nigel images.
- Ensure no other script changes the vehicle before or after capture. Use the Inspector/Profiler to measure rendering and encoding rates and CPU/GPU use.
- On localization loss, the virtual vehicle should hold its last position and the webpage should mark the image stale. Recovery must produce new valid pairs.
- Build and cold-start the application on the actual laptop. Check offline networking, screen resolution, power settings and the projector/external display.

Official references: [CoSimManager](https://github.com/Tinker-Twins/AutoDRIVE/blob/75b7df5216524a3c6b3150d698139190c6c44f8f/Assets/Scripts/CoSimManager.cs) and [Socket coordinate conversion](https://github.com/Tinker-Twins/AutoDRIVE/blob/75b7df5216524a3c6b3150d698139190c6c44f8f/Assets/Scripts/Socket.cs).
