'''
Designs do not use constrianed I/O
Therefore they do not target a real dev board
Spit out JSON for easy result aggregation

Configurations of interest:
-yosys, icestorm
-yosys, vpr
-vendor, icecube
-yosys, icecube
-radiant?

Tested with one or two devices
-The largest device (8k)

Designs:
-SoC
-NES?
-LED blinky

Versions tested with
Radiant: 1.0 64-bit for Linux
Icecube: iCEcube2 2017-08 for Linux 
'''

import os
import subprocess
import time
import collections

class Toolchain:
    def __init__(self):
        self.yosys = 'yosys'
        self.timings = collections.OrderedDict()
        self.toolchain = None

        self.project_name = None
        self.srcs = None
        self.top = None
        self.out_dir = None

    def timed(self, name, dt):
        self.timings[name] = dt

    def perf(self):
        print('Timing (%s %s)' % (self.toolchain, self.project_name))
        for k, v in self.timings.items():
            print('  % -16s %0.3f' % (k + ':', v))

    def project(self, name, srcs, top, out_dir):
        self.project_name = name
        self.srcs = srcs
        self.top = top
        self.out_dir = out_dir

class Timed():
    def __init__(self, t, name):
        self.t = t
        self.name = name
        self.start = None

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, type, value, traceback):
        end = time.time()
        self.t.timed(self.name, end - self.start)

class Ice40(Toolchain):
    def __init__(self):
        Toolchain.__init__(self)
        self.yosys = 'yosys'
        self.toolchain = 'ice40'

    def run(self):
        '''
        icepack example.asc example.bin
        '''

        with Timed(self, 'nop'):
            subprocess.check_call("true", shell=True, cwd=self.out_dir)

        with Timed(self, 'all'):
            with Timed(self, 'yosys'):
                srcs_str = ' '.join(self.srcs)
                script = "synth_ice40 -top %s -blif my.blif" % self.top 
                subprocess.check_call("%s -p '%s' %s" % (self.yosys, script, srcs_str), shell=True, cwd=self.out_dir)
        
            with Timed(self, 'arachne-pnr'):
                subprocess.check_call("arachne-pnr -d 8k -P cm81 -o my.asc my.blif", shell=True, cwd=self.out_dir)
    
            with Timed(self, 'icepack'):
                subprocess.check_call("icepack my.asc my.bin", shell=True, cwd=self.out_dir)

        self.perf()

def run_vpr(srcs, top, out_dir):
    pass

def run(toolchain, project, out_dir):
    t = Ice40()

    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    cwd = os.getcwd()

    if 1:
        srcs = [cwd + '/src/blinky.v']
        top = 'top'
        name = 'blinky'

    t.project(name, srcs, top, out_dir)

    t.run()

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=
        'Analyze tool runtimes'
    )

    parser.add_argument('--verbose', action='store_true', help='')
    parser.add_argument('--overwrite', action='store_true', help='')
    parser.add_argument('--family', default='ice40', help='Device family')
    parser.add_argument('--device', default='hx8k', help='Device')
    parser.add_argument('--toolchain', required=True, help='Tools to use')
    parser.add_argument('--project', required=True, help='Source code to run on')
    parser.add_argument('out_dir', help='Output directory')
    args = parser.parse_args()

    run(args.toolchain, args.project, args.out_dir)

if __name__ == '__main__':
    main()
