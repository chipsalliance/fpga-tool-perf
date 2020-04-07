#!/bin/bash

export FPGA_TOOL_PERF_DIR=`pwd`

if [ -z "${VIVADO_SETTINGS}" ]; then
    echo "ERROR: \$VIVADO_SETTINGS environmental variable needs to be set"
    return 1
fi

source ${VIVADO_SETTINGS}

. ./env/bin/activate
source utils/environment.python.sh
source settings.sh
