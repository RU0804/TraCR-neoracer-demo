#!/usr/bin/env bash
# Check slist immediately before submission; override partition/QOS for A30 standby.
#SBATCH --job-name=tracr-preview
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
: "${TRACR_PREVIEW_SOURCE:?Set the path to the original Nigel run with frames and telemetry}"
"${TRACR_BROWSER_PYTHON:-.venv/bin/python}" scripts/render_readme_preview.py \
  "$TRACR_PREVIEW_SOURCE" --ffmpeg "${TRACR_FFMPEG:-ffmpeg}"
