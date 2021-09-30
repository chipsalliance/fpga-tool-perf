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
    # Testing all projects/toolchains/boards
    python3 exhaust.py --build_type generic-all --fail --num-cpu $NUM_CORES
    # Testing parameters injection feature
    python3 exhaust.py --parameters parameters.yaml --toolchain vpr --project blinky --build_type parameters --only_required --fail
    # Testing multiple samples
    python3 exhaust.py --build_type multiple-samples --run_config run_configs/multiple_samples.yaml --only_required --fail
    # Testing multiple seeds
    python3 exhaust.py --build_type multiple-seeds --run_config run_configs/multiple_seeds.yaml --only_required --fail

)
echo "-------------------------------------------"
