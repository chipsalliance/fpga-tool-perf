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

import os
import json
from datetime import datetime
from collections import defaultdict

from result_entry import ResultEntry, get_entries


def datetime_from_str(s: str):
    return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S')


class ProjectResults:
    project_name: str
    test_dates: 'list[datetime]'
    entries: 'defaultdict[str, defaultdict[str, list[ResultEntry]]]'

    def __init__(self, project_name: str, data_dir: str):
        self.project_name = project_name
        self.test_dates = []
        self.entries = defaultdict(lambda: defaultdict(lambda: []))

        datas = []

        # Load data
        for p in os.listdir(data_dir):
            p = os.path.join(data_dir, p)
            if not os.path.isfile(p):
                continue

            with open(p) as f:
                data = None
                try:
                    data = json.loads(f.read())
                    datas.append(data)
                except Exception as e:
                    print(f'WARNING: couldn\'t load data from `{p}`: {e}')

        # Create test entries
        for data in sorted(datas, key=lambda d: datetime_from_str(d['date'])):
            self.test_dates.append(datetime_from_str(data['date']))

            added = dict()
            for board, device, toolchain, entry in sorted(get_entries(
                    data, project_name), key=lambda k: k[0]):
                key = (device, toolchain)
                if key not in added:
                    self.entries[device][toolchain].append(entry)
                    added[key] = entry
                elif added[key
                           ].status == "failed" and entry.status == "succeeded":
                    self.entries[device][toolchain].pop()
                    self.entries[device][toolchain].append(entry)
                    added[key] = entry

    def get_all_configs(self):
        for device, toolchains in self.entries.items():
            for toolchain in toolchains.keys():
                yield device, toolchain
