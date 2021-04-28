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
import re
import subprocess
import edalize

from toolchains.toolchain import Toolchain
from utils.utils import Timed, have_exec, which
from infrastructure.tool_parameters import ToolParametersHelper

YOSYS_REGEXP = re.compile("(Yosys [a-z0-9+.]+) (\(git sha1) ([a-z0-9]+),.*")


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

                if l == "Final intra-domain critical path delays (CPDs):\n":
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
            clocks[clk] = dict()
            clocks[clk]['actual'] = freqs[clk]

            criticals = self.get_critical_paths(clk, 'setup')
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

        log['pack'] = get_step_runtime('# Packing', pack_log)
        log['place'] = get_step_runtime('# Placement', place_log)
        log['route'] = get_step_runtime('# Routing', route_log)
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
        yosys_version = subprocess.check_output(
            "yosys -V", shell=True, universal_newlines=True
        ).strip()

        m = YOSYS_REGEXP.match(yosys_version)

        assert m, yosys_version

        return "{} {} {})".format(m.group(1), m.group(2), m.group(3))

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


class NextpnrGeneric(Toolchain):
    '''nextpnr using Yosys for synthesis'''
    resources_map = {
        'xilinx':
            {
                'LUT': ('SLICE_LUTX', ),
                'DFF': ('SLICE_FFX', ),
                'CARRY': ('CARRY4', ),
                'IOB':
                    (
                        'IOB33M_OUTBUF',
                        'IOB33M_INBUF_EN',
                        'IOB33_OUTBUF',
                        'IOB33_INBUF_EN',
                    ),
                'PLL': ('PLLE2_ADV_PLLE2_ADV', ),
                'BRAM': (
                    'RAMB18E1_RAMB18E1',
                    'RAMB36E1_RAMB36E1',
                ),
            },
        'fpga_interchange':
            {
                'xilinx':
                    {
                        'LUT': ('LUTS', ),
                        'DFF': ('CARRY', ),
                        'CARRY': ('FLIP_FLOPS', ),
                        'IOB': (
                            'IBUFs',
                            'OBUFs',
                        ),
                        'PLL': ('PLL', ),
                        'BRAM': ('BRAMS', ),
                    },
            },
    }

    def __init__(self, rootdir):
        Toolchain.__init__(self, rootdir)
        self.arch = None
        self.vendor = None
        self.chipdb = None
        self.chip = None
        self.env_script = None
        self.builddir = "."
        self.dbroot = None
        self.files = list()
        self.yosys_synth_opts = list()
        self.yosys_template = None
        self.schema_dir = None
        self.device_file = None
        self.options = str()
        self.fasm2bels = False

    def get_share_data(self):
        out = subprocess.run(
            ["find", ".", "-name", self.toolchain_bin], stdout=subprocess.PIPE
        )
        nextpnr_locations = out.stdout.decode('utf-8').split('\n')
        nextpnr_location = None

        for location in nextpnr_locations:
            if "env/bin/{}".format(self.toolchain_bin) in location:
                nextpnr_location = os.path.abspath(os.path.dirname(location))
                break

        assert nextpnr_location

        return os.path.join(nextpnr_location, '..', 'share')

    def configure(self):
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

        self.files.append(
            {
                'name': os.path.realpath(self.chipdb),
                'file_type': 'bba'
            }
        )

        self.yosys_synth_opts = [
            "-flatten", "-nowidelut", "-abc9", "-arch {}".format(self.family),
            "-nocarry", "-nodsp"
        ]

        if self.fasm2bels and self.arch is not "fpga-interchange":
            symbiflow = os.getenv('SYMBIFLOW', None)
            assert symbiflow

            device_aliases = {"a35t": "a50t"}

            chip_replace = self.chip
            for k, v in device_aliases.items():
                chip_replace = self.chip.replace(k, v)

            device_path = os.path.join(
                symbiflow, 'share', 'symbiflow', 'arch',
                '{}_test'.format(chip_replace)
            )

            self.files.append(
                {
                    'name':
                        os.path.realpath(
                            os.path.join(device_path, '*rr_graph.real.bin')
                        ),
                    'file_type':
                        'RRGraph'
                }
            )

            self.files.append(
                {
                    'name':
                        os.path.realpath(
                            os.path.join(device_path, 'vpr_grid_map.csv')
                        ),
                    'file_type':
                        'VPRGrid'
                }
            )

        yosys_template_name = '{}_yosys_template.tcl'.format(self.toolchain)
        yosys_template_src = os.path.realpath(
            os.path.join(
                self.rootdir, 'src', 'yosys_templates', yosys_template_name
            )
        )
        if os.path.exists(yosys_template_src):
            # Copy yosys_template to build dir as it needs edalize procs from there
            self.yosys_template = os.path.realpath(
                os.path.join(self.out_dir, yosys_template_name)
            )
            with open(yosys_template_src,
                      "r") as src_tcl, open(self.yosys_template,
                                            "w") as dest_tcl:
                data = src_tcl.read()
                dest_tcl.write(data)

        self.symbiflow_options = {
            'arch': self.arch,
            'part': self.chip,
            'package': self.package,
            'vendor': self.vendor,
            'builddir': self.builddir,
            'pnr': 'nextpnr',
            'yosys_synth_options': self.yosys_synth_opts,
            'yosys_template': self.yosys_template,
            'fasm2bels': self.fasm2bels,
            'dbroot': self.dbroot,
            'schema_dir': self.schema_dir,
            'device': self.device_file,
            'clocks': self.clocks,
            'environment_script': self.env_script,
            'options': self.options
        }

        if self.fasm2bels and self.arch is not "fpga-interchange":
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

            # These variables are needed in 'nextpnr_fasm2bels_yosys_template.tcl'
            os.environ["PART_JSON_PATH"] = part_json
            os.environ["XDC_PATH"] = self.xdc

    def run_steps(self):
        with Timed(self, 'bitstream'):
            self.backend.build_main(self.project_name + '.bit')

    def generic_run(self, prepare_edam):
        with Timed(self, 'total'):
            with Timed(self, 'prepare'):
                self.edam = prepare_edam()
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
                    regex = ".*\'(.*)\': ([0-9]*\.[0-9]*).*\(([A-Z]*) at ([0-9]*\.[0-9]*).*"
                    match = re.match(regex, line)
                    if match:
                        clk_name = match.groups()[0]
                        clk_freq = float(match.groups()[1])
                        req_clk_freq = float(match.groups()[3])

                        clocks[clk_name] = dict()
                        clocks[clk_name]['actual'] = float(
                            "{:.3f}".format(clk_freq)
                        )
                        clocks[clk_name]['requested'] = float(
                            "{:.3f}".format(req_clk_freq)
                        )
                        clocks[clk_name]['met'] = match.groups()[2] == "PASS"
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
        resources_count = {
            "LUT": 0,
            "DFF": 0,
            "BRAM": 0,
            "CARRY": 0,
            "GLB": None,
            "PLL": 0,
            "IOB": 0,
        }

        res = self.get_resources()

        # Check arch:
        # xilinx - NextpnrXilinx
        # fpga_interchange - NextpnrFPGAInterchange (multi-vendor target)
        res_map = None
        if self.arch == 'xilinx':
            res_map = self.resources_map[self.arch]
        elif self.arch == 'fpga_interchange':
            res_map = self.resources_map[self.arch][self.vendor]

        assert res_map is not None, "Resources map for arch: {}, vendor: {} doesn't exist".format(
            self.arch, self.vendor
        )

        for res_type, res_names in res_map.items():
            for res_name in res_names:
                if res_name in res:
                    resources_count[res_type] += res[res_name]

        return resources_count

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
        yosys_version = subprocess.check_output(
            "yosys -V", shell=True, universal_newlines=True
        ).strip()

        m = YOSYS_REGEXP.match(yosys_version)

        assert m

        return "{} {} {})".format(m.group(1), m.group(2), m.group(3))

    @staticmethod
    def nextpnr_version(toolchain):
        '''
        nextpnr-<variant>  --version
        '''
        return subprocess.check_output(
            'bash -c ". ./env.sh nextpnr && {} --version"'.format(toolchain),
            shell=True,
            universal_newlines=True,
            stderr=subprocess.STDOUT
        ).strip()

    def versions(self):
        return {
            'yosys':
                NextpnrGeneric.yosys_ver(),
            'nextpnr-{}'.format(self.toolchain_bin):
                self.nextpnr_version(self.toolchain_bin),
        }

    @staticmethod
    def seedable():
        return True

    @staticmethod
    def check_env(toolchain):
        return {
            'yosys': have_exec('yosys'),
            'nextpnr': have_exec('{}'.format(toolchain)),
            'prjxray-config': have_exec('prjxray-config'),
        }


class NextpnrFPGAInterchange(NextpnrGeneric):
    '''nextpnr fpga-interchange variant using Yosys for synthesis'''
    carries = (False, )

    def __init__(self, rootdir):
        NextpnrGeneric.__init__(self, rootdir)
        self.arch = "fpga_interchange"
        self.toolchain = "nextpnr-fpga_interchange"
        self.toolchain_bin = "nextpnr-fpga_interchange"

    def prepare_edam(self):
        assert "fasm2bels" not in self.toolchain, "fasm2bels unsupported for fpga_interchange variant"
        self.chip = self.family + self.device
        share_dir = NextpnrGeneric.get_share_data(self)

        self.chipdb = os.path.join(
            share_dir, 'nextpnr-fpga_interchange', 'chipdb',
            '{}.bin'.format(self.chip)
        )

        self.schema_dir = os.path.join(
            self.rootdir, 'third_party', 'fpga-interchange-schema',
            'interchange'
        )

        self.files.append(
            {
                'name': os.path.realpath(self.chipdb),
                'file_type': 'bba'
            }
        )
        self.device_file = os.path.join(
            share_dir, 'nextpnr-fpga_interchange', 'devices',
            '{}.device'.format(self.chip)
        )
        self.files.append(
            {
                'name': os.path.realpath(self.device_file),
                'file_type': 'device'
            }
        )

        self.options = '--log nextpnr.log'
        self.env_script = os.path.abspath(
            'env.sh'
        ) + ' nextpnr fpga_interchange-' + self.device

        # Run generic configure before constructing an edam
        NextpnrGeneric.configure(self)

        # Assemble edam
        edam = {
            'files': self.files,
            'name': self.project_name,
            'toplevel': self.top,
            'tool_options': {
                'symbiflow': self.symbiflow_options,
            }
        }

        return edam

    def run(self):
        NextpnrGeneric.generic_run(self, self.prepare_edam)

    # FIXME: currently we do not have precise timing info for this variant.
    # Fill the clock data with what we have...
    def max_freq(self):
        """Returns the max frequencies of the implemented design."""
        log_file = os.path.join(self.out_dir, 'nextpnr.log')

        clocks = dict()

        with open(log_file, "r") as file:
            for line in file:
                if "target frequency" in line:
                    regex = "target frequency ([0-9]*\.[0-9]*)"
                    match = re.search(regex, line)
                    if match:
                        clk_name = 'clk'
                        clk_freq = float(match.groups()[0])
                        req_clk_freq = clk_freq

                        clocks[clk_name] = dict()
                        clocks[clk_name]['actual'] = float(
                            "{:.3f}".format(clk_freq)
                        )
                        clocks[clk_name]['requested'] = float(
                            "{:.3f}".format(req_clk_freq)
                        )
                        clocks[clk_name]['met'] = True
                        clocks[clk_name]['setup_violation'] = 0
                        clocks[clk_name]['hold_violation'] = 0

        return clocks


class NextpnrXilinx(NextpnrGeneric):
    '''nextpnr Xilinx variant using Yosys for synthesis'''
    carries = (False, )

    def __init__(self, rootdir):
        NextpnrGeneric.__init__(self, rootdir)
        self.arch = "xilinx"
        self.toolchain = 'nextpnr-xilinx'
        self.toolchain_bin = 'nextpnr-xilinx'

    def prepare_edam(self):
        if "fasm2bels" in self.toolchain:
            self.fasm2bels = True
            self.toolchain_bin = self.toolchain.strip("-fasm2bels")
        self.chip = self.family + self.device
        share_dir = NextpnrGeneric.get_share_data(self)

        self.chipdb = os.path.join(
            share_dir, 'nextpnr-xilinx',
            '{}{}.bin'.format(self.family, self.part)
        )
        self.files.append(
            {
                'name': os.path.realpath(self.chipdb),
                'file_type': 'bba'
            }
        )

        self.env_script = os.path.abspath(
            'env.sh'
        ) + ' nextpnr xilinx-' + self.device
        self.options = '--timing-allow-fail'

        # Run generic configure before constructing an edam
        NextpnrGeneric.configure(self)

        edam = {
            'files': self.files,
            'name': self.project_name,
            'toplevel': self.top,
            'tool_options': {
                'symbiflow': self.symbiflow_options,
            }
        }

        return edam

    def run(self):
        NextpnrGeneric.generic_run(self, self.prepare_edam)


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
