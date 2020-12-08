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

from toolchains.toolchain import Toolchain
from utils.utils import Timed, have_exec


class Icestorm(Toolchain):
    def __init__(self, rootdir):
        Toolchain.__init__(self, rootdir)
        self.files = []
        self.edam = None
        self.backend = None

    def resources(self):
        return self.icebox_stat(
            self.backend, self.out_dir + "/" + self.project_name + ".stat"
        )

    def yosys_ver(self):
        # Yosys 0.7+352 (git sha1 baddb017, clang 3.8.1-24 -fPIC -Os)
        return subprocess.check_output(
            "yosys -V", shell=True, universal_newlines=True
        ).strip()

    def device_simple(self):
        # hx8k => 8k
        assert len(self.device) == 4
        return self.device[2:]

    def icebox_stat(self, backend, stat_file):

        backend.build_main("stats")
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
            return float(
                "{:03f}".format(self.icetime_parse(f)['max_freq'] / 1e6)
            )

    def run(self, pnr, args):
        with Timed(self, 'total'):
            os.makedirs(self.out_dir, exist_ok=True)
            for f in self.srcs:
                self.files.append(
                    {
                        'name': os.path.realpath(f),
                        'file_type': 'verilogSource'
                    }
                )

            if self.pcf is not None:
                self.files.append(
                    {
                        'name': os.path.realpath(self.pcf),
                        'file_type': 'PCF'
                    }
                )

            self.edam = {
                'files': self.files,
                'name': self.project_name,
                'toplevel': self.top,
                'tool_options':
                    {
                        'icestorm':
                            {
                                'nextpnr_options':
                                    args.split(),
                                'arachne_pnr_options':
                                    args.split(),
                                'pnr':
                                    pnr,
                                'part':
                                    self.device,
                                'environment_script':
                                    os.path.abspath('env.sh') + ' nextpnr'
                            }
                    }
            }

            self.backend = edalize.get_edatool('icestorm')(
                edam=self.edam, work_root=self.out_dir
            )
            self.backend.configure("")
            self.backend.build()
            self.backend.build_main('timing')


class NextpnrIcestorm(Icestorm):
    '''Nextpnr PnR + Yosys synthesis'''
    carries = (True, False)

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
    carries = (True, False)

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
