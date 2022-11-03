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

import collections
import datetime
import glob
import json
import math
from pathlib import Path
import os
import re
import shutil
from subprocess import check_call
import sys
import time

from utils.utils import Timed, have_exec, get_file_dict


class Toolchain:
    '''A toolchain takes in verilog files and produces a .bitstream'''
    def __init__(self, rootdir):
        self.rootdir = rootdir
        self.runtimes = collections.OrderedDict()
        self.unprinted_runtimes = collections.OrderedDict()
        self.toolchain = None
        self.verbose = False
        self.cmds = []

        self.pcf = None
        self.sdc = None
        self.xdc = None
        self.pdc = None

        self.params_file = None
        self.params_string = None
        self.seed = None
        self.build = None
        self.build_type = None
        self.date = datetime.datetime.utcnow()

        self.family = None
        self.device = None
        self.package = None
        self.part = None
        self.board = None

        self.project_name = None
        self.srcs = None
        self.top = None
        self.out_dir = None
        self.clocks = None
        self.clock_aliases = None

        self.wirelength = None
        self.maximum_memory_use = None

    def canonicalize(self, fns):
        return [os.path.realpath(self.rootdir + '/' + fn) for fn in fns]

    def add_runtime(self, name, dt, parent=None, unprinted_runtime=False):
        collection = self.runtimes
        if unprinted_runtime:
            collection = self.unprinted_runtimes
        if parent is None:
            collection[name] = dt
        else:
            assert (parent not in collection
                    ) or (type(collection[parent]) is collections.OrderedDict)
            if parent not in collection:
                collection[parent] = collections.OrderedDict()
            collection[parent][name] = dt

    def add_common_files(self):
        """
        Adds common files for the EDAM configuration
        """

        for f in self.srcs:
            vhdl_type = 'vhdlSource'
            verilog_type = 'verilogSource'

            is_vhdl = f.endswith(".vhd") or f.endswith(".vhdl")
            is_verilog = f.endswith(".v")

            if is_vhdl:
                file_type = vhdl_type
            elif is_verilog:
                file_type = verilog_type

            self.files.append(get_file_dict(f, file_type))

        # Constraints files
        if self.pcf:
            self.files.append(get_file_dict(self.pcf, 'PCF'))

        if self.sdc:
            self.files.append(get_file_dict(self.sdc, 'SDC'))

        if self.xdc:
            self.files.append(get_file_dict(self.xdc, 'xdc'))

        if self.pdc:
            self.files.append(get_file_dict(self.pdc, 'PDC'))

    def optstr(self):
        tokens = []
        if self.pcf:
            tokens.append('pcf')
        if self.sdc:
            tokens.append('sdc')
        if self.xdc:
            tokens.append('xdc')
        if self.seed:
            tokens.append('seed-%08X' % (self.seed, ))
        return '_'.join(tokens)

    def design(self):
        ret = "{}_{}_{}_{}_{}".format(
            self.project_name, self.toolchain, self.family, self.part,
            self.board
        )

        if self.build_type:
            ret += '_' + self.build_type

        if self.build:
            ret += '_' + self.build

        op = self.optstr()
        if op:
            ret += '_' + op

        if self.seed:
            ret += '_seed_' + str(self.seed)

        return ret

    def project(
        self,
        project,
        family,
        device,
        package,
        board,
        vendor,
        params_file,
        params_string,
        out_dir=None,
        out_prefix=None,
        overwrite=False,
    ):
        self.family = family
        self.device = device
        self.package = package

        self.part = "".join(
            (device, package)
        ) if package is not None else device
        self.board = board
        self.vendor = vendor

        self.params_file = params_file
        self.params_string = params_string

        self.project_name = project['name']
        self.srcs = self.canonicalize(project['srcs'])
        for src in self.srcs:
            if not os.path.exists(src):
                raise ValueError("Missing source file %s" % src)
        self.add_common_files()

        self.top = project['top']

        self.clocks = project.get('clocks', None)
        self.clock_aliases = project.get('clock_aliases', None)

        out_prefix = out_prefix or 'build'
        os.makedirs(os.path.expanduser(out_prefix), exist_ok=True)

        if out_dir is None:
            out_dir = out_prefix + "/" + self.design()
        self.out_dir = out_dir
        if overwrite and os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(os.path.expanduser(out_dir), exist_ok=True)
        print('Writing to %s' % out_dir)
        data = project.get('data', None)
        if data:
            for f in data:
                dst = os.path.join(out_dir, os.path.basename(f))
                print("Copying data file {} to {}".format(f, dst))
                shutil.copy(f, dst)

    def cmd(self, cmd, argstr, env=None):
        print("Running: %s %s" % (cmd, argstr))
        self.cmds.append('%s %s' % (cmd, argstr))

        cmd_base = os.path.basename(cmd)
        with open("%s/%s.txt" % (self.out_dir, cmd_base), "w") as f:
            f.write("Running: %s %s\n\n" % (cmd_base, argstr))
        with Timed(self, cmd_base):
            if self.verbose:
                cmdstr = "(%s %s) |&tee -a %s.txt; (exit $PIPESTATUS )" % (
                    cmd, argstr, cmd
                )
                print("Running: %s" % cmdstr)
                print("  cwd: %s" % self.out_dir)
            else:
                cmdstr = "(%s %s) >& %s.txt" % (cmd, argstr, cmd_base)
            check_call(
                cmdstr,
                shell=True,
                executable='bash',
                cwd=self.out_dir,
                env=env
            )

    def get_runtimes(self):
        """Returns a standard runtime dictionary.

        Different tools have different names for the various EDA steps and,
        to generate a uniform data structure, these steps must fall into the correct
        standard category."""

        RUNTIME_ALIASES = {
            'prepare': ['prepare'],
            'synthesis': ['synth_design', 'synth', 'synthesis'],
            'optimization': ['opt_design'],
            'packing': ['pack'],
            'placement': ['place', 'place_design'],
            'routing': ['route', 'route_design'],
            'fasm': ['fasm'],
            'overhead': ['overhead'],
            'checkpoint': ['open_checkpoint'],
            'bitstream': ['write_bitstream', 'bitstream'],
            'reports':
                [
                    'report_power', 'report_methodology', 'report_drc',
                    'report_timing'
                ],
            'total': ['total'],
            'fasm2bels': ['fasm2bels'],
            'link design': ['link_design'],
            'phys opt design': ['phys_opt_design']
        }

        runtimes = {k: None for k in RUNTIME_ALIASES.keys()}

        def get_standard_runtime(runtime):
            for k, v in RUNTIME_ALIASES.items():
                for alias in v:
                    if runtime == alias:
                        return k
            raise Exception(f"Couldn't find the standard name for {runtime!s}")

        for k, v in self.runtimes.items():
            runtimes[get_standard_runtime(k)] = round(v, 3)

        return runtimes

    def get_resources_count(self, resources):
        """
        Get the standard resources count using the resources mapping and the total
        resources count from the various log files.
        """

        res_map = self.resources_map["families"][
            self.family
        ] if "families" in self.resources_map else self.resources_map

        resources_count = dict([(x, 0) for x in res_map])

        for res_type, res_names in res_map.items():
            for res_name in res_names:
                if isinstance(res_name, tuple):
                    res_name, multiplier = res_name
                else:
                    multiplier = 1

                if res_name in resources:
                    resources_count[res_type] += math.floor(
                        int(resources[res_name]) * multiplier
                    )

        for res_type, res_count in resources_count.items():
            resources_count[res_type] = str(res_count)

        return resources_count

    def get_metrics(self):
        # If an intermediate write, tolerate missing resource tally
        try:
            resources = self.resources()
            max_freq = self.max_freq()

            clocks_to_remove = list()
            clocks_to_rename = list()
            if self.clock_aliases is not None:
                for clk, clk_data in max_freq.items():
                    alias_found = False
                    for clk_name, clk_aliases in self.clock_aliases.items():
                        if clk in clk_aliases or clk == clk_name:
                            clocks_to_rename.append((clk, clk_name))
                            alias_found = True
                            break

                    if not alias_found:
                        clocks_to_remove.append(clk)

            for clk in clocks_to_remove:
                del max_freq[clk]

            for old_clk, new_clk in clocks_to_rename:
                max_freq[new_clk] = max_freq.pop(old_clk)

        except FileNotFoundError:
            if all:
                raise
            resources = dict()
            for source in ["synth", "impl"]:
                resources[source] = dict(
                    [
                        (x, None) for x in (
                            'LUT', 'DFF', 'BRAM', 'CARRY', 'GLB', 'PLL', 'IOB',
                            'DSP'
                        )
                    ]
                )

            max_freq = 0.0

        return max_freq, resources

    def write_metadata(self, output_error):
        synth_tool, pr_tool = {
            'vpr': ('yosys', 'vpr'),
            'vpr-fasm2bels': ('yosys', 'vpr'),
            'yosys-vivado': ('yosys', 'vivado'),
            'yosys-vivado-uhdm': ('yosys', 'vivado'),
            'vivado-already-synth': ('N/A', 'vivado'),
            'vivado': ('vivado', 'vivado'),
            'nextpnr-ice40': ('yosys', 'nextpnr'),
            'nextpnr-xilinx': ('yosys', 'nextpnr'),
            'nextpnr-nexus': ('yosys', 'nextpnr'),
            'nextpnr-fpga-interchange': ('yosys', 'nextpnr'),
            'nextpnr-fpga-interchange-already-synth': ('N/A', 'nextpnr'),
            'nextpnr-fpga-interchange-experimental-already-synth':
                ('N/A', 'nextpnr'),
            'nextpnr-xilinx-fasm2bels': ('yosys', 'nextpnr'),
            'quicklogic': ('yosys', 'vpr'),
            'lse-radiant': ('lse', 'radiant'),
            'synpro-radiant': ('synplify', 'radiant')
        }[self.toolchain]

        max_freq, resources = (None,
                               None) if output_error else self.get_metrics()

        # Meta information
        json_data = {
            'date': self.date.replace(microsecond=0).isoformat(),
            'status': "failed" if output_error else "succeeded",
            'error_msg': output_error,

            # Task information
            'design': self.design(),
            'family': self.family,
            'device': self.device,
            'package': self.package,
            'board': self.board,
            'vendor': self.vendor,
            'project': self.project_name,
            'toolchain':
                {
                    self.toolchain:
                        {
                            'synth_tool': synth_tool,
                            'pr_tool': pr_tool
                        }
                },

            # Detailed task information
            'optstr': self.optstr(),
            'pcf': os.path.basename(self.pcf) if self.pcf else None,
            'sdc': os.path.basename(self.sdc) if self.sdc else None,
            'xdc': os.path.basename(self.xdc) if self.xdc else None,
            'seed': self.seed,
            'build': self.build,
            'build_type': self.build_type,
            'strategy': self.strategy,
            'parameters': self.params_file or self.params_string,
            'sources': [x.replace(os.getcwd(), '.') for x in self.srcs],
            'top': self.top,
            'versions': self.versions(),
            'cmds': self.cmds,

            # Results
            'runtime': None if output_error else self.get_runtimes(),
            'max_freq': max_freq,
            'resources': resources,
            'wirelength': self.wirelength,
            'maximum_memory_use': self.maximum_memory_use,
        }

        with (Path(self.out_dir) / 'meta.json').open('w') as wfptr:
            json.dump(json_data, wfptr, sort_keys=True, indent=4)

        # Provide some context when comparing runtimes against systems
        check_call(
            """
uname -a >uname.txt
lscpu >lscpu.txt
            """,
            shell=True,
            executable='bash',
            cwd=self.out_dir
        )

    @staticmethod
    def seedable():
        return False

    @staticmethod
    def check_env():
        return {}
