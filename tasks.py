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
from itertools import product

from fpgaperf import get_projects, get_project, get_toolchains, get_constraint


class Tasks:
    """Class to generate and hold the task lists that needs to be run
    exhaustively by FPGA tool perf."""
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.src_dir = os.path.join(root_dir, 'src')
        self.MANDATORY_CONSTRAINTS = {
            "vivado": "xdc",
            "vpr": "pcf",
            "vpr-fasm2bels": "pcf",
            "vivado-yosys": "xdc",
            "nextpnr-xilinx": "xdc",
            "nextpnr-xilinx-fasm2bels": "xdc",
            "nextpnr-ice40": "pcf",
        }

        self.tasks = self.iter_options()

    def iter_options(self):
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

        projects = get_projects()
        toolchains = get_toolchains()

        combinations = set()
        for project, toolchain in list(product(projects, toolchains)):
            project_dict = get_project(project)

            if 'toolchains' in project_dict:
                toolchains_dict = project_dict['toolchains']
            else:
                continue

            if toolchain not in toolchains_dict:
                continue

            if toolchain not in self.MANDATORY_CONSTRAINTS.keys():
                continue

            for board in toolchains_dict[toolchain]:
                assert get_constraint(
                    project, board, toolchains_dict[toolchain][board],
                    self.MANDATORY_CONSTRAINTS[toolchain]
                )

                combinations.add((project, toolchain, board))

        return combinations

    def get_tasks(self, args, seeds=[0], build_number=[0], options=[None]):
        """Returns all the tasks filtering out the ones that do not correspond
        to the selected criteria"""

        tasks = []

        for task in self.tasks:
            take_task = True
            for arg in args.values():
                if arg is None:
                    continue

                if not any(value in arg for value in task):
                    take_task = False
                    break

            if take_task:
                tasks.append(task)

        tasks = self.add_extra_entry(seeds, tasks, create_new_tasks=True)
        tasks = self.add_extra_entry(options, tasks)
        tasks = self.add_extra_entry(
            build_number, tasks, create_new_tasks=True
        )

        return tasks

    def add_extra_entry(
        self, entries, tasks, with_idx=False, create_new_tasks=False
    ):
        def add_tuple_to_tasks(tasks, tpl):
            new_tasks = []

            for task in tasks:
                new_tasks.append(task + tpl)

            return new_tasks

        task_list = []
        for idx, entry in enumerate(entries):
            if create_new_tasks:
                task_list += add_tuple_to_tasks(tasks, (entry, ))
            else:
                task_list = add_tuple_to_tasks(tasks, (entry, ))

        return task_list
