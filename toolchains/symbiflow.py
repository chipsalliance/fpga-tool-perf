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
from utils.utils import Timed, have_exec, which, get_file_dict, get_yosys_resources
from infrastructure.tool_parameters import ToolParametersHelper

YOSYS_REGEXP = re.compile("(Yosys [a-z0-9+.]+) (\(git sha1) ([a-z0-9]+),.*")


class VPR(Toolchain):
    '''VPR using Yosys for synthesis'''
    def __init__(self, rootdir):
        Toolchain.__init__(self, rootdir)
        self.toolchain = 'vpr'
        self.builddir = '.'
        self.files = []
        self.fasm2bels = False
        self.dbroot = None

        self.resources_map = dict(families=dict())
        self.resources_map["families"]["xc7"] = {
            'LUT': ('$lut', 'lut'),
            'DFF':
                (
                    'FDRE', 'FDSE', 'FDPE', 'FDCE', 'FDRE_ZINI', 'FDSE_ZINI',
                    'FDPE_ZINI', 'FDCE_ZINI'
                ),
            'CARRY': ('CARRY4_VPR', ),
            'IOB':
                (
                    'IBUF_VPR',
                    'OBUFT_VPR',
                    'IOBUF_VPR',
                    'OBUFTDS_M_VPR',
                    'OBUFTDS_S_VPR',
                    'IOBUFDS_M_VPR',
                    'IOBUFDS_S_VPR',
                ),
            'PLL': ('PLLE2_ADV'),
            'BRAM':
                (
                    'RAMB18E1_Y0',
                    'RAMB18E1_Y1',
                    'RAMB18E1_VPR',
                    ('RAMB36E1', 2),
                    ('RAMB36E1_PRIM', 2),
                ),
        }

    def prepare_edam(self, part):
        if self.fasm2bels and self.vendor == "xilinx":
            symbiflow = os.getenv('SYMBIFLOW', None)
            assert symbiflow

            device_aliases = {"a35t": "a50t"}

            chip_replace = part
            for k, v in device_aliases.items():
                chip_replace = part.replace(k, v)

            device_path = os.path.join(
                symbiflow, 'share', 'symbiflow', 'arch',
                '{}_test'.format(chip_replace)
            )

            rr_graph_path = os.path.join(device_path, '*rr_graph.real.bin')
            vpr_grid_path = os.path.join(device_path, 'vpr_grid_map.csv')
            self.files.append(get_file_dict(rr_graph_path, 'RRGraph'))
            self.files.append(get_file_dict(vpr_grid_path, 'VPRGrid'))

        seed = f"--seed {self.seed}" if self.seed else ""

        tool_params = self.get_tool_params()

        options = dict()
        options['part'] = part
        options['package'] = self.package
        options['vendor'] = self.vendor
        options['builddir'] = self.builddir
        options['pnr'] = 'vpr'
        options['vpr_options'] = tool_params + seed
        options['fasm2bels'] = self.fasm2bels
        options['dbroot'] = self.dbroot
        options['clocks'] = self.clocks

        edam = dict()
        edam['files'] = self.files
        edam['name'] = self.project_name
        edam['toplevel'] = self.top
        edam['tool_options'] = dict(symbiflow=options)

        return edam, tool_params

    def run_steps(self):
        try:
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
        finally:
            del os.environ['EDALIZE_LAUNCHER']

    def run(self):
        with Timed(self, 'total'):
            with Timed(self, 'prepare'):
                os.environ[
                    "EDALIZE_LAUNCHER"
                ] = f"source {os.path.abspath('env.sh') + ' xilinx-' + self.device} &&"
                os.makedirs(self.out_dir, exist_ok=True)

                edam, tool_params = self.prepare_edam(
                    self.family + self.device
                )

                if tool_params:
                    os.environ["EDALIZE_LAUNCHER"
                               ] += ' VPR_OPTIONS="--echo_file on"'

                self.backend = edalize.get_edatool('symbiflow')(
                    edam=edam, work_root=self.out_dir
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
            return ""

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

                        keys = list(clocks.keys())
                        if len(keys) == 1 and 'clk' in keys:
                            clock = 'clk'

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
                        if 'met' not in critical_paths[clock]:
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

        intra_domain_cpd_processing = False
        intra_domain_slack_processing = False

        with open(route_log, 'r') as fp:
            for l in fp:
                if "Final intra-domain worst hold" in l:
                    intra_domain_slack_processing = True
                    continue

                if "Final critical path" in l and "Fmax" in l:
                    assert len(freqs.keys()) <= 1, (freqs, self.design())

                    if len(freqs.keys()) < 1:
                        clk = 'clk'
                    else:
                        clk = list(freqs.keys())[0]

                    fields = l.split(",")
                    cpd = float(fields[0].split(":")[1].split()[0].strip())
                    freqs[clk] = safe_division_by_zero(1e9, cpd)

                if l == "Final intra-domain critical path delays (CPDs):\n":
                    intra_domain_cpd_processing = True
                    continue

                if intra_domain_slack_processing:
                    if len(l.strip('\n')) == 0:
                        intra_domain_slack_processing = False
                        continue

                    clk = l.split()[0]
                    freqs[clk] = None

                if intra_domain_cpd_processing:
                    if len(l.strip('\n')) == 0:
                        intra_domain_cpd_processing = False
                        continue

                    fields = l.split(':')
                    group = fields[0].split()[0]
                    freqs[group] = safe_division_by_zero(
                        1e9, float(fields[1].split()[0].strip())
                    )

        for clk in freqs:
            clocks[clk] = dict()
            clocks[clk]['actual'] = freqs[clk]

            criticals = self.get_critical_paths(clocks, 'setup')
            if criticals is not None and clk in criticals:
                clocks[clk]['requested'] = safe_division_by_zero(
                    1e9, criticals[clk]['requested']
                )
                clocks[clk]['met'] = criticals[clk]['met']
                clocks[clk]['setup_violation'] = criticals[clk]['violation']

            criticals = self.get_critical_paths(clocks, 'hold')
            if criticals is not None and clk in criticals:
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

    def get_vpr_resources(self):
        """
        pack.log:
        (...)
        Pb types usage...
          GND          : 1
          BLK-TL-IOPAD : 2
          lut          : 1
          IOB33_MODES  : 2
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
        synth_resources = get_yosys_resources(
            os.path.join(self.out_dir, f"{self.top}_synth.log")
        )
        synth_resources = self.get_resources_count(synth_resources)

        impl_resources = self.get_vpr_resources()
        impl_resources = self.get_resources_count(impl_resources)

        return {"synth": synth_resources, "impl": impl_resources}

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


class Quicklogic(VPR):
    '''Quicklogic using Yosys for synthesis'''
    def __init__(self, rootdir):
        VPR.__init__(self, rootdir)
        self.toolchain = 'quicklogic'
        self.files = []
        self.fasm2bels = False
        self.dbroot = None

        self.resources_map["families"]["eos"] = {
            'LUT':
                (
                    'Q_FRAG', 'C_FRAG', 'F_FRAG', 'T_FRAG', 'q_frag', 'c_frag',
                    'f_frag', 't_frag', 'b_frag'
                ),
            'DFF': (),
            'CARRY': (),
            'IOB': (
                'BIDIR_CELL',
                'CLOCK_CELL',
                'bidir',
                'clock_buf',
            ),
            'PLL': (),
            'BRAM': (),
        }

    def run(self):
        with Timed(self, 'total'):
            with Timed(self, 'prepare'):
                os.environ[
                    "EDALIZE_LAUNCHER"
                ] = f"source {os.path.abspath('env.sh') + ' quicklogic'} &&"
                os.makedirs(self.out_dir, exist_ok=True)

                edam, _ = self.prepare_edam(self.device)
                self.backend = edalize.get_edatool('symbiflow')(
                    edam=edam, work_root=self.out_dir
                )
                self.backend.configure("")

            self.run_steps()
