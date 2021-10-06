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
"""
This script is responsible for generating the index page and the
corresponding data file containing all the historical data.
"""

import datetime
import jinja2
import os
from typing import List

import result_entry
from fpgaperf import get_boards
from infrastructure.tasks import Tasks
from project_results import ProjectResults


class ColorGen:
    """
    Class defining a color scheme for each different key. Once a key
    gets assigned with a color, the color cannot be changed.

    The list of colors has been generated so that they are as distant as possible
    avoiding low contrast between any of them.
    """
    def __init__(self):
        self.colors = [
            "#2f4f4f", "#a0522d", "#006400", "#000080", "#ff0000", "#00ced1",
            "#ffa500", "#ffff00", "#c71585", "#00ff00", "#0000ff", "#d8bfd8",
            "#ff00ff", "#1e90ff", "#98fb98"
        ]
        self.idx = -1
        self.keys = dict()

    def get_next_color(self, key):
        self.idx += 1
        assert self.idx < len(self.colors), (self.idx, self.colors)

        color = self.colors[self.idx]
        self.keys[key] = color
        return color

    def get_color(self, key):
        if key not in self.keys:
            color = self.get_next_color(key)
        else:
            color = self.keys[key]

        return color


COLOR_GENERATOR = ColorGen()


def datetime_from_str(s: str):
    return datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%S')


def generate_graph_data(device, toolchain, dates, entries):
    """
    Generates the data for one a specific project/device/toolchain
    combination, that will be added to the various charts containing
    the historical data runs.
    """

    datasets = dict()

    # Generate color for this toolchain
    color_hex = COLOR_GENERATOR.get_color(toolchain)

    def generate_datasets(selector, fill_null=False):

        data = dict()
        for e in entries:
            if e and e.status == "succeeded":
                data[datetime_from_str(e.date)] = selector(e)

        final_data = list()

        for date in dates:
            if fill_null:
                data_point = 'null'
            else:
                data_point = data.get(date, 'null')

            final_data.append(data_point)

        dataset = dict()
        dataset["data"] = final_data
        dataset["color"] = color_hex

        return dataset

    clocks = set()
    for entry in entries:
        if not entry:
            continue
        for clkname in entry.maxfreq.keys():
            clocks.add(clkname)

    datasets['freq'] = dict()
    for clkname in clocks:

        def selector(e: result_entry.ResultEntry):
            nonlocal clkname
            clk = e.maxfreq.get(clkname)
            return clk.actual if clk else 'null'

        datasets['freq'][clkname] = generate_datasets(selector)

    attrs = dict()
    attrs['runtime'] = ['total']
    attrs['maximum_memory_use'] = list()
    attrs['wirelength'] = list()
    attrs['resources'] = ['lut', 'dff', 'carry', 'iob', 'bram', 'pll', 'glb']

    for k, v in attrs.items():
        datasets[k] = dict()
        if not v:
            datasets[k] = generate_datasets(lambda e: getattr(e, k))
            continue

        for elem in v:
            # fasm2bels runtime is not interesting as a metric to visualize
            fill_null = 'fasm2bels' in toolchain and k == 'runtime'
            datasets[k][elem] = generate_datasets(
                lambda e: getattr(getattr(e, k), elem), fill_null
            )

    return datasets


def generate_device_data(results: ProjectResults):
    """
    Generates the data for one a specific project/device/toolchain
    combination which is then represented in a summary table.
    """
    def color(val):
        return (val, "green" if val else "red")

    device_data = dict()

    results_entries = results.entries
    project_name = results.project_name
    dates = results.test_dates
    resources_list = ["LUT", "DFF", "CARRY", "IOB", "PLL", "GLB"]

    for device, toolchains in results_entries.items():
        toolchains_data = dict()
        toolchains_color = list()
        versions = dict()

        graph_data = dict()

        for toolchain, entries in toolchains.items():
            entry = entries[-1]
            passed = entry.status == "succeeded"

            graph_data[toolchain] = generate_graph_data(
                device, toolchain, dates, entries
            )

            toolchains_color.append(
                (toolchain, COLOR_GENERATOR.get_color(toolchain))
            )

            if "fasm2bels" in toolchain:
                orig_toolchain = toolchain.strip("-fasm2bels")
                if orig_toolchain not in toolchains_data:
                    toolchains_data[orig_toolchain] = dict()

                toolchains_data[orig_toolchain]["validation"] = color(passed)
                continue

            if toolchain not in toolchains_data:
                toolchains_data[toolchain] = dict()

            toolchains_data[toolchain]["passed"] = color(passed)

            if "validation" not in toolchains_data:
                toolchains_data[toolchain]["validation"] = color(passed)

            clk_met = True and passed
            for clk, data in entry.maxfreq.items():
                clk_met = clk_met and data.met

            toolchains_data[toolchain]["clk_met"] = color(clk_met)

            synth_tool = entry.toolchain[toolchain]["synth_tool"]
            pr_tool = entry.toolchain[toolchain]["pr_tool"]
            toolchains_data[toolchain]["synth_tool"] = synth_tool
            toolchains_data[toolchain]["pr_tool"] = pr_tool

            runtime = ("N/A", 'grey')
            memory = ("N/A", 'grey')

            resources = dict.fromkeys(resources_list, ("N/A", "grey"))

            if passed:
                runtime = (entry.runtime.total, "black")

                max_mem = entry.maximum_memory_use
                if max_mem != 'null':
                    memory = (
                        "{:.2f}".format(float(entry.maximum_memory_use)),
                        "black"
                    )

                for res in resources_list:
                    count = getattr(entry.resources, res.lower())
                    count = count if count != "null" else 0
                    resources[res] = (count, "black")

            toolchains_data[toolchain]["runtime"] = runtime
            toolchains_data[toolchain]["memory"] = memory
            toolchains_data[toolchain]["resources"] = resources

            for k, v in entry.versions.items():
                if k not in versions:
                    versions[k] = v
                    continue

                if k in versions and len(v) < len(versions[k]):
                    versions[k] = v

        # Unify clock names and add missing data to each toolchain
        clocks = set()
        for toolchain, data in graph_data.items():
            for clock in data["freq"]:
                clocks.add(clock)

        for toolchain, data in graph_data.items():
            for clock in clocks:
                if clock not in data["freq"]:
                    data["freq"][clock] = dict(
                        data=["null" for _ in dates],
                        color=COLOR_GENERATOR.get_color(toolchain)
                    )

        device_data[device] = dict(
            project=project_name,
            device=device,
            versions=versions,
            date=entry.date,
            toolchains_color=sorted(toolchains_color),
            toolchains_data=toolchains_data,
            resources=resources_list,
            graph_data=graph_data,
            clocks=clocks,
            dates=[f"{x}" for x in dates]
        )

    return device_data


def generate_index_html(
    index_template: jinja2.Template, data_template: jinja2.Template,
    results: List[ProjectResults]
):
    print('Generating index page...')

    cur_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.join(cur_dir, '..')
    tasks = Tasks(root_dir)
    combinations = sorted(
        tasks.get_all_combinations(), key=lambda tup: (tup[2], tup[0], tup[1])
    )

    devices = dict()
    projects = set()
    device_data = dict()
    toolchains_data = dict()

    all_boards = get_boards()

    for project, toolchain, board in combinations:
        if "fasm2bels" in toolchain:
            continue

        board = all_boards[board]
        device = f"{board['family']}-{board['device']}"
        device = device.upper()

        if device not in devices:
            devices[device] = dict()

        device_dict = devices[device]
        if project not in device_dict:
            device_dict[project] = dict(all_failed=True)

        proj_dict = device_dict[project]

        proj_dict[toolchain] = "skip"

        if device not in toolchains_data:
            toolchains_data[device] = set()

        toolchains_data[device].add(toolchain)

        projects.add(project)

    for project_results in results:
        entries = project_results.entries
        project = project_results.project_name

        for device, toolchains in entries.items():
            all_failed = True
            for toolchain in toolchains.keys():
                if "fasm2bels" in toolchain:
                    continue

                status = entries[device][toolchain][0].status
                devices[device][project][toolchain] = status

                all_failed &= status != "succeeded"

            devices[device][project]["all_failed"] = all_failed

        device_data[project] = generate_device_data(project_results)

    # Remove project entry if all tests are skipped
    del_proj = set()
    for device, prjs in devices.items():
        for project, toolchains in prjs.items():
            if all([v == "skip" or k == "all_failed"
                    for k, v in toolchains.items()]):
                del_proj.add((device, project))

    for d, p in del_proj:
        del devices[d][p]

    for device, tool_list in toolchains_data.items():
        toolchains_data[device] = sorted(list(tool_list))

    devices_list = [k for k, v in devices.items() if v]

    index_page = index_template.render(
        devices=devices,
        devices_list=sorted(devices_list),
        device_data=device_data,
        toolchains=toolchains_data,
        projects=sorted(projects)
    )

    data_page = data_template.render(devices_data=device_data)

    return index_page, data_page
