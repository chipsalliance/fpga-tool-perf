#!/usr/bin/env python3

import json

from fpgaperf import *
import sow

# to find data files
root_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = root_dir + '/src'


def get_families(project):
    return matching_pattern(
        src_dir + '/' + project + '/*/',
        '.*\/(.*)\/$'
    )


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
        root_dir + '/' + out_prefix + '/*/meta.json',
        '(.*)'
    )


def user_selected(option):
    return [option] if option else None


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description=
        'Exhaustively try project-toolchain combinations'
    )
    parser.add_argument('--family', default=None, help='device family')
    parser.add_argument('--device', default=None, help='device')
    parser.add_argument('--package', default=None, help='device package')
    parser.add_argument('--project', default=None, help='run given project only (default: all)')
    parser.add_argument('--toolchain', default=None, help='run given toolchain only (default: all)')
    parser.add_argument('--out-prefix', default='build', help='output directory prefix (default: build)')
    parser.add_argument('--dry', action='store_true', help='print commands, don\'t invoke')
    parser.add_argument('--fail', action='store_true', help='fail on error')
    parser.add_argument('--verbose', action='store_true', help='verbose output')
    args = parser.parse_args()

    print('Running exhaustive project-toolchain search')

    # Always check if given option was overriden by user's argument
    # if not - run all available tests
    for project in user_selected(args.project) or get_projects():

        for toolchain in user_selected(args.toolchain) or get_toolchains():

            for family in user_selected(args.family) or get_families(project):

                for device in user_selected(args.device) or get_devices(project, family):

                    for package in user_selected(args.package) or get_packages(project, family, device):
                        # Only run a test if PCF constraint file is present
                        # the other (SDC, XDC) files are optional
                        if(get_pcf(project, family, device, package, toolchain) is not None):
                            run(
                                family,
                                device,
                                package,
                                toolchain,
                                project,
                                None, #out_dir
                                args.out_prefix,
                                None, #strategy
                                None, #carry
                                None, #seed
                                None, #build
                                args.verbose
                            )

    # Combine results of all the tests
    # Combine results of all tests
    print('Merging results')
    merged_dict = {}

    for report in get_reports(args.out_prefix):
        sow.merge(merged_dict, json.load(open(report, 'r')))

    fout = open('all.json', 'w')
    json.dump(merged_dict, fout)

if __name__ == '__main__':
    main()


