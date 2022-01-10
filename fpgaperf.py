#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2018-2022 F4PGA Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

import os
import re
import sys
import glob
import logging
import yaml
from contextlib import redirect_stdout
from terminaltables import AsciiTable

from toolchains.icestorm import NextpnrIcestorm
from toolchains.nextpnr import NextpnrOxide, NextpnrXilinx, NextpnrFPGAInterchange
from toolchains.vivado import Vivado
from toolchains.vivado import VivadoYosys
from toolchains.vivado import VivadoYosysUhdm
from toolchains.symbiflow import VPR, Quicklogic
from toolchains.fasm2bels import VPRFasm2Bels, NextpnrXilinxFasm2Bels

# to find data files
root_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(root_dir, 'project')
src_dir = os.path.join(root_dir, 'src')

logger = logging.getLogger(__name__)


class NotAvailable:
    pass


def print_stats(t):
    def print_section_header(title):
        print('')
        print('=' * len(title))
        print(title)
        print('=' * len(title))
        print('')

    print_section_header('Setting')

    table_data = [
        ['Settings', 'Value'],
        ['Design', t.design()],
        ['Family', t.family],
        ['Device', t.device],
        ['Package', t.package],
        ['Project', t.project_name],
        ['Toolchain', t.toolchain],
        ['Strategy', t.strategy],
        ['Carry', t.carry],
    ]

    if t.seed:
        table_data.append(['Seed', ('0x%08X (%u)' % (t.seed, t.seed))])
    else:
        table_data.append(['Seed', 'default'])

    table = AsciiTable(table_data)
    print(table.table)

    print_section_header('Clocks')
    max_freq = t.max_freq()
    table_data = [
        [
            'Clock domain', 'Actual freq', 'Requested freq', 'Met?',
            'Setup violation', 'Hold violation'
        ]
    ]
    if type(max_freq) is float:
        table_data.append(['Design', ("%0.3f MHz" % max_freq)])
    elif type(max_freq) is dict:
        for cd in max_freq:
            actual = "%0.3f MHz" % (max_freq[cd]['actual'])
            requested = "%0.3f MHz" % (max_freq[cd]['requested'])
            met = "unknown" if max_freq[cd]['met'] is None else max_freq[cd][
                'met']
            s_violation = ("%0.3f ns" % max_freq[cd]['setup_violation'])
            h_violation = ("%0.3f ns" % max_freq[cd]['hold_violation'])
            table_data.append(
                [cd, actual, requested, met, s_violation, h_violation]
            )

    table = AsciiTable(table_data)
    print(table.table)

    print_section_header('Toolchain Run-Times')
    table_data = [['Stage', 'Run Time (seconds)']]
    for k, v in t.get_runtimes().items():
        value = "%0.3f" % v if v else "N/A"
        table_data.append([k, value])

    table = AsciiTable(table_data)
    print(table.table)

    resource_map = {"synth": "Post synthesys", "impl": "Post place and route"}

    for k, v in sorted(t.resources().items()):
        print_section_header(f"FPGA {resource_map[k]} resource utilization")
        table_data = [['Resource', 'Used']]

        for res_type, res_count in v.items():
            value = res_count if res_count else "N/A"
            table_data.append([res_type, value])

        table = AsciiTable(table_data)
        print(table.table)


toolchains = {
    'vivado': Vivado,
    'yosys-vivado': VivadoYosys,
    'yosys-vivado-uhdm': VivadoYosysUhdm,
    'vpr': VPR,
    'vpr-fasm2bels': VPRFasm2Bels,
    'nextpnr-ice40': NextpnrIcestorm,
    'nextpnr-xilinx': NextpnrXilinx,
    'nextpnr-xilinx-fasm2bels': NextpnrXilinxFasm2Bels,
    'nextpnr-fpga-interchange': NextpnrFPGAInterchange,
    'quicklogic': Quicklogic,
    'nextpnr-nexus': NextpnrOxide,
    # TODO: These are not currently be extensively tested
    #'synpro-icecube2': Icecube2Synpro,
    #'lse-icecube2': Icecube2LSE,
    #'yosys-icecube2': Icecube2Yosys,
    #'synpro-radiant': RadiantSynpro,
    #'lse-radiant': RadiantLSE,
    #'yosys-radiant': RadiantYosys,
    #'radiant': VPR,
}


def run(
    board,
    toolchain,
    project,
    params_file=None,
    params_string=None,
    out_dir=None,
    out_prefix=None,
    overwrite=False,
    verbose=False,
    strategy=None,
    seed=None,
    carry=None,
    build=None,
    build_type=None,
):
    assert board is not None
    assert toolchain is not None
    assert project is not None

    logger.debug("Preparing Project")
    project_dict = get_project(project)

    board_info = get_boards()[board]
    family = board_info['family']
    device = board_info['device']
    package = board_info['package']

    assert family == 'ice40' or family == 'xc7' or family == 'eos' or family == 'nexus'

    # some toolchains use signed 32 bit
    assert seed is None or 0 <= seed <= 0x7FFFFFFF

    t = toolchains[toolchain](root_dir)
    t.verbose = verbose
    t.strategy = strategy

    if t.seedable():
        t.seed = seed

    t.carry = carry

    # Constraint files shall be in their directories
    logger.debug("Getting Constraints")
    pcf = get_constraint(project, board, toolchain, 'pcf')
    sdc = get_constraint(project, board, toolchain, 'sdc')
    xdc = get_constraint(project, board, toolchain, 'xdc')
    pdc = get_constraint(project, board, toolchain, 'pdc')

    # XXX: sloppy path handling here...
    t.pcf = os.path.realpath(pcf) if pcf else None
    t.sdc = os.path.realpath(sdc) if sdc else None
    t.xdc = os.path.realpath(xdc) if xdc else None
    t.pdc = os.path.realpath(pdc) if pdc else None
    t.build = build
    t.build_type = build_type
    logger.debug("Running Project")
    t.project(
        project_dict,
        family,
        device,
        package,
        board,
        get_vendors(board=board),
        params_file,
        params_string,
        out_dir=out_dir,
        out_prefix=out_prefix,
        overwrite=overwrite,
    )

    output_error = ""
    with redirect_stdout(open(os.devnull, 'w')):
        try:
            t.run()
        except Exception as e:
            output_error = "[...]\n{}".format(
                str(e)[-1000:]
            ) if len(str(e)) > 1000 else str(e)
            output_error = output_error.split("\n")
            logger.debug(f"ERROR: {output_error}")

    logger.debug("Printing Stats")
    if not output_error:
        print_stats(t)

    logger.debug("Writing Metadata")
    t.write_metadata(output_error)


def get_combinations():
    """ Returns a list of tuples with all the possible combinations of supported builds """
    combs = list()
    for p in get_projects():
        toolchain_info = get_project(p)["required_toolchains"]
        vendor_info = get_project(p)["vendors"]
        for t in get_toolchains():
            vendor = get_vendors(t)
            if vendor not in vendor_info:
                continue

            board_info = vendor_info[vendor]
            for b in get_boards():
                if b not in get_vendors()[vendor]["boards"]:
                    continue

                if board_info is None or b not in board_info:
                    continue

                combs.append((p, t, b))

    return combs


def list_combinations(
    project=None,
    toolchain=None,
    board=None,
):
    '''Query all possible project/toolchain/board combinations'''
    table_data = [['Project', 'Toolchain', 'Board', 'Status']]
    for p in get_projects(project):
        toolchain_info = get_project(p)["required_toolchains"]
        vendor_info = get_project(p)["vendors"]
        for t in get_toolchains(toolchain):
            vendor = get_vendors(t)
            if vendor not in vendor_info:
                continue
            text = "Supported"
            board_info = vendor_info[vendor]
            if t not in toolchain_info:
                text = "Missing"
            for b in get_boards(board):
                if b not in get_vendors()[vendor]["boards"]:
                    continue
                text2 = text
                if board_info is None or b not in board_info:
                    text2 = "Missing"
                row = [p, t, b, text2]
                table_data.append(row)
    table = AsciiTable(table_data)
    print(table.table)


def get_vendors(toolchain=None, board=None):
    '''Return vendor information'''
    with open(os.path.join(root_dir, 'other', 'vendors.yaml'),
              'r') as vendors_file:
        vendors = yaml.safe_load(vendors_file)
    if toolchain is None and board is None:
        return vendors
    for v in vendors:
        if toolchain in vendors[v]["toolchains"]:
            return v
        if board in vendors[v]["boards"]:
            return v

    return None


def get_boards(board=None):
    '''Query all supported boards'''
    with open(os.path.join(root_dir, 'other', 'boards.yaml'),
              'r') as boards_file:
        boards = yaml.safe_load(boards_file)
    if board is None:
        return boards
    elif board in boards:
        return [board]
    else:
        return []


def list_boards():
    '''Print all supported boards'''
    for b in get_boards():
        print(b)


def get_toolchains(toolchain=None):
    '''Query all supported toolchains'''
    if toolchain is None:
        return sorted(toolchains.keys())
    elif toolchain in sorted(toolchains.keys()):
        return [toolchain]
    else:
        return []


def list_toolchains():
    '''Print all supported toolchains'''
    for t in get_toolchains():
        print(t)


def matching_pattern(path, pattern):
    return sorted([re.match(pattern, fn).group(1) for fn in glob.glob(path)])


def get_projects(project=None):
    '''Query all supported projects'''
    projects = matching_pattern(
        os.path.join(project_dir, '*.yaml'), '/.*/(.*)[.]yaml'
    )
    if project is None:
        return projects
    elif project in projects:
        return [project]
    else:
        return []


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
    '''Return true if every tool can be run'''
    for tc in toolchains.values():
        for v in tc.check_env().values():
            if not v:
                return False
    return True


def verify_constraint(project, board, extension):
    board_file = board + "." + extension
    path = os.path.join(src_dir, project, 'constr', board_file)
    return os.path.exists(path)


def get_constraint(project, board, toolchain, extension):
    constr_file = board + "-" + toolchain + "." + extension

    path = os.path.join(src_dir, project, 'constr', constr_file)
    if (os.path.exists(path)):
        return path
    constr_file = board + "." + extension

    path = os.path.join(src_dir, project, 'constr', constr_file)
    if (os.path.exists(path)):
        return path

    return None


def get_project(name):
    project_fn = os.path.join(project_dir, '{}.yaml'.format(name))
    with open(project_fn, 'r') as f:
        return yaml.safe_load(f)


def add_bool_arg(parser, yes_arg, default=False, **kwargs):
    dashed = yes_arg.replace('--', '')
    dest = dashed.replace('-', '_')
    parser.add_argument(
        yes_arg, dest=dest, action='store_true', default=default, **kwargs
    )
    parser.add_argument(
        '--no-' + dashed, dest=dest, action='store_false', **kwargs
    )


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description=
        'Analyze FPGA tool performance (MHz, resources, runtime, etc)'
    )

    parser.add_argument(
        '--verbose', action='store_true', help='Print DEBUG Statements'
    )
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite the folder with this run'
    )
    parser.add_argument(
        '--params_file', default=None, help='Use custom tool parameters'
    )
    parser.add_argument(
        '--params_string', default=None, help='Use custom tool parameters'
    )
    parser.add_argument(
        '--strategy', default=None, help='Optimization strategy'
    )
    add_bool_arg(
        parser,
        '--carry',
        default=None,
        help='Force carry / no carry (default: use tool default)'
    )
    parser.add_argument('--board', help='Target board', choices=get_boards())
    parser.add_argument('--list-boards', action='store_true', help='')
    parser.add_argument(
        '--toolchain', help='Tools to use', choices=get_toolchains()
    )
    parser.add_argument('--list-toolchains', action='store_true', help='')
    parser.add_argument(
        '--project', help='Source code to run on', choices=get_projects()
    )
    parser.add_argument('--list-projects', action='store_true', help='')
    parser.add_argument(
        '--list-combinations',
        action='store_true',
        help='Lists every <project, toolchain, board> combination.'
    )
    parser.add_argument(
        '--seed',
        default=None,
        help='31 bit seed number to use, possibly directly mapped to PnR tool'
    )
    parser.add_argument('--list-seedable', action='store_true', help='')
    parser.add_argument(
        '--check-env',
        action='store_true',
        help='Check if environment is present'
    )
    parser.add_argument('--out-dir', default=None, help='Output directory')
    parser.add_argument(
        '--out-prefix',
        default=None,
        help='Auto named directory prefix (default: build)'
    )
    parser.add_argument('--build', default=None, help='Build number')
    parser.add_argument('--build_type', default=None, help='Build type')
    args = parser.parse_args()

    if args.verbose:
        global logger
        logger = logging.getLogger('MyLogger')
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

    logger.debug("Parsing Arguments")

    assert not (args.params_file and args.params_string)

    if args.list_combinations:
        logger.debug("Listing Combinations")
        list_combinations(args.project, args.toolchain, args.board)
    elif args.list_toolchains:
        logger.debug("Listing Toolchains")
        list_toolchains()
    elif args.list_projects:
        logger.debug("Listing Projects")
        list_projects()
    elif args.list_boards:
        logger.debug("Listing Boards")
        list_boards()
    elif args.list_seedable:
        logger.debug("Listing Seedables")
        list_seedable()
    elif args.check_env:
        logger.debug("Checking Environment")
        check_env(args.toolchain)
    else:
        argument_errors = []
        if args.board is None:
            argument_errors.append('--board argument required')
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
        run(
            args.board,
            args.toolchain,
            args.project,
            params_file=args.params_file,
            params_string=args.params_string,
            out_dir=args.out_dir,
            out_prefix=args.out_prefix,
            overwrite=args.overwrite,
            verbose=args.verbose,
            strategy=args.strategy,
            carry=args.carry,
            seed=seed,
            build=args.build,
            build_type=args.build_type
        )


if __name__ == '__main__':
    main()
