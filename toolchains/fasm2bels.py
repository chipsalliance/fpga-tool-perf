#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2020  The SymbiFlow Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

import os
import subprocess

import edalize

from toolchains.toolchain import Toolchain
from toolchains.symbiflow import VPR
from toolchains.nextpnr import NextpnrXilinx
from utils.utils import Timed, get_vivado_max_freq, which, have_exec


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
