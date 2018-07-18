#!/usr/bin/env bash

device="hx8k"
package="ct256"

usage() {
    echo "Exhaustively try project-toolchain combinations, seeding if possible"
    echo "usage: exaust.sh [args]"
    echo "--device         device (default: hx8k)"
    echo "--package        device package (default: ct256)"
}

ARGS=()
while [[ $# -gt 0 ]]; do
    case "$1" in
    --device)
        device=$2
        shift
        shift
        ;;
    --package)
        package=$2
        shift
        shift
        ;;
    -h|--help)
        usage
        exit 0
        ;;
    *)
        echo "Unrecognized argument"
        usage
        exit 1
        ;;
    esac
done

set -x
set -e

function run() {
    toolchain=$1
    project=$2

    if [[ $(python3 main.py --list-seedable) = *"$toolchain"* ]]; then
        for seed in 1 10 100 1000 10000 100000 1000000 10000000 100000000 1000000000 ; do
            # some of these may fail pnr
            python3 main.py --toolchain $toolchain --project $project --device $device --package $package --seed $seed || true
        done
    else
        # some of these may fail pnr
        python3 main.py --toolchain $toolchain --project $project --device $device --package $package || true
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

exhaustive

cat $(find build -name '*.csv') |sort -u >build/all.csv

