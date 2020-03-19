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


class Vivado(Toolchain):
    '''Vivado toolchain (synth and PnR)'''
    carries = (False, False)

    def __init__(self, rootdir):
        Toolchain.__init__(self, rootdir)
        self.toolchain = 'vivado'
        self.synthtool = 'vivado'
        self.files = []
        self.edam = None
        self.backend = None

    def run(self):
        def get_runtimes(logfile):
            def get_seconds(time_str):
                time = time_str.split(':')
                seconds = 3600 * int(time[0])
                seconds += 60 * int(time[1])
                seconds += int(time[2])
                return seconds

            log = dict()
            commands = list()
            with open(logfile, 'r') as fp:
                for l in fp:
                    l = l.strip('\n')
                    if l.startswith("Command"):
                        command = l.split()[1]
                        commands.append(command)
                    if l.startswith(tuple(commands)):
                        cpu = False
                        elapsed = False
                        time_re = re.match(
                            ".*cpu = ([0-9:]+).*elapsed = ([0-9:]+)", str(l)
                        )
                        if time_re is not None:
                            l = l.split()
                            command = l[0].strip(':')
                            log[command] = get_seconds(time_re.groups()[1])
            return log

        with Timed(self, 'bitstream'):
            os.makedirs(self.out_dir, exist_ok=True)
            for f in self.srcs:
                self.files.append(
                    {
                        'name': os.path.realpath(f),
                        'file_type': 'verilogSource'
                    }
                )

            self.files.append(
                {
                    'name': os.path.realpath(self.pcf),
                    'file_type': 'xdc'
                }
            )

            chip = self.family + self.device + self.package

            self.edam = {
                'files': self.files,
                'name': self.project_name,
                'toplevel': self.top,
                'parameters':
                    {
                        'VIVADO':
                            {
                                'paramtype': 'vlogdefine',
                                'datatype': 'int',
                                'default': 1,
                            },
                    },
                'tool_options':
                    {
                        'vivado': {
                            'part': chip,
                            'synth': self.synthtool,
                        }
                    }
            }

            self.backend = edalize.get_edatool('vivado')(
                edam=self.edam, work_root=self.out_dir
            )
            self.backend.configure("")
            self.backend.build()
        runs_dir = self.out_dir + "/" + self.project_name + ".runs"
        synth_times = get_runtimes(runs_dir + '/synth_1/runme.log')
        impl_times = get_runtimes(runs_dir + '/impl_1/runme.log')
        total_runtime = 0
        for t in synth_times:
            self.add_runtime(t, synth_times[t], parent='logs')
            total_runtime += float(synth_times[t])
        for t in impl_times:
            self.add_runtime(t, impl_times[t], parent='logs')
            total_runtime += float(impl_times[t])
        self.add_runtime('total', total_runtime, parent='logs')

    @staticmethod
    def seedable():
        return False

    @staticmethod
    def check_env():
        return {
            'vivado': have_exec('vivado'),
        }

    def max_freq(self):
        processing = False

        group = ""
        delay = ""
        freq = 0
        freqs = {}

        report_file = self.out_dir + "/" + self.project_name + ".runs/impl_1/top_timing_summary_routed.rpt"
        path_type = None

        with open(report_file, 'r') as fp:
            for l in fp:

                if l.startswith("Slack"):
                    if '(MET)' in l:
                        violation = 0.0
                    else:
                        violation = float(
                            l.split(':')[1].split()[0].strip().strip('ns')
                        )
                    processing = True

                if processing is True:
                    fields = l.split()
                    if len(fields) > 1 and fields[1].startswith('----'):
                        processing = False
                        # check if this is a timing we want
                        if group not in requirement.split():
                            continue
                        if group not in freqs:
                            freqs[group] = dict()
                            freqs[group]['actual'] = freq
                            freqs[group]['requested'] = requested_freq
                            freqs[group]['met'] = freq >= requested_freq
                            freqs[group]['{}_violation'.format(
                                path_type.lower()
                            )] = violation
                            path_type = None
                        if path_type is not None:
                            freqs[group]['{}_violation'.format(
                                path_type.lower()
                            )] = violation

                    data = l.split(':')
                    if len(data) > 1:
                        if data[0].strip() == 'Data Path Delay':
                            delay = data[1].split()[0].strip('ns')
                            freq = 1e9 / float(delay)
                        if data[0].strip() == 'Path Group':
                            group = data[1].strip()
                        if data[0].strip() == 'Requirement':
                            requirement = data[1].strip()
                            r = float(requirement.split()[0].strip('ns'))
                            if r != 0.0:
                                requested_freq = 1e9 / r
                        if data[0].strip() == 'Path Type':
                            ptype = data[1].strip()
                            if path_type != ptype.split()[0]:
                                path_type = ptype.split()[0]
        return freqs

    def vivado_resources(self, report_file):
        with open(report_file, 'r') as fp:
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
                        d = re.sub(r'\+-.*-\+\n', '', d)
                        d = re.sub(r'\+-.*-\+$', '', d)
                        d = re.sub(r'^\|\s+', '', d, flags=re.M)
                        d = re.sub(r'\s\|\n', '\n', d)

                        report[section.lower()] = asciitable.read(
                            d,
                            delimiter='|',
                            guess=False,
                            comment=r'(\+.*)|(\*.*)',
                            numpy=False
                        )

        return report

    def resources(self, report_file=None):
        lut = 0
        dff = 0
        carry = 0
        iob = 0
        pll = 0
        bram = 0

        if report_file is None:
            report_file = self.out_dir + "/" + self.project_name + ".runs/impl_1/top_utilization_placed.rpt"

        report = self.vivado_resources(report_file)

        for prim in report['primitives']:
            if prim[2] == 'Flop & Latch':
                dff += int(prim[1])
            if prim[2] == 'CarryLogic':
                carry += int(prim[1])
            if prim[2] == 'IO':
                if prim[0].startswith('OBUF') or prim[0].startswith('IBUF'):
                    iob += int(prim[1])
            if prim[2] == 'LUT':
                lut += int(prim[1])

        for prim in report['clocking']:
            if prim[0] == 'MMCME2_ADV' or prim[0] == 'PLLE2_ADV':
                pll += prim[1]

        for prim in report['memory']:
            if prim[0] == 'Block RAM Tile':
                # Vivado reports RAMB36. Multiply it by 2 to get RAMB18
                bram += prim[1] * 2

        ret = {
            "LUT": str(lut),
            "DFF": str(dff),
            "BRAM": str(bram),
            "CARRY": str(carry),
            "GLB": "unsupported",
            "PLL": str(pll),
            "IOB": str(iob),
        }
        return ret

    def versions(self):
        return self.backend.get_version()


class VivadoYosys(Vivado):
    '''Vivado PnR + Yosys synthesis'''
    carries = (False, False)

    def __init__(self, rootdir):
        Vivado.__init__(self, rootdir)
        self.synthtool = 'yosys'
        self.toolchain = 'yosys-vivado'

    @staticmethod
    def yosys_ver():
        # Yosys 0.7+352 (git sha1 baddb017, clang 3.8.1-24 -fPIC -Os)
        return subprocess.check_output(
            "yosys -V", shell=True, universal_newlines=True
        ).strip()

    def resources(self):
        report_file = self.out_dir + "/top_utilization_placed.rpt"
        return super(VivadoYosys, self).resources(report_file)

    def versions(self):
        return {
            'yosys': self.yosys_ver(),
            'vivado': super(VivadoYosys, self).versions()
        }
