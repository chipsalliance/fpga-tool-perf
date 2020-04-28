#!/bin/bash

export FPGA_TOOL_PERF_BASE_DIR=$(pwd)

. ./env/conda/bin/activate fpga-tool-perf-env

if [ -z "${VIVADO_SETTINGS}" ]; then
    echo "WARNING: using default vivado settings"
    #FIXME: to use the conda xilinx-vivado virtual package when available
    export VIVADO_SETTINGS=/opt/Xilinx/Vivado/2017.2/settings64.sh
fi

if [ -z "${SYMBIFLOW}" ]; then
    echo "WARNING: using default symbiflow dir."
    export SYMBIFLOW=${FPGA_TOOL_PERF_BASE_DIR}/env/install
fi

export PATH=${SYMBIFLOW}/bin:${PATH}
export PYTHONPATH=${FPGA_TOOL_PERF_BASE_DIR}/third_party/prjxray:${PYTHONPATH}
export XRAY_DATABASE_DIR=${FPGA_TOOL_PERF_BASE_DIR}/third_party/prjxray-db
export XRAY_FASM2FRAMES=${FPGA_TOOL_PERF_BASE_DIR}/third_party/prjxray/utils/fasm2frames.py
export XRAY_TOOLS_DIR=${FPGA_TOOL_PERF_BASE_DIR}/third_party/prjxray/build/tools
