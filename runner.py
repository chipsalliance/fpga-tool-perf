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
import glob
import json
import pandas
from multiprocessing import Pool, cpu_count
from contextlib import redirect_stdout

from fpgaperf import run
from dataframe import generate_dataframe
import sow


class Runner:
    """Class to create a runner object that, given a list of tasks
    runs all of them parallely.
    """
    def __init__(
        self,
        task_list,
        verbose,
        out_prefix,
        root_dir,
        build_type,
        build=None,
        seed=None,
        options=[]
    ):
        self.verbose = verbose
        self.out_prefix = out_prefix
        self.root_dir = root_dir
        self.build = int(build) if build else None
        self.build_format = "{:03d}"
        self.build_type = build_type
        self.seed = seed
        self.results = dict()

        def add_tuple_to_tasks(tasks, tpl):
            new_tasks = []

            for task in tasks:
                new_tasks.append(task + tpl)

            return new_tasks

        self.task_list = []
        for idx, option in enumerate(options):
            self.task_list += add_tuple_to_tasks(task_list, (option, idx))

    def worker(self, arglist):
        """Single worker function that is run in the Pool of workers.

        This takes, as argument list, the various tasks to perform.
        """
        def eprint(*args, **kwargs):
            print(*args, file=sys.stderr, **kwargs)

        project, toolchain, board, option, build = arglist

        build = self.build_format.format(self.build or build)

        # We don't want output of all subprocesses here
        # Log files for each build will be placed in build directory
        with redirect_stdout(open(os.devnull, 'w')):
            try:
                run(
                    board,
                    toolchain,
                    project,
                    None,  #options_file
                    option,
                    None,  #out_dir
                    self.out_prefix,
                    self.verbose,
                    None,  #strategy
                    self.seed,
                    None,  #carry
                    build,
                    self.build_type,
                )
            except Exception as e:
                eprint("\n---------------------")
                eprint(
                    "ERROR: {} {} {}{}{} {} test has failed (build type {}, build nr. {})\n"
                    .format(project, toolchain, board, self.build_type, build)
                )
                eprint("ERROR MESSAGE: ", e)
                eprint("---------------------\n")

    def run(self):
        if not os.path.exists(self.out_prefix):
            os.makedirs(self.out_prefix)

        with Pool(cpu_count()) as pool:
            for _ in tqdm.tqdm(pool.imap_unordered(self.worker,
                                                   self.task_list),
                               total=len(self.task_list), unit='test'):
                pass

    def get_reports(self):
        reports = []
        if self.build is not None:
            metadata_path = '*{}_{}*/meta.json'.format(
                self.build_type, self.build_format.format(self.build)
            )
        else:
            metadata_path = '*{}*/meta.json'.format(self.build_type)
        for filename in glob.iglob(os.path.join(self.root_dir, self.out_prefix,
                                                metadata_path)):
            reports.append(filename)

        return reports

    def collect_results(self):
        reports = self.get_reports()

        for report in reports:
            sow.merge(self.results, json.load(open(report, 'r')))

        dataframe = generate_dataframe(self.results)
        dataframe = dataframe.reset_index(drop=True)

        dataframe_path = os.path.join(
            self.root_dir, self.out_prefix, 'dataframe.json'
        )
        if os.path.exists(dataframe_path):
            old_dataframe = pandas.read_json(
                dataframe_path, convert_dates=False
            )
            dataframe = pandas.concat(
                [old_dataframe, dataframe], ignore_index=True
            )

        dataframe.to_json(dataframe_path)
