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

2026-10-23 sketch correction: the road outline should have a diagonal upper connection and a lower-left return branch, not the previous upper-right island layout. The latest sketch does not mark stop lines. Six are provisionally retained from the field photo near the two branch junctions while clarification is pending. The original 4.75 m square assumption remains unmeasured. A conservative full-vehicle rectangle check required a small widening of the drafted lower-left outside curve; the current sampled clearance is about 35.65 mm.

Browser checks on A100 node n008 confirm revision 2 uses 492 footprint samples at <=1 cm spacing, 35.65 mm minimum paint clearance, 70.00/69.26 mm stop gaps at S2/S6 and <1.56 mm tire-bottom variation. Visual inspection of the generated plan and top view confirms the diagonal upper road and lower-left branch; the stops remain provisional.

A precise mesh-vertex probe within A100 job 12011014 found that the earlier tire AABB contact calculation was optimistic: transformed local boxes extended about 14.3 mm below the actual tire surfaces. The preview now grounds and validates the four tires using Box3.setFromObject(tire, true), eliminating that residual gap. Actual bottom variation is about 0.044 mm. A new full render is required after this correction.

The corrected vertex-based browser check in A30/standby job 12011021 confirms actual tire-bottom offsets between 0 and 0.04399 mm. Road footprint and stop checks are unchanged. Rendering is in progress on b009.

## Smooth map revision 3
- Local checkout at /scratch/gilbreth/zjcai/TraCR-neoracer-demo is clean and matches public main d35250e.
- Authoritative source: configs/map.photo-v1.json; generator: scripts/build_photo_map.py; browser/Unity input: configs/map.photo-v1.geometry.json.
- Existing uniform Catmull-Rom interpolation causes lateral bulges on intended straights, lower-edge ripples and distorted small-island corners.
- User references retain diagonal upper section, long vertical sides, horizontal lower straight, lower-left return branch and two islands. Preserve nominal scale and provisional six stops; improve geometry explicitly.

- Revision 3 keeps the left/right/bottom main edges exactly aligned; main straight road widths are nominally 0.8 m, return branch 0.7 m. Independently fitted bends are not claimed to be constant-width offsets. Quintic controls enforce zero endpoint second derivative and geometric tangent/curvature continuity, not identical parametric speeds.

- Visually inspected both comparison and stop-free shape PNGs. The revised corners, straight long sides, shoulder and regular lower-left island match the intended sketch topology. A30 job 12011146 passed nine continuity/straightness tests and map topology checks, and rasterized the three standalone views.
- Initial selected route had 17.04 mm minimum sampled paint clearance. Move it 10 mm toward the divider on the bottom/left straights to improve the corner clearance before the final browser run. This does not change road geometry.

- Final revision-3 preview passes with 26.67 mm minimum sampled paint clearance, 70 mm stop gaps and unchanged precise tire grounding. Rendering and media checks completed on A100 job 12011152. The standalone views directly display the shared exported geometry; the archived revision-2 input provides a reproducible before/after comparison.

## Map revision 4
- User requests a longer upper-right diagonal, shorter right vertical, and visible stop IDs before specifying stop relocation. Lower the right shoulder by 0.35 m in the provisional coordinate system for all three parallel contours. Preserve stop IDs and endpoint coordinates. Archived revision-3 source/geometry for the immediate before/after comparison.

- Revision-4 diagonal straight lengths (outer/divider/inner) are 1.685/1.885/2.085 m, increased by about 0.225 m each. Right vertical straights are each 0.35 m shorter. Nine curve tests and expanded topology/stop connectivity checks pass. Standalone labels and revised shoulder shape inspected visually. Browser footprint metrics remain unchanged on the selected bottom/left route.

## Map revision 5
- User specifies S6 level with S5 upper end, S4 level with the small rounded white island upper-left corner, and S1 at the same x as S2. Use y=2.30 for S6, y=3.00 for S4, and x=2.15 for S1.
- S4 ends on the top tangent of the small island corner (x=1.13); leaving its previous x=1.05 would detach it from the rounded border. S1 upper endpoint is intersected with the sampled central-island lower corner to keep it attached at x=2.15. Road geometry and the scripted route are unchanged.

- Revision-5 labeled PNGs visually confirm all three alignments. The two bottom stop segments now share a divider endpoint but retain separate S1/S2 IDs. Browser geometry validation preserves 26.67 mm minimum paint clearance and 70 mm bumper gaps; S6 stop distance advances by 0.75 m along the route to its new location.

## Revision 6 / Stop alignment details

- The small rounded island has left/right sides x=1.05/1.40 and bottom y=3.65. S2 now follows the right-side extension. S3 sits in the adjacent branch lane between the island and branch divider, with its white endpoint at the bottom-right tangent x=1.32. S5 follows the left-side extension and meets the central island lower-left tangent at y=2.22.
- Independent source assertions confirm these three placements, unchanged S1/S4/S6 and road/route geometry, and exactly one label per stop on the standalone map and annotated plan.

- Visually inspected the revision-6 standalone PNG: S2/S5 align with the small island vertical sides, S3 is on the branch-divider left side at the island bottom, and all six labels are legible. Browser route checks pass with 26.67 mm minimum paint clearance and 70 mm stop gaps; the S2 stop advances by 0.75 m along the unchanged route.

## Revision 7 / Final right-side shortening

- Moving the three shoulder vertex pairs down 0.20 m shortens each exact vertical by 0.20 m: outer edge 1.10 to 0.90 m, main divider 0.85 to 0.65 m, central island 0.60 to 0.40 m. This is an 18.2% reduction of the outer right straight. All corner cuts, other vertices, stops and route coordinates are retained.
- Independent source and segment assertions confirm the intended changes.

- Visually inspected the revision-7 standalone PNG. The right outer straight is visibly shorter and all six labels retain their positions. Software 2D SVG capture succeeds; all nine curve tests and topology/connectivity checks pass.

- The browser geometry report identifies revision 7 and preserves the existing route clearance and stop schedule. The same-scale revision-6/revision-7 comparison shows the lowered right shoulder and shorter vertical with all stop positions retained.

## Revision 8 / Confirmed square physical corners

- User clarified that the four corners must be square, not larger round bends. Set central-island cuts 5/7 and small-island cuts 0/2 to zero. All other vertices/cuts and stop alignment axes are retained.
- Updated island endpoints: S1 y=3.65, S3 x=1.40, S4 x=1.05, S5 y=2.30. SVG/WebGL/Unity use miter joins, including the square closed seam at the small island upper-left.
- Remote main remains d35250e before publication; the connected GitHub app has write permission. The publish operation will use a non-forced ref update against the observed parent.
