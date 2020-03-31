#!/usr/bin/env bash

device="hx8k"
package="ct256"
family=
pcf=
dry=
aproject=
atoolchain=
verbose=
onfail=true
out_prefix=build

usage() {
    echo "Exhaustively try project-toolchain combinations"
    echo "usage: exaust.sh [args]"
    echo "--device <device>         device (default: hx8k)"
    echo "--package <package>       device package (default: ct256)"
    echo "--family <family>         device family"
    echo "--project <project>       run given project only (default: all)"
    echo "--toolchain <toolchain>   run given toolchain only (default: all)"
    echo "--out-prefix <dir>        output directory prefix (default: build)"
    echo "--dry                     print commands, don't invoke"
    echo "--fail                    fail on error"
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
    --family)
        family=$2
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
    --out-prefix)
        out_prefix=$2
        shift
        shift
        ;;
    --fail)
        onfail=false
        shift
        ;;
    --verbose)
        verbose=--verbose
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

function run2() {
    $dry python3 fpgaperf.py --toolchain $toolchain --project "$project" --device "$device" --family "$family" --package "$package" $pcf_arg $sdc_arg $xdc_arg --out-prefix "$out_prefix" $verbose || $onfail
}

function run() {
    toolchain=$1
    project=$2

    if [ "$family" = "ice40" ] ; then
        echo "$family family currently not supported by exhaust.sh"
        exit 1
    fi

    if [ "$toolchain" != vivado ] && [ "$toolchain" != vpr ] ; then
        echo "Currently testing only vivado and vpr toolchains,  not $toolchain"
        return
    fi

    if [ "$family" = "xc7" ] ; then
        if [[ "$device" == "z010" ]] ; then
            if [ "$project" = "oneblink" ] ; then
                if [ "$toolchain" = "vivado" ] ; then
                    pcf="project/oneblink-zybo-z7.xdc"
                fi
            else
                echo "Combination $toolchain/$family/$device/$project doesn't have PCF file defined"
                return 0
            fi
        elif [[ "$device" == "a35t" ]] ; then
            if [ "$project" = "oneblink" ] ; then
                if [ "$toolchain" = "vivado" ] ; then
                    pcf="project/oneblink-arty.xdc"
                fi
            elif [ "$project" = "litex-linux" ] ; then
                if [ "$toolchain" = "vivado" ] ; then
                    pcf="src/baselitex/baselitex_arty_vivado.xdc"
                else
                    pcf="src/baselitex/arty.pcf"
                    sdc="src/baselitex/arty.sdc"
                    xdc="src/baselitex/baselitex_arty.xdc"
                fi
            else
                pcf="src/baselitex/arty.sdc"
            fi
        else
            echo "Device $device not supported"
            exit 1
        fi
    fi

    if [ "$pcf" = "" ] ; then
        pcf_arg=""
    else
        pcf_arg="--pcf $pcf"
    fi

    if [ "$sdc" = "" ] ; then
        sdc_arg=""
    else
        sdc_arg="--sdc $sdc"
    fi

    if [ "$xdc" = "" ] ; then
        xdc_arg=""
    else
        xdc_arg="--xdc $xdc"
    fi

    run2

    # make ^C easier
    sleep 0.1
}

# Some of these will fail
function exhaustive() {
    echo "Running exhaustive project-toolchain search"
    for project in $(python3 fpgaperf.py --list-projects) ; do
        if [ -n "$aproject" -a "$aproject" != "$project" ] ; then
            continue
        fi
        for toolchain in $(python3 fpgaperf.py --list-toolchains) ; do
            if [ -n "$atoolchain" -a "$atoolchain" != "$toolchain" ] ; then
                continue
            fi
            echo
            run $toolchain $project
        done
    done
}

mkdir -p $out_prefix
exhaustive
cd $out_prefix && ../json.sh

