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

from fpgaperf import get_combinations, get_projects, get_project, toolchains
import sys

if len(sys.argv) < 2:
    print("Usage {} <tool>".format(sys.argv[0]))
    sys.exit(1)

tools = sys.argv[1:]

all_toolchains = "all" in tools

jobs = dict()
combinations = get_combinations()
for project_file in get_projects():
    project_dict = get_project(project_file)
    project_name = project_dict["name"]

    for toolchain in toolchains.keys():
        if ((toolchain not in tools and not all_toolchains)
                or ('skip_toolchains' in project_dict
                    and toolchain in project_dict["skip_toolchains"])):
            continue

        for vendor in project_dict["vendors"].items():
            for board in vendor[1]:
                if (project_name, toolchain, board) not in combinations:
                    continue

                if toolchain not in jobs:
                    jobs[toolchain] = list()
                jobs[toolchain].append(
                    dict(
                        project=project_name, toolchain=toolchain, board=board
                    )
                )

matrices = {tool.replace('-', '_'): content for tool, content in jobs.items()}
print(f"::set-output name=matrices::{matrices}")
