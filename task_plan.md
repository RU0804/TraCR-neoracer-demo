# TraCR NeoRacer demo implementation plan

## Objective
Create a portable laptop demo repository with left onboard camera and right AutoDRIVE camera driven by measured physical pose. Preserve honest completed/unverified boundaries. GitHub name: TraCR-neoracer-demo. Original Nigel baseline remains untouched.

## Phases
1. Audit handoff and fixed upstream interfaces — complete.
2. Implement bounded timestamped ingest, paired display, source adapters, and Unity integration source — complete; hardware and Unity execution pending.
3. Add configuration, measured-map workflow, laptop runbook and provenance — complete.
4. Validate software in Slurm on allowed resources and package a clean Git repository — complete.
5. Record remaining hardware/Unity acceptance tasks — complete; GitHub publication complete at public RU0804/TraCR-neoracer-demo; source tree verified against local Git. Hardware/Unity acceptance remains pending.

## English-only repository update
- Translate all 11 documents containing Chinese while preserving technical scope and validation boundaries: complete.
- Scan all tracked text and filenames and check screenshots and links: complete (48 text files, two inspected images, no CJK characters or broken links). Publish this verified snapshot to public main.

## README visualization
- Capture the existing page layout using recorded Nigel front and chase views: complete.
- Render the English 2x replay GIF and still through Slurm on allowed resources: complete (A100-40GB job 12008027).
- Final palette adjustment and repeated media checks: complete (A30/standby job 12008041, 52 seconds; queued A100 retry cancelled).
- Animation decoding, source attribution, English-only text and documentation links: verified. Publish the media and reproduction instructions with this documentation update.

## NeoRacer model preview
- Locate and verify the official NeoRacer V1 mesh/prefab and its materials: complete; all imported materials mapped to the pinned Unity material definitions.
- Generate a model-correct 3D preview on an allowed Slurm allocation, without presenting a visual-only renderer as executed Unity integration: complete. Four-angle probe passed on A30 job 12008087. Corrected inch units; an early full-render sample exposed a reversed vehicle, so the first full render was cancelled and replaced by front/rear-axle-based orientation with an explicit alignment check.
- Final A30/standby job 12008196 completed in 3 minutes 45 seconds: 120 decoded frames, 20-second loop, both views changing, all materials matched, no JavaScript errors or overflow.
- Media inspected; Nigel baseline retained separately; English README/provenance and reproduction scripts prepared for publication with this update. Physical hardware and Unity integration remain pending.

## Constraints
- Laptop OS/GPU, video transport and localization are unknown. GitHub owner is confirmed RU0804.
- Physical footprint was reported as 4.5-5 m; a sketch-guided draft now exists at provisional 4.75 m square scale. No measured layout is available; keep the map unmeasured.
- A100-40GB sukkusur/normal first; if occupied or queued use A30/standby after checking slist. No A10. Substantial rendering/tests through Slurm.
- No car control publishers. Do not claim physical hardware, NeoRacer Unity build or field synchronization has been validated.
- /home/zjcai/d2s-diffusion and original baseline outputs must stay untouched.

## Errors
- A documentation tool call had a JS string syntax error before execution; split into smaller calls and completed.
- gh CLI is unavailable; connected GitHub tools can edit existing repositories but do not expose repository creation. Target RU0804/TraCR-neoracer-demo confirmed; get_repo returned 404. This earlier blocker is resolved: user created a public repository and GitHub API access is now available; publishing through connected tools.

## Photo-derived map and vehicle placement
- Reconstruct the supplied oblique photo as an editable approximate vector map, including six red stop lines; provisional 4.75 m square until dimensions are clarified: complete; six stop lines, main loop and branch islands are included.
- Ground the model using the actual tire geometry, remove the extra body lift, and validate a lane-centered route with full vehicle footprint clearance: complete for the selected partial outer-lane route.
- Add scripted stops before the front bumper crosses the relevant red lines; preserve WebGL-only scope: complete; S2/S6 stop gaps and two-second dwell schedule checked.
- Render and inspect a revised GIF plus a map overview on allowed Slurm resources: complete. English documentation and all artifact checks pass; publish the verified snapshot with this update.

## Sketch-guided map revision
- Replace the previous road contours with the user's 2026-10-23 sketch: diagonal upper road, straight left/right sides, broad lower straight, and a lower-left return branch: complete.
- Keep the four-tire grounding and full-footprint checks; rebuild the demo route for the new lanes: complete; browser checks pass with 35.65 mm minimum sampled paint clearance.
- Asked about stop-line retention asynchronously; proceeded with the stated provisional retention assumption while awaiting confirmation. Scale remains unmeasured.
- Render updated plan/overview/GIF on permitted Slurm resources and verify artifacts: complete (A30/standby job 12011032). Publish the verified English repository snapshot with this update.

- Sketch-render trial error: changing the contact metadata assertion while job 12011014 still used its previously loaded scene caused a final KeyError. Removed the premature assertion and scheduled a fresh render; intermediate media are not the publication target.

## Smooth map revision 3 (2026-10-23)
- Locate authoritative map data and inspect existing standalone visualization: complete.
- Replace unconstrained smoothing with exact straights and controlled continuous bends; preserve sketch topology and provisional stops: complete.
- Produce map-only before/after views and regenerate shared geometry: complete.
- Verify topology, continuity, straightness, route clearance and updated preview artifacts on allowed Slurm resources: complete; A30 job 12011146 and A100 job 12011152 passed.
- Document editable files and deliver the local reviewable branch: complete on fix/smooth-sketch-map; no remote push performed.

- Environment note: repository .venv has NumPy/Pillow but lacks Playwright. Reuse existing autodrive-demo/envs/report-check interpreter and pinned browser directory for rendering.

## Map revision 4 / Longer diagonal and stop identifiers
- Lower the right shoulder to lengthen the diagonal and shorten the right vertical: complete.
- Label all six stop lines S1-S6 while keeping their existing IDs and coordinates: complete.
- Regenerate map views, verify geometry, and synchronize preview artifacts: complete; A30/standby job 12011396 passed, with labeled PNGs and a verified revision-4 animation.

## Map revision 5 / User-directed stop placements
- Align S6 with the upper endpoint of S5, S4 with the small island upper-left/top edge, and S1 vertically with S2: complete.
- Snap endpoints to the actual rounded paint boundaries and regenerate labeled views: complete.
- Verify alignments/connectivity and synchronize preview stopping behavior: complete; alignments, nine map tests, topology checks and all preview media checks pass in A100/normal job 12011446.

## Map revision 6 / Small-island stop alignments
- Align S2 with the small island right side, move S3 to the adjacent branch lane at island bottom height, and align S5 with the island left side: complete.
- Regenerate labeled views, verify connectivity and synchronize the relocated S2 stop in the preview: complete; all geometry and media checks pass in A30/standby job 12011483.

- Editing note: a multi-file patch matched only the first document; subsequent replacements verified exact text before updating the remaining documentation. A pending job had not yet created its log, so monitoring uses its queue state until launch.

## Map revision 7 / Shorter right vertical
- Lower all three upper-right shoulder contours by another 0.20 m while retaining all stops: complete.
- Regenerate map views, verify straightness/continuity and synchronize preview artifacts: complete; nine curve tests, topology/route checks and all media checks pass in A30 job 12011937.

- Render error: A30 job 12011935 failed in Chromium Page.captureScreenshot before writing the standalone PNG. Static SVG rendering now disables GPU acceleration; the WebGL renderer retains its existing SwiftShader path.

## Map revision 8 / Final corner correction and publication
- Confirm the four named corners: complete; the user explicitly requires square corners matching the physical course.
- Add explicit zero-cut corners, regenerate maps and a fresh preview, and run release checks: complete; 39 tests and all geometry/media checks pass in A30 job 12012087.
- Publish the verified map/preview update to GitHub main and confirm the remote revision: pending; user explicitly authorized repository update.

- Environment note: Node.js is unavailable in the login environment. The fresh browser render will parse and execute the updated JavaScript; no standalone Node syntax check is claimed.
