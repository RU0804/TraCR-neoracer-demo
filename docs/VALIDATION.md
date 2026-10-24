# Validation record

Recorded on 2026-10-22. **The service and protocol prototype passed software checks. Physical NeoRacer integration, Unity builds and field spatial/temporal alignment remain unverified.**

## Executed checks

- Slurm job `12006837`: `sukkusur / a100-40gb / normal`, 2 CPUs, 6 GB, 1 GPU, 36 seconds, COMPLETED.
- The first 26 Python tests passed, covering timestamps and numeric validation, nearest-time matching, bounded buffers, coordinate axes, localization loss, incorrect/duplicate/late acknowledgements, no fabricated simulation image when localization is missing, HTTP/WS tokens, JPEG decoding and marker geometry.
- Chromium checks passed for image decoding, synthetic-source labels, desktop 1440 x 1080 and mobile 390 x 844 layouts without horizontal overflow, a connection lasting more than 16 seconds, stale indicators on frozen images after disconnection, no fabricated images in live-input mode, and no JavaScript errors.
- Scheduler simulations passed for selecting an idle A100, falling back to A30 when occupied or queued, refusing to guess when A30 entitlement changes, rejecting malformed allocation output, and refusing full execution on A10.
- Python compilation and shell syntax checks passed. These local results predate the first GitHub Actions run; see the repository's Actions page for subsequent CI results. Windows/macOS have not been tested on physical machines.

After correcting source-timestamp freshness and loopback Host validation, job **12006850** used the same A100-40GB configuration and completed in 33 seconds: **all 28 Python tests and all browser checks passed**. The validation evidence corresponds to that software version.

`requirements-tested-linux-py39.txt` records the tested dependencies. aiohttp emits non-failing recommendations to use AppKey instances; these warnings do not change the recorded results.

## Evidence

`docs/evidence/` contains the synthetic self-test interface, the waiting-for-hardware interface and machine-readable validation summaries. These screenshots are not evidence of physical vehicle or AutoDRIVE operation. The Unity client in HTTP tests is a protocol stand-in; those tests do not start Unity.

To reproduce browser checks, install `playwright` and Chromium. Run `tracr-demo --self-test` and `tracr-demo --port 8081` in separate terminals, then run `python scripts/check_browser.py` in a third terminal. On Gilbreth, use `scripts/submit_validation.sh` rather than running sustained rendering on a login node.

## README preview checks

The [README media](PREVIEW.md) uses recorded Nigel images in the existing frontend layout. Initial rendering completed in Slurm A100-40GB/normal job `12008027` (57 seconds); media checks completed in job `12008032` (10 seconds). Chromium reported no JavaScript errors or horizontal overflow. All 145 GIF frames decoded, the loop duration was 24.17 seconds, and 130 distinct camera-image regions confirmed changing scene content. Artifact checksums matched the generation report.

Final rendering preserved the interface accent colors with a full-frame GIF palette. Job `12008041` on **A30/standby** completed rendering and repeated media checks in 52 seconds: 145 decoded frames, 24.17 seconds, 130 distinct camera regions, matching checksums, no browser errors and no horizontal overflow. Before fallback, `slist` showed A100-40GB `1/1/0/1` and A30 `N/A`; the queued A100 retry `12008036` had a scheduler estimate more than an hour away and was cancelled. No new A10 work or Unity execution occurred. See the [generation manifest](media/preview.json) and [media validation record](media/validation.json).

The PNG and sampled GIF frames were visually inspected for English labels and explicit recorded-simulation status. Text, filenames and relative documentation links were checked separately. These checks concern documentation media only; they do not run the live bridge, physical hardware or Unity.

## Earlier NeoRacer geometry preview

Before the photo-map update, the [NeoRacer preview](NEORACER_PREVIEW.md) used the official pinned AutoDRIVE FBX in WebGL, with a scripted path and illustrative course. A30/standby inspection job `12008087` completed in 33 seconds. That version's render and media checks completed in **A30/standby job `12008196`, 3 minutes 45 seconds**, using four CPUs, 12 GB and one allocated GPU. Chromium used SwiftShader; Unity and native GPU graphics compatibility were not tested.

- All 120 GIF frames decoded; duration is exactly 20 seconds at 6 fps, with infinite looping.
- Both camera-image regions had 120 distinct decoded images; the animation does not only update labels over frozen views.
- The source inch units were read from the FBX binary property and converted to meters. Front/rear axle geometry determines forward orientation, verified against the preview's +Z direction.
- All imported materials mapped to the pinned Unity definitions. Generic FBX material-type warnings precede explicit material conversion; no final material was missing.
- No JavaScript errors or horizontal overflow. PNG/GIF checksums match the generation manifest. The still and sampled GIF frames were visually inspected.
- Source, comments, documentation, filenames and rendered labels were checked for English-only content. The live service and its source files were not changed.

See [generation metadata](media/neoracer-preview.json) and [media validation](media/neoracer-validation.json). A queued A100 inspection request was cancelled after fallback; an early A100 capture was also cancelled when a reversed model was caught during visual review. Those trial images were not published. No new A10 work was submitted.

## Earlier photo-derived map and placement checks

The earlier map draft included the main loop, central and upper-right islands, and six red stop lines. `scripts/check_photo_map.py` checks the shared source hash, footprint bounds, dash lengths, boundary crossings and self-intersections. That revision passed with 11 markings and 121 sampled paint strips. Its scale was a provisional, unmeasured 4.75 m square.

A100-40GB/normal inspection job `12008351` completed in 40 seconds. It reported all four tire-group bounding boxes within 1.56 mm of the mat (the later revision-2 vertex probe found this approximation left an actual mesh gap) and the full CAD bounding rectangle at 454 route samples spaced at most 1 cm apart. Minimum sampled white/yellow paint clearance was 18.49 mm. At S2/S6, the front bumper remains 66.18/70.00 mm before the tape. These are **preview geometry measurements**, not physical-car positioning accuracy or full-course validation.

The render phase of A100-40GB/normal job `12008390` on n014 produced that version's 1200 x 845, 24-second, 144-frame GIF and map overview. The job then failed an initially over-strict bit-identical pause check: inspection found only a few tiny rasterization/quantization differences in stationary camera regions, including one-channel changes of 1 in raw PNGs. The revised checker bounds mean absolute difference to 0.001 on the 0-255 scale instead of requiring identical bytes.

Final lightweight media inspection passed in 0.93 seconds after rendering: all 144 frames decode, both views change during motion (98/99 distinct camera regions), both stops retain 12 stationary camera frames, and the largest stopped-image mean absolute difference is 0.000054. Duration is exactly 24 seconds; all artifact hashes match. The top view, overview, driving and both stop frames were visually inspected. No live frontend behavior changed. The English audit covers all 77 tracked/candidate paths with no CJK text or broken local Markdown links.

Chromium startup failed on A100 nodes n002/n011 before scene loading (GPU-process launch error 1002); an in-process-GPU trial also failed and was reverted. A subsequent browser probe on n014 succeeded. Successful WebGL rendering on that node does not establish general native Unity graphics compatibility. No A10 was used.

## Not executed; no passing claim is justified

- AutoDRIVE NeoRacer scene import, C# compilation, camera rendering or a standalone application build.
- Unity graphics API compatibility on the demonstration laptop or permitted Gilbreth GPUs.
- Physical camera and ROS 2 integration, marker detection performance or recovery from real occlusion.
- Metric road survey, map/vehicle reference-point calibration or measured spatial error.
- Device clock calibration, exposure-to-screen latency, physical frame rate or dropped-frame rate.

Self-test frame rates, P95 values and zero timestamp differences come from data generated in the same process. They are software smoke-test results, not hardware performance measurements.

## Sketch-guided revision 2

The latest hand-drawn sketch replaces the earlier inferred outline with a diagonal upper road and a lower-left return branch. The six stop lines are provisionally relocated from the earlier photo; the sketch supplies no stop locations. The nominal 4.75 m square remains unmeasured. Map checks pass with 11 markings, six stops, 120 paint strips, matching source hashes, no boundary crossings and no self-intersections.

A30/standby job `12011032` completed on `gilbreth-b009` in 00:01:46. The initial A30/standby capture job 12011021 reached its six-minute allocation limit; the final job reused complete PNGs and captured the remaining frames after checking unchanged renderer, map and asset-lock hashes. The full-render Slurm template now allows twelve minutes for slower nodes. The browser checks 492 full-vehicle rectangles at intervals no greater than 1 cm. Minimum sampled white/yellow paint clearance is 35.65 mm; stop gaps at S2/S6 are 70.00/69.26 mm. All four actual tire bottoms remain within 0.044 mm of the mat. Grounding now uses transformed mesh vertices: a separate probe found that the earlier approximate boxes left about 14.3 mm of actual mesh clearance, despite the old contact report. That residual visual gap is corrected in this render. These checks cover the selected partial route, not every lane, a complete lap or vehicle dynamics.

The updated GIF is 1200 x 845, 25 seconds and 150 frames. Every frame decodes, artifact hashes match, both camera views change during motion (105/104 distinct cropped regions), and each stop retains 12 stationary frames. Maximum stopped-image mean absolute difference is 0.00009068, below the 0.001 limit on a 0-255 scale. The render reports no JavaScript errors or horizontal overflow. The plan, overview, driving and stopping frames were visually inspected. Python/JavaScript syntax, English-only content and local Markdown links pass checks.

This remains a WebGL geometry preview. Unity compilation/execution, physical camera input, metric map survey and live synchronization remain unverified.

## Smooth map revision 3

The map source replaces unconstrained Catmull-Rom interpolation with exact straight segments and quintic corner fillets. The curve tests check tangent direction and zero endpoint curvature at every join, including closed seams, straightness on the long sides, a maximum 8 mm sampling chord and rejection of overlapping corner cuts. The source and shared geometry retain revision 3, six provisional stops and the sketch's two-island topology.

A30/standby job `12011146` completed on `gilbreth-d001` in 49 seconds: nine map tests passed, the shared geometry has 11 markings and 119 paint strips, its source hash matches, and the checker found no boundary crossings or self-intersections. Standalone map, stop-free shape and same-scale before/after views were rendered and visually inspected. A follow-up step in job `12011152` reran all nine map tests and the expanded topology checks on the final source: all stop endpoints touch their intended paint, both branch endpoints meet the main divider, and there are no boundary crossings or self-intersections.

The final A100-40GB/normal browser run checks 481 full-vehicle rectangles at intervals no greater than 1 cm along the revised partial route. Minimum sampled white/yellow paint clearance is 26.67 mm, above the existing 15 mm threshold, and both front-bumper stop gaps are 70 mm. The lower/left route was moved 10 mm toward the divider to improve clearance through the regularized corner. These are geometric checks of the selected demonstration route, not whole-course drivability or vehicle dynamics.

A100-40GB/normal job `12011152` completed on `gilbreth-n009` in 6 minutes 24 seconds. The refreshed 1200 x 845 GIF contains 144 decoded frames over 24 seconds. All recorded artifact hashes match; S2 and S6 each retain 12 stationary frames, with maximum stopped-image mean absolute difference 0.000133 (limit 0.001). There are no browser errors or horizontal overflow. The map overview, S2 still and decoded driving frame were visually inspected. Geometry and SVG regeneration is deterministic, and English-only content and local documentation links pass. Unity compilation, full-course driving and physical measurements remain unverified.

## Map revision 4 / Longer diagonal and numbered stops

Revision 4 moves the upper-right shoulder down by 0.35 m on each of the three main contours. Each exact diagonal straight is about 0.225 m longer and each right vertical is 0.35 m shorter. All six stop IDs and endpoint pairs match the revision-3 source exactly. The standalone map and annotated plan each contain one visible S1-S6 label; SVG XML checks confirm uniqueness, and the rendered PNGs were visually inspected for placement and legibility.

A30/standby job `12011396` passes all nine curve/straightness tests. Its topology checks report 11 markings, six stops, 118 paint strips, matching source hash, no boundary crossings or self-intersections, connected branch endpoints and stop endpoints on the lane markings. Browser checks on the unchanged partial route retain 481 footprint samples, 26.67 mm minimum paint clearance and 70 mm stop gaps.

Job `12011396` completed on `gilbreth-b008` in 4 minutes 35 seconds. The synchronized 24-second preview has 144 decoded frames, matching artifact hashes, 12 stationary frames at each stop and passing stopped-image checks. Both camera views change during motion, with no browser errors or horizontal overflow. English-only content and local documentation links pass. All six endpoint pairs in the stop-ID table match the editable source.

## Map revision 5 / Stop-line alignments

The user moved S6 to the S5 upper-end height (y=2.30), S4 to the small island top at its upper-left corner (y=3.00), and S1 onto the same vertical as S2 (x=2.15). Independent assertions check these alignments, unique labels, and unchanged road geometry, S2/S3/S5 and preview-route coordinates. S4's endpoint follows the corner top tangent at x=1.13; S1's upper endpoint is intersected with the sampled lower white curve at y=3.64640816. These intersection digits express geometric attachment, not survey accuracy.

A100-40GB/normal job `12011446` passes all nine curve tests and the topology/connectivity checks: six stops, 118 paint strips, no crossings or self-intersections, connected branch endpoints and maximum stop endpoint error below 1.5e-9 m. The labeled standalone and before/after PNGs were visually inspected. The browser checks revision 5 with the stop schedule recomputed from the relocated S6.

Job `12011446` completed on `gilbreth-n016` in 4 minutes 37 seconds. All 144 frames of the 24-second preview decode and artifact hashes match. Both stops retain 12 stationary frames; maximum stopped-image mean absolute difference is 0.00004421, below the 0.001 limit. Browser geometry checks retain 481 footprint samples, 26.67 mm minimum paint clearance and 70 mm bumper gaps at S2 and the relocated S6. This validation covers the selected scripted WebGL route.

## Map revision 6 / Small-island stop alignments

Independent assertions confirm S2 at x=1.40 (small island right side), S3 at y=3.65 in the branch lane between the small island and yellow divider, and S5 at x=1.05 (island left side). S3 attaches to the island bottom tangent at x=1.32; S5 attaches to the central island corner tangent at y=2.22. Road contours, route coordinates, S1/S4/S6 and all stop IDs match revision 5. Standalone and plan SVGs each contain one label per stop. A30/standby job `12011483` passes all nine curve tests and topology/connectivity checks: 118 paint strips, matching source hash, no crossings or self-intersections, connected branch endpoints and maximum stop endpoint error below 1.5e-9 m. The labeled map was visually inspected. Browser geometry checks retain 481 footprint samples, 26.67 mm minimum paint clearance and 70 mm bumper gaps. S2 now stops at route distance 1.625627 m, 0.75 m farther along the pass than in revision 5. The final 24-second animation has 144 decoded frames, matching artifact hashes and 12 stationary frames at each stop. Maximum stopped-image mean absolute difference is 0.00015471, below the 0.001 limit. The relocated S2 stop frame was visually inspected. Job `12011483` ran on `gilbreth-b006`. These checks cover the scripted WebGL preview.

## Map revision 7 / Final right-side shortening

Independent source comparisons confirm that only the two upper-right shoulder vertices on each of the outer edge, main divider and central island move, each by +0.20 m in plan y. All six stops, other vertices, corner cuts and preview-route coordinates match revision 6. Exact segment calculations show right vertical lengths of 0.90/0.65/0.40 m, each 0.20 m shorter. Straightness-test sampling windows move inside the shortened straight portions. The first A30 render job `12011935` failed before capture with a Chromium screenshot protocol error. Static SVG capture now disables GPU acceleration; the WebGL renderer retains its existing SwiftShader path. A30/standby retry `12011937` on `gilbreth-d001` successfully renders the standalone maps and passes all nine curve tests. Topology checks report 118 paint strips, matching source hash, no boundary crossings or self-intersections, connected branch endpoints and maximum stop endpoint error below 1.5e-9 m. The new labeled map was visually inspected. Browser checks at revision 7 retain 481 vehicle-footprint samples, 26.67 mm minimum paint clearance and 70 mm front-bumper gaps at S2/S6. The lower/left preview route and stop schedule remain unchanged. Job `12011937` completed on `gilbreth-d001` in 10 minutes 44 seconds. The 24-second revision-7 preview contains 144 decoded frames, matching source/artifact hashes and 12 stationary frames at each stop. Maximum stopped-image mean absolute difference is 0.00010735, below the 0.001 limit. All media checks pass.

## Map revision 8 / Confirmed square corners

The user confirmed four physical right-angle vertices: central island (2.10, 3.65) and (1.05, 2.30), and small island (1.05, 3.00) and (1.40, 3.65). Independent assertions confirm that only those cuts become zero, that all other vertices/cuts and the route are retained, and that stop alignment axes are unchanged. Island-side endpoints on S1/S3/S4/S5 now meet the square boundaries. SVG/WebGL/Unity use miter joins, including closed seams. Regression tests exercise sharp open-path vertices and closed square seams as well as continuity at the remaining fillets. A30/standby job `12012087` on `gilbreth-b000` passes all 39 tests (including 11 map tests), with 18 existing aiohttp AppKey warnings. Topology checks report matching source hash, 118 paint strips, no crossings or self-intersections, connected branch endpoints and stop endpoint error below 1e-18 m. Explicit SVG path closure preserves the square corner at the loop seam; a Slurm step regenerates the standalone PNGs after this SVG fix. The revision-8 browser reports 481 footprint samples, 26.67 mm minimum paint clearance and 70 mm bumper gaps at S2/S6. The labeled map was visually inspected. Job `12012087` completed on `gilbreth-b000` in 8 minutes 13 seconds. All 144 frames of the 24-second preview decode, source/artifact hashes match and both stops retain 12 stationary frames. Maximum stopped-image mean absolute difference is 0.00015471, below the 0.001 limit. The revised map and S2 still were visually inspected. All media checks pass. Unity compilation remains unverified.

Published revision 8 in [commit 69bb49b](https://github.com/RU0804/TraCR-neoracer-demo/commit/69bb49bebadff9a03ee92c68e08f7abbacbf55ba). Both Python 3.10 and 3.11 jobs in [GitHub Actions run 40053311260](https://github.com/RU0804/TraCR-neoracer-demo/actions/runs/40053311260) succeeded. The fetched remote tree matches the reviewed local index, including the map and preview artifacts.

## Map revision 9 / Right-hand traffic

The route now travels down the left outer lane and right along the bottom, with S6 then S2 stops. Independent comparisons show every road strip, stop endpoint and corner parameter is identical to revision 8. The new start extends the reversed route by 0.30 m to provide a valid approach to S6. Geometry/SVG regeneration is deterministic.

The browser verifies that the nearest main-divider point stays on the driver's left at every footprint sample. The old direction fails an independent signed-offset check. The stopping solver uses the rotated full-body footprint: the old half-length approximation would leave only 59.48 mm at S2 when approaching through the bend; the new solver preserves the configured 70 mm gap. Invalid stop order and insufficient approach distance are rejected before capture.

A100-40GB/normal job 12012194 on gilbreth-n007 passes all 39 tests and the map topology checks. Its browser checks 511 full-body footprints with at most 1 cm spacing, minimum paint clearance 26.73 mm, positive divider-left offset of at least 190 mm and 70 mm stop gaps at both S6 and S2. Four tire contacts remain within the 2 mm tolerance. The direction plan and S6 still were visually inspected. All 150 GIF frames decode over 25 seconds, artifact/source hashes match and both stops retain 12 stationary camera frames. Maximum stopped-image mean absolute difference is 0.00006880 (limit 0.001). Both camera views change during motion, with no browser errors or horizontal overflow. S2 was also visually inspected. All media checks pass; English-only content and local links pass. These results cover the scripted WebGL route, not Unity execution or physical driving.

The initial job 12012174 stopped at an existing real-time service test: the WebSocket received a video fallback instead of a fresh pair. That code uses a 0.75 s freshness window. The unchanged test passed independently in 0.41 s and all 39 tests passed on retry. No live-service code was changed. Early capture 12012180 was deliberately cancelled after its geometry report exposed the angled S2 stopping gap; 12012194 rerenders all frames with the corrected solver.

Published revision 9 in [commit 609bbb6](https://github.com/RU0804/TraCR-neoracer-demo/commit/609bbb69f4f2c0d83f0e1629f7c333a4f659381d). Both Python 3.10 and 3.11 jobs in [GitHub Actions run 40054969299](https://github.com/RU0804/TraCR-neoracer-demo/actions/runs/40054969299) succeed. A100 job 12012194 completed in 4 minutes 21 seconds; the fetched public tree and revision-9 media match the verified snapshot.
