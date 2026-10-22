# TraCR NeoRacer demo implementation plan

## Objective
Create a portable laptop demo repository with left onboard camera and right AutoDRIVE camera driven by measured physical pose. Preserve honest completed/unverified boundaries. GitHub name: TraCR-neoracer-demo. Original Nigel baseline remains untouched.

## Phases
1. Audit handoff and fixed upstream interfaces — complete.
2. Implement bounded timestamped ingest, paired display, source adapters, and Unity integration source — complete; hardware and Unity execution pending.
3. Add configuration, measured-map workflow, laptop runbook and provenance — complete.
4. Validate software in Slurm on allowed resources and package a clean Git repository — complete.
5. Record remaining hardware/Unity acceptance tasks — complete; GitHub owner RU0804 and public visibility confirmed; repository accessible, publication in progress.

## Constraints
- Laptop OS/GPU, video transport and localization are unknown. GitHub owner is confirmed RU0804.
- Physical map is approximately 5 m × 5 m. No measured layout available; example map must be labeled illustrative.
- A100-40GB sukkusur/normal first; if occupied or queued use A30/standby after checking slist. No A10. Substantial rendering/tests through Slurm.
- No car control publishers. Do not claim physical hardware, NeoRacer Unity build or field synchronization has been validated.
- /home/zjcai/d2s-diffusion and original baseline outputs must stay untouched.

## Errors
- A documentation tool call had a JS string syntax error before execution; split into smaller calls and completed.
- gh CLI is unavailable; connected GitHub tools can edit existing repositories but do not expose repository creation. Target RU0804/TraCR-neoracer-demo confirmed; get_repo returned 404. This earlier blocker is resolved: user created a public repository and GitHub API access is now available; publishing through connected tools.
