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

from fpgaperf import get_combinations
import sys

if len(sys.argv) < 2:
    print("Usage {} <tool>".format(sys.argv[0]))
    sys.exit(1)

tools = sys.argv[1:]

all_toolchains = "all" in tools

jobs = dict()
for combination in get_combinations():
    project, toolchain, board = combination

    if toolchain not in tools and not all_toolchains:
        continue

    if toolchain not in jobs:
        jobs[toolchain] = list()

    jobs[toolchain].append(
        dict(project=project, toolchain=toolchain, board=board)
    )

# Different matrices need to be produced to overcome the 256 jobs limit imposed
# by GH actions
for tool, matrix in jobs.items():
    print(f"::set-output name=matrix_{tool.replace('-', '_')}:: {matrix}")
