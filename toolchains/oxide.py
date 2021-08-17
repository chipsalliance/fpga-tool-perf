import os
import edalize
from utils.utils import have_exec
from toolchains.toolchain import Toolchain

class Oxide(Toolchain):

    def __init__(self,rootdir):
        Toolchain.__init__(self, rootdir)
        self.files = []

    def max_freq(self):
        pass

    def run(self, pnr, args):
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
        self.backend.build()
        #self.backend.build_main('timing')


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
