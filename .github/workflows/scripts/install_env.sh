#!/bin/bash
#
# Copyright (C) 2021  The SymbiFlow Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

if [ "$#" -ne 1 ]; then
    echo "ERROR: please provide the toolchain to setup."
    exit 1
fi

TOOL=$1

SYMBIFLOW_LIST="vpr vpr-fasm2bels"
NEXTPNR_LIST="nextpnr-ice40 nextpnr-nexus nextpnr-xilinx nextpnr-xilinx-fasm2bels"
INTERCHANGE_LIST="nextpnr-fpga-interchange"
QUICKLOGIC_LIST="quicklogic"
VIVADO_LIST="vivado yosys-vivado yosys-uhdm-vivado"

if echo $SYMBIFLOW_LIST | grep -F -wq $TOOL; then
    TOOLCHAIN=symbiflow make env
    make install_symbiflow
elif echo $VIVADO_LIST | grep -F -wq $TOOL; then
    TOOLCHAIN=symbiflow make env
elif echo $NEXTPNR_LIST | grep -F -wq $TOOL; then
    TOOLCHAIN=nextpnr make env
elif echo $INTERCHANGE_LIST | grep -F -wq $TOOL; then
    TOOLCHAIN=nextpnr make env
    make install_interchange
elif echo $QUICKLOGIC_LIST | grep -F -wq $TOOL; then
    TOOLCHAIN=quicklogic make env
    make install_quicklogic
else
    echo "ERROR: toolchain did not match any available ones!"
    exit 1
fi
