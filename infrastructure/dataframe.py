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

import pandas


def get_clock_dataframe(results):
    designs = []

    # Clock-related lists
    actual_frequency = []
    requested_frequency = []
    hold_violation = []
    setup_violation = []
    clock_met = []
    clock_names = []

    for idx, design in enumerate(results['design']):
        clock = results['max_freq'][idx]
        if clock and type(clock) is dict:
            for key, value in clock.items():
                designs.append(design)
                clock_names.append(key)
                actual_frequency.append(value['actual'] / 1e6)
                requested_frequency.append(value['requested'] / 1e6)
                hold_violation.append(value['hold_violation'])
                setup_violation.append(value['setup_violation'])
                clock_met.append(value['met'])
        else:
            clock_name = None
            actual_freq = None
            if clock and type(clock) is float:
                clock_name = 'clk'
                actual_freq = clock

            designs.append(design)
            clock_names.append(clock_name)
            actual_frequency.append(actual_freq)
            requested_frequency.append(None)
            hold_violation.append(None)
            setup_violation.append(None)
            clock_met.append(None)

    index = pandas.Index(designs)
    return pandas.DataFrame(
        {
            'clocks': clock_names,
            'clock_actual_frequency': actual_frequency,
            'clock_requested_frequency': requested_frequency,
            'clock_hold_violation': hold_violation,
            'clock_setup_violation': setup_violation,
            'clock_met': clock_met,
        },
        index=index
    )


def get_general_dataframe(results):
    designs = results['design']

    # Get runtimes
    runtimes = dict()
    for runtime in results['runtime']:
        if not runtimes:
            runtimes = {k: [] for k in runtime.keys()}

        for k, v in runtime.items():
            runtimes[k].append(v)

    runtimes_keys = list(runtimes.keys())
    for key in runtimes_keys:
        runtimes["{}_time".format(key)] = runtimes.pop(key)

    # Get resources
    resources = dict()
    for resource in results['resources']:
        if not resources:
            resources = {k: [] for k in resource.keys()}

        for k, v in resource.items():
            value = int(float(v)) if v else None
            resources[k].append(value)

    resources_keys = list(resources.keys())
    for key in resources_keys:
        resources["#{}".format(key)] = resources.pop(key)

    # Get versions
    tools = dict()
    # Initialize versions dictionary with all possible
    # versions of the tools.
    for version in results['versions']:
        for key in version:
            tools[key] = []

    for version in results['versions']:
        for k, v in version.items():
            tools[k].append(v)

        for k in version.keys() ^ tools.keys():
            tools[k].append(None)

    tools_keys = list(tools.keys())
    for key in tools_keys:
        tools["{}_version".format(key)] = tools.pop(key)

    ALREADY_PARSED_KEYS = ['versions', 'max_freq', 'runtime', 'resources']
    general_data = {
        k: results[k]
        for k in results.keys() ^ ALREADY_PARSED_KEYS
    }

    data = {**runtimes, **resources, **general_data, **tools}
    index = pandas.Index(designs)
    return pandas.DataFrame(data, index)


def generate_dataframe(results):
    clock_df = get_clock_dataframe(results)

    general_df = get_general_dataframe(results)

    df = general_df.join(clock_df, how="left")

    return df
