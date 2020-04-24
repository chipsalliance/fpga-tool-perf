#!/usr/bin/env python3

import json
import os
import glob
import multiprocessing as mp
import time
import re
import tqdm
from contextlib import redirect_stdout
from terminaltables import SingleTable
from colorclass import Color
from itertools import product

from fpgaperf import *
import sow

MANDATORY_CONSTRAINTS = {
    "vivado": "xdc",
    "vpr": "pcf",
    "vivado-yosys": "xdc",
    "nextpnr": "xdc",
}

# to find data files
root_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = root_dir + '/src'


def get_reports(out_prefix):
    """Returns all the reports from all the build runs."""
    return matching_pattern(
        os.path.join(root_dir, out_prefix, '*/meta.json'), '(.*)'
    )


def get_builds(out_prefix):
    """Returns all the paths of all the builds in the build directory."""
    return matching_pattern(
        os.path.join(root_dir, out_prefix, '*/'), '.*\/(.*)\/$'
    )


def print_summary_table(out_prefix, total_tasks):
    """Prints a summary table of the outcome of each test."""
    builds = get_builds(out_prefix)
    table_data = [
        ['Project', 'Toolchain', 'Family', 'Part', 'Board', 'Options']
    ]
    passed = failed = 0
    for build in builds:
        # Split directory name into columns
        # Example: oneblink_vpr_xc7_a35tcsg326-1_arty_options
        pattern = '([^_]*)_([^_]*)_([^_]*)_([^_]*)_([^_]*)_(.*)'
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


def get_device_info(constraint):
    """Returns the device information:
        - FPGA family
        - FPGA part
        - board
    """
    full_info = os.path.splitext(constraint)[0]
    return full_info.split('_')


def user_selected(option):
    return [option] if option else None


def iter_options(args):
    """Returns all the possible combination of:
        - projects,
        - toolchains,
        - families,
        - devices,
        - packages
        - boards.

    Example:
    - path structure:    src/<project>/<toolchain>/<family>_<device>_<package>_<board>.<constraint>
    - valid combination: src/oneblink/vpr/xc7_a35t_csg324-1_arty.pcf
    """

    projects = user_selected(args.project) or get_projects()
    toolchains = user_selected(args.toolchain) or get_toolchains()

    combinations = set()
    for project, toolchain in list(product(projects, toolchains)):
        constraint_path = os.path.join(src_dir, project, 'constr', toolchain)

        if not os.path.exists(constraint_path):
            continue

        for constraint in os.listdir(constraint_path):
            family, device, package, board = get_device_info(constraint)
            combinations.add(
                (project, toolchain, family, device, package, board)
            )

    return combinations


def worker(arglist):
    out_prefix, verbose, project, family, device, package, board, toolchain = arglist
    # We don't want output of all subprocesses here
    # Log files for each build will be placed in build directory
    with redirect_stdout(open(os.devnull, 'w')):
        run(
            family,
            device,
            package,
            board,
            toolchain,
            project,
            None,  #out_dir
            out_prefix,
            None,  #strategy
            None,  #carry
            None,  #seed
            None,  #build
            verbose
        )


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='Exhaustively try project-toolchain combinations'
    )
    parser.add_argument('--family', default=None, help='device family')
    parser.add_argument('--part', default=None, help='device part')
    parser.add_argument('--board', default=None, help='target board')
    parser.add_argument(
        '--project',
        default=None,
        help='run given project only (default: all)'
    )
    parser.add_argument(
        '--toolchain',
        default=None,
        help='run given toolchain only (default: all)'
    )
    parser.add_argument(
        '--out-prefix',
        default='build',
        help='output directory prefix (default: build)'
    )
    parser.add_argument(
        '--dry', action='store_true', help='print commands, don\'t invoke'
    )
    parser.add_argument('--fail', action='store_true', help='fail on error')
    parser.add_argument(
        '--verbose', action='store_true', help='verbose output'
    )
    args = parser.parse_args()

    print('Running exhaustive project-toolchain search')

    tasks = []

    # Always check if given option was overriden by user's argument
    # if not - run all available tests
    combinations = iter_options(args)
    for project, toolchain, family, device, package, board in combinations:
        if toolchain not in MANDATORY_CONSTRAINTS.keys():
            continue

        mandatory_constraint = MANDATORY_CONSTRAINTS[toolchain]
        constraint = "_".join((family, device, package, board)
                              ) + ".{}".format(mandatory_constraint)
        constraint_path = os.path.join(
            src_dir, project, 'constr', toolchain, constraint
        )

        if os.path.exists(constraint_path):
            task = (
                args.out_prefix, args.verbose, project, family, device,
                package, board, toolchain
            )
            tasks.append(task)

    assert len(tasks), "No tasks to run!"

    if not os.path.exists(args.out_prefix):
        os.mkdir(args.out_prefix)

    with mp.Pool(mp.cpu_count()) as pool:
        for _ in tqdm.tqdm(pool.imap_unordered(worker, tasks),
                           total=len(tasks), unit='test'):
            pass

    # Combine results of all tests
    print('Merging results')
    merged_dict = {}

    for report in get_reports(args.out_prefix):
        sow.merge(merged_dict, json.load(open(report, 'r')))

    fout = open('{}/all.json'.format(args.out_prefix), 'w')
    json.dump(merged_dict, fout, indent=4, sort_keys=True)

    result = print_summary_table(args.out_prefix, len(tasks))

    if not result:
        print("ERROR: some tests have failed.")
        exit(1)


if __name__ == '__main__':
    main()
