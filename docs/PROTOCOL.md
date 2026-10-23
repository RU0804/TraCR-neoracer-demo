# Input and rendering protocol

The local HTTP service defaults to `127.0.0.1:8080`. Request bodies are JSON, with a 3 MB limit. JPEG images may be at most 1920 x 1080 and approximately 2 MB of binary data before base64 encoding. Each video/pose ring buffer holds at most 40 entries by default. Only one Unity request may be outstanding; stale data is not queued for later playback.

## Video input

`POST /api/camera`:

```json
{"id":"camera-session:42","capture_time":1790000000.125,"time_basis":"capture","source":"onboard-camera","jpeg":"BASE64_JPEG"}
```

Timestamps are **UTC Unix seconds**. The example illustrates the format; do not send its literal timestamp. Use `time_basis=capture` only when the source provides an exposure/sampling timestamp converted to the service clock. Otherwise use `receipt`. The OpenCV adapter timestamps receipt of a decoded frame and cannot measure latency already introduced by camera encoding, transport or internal buffering.

## Pose input

`POST /api/pose`:

```json
{"id":"localizer-session:42","capture_time":1790000000.125,"time_basis":"capture","source":"real-localizer","frame_id":"map","quality":"localized","x":1.2,"y":0.8,"z":0.0,"yaw":1.5707963268}
```

Map coordinates use a right-handed frame, meters and radians: +x is the zero-heading direction, +y points left, +z points up, and yaw increases counterclockwise from +x toward +y. Position refers to the selected vehicle reference point and must agree with the Unity offset settings. `quality=odometry` identifies relative odometry and keeps a drift warning visible. `quality=test` is reserved for synthetic self-test data.

Report localization loss immediately with `quality=lost`, the current UTC `capture_time` and the appropriate `time_basis`. Loss clears the pose buffer and invalidates outstanding renders. Stopping the stream also triggers a timeout. Do not republish old poses with new sampling timestamps or mix simulated `/odom` into the input.

Numbers must be finite and timestamps must increase monotonically. By default, inputs older than 2 seconds or more than 50 ms ahead of the service clock are rejected. The freshness threshold is 750 ms and the video/pose matching tolerance is 80 ms. These are configurable engineering limits, not measured performance claims.

## Unity requests and acknowledgements

`GET /api/unity/next` returns 204 when no new video can be matched. Otherwise it returns `ticket, frame_id, pose_id, capture_time, pose_time, ux,uy,uz,qx,qy,qz,qw`. The service selects the newest video and its nearest pose in time, without motion prediction or extrapolation.

The map-to-Unity transform matches the pinned `Socket.cs`: position `(-y,z,x)` and planar quaternion `(0,-sin(yaw/2),0,cos(yaw/2))`. For native Socket.IO, use `core.cosim_payload()` to send map coordinates and let Socket.cs perform the transform. Do not apply it twice.

Unity applies the target pose, waits for the chase camera to update, explicitly renders the selected camera, and calls `POST /api/unity/frame`:

```json
{"ticket":"SERVER_TICKET","frame_id":"camera-session:42","pose_id":"localizer-session:42","jpeg":"BASE64_RENDERED_JPEG"}
```

The ticket must exist and both IDs must match exactly. Late acknowledgements (600 ms by default), duplicates and out-of-order responses are rejected. An acknowledgement is the component's assertion that the image used the given pose; it is not independent visual localization or evidence of physical accuracy. Actual Unity integration must verify execution order and other scripts in the scene.

The browser first sends `{"token":"..."}` on `/ws`, then receives status and paired images. After both images decode, the frontend updates them in the same browser animation callback. Network transport and display refresh still add latency; a shared DOM update is not exposure synchronization or synchronized display scanout. Without a matching render, new video is shown while the retained simulation image is marked stale.

## Metrics and clocks

P95 metrics from `/api/status` cover the most recent 600 successful pairs: video timestamp to receipt of the render acknowledgement, and absolute video/pose timestamp difference. They exclude browser transport, decoding and screen refresh. Receipt timestamps also exclude latency that occurred before frame receipt. `clock_verified=false` is the default; set it to true only after recording clock calibration. It is an operator declaration, not an automatic timing measurement.

Align device and laptop clocks with verified NTP/PTP or measured offsets. ROS `use_sim_time` must be disabled. Determine whether each timestamp represents exposure, publication or driver receipt. The ROS adapter also defaults to receipt timestamps; source timestamps require explicit `--capture-timestamps --clock-offset-s OFFSET`. Restarting the service clears sessions and statistics.

## Local network access

Same-machine deployment requires no token by default. Binding a non-loopback address requires `TRACR_TOKEN` with at least 20 characters. HTTP requests use `Authorization: Bearer ...`; the browser accepts the token through a password field and stores it only for the tab session. Unity reads the same environment variable. Do not save tokens in scenes or Git.

Browser cross-origin requests are rejected by default. Plain HTTP is intended for a controlled demonstration LAN; add TLS before using an untrusted network. The service exposes no physical driving, throttle, steering or ROS publishing interface.
