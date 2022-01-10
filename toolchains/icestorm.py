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
import re
import edalize

from toolchains.toolchain import Toolchain
from utils.utils import Timed, have_exec, get_yosys_resources, get_file_dict

YOSYS_REGEXP = re.compile("(Yosys [a-z0-9+.]+) (\(git sha1) ([a-z0-9]+),.*")


class Icestorm(Toolchain):
    def __init__(self, rootdir):
        Toolchain.__init__(self, rootdir)
        self.files = []
        self.edam = None
        self.backend = None

        self.resources_map = {
            'LUT': (
                'LUT',
                'SB_LUT4',
            ),
            'DFF':
                (
                    'DFF',
                    'SB_DFF',
                    'SB_DFFE',
                    'SB_DFFESR',
                    'SB_DFFESS',
                    'SB_DFFN',
                    'SB_DFFSR',
                    'SB_DFFSS',
                ),
            'CARRY': (
                'CARRY',
                'SB_CARRY',
            ),
            'IOB': ('IOB', ),
            'PLL': ('PLL', ),
            'BRAM': ('BRAM', ),
        }

    def prepare_edam(self, pnr, args):
        options = dict(
            nextpnr_options=args.split(),
            arachne_pnr_options=args.split(),
            pnr=pnr,
            part=self.device
        )

        edam = dict()
        edam['files'] = self.files
        edam['name'] = self.project_name
        edam['toplevel'] = self.top
        edam['tool_options'] = dict(icestorm=options)

        return edam

    def run(self, pnr, args):
        with Timed(self, 'total'):
            os.makedirs(self.out_dir, exist_ok=True)

            self.env_script = os.path.abspath('env.sh') + ' nextpnr'
            os.environ["EDALIZE_LAUNCHER"] = f"source {self.env_script} &&"

            edam = self.prepare_edam(pnr, args)
            self.backend = edalize.get_edatool('icestorm')(
                edam=edam, work_root=self.out_dir
            )
            self.backend.configure("")
            self.backend.build()
            self.backend.build_main('timing')
        del os.environ["EDALIZE_LAUNCHER"]

    def icebox_stat(self, backend, stat_file):
        os.environ["EDALIZE_LAUNCHER"] = f"source {self.env_script} &&"

        backend.build_main("stats")
        del os.environ["EDALIZE_LAUNCHER"]
        '''
        DFFs:     22
        LUTs:     24
        CARRYs:   20
        BRAMs:     0
        IOBs:      4
        PLLs:      0
        GLBs:      1
        '''
        ret = {}
        with open(stat_file) as f:
            for l in f:
                # DFFs:     22
                m = re.match(r'(.*)s: *([0-9]*)', l)
                t = m.group(1)
                n = int(m.group(2))
                ret[t] = n
        assert 'LUT' in ret
        return ret

    def resources(self):
        synth_resources = get_yosys_resources(
            os.path.join(os.path.join(self.out_dir, "yosys.log"))
        )
        synth_resources = self.get_resources_count(synth_resources)

        impl_resources = self.icebox_stat(
            self.backend,
            os.path.join(self.out_dir, f"{self.project_name}.stat")
        )
        impl_resources = self.get_resources_count(impl_resources)

        return {"synth": synth_resources, "impl": impl_resources}

    def icetime_parse(self, f):
        ret = {}
        for l in f:
            # Total path delay: 8.05 ns (124.28 MHz)
            m = re.match(r'Total path delay: .*s \((.*) (.*)\)', l)
            if m:
                assert m.group(2) == 'MHz'
                ret['max_freq'] = float(m.group(1)) * 1e6
        return ret

    def max_freq(self):
        with open(self.out_dir + '/' + self.project_name + '.tim') as f:
            max_freq = float(
                "{:03f}".format(self.icetime_parse(f)['max_freq'] / 1e6)
            )

            clk_data = dict()
            clk_data["actual"] = max_freq
            clk_data["hold_violation"] = 0.0
            clk_data["met"] = True
            clk_data["requested"] = 0.0
            clk_data["setup_violation"] = 0.0

            return {"clk": clk_data}

    @staticmethod
    def yosys_ver():
        # Yosys 0.7+352 (git sha1 baddb017, clang 3.8.1-24 -fPIC -Os)
        yosys_version = subprocess.check_output(
            "yosys -V", shell=True, universal_newlines=True
        ).strip()

        m = YOSYS_REGEXP.match(yosys_version)

        assert m

        return "{} {} {})".format(m.group(1), m.group(2), m.group(3))

    def device_simple(self):
        # hx8k => 8k
        assert len(self.device) == 4
        return self.device[2:]


class NextpnrIcestorm(Icestorm):
    '''Nextpnr PnR + Yosys synthesis'''
    def __init__(self, rootdir):
        Icestorm.__init__(self, rootdir)
        self.toolchain = "nextpnr-ice40"

    def run(self):
        args = ''
        args += " --" + self.device
        args += " --package " + self.package
        args += " --timing-allow-fail "
        if self.seed:
            args += " --seed %u" % (self.seed, )

        if self.pcf is None:
            args += ' --pcf-allow-unconstrained'
        super(NextpnrIcestorm, self).run('next', args)

    @staticmethod
    def nextpnr_version():
        '''
        nextpnr-ice40  -V
        '''
        return subprocess.check_output(
            "nextpnr-ice40 -V || true",
            shell=True,
            universal_newlines=True,
            stderr=subprocess.STDOUT
        ).strip()

    def versions(self):
        return {
            'yosys': self.yosys_ver(),
            'nextpnr-ice40': self.nextpnr_version(),
        }

    @staticmethod
    def seedable():
        return True

    @staticmethod
    def check_env():
        return {
            'yosys': have_exec('yosys'),
            'nextpnr-ice40': have_exec('nextpnr-ice40'),
            'icepack': have_exec('icepack'),
            'icetime': have_exec('icetime'),
        }


class Arachne(Icestorm):
    '''Arachne PnR + Yosys synthesis'''
    def __init__(self, rootdir):
        Icestorm.__init__(self, rootdir)
        self.toolchain = 'arachne'

    def run(self):

        args = ''
        args += "-d " + self.device_simple()
        args += " -P " + self.package
        if self.seed:
            args += ' --seed %d' % self.seed

        super(Arachne, self).run('arachne', args)

    @staticmethod
    def arachne_version():
        '''
        $ arachne-pnr -v
        arachne-pnr 0.1+203+0 (git sha1 7e135ed, g++ 4.8.4-2ubuntu1~14.04.3 -O2)
        '''
        return subprocess.check_output(
            "arachne-pnr -v", shell=True, universal_newlines=True
        ).strip()

    def versions(self):
        return {
            'yosys': self.yosys_ver(),
            'arachne': self.arachne_version(),
        }

    @staticmethod
    def seedable():
        return True

    @staticmethod
    def check_env():
        return {
            'yosys': have_exec('yosys'),
            'arachne-pnr': have_exec('arachne-pnr'),
            'icepack': have_exec('icepack'),
            'icetime': have_exec('icetime'),
        }
