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

import os
from typing import List

import jinja2

from project_results import ProjectResults
from infrastructure.tasks import Tasks
from fpgaperf import get_boards


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

    devices = dict()
    toolchains_dict = dict()
    projects = set()

    all_boards = get_boards()

    for project, toolchain, board in combinations:
        board = all_boards[board]
        device = f"{board['family']}-{board['device']}"
        device = device.upper()

        if device not in devices:
            devices[device] = dict()

        device_dict = devices[device]
        if project not in device_dict:
            device_dict[project] = dict(all_failed=True)

        proj_dict = device_dict[project]

        proj_dict[toolchain] = "skip"

        if device not in toolchains_dict:
            toolchains_dict[device] = set()

        toolchains_dict[device].add(toolchain)

        projects.add(project)

    for project_results in results:
        entries = project_results.entries
        project = project_results.project_name

        for device, toolchains in entries.items():
            all_failed = True
            for toolchain in toolchains.keys():
                status = entries[device][toolchain][0].status
                devices[device][project][toolchain] = status

                all_failed &= status != "succeeded"

            devices[device][project]["all_failed"] = all_failed

    # Remove project entry if all tests are skipped
    del_proj = set()
    for device, prjs in devices.items():
        for project, toolchains in prjs.items():
            if all([v == "skip" or k == "all_failed"
                    for k, v in toolchains.items()]):
                del_proj.add((device, project))

    for d, p in del_proj:
        del devices[d][p]

    for device, tool_list in toolchains_dict.items():
        toolchains_dict[device] = sorted(list(tool_list))

    return template.render(
        devices=devices,
        devices_list=sorted(devices),
        toolchains=toolchains_dict,
        projects=sorted(projects)
    )
