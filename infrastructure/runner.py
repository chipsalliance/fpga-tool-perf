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

import datetime
import os
import sys
import tqdm
import glob
import json
import pandas
from multiprocessing import Pool, cpu_count
from contextlib import redirect_stdout

from fpgaperf import run
from infrastructure.dataframe import generate_dataframe
import utils.sow as sow


class Runner:
    """Class to create a runner object that, given a list of tasks
    runs all of them parallely.
    """
    def __init__(
        self, task_list, verbose, out_prefix, root_dir, build_type,
        build_numbers, overwrite, num_cpu
    ):
        self.verbose = verbose
        self.out_prefix = out_prefix
        self.root_dir = root_dir
        self.build_format = "{:03d}"
        self.build_type = build_type
        self.results = dict()
        self.task_list = task_list
        self.build_numbers = build_numbers
        self.overwrite = overwrite
        self.num_cpu = num_cpu

    def worker(self, arglist):
        """Single worker function that is run in the Pool of workers.

        This takes, as argument list, the various tasks to perform.
        """
        def eprint(*args, **kwargs):
            print(*args, file=sys.stderr, **kwargs)

        project, toolchain, board, seed, option, build_number = arglist

        build = self.build_format.format(build_number)

        # We don't want output of all subprocesses here
        # Log files for each build will be placed in build directory
        with redirect_stdout(open(os.devnull, 'w')):
            try:
                run(
                    board,
                    toolchain,
                    project,
                    None,  #params_file
                    option,  #params_string
                    None,  #out_dir
                    self.out_prefix,
                    self.overwrite,
                    self.verbose,
                    None,  #strategy
                    seed,
                    None,  #carry
                    build,
                    self.build_type,
                )
            except Exception as e:
                eprint("\n---------------------")
                eprint(
                    "ERROR: {} {} {} test has failed (build type {}, build nr. {})\n"
                    .format(project, toolchain, board, self.build_type, build)
                )
                # Limit output to max 300 characters for exhaust.py to make sure log files are not too large.
                exception_str = str(e)
                eprint(
                    "ERROR MESSAGE: ",
                    ("[...]\n{}".format(exception_str[-1000:]))
                    if len(str(exception_str)) > 1000 else exception_str
                )
                eprint("---------------------\n")

    def run(self):
        os.makedirs(os.path.expanduser(self.out_prefix), exist_ok=True)
        print('Writing to %s' % self.out_prefix)

        with Pool(self.num_cpu) as pool:
            for _ in tqdm.tqdm(pool.imap_unordered(self.worker,
                                                   self.task_list),
                               total=len(self.task_list), unit='test'):
                pass

    def get_reports(self):
        reports = []
        for build_number in self.build_numbers:
            if build_number is not None:
                metadata_path = '*{}_{}*/meta.json'.format(
                    self.build_type, self.build_format.format(build_number)
                )
            else:
                metadata_path = '*{}*/meta.json'.format(self.build_type)
            for filename in glob.iglob(os.path.join(self.root_dir,
                                                    self.out_prefix,
                                                    metadata_path)):
                reports.append(filename)

        return reports

    def collect_results(self):
        reports = self.get_reports()

        if len(reports) == 0:
            return

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

    def merge_results(self):
        for report in self.get_reports():
            sow.merge(self.results, json.load(open(report, 'r')), ["date"])

        date = datetime.datetime.utcnow()
        date_str = date.replace(microsecond=0).isoformat()

        json_data = dict()
        json_data["date"] = date_str
        json_data["results"] = self.results
        json_file_path = os.path.join(
            self.root_dir, self.out_prefix, f'results-{self.build_type}.json'
        )
        with open(json_file_path, "w") as f:
            f.write(json.dumps(json_data, indent=4))
