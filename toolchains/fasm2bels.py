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

import os
import subprocess

from toolchains.f4pga import VPR
from toolchains.nextpnr import NextpnrXilinx
from utils.utils import Timed, get_vivado_max_freq


class VPRFasm2Bels(VPR):
    """This class is used to generate the VPR -> Fasm2bels flow.

    fasm2bels is a tool that, given a bitstream, can reproduce the original netlist
    and run it through Vivado to get a mean of comparison with the VPR outputs.

    fasm2bels generates two different files:
        - verilog netlist corresponding to the bitstream
        - tcl script to force the placement and routing

    It then runs the two generated outputs through Vivado and gets the timing reports.

    NOTE: This flow is purely for verification purposes and is intended for developers only.
          In addition, this flow makes use of Vivado.
    """
    def __init__(self, rootdir):
        VPR.__init__(self, rootdir)
        self.toolchain = 'vpr-fasm2bels'
        self.fasm2bels = True
        self.dbroot = subprocess.check_output(
            'prjxray-config', shell=True
        ).decode('utf-8').strip()

        capnp_schema_dir = subprocess.check_output(
            'capnp-schemas-dir', shell=True
        ).decode('utf-8').strip()

        # FIXME: remove when package from https://github.com/hdl/conda-eda/pull/127 is used
        capnp_schema_dir = os.path.join(
            os.path.split(capnp_schema_dir)[0], 'share', 'vtr'
        )

        self.files.append({'name': capnp_schema_dir, 'file_type': 'capnp'})

        assert self.dbroot

    def run_steps(self):
        self.backend.build_main(self.top + '.eblif')
        self.backend.build_main(self.top + '.net')
        self.backend.build_main(self.top + '.place')
        self.backend.build_main(self.top + '.route')
        self.backend.build_main(self.top + '.fasm')
        with Timed(self, 'bitstream'):
            self.backend.build_main(self.top + '.bit')

        with Timed(self, 'fasm2bels'):
            self.backend.build_main('timing_summary.rpt')

    def max_freq(self):
        report_file = os.path.join(self.out_dir, 'timing_summary.rpt')
        return get_vivado_max_freq(report_file)


class NextpnrXilinxFasm2Bels(NextpnrXilinx):
    '''nextpnr using Yosys for synthesis'''
    def __init__(self, rootdir):
        NextpnrXilinx.__init__(self, rootdir)
        self.toolchain = 'nextpnr-xilinx-fasm2bels'
        self.builddir = '.'
        self.files = []
        self.fasm2bels = True

        self.dbroot = subprocess.check_output(
            'bash -c ". ./env.sh nextpnr && prjxray-config"', shell=True
        ).decode('utf-8').strip()

        capnp_schema_dir = subprocess.check_output(
            'bash -c ". ./env.sh nextpnr && capnp-schemas-dir"', shell=True
        ).decode('utf-8').strip()

        # FIXME: remove when package from https://github.com/hdl/conda-eda/pull/127 is used
        capnp_schema_dir = os.path.join(
            os.path.split(capnp_schema_dir)[0], 'share', 'vtr'
        )

        self.files.append({'name': capnp_schema_dir, 'file_type': 'capnp'})

        assert self.dbroot

    def run_steps(self):
        with Timed(self, 'bitstream'):
            self.backend.build_main(self.project_name + '.bit')

        with Timed(self, 'fasm2bels'):
            self.backend.build_main('timing_summary.rpt')

    def max_freq(self):
        report_file = os.path.join(self.out_dir, 'timing_summary.rpt')
        return get_vivado_max_freq(report_file)
