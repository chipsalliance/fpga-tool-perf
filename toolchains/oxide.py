import os
import re
import subprocess
import edalize

from utils.utils import Timed, have_exec
from toolchains.symbiflow import NextpnrGeneric

class Oxide(NextpnrGeneric):

    def __init__(self,rootdir):
        NextpnrGeneric.__init__(self, rootdir)
        self.files = []

    def resources(self):
        '''resources map for nexus arch'''
        res_map_nexus = {
                'LUT':   ('OXIDE_COMB'),
                'FF':    ('OXIDE_FF'),
                'CARRY': ('CCU2'),
                'IOB':   ('SEIO33_CORE'),
                'PLL':   ('PLL_CORE'),
                'BRAM':  ('OXIDE_EBR'),
                'LRAM':  ('LRAM_CORE'),
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

    def max_freq(self):
        return NextpnrGeneric.max_freq(self)

    def yosys_ver(self):
        return subprocess.check_output(
            "yosys -V", shell=True, universal_newlines=True
        ).strip()

    def run(self, pnr, args):
        with Timed(self, 'total'):
            with Timed(self, 'prepare'):
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
                self.edam = {
                    'files': self.files,
                    'name': self.project_name,
                    'toplevel': self.top,
                    'tool_options':
                        {
                            'oxide':
                                {
                                    'nextpnr_options': args.split(),
                                    'arachne_pnr_options': args.split(),
                                    'pnr': pnr,
                                    'part': self.device,
                                    'environment_script': os.path.abspath('env.sh') + ' nextpnr'
                                }
                        }
                }
                self.backend = edalize.get_edatool('oxide')(edam=self.edam, work_root=self.out_dir)
                self.backend.configure("")
            with Timed(self, 'bitstream'):
                self.backend.build_main(self.project_name + '.bit')
            with Timed(self, 'fasm'):
                self.backend.build_main(self.project_name + '.fasm')


class NextpnrOxide(Oxide):
    carries = (True, False)

    '''Nextpnr PnR + Yosys synthesis'''
    def __init__(self, rootdir):
        Oxide.__init__(self, rootdir)
        self.toolchain = "nextpnr-nexus"

    def run(self):
        args = ''
        args += " --device " + self.device
        args += " --timing-allow-fail "

        if self.seed:
            args += " --seed %u" % (self.seed, )
        super(NextpnrOxide, self).run('next', args)

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
