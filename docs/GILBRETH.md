# Gilbreth resource constraints

Follow the user's GPU instructions recorded on 2026-10-20:

1. Check `slist` for group entitlement, running jobs and queued jobs before submission. Prefer the group's single A100-40GB allocation: `sukkusur / a100-40gb / normal`.
2. When that allocation is occupied or committed to queued work, select A30. The group currently has no purchased A30 entitlement, so use `a30 / standby`; verify again if allocations change.
3. A10 is prohibited for full demonstrations and graphical simulations. The user permits it only for extremely small tasks expected to finish within 30 seconds. This repository's submission script never selects A10.
4. Run substantial work, including Unity, video encoding and browser rendering, through Slurm rather than continuously on a login node.

```bash
bash scripts/submit_validation.sh --dry-run
bash scripts/submit_validation.sh --test-only
# After configuring Python/Playwright paths for browser checks:
bash scripts/submit_validation.sh
```

`TRACR_BROWSER_PYTHON` defaults to `.venv/bin/python`. Install Playwright and Chromium before browser checks. Set `TRACR_BROWSER_PYTHON` and `PLAYWRIGHT_BROWSERS_PATH` to reuse existing installations.

The current script requests 2 CPUs, 6 GB of memory, 1 GPU and an 8-minute time limit. Normal validation takes tens of seconds. Services stop when the job ends. The full Python service also rejects execution in an A10 partition.

Passing browser tests **does not validate Unity's NVIDIA Vulkan rendering path**. Unity graphics compatibility on A100/A30 remains unverified, and incompatibility does not authorize an A10 fallback. Prefer local laptop rendering for the field demonstration.
