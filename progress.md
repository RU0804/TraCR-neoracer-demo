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

- Photo-map update: created editable control-point JSON, deterministic sampled geometry, an SVG plan and a Unity importer extension for flat tape strips. Six red stop lines are preserved. Dimensions remain a provisional 4.75 m square. The demo route is an outer-lane partial pass through S2/S6, not a complete lap.
- A100-40GB probe job 12008351 completed in 40 seconds. Four tire groups ground within 1.56 mm; full vehicle bounding footprint samples at <=1 cm spacing remain in the selected lane, with minimum paint clearance 18.49 mm. Stop bumper gaps are 66.18 mm and 70 mm, with two-second dwells. All materials and axle-forward alignment pass.
- Corrected a white/yellow crossing in the initial manual map draft. Map-data validation now confirms six stop lines, 121 sampled paint strips, source hash agreement, bounds, no boundary crossings or self-intersections, and bounded dash lengths.
- Full render attempts 12008368 and 12008372 failed at Chromium startup on A100 nodes n002/n011 (GPU process launch error 1002), before loading the scene. An in-process-GPU trial 12008374 also failed; that flag was reverted. Retrying the previously successful n014 path in job 12008375. No A10 job was submitted. Queued duplicate attempts were cancelled.

- A100 browser probe 12008383 on n014 succeeded. The full render phase of A100 job 12008390 produced 144 frames, a 24-second GIF and the map overview. Its initial exact-byte pause assertion failed on minute rasterization/quantization differences, not vehicle motion. After comparing raw and GIF crops, the checker now requires stopped-image MAE <=0.001 (0-255 scale); actual maximum is 0.000054. Final lightweight media inspection passed in 0.93 seconds: both stops retain 12 stationary frames, 98/99 distinct moving camera regions, all hashes match and all frames decode. The render job's overall FAILED state is retained in the validation narrative.
- Inspected the map plan/overview, grounded car, driving frames and both stop frames. English text/filename and relative-link audit passed across 77 paths. Shared Unity geometry importer remains source-only and uncompiled. Preparing the complete update for public main.

- Sketch revision 2 replaces the earlier inferred contours with the latest hand drawing: diagonal upper section and lower-left branch/island. Six earlier-photo stop lines are retained provisionally near the branch junctions because the sketch has no stop locations. The 4.75 m square scale remains unmeasured.
- Rebuilt shared geometry and the SVG plan; map checks pass with 11 markings, six stop lines, 120 paint strips, source hash agreement and no boundary crossings or self-intersections. An independent full-footprint route calculation gives 35.65 mm minimum sampled white/yellow paint clearance; browser checks and updated media are pending.
- Submitted A100-40GB/normal render job 12011014 after checking group allocation. The previously successful n014 node was fully occupied, so removed the node restriction while excluding the two previously failing Chromium nodes n002/n011; retained the same job and partition. No A10 work submitted.

- Visual review prompted an exact tire-vertex probe in an overlapping Slurm step of job 12011014. It found a residual 14.3 mm gap hidden by the transformed bounding-box approximation. Changed grounding/contact checks to exact transformed tire vertices; the earlier 1.56 mm figure describes approximate boxes, not actual tire contact. Re-rendering is required before publication.

- Initial render job 12011014 produced 150 frames but finished FAILED when its checker briefly required the new contact-method metadata from a scene that had already loaded the old code (KeyError). Those intermediate media will be replaced. Reverted the premature checker requirement; the final render must explicitly contain vertex-based contact metadata. The tire-vertex probe succeeded in the same allocation. Checked slist again (A100 free) and submitted a fresh A100/normal render on n008.

- Final render job 12011020 initially requested n008, but another queued four-hour job took the freed GPU. Removed the node restriction while retaining A100/normal and excluding n002/n011.

- With A100 render 12011020 queued for resources (four-hour estimate), checked group usage and confirmed A30 entitlement remains N/A. Submitted A30/standby replacement 12011021 and cancelled the still-pending duplicate A100 job after rechecking its state. No A10 job was submitted.

- A30 b009 captures at about 2.6 s/frame, so the initial six-minute limit is insufficient for all 150 frames. Slurm denied increasing a running job time limit. Preparing a continuation that reuses completed PNGs after verifying unchanged renderer/map/asset hashes, avoiding a full recapture.

- Prepared hash-checked continuation job 12011028 on A100/normal after confirming the group A100 slot was free; it depends on completion of the current A30 capture to avoid reading an in-progress frame. Completed PNG files are reused only when their PNG signature and end marker are present. The reproducible full-render Slurm template now allows twelve minutes for slower nodes.

- Initial A30 capture 12011021 reached its allocation time limit after saving both complete stop windows. A100 continuation 12011028 remained queued. Rechecked slist (A100 queued, A30 entitlement N/A), submitted the A30/standby continuation, and cancelled the still-pending A100 duplicate after checking its current state.

- A30/standby render and media-check job 12011032 completed on gilbreth-b009 in 00:01:46: 150 frames, 25 seconds, matching artifact hashes, no browser errors/overflow, and 12 stationary frames at each stop. Actual transformed tire vertices are within 0.044 mm of the mat. Browser lane geometry matches the independent calculation: 492 footprint samples, 35.65 mm minimum paint clearance and 70.00/69.26 mm stop gaps. Visually inspected the plan, overview, driving and stop frames. English/source/link checks pass; preparing the verified snapshot for public main.
