# Findings

2026-10-22: Read original HANDOFF.md and README. Existing verified demo: Nigel/Tiny Town Simulator 0.2.0, historical A10 job before policy change. No NeoRacer real-time demo exists yet.

Current Socket_current.cs maps ROS-like pose to Unity: position (-y,z,x), quaternion (qy,-qz,-qx,qw). CoSimManager supports Teleport. Default smoothing resets on each packet and should not be treated as low latency.

Prefer a separate Unity HTTP component for explicit frame attribution (pose id + camera frame id), alongside a pure protocol serializer for the upstream CoSim Socket.IO interface. Stock Bridge image messages have no verified pose-application acknowledgement.

Current group allocation checked: A100-40GB total/queued/running/free = 1/0/0/1; A30 = N/A. Recheck immediately before submission.

Use portable Python service plus browser; avoid hosted-site dependencies because live devices and Unity run locally. Camera is onboard; absolute localization remains a separate input.

Final verification: 28 tests and Chromium checks passed in Slurm A100-40GB job 12006850 (33 s). CPU/browser tests do not validate Unity graphics. Six scheduler/guard checks passed. Connected GitHub profile: RU0804 / Joey Cai; owner and visibility are unconfirmed; no create-repository tool or local gh CLI.

User confirmed GitHub owner RU0804. New repository visibility defaults to private. Remote lookup returns 404; current connection cannot create repositories and local GitHub authentication is unavailable. Waiting for an accessible empty remote, not another owner confirmation.

Repository creation/access blocker resolved by user: public RU0804/TraCR-neoracer-demo, initially empty. Map builder only creates straight rectangular strips; curves, markings, foam walls and photo textures are not currently implemented.

Public repository upload succeeded through connected GitHub Git-data tools. First create_commit call timed out; retry with explicit additional_parent_shas=[] succeeded. Full 50-file source tree matched local. Keep the pre-publication local history on a backup branch when adopting remote main.

English-only audit: Chinese text was confined to 11 Markdown documents. Both binary artifacts are UI screenshots with English labels. Translation preserves the GPU rules, measured-map requirements and hardware/Unity validation boundaries.

README visualization: original presentation assets contain Chinese, so the new English preview uses only the raw Nigel front/scene JPEGs and telemetry. Source intervals are retained at 2x speed and encoded at 6 fps; 136 samples span 46.391 seconds. The existing frontend HTML/CSS provides the layout, with replay labels and simulation metrics applied inside the recording browser only. Live service behavior is unchanged. Slurm A100-40GB job 12008027 rendered the GIF and still in 57 seconds; no Unity session or A10 job was started.

Final media: full-frame palette statistics retain static interface colors better than difference-only statistics. A30/standby job 12008041 produced the final assets and decoded all 145 GIF frames in 52 seconds, after the A100 retry queued with an estimated wait over an hour. The queued A100 retry was cancelled. This is recorded-media processing, not validation of Unity graphics on A30.

NeoRacer model update: the pinned AutoDRIVE source contains an 18,129,712-byte NeoRacer FBX (Git blob 4bec75b5320467004ac3ae1c5141f378deab282b), Unity material remappings and a NeoRacer prefab. The model and preview dependencies were downloaded into ignored upstream/preview-assets and hash-pinned. Existing prebuilt releases do not establish a runnable NeoRacer scene, and no Unity Editor is available here. The new preview renders the official geometry with Three.js/Chromium on Slurm, with explicit model-only labels; this does not execute Unity or validate vehicle dynamics, camera calibration, the physical map or hardware sync.

The source FBX has 210 mesh nodes and uses inches (binary UnitScaleFactor=2.54), but FBXLoader r180 exposes that property as NaN. Read the verified binary property directly. Body orientation must follow the named front/rear axle geometry, not a guess from the body silhouette; an early trial with the wrong sign was cancelled before publication. All FBX materials map to the official Unity material definitions. Generic FBX material-type warnings occur before this explicit remapping; they do not indicate missing final materials.

The user supplied an oblique photo of the foam-mat road layout, identified red tape as stop lines, and estimated the gray footprint at 4.5-5 m. The photo shows a two-lane outer loop, a large central island, a smaller upper-right island and six red line segments. Exact dimensions, corner coordinates and camera calibration are unknown. The previous preview followed the yellow divider itself and added a 12 mm body lift; these are presentation defects, not physical vehicle behavior.

The photo-map preview validates a partial outer-lane route, not every road: 454 footprint samples at <=1 cm spacing, minimum sampled paint clearance 18.49 mm, and front-bumper gaps 66.18/70 mm at S2/S6. The source tire-bottom spread is 1.56 mm. A100 node n014 rendered successfully; Chromium startup failed on n002/n011, with the cause unresolved. Stationary images can differ in a few channel values by one unit before GIF encoding; compare bounded image error rather than demanding byte identity.
