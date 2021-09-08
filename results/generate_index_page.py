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

from typing import List

import jinja2

from project_results import ProjectResults


def generate_index_html(
    template: jinja2.Template, results: List[ProjectResults]
):
    print('Generating index page...')

    projects_dict = {}
    all_toolchains = set()
    for project_results in results:
        boards = {}
        for board, toolchains in project_results.entries.items():
            board_toolchains = []
            for toolchain in toolchains.keys():
                board_toolchains.append(toolchain)
                all_toolchains.add(toolchain)
            boards[board] = board_toolchains

        projects_dict[project_results.project_name] = boards

    projects_list = sorted(list(projects_dict.items()), key=lambda t: t[0])
    toolchain_list = sorted(list(all_toolchains))

    return template.render(projects=projects_list, toolchains=toolchain_list)
