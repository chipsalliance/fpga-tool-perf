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
from utils import Timed

class Toolchain:
    '''A toolchain takes in verilog files and produces a .bitstream'''
    # List of supported carry modes
    # Default to first item
    carries = None
    strategies = None

    def __init__(self, rootdir):
        self.rootdir = rootdir
        self.runtimes = collections.OrderedDict()
        self.toolchain = None
        self.verbose = False
        self.cmds = []
        self.pcf = None
        self._strategy = None
        self._carry = None
        self.seed = None
        self.build = None
        self.date = datetime.datetime.utcnow()

        self.family = None
        self.device = None
        self.package = None

        self.project_name = None
        self.srcs = None
        self.top = None
        self.out_dir = None

        with Timed(self, 'nop'):
            subprocess.check_call("true", shell=True, cwd=self.out_dir)

    def canonicalize(self, fns):
        return [os.path.realpath(self.rootdir + '/' + fn) for fn in fns]

    def optstr(self):
        ret = ''
        def add(s):
            nonlocal ret

            if ret:
                ret += '_' + s
            else:
                ret = s

        if self.pcf:
            add('pcf')
        # omit carry if not explicitly given?
        if self.carry is not None:
            add('carry-%c' % ('y' if self.carry else 'n',))
        if self.strategy:
            add(self.strategy)
        if self.seed:
            add('seed-%08X' % (self.seed,))
        return ret

    def add_runtime(self, name, dt):
        self.runtimes[name] = dt

    def design(self):
        ret = self.family + '-' + self.device + '-' + self.package + '_' + self.toolchain + '_' + self.project_name
        op = self.optstr()
        if op:
            ret += '_' + op
        return ret

    @property
    def carry(self):
        return self.carries[0] if self._carry is None else self._carry

    @carry.setter
    def carry(self, value):
        assert value is None or value in self.carries, 'Carry modes supported: %s, got: %s' % (self.carries, value)
        self._carry = value

    def ycarry(self):
        if self.carry:
            return ""
        else:
            return " -nocarry"

    def yscript(self, cmds):
        def process(cmd):
            if cmd.find('synth_ice40') == 0:
                cmd += self.ycarry()
            return cmd

        yscript = '; '.join([process(cmd) for cmd in cmds])
        self.cmd("yosys", "-p '%s' %s" % (yscript, ' '.join(self.srcs)))

    @property
    def strategy(self):
        # Use given strategy first
        if self._strategy is not None:
            return self._strategy
        # Default
        elif self.strategies is not None:
            return self.strategies[0]
        # Not supported
        else:
            return None

    @strategy.setter
    def strategy(self, value):
        if self.strategies is None:
            assert value is None, "Strategies not supported, got %s" % (value,)
        else:
            assert value is None or value in self.strategies, 'Strategies supported: %s, got: %s' % (self.strategies, value)
        self._strategy = value

    def project(self, name, family, device, package, srcs, top, out_dir=None, out_prefix=None, data=None):
        self.family = family
        self.device = device
        self.package = package

        self.project_name = name
        self.srcs = self.canonicalize(srcs)
        for src in self.srcs:
            if not os.path.exists(src):
                raise ValueError("Missing source file %s" % src)
        self.top = top

        out_prefix = out_prefix or 'build'
        if not os.path.exists(out_prefix):
            os.mkdir(out_prefix)

        if out_dir is None:
            out_dir = out_prefix + "/" + self.design()
        self.out_dir = out_dir
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)
        print('Writing to %s' % out_dir)
        if data:
            for f in data:
                dst = os.path.join(out_dir, os.path.basename(f))
                print("Copying data file {} to {}".format(f, dst))
                shutil.copy(f, dst)

    def cmd(self, cmd, argstr, env=None):
        print("Running: %s %s" % (cmd, argstr))
        self.cmds.append('%s %s' % (cmd, argstr))

        # Use this to checkpoint various stages
        # If a command fails, we'll have everything up to it
        self.write_metadata(all=False)

        cmd_base = os.path.basename(cmd)
        with open("%s/%s.txt" % (self.out_dir, cmd_base), "w") as f:
            f.write("Running: %s %s\n\n" % (cmd_base, argstr))
        with Timed(self, cmd_base):
            if self.verbose:
                cmdstr = "(%s %s) |&tee -a %s.txt; (exit $PIPESTATUS )" % (cmd, argstr, cmd)
                print("Running: %s" % cmdstr)
                print("  cwd: %s" % self.out_dir)
            else:
                cmdstr = "(%s %s) >& %s.txt" % (cmd, argstr, cmd_base)
            subprocess.check_call(cmdstr, shell=True, executable='bash', cwd=self.out_dir, env=env)

    def write_metadata(self, all=True):
        out_dir = self.out_dir

        # If an intermediate write, tolerate missing resource tally
        try:
            resources = self.resources()
            max_freq = self.max_freq()
        except FileNotFoundError:
            if all:
                raise
            resources = dict([(x, None) for x in ('LUT', 'DFF', 'BRAM', 'CARRY', 'GLB', 'PLL', 'IOB')])
            max_freq = None

        date_str = self.date.replace(microsecond=0).isoformat()
        j = {
            'design': self.design(),
            'family': self.family,
            'device': self.device,
            'package': self.package,
            'project': self.project_name,
            'optstr': self.optstr(),
            'pcf': os.path.basename(self.pcf) if self.pcf else None,
            'carry': self.carry,
            'seed': self.seed,
            'build': self.build,
            'date': date_str,

            'toolchain': self.toolchain,
            'strategy': self.strategy,

            # canonicalize
            'sources': [x.replace(os.getcwd(), '.') for x in self.srcs],
            'top': self.top,

            "runtime": self.runtimes,
            "max_freq": max_freq,
            "resources": resources,
            "verions": self.versions(),
            "cmds": self.cmds,
            }
        with open(out_dir + '/meta.json', 'w') as f:
            json.dump(j, f, sort_keys=True, indent=4)

        # write .csv for easy import
        with open(out_dir + '/meta.csv', 'w') as csv:
            nonestr = lambda x: x if x is not None else ''

            csv.write('Build,Date,Family,Device,Package,Project,Toolchain,Strategy,pcf,Carry,Seed,Freq (MHz),Build (sec),#LUT,#DFF,#BRAM,#CARRY,#GLB,#PLL,#IOB\n')
            pcf_str = os.path.basename(self.pcf) if self.pcf else ''
            seed_str = '%08X' % self.seed if self.seed else ''
            runtime_str = '%0.1f' % self.runtimes['bit-all'] if 'bit-all' in self.runtimes else ''
            freq_str = '%0.1f' % (max_freq/1e6) if max_freq is not None else ''
            fields = [nonestr(self.build), date_str, self.family, self.device, self.package, self.project_name, self.toolchain, nonestr(self.strategy), pcf_str, str(self.carry), seed_str, freq_str, runtime_str]
            fields += [str(resources[x]) for x in ('LUT', 'DFF', 'BRAM', 'CARRY', 'GLB', 'PLL', 'IOB')]
            csv.write(','.join(fields) + '\n')
            csv.close()

        # Provide some context when comparing runtimes against systems
        subprocess.check_call('uname -a >uname.txt', shell=True, executable='bash', cwd=self.out_dir)
        subprocess.check_call('lscpu >lscpu.txt', shell=True, executable='bash', cwd=self.out_dir)

    @staticmethod
    def seedable():
        return False

    @staticmethod
    def check_env():
        return {}
