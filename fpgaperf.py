#!/usr/bin/env python3

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

from toolchain import Toolchain
from utils import Timed

from icestorm import Nextpnr
from icestorm import Arachne

# to find data files
root_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = root_dir + '/project'

class NotAvailable:
    pass

# https://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

def have_exec(mybin):
    return which(mybin) != None

# couldn't get icestorm version
# filed https://github.com/cliffordwolf/icestorm/issues/163
class Vivado(Toolchain):
    '''Vivado toolchain (synth and PnR)'''
    carries = (False, False)

    def __init__(self):
        Toolchain.__init__(self)
        self.toolchain = 'vivado'
        self.files = []
        self.edam = None
        self.backend = None

    def run(self):
        with Timed(self, 'bitstream'):
            os.makedirs(self.out_dir, exist_ok = True)
            for f in self.srcs:
                self.files.append({'name' : os.path.realpath(f), 'file_type': 'verilogSource'})

            self.files.append({'name' : os.path.realpath(self.pcf), 'file_type': 'xdc'})

            chip = self.family + self.device + self.package

            self.edam = {
                'files' : self.files,
                'name' : self.project_name,
                'toplevel' : self.top,
                'tool_options' : {'vivado' : {'part' : chip}}
            }

            self.backend = edalize.get_edatool('vivado')(edam=self.edam, work_root=self.out_dir)
            self.backend.configure("")
            self.backend.build()

    @staticmethod
    def seedable():
        return False

    @staticmethod
    def check_env():
        return {
            'vivado': have_exec('vivado'),
            }

    def max_freq(self):
        # FIXME: this should be read from timing report
        return 0.0

    def vivado_resources(self):
        report_path = self.out_dir + "/" + self.project_name + ".runs/impl_1/top_utilization_placed.rpt"
        with open(report_path, 'r') as fp:
            report_data = fp.read()
            report_data = report_data.split('\n\n')
            report = dict()
            section = None
            for d in report_data:
                match = re.search(r'\n-+$', d)
                if match is not None:
                    match = re.search(r'\n?[0-9\.]+ (.*)', d)
                    if match is not None:
                        section = match.groups()[0]
                if d.startswith('+--'):
                    if section is not None:
                        # cleanup the table
                        d = re.sub(r'\+-.*-\+\n','', d)
                        d = re.sub(r'\+-.*-\+$','', d)
                        d = re.sub(r'^\|\s+','', d, flags=re.M)
                        d = re.sub(r'\s\|\n','\n', d)

                        report[section.lower()] = asciitable.read(d, delimiter='|', guess=False, comment=r'(\+.*)|(\*.*)', numpy=False)

        return report

    def resources(self):
        lut = 0
        dff = 0
        carry = 0
        iob = 0
        pll = 0
        bram = 0

        report = self.vivado_resources()

        for prim in report['primitives']:
            if prim[2] == 'Flop & Latch':
                dff += int(prim[1])
            if prim[2] == 'CarryLogic':
                carry += int(prim[1])
            if prim[2] == 'IO':
                iob += int(prim[1])
            if prim[2] == 'LUT':
                lut += int(prim[1])

        for prim in report['clocking']:
            if prim[0] == 'MMCME2_ADV' or prim[0] == 'PLLE2_ADV':
                pll += prim[1]

        for prim in report['memory']:
            if prim[0] == 'Block RAM Tile':
                bram += prim[1]

        ret = {
            "LUT" : str(lut),
            "DFF" : str(dff),
            "BRAM" : str(bram),
            "CARRY" : str(carry),
            "GLB" : "unsupported",
            "PLL" : str(pll),
            "IOB" : str(iob),
            }
        return ret

    def versions(self):
        return self.backend.get_version()


class VPR(Toolchain):
    '''VPR using Yosys for synthesis'''
    # as of 2018-08-06 think carry doesn't work
    carries = (False,)

    def __init__(self):
        Toolchain.__init__(self)
        self.toolchain = 'vpr'

    def yosys(self):
        self.yscript(["synth_ice40 -vpr -top %s -blif my.eblif" % (self.top,)])

    def sfad_dir(self):
        return os.getenv("SFAD_DIR", os.getenv("HOME") + "/symbiflow-arch-defs")

    def sfad_build(self):
        sfad_build = os.getenv("SFAD_BUILD", None)
        if sfad_build:
            return sfad_build

        if not os.path.exists(self.sfad_dir()):
            raise Exception("Missing SFAD dir: %s" % self.sfad_dir())
        return self.sfad_dir() + "/ice40/build/ice40-top-routing-virt-" + self.device

    @staticmethod
    def vpr_bin():
        return os.getenv("VPR", 'vpr')

    def run(self):
        self.sfad_build = self.sfad_build()
        if not os.path.exists(self.sfad_build):
            raise Exception("Missing VPR dir: %s" % self.sfad_build)

        with Timed(self, 'bit-all'):
            self.yosys()

            arch_xml = self.sfad_build + '/arch.xml'
            rr_graph = self.sfad_build + "/rr_graph.real.xml"

            devstr = self.device + '-' + self.package

            optstr = ''
            optstr += arch_xml
            optstr += " my.eblif"
            optstr += " --device " + devstr
            optstr += " --min_route_chan_width_hint 100 --route_chan_width 100"
            optstr += " --read_rr_graph " + rr_graph

            if self.pcf:
                #io_place_file = self.out_dir + '/io.place'
                #create_ioplace = 'python3 ' + self.sfad_dir() + '/ice40/utils/ice40_create_ioplace.py'
                create_ioplace = self.sfad_dir() + '/ice40/utils/ice40_create_ioplace.py'
                map_file = self.sfad_dir() + '/ice40/devices/layouts/icebox/%s.%s.pinmap.csv' % (self.device, self.package)
                self.cmd(create_ioplace, '--pcf %s --blif %s --map %s --output %s' % (self.pcf, "my.eblif", map_file, 'io.place'))
                optstr += ' --fix_pins io.place'
            if self.seed:
                optstr += ' --seed %d' % self.seed

            # Workaround for https://github.com/SymbiFlow/fpga-tool-perf/issues/9
            # optstr += " --pack --place --route"
            for phase_args in (" --pack --place", " --route"):
                self.cmd(self.vpr_bin(), optstr + phase_args)

            self.cmd("icebox_hlc2asc", "%s.hlc > my.asc" % (self.top,))
            self.cmd("icepack", "my.asc my.bin")

        self.cmd("icetime", "-tmd " + self.device + " my.asc")

    def max_freq(self):
        with open(self.out_dir + '/icetime.txt') as f:
            return icetime_parse(f)['max_freq']

    """
    @staticmethod
    def resource_parse(f):
        '''
        abanonded in favor of icebox_stat
        although maybe would be good to compare results?

        Resource usage...
            Netlist      0    blocks of type: EMPTY
            Architecture 0    blocks of type: EMPTY
            Netlist      4    blocks of type: BLK_TL-PLB
            Architecture 960    blocks of type: BLK_TL-PLB
            Netlist      0    blocks of type: BLK_TL-RAM
            Architecture 32    blocks of type: BLK_TL-RAM
            Netlist      2    blocks of type: BLK_TL-PIO
            Architecture 256    blocks of type: BLK_TL-PIO

        Device Utilization: 0.00 (target 1.00)
            Block Utilization: 0.00 Type: EMPTY
            Block Utilization: 0.00 Type: BLK_TL-PLB
            Block Utilization: 0.00 Type: BLK_TL-RAM
            Block Utilization: 0.01 Type: BLK_TL-PIO
        '''
        def waitfor(s):
            while True:
                l = f.readline()
                if not l:
                    raise Exception("EOF")
                if s.find(s) >= 0:
                    return
        waitfor('Resource usage...')
        while True:
            l = f.readline().strip()
            if not l:
                break
            # Netlist      2    blocks of type: BLK_TL-PIO
            # Architecture 256    blocks of type: BLK_TL-PIO
            parts = l.split()
            if parts[0] != 'Netlist':
                continue

        waitfor('Device Utilization: ')
    """

    def resources(self):
        return icebox_stat("my.asc", self.out_dir)

    @staticmethod
    def vpr_version():
        '''
        vpr  --version

        VPR FPGA Placement and Routing.
        Version: 8.0.0-dev+vpr-7.0.5-6027-g94a747729
        Revision: vpr-7.0.5-6027-g94a747729
        Compiled: 2018-06-21T16:45:11 (release build)
        Compiler: GNU 6.3.0 on Linux-4.9.0-5-amd64 x86_64
        University of Toronto
        vtr-users@googlegroups.com
        This is free open source code under MIT license.
        '''
        out = subprocess.check_output("vpr --version", shell=True, universal_newlines=True).strip()
        version = None
        revision = None
        for l in out.split('\n'):
            l = l.strip()
            if l.find('Version:') == 0:
                version = l
            if l.find('Revision:') == 0:
                revision = l
        assert version is not None
        assert revision is not None
        return version + ', ' + revision

    def versions(self):
        return {
            'yosys': yosys_ver(),
            'vpr': VPR.vpr_version(),
            }

    @staticmethod
    def seedable():
        return True

    @staticmethod
    def check_env():
        return {
            'yosys':            have_exec('yosys'),
            'vpr':              have_exec(VPR.vpr_bin()),
            'icebox_hlc2asc':   have_exec('icebox_hlc2asc'),
            'icepack':          have_exec('icepack'),
            'icetime':          have_exec('icetime'),
            }


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
            args = "--syn %s" % (self.syn(),)
            if self.strategy:
                args += " --strategy %s" % (self.strategy,)
            self.cmd(root_dir + "/icecubed.sh", args, env=env)

            self.cmd("iceunpack", "my.bin my.asc")

        self.cmd("icetime", "-tmd %s my.asc" % (self.device,))

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
    carries = (True,)

    def __init__(self):
        Icecube2.__init__(self)
        self.toolchain = 'icecube2-synpro'

    def syn(self):
        return "synpro"

    @staticmethod
    def check_env():
        return {
            'ICECUBEDIR':       os.path.exists(Icecube2.ICECUBEDIR_DEFAULT),
            'icetime':          have_exec('icetime'),
            }


class Icecube2LSE(Icecube2):
    '''Lattice Icecube2 using LSE for synthesis'''
    carries = (True,)

    def __init__(self):
        Icecube2.__init__(self)
        self.toolchain = 'icecube2-lse'

    def syn(self):
        return "lse"

    @staticmethod
    def check_env():
        return {
            'ICECUBEDIR':       os.path.exists(Icecube2.ICECUBEDIR_DEFAULT),
            'icetime':          have_exec('icetime'),
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
            'yosys':            have_exec('yosys'),
            'ICECUBEDIR':       os.path.exists(Icecube2.ICECUBEDIR_DEFAULT),
            'icetime':          have_exec('icetime'),
            }


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
        assert (self.device, self.package) in [('up3k', 'uwg30'), ('up5k', 'uwg30'), ('up5k', 'sg48')]

        with Timed(self, 'bit-all'):
            env = os.environ.copy()
            env["SRCS"] = ' '.join(self.srcs)
            env["TOP"] = self.top
            env["RADIANTDIR"] = self.radiantdir
            env["RADDEV"] = self.device + '-' + self.package
            syn = self.syn()
            args = "--syn %s" % (syn,)
            if self.strategy:
                args +=  " --strategy %s" % self.strategy
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
            'RADIANTDIR':       os.path.exists(Radiant.RADIANTDIR_DEFAULT),
            'iceunpack':        have_exec('iceunpack'),
            'icetime':          have_exec('icetime'),
            }


class RadiantLSE(Radiant):
    '''Lattice Radiant using LSE for synthesis'''
    carries = (True,)

    def __init__(self):
        Radiant.__init__(self)
        self.toolchain = 'radiant-lse'

    def syn(self):
        return "lse"


class RadiantSynpro(Radiant):
    '''Lattice Radiant using Synplify for synthesis'''
    carries = (True,)

    def __init__(self):
        Radiant.__init__(self)
        self.toolchain = 'radiant-synpro'

    def syn(self):
        return "synplify"


# @E: CG389 :"/home/mcmaster/.../impl/impl.v":18:4:18:7|Reference to undefined module SB_LUT4
# didn't look into importing edif
class RadiantYosys(Radiant):
    carries = (True, False)

    def __init__(self):
        Radiant.__init__(self)
        self.toolchain = 'radiant-yosys'

    def syn(self):
        return "yosys-synpro"


def print_stats(t):
    print('Design %s' % t.design())
    print('  Family: %s' % t.family)
    print('  Device: %s' % t.device)
    print('  Package: %s' % t.package)
    print('  Project: %s' % t.project_name)
    print('  Toolchain: %s' % t.toolchain)
    print('  Strategy: %s' % t.strategy)
    print('  Carry: %s' % (t.carry,))
    if t.seed:
        print('  Seed: 0x%08X (%u)' % (t.seed, t.seed))
    else:
        print('  Seed: default')
    print('Timing:')
    for k, v in t.runtimes.items():
        print('  % -16s %0.3f' % (k + ':', v))
    print('Max frequency: %0.3f MHz' % (t.max_freq() / 1e6,))
    print('Resource utilization')
    for k, v in sorted(t.resources().items()):
        print('  %- 20s %s' % (k + ':', v))

toolchains = {
        'vivado' : Vivado,
        'arachne': Arachne,
        'vpr': VPR,
        'nextpnr': Nextpnr,
        'icecube2-synpro':  Icecube2Synpro,
        'icecube2-lse':     Icecube2LSE,
        'icecube2-yosys':   Icecube2Yosys,
        'radiant-synpro':   RadiantSynpro,
        'radiant-lse':      RadiantLSE,
        #'radiant-yosys':    RadiantYosys,
        #'radiant': VPR,
        }

def run(family, device, package, toolchain, project, out_dir=None, out_prefix=None, verbose=False, strategy=None, seed=None, pcf=None, carry=None, build=None):
    assert family == 'ice40' or family == 'xc7'
    assert device is not None
    assert package is not None
    assert toolchain is not None
    assert project is not None
    # some toolchains use signed 32 bit
    assert seed is None or 1 <= seed <= 0x7FFFFFFF

    t = toolchains[toolchain](root_dir)
    t.verbose = verbose
    t.strategy = strategy
    t.seed = seed
    t.carry = carry
    # XXX: sloppy path handling here...
    t.pcf = os.path.realpath(pcf) if pcf else None
    t.build = build

    t.project(project['name'], family, device, package, project['srcs'], project['top'], out_dir=out_dir, out_prefix=out_prefix, data=project.get('data', None))

    t.run()
    print_stats(t)
    t.write_metadata()

def get_toolchains():
    '''Query all supported toolchains'''
    return sorted(toolchains.keys())

def list_toolchains():
    '''Print all supported toolchains'''
    for t in get_toolchains():
        print(t)

def get_projects():
    '''Query all supported projects'''
    return sorted([re.match('/.*/(.*)[.]json', fn).group(1) for fn in glob.glob(project_dir + '/*.json')])

def list_projects():
    '''Print all supported projects'''
    for project in get_projects():
        print(project)

def get_seedable():
    '''Query toolchains that support --seed'''
    ret = []
    for t, tc in sorted(toolchains.items()):
        if tc.seedable():
            ret.append(t)
    return ret

def list_seedable():
    '''Print toolchains that support --seed'''
    for t in get_seedable():
        print(t)

def check_env(to_check=None):
    '''For each tool, print dependencies and if they are met'''
    tools = toolchains.items()
    if to_check:
        tools = list(filter(lambda t: t[0] == to_check, tools))
        if not tools:
            raise TypeError("Unknown toolchain %s" % to_check)
    for t, tc in sorted(tools):
        print(t)
        for k, v in tc.check_env().items():
            print('  %s: %s' % (k, v))

def env_ready():
    '''Return true if every tool can be ran'''
    for tc in toolchains.values():
        for v in tc.check_env().values():
            if not v:
                return False
    return True

def get_project(name):
    project_fn = project_dir + '/' + name + '.json'
    with open(project_fn, 'r') as f:
        return json.load(f)

def add_bool_arg(parser, yes_arg, default=False, **kwargs):
    dashed = yes_arg.replace('--', '')
    dest = dashed.replace('-', '_')
    parser.add_argument(yes_arg, dest=dest, action='store_true', default=default, **kwargs)
    parser.add_argument('--no-' + dashed, dest=dest, action='store_false', **kwargs)

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=
        'Analyze FPGA tool performance (MHz, resources, runtime, etc)'
    )

    parser.add_argument('--verbose', action='store_true', help='')
    parser.add_argument('--overwrite', action='store_true', help='')
    parser.add_argument('--family', default='ice40', help='Device family')
    parser.add_argument('--device', default='hx8k', help='Device within family')
    parser.add_argument('--package', default=None, help='Device package')
    parser.add_argument('--strategy', default=None, help='Optimization strategy')
    add_bool_arg(parser, '--carry', default=None, help='Force carry / no carry (default: use tool default)') 
    parser.add_argument('--toolchain', help='Tools to use', choices=get_toolchains())
    parser.add_argument('--list-toolchains', action='store_true', help='')
    parser.add_argument('--project', help='Source code to run on', choices=get_projects())
    parser.add_argument('--list-projects', action='store_true', help='')
    parser.add_argument('--seed', default=None, help='31 bit seed number to use, possibly directly mapped to PnR tool')
    parser.add_argument('--list-seedable', action='store_true', help='')
    parser.add_argument('--check-env', action='store_true', help='Check if environment is present')
    parser.add_argument('--out-dir', default=None, help='Output directory')
    parser.add_argument('--out-prefix', default=None, help='Auto named directory prefix (default: build)')
    parser.add_argument('--pcf', default=None, help='')
    parser.add_argument('--build', default=None, help='Build number')
    args = parser.parse_args()

    if args.list_toolchains:
        list_toolchains()
    elif args.list_projects:
        list_projects()
    elif args.list_seedable:
        list_seedable()
    elif args.check_env:
        check_env(args.toolchain)
    else:
        argument_errors = []
        if args.family is None:
            argument_errors.append('--family argument required')
        if args.device is None:
            argument_errors.append('--device argument required')
        if args.package is None:
            argument_errors.append('--package argument required')
        if args.toolchain is None:
            argument_errors.append('--toolchain argument required')
        if args.project is None:
            argument_errors.append('--project argument required')

        if argument_errors:
            parser.print_usage()
            for e in argument_errors:
                print('{}: error: {}'.format(sys.argv[0], e))
            sys.exit(1)

        seed = int(args.seed, 0) if args.seed else None
        run(args.family, args.device, args.package, args.toolchain, get_project(args.project), out_dir=args.out_dir, out_prefix=args.out_prefix, strategy=args.strategy, pcf=args.pcf, carry=args.carry, seed=seed, build=args.build, verbose=args.verbose)

if __name__ == '__main__':
    main()
