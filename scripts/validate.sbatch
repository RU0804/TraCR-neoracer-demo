#!/usr/bin/env bash
#SBATCH --job-name=tracr-validate
#SBATCH --account=sukkusur
#SBATCH --partition=a100-40gb
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --gpus-per-node=1
#SBATCH --mem=6G
#SBATCH --time=00:08:00
set -euo pipefail
case "${SLURM_JOB_PARTITION:-}" in a100-40gb|a30) ;; *) echo 'Use allocated A100-40GB or A30'; exit 2;; esac
mkdir -p runtime/validation
.venv/bin/python -m pytest -q --junitxml=runtime/validation/tests.xml
.venv/bin/python -m tracr_demo.server --self-test > runtime/validation/selftest.log 2>&1 &
selftest_pid=$!
.venv/bin/python -m tracr_demo.server --port 8081 > runtime/validation/live.log 2>&1 &
live_pid=$!
trap 'kill "$selftest_pid" "$live_pid" 2>/dev/null || true' EXIT
.venv/bin/python - <<'PY'
import time, urllib.request
for port in (8080,8081):
    for attempt in range(50):
        try:
            urllib.request.urlopen(f'http://127.0.0.1:{port}/api/status',timeout=.2).close()
            break
        except OSError:
            time.sleep(.1)
    else:
        raise SystemExit(f'Server {port} did not start')
PY
"${TRACR_BROWSER_PYTHON:-.venv/bin/python}" scripts/check_browser.py
