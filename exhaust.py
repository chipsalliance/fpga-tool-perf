#!/usr/bin/env python3

import json
import os
import glob
import time
import re
import pathlib
import logging
from terminaltables import AsciiTable
from colorclass import Color

from tasks import Tasks
from runner import Runner
from tool_parameters import ToolParametersHelper

root_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = root_dir + '/src'


def get_builds(out_prefix):
    """Returns all the paths of all the builds in the build directory."""
    build_dir = os.path.join(root_dir, out_prefix)
    builds = []
    for content in os.listdir(build_dir):
        if os.path.isdir(os.path.join(build_dir, content)):
            builds.append(content)

    return builds


def print_summary_table(out_prefix, build_type, build_nr=None):
    """Prints a summary table of the outcome of each test."""
    builds = get_builds(out_prefix)
    table_data = [
        [
            'Project', 'Toolchain', 'Family', 'Part', 'Board', 'Build Type',
            'Build N.', 'Options'
        ]
    ]
    passed = failed = 0
    build_count = 0
    for build in sorted(builds):
        # Split directory name into columns
        # Example: oneblink_vpr_xc7_a35tcsg326-1_arty_generic-build_0_options
        pattern = ''
        for i in range(0, len(table_data[0]) - 1):
            pattern += '([^_]*)_'
        pattern += '(.*)'

        row = list((re.match(pattern, build)).groups())

        if build_type != row[5] or (build_nr and int(build_nr) != int(row[6])):
            continue

        # Check if metadata was generated
        # It is created for successful builds only
        if os.path.exists(os.path.join(root_dir, out_prefix, build,
                                       'meta.json')):
            row.append(Color('{autogreen}passed{/autogreen}'))
            passed += 1
        else:
            row.append(Color('{autored}failed{/autored}'))
            failed += 1
        table_data.append(row)
        build_count += 1

    table_data.append(
        [
            Color('{autogreen}Passed:{/autogreen}'), passed,
            Color('{autored}Failed:{/autored}'), failed, '', '', '', '',
            '{}%'.format(int(passed / build_count * 100))
        ]
    )
    table = AsciiTable(table_data)
    table.inner_footing_row_border = True
    print(table.table)

    return failed == 0


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Exhaustively try project-toolchain combinations'
    )
    parser.add_argument(
        '--project',
        default=None,
        nargs="+",
        help='run given project only (default: all)'
    )
    parser.add_argument(
        '--toolchain',
        default=None,
        nargs="+",
        help='run given toolchain only (default: all)'
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
    parser.add_argument('--build', default=None, help='Build number')
    parser.add_argument(
        '--parameters', default=None, help='Tool parameters json file'
    )
    parser.add_argument('--fail', action='store_true', help='fail on error')
    parser.add_argument(
        '--verbose', action='store_true', help='verbose output'
    )

    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(format='%(message)s', level=logging.INFO)
    logging.info("Parsing Arguments........")

    tasks = Tasks(src_dir)

    args_dict = {"project": args.project, "toolchain": args.toolchain}

    logging.info("\nGetting Tasks............")
    task_list = tasks.get_tasks(args_dict)

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

    runner = Runner(
        task_list, args.verbose, args.out_prefix, root_dir, args.build_type,
        args.build, params_strings
    )
    logging.info("\nRunning Project..........") 
    runner.run()
    logging.info("\nCollecting Results.......")
    runner.collect_results()

    logging.info("\nPrinting Summary Table...")
    result = print_summary_table(args.out_prefix, args.build_type, args.build)

    if not result and args.fail:
        print("ERROR: some tests have failed.")
        exit(1)


if __name__ == '__main__':
    main()
