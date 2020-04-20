#!/bin/bash

. ./env/conda/bin/activate fpga-tool-perf-env
source utils/environment.python.sh

if [ -z "${VIVADO_SETTINGS}" ]; then
    echo "WARNING: using default vivado settings"
    #FIXME: to use the conda xilinx-vivado virtual package when available
    export VIVADO_SETTINGS=/opt/Xilinx/Vivado/2017.2/settings64.sh
fi

# TODO: enable this when integrating symbiflow package
#if [ -z "${SYMBIFLOW}" ]; then
#    echo "ERROR: SYMBIFLOW install dir not set."
#    return 1
#fi

#export PATH=${SYMBIFLOW}/bin:${PATH}
export XRAY_DATABASE_DIR=$(pwd)/third_party/prjxray-db
export XRAY_FASM2FRAMES=$(pwd)/third_party/prjxray/utils/fasm2frames.py
