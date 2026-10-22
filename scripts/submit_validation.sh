#!/usr/bin/env bash
# Group allocation check before every submission. Never submits an A10 job.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
mode=${1:-submit}
if (( $# > 1 )) || [[ $mode != submit && $mode != --dry-run && $mode != --test-only ]]; then
  echo 'Usage: scripts/submit_validation.sh [--dry-run|--test-only]' >&2; exit 2
fi
allocation=$(slist)
if ! printf '%s\n' "$allocation" | rg -q 'Accounts\s*\|\s*A10\s+A30\s+A100-40gb'; then
  echo 'Unrecognized allocation format; refusing to guess.' >&2; exit 2
fi
counts=$(printf '%s\n' "$allocation" | awk '$1=="sukkusur" && $2=="|" {print $5}')
a30_counts=$(printf '%s\n' "$allocation" | awk '$1=="sukkusur" && $2=="|" {print $4}')
if [[ ! $counts =~ ^([0-9]+)/([0-9]+)/([0-9]+)/([0-9]+)$ ]]; then
  echo 'Cannot parse group A100-40GB allocation'; exit 2
fi
queued=${BASH_REMATCH[2]}; free=${BASH_REMATCH[4]}
if (( free > 0 && queued == 0 )); then
  partition=a100-40gb; qos=normal
else
  if [[ $a30_counts != N/A ]]; then
    echo 'A30 allocation changed; inspect entitlement before choosing QOS.' >&2; exit 2
  fi
  partition=a30; qos=standby
fi
printf 'Group A100-40GB total/queued/running/free=%s; A30=%s; selected %s/%s\n' "$counts" "$a30_counts" "$partition" "$qos"
mkdir -p logs
cmd=(sbatch --account=sukkusur --partition="$partition" --qos="$qos" --chdir="$PWD" --output=logs/validation-%j.out --error=logs/validation-%j.err)
if [[ $mode == --test-only ]]; then cmd+=(--test-only); fi
cmd+=(scripts/validate.sbatch)
if [[ $mode == --dry-run ]]; then printf '%q ' "${cmd[@]}"; printf '\n'; exit 0; fi
exec "${cmd[@]}"
