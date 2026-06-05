#!/usr/bin/env bash
set -euo pipefail

: "${DATA_DIR:?DATA_DIR must be set}"
: "${LOG_LEVEL:=INFO}"

LOCK_FILE="${DATA_DIR}/.pipeline.lock"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cleanup() {
    rm -f "${LOCK_FILE}"
}
trap cleanup EXIT

if [[ -f "${LOCK_FILE}" ]]; then
    echo "ERROR: pipeline already running (lock file: ${LOCK_FILE})" >&2
    exit 1
fi

touch "${LOCK_FILE}"

archive_dir="${DATA_DIR}/archive/$(date +%Y%m%d_%H%M%S)"
mkdir -p "${archive_dir}"

for f in "${DATA_DIR}/input/"*.csv; do
    [[ -e "${f}" ]] || break
    cp "${f}" "${archive_dir}/"
done

LOG_LEVEL="${LOG_LEVEL}" python3 "${SCRIPT_DIR}/ingest.py"
