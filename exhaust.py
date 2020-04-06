#!/usr/bin/env python3

import json
import os
import glob
import multiprocessing as mp
import progressbar as pb
import time
import re
from contextlib import redirect_stdout
from terminaltables import SingleTable
from colorclass import Color

from fpgaperf import *
import sow

MANDATORY_CONSTRAINTS = {
    "vivado": ["xdc"],
    "vpr": ["pcf"],
}

# to find data files
root_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = root_dir + '/src'


def get_families(project):
    """Returns all the FPGA families related to a project.

    Example:
        - project content:
            src/oneblink/xc7
            src/oneblink/ice40

        - return value: ['xc7', 'ice40']
    """
    return matching_pattern(
        os.path.join(src_dir, project, '*/'), '.*\/(.*)\/$'
    )


def get_devices(project, family):
    """Returns all the FPGA devices related to a project and
    an FPGA family.

    Example:
        - FPGA family content:
            src/oneblink/xc7/a35t_csg324-1
            src/oneblink/xc7/z010_clg400-1

        - return value: ['a35t', 'z010']
    """
    return matching_pattern(
        os.path.join(src_dir, project, family, '*/'),
        '.*\/([^/_]*)(?:_?)(?:[^/_]*)\/$'
    )


def get_packages(project, family, device):
    """Returns all the device packages related to a project,
    an FPGA family and a device.

    Example:
        - FPGA family content:
            src/oneblink/xc7/a35t_csg324-1
            src/oneblink/xc7/a35t_cpg236-1

        - return value: ['csg324-1', 'cpg236-1']
    """
    return matching_pattern(
        os.path.join(src_dir, project, family, "{}*/".format(device)),
        '.*\/(?:[^/_]*' + device + ')(?:_?)([^/_]*)\/$'
    )


def get_boards(project, family, device, package):
    """Returns all the boards related to a project, an FPGA family,
    a device and a package.

    Example:
        - device and package content:
            src/oneblink/xc7/a35t_csg324-1/arty

        - return value: ['arty']
    """
    boards = glob.glob(
        os.path.join(
            src_dir, project, family, "{}_{}/*".format(device, package)
        )
    )
    return sorted([board.split('/')[-1] for board in boards])


def get_reports(out_prefix):
    """Returns all the reports from all the build runs."""
    return matching_pattern(
        os.path.join(root_dir, out_prefix, '/*/meta.json'), '(.*)'
    )


def get_builds(out_prefix):
    """Returns all the paths of all the builds in the build directory."""
    return matching_pattern(
        os.path.join(root_dir, out_prefix, '/*/'), '.*\/(.*)\/$'
    )


def print_summary_table(out_prefix):
    """Prints a summary table of the outcome of each test."""
    builds = get_builds(out_prefix)
    table_data = [
        [
            'Family', 'Device', 'Package', 'Board', 'Toolchain', 'Project',
            'Result'
        ]
    ]
    passed = failed = 0
    for build in builds:
        # Split directory name into columns
        # Example: xc7_a35t_csg326_arty_vpr_oneblink
        pattern = '([^-]*)-([^-]*)-([^_]*)-([^_]*)_([^_]*)_([^_]*)_.*'
        row = list(re.match(pattern, build).groups())
        # Check if metadata was generated
        # It is created for successful builds only
        if os.path.exists(os.path.join(root_dir, out_prefix, build,
                                       '/meta.json')):
            row.append(Color('{autogreen}passed{/autogreen}'))
            passed += 1
        else:
            row.append(Color('{autored}failed{/autored}'))
            failed += 1
        table_data.append(row)
    table_data.append(
        [
            Color('{autogreen}Passed:{/autogreen}'), passed,
            Color('{autored}Failed:{/autored}'), failed
        ]
    )
    table = SingleTable(table_data)
    table.inner_footing_row_border = True
    print(table.table)


def user_selected(option):
    return [option] if option else None


def iter_options(args):
    for project in user_selected(args.project) or get_projects():
        for toolchain in user_selected(args.toolchain) or get_toolchains():
            for family in user_selected(args.family) or get_families(project):
                for device in user_selected(args.device) or set(get_devices(
                        project, family)):
                    for package in user_selected(args.package) or get_packages(
                            project, family, device):
                        for board in user_selected(args.board) or get_boards(
                                project, family, device, package):
                            yield project, family, device, package, board, toolchain


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
    parser.add_argument('--device', default=None, help='device')
    parser.add_argument('--package', default=None, help='device package')
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
    for project, family, device, package, board, toolchain in iter_options(args
                                                                           ):
        constraints = get_constraints(
            project, family, device, package, board, toolchain
        )

        if toolchain not in MANDATORY_CONSTRAINTS.keys():
            continue

        for mandatory_constraint in MANDATORY_CONSTRAINTS[toolchain]:
            if constraints[mandatory_constraint] is not None:
                task = (
                    args.out_prefix, args.verbose, project, family, device,
                    package, board, toolchain
                )
                tasks.append(task)
                break

    jobs = mp.Pool(mp.cpu_count()).map_async(worker, tasks)
    widget = ['Exhaust progress:\n', pb.SimpleProgress(), pb.Bar()]
    bar = pb.ProgressBar(widgets=widget, maxval=len(tasks)).start()

    while not jobs.ready():
        bar.update(len(tasks) - jobs._number_left)
        time.sleep(1)
    bar.update(len(tasks))

    # Combine results of all tests
    print('Merging results')
    merged_dict = {}

    for report in get_reports(args.out_prefix):
        sow.merge(merged_dict, json.load(open(report, 'r')))

    fout = open('{}/all.json'.format(args.out_prefix), 'w')
    json.dump(merged_dict, fout, indent=4, sort_keys=True)

    print_summary_table(args.out_prefix)


if __name__ == '__main__':
    main()
