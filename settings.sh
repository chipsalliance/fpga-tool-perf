#!/bin/bash

# Checking that required commands and environmental variables are set
if [ -z "${VPR}" ]; then
    echo "ERROR: \$VPR environmental variable is required, but is not set"
    return 1
fi

if [ -z "${GENFASM}" ]; then
    echo "ERROR: \$GENFASM environmental variable is required, but is not set"
    return 1
fi

if [ -z "${SYMBIFLOW}" ]; then
    echo "ERROR: \$SYMBIFLOW environmental variable is required, but is not set"
    return 1
fi

if ! [ -x "$(command -v vivado)" ]; then
    echo "ERROR: vivado command not found, please source Vivado settings"
    return 1
fi

if ! [ -x "$(command -v yosys)" ]; then
    echo "ERROR: yosys command not found, please install yosys"
    return 1
fi

echo "Setting PATH environmental variable:"
echo -e "\t- ${VPR}"
echo -e "\t- ${GENFASM}"
echo -e "\t- ${SYMBIFLOW}"
export PATH=${VPR}:${GENFASM}:${SYMBIFLOW}:${PATH}
export FPGA_TOOL_PERF_DIR=`pwd`
