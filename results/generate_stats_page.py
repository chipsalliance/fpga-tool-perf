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

import jinja2

from project_results import ProjectResults


def color(val):
    return (val, "green" if val else "red")


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
            passed = entry.status == "succeeded"

            if "fasm2bels" in toolchain:
                orig_toolchain = toolchain.strip("-fasm2bels")
                if orig_toolchain not in toolchains_dict:
                    toolchains_dict[orig_toolchain] = dict()

                toolchains_dict[orig_toolchain]["validation"] = color(passed)
                continue

            if toolchain not in toolchains_dict:
                toolchains_dict[toolchain] = dict()

            toolchains_dict[toolchain]["passed"] = color(passed)

            if "validation" not in toolchains_dict:
                toolchains_dict[toolchain]["validation"] = color(passed)

            clk_met = True and passed
            for clk, data in entry.maxfreq.items():
                clk_met = clk_met and data.met

            toolchains_dict[toolchain]["clk_met"] = color(clk_met)

            synth_tool = entry.toolchain[toolchain]["synth_tool"]
            pr_tool = entry.toolchain[toolchain]["pr_tool"]
            toolchains_dict[toolchain]["synth_tool"] = synth_tool
            toolchains_dict[toolchain]["pr_tool"] = pr_tool

            runtime = ("N/A", 'grey')
            memory = ("N/A", 'grey')
            if passed:
                runtime = (entry.runtime.total, "black")
                max_mem = entry.maximum_memory_use

                if max_mem != 'null':
                    memory = (
                        "{:.2f}".format(float(entry.maximum_memory_use)),
                        "black"
                    )

            toolchains_dict[toolchain]["runtime"] = runtime
            toolchains_dict[toolchain]["memory"] = memory

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
            toolchains=toolchains_dict,
        )

        boards[board] = html

    return boards
