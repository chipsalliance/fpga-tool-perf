import os
import re
import subprocess

import edalize

from toolchain import Toolchain
from utils import Timed, have_exec, which
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
        self.backend.build_main(self.top + '.eblif')
        with Timed(self, 'pack_all', unprinted_runtime=True):
            self.backend.build_main(self.top + '.net')
        with Timed(self, 'place_all', unprinted_runtime=True):
            self.backend.build_main(self.top + '.place')
        with Timed(self, 'route_all', unprinted_runtime=True):
            self.backend.build_main(self.top + '.route')
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
                symbiflow_options = {
                    'part':
                        chip,
                    'package':
                        self.package,
                    'vendor':
                        'xilinx',
                    'builddir':
                        '.',
                    'pnr':
                        'vpr',
                    'options':
                        tool_params,
                    'fasm2bels':
                        self.fasm2bels,
                    'dbroot':
                        self.dbroot,
                    'clocks':
                        self.clocks,
                    'seed':
                        self.seed,
                    'environment_script':
                        os.path.abspath('env.sh') + ' xilinx-' + self.device,
                }
                self.edam = {
                    'files': self.files,
                    'name': self.project_name,
                    'toplevel': self.top,
                    'tool_options': {
                        'symbiflow': symbiflow_options
                    }
                }
                self.backend = edalize.get_edatool('symbiflow')(
                    edam=self.edam, work_root=self.out_dir
                )
                self.backend.configure("")

            self.run_steps()
            self.add_runtimes()
            self.add_wirelength()
            self.add_maximum_memory_use()

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

    def add_wirelength(self):
        def get_wirelength(log_file):
            with open(log_file, 'r') as fp:
                for l in fp:
                    l = l.strip()
                    if 'Total wirelength:' in l:
                        return int(l.split()[2][:-1])
            return 0

        route_log = os.path.join(self.out_dir, 'route.log')
        self.wirelength = get_wirelength(route_log)

    def add_maximum_memory_use(self):
        def get_usage(log_file, token="max_rss"):
            unit_list = ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]
            memory_usage = list()
            with open(log_file, 'r') as fp:
                for l in fp:
                    l = l.strip()
                    if token in l:
                        l_split = l.split()
                        unit = l_split[l_split.index("(max_rss") + 2][:-1]
                        max_rss = float(l_split[l_split.index("(max_rss") + 1])
                        # convert memory to MiB
                        unit_index = unit_list.index(unit) - 2
                        if unit_index < 0:
                            max_rss = max_rss / (
                                1024 * (-unit_index)
                            )  # make unit index positive
                        elif unit_index > 0:
                            max_rss = max_rss * 1024 * unit_index

                        memory_usage.append(max_rss)

            return memory_usage

        pack_log = os.path.join(self.out_dir, 'pack.log')
        place_log = os.path.join(self.out_dir, 'place.log')
        route_log = os.path.join(self.out_dir, 'route.log')
        fasm_log = os.path.join(self.out_dir, 'fasm.log')

        self.maximum_memory_use = 0.0
        self.maximum_memory_use = max(
            max(get_usage(pack_log)), self.maximum_memory_use
        )
        self.maximum_memory_use = max(
            max(get_usage(place_log)), self.maximum_memory_use
        )
        self.maximum_memory_use = max(
            max(get_usage(route_log)), self.maximum_memory_use
        )
        self.maximum_memory_use = max(
            max(get_usage(fasm_log)), self.maximum_memory_use
        )

    def max_freq(self):
        def safe_division_by_zero(n, d):
            return n / d if d else 0.0

        freqs = dict()
        clocks = dict()
        route_log = os.path.join(self.out_dir, 'route.log')

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

        for cd in clocks:
            clocks[cd]['actual'] = float(
                "{:.3f}".format(clocks[cd]['actual'] / 1e6)
            )
            clocks[cd]['requested'] = float(
                "{:.3f}".format(clocks[cd]['requested'] / 1e6)
            )

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
        pack_logfile = os.path.join(self.out_dir, "pack.log")
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

        if 'lut' in res:
            lut = res['lut']

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
        if 'RAMB36E1' in res:
            bram += res['RAMB36E1'] * 2
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

    def get_yosys_runtimes(self, logfile):
        runtime_re = 'CPU: user (\d+\.\d+)s system (\d+\.\d+)s'
        log = dict()
        with open(logfile, 'r') as fp:
            for l in fp:
                m = re.search(runtime_re, l)
                if not m:
                    continue
                time = float(m[1]) + float(m[2])
                log['synthesis'] = time

                return log

        assert False, "No run time found for yosys."

    def get_vpr_runtimes(self):
        def get_step_runtime(step, logfile):
            with open(logfile, 'r') as fp:
                for l in fp:
                    l = l.strip()
                    if '{} took'.format(step) in l:
                        l = l.split()
                        position = l.index("took") + 1
                        return float(l[position])

        def get_overhead_runtime(name, log):
            if name in log and "%s_all" % name in self.unprinted_runtimes:
                if 'overhead' not in log:
                    log['overhead'] = 0.0
                log['overhead'] += self.unprinted_runtimes["%s_all" % name
                                                           ] - log[name]

        log = dict()

        pack_log = os.path.join(self.out_dir, 'pack.log')
        place_log = os.path.join(self.out_dir, 'place.log')
        route_log = os.path.join(self.out_dir, 'route.log')
        fasm_log = os.path.join(self.out_dir, 'fasm.log')

        log['pack'] = get_step_runtime('Packing', pack_log)
        log['place'] = get_step_runtime('Placement', place_log)
        log['route'] = get_step_runtime('Routing', route_log)
        # XXX: Need add to genfasm the amount of time it took to create the fasm file.
        #      For now the whole command execution time is considered
        log['fasm'] = get_step_runtime('The entire flow of VPR', fasm_log)

        get_overhead_runtime("pack", log)
        get_overhead_runtime("place", log)
        get_overhead_runtime("route", log)

        return log

    def add_runtimes(self):
        """Returns the runtimes of the various steps"""

        yosys_log = os.path.join(self.out_dir, '{}_synth.log'.format(self.top))

        synth_times = self.get_yosys_runtimes(yosys_log)
        impl_times = self.get_vpr_runtimes()

        for t in synth_times:
            self.add_runtime(t, synth_times[t])
        for t in impl_times:
            self.add_runtime(t, impl_times[t])

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
            'vpr': have_exec('vpr'),
            'prjxray-config': have_exec('prjxray-config')
        }


class NextpnrXilinx(Toolchain):
    '''nextpnr using Yosys for synthesis'''
    carries = (False, )

    def __init__(self, rootdir):
        Toolchain.__init__(self, rootdir)
        self.toolchain = 'nextpnr-xilinx'
        self.files = []
        self.fasm2bels = False
        self.dbroot = None

    def run_steps(self):
        with Timed(self, 'bitstream'):
            self.backend.build_main(self.project_name + '.bit')

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

                assert self.xdc
                self.files.append(
                    {
                        'name': os.path.realpath(self.xdc),
                        'file_type': 'xdc'
                    }
                )

                chip = self.family + self.device

                nextpnr_location = which(
                    program='nextpnr-xilinx', get_dir=True
                )
                assert nextpnr_location

                share_dir = os.path.join(nextpnr_location, '..', 'share')

                chipdb = os.path.join(
                    share_dir, 'nextpnr-xilinx',
                    '{}{}.bin'.format(self.family, self.part)
                )
                self.files.append(
                    {
                        'name': os.path.realpath(chipdb),
                        'file_type': 'bba'
                    }
                )

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

                symbiflow_options = {
                    'part':
                        chip,
                    'package':
                        self.package,
                    'vendor':
                        'xilinx',
                    'builddir':
                        '.',
                    'pnr':
                        'nextpnr',
                    'yosys_synth_options':
                        [
                            "-flatten", "-nowidelut", "-abc9", "-arch xc7",
                            "-nocarry"
                        ],
                    'fasm2bels':
                        self.fasm2bels,
                    'dbroot':
                        self.dbroot,
                    'clocks':
                        self.clocks,
                    'environment_script':
                        os.path.abspath('env.sh') + ' xilinx-' + self.device,
                }

                if self.fasm2bels:
                    bitstream_device = None
                    if self.device.startswith('a'):
                        bitstream_device = 'artix7'
                    if self.device.startswith('z'):
                        bitstream_device = 'zynq7'
                    if self.device.startswith('k'):
                        bitstream_device = 'kintex7'

                    assert bitstream_device

                    part_json = os.path.join(
                        self.dbroot, bitstream_device, self.family + self.part,
                        'part.json'
                    )
                    symbiflow_options['yosys_additional_commands'] = [
                        "plugin -i xdc",
                        "yosys -import",
                        "read_xdc -part_json {} {}".format(
                            part_json, os.path.realpath(self.xdc)
                        ),
                        "clean",
                        "write_blif -attr -param {}.eblif".format(
                            self.project_name
                        ),
                    ]

                self.edam = {
                    'files': self.files,
                    'name': self.project_name,
                    'toplevel': self.top,
                    'tool_options': {
                        'symbiflow': symbiflow_options,
                    }
                }
                self.backend = edalize.get_edatool('symbiflow')(
                    edam=self.edam, work_root=self.out_dir
                )
                self.backend.configure("")

            self.backend.build_main(self.project_name + '.fasm')

            self.run_steps()

            self.add_runtimes()
            self.add_wirelength()

    def add_wirelength(self):
        def get_wirelength(log_file):
            wirelen = 0
            with open(log_file, 'r') as fp:
                for l in fp:
                    l = l.strip()
                    if 'wirelen =' in l:
                        l_split = l.split()
                        wirelen = l_split[l_split.index("wirelen") + 2]
                        wirelen = ''.join(c for c in wirelen if c.isdigit())
                        wirelen = int(wirelen)
            return wirelen

        route_log = os.path.join(self.out_dir, 'nextpnr.log')
        self.wirelength = get_wirelength(route_log)

    def max_freq(self):
        """Returns the max frequencies of the implemented design."""
        log_file = os.path.join(self.out_dir, 'nextpnr.log')

        clocks = dict()

        with open(log_file, "r") as file:
            in_routing = False
            for line in file:
                if "Routing.." in line:
                    in_routing = True

                if "Max frequency" in line and in_routing:
                    regex = ".*\'(.*)\': ([0-9]*\.[0-9]*).*"
                    match = re.match(regex, line)
                    if match:
                        clk_name = match.groups()[0]
                        clk_freq = float(match.groups()[1])

                        clocks[clk_name] = dict()
                        clocks[clk_name]['actual'] = float(
                            "{:.3f}".format(clk_freq)
                        )
                        clocks[clk_name]['requested'] = 0
                        clocks[clk_name]['met'] = None
                        clocks[clk_name]['setup_violation'] = 0
                        clocks[clk_name]['hold_violation'] = 0

        return clocks

    def get_resources(self):
        """Returns a dictionary with the resources parsed from the nextpnr log file"""

        resources = dict()

        log_file = os.path.join(self.out_dir, 'nextpnr.log')

        with open(log_file, "r") as file:
            processing = False
            for line in file:
                line = line.strip()

                if "Device utilisation" in line:
                    processing = True
                    continue

                if not processing:
                    continue
                else:
                    if len(line) == 0:
                        break

                    res = line.split(":")
                    res_type = res[1].strip()

                    regex = "([0-9]*)\/.*"
                    match = re.match(regex, res[2].lstrip())

                    assert match

                    res_count = int(match.groups()[0])
                    resources[res_type] = res_count

        return resources

    def resources(self):
        lut = 0
        dff = 0
        carry = 0
        iob = 0
        pll = 0
        bram = 0

        res = self.get_resources()

        if 'SLICE_LUTX' in res:
            lut = res['SLICE_LUTX']
        if 'SLICE_FFX' in res:
            dff = dff = res['SLICE_FFX']
        if 'CARRY4' in res:
            carry = res['CARRY4']
        if 'PAD' in res:
            iob = iob + res['PAD']
        if 'RAMB18E1_RAMB18E1' in res:
            bram = res['RAMB18E1_RAMB18E1']
        if 'RAMB36E1_RAMB36E1' in res:
            bram += res['RAMB36E1_RAMB36E1'] * 2
        if 'PLLE2_ADV_PLLE2_ADV' in res:
            pll = res['PLLE2_ADV_PLLE2_ADV']

        ret = {
            "LUT": lut,
            "DFF": dff,
            "BRAM": bram,
            "CARRY": carry,
            "GLB": None,
            "PLL": pll,
            "IOB": iob,
        }
        return ret

    def get_yosys_runtimes(self, logfile):
        runtime_re = 'CPU: user (\d+\.\d+)s system (\d+\.\d+)s'
        log = dict()
        with open(logfile, 'r') as fp:
            for l in fp:
                m = re.search(runtime_re, l)
                if not m:
                    continue
                time = float(m[1]) + float(m[2])
                log['synthesis'] = time

                return log

        assert False, "No run time found for yosys."

    def get_nextpnr_runtimes(self, logfile):
        log = dict()

        placement = 0.0
        routing = 0.0

        with open(logfile, 'r') as fp:
            for l in fp:
                l = l.strip()
                if len(l) == 0:
                    continue

                l = l.lstrip("Info: ")
                heap_placer_string = "HeAP Placer Time: "
                sa_placer_string = "SA placement time "

                router1_string = "Router1 time "
                router2_string = "Router2 time "

                if heap_placer_string in l:
                    time = float(l.lstrip(heap_placer_string).rstrip("s"))
                    placement += time
                elif sa_placer_string in l:
                    time = float(l.lstrip(sa_placer_string).rstrip("s"))
                    placement += time
                elif router1_string in l:
                    time = float(l.lstrip(router1_string).rstrip("s"))
                    routing += time
                elif router2_string in l:
                    time = float(l.lstrip(router2_string).rstrip("s"))
                    routing += time

        log["place"] = placement
        log["route"] = routing

        return log

    def add_runtimes(self):
        """Returns the runtimes of the various steps"""

        yosys_log = os.path.join(self.out_dir, 'yosys.log')
        nextpnr_log = os.path.join(self.out_dir, 'nextpnr.log')

        synth_times = self.get_yosys_runtimes(yosys_log)
        impl_times = self.get_nextpnr_runtimes(nextpnr_log)

        for t in synth_times:
            self.add_runtime(t, synth_times[t])
        for t in impl_times:
            self.add_runtime(t, impl_times[t])

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
            'nextpnr': have_exec('nextpnr-xilinx'),
            'prjxray-config': have_exec('prjxray-config'),
        }


class Quicklogic(VPR):
    '''Quicklogic using Yosys for synthesis'''
    carries = (False, )

    def __init__(self, rootdir):
        VPR.__init__(self, rootdir)
        self.toolchain = 'quicklogic'
        self.files = []
        self.fasm2bels = False
        self.dbroot = None

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

                tool_params = []
                symbiflow_options = {
                    'part':
                        self.device,
                    'package':
                        self.package,
                    'vendor':
                        'quicklogic',
                    'builddir':
                        '.',
                    'pnr':
                        'vpr',
                    'options':
                        tool_params,
                    'fasm2bels':
                        self.fasm2bels,
                    'dbroot':
                        self.dbroot,
                    'clocks':
                        self.clocks,
                    'seed':
                        self.seed,
                    'environment_script':
                        os.path.abspath('env.sh') + ' quicklogic',
                }

                self.edam = {
                    'files': self.files,
                    'name': self.project_name,
                    'toplevel': self.top,
                    'tool_options': {
                        'symbiflow': symbiflow_options
                    }
                }
                self.backend = edalize.get_edatool('symbiflow')(
                    edam=self.edam, work_root=self.out_dir
                )
                self.backend.configure("")

            self.run_steps()
