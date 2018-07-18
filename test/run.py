#!/usr/bin/env python3

import sys
import os
sys.path.append(os.getcwd() + "/..")
import unittest
import fpgaperf

class TestCase(unittest.TestCase):
    def test_icetime_parse(self):
        ''''''
        fpgaperf.icetime_parse

    def test_yosys_ver(self):
        fpgaperf.yosys_ver

    def test_toolchains(self):
        '''Try each toolchain'''
        #for toolchain in ['arachne']:
        for toolchain in fpgaperf.toolchains.keys():
            if 'radiant' in toolchain:
                device = 'up5k'
                package = 'uwg30'
            else:
                device = 'lp8k'
                package = 'cm81'
            fpgaperf.run(family='ice40', device=device, package=package, toolchain=toolchain, project=fpgaperf.get_project('oneblink'), verbose=True)

    def test_pcf(self):
        '''Try each toolchain with a pcf'''

    def test_seed(self):
        '''Try seeding, where possible'''

if __name__ == '__main__':
    unittest.main()
