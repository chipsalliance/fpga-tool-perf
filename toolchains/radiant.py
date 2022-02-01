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
import edalize
import re
import subprocess

from toolchains.toolchain import Toolchain
from utils.utils import Timed, have_exec


class Radiant(Toolchain):
    '''Lattice Radiant based toolchains'''

    strategies = ('Timing', 'Area')

    def __init__(self, rootdir):
        Toolchain.__init__(self, rootdir)
        self.radiantdir = os.getenv(
            "RADIANT",
            os.path.expanduser("~") + "/lscc/radiant/3.0"
        )
        self.files = []
        self.edam = None
        self.backend = None
        self.resources_map = {
            'LUT':
                (
                    'LUT', 'LUTS', 'LUT1', 'LUT2', 'LUT3', 'LUT4', 'LUT5',
                    'LUT6'
                ),
            'DFF': ('DFF', 'SB_DFF'),
            'CARRY': ('CARRY', 'SB_CARRY'),
            'IOB': ('SEIO33', 'IOB'),
            'PLL': ('PLL'),
            'BRAM': ('BRAM', 'LRAM', 'EBR'),
            'DSP': ('PREADD9', 'MULT9', 'MULT18', 'MULT18X36', 'MULT36'),
            'GLB': ('GLB'),
        }

    def prepare_edam(self):
        os.makedirs(self.out_dir, exist_ok=True)

        part = f'{self.device}-{self.package}'.upper()
        if self.family == "ice40":
            part = "iCE40" + part

        radiant_options = {
            'part': part,
            'synth': self.synth_tool(),
            'strategy': self.strategy
        }
        edam = {
            'files': self.files,
            'name': self.project_name,
            'toplevel': self.top,
            'parameters':
                {
                    'RADIANT':
                        {
                            'paramtype': 'vlogdefine',
                            'datatype': 'int',
                            'default': 1,
                        },
                },
            'tool_options': {
                'radiant': radiant_options
            }
        }
        return edam

    def run(self):
        with Timed(self, 'total'):
            with Timed(self, 'prepare'):
                self.edam = self.prepare_edam()
                self.backend = edalize.get_edatool('radiant')(
                    edam=self.edam, work_root=self.out_dir
                )
                self.backend.configure("")
                self.backend.build()
            self.add_maximum_memory_use()

    def add_maximum_memory_use(self):
        log_file = os.path.join(
            self.out_dir, "impl", self.project_name + "_impl.par"
        )
        with open(log_file, 'r') as file:
            for line in file:
                line = line.strip()
                if "Peak Memory Usage:" in line:
                    self.maximum_memory_use = line.split()[3]
                    return

    def radiant_ver(self):
        for l in open(os.path.join(self.radiantdir, 'data', 'ispsys.ini')):
            if l.find('ProductType') == 0:
                return l.split('=')[1].strip()

    def check_env():
        return {
            'Radiant': have_exec('radiantc'),
        }

    @staticmethod
    def seedable():
        return False

    def resources(self):
        res_file = os.path.join(
            self.out_dir, "impl", self.project_name + "_impl.par"
        )
        resources = dict()
        with open(res_file, "r") as file:
            processing = False
            for line in file:
                line = line.strip()
                if "Device utilization" in line:
                    processing = True
                    next(file)
                    continue
                if not processing:
                    continue
                else:
                    if len(line) == 0:
                        break
                    res = line.split()
                    if len(res) == 3:
                        continue
                    res_type = res[0]
                    regex = "(\d+)"
                    match = re.search(regex, line)
                    assert match
                    res_count = int(match.groups()[0])
                    resources[res_type] = res_count

        resources = self.get_resources_count(resources)
        return {"synth": resources, "impl": resources}

    def max_freq(self):
        freqs = dict()
        res_name = None

        freq_file_exts = ["twr", "tws"]

        path = ""
        for ext in freq_file_exts:
            temp_path = os.path.join(
                self.out_dir, "impl", self.project_name + "_impl." + ext
            )

            if os.path.isfile(temp_path):
                path = temp_path
                break

        assert path, "Path to the timing report file is empty"

        with open(path, "r") as file:
            for line in file:
                line = line.strip()
                if "From" in line:
                    res = line.split()
                    res_name = res[1]
                    freqs[res_name] = dict()
                    freqs[res_name]['requested'] = float(res[8])
                    line = next(file)
                    res = line.split()
                    freqs[res_name]['actual'] = float(res[8])
                    freqs[res_name]['met'] = freqs[res_name]['actual'] > freqs[
                        res_name]['requested']
                if "Total N" in line:
                    match = re.match(
                        "^Total.* *.(\d+\.\d+).* *.(\d+\.\d+).*", line
                    )
                    if match and res_name is not None:
                        setup_viol = float(match.groups()[0])
                        hold_viol = float(match.groups()[1])
                        freqs[res_name]['setup_violation'] = setup_viol
                        freqs[res_name]['hold_violation'] = hold_viol

        return freqs


class RadiantLSE(Radiant):
    '''Lattice Radiant using LSE for synthesis'''
    def __init__(self, rootdir):
        Radiant.__init__(self, rootdir)
        self.toolchain = 'lse-radiant'
        self.synthtool = 'lse'

    def synth_tool(self):
        return self.synthtool

    def versions(self):
        return {'Radiant': self.radiant_ver()}


class RadiantSynpro(Radiant):
    '''Lattice Radiant using Synplify for synthesis'''
    def __init__(self, rootdir):
        Radiant.__init__(self, rootdir)
        self.toolchain = 'synpro-radiant'
        self.synthtool = 'synplify'

    def versions(self):
        return {'Radiant': self.radiant_ver()}

    def synth_tool(self):
        return self.synthtool
