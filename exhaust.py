#!/usr/bin/env python3

import json
import multiprocessing as mp

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
    return matching_pattern(src_dir + '/' + project + '/*/', '.*\/(.*)\/$')


def get_devices(project, family):
    return matching_pattern(
        src_dir + '/' + project + '/' + family + '/*/',
        '.*\/([^/_]*)(?:_?)(?:[^/_]*)\/$'
    )


def get_packages(project, family, device):
    return matching_pattern(
        src_dir + '/' + project + '/' + family + '/' + device + '*/',
        '.*\/(?:[^/_]*' + device + ')(?:_?)([^/_]*)\/$'
    )


def get_reports(out_prefix):
    return matching_pattern(
        root_dir + '/' + out_prefix + '/*/meta.json', '(.*)'
    )


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
                        yield project, family, device, package, toolchain


def worker(arglist):
    out_prefix, verbose, project, family, device, package, toolchain = arglist
    run(
        family,
        device,
        package,
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
    for project, family, device, package, toolchain in iter_options(args):
        constraints = get_constraints(
            project, family, device, package, toolchain
        )

        if toolchain not in MANDATORY_CONSTRAINTS.keys():
            continue

        for mandatory_constraint in MANDATORY_CONSTRAINTS[toolchain]:
            if constraints[mandatory_constraint] is not None:
                task = (
                    args.out_prefix, args.verbose, project, family, device,
                    package, toolchain
                )
                tasks.append(task)
                break

    with mp.Pool(mp.cpu_count()) as pool:
        pool.map(worker, tasks)

    # Combine results of all tests
    print('Merging results')
    merged_dict = {}

    for report in get_reports(args.out_prefix):
        sow.merge(merged_dict, json.load(open(report, 'r')))

    fout = open('{}/all.json'.format(args.out_prefix), 'w')
    json.dump(merged_dict, fout, indent=4, sort_keys=True)


if __name__ == '__main__':
    main()
