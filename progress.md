# Progress

- Read handoff, GPU preferences, source-level CoSim mapping and baseline README.
- Asked for laptop platform and current camera/localization interfaces; awaiting answer.
- Created independent project directory. Original baseline and d2s-diffusion were not modified.

- Implemented bounded video/pose buffers, finite-value/frame validation, timestamp pairing and one outstanding Unity render ticket.
- Added local browser display with explicit self-test watermark, stale-state indicators and pair timestamp metrics.
- Added USB/RTSP/MJPEG, read-only ROS 2 and optional AprilTag source adapters. Hardware integration remains unverified.
- Added AutoDRIVE CoSim HTTP follower and Unity editor road-layout importer. C# source has not been compiled or executed.
- Upstream simulator pinned to 75b7df5216524a3c6b3150d698139190c6c44f8f; editor 2022.3.52f1 confirmed from primary source.
- First software validation: 26 tests and browser checks passed on Slurm A100-40GB job 12006837 (36 s). No real car or Unity validation.
- Review found freshness should depend on source timestamp, not recent render arrival; fixed and added a regression case. Added loopback Host validation.
- One documentation-writing tool call had a JavaScript string syntax error before execution; retried in smaller calls, no partial writes from the failed call.

- Final software validation: 28 tests passed; browser checks passed; six GPU-selection/guard checks passed. Slurm job 12006850, A100-40GB normal, 33 s, completed.
- Wrote Chinese setup, Unity integration, calibration, runbook, provenance, publishing and validation documentation; snapshots explicitly label self-test.
- Prepared standalone Git repository and source archive, excluding environments and upstream assets. Hardware/Unity acceptance and GitHub destination remain pending.

- User confirmed RU0804 as GitHub owner. Target RU0804/TraCR-neoracer-demo queried via connected GitHub API: 404 (missing or inaccessible). No create-repository tool, local gh login, token environment or SSH agent. Configured origin and updated publication instructions; no upload claimed.

- User created RU0804/TraCR-neoracer-demo as public. Confirmed repository is empty and current connection has push permission. Preparing source publication through GitHub API.
- Added MAP_WORKFLOW.md explaining measured foam-board map reconstruction, coordinate alignment, current straight-segment importer limits, and optional future photo-texture workflow. No physical map has been fabricated.

- GitHub source tree upload matched the local Git tree. First create_commit call timed out after 300 s; inspecting remote refs before retry. No full-publication claim made.

- Retry with explicit empty additional-parent list succeeded. Published the complete 50-file source snapshot to public main and verified identical local/remote Git trees. Final publication notes are included in the follow-up documentation commit.

- English-only update: translated all 11 documents containing Chinese, including command comments and Mermaid labels. Source code, configuration and UI were already English. Both committed screenshots were visually inspected and contain English text. Added the English-only requirement to AGENTS.md and HANDOFF.md.
- English-only verification passed across all 50 tracked paths: 48 text files (including escaped Unicode and HTML entities), two visually inspected English screenshots, and all relative documentation links. No application behavior changed.

- Added README visualization using the historical Nigel / Tiny Town front and chase images. Both panels have permanent recorded-simulation labels. The field map and physical NeoRacer remain pending.
- Slurm A100-40GB/normal job 12008027 generated a 1200 x 859 GIF and PNG in 57 seconds, with no browser errors or horizontal overflow. Source files remain untouched; the live frontend and protocol were not changed.
- Improved the GIF palette to retain static UI colors. With an A100 retry queued and A30 entitlement still absent, submitted A30/standby job 12008041 and cancelled the duplicate queued A100 job 12008036. Final render and media validation completed in 52 seconds: 145 frames, 24.17 seconds, 130 distinct camera regions, checksum matches and no browser errors. The final GIF, PNG, source manifest, validation record and reproduction instructions are prepared for publication with this update.

- User requested the correct NeoRacer model in the preview. Downloaded the official pinned AutoDRIVE FBX, prefab and materials plus pinned Three.js files into an ignored cache, preserving their license notices separately. No Unity Editor or confirmed prebuilt NeoRacer scene is available in this environment.
- A30/standby probe job 12008087 completed in 33 seconds after the preferred A100 job queued and was cancelled. Four model views showed NeoRacer geometry and branding, 210 meshes, 599,035 rendered triangles including the illustrative course, and no unmatched materials or JavaScript errors. Fixed the renderer to read UnitScaleFactor=2.54 directly. An early frame of A100 full-render job 12008116 exposed a reversed vehicle; cancelled that run and replaced the guessed heading with an orientation derived from the named front/rear axle geometry, with an explicit +Z alignment check.
- Final A30/standby job 12008196 completed rendering and media validation in 3 minutes 45 seconds. Output: 1200 x 845, 20 seconds, 120 frames, approximately 3.2 MB GIF. Both views have 120 distinct image regions, every material is mapped, source units and forward alignment pass checks, and browser errors/overflow are absent. The model is approximately 0.268 x 0.216 x 0.454 m in the preview, from the source mesh units; these are not measurements of the user's physical car.
- Replaced the main README illustration with the official NeoRacer geometry preview, preserving the historical Nigel media separately. Added hash-pinned asset fetching, rendering/validation scripts, Slurm reproduction, third-party notices and explicit WebGL/Unity/hardware boundaries. No runtime application behavior changed.
