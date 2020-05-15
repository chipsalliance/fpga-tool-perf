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
import sys
import tqdm
from multiprocessing import Pool, cpu_count
from contextlib import redirect_stdout

from fpgaperf import run


class Runner:
    """Class to create a runner object that, given a list of tasks
    runs all of them parallely.
    """
    def __init__(self, task_list, verbose, out_prefix, options=[None]):
        self.verbose = verbose
        self.out_prefix = out_prefix

        def add_tuple_to_tasks(tasks, tpl):
            new_tasks = []

            for task in tasks:
                new_tasks.append(task + tpl)

            return new_tasks

        self.task_list = []
        for idx, option in enumerate(options):
            self.task_list += add_tuple_to_tasks(
                task_list, (option, "{:03d}".format(idx))
            )

    def worker(self, arglist):
        """Single worker function that is run in the Pool of workers.

        This takes, as argument list, the various tasks to perform.
        """
        def eprint(*args, **kwargs):
            print(*args, file=sys.stderr, **kwargs)

        project, toolchain, family, device, package, board, option, build = arglist

        # We don't want output of all subprocesses here
        # Log files for each build will be placed in build directory
        with redirect_stdout(open(os.devnull, 'w')):
            try:
                run(
                    family,
                    device,
                    package,
                    board,
                    toolchain,
                    project,
                    None,  #options_file
                    option,
                    None,  #out_dir
                    self.out_prefix,
                    self.verbose,
                    None,  #strategy
                    None,  #seed
                    None,  #carry
                    build,
                )
            except Exception as e:
                eprint("\n---------------------")
                eprint(
                    "ERROR: {} {} {}{}{} {} test has failed\n".format(
                        project, toolchain, family, device, package, board
                    )
                )
                eprint("ERROR MESSAGE: ", e)
                eprint("---------------------\n")

    def run(self):
        if not os.path.exists(self.out_prefix):
            os.mkdir(self.out_prefix)

        with Pool(cpu_count()) as pool:
            for _ in tqdm.tqdm(pool.imap_unordered(self.worker,
                                                   self.task_list),
                               total=len(self.task_list), unit='test'):
                pass
