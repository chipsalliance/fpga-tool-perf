#!/bin/bash

set -e

cd github/$KOKORO_DIR/

source ./.github/kokoro/steps/hostsetup.sh
source ./.github/kokoro/steps/hostinfo.sh
source ./.github/kokoro/steps/git.sh

echo
echo "==========================================="
echo "Running FPGA perf tool tests (make run-all, run-all-multiple-samples-tests, run-all-seedable-tests)"
echo "-------------------------------------------"
(
    source env.sh
    make run-all
    make run-all-multiple-samples-tests
    make run-all-seedable-tests
)
echo "-------------------------------------------"
