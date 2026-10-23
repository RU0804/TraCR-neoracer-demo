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
- Physical footprint was reported as 4.5-5 m; a photo draft now exists at provisional 4.75 m square scale. No measured layout is available; keep the map unmeasured.
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
