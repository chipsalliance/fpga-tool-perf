#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2021  The SymbiFlow Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

import json
import os
from typing import List

import jinja2

from project_results import ProjectResults
from infrastructure.tasks import Tasks


def generate_index_html(
    template: jinja2.Template, results: List[ProjectResults]
):
    print('Generating index page...')

    cur_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.join(cur_dir, '..')
    tasks = Tasks(root_dir)
    combinations = sorted(
        tasks.get_all_combinations(), key=lambda tup: (tup[2], tup[0], tup[1])
    )

    boards = dict()
    toolchains_dict = dict()
    projects = set()
    for project, toolchain, board in combinations:
        if board not in boards:
            boards[board] = dict()

        board_dict = boards[board]
        if project not in board_dict:
            board_dict[project] = dict()

        proj_dict = board_dict[project]

        proj_dict[toolchain] = "skip"

        if board not in toolchains_dict:
            toolchains_dict[board] = set()

        toolchains_dict[board].add(toolchain)

        projects.add(project)

    for project_results in results:
        entries = project_results.entries
        project = project_results.project_name

        for board, toolchains in entries.items():
            for toolchain in toolchains.keys():
                status = entries[board][toolchain][0].status
                boards[board][project][toolchain] = status

    for board, tool_list in toolchains_dict.items():
        toolchains_dict[board] = sorted(list(tool_list))

    return template.render(
        boards=boards,
        boards_list=list(boards.keys()),
        toolchains=toolchains_dict,
        projects=projects
    )
