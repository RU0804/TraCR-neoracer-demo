# TraCR NeoRacer demo

- All repository content must be in English, including documentation, comments, configuration descriptions, diagrams, filenames and user-facing text. Do not add Chinese text.

- Keep the previous Nigel baseline and this NeoRacer integration separate in all claims. Synthetic self-test images are not physical-car or AutoDRIVE evidence.
- This project reads physical vehicle state only. Do not add physical control publishers or merge simulated sensor topics into real localization without explicit task scope.
- Field laptop hardware, camera transport, localization and measured road layout are not yet confirmed. See HANDOFF.md and docs/VALIDATION.md.
- Gilbreth: check group running and queued usage before submission; prefer sukkusur / a100-40gb / normal. When occupied or committed to queued group work, use a30 / standby after verifying the current A30 entitlement.
- Do not use A10 for ordinary work. User permits it only for extremely small tasks expected to finish within 30 seconds; never for a full demo or graphical simulation.
- Submit substantial compute, Unity, video encoding and browser rendering through Slurm. Rendering incompatibility does not authorize a prohibited GPU fallback.
- Never commit tokens, environment directories, private camera addresses or raw recordings. Keep local configuration in configs/local*.json.
