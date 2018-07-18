#!/usr/bin/env bash

# Run all officially support hx8k designs

set -x
set -e

function run() {
    toolchain=$1
    project=$2

    if [[ $(python3 main.py --list-seedable) = *"$toolchain"* ]]; then
        for seed in 1 10 100 1000 10000 100000 1000000 10000000 100000000 1000000000 ; do
            # some of these may fail pnr
            python3 main.py --toolchain $toolchain --project $project --device "hx8k" --package "ct256" --seed $seed || true
        done
    else
        # some of these may fail pnr
        python3 main.py --toolchain $toolchain --project $project --device "hx8k" --package "ct256" || true
    fi
}

# Some of these will fail
function exhaustive() {
    echo "Running exhaustive project-toolchain search"
    for project in $(python3 main.py --list-projects) ; do
        for toolchain in $(python3 main.py --list-toolchains) ; do
            echo
            run $toolchain $project
        done
    done
}

function test1() {
    for project in oneblink picosoc-hx8kdemo ; do
        run arachne $project

        run icecube2-synpro $project
        run icecube2-lse $project
        run icecube2-yosys $project

        # Radiant does not support this part

        #run vpr $project
    done
}

#test1
exhaustive

cat $(find build -name '*.csv') |sort -u >build/all.csv

