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
import json
from datetime import datetime
from collections import defaultdict

from testentry import *


def config_name(board: str, toolchain: str):
    return f'{board}-{toolchain}'


def datetime_from_str(s: str):
    return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S')


class ProjectResults:
    project_name: str
    test_dates: 'list[datetime]'
    entries: 'defaultdict[str, defaultdict[str, list[TestEntry]]]'

    def __init__(self, project_name: str, data_dir: str):
        self.project_name = project_name
        self.test_dates = []
        self.entries = defaultdict(lambda: defaultdict(lambda: []))

        configs = defaultdict(lambda: set())
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
                except Exception as e:
                    print(f'WARNING: couldn\'t load data from `{p}`: {e}')
                if data:
                    try:
                        for board, toolchain in get_configs(data):
                            configs[board].add(toolchain)
                    except KeyError as e:
                        print(f'Invalid config `{p}`, missing: {e}')
                        continue

                    datas.append(data)

        # Create test entries
        for data in sorted(datas, key=lambda d: datetime_from_str(d['date'])):
            self.test_dates.append(datetime_from_str(data['date']))
            configs_to_handle = {}
            for board, toolchains in configs.items():
                configs_to_handle[board] = toolchains.copy()

            for board, toolchain, entry in get_entries(data):
                try:
                    configs_to_handle[board].remove(toolchain)
                except KeyError:
                    print(f'WARNING: config `{config_name(board, toolchain)}` '
                          f'repeated in data forproject `{project_name}, '
                          f'date: {data["date"]}. Data will be ignoreed.')
                    continue
                self.entries[board][toolchain].append(entry)

            for board, toolchains in configs_to_handle.items():
                for toolchain in toolchains:
                    self.entries[board][toolchain].append(None)

    def get_all_configs(self):
        for board, toolchains in self.entries.items():
            for toolchain in toolchains.keys():
                yield board, toolchain
