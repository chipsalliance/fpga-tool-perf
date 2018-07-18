#!/usr/bin/env bash

device="hx8k"
package="ct256"
pcf=
dry=
aproject=
atoolchain=
verbose=

usage() {
    echo "Exhaustively try project-toolchain combinations, seeding if possible"
    echo "usage: exaust.sh [args]"
    echo "--device <device>         device (default: hx8k)"
    echo "--package <package>       device package (default: ct256)"
    echo "--project <project>       run given project only (default: all)"
    echo "--toolchain <toolchain>   run given toolchain only (default: all)"
    echo "--pcf <pcf>               pin constraint file (default: none)"
    echo "--dry                     print commands, don't invoke"
    echo "--verbose                 verbose output"
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
    --pcf)
        pcf=$2
        shift
        shift
        ;;
    --dry)
        dry=echo
        shift
        ;;
    --project)
        aproject=$2
        shift
        shift
        ;;
    --toolchain)
        atoolchain=$2
        shift
        shift
        ;;
    --verbose)
        verbose=--verbose
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

    if [ "$pcf" = "" ] ; then
        pcf_arg=""
    else
        pcf_arg="--pcf $pcf"
    fi

    if [[ $(python3 main.py --list-seedable) = *"$toolchain"* ]]; then
        for seed in 1 10 100 1000 10000 100000 1000000 10000000 100000000 1000000000 ; do
            # some of these may fail pnr
            $dry python3 main.py --toolchain $toolchain --project $project --device $device --package $package --seed $seed $pcf_arg $verbose || true
        done
    else
        # some of these may fail pnr
        $dry python3 main.py --toolchain $toolchain --project $project --device $device --package $package $pcf_arg $verbose || true
    fi
    # make ^C easier
    sleep 0.1
}

# Some of these will fail
function exhaustive() {
    echo "Running exhaustive project-toolchain search"
    for project in $(python3 main.py --list-projects) ; do
        if [ -n "$aproject" -a "$aproject" != "$project" ] ; then
            continue
        fi
        for toolchain in $(python3 main.py --list-toolchains) ; do
            if [ -n "$atoolchain" -a "$atoolchain" != "$toolchain" ] ; then
                continue
            fi
            echo
            run $toolchain $project
        done
    done
}

exhaustive

cat $(find build -name '*.csv') |sort -u >build/all.csv
python sow.py build/all.csv build/sow.csv

