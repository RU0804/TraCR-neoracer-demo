# Sketch-guided foam-mat course

![Map plan with six red stop lines](media/field-map-plan.svg)

Revision 2 follows the user's hand-drawn road sketch supplied on 2026-10-23. It replaces the earlier photo-inferred outline with a diagonal upper section, long left and right sides, a broad lower straight, a large central island and a **lower-left return branch** around a smaller island. White edges and yellow dividers use smoothed editable control points.

The sketch does not show stop lines. The six red stop lines from the earlier field photo are provisionally relocated to the two branch junctions, with IDs S1-S6 retained. Their positions require confirmation. This is a manual interpretation of the sketch, not calibrated photogrammetry or a metric survey. The existing `map.photo-v1.json` filename remains the editable entry point; its `revision` field is now 2.

The reported gray footprint is approximately 4.5-5 m. Pending confirmation of both dimensions, the draft assumes **4.75 m x 4.75 m**. Lane widths, curve radii and stop-line positions are approximate. `measured` remains `false`. The classroom photograph is not included in the repository.

[Top-down WebGL rendering](media/field-map-overview.png) · [Editable JSON](../configs/map.photo-v1.json) · [Shared sampled geometry](../configs/map.photo-v1.geometry.json)

## Edit and import

1. Edit the meter-valued control points, widths, stop-line endpoints and footprint in `configs/map.photo-v1.json`. Changing only `width_m` or `height_m` changes the mat size, **not** the coordinates; rescale or remeasure the points as well.
2. Run `python scripts/build_photo_map.py`, followed by `python scripts/check_photo_map.py`, to regenerate and check `configs/map.photo-v1.geometry.json` and the SVG plan. The generated file records its source SHA-256.
3. To reproduce the browser preview, follow [the rendering instructions](NEORACER_PREVIEW.md). Rendering and encoding must run in an allowed Slurm allocation on Gilbreth.
4. In the AutoDRIVE Unity project, use `TraCR / Import road layout JSON` and select the generated `.geometry.json`, not the control-point file. The importer creates the flat mat and sampled curved tape strips. The C# changes remain uncompiled and unexecuted in this environment.

The map origin is the far-left mat corner in this plan; +x points right and +y points toward the near edge. Units are meters. The Unity importer uses `(-y, height, x)`, consistent with the pose bridge. The WebGL preview centers and rotates this plan for presentation. Grid seams are illustrative and do not establish actual foam-tile dimensions.

The sampled strips are shared across SVG, WebGL and Unity. Yellow dashes are split by arc length before export, so the importer does not invent a different dash pattern. Stop lines are flat red geometry with IDs S1-S6. Importing them does **not** implement stop detection or vehicle control.

## Vehicle placement and scripted stops

The official NeoRacer mesh uses its original source units and axle-derived forward direction. Ground placement uses the transformed mesh vertices of the four named tire groups. The earlier approximate bounding boxes extended about 14.3 mm below the actual tire surfaces; revision 2 corrects this remaining gap as well as retaining removal of the previous 12 mm body lift. The actual tire bottoms vary by about 0.044 mm; the preview checks a 2 mm contact tolerance and reduces shadow bias.

The selected route is a **partial clockwise pass in the outer lane**, along the lower straight, around the lower-left turn and up the left side. It is offset from the yellow divider. The checker samples the complete CAD bounding rectangle at intervals no greater than 1 cm, requiring it to remain inside the outer white boundary and outside the yellow divider, with clearance from every white/yellow marking. This checks the rendered footprint; it does not validate a steering model or the whole course.

The animation accelerates and brakes along that route, stopping with the front bumper before **S2**, waiting two seconds, and repeating at **S6**. The nominal bumper gap is 7 cm; geometric verification includes tape width and heading. The other four stop lines belong to lanes/branches not traversed in this preview. The final hold is labeled as a completed pass before the GIF restarts.

For live synchronization, measured vehicle poses must drive the virtual car. Do not make the virtual car stop independently while the physical car continues. This preview's stopping schedule is not connected to the physical vehicle or the live service.

## Before the poster session

Measure the mat's two dimensions, lane widths, stop-line endpoints and several independent road reference points. An overhead image will improve the contours. Refine the map, rerun the footprint checks for the intended route, import it into Unity, and verify the real vehicle reference point and camera calibration at several locations. A measured map and successful laptop rehearsal are still required.
