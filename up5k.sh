#!/usr/bin/env bash

# Run all officially support up5k designs

set -x
set -e

function run() {
    toolchain=$1
    project=$2
    # some of these may fail pnr
    python3 main.py --toolchain $toolchain --project $project --device "up5k" --package "uwg30" || true
}

run icecube2-synpro oneblink
run icecube2-lse oneblink

run radiant-synpro oneblink
run radiant-lse oneblink

# FIXME: vpr issue mixing up hx and up
# run vpr oneblink

cat $(find build -name '*.csv') |sort -u >build/all.csv

