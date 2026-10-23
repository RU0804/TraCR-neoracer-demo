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

## NeoRacer geometry preview

The [NeoRacer preview](NEORACER_PREVIEW.md) uses the official pinned AutoDRIVE FBX in WebGL, with a scripted path and illustrative course. A30/standby inspection job `12008087` completed in 33 seconds. The final render and media checks completed in **A30/standby job `12008196`, 3 minutes 45 seconds**, using four CPUs, 12 GB and one allocated GPU. Chromium used SwiftShader; Unity and native GPU graphics compatibility were not tested.

- All 120 GIF frames decoded; duration is exactly 20 seconds at 6 fps, with infinite looping.
- Both camera-image regions had 120 distinct decoded images; the animation does not only update labels over frozen views.
- The source inch units were read from the FBX binary property and converted to meters. Front/rear axle geometry determines forward orientation, verified against the preview's +Z direction.
- All imported materials mapped to the pinned Unity definitions. Generic FBX material-type warnings precede explicit material conversion; no final material was missing.
- No JavaScript errors or horizontal overflow. PNG/GIF checksums match the generation manifest. The still and sampled GIF frames were visually inspected.
- Source, comments, documentation, filenames and rendered labels were checked for English-only content. The live service and its source files were not changed.

See [generation metadata](media/neoracer-preview.json) and [media validation](media/neoracer-validation.json). A queued A100 inspection request was cancelled after fallback; an early A100 capture was also cancelled when a reversed model was caught during visual review. Those trial images were not published. No new A10 work was submitted.

## Not executed; no passing claim is justified

- AutoDRIVE NeoRacer scene import, C# compilation, camera rendering or a standalone application build.
- Unity graphics API compatibility on the demonstration laptop or permitted Gilbreth GPUs.
- Physical camera and ROS 2 integration, marker detection performance or recovery from real occlusion.
- Actual road reconstruction, map/vehicle reference-point calibration or measured spatial error.
- Device clock calibration, exposure-to-screen latency, physical frame rate or dropped-frame rate.

Self-test frame rates, P95 values and zero timestamp differences come from data generated in the same process. They are software smoke-test results, not hardware performance measurements.
