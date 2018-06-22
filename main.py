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

class Timed():
    def __init__(self, t, name):
        self.t = t
        self.name = name
        self.start = None

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, type, value, traceback):
        end = time.time()
        self.t.add_runtime(self.name, end - self.start)

class Toolchain:
    def __init__(self):
        self.runtimes = collections.OrderedDict()
        self.toolchain = None

        self.family = None
        self.device = None

        self.project_name = None
        self.srcs = None
        self.top = None
        self.out_dir = None

        with Timed(self, 'nop'):
            subprocess.check_call("true", shell=True, cwd=self.out_dir)

    def add_runtime(self, name, dt):
        self.runtimes[name] = dt

    def perf(self):
        s = self.family + '-' + self.device + '_' + self.toolchain + '_' + self.project_name
        print('Timing (%s)' % s)
        for k, v in self.runtimes.items():
            print('  % -16s %0.3f' % (k + ':', v))

    def project(self, name, family, device, srcs, top, out_dir):
        self.family = family
        self.device = device

        self.project_name = name
        self.srcs = srcs
        self.top = top
        self.out_dir = out_dir

    def cmd(self, cmd, argstr):
        print("Running: %s %s" % (cmd, argstr))
        open("%s/%s.txt" % (self.out_dir, cmd), "w").write("Running: %s %s\n\n" % (cmd, argstr))
        with Timed(self, cmd):
            subprocess.check_call("%s %s |&tee -a %s.txt; (exit $PIPESTATUS )" % (cmd, argstr, cmd), shell=True, cwd=self.out_dir)

class Icestorm(Toolchain):
    def __init__(self):
        Toolchain.__init__(self)
        self.toolchain = 'icestorm'

    def yosys(self):
        yscript = "synth_ice40 -top %s -blif my.blif" % self.top
        self.cmd("yosys", "-p '%s' %s" % (yscript, ' '.join(self.srcs)))

    def run(self):
        with Timed(self, 'bit-all'):
            self.yosys()
            self.cmd("arachne-pnr", "-d 8k -P cm81 -o my.asc my.blif")
            self.cmd("icepack", "my.asc my.bin")

        self.cmd("icetime", "-tmd hx8k my.asc")

class VPR(Toolchain):
    def __init__(self):
        Toolchain.__init__(self)
        self.toolchain = 'vpr'
        self.sfad_build = os.getenv("HOME") + "/symbiflow-arch-defs/tests/build/ice40-top-routing-virt-hx8k"

    def yosys(self):
        yscript = "synth_ice40 -top %s -nocarry; ice40_opt -unlut; abc -lut 4; opt_clean; write_blif -attr -cname -param my.eblif" % self.top
        self.cmd("yosys", "-p '%s' %s" % (yscript, ' '.join(self.srcs)))

    def run(self):
        with Timed(self, 'bit-all'):
            self.yosys()

            arch_xml = self.sfad_build + '/arch.xml'
            rr_graph = self.sfad_build + "/rr_graph.real.xml"
            # --fix_pins " + io_place
            #io_place = ".../symbiflow-arch-defs/tests/ice40/tiny-b2_blink//build-ice40-top-routing-virt-hx8k/io.place"
            self.cmd("vpr", arch_xml + " my.eblif --device hx8k-cm81 --min_route_chan_width_hint 100 --route_chan_width 100 --read_rr_graph " + rr_graph + " --debug_clustering on --pack --place --route")

            self.cmd("icebox_hlc2asc.py", "top.hlc > my.asc")

        self.cmd("icetime", "-tmd hx8k my.asc")

def run_vpr(srcs, top, out_dir):
    pass

def run(family, device, toolchain, project, out_dir):
    assert family == 'ice40'
    assert device == 'hx8k'

    t = {
        'icestorm': Icestorm,
        'vpr': VPR,
        #'radiant': VPR,
        #'icecube': VPR,
        }[toolchain]()

    if out_dir is None:
        out_dir = "build/" + family + '-' + device + '_' + toolchain + '_' + project
    if not os.path.exists("build"):
        os.mkdir("build")
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    print('Writing to %s' % out_dir)

    cwd = os.getcwd()

    if 1:
        srcs = [cwd + '/src/blinky.v']
        top = 'top'
        name = 'blinky'

    t.project(name, family, device, srcs, top, out_dir)

    t.run()
    t.perf()

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
    parser.add_argument('--out-dir', default=None, help='Output directory')
    args = parser.parse_args()

    run(args.family, args.device, args.toolchain, args.project, args.out_dir)

if __name__ == '__main__':
    main()
