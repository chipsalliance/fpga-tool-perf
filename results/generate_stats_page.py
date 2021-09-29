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

import json
import os
from typing import List

import jinja2

from project_results import ProjectResults
from infrastructure.tasks import Tasks


def generate_stats_html(template: jinja2.Template, results: ProjectResults):
    print("Generating stats page...")

    boards = dict()

    results_entries = results.entries
    project_name = results.project_name

    for board, toolchains in results_entries.items():
        toolchains_dict = dict()
        versions = dict()

        for toolchain, entries in toolchains.items():
            entry = entries[-1]

            if "fasm2bels" in toolchain:
                orig_toolchain = toolchain.strip("-fasm2bels")
                if orig_toolchain not in toolchains_dict:
                    toolchains_dict[orig_toolchain] = dict()

                toolchains_dict[orig_toolchain]["validation"
                                                ] = entry.status == "succeeded"

            for k, v in entry.versions.items():
                if k not in versions:
                    versions[k] = v
                    continue

                if k in versions and len(v) < len(versions[k]):
                    versions[k] = v

        html = template.render(
            title=f"{project_name} {board.upper()}",
            versions=versions,
            date=entry.date,
        )

        boards[board] = html

    return boards
