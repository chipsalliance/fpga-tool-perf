#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

from fpgaperf import get_boards

import subprocess
import sys

if len(sys.argv) < 3:
    print("Usage {} <tool> <board>".format(sys.argv[0]))
    sys.exit(1)

tool = sys.argv[1]
board = get_boards()[sys.argv[2]]

f4pga = ["vpr", "vpr-fasm2bels"]
vivado = ["vivado", "yosys-vivado", "yosys-vivado-uhdm"]
nextpnr = [
    "nextpnr-ice40", "nextpnr-nexus", "nextpnr-xilinx",
    "nextpnr-xilinx-fasm2bels"
]
interchange = ["nextpnr-fpga-interchange"]
quicklogic = ["quicklogic"]

toolchain = ""
install = ""
if tool in f4pga:
    toolchain = "f4pga"
    board_device = board["device"] if board["device"] != "a35t" else "a50t"
    board_family = board["family"]
    install = f"F4PGA_DEVICES={board_family + board_device} make install_f4pga"
elif tool in vivado:
    # The basic f4pga environment contains yosys and yosys-uhdm
    toolchain = "f4pga"
elif tool in nextpnr:
    toolchain = "nextpnr"
elif tool in interchange:
    toolchain = "nextpnr"
    board_device = board["device"]
    board_family = board["family"]
    # TODO: Fix naming convention
    device_name = board_family + board_device if board_family not in ["xcup"] else board_device
    install = f"INTERCHANGE_DEVICES={device_name} make install_interchange"
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
