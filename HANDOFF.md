# TraCR NeoRacer handoff

This repository continues the work described in `/scratch/gilbreth/zjcai/autodrive-demo/HANDOFF.md`. The target is a laptop demonstration with onboard video on the left and AutoDRIVE NeoRacer on the right, using an approximately 5 m x 5 m foam-board road layout. The earlier Nigel offline results remain separate and unchanged.

## Delivered components

- Python service, browser dual-view display, bounded timestamp matching, stale indicators and self-test mode.
- Camera, read-only ROS 2 and optional overhead AprilTag adapters.
- Unity CoSim follower/render acknowledgement C# source and a road-layout JSON importer.
- Calibration tools, pinned upstream versions, setup and field documentation, automated tests and GitHub CI configuration.
- Historical GIF and still-image layout preview derived from the earlier Nigel / Tiny Town recording, retained separately. Both panels are labeled recorded simulation; see `docs/PREVIEW.md`. These media do not exercise the live bridge or validate NeoRacer integration.
- The main README now shows the official NeoRacer model in a WebGL geometry preview, with virtual front and chase cameras on the photo-derived draft, with a scripted outer-lane pass and stops at S2/S6. See `docs/NEORACER_PREVIEW.md`. This is not Unity execution or a dynamics/hardware test; the Nigel animation is retained separately.

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

The user supplied an oblique course photo and identified six red markings as stop lines. The gray region was described as approximately 4.5-5 m; its aspect ratio is unconfirmed. `configs/map.photo-v1.json` provisionally uses a 4.75 m square and remains unmeasured. `scripts/build_photo_map.py` generates shared browser/Unity strip geometry and an English SVG plan. The revised preview removes the 12 mm body lift, grounds the tires, checks the full CAD bounding footprint against paint and demonstrates stops before the front bumper reaches S2/S6. This is a partial scripted pass, not full-lap or autonomous-driving validation. The updated Unity importer source handles curved tape strips but is still uncompiled. See `docs/PHOTO_MAP.md`.
