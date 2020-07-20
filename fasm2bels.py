import os
import subprocess

import edalize

from toolchain import Toolchain
from symbiflow import VPR, NextpnrXilinx
from utils import Timed, get_vivado_max_freq, which


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
        Toolchain.__init__(self, rootdir)
        self.toolchain = 'vpr-fasm2bels'
        self.files = []
        self.fasm2bels = True

        self.dbroot = subprocess.check_output(
            'prjxray-config', shell=True
        ).decode('utf-8').strip()

        capnp_schema_dir = subprocess.check_output(
            'capnp-schemas-dir', shell=True
        ).decode('utf-8').strip()

        self.files.append({'name': capnp_schema_dir, 'file_type': 'capnp'})

        assert self.dbroot

    def max_freq(self):
        report_file = os.path.join(self.out_dir, 'timing_summary.rpt')
        return get_vivado_max_freq(report_file)

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


class NextpnrXilinxFasm2Bels(NextpnrXilinx):
    '''nextpnr using Yosys for synthesis'''
    carries = (False, )

    def __init__(self, rootdir):
        Toolchain.__init__(self, rootdir)
        self.toolchain = 'nextpnr-xilinx-fasm2bels'
        self.files = []
        self.fasm2bels = True

        self.dbroot = subprocess.check_output(
            'prjxray-config', shell=True
        ).decode('utf-8').strip()

        capnp_schema_dir = subprocess.check_output(
            'capnp-schemas-dir', shell=True
        ).decode('utf-8').strip()

        self.files.append({'name': capnp_schema_dir, 'file_type': 'capnp'})

        assert self.dbroot

    def max_freq(self):
        report_file = os.path.join(self.out_dir, 'timing_summary.rpt')
        return get_vivado_max_freq(report_file)

    def run_steps(self):
        with Timed(self, 'bitstream'):
            self.backend.build_main(self.project_name + '.bit')
        with Timed(self, 'fasm2bels'):
            self.backend.build_main('timing_summary.rpt')
