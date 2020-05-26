import os
import subprocess
import edalize

from toolchain import Toolchain
from utils import Timed, get_vivado_max_freq
from tool_parameters import ToolParametersHelper


class VPR(Toolchain):
    '''VPR using Yosys for synthesis'''
    carries = (False, )

    def __init__(self, rootdir):
        Toolchain.__init__(self, rootdir)
        self.toolchain = 'vpr'
        self.files = []
        self.fasm2bels = False
        self.dbroot = None

    def run_steps(self):
        with Timed(self, 'synthesis'):
            self.backend.build_main(self.top + '.eblif')
        with Timed(self, 'pack'):
            self.backend.build_main(self.top + '.net')
        with Timed(self, 'place'):
            self.backend.build_main(self.top + '.place')
        with Timed(self, 'route'):
            self.backend.build_main(self.top + '.route')
        with Timed(self, 'fasm'):
            self.backend.build_main(self.top + '.fasm')
        with Timed(self, 'bitstream'):
            self.backend.build_main(self.top + '.bit')

    def run(self):
        with Timed(self, 'total'):
            with Timed(self, 'prepare'):
                os.makedirs(self.out_dir, exist_ok=True)

                for f in self.srcs:
                    self.files.append(
                        {
                            'name': os.path.realpath(f),
                            'file_type': 'verilogSource'
                        }
                    )

                if self.pcf:
                    self.files.append(
                        {
                            'name': os.path.realpath(self.pcf),
                            'file_type': 'PCF'
                        }
                    )
                if self.sdc:
                    self.files.append(
                        {
                            'name': os.path.realpath(self.sdc),
                            'file_type': 'SDC'
                        }
                    )

                if self.xdc:
                    self.files.append(
                        {
                            'name': os.path.realpath(self.xdc),
                            'file_type': 'xdc'
                        }
                    )

                chip = self.family + self.device

                tool_params = self.get_tool_params()

                if self.fasm2bels:
                    symbiflow = os.getenv('SYMBIFLOW', None)
                    assert symbiflow

                    device_aliases = {"a35t": "a50t"}

                    chip_replace = chip
                    for k, v in device_aliases.items():
                        chip_replace = chip.replace(k, v)

                    device_path = os.path.join(
                        symbiflow, 'share', 'symbiflow', 'arch',
                        '{}_test'.format(chip_replace)
                    )

                    self.files.append(
                        {
                            'name':
                                os.path.realpath(
                                    os.path.join(
                                        device_path, '*rr_graph.real.bin'
                                    )
                                ),
                            'file_type':
                                'RRGraph'
                        }
                    )

                    self.files.append(
                        {
                            'name':
                                os.path.realpath(
                                    os.path.join(
                                        device_path, 'vpr_grid_map.csv'
                                    )
                                ),
                            'file_type':
                                'VPRGrid'
                        }
                    )

                self.edam = {
                    'files': self.files,
                    'name': self.project_name,
                    'toplevel': self.top,
                    'tool_options':
                        {
                            'symbiflow':
                                {
                                    'part': chip,
                                    'package': self.package,
                                    'vendor': 'xilinx',
                                    'builddir': '.',
                                    'pnr': 'vpr',
                                    'options': tool_params,
                                    'fasm2bels': self.fasm2bels,
                                    'dbroot': self.dbroot,
                                    'clocks': self.clocks,
                                }
                        }
                }
                self.backend = edalize.get_edatool('symbiflow')(
                    edam=self.edam, work_root=self.out_dir
                )
                self.backend.configure("")
                self.run_steps()

    def get_tool_params(self):
        if self.params_file:
            opt_helper = ToolParametersHelper('vpr', self.params_file)
            params = opt_helper.get_all_params_combinations()

            assert len(params) == 1
            return " ".join(params[0])
        elif self.params_string:
            return self.params_string
        else:
            return None

    def get_critical_paths(self, clocks, timing):

        report = self.out_dir + '/report_timing.{}.rpt'.format(timing)
        processing = False
        in_block = False
        critical_paths = None
        with open(report, 'r') as fp:
            for l in fp:
                l = l.strip('\n')
                if l.startswith('#Path'):
                    in_block = True
                    continue

                if in_block is True:
                    if l.startswith('data arrival time'):
                        processing = True
                        continue

                if processing is True:
                    if l.startswith('clock') and not l.startswith(
                        ('clock source latency', 'clock uncertainty')):
                        clock = l.split()[1]
                        if clock in clocks:
                            if critical_paths is None:
                                critical_paths = dict()

                            if clock not in critical_paths:
                                critical_paths[clock] = dict()
                                critical_paths[clock]['requested'] = float(
                                    l.split()[-1]
                                )

                    if l.startswith('slack'):
                        if critical_paths is None:
                            in_block = False
                            processing = False
                            continue
                        if clock in clocks and not 'met' in critical_paths[
                                clock]:
                            critical_paths[clock]['met'] = '(MET)' in l
                            critical_paths[clock]['violation'] = float(
                                l.split()[-1]
                            ) if not critical_paths[clock]['met'] else 0.0
                        in_block = False
                        processing = False

        return critical_paths

    def max_freq(self):
        def safe_division_by_zero(n, d):
            return n / d if d else 0.0

        freqs = dict()
        clocks = dict()
        route_log = self.out_dir + '/route.log'

        intra_domain_processing = False

        with open(route_log, 'r') as fp:
            for l in fp:
                if "Final critical path" in l and "Fmax" in l:
                    clk = 'clk'
                    fields = l.split(",")
                    cpd = float(fields[0].split(":")[1].split()[0].strip())
                    freqs[clk] = safe_division_by_zero(1e9, cpd)

                if l == "Intra-domain critical path delays (CPDs):\n":
                    intra_domain_processing = True
                    continue

                if intra_domain_processing:
                    if len(l.strip('\n')) == 0:
                        intra_domain_processing = False
                        continue

                    fields = l.split(':')
                    group = fields[0].split()[0]
                    freqs[group] = safe_division_by_zero(
                        1e9, float(fields[1].split()[0].strip())
                    )

        for clk in freqs:
            criticals = self.get_critical_paths(clk, 'setup')
            clocks[clk] = dict()
            clocks[clk]['actual'] = freqs[clk]
            if criticals is not None:
                clocks[clk]['requested'] = safe_division_by_zero(
                    1e9, criticals[clk]['requested']
                )
                clocks[clk]['met'] = criticals[clk]['met']
                clocks[clk]['setup_violation'] = criticals[clk]['violation']
            criticals = self.get_critical_paths(clk, 'hold')
            if criticals is not None:
                clocks[clk]['hold_violation'] = criticals[clk]['violation']
                if 'requested' not in clocks[clk]:
                    clocks[clk]['requested'] = safe_division_by_zero(
                        1e9, criticals[clk]['requested']
                    )
                if 'met' not in clocks[clk]:
                    clocks[clk]['met'] = criticals[clk]['met']
            for v in ['requested', 'setup_violation', 'hold_violation']:
                if v not in clocks[clk]:
                    clocks[clk][v] = 0.0
            if 'met' not in clocks[clk]:
                clocks[clk]['met'] = None

        return clocks

    def get_resources(self):
        """
        pack.log:
        (...)
        Pb types usage...
          GND          : 1
          BLK-TL-IOPAD : 2
          lut          : 1
          IOB33_MODES  : 2
          COMMON_LUT_AND_F78MUX : 1
          ALUT         : 1
          COMMON_SLICE : 6
          FDRE         : 24
          REG_FDSE_or_FDRE : 24
          SYN-GND      : 1
          BLK-TL-SLICEL : 6
          CEUSEDMUX    : 6
          CARRY4_VPR   : 6
          outpad       : 1
          A5LUT        : 1
          SLICEL0      : 6
          IOB33        : 2
          CE_VCC       : 24
          SRUSEDMUX    : 6
          inpad        : 1
          SLICE_FF     : 6
          SR_GND       : 24
        (...)
        """
        pack_logfile = self.out_dir + "/pack.log"
        resources = {}
        with open(pack_logfile, 'r') as fp:
            processing = False
            for l in fp:
                l = l.strip()
                if l == "Pb types usage...":
                    processing = True
                    continue

                if not processing:
                    continue
                else:
                    if len(l) == 0:
                        break
                    res = l.split(":")
                    restype = res[0].strip()
                    rescount = int(res[1].strip())
                    if restype in resources:
                        resources[restype] += rescount
                    else:
                        resources[restype] = rescount

        return resources

    def resources(self):
        lut = 0
        dff = 0
        carry = 0
        iob = 0
        pll = 0
        bram = 0

        res = self.get_resources()

        for nlut in ['ALUT', 'BLUT', 'CLUT', 'DLUT']:
            if nlut in res:
                lut += res[nlut]

        for nff in ['FDRE', 'FDSE', 'FDPE', 'FDCE']:
            if nff in res:
                dff += res[nff]

        if 'CARRY4_VPR' in res:
            carry += res['CARRY4_VPR']
        if 'outpad' in res:
            iob += res['outpad']
        if 'inpad' in res:
            iob += res['inpad']
        if 'RAMB18E1_Y0' in res:
            bram += res['RAMB18E1_Y0']
        if 'RAMB18E1_Y1' in res:
            bram += res['RAMB18E1_Y1']
        if 'PLLE2_ADV' in res:
            pll = res['PLLE2_ADV']

        ret = {
            "LUT": str(lut),
            "DFF": str(dff),
            "BRAM": str(bram),
            "CARRY": str(carry),
            "GLB": None,
            "PLL": str(pll),
            "IOB": str(iob),
        }
        return ret

    @staticmethod
    def yosys_ver():
        # Yosys 0.7+352 (git sha1 baddb017, clang 3.8.1-24 -fPIC -Os)
        return subprocess.check_output(
            "yosys -V", shell=True, universal_newlines=True
        ).strip()

    @staticmethod
    def vpr_version():
        '''
        vpr  --version

        VPR FPGA Placement and Routing.
        Version: 8.0.0-dev+vpr-7.0.5-6027-g94a747729
        Revision: vpr-7.0.5-6027-g94a747729
        Compiled: 2018-06-21T16:45:11 (release build)
        Compiler: GNU 6.3.0 on Linux-4.9.0-5-amd64 x86_64
        University of Toronto
        vtr-users@googlegroups.com
        This is free open source code under MIT license.
        '''
        out = subprocess.check_output(
            "vpr --version", shell=True, universal_newlines=True
        ).strip()
        version = None
        revision = None
        for l in out.split('\n'):
            l = l.strip()
            if l.find('Version:') == 0:
                version = l
            if l.find('Revision:') == 0:
                revision = l
        assert version is not None
        assert revision is not None
        return version + ', ' + revision

    def versions(self):
        return {
            'yosys': VPR.yosys_ver(),
            'vpr': VPR.vpr_version(),
        }

    @staticmethod
    def seedable():
        return True

    @staticmethod
    def check_env():
        return {
            'yosys': have_exec('yosys'),
            'vpr': have_exec(VPR.vpr_bin()),
        }


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

        self.dbroot = os.getenv('XRAY_DATABASE_DIR', None)

        assert self.dbroot

    def max_freq(self):
        report_file = os.path.join(self.out_dir, 'timing_summary.rpt')
        return get_vivado_max_freq(report_file)

    def run_steps(self):
        with Timed(self, 'synthesis'):
            self.backend.build_main(self.top + '.eblif')
        with Timed(self, 'pack'):
            self.backend.build_main(self.top + '.net')
        with Timed(self, 'place'):
            self.backend.build_main(self.top + '.place')
        with Timed(self, 'route'):
            self.backend.build_main(self.top + '.route')
        with Timed(self, 'fasm'):
            self.backend.build_main(self.top + '.fasm')
        with Timed(self, 'bitstream'):
            self.backend.build_main(self.top + '.bit')
        with Timed(self, 'fasm2bels'):
            self.backend.build_main('timing_summary.rpt')


class NextpnrXilinx(Toolchain):
    '''nextpnr using Yosys for synthesis'''
    carries = (False, )

    def __init__(self, rootdir):
        Toolchain.__init__(self, rootdir)
        self.toolchain = 'nextpnr'
        self.files = []

    def run(self):
        with Timed(self, 'total'):
            with Timed(self, 'prepare'):
                os.makedirs(self.out_dir, exist_ok=True)

                for f in self.srcs:
                    self.files.append(
                        {
                            'name': os.path.realpath(f),
                            'file_type': 'verilogSource'
                        }
                    )

                if self.xdc:
                    self.files.append(
                        {
                            'name': os.path.realpath(self.xdc),
                            'file_type': 'xdc'
                        }
                    )

                chip = self.family + self.device

                chipdb = os.path.join(
                    self.rootdir, 'env', 'conda', 'pkgs', 'nextpnr-xilinx*',
                    'share', 'nextpnr-xilinx',
                    '{}{}.bin'.format(self.family, self.part)
                )
                self.files.append(
                    {
                        'name': os.path.realpath(chipdb),
                        'file_type': 'bba'
                    }
                )

                self.edam = {
                    'files': self.files,
                    'name': self.project_name,
                    'toplevel': self.top,
                    'tool_options':
                        {
                            'symbiflow':
                                {
                                    'part': chip,
                                    'package': self.package,
                                    'vendor': 'xilinx',
                                    'builddir': '.',
                                    'pnr': 'nextpnr'
                                }
                        }
                }
                self.backend = edalize.get_edatool('symbiflow')(
                    edam=self.edam, work_root=self.out_dir
                )
                self.backend.configure("")

            with Timed(self, 'fasm'):
                self.backend.build_main(self.project_name + '.fasm')

            with Timed(self, 'bitstream'):
                self.backend.build_main(self.project_name + '.bit')

    def get_critical_paths(self, clocks, timing):
        #TODO critical paths
        return None

    def max_freq(self):
        #TODO max freq
        clocks = dict()

        return clocks

    def get_resources(self):
        #TODO resources
        resources = {}

        return resources

    def resources(self):
        lut = 0
        dff = 0
        carry = 0
        iob = 0
        pll = 0
        bram = 0

        res = self.get_resources()

        if 'lut' in res:
            lut = res['lut']
        if 'REG_FDSE_or_FDRE' in res:
            dff = dff = res['REG_FDSE_or_FDRE']
        if 'CARRY4_VPR' in res:
            carry = carry + res['CARRY4_VPR']
        if 'outpad' in res:
            iob = iob + res['outpad']
        if 'inpad' in res:
            iob = iob + res['inpad']
        if 'RAMB18E1_Y0' in res:
            bram += res['RAMB18E1_Y0']
        if 'RAMB18E1_Y1' in res:
            bram += res['RAMB18E1_Y1']
        if 'PLLE2_ADV' in res:
            pll = res['PLLE2_ADV']

        ret = {
            "LUT": None,
            "DFF": None,
            "BRAM": None,
            "CARRY": None,
            "GLB": None,
            "PLL": None,
            "IOB": None,
        }
        return ret

    @staticmethod
    def yosys_ver():
        # Yosys 0.7+352 (git sha1 baddb017, clang 3.8.1-24 -fPIC -Os)
        return subprocess.check_output(
            "yosys -V", shell=True, universal_newlines=True
        ).strip()

    @staticmethod
    def nextpnr_version():
        '''
        nextpnr-xilinx  --version
        '''
        return subprocess.check_output(
            "nextpnr-xilinx --version",
            shell=True,
            universal_newlines=True,
            stderr=subprocess.STDOUT
        ).strip()

    def versions(self):
        return {
            'yosys': NextpnrXilinx.yosys_ver(),
            'nextpnr-xilinx': NextpnrXilinx.nextpnr_version(),
        }

    @staticmethod
    def seedable():
        return True

    @staticmethod
    def check_env():
        return {
            'yosys': have_exec('yosys'),
            'nextpnr': have_exec(NextpnrXilinx.nextpnr_bin()),
        }
