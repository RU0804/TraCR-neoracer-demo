# TraCR NeoRacer handoff

This repository continues the work described in `/scratch/gilbreth/zjcai/autodrive-demo/HANDOFF.md`. The target is a laptop demonstration with onboard video on the left and AutoDRIVE NeoRacer on the right, using an approximately 5 m x 5 m foam-board road layout. The earlier Nigel offline results remain separate and unchanged.

## Delivered components

- Python service, browser dual-view display, bounded timestamp matching, stale indicators and self-test mode.
- Camera, read-only ROS 2 and optional overhead AprilTag adapters.
- Unity CoSim follower/render acknowledgement C# source and a road-layout JSON importer.
- Calibration tools, pinned upstream versions, setup and field documentation, automated tests and GitHub CI configuration.
- Historical GIF and still-image layout preview derived from the earlier Nigel / Tiny Town recording, retained separately. Both panels are labeled recorded simulation; see `docs/PREVIEW.md`. These media do not exercise the live bridge or validate NeoRacer integration.
- The main README now shows the official NeoRacer model in a WebGL geometry preview, with virtual front and chase cameras on the sketch-guided draft, with a scripted right-hand outer-lane pass and stops at S6/S2. See `docs/NEORACER_PREVIEW.md`. This is not Unity execution or a dynamics/hardware test; the Nigel animation is retained separately.

See `docs/VALIDATION.md` for software validation. **Physical vehicle integration, Unity C# compilation/builds, NeoRacer rendering and field time/space synchronization remain unverified.** Both self-test images are generated; their accuracy and latency must not be presented as hardware measurements.

## Remaining integration requirements

1. Confirm the presenter's laptop OS and GPU; install the required Unity version and compile the supplied components on that machine.
2. Identify the physical camera interface/ROS 2 topics, localization source and localization quality signals.
3. Obtain a surveyed road layout and define map coordinates and the vehicle reference point. If no map localizer exists, determine whether an overhead camera can be installed.
4. Connect the hardware, calibrate it, and complete the continuous-operation and failure-recovery checks in `docs/RUNBOOK.md`.
5. The user created `RU0804/TraCR-neoracer-demo` and explicitly selected Public visibility. The connected GitHub API has write access and has been used for publication. Do not ask again about the owner or visibility. See `docs/MAP_WORKFLOW.md` for map construction.

Do not turn these unknowns into assumed vehicle specifications or equate available source code with a successful field demonstration. A new Nigel run would not establish NeoRacer integration.

## Resource and repository rules

Follow the user's A100-40GB preference, A30 standby fallback only when the allocation is occupied or queued, and prohibition on A10 for full demonstrations. Submit substantial computation through Slurm; see `docs/GILBRETH.md`. Passing scheduling and browser checks does not validate Unity graphics.

The field deployment uses a local service rather than persistent Gilbreth processes. The original project and `/home/zjcai/d2s-diffusion` were not modified. Existing environments and large upstream files remain in the original project and are not bundled here.

All repository files, documentation, comments, configuration descriptions, diagrams and user-facing text must be in English.

## Photo-derived map update

The user supplied an oblique course photo and identified six red markings as stop lines. The gray region was described as approximately 4.5-5 m; its aspect ratio is unconfirmed. `configs/map.photo-v1.json` provisionally uses a 4.75 m square and remains unmeasured. `scripts/build_photo_map.py` generates shared browser/Unity strip geometry and an English SVG plan. The revised preview removes the 12 mm body lift, grounds the tires, checks the full CAD bounding footprint against paint and demonstrates stops before the front bumper reaches S6/S2. This is a partial scripted pass, not full-lap or autonomous-driving validation. The updated Unity importer source handles curved tape strips but is still uncompiled. See `docs/PHOTO_MAP.md`.

## Sketch-guided revision 2

The 2026-10-23 hand-drawn sketch supersedes the earlier inferred road contours. It has a diagonal upper section, long side straights, a broad lower straight and a lower-left return branch with a small island. The same editable JSON filename now has `revision=2`. The nominal 4.75 m square mat remains unmeasured. The sketch has no stop lines; six lines from the earlier field photo are retained near the two branch junctions as provisional placements, awaiting confirmation. The preview takes the lower/left outer lane and keeps two-second stops at S2/S6.

Revision 2 also corrects a residual approximately 14.3 mm visual ground gap: tire placement and contact verification now use transformed mesh vertices, not the earlier rotated local bounding-box approximation. The old 1.56 mm contact report was a bounding-box result; actual corrected tire-bottom variation is about 0.044 mm.

## Smooth map revision 3

The user requested regular straight sections and smoother, continuous turns. The editable JSON now uses tangent-intersection vertices and `corner_cut_m`, compiled by `scripts/map_curves.py` into exact lines and quintic Bezier fillets with zero endpoint curvature. It retains the diagonal upper road, lower-left return branch and both islands. Stops remain provisional, with their endpoints moved onto the revised paint. The lower/left preview route uses the same curve construction. `docs/media/field-map-only.svg` shows just the map; `field-map-only-shape.svg` omits provisional stops, and `field-map-comparison.svg` compares the archived revision-2 geometry at the same scale. See `docs/PHOTO_MAP.md` for editing and reproduction instructions.

## Map revision 4 / Stop placement review

The user requested a longer upper-right diagonal and shorter right vertical. The shoulder vertices of all three main contours move downward by 0.35 m at the provisional scale; the diagonal straight gains about 0.225 m. Stop IDs S1-S6 and their endpoints are retained, and the standalone map and plan now show offset labels with leaders. `docs/PHOTO_MAP.md` lists all six endpoint pairs. The user intends to specify subsequent placement changes by ID. Revision-3 source and geometry are archived for the immediate before/after comparison.

## Map revision 5 / Requested stop alignments

The user moved S6 upward to the S5 upper-end height (y=2.30), S4 upward to the small rounded white island upper-left/top height (y=3.00), and S1 rightward into alignment with S2 (x=2.15). S4's right endpoint meets the corner top tangent at x=1.13. S1's upper endpoint intersects the sampled central-island lower corner at y=3.64640816; both stop segments meet at the main divider. IDs, road geometry, S2/S3/S5 and the geometric preview route are retained. The animated S6 stop follows its new position. Absolute dimensions remain unmeasured.

## Map revision 6 / Small-island stop alignments

S2 moves left to x=1.40, aligned with the small island right side. S3 moves from the right branch lane to the lane between the small island and yellow branch divider, at island-bottom height y=3.65; its white-boundary endpoint follows the bottom-right tangent at x=1.32. S5 moves left to x=1.05, aligned with the island left side, with its upper endpoint attached to the central island corner at y=2.22. S1, S4, S6, road geometry and the geometric preview route retain revision-5 coordinates. The animated S2 stop is regenerated from its new position. Revision-5 source and geometry are archived for comparison.

## Map revision 7 / Shorter right vertical

The user requested one final shortening of the large loop right vertical. Both upper-right shoulder vertices on the outer edge, main divider and central island move down another 0.20 m at the provisional scale. Their exact right straights change from 1.10/0.85/0.60 m to 0.90/0.65/0.40 m respectively. Corner cuts are retained, so all joins remain tangent- and curvature-continuous. All six stop coordinates, other vertices and preview-route coordinates match revision 6. Revision-6 source and geometry are archived for comparison.

## Map revision 8 / Confirmed square corners and publication

The user explicitly confirmed that four physical corners are square: above S1 and S5, and the small island upper-left/lower-right. Their corner cuts are zero; all other cuts and vertices remain at revision 7. S1/S3/S4/S5 island-side endpoints attach to the new square boundaries while retaining the agreed alignment axes. The sampler supports zero cuts on interior vertices and closed seams. SVG, WebGL and Unity importer tape geometry use miter joins. The Unity source remains uncompiled in this environment. The fresh 24-second preview and map revision 8 are published on GitHub main in commit 69bb49bebadff9a03ee92c68e08f7abbacbf55ba; all 39 tests and media checks pass. The fetched remote source and validation report agree with the reviewed local snapshot.

## Map revision 9 / Right-hand traffic

The preview now travels down the left outer lane and right along the bottom, with S6 then S2 stops. Road contours and all six stop lines retain revision-8 coordinates. The new start is y=1.75 instead of the old endpoint y=2.05, leaving room to stop the front bumper before S6. Browser checks verify the main divider remains on the driver's left and that all stop approaches have positive distance. The stopping solver uses the rotated full-body footprint, including the angled approach to S2. A100 job 12012194 passes 39 tests and media checks: 25 seconds, 150 frames, 511 route samples, 26.73 mm minimum paint clearance and 70 mm gaps at both stops. Revision 9 is published on GitHub main in commit 609bbb69f4f2c0d83f0e1629f7c333a4f659381d; GitHub Actions run 40054969299 passes Python 3.10 and 3.11. The fetched public tree matches the validated snapshot.
