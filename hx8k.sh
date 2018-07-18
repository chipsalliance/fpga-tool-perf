#!/usr/bin/env bash

# Run all officially support hx8k designs

set -x
set -e

function run() {
    toolchain=$1
    project=$2
    # some of these may fail pnr
    python3 main.py --toolchain $toolchain --project $project --device "hx8k" --package "ct256" || true
}

for project in oneblink picosoc-hx8kdemo ; do
    run arachne $project

    run icecube2-synpro $project
    run icecube2-lse $project
    run icecube2-yosys $project

    # Radiant does not support this part

    #run vpr $project
done

cat $(find build -name '*.csv') |sort -u >build/all.csv

