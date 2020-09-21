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

from fpgaperf import get_projects, get_project, get_toolchains, get_constraint, get_vendors, verify_constraint


class Tasks:
    """Class to generate and hold the task lists that needs to be run
    exhaustively by FPGA tool perf."""
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.src_dir = os.path.join(root_dir, 'src')
        self.tasks = self.iter_options()

    def iter_options(self):
        """Returns all the possible combination of:
            - projects,
            - toolchains,
            - boards.

        Example:
        - path structure:    src/<project>/constr/<board>.<constraint>
        - valid combination: src/oneblink/constr/arty.pcf
        """

        combinations = set()

        vendors = get_vendors()
        for project in get_projects():
            project_dict = get_project(project)

            for vendor in project_dict["vendors"]:
                toolchains = vendors[vendor]["toolchains"]
                boards = vendors[vendor]["boards"]

                for toolchain, board in list(product(toolchains, boards)):
                    combinations.add((project, toolchain, board))

        return combinations

    def get_tasks(
        self,
        args,
        seeds=[0],
        build_number=[0],
        options=[None],
        only_required=False
    ):
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
                if only_required:
                    required = get_project(task[0])["required_working"]
                    try:
                        if task[2] in required[task[1]]:
                            tasks.append(task)
                    except:
                        continue
                else:
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
