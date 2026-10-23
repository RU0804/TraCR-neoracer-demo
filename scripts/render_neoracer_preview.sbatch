#!/usr/bin/env bash
# Check slist immediately before submission; select A30/standby when required.
#SBATCH --job-name=neoracer-preview
#SBATCH --account=sukkusur
#SBATCH --partition=a100-40gb
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --gpus-per-node=1
#SBATCH --mem=12G
#SBATCH --time=00:12:00
set -euo pipefail
case "${SLURM_JOB_PARTITION:-}" in a100-40gb|a30) ;; *) echo 'Use allocated A100-40GB or A30'; exit 2;; esac
"${TRACR_BROWSER_PYTHON:-.venv/bin/python}" scripts/render_neoracer_preview.py \
  --ffmpeg "${TRACR_FFMPEG:-ffmpeg}"
"${TRACR_VALIDATION_PYTHON:-.venv/bin/python}" scripts/check_neoracer_preview.py
