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
        self.unprinted_runtimes = collections.OrderedDict()
        self.toolchain = None
        self.verbose = False
        self.cmds = []
        self.pcf = None
        self.sdc = None
        self.xdc = None
        self.params_file = None
        self.params_string = None
        self._strategy = None
        self._carry = None
        self.seed = None
        self.build = None
        self.build_type = None
        self.date = datetime.datetime.utcnow()

        self.family = None
        self.device = None
        self.package = None
        self.part = None
        self.board = None

        self.project_name = None
        self.srcs = None
        self.top = None
        self.out_dir = None
        self.clocks = None

        self.wirelength = None
        self.maximum_memory_use = None

        with Timed(self, 'nop'):
            subprocess.check_call("true", shell=True, cwd=self.out_dir)

    def canonicalize(self, fns):
        return [os.path.realpath(self.rootdir + '/' + fn) for fn in fns]

    def optstr(self):
        tokens = []

        if self.pcf:
            tokens.append('pcf')
        if self.sdc:
            tokens.append('sdc')
        if self.xdc:
            tokens.append('xdc')
        # omit carry if not explicitly given?
        if self.carry is not None:
            tokens.append('carry-%c' % ('y' if self.carry else 'n', ))
        if self.strategy:
            tokens.append(self.strategy)
        if self.seed:
            tokens.append('seed-%08X' % (self.seed, ))
        return '_'.join(tokens)

    def add_runtime(self, name, dt, parent=None, unprinted_runtime=False):
        collection = self.runtimes
        if unprinted_runtime:
            collection = self.unprinted_runtimes
        if parent is None:
            collection[name] = dt
        else:
            assert (parent not in collection
                    ) or (type(collection[parent]) is collections.OrderedDict)
            if parent not in collection:
                collection[parent] = collections.OrderedDict()
            collection[parent][name] = dt

    def design(self):
        ret = "{}_{}_{}_{}_{}".format(
            self.project_name, self.toolchain, self.family, self.part,
            self.board
        )

        if self.build_type:
            ret += '_' + self.build_type

        if self.build:
            ret += '_' + self.build

        op = self.optstr()
        if op:
            ret += '_' + op

        if self.seed:
            ret += '_seed_' + str(self.seed)

        return ret

    @property
    def carry(self):
        return self.carries[0] if self._carry is None else self._carry

    @carry.setter
    def carry(self, value):
        assert value is None or value in self.carries, 'Carry modes supported: %s, got: %s' % (
            self.carries, value
        )
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
            assert value is None, "Strategies not supported, got %s" % (
                value,
            )
        else:
            assert value is None or value in self.strategies, 'Strategies supported: %s, got: %s' % (
                self.strategies, value
            )
        self._strategy = value

    def project(
        self,
        project,
        family,
        device,
        package,
        board,
        params_file,
        params_string,
        out_dir=None,
        out_prefix=None,
    ):
        self.family = family
        self.device = device
        self.package = package
        self.part = "".join((device, package))
        self.board = board

        self.params_file = params_file
        self.params_string = params_string

        self.project_name = project['name']
        self.srcs = self.canonicalize(project['srcs'])
        for src in self.srcs:
            if not os.path.exists(src):
                raise ValueError("Missing source file %s" % src)
        self.top = project['top']

        if 'clocks' in project:
            self.clocks = project['clocks']

        out_prefix = out_prefix or 'build'
        if not os.path.exists(out_prefix):
            os.mkdir(out_prefix)

        if out_dir is None:
            out_dir = out_prefix + "/" + self.design()
        self.out_dir = out_dir
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)
        print('Writing to %s' % out_dir)
        data = project.get('data', None)
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
                cmdstr = "(%s %s) |&tee -a %s.txt; (exit $PIPESTATUS )" % (
                    cmd, argstr, cmd
                )
                print("Running: %s" % cmdstr)
                print("  cwd: %s" % self.out_dir)
            else:
                cmdstr = "(%s %s) >& %s.txt" % (cmd, argstr, cmd_base)
            subprocess.check_call(
                cmdstr,
                shell=True,
                executable='bash',
                cwd=self.out_dir,
                env=env
            )

    def get_runtimes(self):
        """Returns a standard runtime dictionary.

        Different tools have different names for the various EDA steps and,
        to generate a uniform data structure, these steps must fall into the correct
        standard category."""

        RUNTIME_ALIASES = {
            'prepare': ['prepare'],
            'synthesis': ['synth_design', 'synth', 'synthesis'],
            'optimization': ['opt_design'],
            'packing': ['pack'],
            'placement': ['place', 'place_design'],
            'routing': ['route', 'route_design'],
            'fasm': ['fasm'],
            'overhead': ['overhead'],
            'checkpoint': ['open_checkpoint'],
            'bitstream': ['write_bitstream', 'bitstream'],
            'reports': ['report_power', 'report_methodology', 'report_drc'],
            'total': ['total'],
            'nop': ['nop'],
            'fasm2bels': ['fasm2bels'],
            'link design': ['link_design'],
            'phys opt design': ['phys_opt_design']
        }

        def get_standard_runtime(runtime):
            for k, v in RUNTIME_ALIASES.items():
                for alias in v:
                    if runtime == alias:
                        return k

            assert False, "Couldn't find the standard name for {}".format(
                runtime
            )

        runtimes = {k: None for k in RUNTIME_ALIASES.keys()}

        for k, v in self.runtimes.items():
            runtime = get_standard_runtime(k)

            runtimes[runtime] = round(v, 3)

        return runtimes

    def write_metadata(self, all=True):
        out_dir = self.out_dir

        # If an intermediate write, tolerate missing resource tally
        try:
            resources = self.resources()
            max_freq = self.max_freq()
        except FileNotFoundError:
            if all:
                raise
            resources = dict(
                [
                    (x, None) for x in
                    ('LUT', 'DFF', 'BRAM', 'CARRY', 'GLB', 'PLL', 'IOB')
                ]
            )
            max_freq = None

        date_str = self.date.replace(microsecond=0).isoformat()
        j = {
            'design': self.design(),
            'family': self.family,
            'device': self.device,
            'package': self.package,
            'board': self.board,
            'project': self.project_name,
            'optstr': self.optstr(),
            'pcf': os.path.basename(self.pcf) if self.pcf else None,
            'sdc': os.path.basename(self.sdc) if self.sdc else None,
            'xdc': os.path.basename(self.xdc) if self.xdc else None,
            'carry': self.carry,
            'seed': self.seed,
            'build': self.build,
            'build_type': self.build_type,
            'date': date_str,
            'toolchain': self.toolchain,
            'strategy': self.strategy,
            'parameters': self.params_file or self.params_string,

            # canonicalize
            'sources': [x.replace(os.getcwd(), '.') for x in self.srcs],
            'top': self.top,
            "runtime": self.get_runtimes(),
            "max_freq": max_freq,
            "resources": resources,
            "versions": self.versions(),
            "cmds": self.cmds,
            "wirelength": self.wirelength,
            "maximum_memory_use": self.maximum_memory_use,
        }

        print

        with open(out_dir + '/meta.json', 'w') as f:
            json.dump(j, f, sort_keys=True, indent=4)

        # Provide some context when comparing runtimes against systems
        subprocess.check_call(
            'uname -a >uname.txt',
            shell=True,
            executable='bash',
            cwd=self.out_dir
        )
        subprocess.check_call(
            'lscpu >lscpu.txt',
            shell=True,
            executable='bash',
            cwd=self.out_dir
        )

    @staticmethod
    def seedable():
        return False

    @staticmethod
    def check_env():
        return {}
