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

from fpgaperf import get_combinations

jobs = list()
for combination in get_combinations():
    project, toolchain, board = combination

    # TODO: different matrices need to be produced, otherwise the 256 jobs limit is reached
    #       for now test only vivado and vpr tests
    if toolchain not in ["vpr"]:
        continue

    jobs.append(dict(project=project, toolchain=toolchain, board=board))

print('::set-output name=matrix::' + str(jobs))
