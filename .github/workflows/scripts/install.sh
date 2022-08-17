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

set -e

echo
echo "======================================="
echo "Installing packages"
echo "---------------------------------------"
$(command -v sudo) apt update -qq
DEBIAN_FRONTEND=noninteractive $(command -v sudo) apt install -qq -y --no-install-recommends \
  curl \
  git \
  make \
  python3 \
  python3-pip \
  wget \
  unzip \
  default-jdk \
  xz-utils \
  libtinfo5
echo "---------------------------------------"

echo
echo "======================================="
echo "Installing Python packages"
echo "---------------------------------------"
python3 -m pip install -r conf/requirements.txt
echo "---------------------------------------"

USE_VIVADO=""
RW_LINK=""

TOOLCHAIN=""
BOARD=""

while getopts vl:t:b: opt; do
    case "${opt}" in
        v) USE_VIVADO="TRUE";;
        l) RW_LINK=${OPTARG};;
        t) TOOLCHAIN=${OPTARG};;
        b) BOARD=${OPTARG};;
        *)
            echo "ERROR: option not recognized!"
            exit;;
    esac
done

if [ ! -z "$USE_VIVADO" ]; then
    echo
    echo "======================================="
    echo "Creating Vivado Symbolic Link"
    echo "---------------------------------------"
    ln -s /mnt/aux/Xilinx /opt/Xilinx
    source /opt/Xilinx/Vivado/2017.2/settings64.sh
    vivado -version
fi

if [ ! -z "$RW_LINK" ]; then
    echo
    echo "======================================="
    echo "Export RapidWright JARs Link"
    echo "---------------------------------------"
    export RW_LINK=$RW_LINK
fi

echo
echo "======================================="
echo "Generate Test's environment"
echo "---------------------------------------"
eval $(PYTHONPATH=$(pwd) ./.github/workflows/scripts/get_env_cmd.py $TOOLCHAIN $BOARD)
