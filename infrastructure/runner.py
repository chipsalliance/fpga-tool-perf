#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2018-2022 F4PGA Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

import datetime
import os
import sys
import glob
import gzip
import json
import pandas
from multiprocessing import Pool, cpu_count

from fpgaperf import run
from infrastructure.dataframe import generate_dataframe
import utils.sow as sow


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
        build_numbers,
        overwrite,
        num_cpu,
        timeout=0
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
        self.timeout = timeout

    def worker(self, arglist):
        """Single worker function that is run in the Pool of workers.

        This takes, as argument list, the various tasks to perform.
        """
        def eprint(*args, **kwargs):
            print(*args, file=sys.stderr, **kwargs)

        project, toolchain, board, seed, option, build_number = arglist

        build = self.build_format.format(build_number)

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
            self.timeout
        )

    def run(self):
        os.makedirs(os.path.expanduser(self.out_prefix), exist_ok=True)
        print('Writing to %s' % self.out_prefix)

        with Pool(self.num_cpu) as pool:
            for _ in pool.imap_unordered(self.worker, self.task_list):
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
        exclude_results = [
            "date", "build_type", "carry", "cmds", "design", "parameters",
            "sources", "strategy", "optstr", "top", "xdc", "sdc", "pcf"
        ]
        for report in self.get_reports():
            sow.merge(
                self.results, json.load(open(report, 'r')), exclude_results
            )

        date = datetime.datetime.utcnow()
        date_str = date.replace(microsecond=0).isoformat()

        json_data = dict()
        json_data["date"] = date_str
        json_data["results"] = self.results

        json_str = json.dumps(json_data)
        json_byte = json_str.encode("utf-8")

        gzip_file_path = os.path.join(
            self.root_dir, self.out_prefix,
            f'results-{self.build_type}.json.gz'
        )

        with gzip.open(gzip_file_path, "wb") as f:
            f.write(json_byte)
