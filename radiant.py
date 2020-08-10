import os

from toolchain import Toolchain
from utils import Timed


# .asc version field just says "DiamondNG"
# guess that was the code name...
# no seed support? -n just does more passes
class Radiant(Toolchain):
    '''Lattice Radiant based toolchains'''
    carries = None
    # FIXME: strategy isn't being set correctly
    # https://github.com/SymbiFlow/fpga-tool-perf/issues/14
    strategies = ('Timing', 'Quick', 'Area')

    RADIANTDIR_DEFAULT = os.getenv("RADIANTDIR", "/opt/lscc/radiant/1.0")

    def __init__(self):
        Toolchain.__init__(self)
        self.radiantdir = Radiant.RADIANTDIR_DEFAULT

    def run(self):
        # acceptable for either device
        assert (self.device, self.package) in [
            ('up3k', 'uwg30'), ('up5k', 'uwg30'), ('up5k', 'sg48')
        ]

        with Timed(self, 'bit-all'):
            env = os.environ.copy()
            env["SRCS"] = ' '.join(self.srcs)
            env["TOP"] = self.top
            env["RADIANTDIR"] = self.radiantdir
            env["RADDEV"] = self.device + '-' + self.package
            syn = self.syn()
            args = "--syn %s" % (syn, )
            if self.strategy:
                args += " --strategy %s" % self.strategy
            self.cmd(root_dir + "/radiant.sh", args, env=env)

            self.cmd("iceunpack", "my.bin my.asc")

        self.cmd("icetime", "-tmd up5k my.asc")

    def max_freq(self):
        with open(self.out_dir + '/icetime.txt') as f:
            return icetime_parse(f)['max_freq']

    def resources(self):
        return icebox_stat("my.asc", self.out_dir)

    def radiant_ver(self):
        # a lot of places where this is, but not sure whats authoritative
        for l in open(self.radiantdir + '/data/ispsys.ini'):
            # ./data/ispsys.ini:19:ProductType=1.0.0.350.6
            if l.find('ProductType') == 0:
                return l.split('=')[1].strip()
        assert 0

    def versions(self):
        return {
            'yosys': yosys_ver(),
            'radiant': self.radiant_ver(),
        }

    @staticmethod
    def check_env():
        return {
            'RADIANTDIR': os.path.exists(Radiant.RADIANTDIR_DEFAULT),
            'iceunpack': have_exec('iceunpack'),
            'icetime': have_exec('icetime'),
        }


class RadiantLSE(Radiant):
    '''Lattice Radiant using LSE for synthesis'''
    carries = (True, )

    def __init__(self):
        Radiant.__init__(self)
        self.toolchain = 'lse-radiant'

    def syn(self):
        return "lse"


class RadiantSynpro(Radiant):
    '''Lattice Radiant using Synplify for synthesis'''
    carries = (True, )

    def __init__(self):
        Radiant.__init__(self)
        self.toolchain = 'synpro-radiant'

    def syn(self):
        return "synplify"


# @E: CG389 :"/home/mcmaster/.../impl/impl.v":18:4:18:7|Reference to undefined module SB_LUT4
# didn't look into importing edif
class RadiantYosys(Radiant):
    carries = (True, False)

    def __init__(self):
        Radiant.__init__(self)
        self.toolchain = 'yosys-radiant'

    def syn(self):
        return "yosys-synpro"
