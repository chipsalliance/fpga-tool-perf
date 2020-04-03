import os

from toolchain import Toolchain
from utils import Timed

# no seed support?
class Icecube2(Toolchain):
    '''Lattice Icecube2 based toolchains'''
    carries = None

    ICECUBEDIR_DEFAULT = os.getenv("ICECUBEDIR", "/opt/lscc/iCEcube2.2017.08")

    def __init__(self):
        Toolchain.__init__(self)
        self.icecubedir = self.ICECUBEDIR_DEFAULT

    def run(self):
        with Timed(self, 'bit-all'):
            print('top: %s' % self.top)
            env = os.environ.copy()
            env["SRCS"] = ' '.join(self.srcs)
            env["TOP"] = self.top
            env["ICECUBEDIR"] = self.icecubedir
            #env["ICEDEV"] = 'hx8k-ct256'
            env["ICEDEV"] = self.device + '-' + self.package
            args = "--syn %s" % (self.syn(), )
            if self.strategy:
                args += " --strategy %s" % (self.strategy, )
            self.cmd(root_dir + "/icecubed.sh", args, env=env)

            self.cmd("iceunpack", "my.bin my.asc")

        self.cmd("icetime", "-tmd %s my.asc" % (self.device, ))

    def max_freq(self):
        with open(self.out_dir + '/icetime.txt') as f:
            return icetime_parse(f)['max_freq']

    def resources(self):
        return icebox_stat("my.asc", self.out_dir)

    @staticmethod
    def asc_ver(f):
        '''
        .comment
        Lattice
        iCEcube2 2017.08.27940
        Part: iCE40HX1K-TQ144
        Date: Jun 27 2018 13:22:06
        '''
        for l in f:
            if l.find('iCEcube2') == 0:
                return l.split()[1].strip()
        assert 0

    def versions(self):
        # FIXME: see if can get from tool
        asc_ver = None
        try:
            with open(self.out_dir + '/my.asc') as ascf:
                asc_ver = Icecube2.asc_ver(ascf)
        except FileNotFoundError:
            pass

        return {
            'yosys': yosys_ver(),
            'icecube2': asc_ver,
        }


class Icecube2Synpro(Icecube2):
    '''Lattice Icecube2 using Synplify for synthesis'''
    carries = (True, )

    def __init__(self):
        Icecube2.__init__(self)
        self.toolchain = 'icecube2-synpro'

    def syn(self):
        return "synpro"

    @staticmethod
    def check_env():
        return {
            'ICECUBEDIR': os.path.exists(Icecube2.ICECUBEDIR_DEFAULT),
            'icetime': have_exec('icetime'),
        }


class Icecube2LSE(Icecube2):
    '''Lattice Icecube2 using LSE for synthesis'''
    carries = (True, )

    def __init__(self):
        Icecube2.__init__(self)
        self.toolchain = 'icecube2-lse'

    def syn(self):
        return "lse"

    @staticmethod
    def check_env():
        return {
            'ICECUBEDIR': os.path.exists(Icecube2.ICECUBEDIR_DEFAULT),
            'icetime': have_exec('icetime'),
        }


class Icecube2Yosys(Icecube2):
    '''Lattice Icecube2 using Yosys for synthesis'''
    carries = (True, False)

    def __init__(self):
        Icecube2.__init__(self)
        self.toolchain = 'icecube2-yosys'

    def syn(self):
        return "yosys-synpro"

    @staticmethod
    def check_env():
        return {
            'yosys': have_exec('yosys'),
            'ICECUBEDIR': os.path.exists(Icecube2.ICECUBEDIR_DEFAULT),
            'icetime': have_exec('icetime'),
        }


