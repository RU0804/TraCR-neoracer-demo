# NeoRacer model preview

![Official NeoRacer model in the dual-view layout](media/neoracer-preview.png)

[Play the 20-second GIF](media/neoracer-preview.gif) · [Generation manifest](media/neoracer-preview.json) · [Media checks](media/neoracer-validation.json)

This preview uses the **official NeoRacer 3D geometry from AutoDRIVE**, replacing the visually different Nigel vehicle in the main README illustration. Both the virtual front camera and chase camera view the same animated NeoRacer and illustrative road scene.

The renderer is Three.js in Chromium WebGL. **This is not an executed AutoDRIVE/Unity scene, a vehicle dynamics simulation, physical footage or a live synchronization test.** The route is scripted, and camera placement is illustrative. The approximately 5 m x 5 m road loop is not a survey or reconstruction of the physical foam-board layout. The frontend's normal live and synthetic self-test modes are unchanged.

The rounded road loop is generated only for this preview. It does not extend the Unity map importer's current support for straight rectangular road segments.

## Model source and conversion

- Repository: [Tinker-Twins/AutoDRIVE](https://github.com/Tinker-Twins/AutoDRIVE/tree/75b7df5216524a3c6b3150d698139190c6c44f8f).
- Geometry: [NeoRacer.fbx](https://github.com/Tinker-Twins/AutoDRIVE/blob/75b7df5216524a3c6b3150d698139190c6c44f8f/Assets/Models/Vehicle/NeoRacer/NeoRacer.fbx), 18,129,712 bytes, Git blob `4bec75b5320467004ac3ae1c5141f378deab282b`.
- The corresponding [NeoRacer prefab](https://github.com/Tinker-Twins/AutoDRIVE/blob/75b7df5216524a3c6b3150d698139190c6c44f8f/Assets/Prefabs/NeoRacer/NeoRacer.prefab) remains the integration target for Unity. Loading its FBX in a browser does not compile or run that prefab's controllers, sensors or other components.
- Unity material remappings supply the base colors, metallic values and smoothness. These are approximated with WebGL materials; Unity HDRP shaders are not reproduced exactly.
- The FBX uses inches (`UnitScaleFactor = 2.54` centimeters per source unit). The renderer reads this binary property directly and converts to meters. It identifies the front and rear axle geometry, rotates their rear-to-front direction to the preview's +Z axis and verifies the alignment. The body is centered horizontally and placed on the road. No hand-drawn vehicle substitutes, image-generation replacements or Nigel meshes are used.
- Cameras, lighting, road geometry and scripted motion are presentation settings, not calibrated NeoRacer measurements or a demonstration of its dynamics.

`configs/preview-assets.lock.json` records each upstream URL and SHA-256. Model files and third-party JavaScript are downloaded to the ignored `upstream/preview-assets/` directory instead of being bundled into the repository. The respective [AutoDRIVE](third-party/AutoDRIVE-LICENSE.txt) and [Three.js](third-party/threejs-LICENSE.txt) notices are preserved.

## Reproduce

With Python, Playwright/Chromium and FFmpeg installed:

```bash
python scripts/fetch_neoracer_preview.py
python -m pip install playwright
python -m playwright install chromium
python scripts/render_neoracer_preview.py --probe
python scripts/render_neoracer_preview.py --ffmpeg /path/to/ffmpeg
python scripts/check_neoracer_preview.py
```

The probe saves four model inspection angles and a mesh/material report in `runtime/neoracer-preview/`. The full renderer writes `docs/media/neoracer-preview.gif`, `docs/media/neoracer-preview.png` and a provenance manifest. Both use the existing frontend HTML/CSS, with recording-only labels applied in the browser. The live application JavaScript is not executed.

On Gilbreth, run both rendering commands inside Slurm, following [the allocation policy](GILBRETH.md). Check `slist` immediately before submission; prefer `sukkusur / a100-40gb / normal`, and use `a30 / standby` when the group A100 allocation is occupied or committed to queued work and A30 entitlement remains absent. Do not use A10. Chromium uses SwiftShader for this geometry preview; its success does not establish native Unity Vulkan compatibility on either GPU.

`scripts/render_neoracer_preview.sbatch` runs the full capture and media checks with four CPUs, 12 GB, one GPU and an eight-minute limit. Submit it from the repository root after checking the allocation. Set `TRACR_BROWSER_PYTHON`, `TRACR_VALIDATION_PYTHON`, `PLAYWRIGHT_BROWSERS_PATH` and `TRACR_FFMPEG` when reusing separate existing environments. The validation Python requires Pillow. Use `--partition=a30 --qos=standby` on `sbatch` only when the allocation rule requires the fallback.

## What still needs to happen for the poster

Import the actual NeoRacer prefab into the laptop's AutoDRIVE scene, build the surveyed road layout, calibrate the physical/virtual coordinate transform and camera view, then connect the camera/localizer and Unity acknowledgement protocol. Follow [Unity integration](UNITY.md), [map reconstruction](MAP_WORKFLOW.md) and the [field runbook](RUNBOOK.md).

The earlier [Nigel/Tiny Town animation](PREVIEW.md) is retained as a separate recorded Unity simulation example. Its controller results and error measurements do not transfer to this NeoRacer geometry preview.
