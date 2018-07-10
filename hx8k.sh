#!/usr/bin/env bash

# Run all officially support up5k designs

set -x
set -e

function run() {
    toolchain=$1
    project=$2
    python3 main.py --toolchain $toolchain --project $project --device "hx8k" --package "ct256"
}

run icecube2-synpro blinky
run icecube2-lse blinky
run icecube2-yosys blinky

# Radiant does not support this part

run vpr blinky

cat $(find build -name '*.csv') |sort -u >build/hx8k.csv

