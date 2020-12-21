#!/bin/bash

set -e

cd github/$KOKORO_DIR/

source ./.github/kokoro/steps/hostsetup.sh
source ./.github/kokoro/steps/hostinfo.sh
source ./.github/kokoro/steps/git.sh

if [ -z $NUM_CORES  ]; then
    echo "Missing $$NUM_CORES value"
    exit 1
fi

echo
echo "==========================================="
echo "Running FPGA perf tool tests (make run-all)"
echo "-------------------------------------------"
(
    source env.sh
    python3 exhaust.py \
            --build_type vpr-runtime \
            --run_config run_configs/vpr_runtime.json \
            --only_required

)
echo "-------------------------------------------"
