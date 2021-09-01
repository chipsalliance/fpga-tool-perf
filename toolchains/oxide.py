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
from utils.utils import Timed, have_exec
from toolchains.symbiflow import NextpnrGeneric

YOSYS_REGEXP = re.compile("(Yosys [a-z0-9+.]+) (\(git sha1) ([a-z0-9]+),.*")


class NextpnrOxide(NextpnrGeneric):
    '''Nextpnr PnR + Yosys synthesis'''
    def __init__(self, rootdir):
        NextpnrGeneric.__init__(self, rootdir)
        self.toolchain = "nextpnr-nexus"
        self.carries = (True, False)
        self.nextpnr_log = "next.log"

    def resources(self):
        '''resources map for nexus arch'''
        res_map_nexus = {
            'LUT': ('OXIDE_COMB'),
            'FF': ('OXIDE_FF'),
            'CARRY': ('CCU2'),
            'IOB': ('SEIO33_CORE'),
            'PLL': ('PLL_CORE'),
            'BRAM': ('OXIDE_EBR'),
            'LRAM': ('LRAM_CORE'),
        }
        resources_count = {
            "LUT": 0,
            "FF": 0,
            "BRAM": 0,
            "LRAM": 0,
            "CARRY": 0,
            "PLL": 0,
            "IOB": 0,
        }
        res = self.get_resources()
        for res_type, res_name in res_map_nexus.items():
            if res_name in res:
                resources_count[res_type] += res[res_name]

        return resources_count

    def prepare_edam(self):
        os.makedirs(self.out_dir, exist_ok=True)
        for f in self.srcs:
            self.files.append(
                {
                    'name': os.path.realpath(f),
                    'file_type': 'verilogSource'
                }
            )
        if self.pdc is not None:
            self.files.append(
                {
                    'name': os.path.realpath(self.pdc),
                    'file_type': 'PDC'
                }
            )

        args = f"--device {self.device} "
        args += "--timing-allow-fail "
        if self.seed:
            args += " --seed %u" % (self.seed, )

        edam = {
            'files': self.files,
            'name': self.project_name,
            'toplevel': self.top,
            'tool_options': {
                'oxide': {
                    'nextpnr_options': args.split(),
                }
            }
        }

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
    def yosys_ver():
        # Yosys 0.7+352 (git sha1 baddb017, clang 3.8.1-24 -fPIC -Os)
        yosys_version = subprocess.check_output(
            "yosys -V", shell=True, universal_newlines=True
        ).strip()

        m = YOSYS_REGEXP.match(yosys_version)

        assert m

        return "{} {} {})".format(m.group(1), m.group(2), m.group(3))

    @staticmethod
    def nextpnr_version():
        '''
        nextpnr-nexus -V
        '''
        return subprocess.check_output(
            "nextpnr-nexus -V || true",
            shell=True,
            universal_newlines=True,
            stderr=subprocess.STDOUT
        ).strip()

    def versions(self):
        return {
            'yosys': self.yosys_ver(),
            'nextpnr-nexus': self.nextpnr_version(),
        }

    @staticmethod
    def seedable():
        return True

    @staticmethod
    def check_env():
        return {
            'yosys': have_exec('yosys'),
            'nextpnr-nexus': have_exec('nextpnr-nexus'),
        }
