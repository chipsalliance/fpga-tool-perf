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

import edalize
import os
import re
import subprocess

from toolchains.toolchain import Toolchain
from utils.utils import Timed, have_exec, get_file_dict, get_vivado_max_freq, get_yosys_resources

YOSYS_REGEXP = re.compile("(Yosys [a-z0-9+.]+) (\(git sha1) ([a-z0-9]+),.*")


class NextpnrGeneric(Toolchain):
    '''nextpnr using Yosys for synthesis'''
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
        self.yosys_additional_commands = list()
        self.schema_dir = None
        self.device_file = None
        self.fasm2bels = False
        self.tool_options = dict()

        self.nextpnr_log = "nextpnr.log"

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
        assert self.xdc

        os.makedirs(self.out_dir, exist_ok=True)

        self.files.append(get_file_dict(self.chipdb, 'bba'))

        if len(self.yosys_synth_opts) == 0:
            self.yosys_synth_opts = [
                "-flatten", "-nowidelut", "-abc9",
                "-arch {}".format(self.family), "-nodsp"
            ]

        if self.fasm2bels and self.arch != "fpga_interchange":
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

            rr_graph_path = os.path.join(device_path, '*rr_graph.real.bin')
            vpr_grid_path = os.path.join(device_path, 'vpr_grid_map.csv')
            self.files.append(get_file_dict(rr_graph_path, 'RRGraph'))
            self.files.append(get_file_dict(vpr_grid_path, 'VPRGrid'))

        options = self.tool_options
        options['arch'] = self.arch
        options['part'] = self.chip
        options['package'] = self.package
        options['vendor'] = self.vendor
        options['builddir'] = self.builddir
        options['pnr'] = 'nextpnr'
        options['yosys_synth_options'] = self.yosys_synth_opts
        options['yosys_additional_commands'] = self.yosys_additional_commands
        options['fasm2bels'] = self.fasm2bels
        options['dbroot'] = self.dbroot
        options['schema_dir'] = self.schema_dir
        options['device'] = self.device_file
        options['clocks'] = self.clocks
        options['nextpnr_options'] = self.options

    def run_steps(self):
        with Timed(self, 'bitstream'):
            self.backend.build_main(self.project_name + '.bit')

    def generic_run(self, prepare_edam):
        with Timed(self, 'total'):
            with Timed(self, 'prepare'):
                self.edam = prepare_edam()
                os.environ["EDALIZE_LAUNCHER"] = f"source {self.env_script} &&"
                self.backend = edalize.get_edatool('symbiflow')(
                    edam=self.edam, work_root=self.out_dir
                )
                self.backend.configure("")
            try:
                self.backend.build_main(self.project_name + '.fasm')
                self.run_steps()
            finally:
                del os.environ['EDALIZE_LAUNCHER']

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

        route_log = os.path.join(self.out_dir, self.nextpnr_log)
        self.wirelength = get_wirelength(route_log)

    def max_freq(self):
        """Returns the max frequencies of the implemented design."""
        log_file = os.path.join(self.out_dir, self.nextpnr_log)

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

        log_file = os.path.join(self.out_dir, self.nextpnr_log)

        with open(log_file, "r") as f:
            lines = f.readlines()

        processing = False
        for line in lines:
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
        synth_resources = get_yosys_resources(
            os.path.join(self.out_dir, "yosys.log")
        )
        synth_resources = self.get_resources_count(synth_resources)

        impl_resources = self.get_resources()
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
        nextpnr_log = os.path.join(self.out_dir, self.nextpnr_log)

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
            '{}'.format(self.toolchain_bin):
                self.nextpnr_version(self.toolchain_bin),
        }

    @staticmethod
    def seedable():
        return True

    @staticmethod
    def check_env(toolchain):
        return {
            'yosys': have_exec('yosys'),
            'nextpnr': have_exec(f'{toolchain}'),
        }


class NextpnrFPGAInterchange(NextpnrGeneric):
    '''nextpnr fpga-interchange variant using Yosys for synthesis'''
    def __init__(self, rootdir):
        NextpnrGeneric.__init__(self, rootdir)
        self.arch = "fpga_interchange"
        self.toolchain = "nextpnr-fpga-interchange"
        self.toolchain_bin = "nextpnr-fpga_interchange"

        self.resources_map = dict(families=dict())
        self.resources_map['families']['xc7'] = {
            'LUT': ('LUTS', 'LUT1', 'LUT2', 'LUT3', 'LUT4', 'LUT5', 'LUT6'),
            'DFF': ('FLIP_FLOPS', 'FDRE', 'FDSE', 'FDPE', 'FDCE'),
            'CARRY': ('CARRY', 'CARRY4'),
            'IOB':
                (
                    'IBUFs',
                    'OBUFs',
                    'IBUF',
                    'OBUF',
                    'OBUFT',
                    'IOBUF',
                    'OBUFTDS',
                    'OBUFDS',
                    ('IOBUF', 2),
                    ('IOBUFDS', 2),
                ),
            'PLL': ('PLL', 'PLLE2_ADV', 'MMCME2_ADV'),
            'BRAM': (
                'BRAMS',
                'RAMB18E1',
                ('RAMB36E1', 2),
            )
        }

    def prepare_edam(self):
        assert "fasm2bels" not in self.toolchain, "fasm2bels unsupported for fpga_interchange variant"
        self.chip = self.family + self.device
        share_dir = NextpnrGeneric.get_share_data(self)

        self.chipdb = os.path.join(
            self.rootdir, 'env', 'interchange', 'devices', self.chip,
            '{}.bin'.format(self.chip)
        )

        self.schema_dir = os.path.join(
            self.rootdir, 'third_party', 'fpga-interchange-schema',
            'interchange'
        )

        self.device_file = os.path.join(
            self.rootdir, 'env', 'interchange', 'devices', self.chip,
            '{}.device'.format(self.chip)
        )
        self.files.append(get_file_dict(self.device_file, 'device'))

        self.yosys_additional_commands = ["setundef -zero -params"]
        self.options = f"--log {self.nextpnr_log} --disable-lut-mapping-cache"
        self.env_script = os.path.abspath(
            'env.sh'
        ) + ' nextpnr fpga_interchange-' + self.device

        self.yosys_synth_opts = [
            "-flatten", "-nowidelut", "-arch {}".format(self.family), "-nodsp",
            "-nosrl"
        ]

        lib_file = os.path.join(
            self.rootdir, 'env', 'interchange', 'techmaps',
            'lib_{}.v'.format(self.family)
        )
        if os.path.isfile(lib_file):
            self.files.append(get_file_dict(lib_file, 'yosys_lib'))

        techmap_file = os.path.join(
            self.rootdir, 'env', 'interchange', 'techmaps',
            'remap_{}.v'.format(self.family)
        )
        if os.path.isfile(lib_file):
            self.yosys_additional_commands = [
                "techmap -map {}".format(techmap_file),
                "techmap -map {}".format(lib_file), "opt_expr -undriven",
                "opt_clean", "setundef -zero -params"
            ]
        else:
            self.yosys_additional_commands.extend(
                [
                    "techmap -map {}".format(techmap_file),
                    "opt_expr -undriven", "opt_clean", "setundef -zero -params"
                ]
            )

        # Run generic configure before constructing an edam
        NextpnrGeneric.configure(self)

        # Assemble edam
        edam = dict()
        edam['files'] = self.files
        edam['name'] = self.project_name
        edam['toplevel'] = self.top
        edam['tool_options'] = dict(symbiflow=self.tool_options)

        return edam

    def run_steps(self):
        with Timed(self, 'fasm'):
            self.backend.build_main(self.project_name + '.fasm')
        with Timed(self, 'bitstream'):
            self.backend.build_main(self.project_name + '.bit')

    def run(self):
        with Timed(self, 'total'):
            with Timed(self, 'prepare'):
                self.edam = self.prepare_edam()
                os.environ["EDALIZE_LAUNCHER"] = f"source {self.env_script} &&"
                self.backend = edalize.get_edatool('symbiflow')(
                    edam=self.edam, work_root=self.out_dir
                )
                self.backend.configure("")

            self.backend.build_main(self.project_name + '.phys')
            self.run_steps()

        with Timed(self, 'report_timing'):
            self.backend.build_main(self.project_name + '.timing')

        del os.environ["EDALIZE_LAUNCHER"]

        self.add_runtimes()
        self.add_wirelength()

    # FIXME: currently we do not have precise timing info for this variant.
    # Fill the clock data with what we have...
    def max_freq(self):
        report_file = os.path.join(self.out_dir, f"{self.project_name}.timing")
        return get_vivado_max_freq(report_file)


class NextpnrXilinx(NextpnrGeneric):
    '''nextpnr Xilinx variant using Yosys for synthesis'''
    def __init__(self, rootdir):
        NextpnrGeneric.__init__(self, rootdir)
        self.arch = "xilinx"
        self.toolchain = 'nextpnr-xilinx'
        self.toolchain_bin = 'nextpnr-xilinx'

        self.resources_map = {
            'LUT':
                ('SLICE_LUTX', 'LUT1', 'LUT2', 'LUT3', 'LUT4', 'LUT5', 'LUT6'),
            'DFF': ('SLICE_FFX', 'FDRE', 'FDSE', 'FDPE', 'FDCE'),
            'CARRY': ('CARRY4', ),
            'IOB':
                (
                    'IOB33M_OUTBUF',
                    'IOB33M_INBUF_EN',
                    'IOB33_OUTBUF',
                    'IOB33_INBUF_EN',
                    'IBUF',
                    'OBUF',
                ),
            'PLL': ('PLLE2_ADV_PLLE2_ADV', 'PLLE2_ADV'),
            'BRAM':
                (
                    'RAMB18E1_RAMB18E1',
                    ('RAMB36E1_RAMB36E1', 2),
                    'RAMB18E1',
                    ('RAMB36E1', 2),
                ),
        }

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
        self.files.append(get_file_dict(self.chipdb, 'bba'))

        self.env_script = os.path.abspath(
            'env.sh'
        ) + ' nextpnr xilinx-' + self.device
        self.options = '--timing-allow-fail'

        # Run generic configure before constructing an edam
        NextpnrGeneric.configure(self)

        edam = dict()
        edam['files'] = self.files
        edam['name'] = self.project_name
        edam['toplevel'] = self.top
        edam['tool_options'] = dict(symbiflow=self.tool_options)

        return edam

    def run(self):
        NextpnrGeneric.generic_run(self, self.prepare_edam)


class NextpnrOxide(NextpnrGeneric):
    '''Nextpnr PnR + Yosys synthesis'''
    def __init__(self, rootdir):
        NextpnrGeneric.__init__(self, rootdir)
        self.toolchain = "nextpnr-nexus"
        self.toolchain_bin = "nextpnr-nexus"
        self.nextpnr_log = "next.log"

        self.resources_map = {
            'LUT': ('OXIDE_COMB'),
            'DFF': ('OXIDE_FF'),
            'CARRY': ('CCU2'),
            'IOB': ('SEIO33_CORE'),
            'PLL': ('PLL_CORE'),
            'BRAM': ('OXIDE_EBR', 'LRAM_CORE'),
        }

    def prepare_edam(self):
        os.makedirs(self.out_dir, exist_ok=True)
        args = f"--device {self.device} "
        args += "--timing-allow-fail "
        args += "--router router1 "
        if self.seed:
            args += " --seed %u" % (self.seed, )
        options = dict(nextpnr_options=args.split())

        edam = dict()
        edam['files'] = self.files
        edam['name'] = self.project_name
        edam['toplevel'] = self.top
        edam['tool_options'] = dict(oxide=options)

        self.env_script = os.path.abspath(
            'env.sh'
        ) + ' nextpnr lattice-' + self.device

        return edam

    def run(self):
        with Timed(self, 'total'):
            with Timed(self, 'prepare'):
                self.edam = self.prepare_edam()
                os.environ["EDALIZE_LAUNCHER"] = f"source {self.env_script} &&"
                self.backend = edalize.get_edatool('oxide')(
                    edam=self.edam, work_root=self.out_dir
                )
                self.backend.configure("")
            try:
                with Timed(self, 'fasm'):
                    self.backend.build_main(self.project_name + '.fasm')
                with Timed(self, 'bitstream'):
                    self.backend.build_main(self.project_name + '.bit')
            finally:
                del os.environ['EDALIZE_LAUNCHER']

        self.add_runtimes()
        self.add_wirelength()

    @staticmethod
    def seedable():
        return True

    @staticmethod
    def check_env():
        return {
            'yosys': have_exec('yosys'),
            'nextpnr-nexus': have_exec('nextpnr-nexus'),
        }
