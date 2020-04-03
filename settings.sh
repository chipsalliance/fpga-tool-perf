#!/bin/bash

export FPGA_TOOL_PERF_DIR=`pwd`

export PATH=$(getconf PATH)

set_tool_path () {
    local TOOL=$1
    local TOOL_PATH=$2
    local REQUIRED=$3

    if [ -z "${!TOOL}" ]; then
        if [ "$REQUIRED" = "no" ]; then
            echo "Default $TOOL is being used."
            export PATH=${FPGA_TOOL_PERF_DIR}/$TOOL_PATH:${PATH}
        else
            echo "ERROR: $TOOL path is required, but it is not set in the corresponding env variable!"
            return 1
        fi
    else
        echo "Using $TOOL from ${!TOOL}"
        export PATH=${!TOOL}:${PATH}
    fi
}

# Checking that required commands and environmental variables are set
set_tool_path VPR third_party/vtr/build/vpr no
set_tool_path GENFASM third_party/vtr/build/util/fasm no
set_tool_path YOSYS third_party/yosys no
set_tool_path SYMBIFLOW third_party/symbiflow/bin yes
