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
import time
import collections
import json
import re
import shutil
import sys
import glob
import datetime
import asciitable
import edalize
import glob

from toolchains.toolchain import Toolchain
from utils.utils import Timed, get_vivado_max_freq, have_exec


class Vivado(Toolchain):
    '''Vivado toolchain (synth and PnR)'''
    carries = (False, False)

    def __init__(self, rootdir):
        Toolchain.__init__(self, rootdir)
        self.toolchain = 'vivado'
        self.synthtool = 'vivado'
        self.synthoptions = []
        self.files = []
        self.edam = None
        self.backend = None

    def get_vivado_runtimes(self, logfile):
        def get_seconds(time_str):
            time = time_str.split(':')
            seconds = 3600 * int(time[0])
            seconds += 60 * int(time[1])
            seconds += int(time[2])
            return seconds

        log = dict()
        commands = list()
        with open(logfile, 'r') as fp:
            for l in fp:
                l = l.strip('\n')
                if l.startswith("Command"):
                    command = l.split()[1]
                    commands.append(command)
                if l.startswith(tuple(commands)):
                    cpu = False
                    elapsed = False
                    time_re = re.match(
                        ".*cpu = ([0-9:]+).*elapsed = ([0-9:]+)", str(l)
                    )
                    if time_re is not None:
                        l = l.split()
                        command = l[0].strip(':')
                        log[command] = get_seconds(time_re.groups()[1])
        return log

    def add_runtimes(self):
        runs_dir = self.out_dir + "/" + self.project_name + ".runs"
        synth_times = self.get_vivado_runtimes(runs_dir + '/synth_1/runme.log')
        impl_times = self.get_vivado_runtimes(runs_dir + '/impl_1/runme.log')
        for t in synth_times:
            self.add_runtime(t, synth_times[t])
        for t in impl_times:
            self.add_runtime(t, impl_times[t])

    def run(self):
        with Timed(self, 'total'):
            with Timed(self, 'prepare'):
                os.makedirs(self.out_dir, exist_ok=True)
                for f in self.srcs:
                    if f.endswith(".vhd") or f.endswith(".vhdl"):
                        self.files.append(
                            {
                                'name': os.path.realpath(f),
                                'file_type': 'vhdlSource'
                            }
                        )
                    elif f.endswith(".v"):
                        self.files.append(
                            {
                                'name': os.path.realpath(f),
                                'file_type': 'verilogSource'
                            }
                        )

                self.files.append(
                    {
                        'name': os.path.realpath(self.xdc),
                        'file_type': 'xdc'
                    }
                )

                chip = self.family + self.device + self.package

                vivado_settings = os.getenv('VIVADO_SETTINGS')

                vivado_options = {
                    'part': chip,
                    'synth': self.synthtool,
                    'vivado-settings': vivado_settings,
                    'yosys_synth_options': self.synthoptions,
                }

                self.edam = {
                    'files': self.files,
                    'name': self.project_name,
                    'toplevel': self.top,
                    'parameters':
                        {
                            'VIVADO':
                                {
                                    'paramtype': 'vlogdefine',
                                    'datatype': 'int',
                                    'default': 1,
                                },
                        },
                    'tool_options': {
                        'vivado': vivado_options
                    }
                }
                self.backend = edalize.get_edatool('vivado')(
                    edam=self.edam, work_root=self.out_dir
                )
                self.backend.configure("")

            self.backend.build()

        self.add_runtimes()
        self.add_maximum_memory_use()

    def add_maximum_memory_use(self):
        def get_usage(log_file, token="Memory ("):
            unit_list = ["B", "KB", "MB", "GB", "TB", "PB"]
            memory_usage = list()
            with open(log_file, 'r') as fp:
                for l in fp:
                    l = l.strip()
                    if token in l:
                        l_split = l.split()
                        memory_index = [
                            idx for idx, s in enumerate(l_split)
                            if "Memory" in s
                        ][0]
                        unit = l_split[memory_index + 1][1:-2]
                        max_rss = float(l_split[memory_index + 4])
                        # convert memory to MB
                        unit_index = unit_list.index(unit) - 2
                        if unit_index < 0:
                            max_rss = max_rss / (
                                1000 * (-unit_index)
                            )  # make unit index positive
                        elif unit_index > 0:
                            max_rss = max_rss * 1000 * unit_index

                        # convert MB to MiB
                        max_rss = max_rss * 0.95367431640625

                        memory_usage.append(max_rss)
            return memory_usage

        vivado_log = os.path.join(self.out_dir, 'vivado.log')

        self.maximum_memory_use = max(get_usage(vivado_log))

    @staticmethod
    def seedable():
        return False

    def check_env():
        return {
            'vivado': have_exec('vivado'),
        }

    def max_freq(self):
        report_file_pattern = self.out_dir + "/" + self.project_name + '.runs/impl_1/*_timing_summary_routed.rpt'
        report_file = glob.glob(report_file_pattern).pop()
        return get_vivado_max_freq(report_file)

    def vivado_resources(self, report_file):
        with open(report_file, 'r') as fp:
            report_data = fp.read()
            report_data = report_data.split('\n\n')
            report = dict()
            section = None
            for d in report_data:
                match = re.search(r'\n-+$', d)
                if match is not None:
                    match = re.search(r'\n?[0-9\.]+ (.*)', d)
                    if match is not None:
                        section = match.groups()[0]
                if d.startswith('+--'):
                    if section is not None:
                        # cleanup the table
                        d = re.sub(r'\+-.*-\+\n', '', d)
                        d = re.sub(r'\+-.*-\+$', '', d)
                        d = re.sub(r'^\|\s+', '', d, flags=re.M)
                        d = re.sub(r'\s\|\n', '\n', d)

                        report[section.lower()] = asciitable.read(
                            d,
                            delimiter='|',
                            guess=False,
                            comment=r'(\+.*)|(\*.*)',
                            numpy=False
                        )

        return report

    def resources(self, report_file=None):
        lut = 0
        dff = 0
        carry = 0
        iob = 0
        pll = 0
        bram = 0

        if report_file is None:
            report_file_pattern = self.out_dir + "/" + self.project_name + ".runs/impl_1/*_utilization_placed.rpt"
            report_file = glob.glob(report_file_pattern).pop()

        report = self.vivado_resources(report_file)

        for prim in report['primitives']:
            if prim[2] == 'Flop & Latch':
                dff += int(prim[1])
            if prim[2] == 'CarryLogic':
                carry += int(prim[1])
            if prim[2] == 'IO':
                if prim[0].startswith('OBUF') or prim[0].startswith('IBUF'):
                    iob += int(prim[1])
            if prim[2] == 'LUT':
                lut += int(prim[1])

        for prim in report['clocking']:
            if prim[0] == 'MMCME2_ADV' or prim[0] == 'PLLE2_ADV':
                pll += prim[1]

        for prim in report['memory']:
            if prim[0] == 'Block RAM Tile':
                # Vivado reports RAMB36. Multiply it by 2 to get RAMB18
                bram += prim[1] * 2

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

    def vivado_ver(self):
        return self.backend.get_version()

    def versions(self):
        return {"vivado": self.vivado_ver()}


class VivadoYosys(Vivado):
    '''Vivado PnR + Yosys synthesis'''
    carries = (False, False)

    def __init__(self, rootdir):
        Vivado.__init__(self, rootdir)
        self.synthtool = 'yosys'
        self.synthoptions = ['-iopad', '-arch xc7', '-flatten']
        self.toolchain = 'yosys-vivado'

    @staticmethod
    def check_env():
        return {
            'yosys': have_exec('yosys'),
            'vivado': have_exec('vivado'),
        }

    @staticmethod
    def yosys_ver():
        # Yosys 0.7+352 (git sha1 baddb017, clang 3.8.1-24 -fPIC -Os)
        return subprocess.check_output(
            "yosys -V", shell=True, universal_newlines=True
        ).strip()

    def get_yosys_runtimes(self, logfile):
        log = dict()
        commands = list()
        with open(logfile, 'r') as fp:
            for l in fp:
                time_re = re.match(".*CPU: user ([0-9]+\.[0-9]+)s", str(l))
                if time_re:
                    l = l.split()
                    log['synth'] = float(time_re.groups()[0])

                    return log

        assert False, "No run time found for yosys."

    def add_runtimes(self):

        synth_times = self.get_yosys_runtimes(
            os.path.join(self.out_dir, 'yosys.log')
        )

        runs_dir = os.path.join(self.out_dir, self.project_name + ".runs")
        impl_times = self.get_vivado_runtimes(runs_dir + '/impl_1/runme.log')
        total_runtime = 0
        for t in synth_times:
            self.add_runtime(t, synth_times[t])
            total_runtime += float(synth_times[t])
        for t in impl_times:
            self.add_runtime(t, impl_times[t])
            total_runtime += float(impl_times[t])
        self.add_runtime('total', total_runtime)

    def versions(self):
        return {'yosys': self.yosys_ver(), 'vivado': self.vivado_ver()}


class VivadoYosysUhdm(VivadoYosys):
    '''Vivado PnR + Yosys synthesis using uhdm frontend'''
    def __init__(self, rootdir):
        VivadoYosys.__init__(self, rootdir)
        self.synthtool = 'yosys'
        self.synthoptions = [
            '-iopad', '-arch xc7', '-flatten', 'frontend=surelog'
        ]
        self.toolchain = 'yosys-vivado-uhdm'
        uhdm_yosys_path = shutil.which("uhdm-yosys")
        # by default assume, uhdm-yosys is installed in symbiflow env
        if uhdm_yosys_path is None:
            print(
                "Could not find uhdm-yosys binary. Please execute 'source env.sh' or reinstall conda environments."
            )
            sys.exit(1)
        uhdm_yosys_path = os.path.dirname(uhdm_yosys_path)
