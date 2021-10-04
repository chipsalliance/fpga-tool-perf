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

import datetime
import jinja2
import math
import os
import zlib
from color import hsl_to_rgb, rgb_to_hex
from typing import List

import testentry
from fpgaperf import get_boards
from infrastructure.tasks import Tasks
from jinja2_templates import gen_datasets_def
from project_results import ProjectResults


def datetime_from_str(s: str):
    return datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%S')


# Generate an HSL color unique for a given config
def gen_config_color(config_name: str):
    hash = zlib.crc32(config_name.encode()) & 0xffffff
    h = float(hash & 0x0000ff) / 255.0 * math.pi * 2.0
    s = float((hash & 0x00ff00) >> 8) / 255.0 * 0.25 + 0.375
    l = float((hash & 0xff0000) >> 16) / 255.0 * 0.5 + 0.25

    return min(h, math.pi * 2.0), min(s, 1.0), min(l, 1.0)


def fmt_list(l: list):
    return ', '.join('{}'.format(e) for e in l)


def generate_graph_data(device, toolchain, dates, entries):
    datasets = dict()

    # Generate color for this toolchain
    label = f"{toolchain}"
    r, g, b = hsl_to_rgb(*gen_config_color(label))
    color_hex = rgb_to_hex(r, g, b)

    def generate_datasets(selector):

        data = dict()
        for e in entries:
            if e and e.status == "succeeded":
                data[datetime_from_str(e.date)] = selector(e)

        final_data = list()

        for date in dates:
            final_data.append(data.get(date, 'null'))

        dataset = dict()
        dataset["data"] = fmt_list(final_data)
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

        def selector(e: testentry.TestEntry):
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
            datasets[k][elem] = generate_datasets(
                lambda e: getattr(getattr(e, k), elem)
            )

    return datasets, color_hex


def generate_device_data(results: ProjectResults):
    def color(val):
        return (val, "green" if val else "red")

    device_data = dict()

    results_entries = results.entries
    project_name = results.project_name
    dates = results.test_dates
    resources_list = ["LUT", "DFF", "CARRY", "PLL", "GLB"]

    for device, toolchains in results_entries.items():
        toolchains_dict = dict()
        versions = dict()

        graph_data = dict()

        for toolchain, entries in toolchains.items():
            entry = entries[-1]
            passed = entry.status == "succeeded"

            graph_data[toolchain], hex_color = generate_graph_data(
                device, toolchain, dates, entries
            )

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

            toolchains_dict[toolchain]["runtime"] = runtime
            toolchains_dict[toolchain]["memory"] = memory
            toolchains_dict[toolchain]["resources"] = resources
            toolchains_dict[toolchain]["color"] = hex_color

            for k, v in entry.versions.items():
                if k not in versions:
                    versions[k] = v
                    continue

                if k in versions and len(v) < len(versions[k]):
                    versions[k] = v

        device_data[device] = dict(
            project=project_name,
            device=device,
            versions=versions,
            date=entry.date,
            toolchains=toolchains_dict,
            resources=resources_list,
            graph_data=graph_data,
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
    toolchains_dict = dict()

    all_boards = get_boards()

    for project, toolchain, board in combinations:
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

        if device not in toolchains_dict:
            toolchains_dict[device] = set()

        toolchains_dict[device].add(toolchain)

        projects.add(project)

    for project_results in results:
        entries = project_results.entries
        project = project_results.project_name

        for device, toolchains in entries.items():
            all_failed = True
            for toolchain in toolchains.keys():
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

    for device, tool_list in toolchains_dict.items():
        toolchains_dict[device] = sorted(list(tool_list))

    index_page = index_template.render(
        devices=devices,
        devices_list=sorted(devices),
        device_data=device_data,
        toolchains=toolchains_dict,
        projects=sorted(projects)
    )

    data_page = data_template.render(devices_data=device_data)

    return index_page, data_page
