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
