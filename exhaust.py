#!/usr/bin/env python3

from fpgaperf import *

families = [
    'xc7'
]

devices = [
    'a35t',
    'z010'
]

packages = [
    'cpg236-1',
    'csg324-1',
    'clg400-1'
]

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description=
        'Exhaustively try project-toolchain combinations'
    )
    parser.add_argument('--family', default='all', help='device family')
    parser.add_argument('--device', default='all', help='device')
    parser.add_argument('--package', default='all', help='device package')
    parser.add_argument('--project', default='all', help='run given project only (default: all)')
    parser.add_argument('--toolchain', default='all', help='run given toolchain only (default: all)')
    parser.add_argument('--out-prefix', default='build', help='output directory prefix (default: build)')
    parser.add_argument('--dry', action='store_true', help='print commands, don\'t invoke')
    parser.add_argument('--fail', action='store_true', help='fail on error')
    parser.add_argument('--verbose', action='store_true', help='verbose output')
    args = parser.parse_args()

    print('Running exhaustive project-toolchain search')

    if(args.project != "all"):
        # Only specified project
        selected_projects = [args.project]
    else:
        # All projects
        selected_projects = get_projects()

    if(args.toolchain != "all"):
        selected_toolchains = [args.toolchain]
    else:
        selected_toolchains = get_toolchains()

    if(args.family != "all"):
        selected_families = [args.familes]
    else:
        selected_families = families

    if(args.device != "all"):
        selected_devices = [args.device]
    else:
        selected_devices = devices

    if(args.package != "all"):
        selected_packages = [args.package]
    else:
        selected_packages = packages


    for project in selected_projects:
        for toolchain in selected_toolchains:
            for family in selected_families:
                for device in selected_devices:
                    for package in selected_packages:
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

if __name__ == '__main__':
    main()


