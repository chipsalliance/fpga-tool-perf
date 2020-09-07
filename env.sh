#!/bin/bash

if [ -z "${FPGA_TOOL_PERF_BASE_DIR}" ]; then
    export FPGA_TOOL_PERF_BASE_DIR=$(pwd)
fi
if [ -z "${VIVADO_SETTINGS}" ]; then
    echo "WARNING: using default vivado settings"
    #FIXME: to use the conda xilinx-vivado virtual package when available
    export VIVADO_SETTINGS=/opt/Xilinx/Vivado/2017.2/settings64.sh
fi
if [ -z "${SYMBIFLOW}" ]; then
    echo "WARNING: using default symbiflow dir."
    export SYMBIFLOW=${FPGA_TOOL_PERF_BASE_DIR}/env/symbiflow
fi
if [ -z "${QUICKLOGIC}" ]; then
    echo "WARNING: using default quicklogic dir."
    export QUICKLOGIC=${FPGA_TOOL_PERF_BASE_DIR}/env/quicklogic
fi

#https://unix.stackexchange.com/a/291611
function path_remove {
  # Delete path by parts so we can never accidentally remove sub paths
  PATH=${PATH//":$1:"/":"} # delete any instances in the middle
  PATH=${PATH/#"$1:"/} # delete any instance at the beginning
  PATH=${PATH/%":$1"/} # delete any instance in the at the end
}

path_remove ${SYMBIFLOW}/bin
path_remove ${QUICKLOGIC}/install/bin

conda_env=${1:-xilinx}

if [ "quicklogic" == ${conda_env} ]; then
    . ${FPGA_TOOL_PERF_BASE_DIR}/env/conda/bin/activate quicklogic
    export PATH=${QUICKLOGIC}/install/bin:${PATH}
else
    . ${FPGA_TOOL_PERF_BASE_DIR}/env/conda/bin/activate fpga-tool-perf-env
    export PATH=${SYMBIFLOW}/bin:${PATH}
fi
