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

# Fetch test results from Google Storage

import gzip
import json
import os
from argparse import ArgumentParser
from datetime import datetime
from collections import defaultdict
from typing import List
from multiprocessing.pool import ThreadPool


def download_and_split_compound(meta_path):
    with gzip.open(meta_path, "r") as f:
        meta = json.loads(f.read().decode("utf-8"))

    projects = defaultdict(lambda: {'results': defaultdict(lambda: [])})

    meta_results = meta['results']

    meta_projects = meta_results['project']

    for idx, project in enumerate(meta_projects):
        project_res = projects[project]['results']

        for k, v in meta_results.items():
            if k in ['project']:
                continue

            project_res[k].append(v[idx])

    for project in projects.values():
        project['date'] = meta['date']

    return projects


def process_result(result_path, out_dir, idx):
    projects = download_and_split_compound(result_path)

    for project_name, data in projects.items():
        project_dir = os.path.join(out_dir, project_name)
        out_file = os.path.join(project_dir, f'meta-{idx}.json')
        os.makedirs(project_dir, exist_ok=True)
        json_data = json.dumps(data, indent=4)
        with open(out_file, 'w') as f:
            f.write(json_data)


def main():
    parser = ArgumentParser()
    parser.add_argument(
        '--in-dir', type=str, help='Directory containing all the results'
    )
    parser.add_argument(
        '--out-dir', type=str, help='Output directory with all meta files'
    )
    args = parser.parse_args()

    if not os.path.isdir(args.out_dir):
        print('Output path is not a directory!')
        exit(-1)

    for idx, result in enumerate(os.listdir(args.in_dir)):
        process_result(os.path.join(args.in_dir, result), args.out_dir, idx)


if __name__ == "__main__":
    main()
