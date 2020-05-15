#!/usr/bin/env python3

import json
import os
import glob
import time
import re
from terminaltables import AsciiTable
from colorclass import Color
from itertools import product

from fpgaperf import run, matching_pattern
import sow
import pandas
from dataframe import generate_dataframe
from tasks import Tasks
from runner import Runner

root_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = root_dir + '/src'


def get_reports(out_prefix):
    """Returns all the reports from all the build runs."""
    return matching_pattern(
        os.path.join(root_dir, out_prefix, '*/meta.json'), '(.*)'
    )


def get_builds(out_prefix):
    """Returns all the paths of all the builds in the build directory."""
    build_dir = os.path.join(root_dir, out_prefix)
    builds = []
    for content in os.listdir(build_dir):
        if os.path.isdir(os.path.join(build_dir, content)):
            builds.append(content)

    return builds


def print_summary_table(out_prefix, total_tasks):
    """Prints a summary table of the outcome of each test."""
    builds = get_builds(out_prefix)
    table_data = [
        [
            'Project', 'Toolchain', 'Family', 'Part', 'Board', 'Build N.',
            'Options'
        ]
    ]
    passed = failed = 0
    for build in sorted(builds):
        # Split directory name into columns
        # Example: oneblink_vpr_xc7_a35tcsg326-1_arty_options
        pattern = '([^_]*)_([^_]*)_([^_]*)_([^_]*)_([^_]*)_([^_]*)_(.*)'
        row = list(re.match(pattern, build).groups())
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

    table_data.append(
        [
            Color('{autogreen}Passed:{/autogreen}'), passed,
            Color('{autored}Failed:{/autored}'), failed, '', '',
            '{}%'.format(int(passed / total_tasks * 100))
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
        default='build',
        help='output directory prefix (default: build)'
    )
    parser.add_argument('--fail', action='store_true', help='fail on error')
    parser.add_argument(
        '--verbose', action='store_true', help='verbose output'
    )
    args = parser.parse_args()

    tasks = Tasks(src_dir)

    args_dict = {"project": args.project, "toolchain": args.toolchain}

    task_list = tasks.get_tasks(args_dict)

    runner = Runner(task_list, args.verbose, args.out_prefix)
    runner.run()

    # Combine results of all tests
    print('Merging results')
    merged_dict = {}

    for report in get_reports(args.out_prefix):
        sow.merge(merged_dict, json.load(open(report, 'r')))

    with open('{}/all.json'.format(args.out_prefix), 'w') as fout:
        json.dump(merged_dict, fout, indent=4, sort_keys=True)

    dataframe = generate_dataframe(merged_dict)
    dataframe = dataframe.reset_index(drop=True)
    dataframe.to_json('{}/dataframe.json'.format(args.out_prefix))

    result = print_summary_table(args.out_prefix, len(task_list))

    if not result and args.fail:
        print("ERROR: some tests have failed.")
        exit(1)


if __name__ == '__main__':
    main()
