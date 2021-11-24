#!/bin/bash
#
# Copyright (C) 2021  The SymbiFlow Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

echo
echo "======================================="
echo "Installing packages"
echo "---------------------------------------"
apt update
apt install -y python3 python3-pip wget git curl unzip default-jdk
echo "---------------------------------------"

echo
echo "======================================="
echo "Installing Python packages"
echo "---------------------------------------"
python3 -m pip install -r conf/common/requirements.txt
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
