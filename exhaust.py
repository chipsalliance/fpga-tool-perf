#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2020  The SymbiFlow Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

import json
import os
import glob
import time
import re
import logging
from terminaltables import AsciiTable
from termcolor import colored
from multiprocessing import cpu_count

from utils.utils import safe_get_dict_value

from infrastructure.tasks import Tasks
from infrastructure.runner import Runner
from infrastructure.tool_parameters import ToolParametersHelper
from fpgaperf import get_projects, get_toolchains, get_boards

root_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = root_dir + '/src'

logger = logging.getLogger(__name__)


def get_builds(out_prefix):
    """Returns all the paths of all the builds in the build directory."""
    build_dir = os.path.join(root_dir, out_prefix)
    builds = []
    for content in os.listdir(build_dir):
        if os.path.isdir(os.path.join(build_dir, content)):
            builds.append(content)

    return builds


def print_summary_table(
    out_prefix,
    project,
    toolchain,
    board,
    build_type,
    required_task_list,
    build_nr=None
):
    """Prints a summary table of the outcome of each test."""
    builds = get_builds(out_prefix)
    table_data = [
        [
            'Project', 'Toolchain', 'Family', 'Part', 'Board', 'Build Type',
            'Build N.', 'Options'
        ]
    ]
    passed = failed = 0
    build_status = True
    build_count = 0
    failed_required_tests = []
    for build in sorted(builds):
        # Split directory name into columns
        # Example: oneblink_vpr_xc7_a35tcsg326-1_arty_generic-build_0_options
        pattern = ''
        for i in range(0, len(table_data[0]) - 1):
            pattern += '([^_]*)_'
        pattern += '(.*)'

        row = list(re.match(pattern, build).groups())

        is_required = (row[0], row[1], row[4]) in required_task_list

        if build_type != row[5] or (build_nr and int(build_nr) != int(row[6])):
            continue
        if project and row[0] not in project:
            continue
        if toolchain and row[1] not in toolchain:
            continue
        if board and row[4] not in board:
            continue

        # Check if metadata was generated
        # It is created for successful builds only
        with open(os.path.join(root_dir, out_prefix, build, 'meta.json')) as meta:
            meta_data = json.load(meta)
            if meta_data["status"] == "succeeded":
                row.append(colored('passed', 'green'))
                passed += 1
            else:
                assert meta_data["status"] == "failed"
                if is_required:
                    row.append(colored('failed', 'red'))

                    build_status = False
                    failed_required_tests.append(
                        "{} {} {}".format(row[0], row[1], row[4])
                    )
                else:
                    row.append(colored('allowed to fail', 'blue'))

                failed += 1

        table_data.append(row)
        build_count += 1

    table_data.append(
        [
            colored('Total Runs:', 'blue'), build_count,
            colored('Passed:', 'green'), passed,
            colored('Failed:', 'red'), failed, '', '', '{}%'.
            format(int(passed / build_count * 100) if build_count != 0 else 0)
        ]
    )
    table = AsciiTable(table_data)
    table.inner_footing_row_border = True
    print(table.table)

    return build_status, failed_required_tests


def parse_args():
    import argparse
    parser = argparse.ArgumentParser(
        description='Exhaustively try project-toolchain-board combinations'
    )
    parser.add_argument(
        '--project',
        default=None,
        nargs="+",
        choices=get_projects(),
        help='run given project(s) only (default: all)'
    )
    parser.add_argument(
        '--toolchain',
        default=None,
        nargs="+",
        choices=get_toolchains(),
        help='run given toolchain(s) only (default: all)'
    )
    parser.add_argument(
        '--board',
        default=None,
        nargs='+',
        choices=get_boards(),
        help='run given board(s) only (default: all)'
    )
    parser.add_argument(
        '--out-prefix',
        default='build/_exhaust-runs',
        help='output directory prefix (default: build/_exhaust-runs)'
    )
    parser.add_argument(
        '--build_type',
        default='generic',
        help=
        'Type of build that is performed (e.g. regression test, multiple options, etc.)'
    )
    parser.add_argument('--build', default=0, help='Build number')
    parser.add_argument(
        '--parameters', default=None, help='Tool parameters json file'
    )
    parser.add_argument(
        '--seed', default=None, help='Seed to assign when running the tools'
    )
    parser.add_argument(
        '--run_config',
        default=None,
        help="Run configuration file in JSON format."
    )
    parser.add_argument('--fail', action='store_true', help='fail on error')
    parser.add_argument(
        '--verbose', action='store_true', help='verbose output'
    )
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='deletes previous exhuast builds before running'
    )
    parser.add_argument(
        '--only_required',
        action='store_true',
        help='runs only test/board/toolchain combinations that should pass'
    )
    parser.add_argument(
        '--num-cpu',
        default=cpu_count(),
        type=int,
        help='Number of CPUs to use in parallel to run the tests'
    )

    return parser.parse_args()


def main():
    args = parse_args()

    if args.verbose:
        global logger
        logger = logging.getLogger('MyLogger')
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
    logger.debug("Parsing Arguments")

    tasks = Tasks(src_dir)

    assert args.run_config is None or args.run_config and not (
        args.project or args.toolchain
    )

    args_dict = dict()
    seeds = list()
    if args.run_config:
        with open(args.run_config, 'r') as f:
            run_config = json.load(f)
            project = safe_get_dict_value(run_config, "project", None)
            toolchain = safe_get_dict_value(run_config, "toolchain", None)
            seeds = [
                int(i) for i in safe_get_dict_value(run_config, "seeds", [0])
            ]
            build_numbers = [
                int(i)
                for i in safe_get_dict_value(run_config, "build_number", [0])
            ]

            args_dict = {
                "project": project,
                "toolchain": toolchain,
                "board": args.board
            }

    else:
        args_dict = {
            "project": args.project,
            "toolchain": args.toolchain,
            "board": args.board
        }
        seeds = [int(args.seed)] if args.seed else [0]
        build_numbers = [int(args.build)] if args.build else [0]

    params_file = args.parameters
    params_strings = [None]
    if params_file:
        params_strings = []
        assert len(
            args.toolchain
        ) == 1, "A single toolchain can be selected when running multiple params."

        params_helper = ToolParametersHelper(args.toolchain[0], params_file)
        for params in params_helper.get_all_params_combinations():
            params_strings.append(" ".join(params))

    logger.debug("Getting Tasks")
    required_task_list = tasks.get_tasks(
        args_dict, seeds, build_numbers, params_strings, True
    )
    required_task_list = [
        (task[0], task[1], task[2]) for task in required_task_list
    ]
    task_list = tasks.get_tasks(
        args_dict, seeds, build_numbers, params_strings, args.only_required
    )

    num_cpu = min(args.num_cpu, cpu_count())

    runner = Runner(
        task_list, args.verbose, args.out_prefix, root_dir, args.build_type,
        build_numbers, args.overwrite, num_cpu
    )

    logger.debug("Running Projects")
    runner.run()

    logger.debug("Merging results data")
    runner.merge_results()

    logger.debug("Printing Summary Table")
    result, failed_required_tests = print_summary_table(
        args.out_prefix, args.project, args.toolchain, args.board,
        args.build_type, required_task_list, args.build
    )

    if not result and args.fail:
        print("ERROR: Some required tests have failed.")
        for failed_required_test in failed_required_tests:
            print(failed_required_test)

        exit(1)


if __name__ == '__main__':
    main()
