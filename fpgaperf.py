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
import edalize
import logging
import importlib
from terminaltables import AsciiTable
from omegaconf import DictConfig, OmegaConf
import hydra
from hydra.core.hydra_config import HydraConfig
from hydra.utils import get_original_cwd

from utils.utils import Timed


logger = logging.getLogger(__name__)


def print_stats(t):
    def print_section_header(title):
        logger.info('')
        logger.info('===============================')
        logger.info(title)
        logger.info('===============================')
        logger.info('')

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
    logger.info('\n' + table.table)

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
    logger.info('\n' + table.table)

    print_section_header('Toolchain Run-Times')
    table_data = [['Stage', 'Run Time (seconds)']]
    for k, v in t.get_runtimes().items():
        value = "%0.3f" % v if v else "N/A"
        table_data.append([k, value])

    table = AsciiTable(table_data)
    logger.info('\n' + table.table)

    print_section_header('FPGA resource utilization')
    table_data = [['Resource', 'Used']]

    for k, v in sorted(t.resources().items()):
        value = v if v else "N/A"
        table_data.append([k, value])

    table = AsciiTable(table_data)
    logger.info('\n' + table.table)


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
    project_name, project_info = project
    board_name, board_info = board
    family = board_info['family']
    device = board_info['device']
    package = board_info['package']

    assert family == 'ice40' or family == 'xc7' or family == 'eos'

    # some toolchains use signed 32 bit
    assert seed is None or 0 <= seed <= 0x7FFFFFFF
    tc_name, tc = toolchain
    tool_class = getattr(
        importlib.import_module(tc['module']), tc['class'])
    t = tool_class(get_original_cwd())
    t.verbose = verbose
    t.strategy = strategy

    if t.seedable():
        t.seed = seed

    t.carry = carry

    # Constraint files shall be in their directories
    logger.debug("Getting Constraints")
    pcf = get_constraint(project_name, board_name, tc_name, 'pcf')
    sdc = get_constraint(project_name, board_name, tc_name, 'sdc')
    xdc = get_constraint(project_name, board_name, tc_name, 'xdc')

    # XXX: sloppy path handling here...
    t.pcf = os.path.realpath(pcf) if pcf else None
    t.sdc = os.path.realpath(sdc) if sdc else None
    t.xdc = os.path.realpath(xdc) if xdc else None
    t.build = build
    t.build_type = build_type
    logger.debug("Running Project")
    t.project(
        project_info,
        family,
        device,
        package,
        board_name,
        board_info['vendor'],
        params_file,
        params_string,
        out_dir=out_dir,
        out_prefix=out_prefix,
        overwrite=overwrite,
    )
    t.run()
    logger.debug("Printing Stats")
    print_stats(t)
    logger.debug("Writing Metadata")
    t.write_metadata()


def list_combinations(
    project=None,
    toolchain=None,
    board=None,
):
    '''Query all possible project/toolchain/board combinations'''
    table_data = [['Project', 'Toolchain', 'Board', 'Status']]
    for p, p_val in project.items():
        toolchain_info = p_val["required_toolchains"]
        vendor_info = p_val["vendors"]
        for t, t_val in toolchain.items():
            vendor = t_val.vendor
            if vendor not in vendor_info:
                continue
            text = "Supported"
            board_info = vendor_info[vendor]
            if t not in toolchain_info:
                text = "Missing"
            for b, b_val in board.items():
                if b_val.vendor != vendor:
                    continue
                text2 = text
                if board_info is None or b not in board_info:
                    text2 = "Missing"
                row = [p, t, b, text2]
                table_data.append(row)
    table = AsciiTable(table_data)
    print(table.table)


def check_env(cfg):
    '''For each tool, print dependencies and if they are met'''
    for t, tc in sorted(cfg.items()):
        print(t)
        tool_class = getattr(
            importlib.import_module(tc['module']), tc['class'])
        for k, v in tool_class.check_env().items():
            print('  %s: %s' % (k, v))


def get_constraint(project, board, toolchain, extension):
    constr_file = board + "-" + toolchain + "." + extension

    path = os.path.join(get_original_cwd(), 'src',
                        project, 'constr', constr_file)
    if (os.path.exists(path)):
        return path
    constr_file = board + "." + extension

    path = os.path.join(get_original_cwd(), 'src',
                        project, 'constr', constr_file)
    if (os.path.exists(path)):
        return path

    return None


@hydra.main(config_path="conf", config_name="config")
def main(cfg):
    logger.debug("Parsing Arguments")

    assert not (cfg.params_file and cfg.params_string)

    if cfg.list == "combinations":
        logger.debug("Listing Combinations")
        list_combinations(cfg.project, cfg.toolchain, cfg.board)
    elif cfg.list == "toolchains":
        logger.debug("Listing Toolchains")
        [print(key) for key in sorted(cfg.toolchain.keys())]
    elif cfg.list == "projects":
        logger.debug("Listing Projects")
        [print(key) for key in sorted(cfg.project.keys())]
    elif cfg.list == "boards":
        logger.debug("Listing Boards")
        [print(key) for key in sorted(cfg.board.keys())]
    elif cfg.list == "seedable":
        logger.debug("Listing Seedables")
        [print(t) for t, tc in sorted(cfg.toolchain.items())
         if getattr(importlib.import_module(tc['module']), tc['class']).seedable()]
    elif cfg.check == "env":
        logger.debug("Checking Environment")
        check_env(cfg.toolchain)
    else:
        argument_errors = []
        if cfg.board is None:
            argument_errors.append('board argument required')
        if cfg.toolchain is None:
            argument_errors.append('toolchain argument required')
        if cfg.project is None:
            argument_errors.append('project argument required')

        if argument_errors:
            print('Use --help to print usage')
            for e in argument_errors:
                print('{}: error: {}'.format(sys.argv[0], e))
            sys.exit(1)
        seed = int(cfg.seed, 0) if cfg.seed else None

        for p, p_val in cfg.project.items():
            toolchain_info = p_val["required_toolchains"]
            vendor_info = p_val["vendors"]
            for t, t_val in cfg.toolchain.items():
                vendor = t_val.vendor
                if vendor not in vendor_info:
                    continue
                text = "Supported"
                board_info = vendor_info[vendor]
                if t not in toolchain_info:
                    text = "Missing"
                for b, b_val in cfg.board.items():
                    if b_val.vendor != vendor:
                        continue
                    text2 = text
                    if board_info is None or b not in board_info:
                        text2 = "Missing"
                    if text2 == "Supported":
                        run(
                            (b, b_val),
                            (t, t_val),
                            (p, p_val),
                            params_file=cfg.params_file,
                            params_string=cfg.params_string,
                            out_dir=cfg.out_dir,
                            out_prefix=cfg.out_prefix,
                            overwrite=cfg.overwrite,
                            verbose=HydraConfig.get().verbose,
                            strategy=cfg.strategy,
                            carry=cfg.carry,
                            seed=seed,
                            build=cfg.build,
                            build_type=cfg.build_type
                        )
                    else:
                        logger.info(
                            'The given configuration is not supported. \
                                Use list=combinations to find out the \
                                    configurations that are supported.')


if __name__ == '__main__':
    main()
