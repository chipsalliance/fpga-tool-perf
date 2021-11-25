#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2021  The SymbiFlow Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

from fpgaperf import get_boards

import subprocess
import sys

if len(sys.argv) < 3:
    print("Usage {} <tool> <board>".format(sys.argv[0]))
    sys.exit(1)

tool = sys.argv[1]
board = get_boards()[sys.argv[2]]

symbiflow = ["vpr", "vpr-fasm2bels"]
vivado = ["vivado", "yosys-vivado", "yosys-vivado-uhdm"]
nextpnr = [
    "nextpnr-ice40", "nextpnr-nexus", "nextpnr-xilinx",
    "nextpnr-xilinx-fasm2bels"
]
interchange = ["nextpnr-fpga-interchange"]
quicklogic = ["quicklogic"]

toolchain = ""
install = ""
if tool in symbiflow:
    toolchain = "symbiflow"
    board_device = board["device"] if board["device"] != "a35t" else "a50t"
    board_family = board["family"]
    install = f"SYMBIFLOW_DEVICES={board_family + board_device} make install_symbiflow"
elif tool in vivado:
    # The basic symbiflow environment contains yosys and yosys-uhdm
    toolchain = "symbiflow"
elif tool in nextpnr:
    toolchain = "nextpnr"
elif tool in interchange:
    toolchain = "nextpnr"
    board_device = board["device"]
    board_family = board["family"]
    install = f"INTERCHANGE_DEVICES={board_family + board_device} make install_interchange"
elif tool in quicklogic:
    toolchain = "quicklogic"
    install = "make install_quicklogic"
else:
    print("ERROR: toolchain did not match any available ones!")
    raise ValueError()

cmd = f"TOOLCHAIN={toolchain} make env"
if install:
    cmd += f" && {install}"

print(cmd)
