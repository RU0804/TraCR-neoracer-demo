# Provenance and scope of results

## Earlier results

The original Gilbreth project is at `/scratch/gilbreth/zjcai/autodrive-demo`, with its handoff in `HANDOFF.md`. This repository is a separate continuation. It has not modified `/home/zjcai/d2s-diffusion`, the original outputs or historical logs.

The successful earlier run used **AutoDRIVE Simulator 0.2.0 / Nigel / Tiny Town** and included stopping at a red light, following a left-turn route and stopping at a target point. Its approximately 46-second offline presentation remains in the original project's `outputs/final_demo_presentation/` and `outputs/autodrive_demo_delivery.zip`.

That experiment recorded 136 telemetry samples over 46.391 seconds, with approximately 2.82 cm path RMSE and 3.30 cm final position error. These measurements apply only to that Nigel simulation route, not NeoRacer, the current webpage, a physical vehicle or the foam-board map. The video's 10 fps output rate is not the telemetry sampling rate. The historical job used A10 before the new resource constraints took effect; its provenance must not be relabeled as A100.

## New work in this repository

This repository adds a local Python display service, read-only input adapters, video/pose pairing protocol, synthetic self-test, Unity follower/render acknowledgement source, road-layout JSON importer, calibration tools, software tests and deployment documentation. Synthetic images are generated and labeled. No physical NeoRacer footage or executed NeoRacer Unity renders are included.

The README also includes a labeled GIF and still image derived from the earlier Nigel recording, arranged in the current browser layout. Both panels show recorded simulation, including the left onboard-camera example. They are separate from the synthetic self-test and do not validate the live bridge or physical vehicle integration. See [preview provenance and reproduction](PREVIEW.md).

Pinned upstream versions are recorded in `upstream.lock.json`. AutoDRIVE assets and binaries are not copied into this repository. CoSim fields and coordinate conventions reference the pinned official [Socket.cs](https://github.com/Tinker-Twins/AutoDRIVE/blob/75b7df5216524a3c6b3150d698139190c6c44f8f/Assets/Scripts/Socket.cs) and [CoSimManager.cs](https://github.com/Tinker-Twins/AutoDRIVE/blob/75b7df5216524a3c6b3150d698139190c6c44f8f/Assets/Scripts/CoSimManager.cs).

Candidate physical NeoRacer interfaces come from the [Neobotics driver](https://github.com/Neobotics-Foundation-Inc/neoracer_ros2_driver) and the earlier source review. Upstream vehicle configuration is not treated as confirmed configuration of the user's car.

## Licensing and redistribution

No open-source license has been selected for this repository; the project owner should choose one before adding LICENSE. Publishing on GitHub does not itself select an open-source license. Preserve copyright notices and follow the applicable licenses when using or downloading AutoDRIVE, NeoRacer models and other third-party assets. This repository does not relicense third-party material.
