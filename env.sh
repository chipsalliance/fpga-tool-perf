#!/bin/bash
#
# Copyright 2018-2022 F4PGA Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

if [ -z "${FPGA_TOOL_PERF_BASE_DIR}" ]; then
    export FPGA_TOOL_PERF_BASE_DIR=$(pwd)
fi
if [ -z "${VIVADO_SETTINGS}" ]; then
    #FIXME: to use the conda xilinx-vivado virtual package when available
    export VIVADO_SETTINGS=/opt/Xilinx/Vivado/2017.2/settings64.sh
fi
if [ -z "${QUICKLOGIC}" ]; then
    export QUICKLOGIC=${FPGA_TOOL_PERF_BASE_DIR}/env/quicklogic
fi

#https://unix.stackexchange.com/a/291611
function path_remove {
  # Delete path by parts so we can never accidentally remove sub paths
  PATH=${PATH//":$1:"/":"} # delete any instances in the middle
  PATH=${PATH/#"$1:"/} # delete any instance at the beginning
  PATH=${PATH/%":$1"/} # delete any instance in the at the end
}

#Remove all possible paths from PATH
path_remove ${QUICKLOGIC}/install/bin

#Set now environment variables
environment=${1:-xilinx-a35t}

export RAPIDWRIGHT_PATH=${FPGA_TOOL_PERF_BASE_DIR}/third_party/RapidWright

if [ "quicklogic" == ${environment} ]; then
    . ${FPGA_TOOL_PERF_BASE_DIR}/env/conda/bin/activate quicklogic
    export PATH=${QUICKLOGIC}/quicklogic-arch-defs/bin:${PATH}
elif [ "nextpnr" == ${environment} ]; then
    . ${FPGA_TOOL_PERF_BASE_DIR}/env/conda/bin/activate nextpnr-env
else
    . ${FPGA_TOOL_PERF_BASE_DIR}/env/conda/bin/activate f4pga-env
    export F4PGA_INSTALL_DIR=${FPGA_TOOL_PERF_BASE_DIR}/env/f4pga
    export F4PGA_SHARE_DIR=${FPGA_TOOL_PERF_BASE_DIR}/env/f4pga/share/f4pga
fi
