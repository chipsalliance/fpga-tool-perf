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
from utils.utils import Timed, get_vivado_max_freq, have_exec, get_yosys_resources, get_file_dict


class Vivado(Toolchain):
    '''Vivado toolchain (synth and PnR)'''
    def __init__(self, rootdir):
        Toolchain.__init__(self, rootdir)
        self.toolchain = 'vivado'
        self.synthtool = 'vivado'
        self.synthoptions = []
        self.files = []
        self.edam = None
        self.backend = None

        self.resources_map = dict(families=dict())
        self.resources_map["families"]["xc7"] = {
            'LUT': (
                'LUT1',
                'LUT2',
                'LUT3',
                'LUT4',
                'LUT5',
                'LUT6',
            ),
            'DFF': (
                'FDRE',
                'FDSE',
                'FDPE',
                "FDCE",
            ),
            'CARRY': ('CARRY4', ),
            'IOB':
                (
                    'IBUF',
                    'OBUF',
                    'OBUFT',
                    'IOBUF',
                    'OBUFTDS',
                    'OBUFDS',
                    ('IOBUF', 2),
                    ('IOBUFDS', 2),
                ),
            'PLL': ('MMCME2_ADV', 'PLLE2_ADV'),
            'BRAM': (
                'RAMB18E1',
                ('RAMB36E1', 2),
            ),
            'DSP': ('DSP48E1', ),
        }

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

    def prepare_edam(self):
        chip = self.family + self.device + self.package

        vivado_settings = os.getenv('VIVADO_SETTINGS')

        options = dict()
        options['part'] = chip
        options['synth'] = self.synthtool
        options['vivado-settings'] = vivado_settings
        options['yosys_synth_options'] = self.synthoptions

        params = dict(paramtype='vlogdefine', datatype='int', default=1)

        edam = dict()
        edam['files'] = self.files
        edam['name'] = self.project_name
        edam['toplevel'] = self.top
        edam['tool_options'] = dict(vivado=options)
        edam['parameters'] = dict(VIVADO=params)

        return edam

    def run(self):
        with Timed(self, 'total'):
            with Timed(self, 'prepare'):
                os.makedirs(self.out_dir, exist_ok=True)

                edam = self.prepare_edam()
                self.backend = edalize.get_edatool('vivado')(
                    edam=edam, work_root=self.out_dir
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

        prims = report["primitives"]
        zip_it = zip(prims["Ref Name"], prims["Used"])

        return dict(zip_it)

    def resources(self, report_file=None):
        def get_report_file(step, suffix):
            return os.path.join(
                self.out_dir, f"{self.project_name}.runs", f"{step}_1",
                f"{self.top}_utilization_{suffix}.rpt"
            )

        synth_resources = self.vivado_resources(
            get_report_file("synth", "synth")
        )
        synth_resources = self.get_resources_count(synth_resources)

        impl_resources = self.vivado_resources(
            get_report_file("impl", "placed")
        )
        impl_resources = self.get_resources_count(impl_resources)

        return {"synth": synth_resources, "impl": impl_resources}

    def vivado_ver(self):
        cmd = "source $(find -L /opt -wholename \"*Xilinx/Vivado/*/settings64.sh\" 2>/dev/null | sort | head -n 1);"
        cmd += "which vivado"
        output = subprocess.check_output(
            cmd, shell=True, universal_newlines=True, executable="/bin/bash"
        ).strip()

        version_re = re.compile(".*/Vivado/([0-9]+\.[0-9]+)/.*")
        match = version_re.match(output)

        if match:
            return match.group(1)

    def versions(self):
        return {"vivado": self.vivado_ver()}


class VivadoYosys(Vivado):
    '''Vivado PnR + Yosys synthesis'''
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

    def resources(self):
        def get_report_file(step, suffix):
            return os.path.join(
                self.out_dir, f"{self.project_name}.runs", f"{step}_1",
                f"{self.project_name}_utilization_{suffix}.rpt"
            )

        synth_resources = get_yosys_resources(
            os.path.join(self.out_dir, "yosys.log")
        )
        synth_resources = self.get_resources_count(synth_resources)

        impl_resources = self.vivado_resources(
            get_report_file("impl", "placed")
        )
        impl_resources = self.get_resources_count(impl_resources)

        return {"synth": synth_resources, "impl": impl_resources}

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
