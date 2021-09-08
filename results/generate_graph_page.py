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
import datetime
import zlib
import math
from collections import defaultdict
from typing import DefaultDict, Set

import jinja2

from color import hsl_to_rgb, rgb_to_hex
from jinja2_templates import gen_datasets_def
import testentry
from project_results import ProjectResults


def datetime_from_str(s: str):
    return datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%S')


def fmt_list(l: list, fmt: str):
    return ', '.join(fmt.format(e) for e in l)


def config_name(board: str, toolchain: str):
    return f'{board}-{toolchain}'


# Generate an HSL color unique for a given config
def gen_config_color(config_name: str):
    hash = zlib.crc32(config_name.encode()) & 0xffffff
    h = float(hash & 0x0000ff) / 255.0 * math.pi * 2.0
    s = float((hash & 0x00ff00) >> 8) / 255.0 * 0.25 + 0.375
    l = float((hash & 0xff0000) >> 16) / 255.0 * 0.5 + 0.25

    return min(h, math.pi * 2.0), min(s, 1.0), min(l, 1.0)


def generate_graph_html(template: jinja2.Template,
                        project_results: ProjectResults):
    print(f'Generating page for project `{project_results.project_name}`...')

    all_config_names = set()
    board_configs: DefaultDict[str, Set[str]] = defaultdict(lambda: set())

    for board, toolchain in project_results.get_all_configs():
        gname = config_name(board, toolchain)
        board_configs[board].add(gname)
        all_config_names.add(gname)
    board_configs['(all configs)'] = all_config_names

    labels = project_results.test_dates

    # Generic dataset generator
    # Takes tuple of the following format as its arguments:
    # - d_dict: a target dictionray for datasets of certain measurements for
    #           different configs
    # - fmt: a string used for formatting the items within generated lists
    # - selector: a function used to retreive a sample from an entry
    def generate_datasets(*ds_defs):
        for board, toolchains in project_results.entries.items():
            for toolchain, entries in toolchains.items():
                gname = config_name(board, toolchain)
                r, g, b = hsl_to_rgb(*gen_config_color(gname))
                color_hex = rgb_to_hex(r, g, b)

                for d_dict, fmt, selector in ds_defs:
                    d_dict[gname] = {
                        'data': fmt_list([selector(e) if e else 'null' \
                                        for e in entries], fmt),
                        'color': color_hex
                    }

    runtime_datasets = {}
    freq_multidatasets = {}
    lut_datasets = {}
    dff_datasets = {}
    carry_datasets = {}
    iob_datasets = {}
    bram_datasets = {}
    pll_datasets = {}
    glb_datasets = {}
    mem_use_datasets = {}
    wirelength_datasets = {}

    clocks = set()
    for _, toolchains in project_results.entries.items():
        for _, entries in toolchains.items():
            for entry in entries:
                if not entry:
                    continue
                for clkname in entry.maxfreq.keys():
                    clocks.add(clkname)

    for clkname in clocks:
        freq_multidatasets[clkname] = {}

        def selector(e: testentry.TestEntry):
            nonlocal clkname
            clk = e.maxfreq.get(clkname)
            return clk.actual if clk else 'null'

        generate_datasets((freq_multidatasets[clkname], '{}', selector))

    generate_datasets((runtime_datasets, '{}', lambda e: e.runtime.total),
                      (lut_datasets, '{}', lambda e: e.resources.lut),
                      (dff_datasets, '{}', lambda e: e.resources.dff),
                      (carry_datasets, '{}', lambda e: e.resources.carry),
                      (iob_datasets, '{}', lambda e: e.resources.iob),
                      (bram_datasets, '{}', lambda e: e.resources.bram),
                      (pll_datasets, '{}', lambda e: e.resources.pll),
                      (glb_datasets, '{}', lambda e: e.resources.glb),
                      (mem_use_datasets, '{}', lambda e: e.maximum_memory_use),
                      (wirelength_datasets, '{}', lambda e: e.wirelength))

    rdata = template.render(
        labels=fmt_list(labels, '"{}"'),
        runtime_datasets=gen_datasets_def(runtime_datasets),
        freq_multidatasets=freq_multidatasets,
        lut_datasets=gen_datasets_def(lut_datasets),
        dff_datasets=gen_datasets_def(dff_datasets),
        carry_datasets=gen_datasets_def(carry_datasets),
        iob_datasets=gen_datasets_def(iob_datasets),
        bram_datasets=gen_datasets_def(bram_datasets),
        pll_datasets=gen_datasets_def(pll_datasets),
        glb_datasets=gen_datasets_def(glb_datasets),
        mem_use_datasets=gen_datasets_def(mem_use_datasets),
        wirelength_datasets=gen_datasets_def(wirelength_datasets),
        project=project_results.project_name,
        board_configs=board_configs)

    return rdata
