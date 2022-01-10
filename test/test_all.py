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

import sys
import os

sys.path.append(os.getcwd() + "/..")
import unittest
import fpgaperf
import re
import random


def def_devpack(toolchain):
    if 'radiant' in toolchain:
        device = 'up5k'
        package = 'uwg30'
    else:
        # tinyfpga b2
        # XXX: change to hx8k, ct256?
        device = 'lp8k'
        package = 'cm81'
    return device, package


class TestCase(unittest.TestCase):
    def setUp(self):
        self.verbose = False

    def test_env_ready(self):
        assert fpgaperf.env_ready()

    def test_icetime_parse(self):
        with open('icetime.txt', 'r') as f:
            m = fpgaperf.icetime_parse(f)
        assert 'max_freq' in m
        assert abs(m['max_freq'] - 132.94e6) < 1.0

    def test_yosys_ver(self):
        v = fpgaperf.yosys_ver()
        assert re.match(r'Yosys .* .*git sha1 .*', v)

    def test_get_toolchains(self):
        ts = fpgaperf.get_toolchains()
        assert 'vpr' in ts
        assert 'arachne' in ts
        assert 'radiant-synpro' in ts

    def test_get_projects(self):
        ps = fpgaperf.get_projects()
        assert 'oneblink' in ps
        assert 'picosoc-hx8kdemo' in ps
        assert 'picorv32-wrap' in ps

    def test_get_seedable(self):
        ts = fpgaperf.get_seedable()
        assert 'vpr' in ts
        assert 'arachne' in ts
        assert 'nextpnr' in ts

    def test_toolchains(self):
        '''Try each toolchain'''
        for toolchain in fpgaperf.toolchains.keys():
            device, package = def_devpack(toolchain)
            fpgaperf.run(
                family='ice40',
                device=device,
                package=package,
                toolchain=toolchain,
                project=fpgaperf.get_project('oneblink'),
                verbose=self.verbose
            )

    def test_pcf(self):
        '''Try each toolchain with a pcf'''
        for toolchain in fpgaperf.toolchains.keys():
            device, package = def_devpack(toolchain)
            if 'radiant' in toolchain:
                pcf = fpgaperf.root_dir + '/project/FIXME.pcf'
            else:
                pcf = fpgaperf.root_dir + '/project/oneblink_lp8k-cm81.pcf'
            fpgaperf.run(
                family='ice40',
                device=device,
                package=package,
                toolchain=toolchain,
                project=fpgaperf.get_project('oneblink'),
                pcf=pcf,
                verbose=self.verbose
            )

    def test_seed(self):
        '''Try seeding, where possible'''
        random.seed(1234)
        for toolchain in fpgaperf.get_seedable():
            seed = random.randint(1, 0x7FFFFFFF)
            device, package = def_devpack(toolchain)
            fpgaperf.run(
                family='ice40',
                device=device,
                package=package,
                toolchain=toolchain,
                project=fpgaperf.get_project('oneblink'),
                seed=seed,
                verbose=self.verbose
            )


if __name__ == '__main__':
    unittest.main()
