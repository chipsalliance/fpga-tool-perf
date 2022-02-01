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
"""
This file contains the definition of a result entry, specifying
all the possible data present within it, as well as their types.
"""


class Clk:
    actual: float
    hold_violation: float
    met: bool
    requested: float
    setup_violation: float


class Resources:
    bram: int
    carry: int
    dff: int
    glb: int
    iob: int
    lut: int
    pll: int
    dsp: int

    def sanitize(self):
        # FIXME: currenly oxide uses FF instead of DFF, lacks GLB and has LRAM
        # https://github.com/SymbiFlow/fpga-tool-perf/pull/342
        if hasattr(self, 'ff'):
            # rename FF to DFF
            assert not hasattr(self, 'dff')
            self.dff = self.ff
            del self.ff
        # empty GLB
        if not hasattr(self, 'glb'):
            self.glb = 0
        if not hasattr(self, 'dsp'):
            self.dsp = 0
        # ignore LRAM
        if hasattr(self, 'lram'):
            del self.lram


class Runtime:
    bitstream: 'float | None'
    checkpoint: 'float | None'
    fasm: 'float | None'
    fasm2bels: 'float | None'
    link_design: 'float | None'
    optimization: 'float | None'
    overhead: 'float | None'
    packing: 'float | None'
    phys_opt_deing: 'float | None'
    placement: 'float | None'
    prepare: 'float | None'
    repots: 'float | None'
    routing: 'float | None'
    synthesis: 'float | None'
    total: 'float | None'


class ResultEntry:
    maxfreq: 'dict[str, Clk]'
    maximum_memory_use: float
    synth_resources: Resources
    impl_resources: Resources
    runtime: Runtime
    wirelength: 'int | None'
    status: 'str'
    date: 'str'
    toolchain: 'dict'
    versions: 'dict'
    device: 'str'

    def sanitize_device(self):
        dev_map = {
            "ICE40-ICE40UP5K": "ICE40-UP5K",
            "NEXUS-LIFCL-17-8UWG72C": "NEXUS-LIFCL-17",
            "NEXUS-LIFCL-40-9BG400CES": "NEXUS-LIFCL-40"
        }

        if self.device in dev_map:
            self.device = dev_map[self.device]

    def sanitize(self):
        self.sanitize_device()


def null_generator():
    while True:
        yield None


def get_entries(json_data: dict, project: str):
    def make_clks(clkdef: 'dict | float | None'):
        def get_clk(freq):
            clk = Clk()
            clk.actual = freq
            clk.hold_violation = 0.0
            clk.met = False
            clk.requested = 0.0
            clk.setup_violation = 0.0

            return clk

        clks = {}
        if type(clkdef) is dict:
            for clkname, clkvals in clkdef.items():
                clk = Clk()
                for k, v in clkvals.items():
                    setattr(clk, k, v)
                clks[clkname] = clk
        elif type(clkdef) is float:
            clks['clk'] = get_clk(clkdef)
        elif clkdef is None:
            return clks
        else:
            raise Exception('Wrong type for clock definition')
        return clks

    def make_runtime(runtimedef: 'dict | None'):
        runtime = Runtime()
        if type(runtimedef) is dict:
            for k, v in runtimedef.items():
                k = k.replace(' ', '_')
                setattr(runtime, k, v)
        return runtime

    def make_resources(resourcesdef: 'dict | None'):
        resources = Resources()
        if type(resourcesdef) is dict:
            for k, v in resourcesdef.items():
                k = k.lower()
                if v is None:
                    v = 'null'
                setattr(resources, k, v)
            resources.sanitize()
        return resources

    results = json_data['results']
    date = json_data['date']

    wirelength = results.get('wirelength', null_generator())
    status = results.get('status', null_generator())

    entries = list()
    zipped = zip(
        results['board'], results['toolchain'], results['max_freq'],
        results['maximum_memory_use'], results['resources'],
        results['runtime'], wirelength, status, results['toolchain'],
        results['versions'], results['family'], results['device']
    )
    for board, toolchain_dict, max_freq, max_mem_use, resources, runtime, \
            wirelength, status, toolchain, versions, family, device in zipped:
        toolchain_name, _ = next(iter(toolchain_dict.items()))

        # Some platforms are cursed and the tests return just a single float
        # instead of a dict
        entry = ResultEntry()
        entry.maximum_memory_use =\
            max_mem_use if max_mem_use is not None else 'null'
        entry.wirelength = wirelength if wirelength is not None else 'null'
        entry.maxfreq = make_clks(max_freq)
        entry.runtime = make_runtime(runtime)

        if resources is None or "synth" not in resources:
            # Backwards compatibility with older results
            synth_res = impl_res = resources
        else:
            synth_res = resources["synth"]
            impl_res = resources["impl"]

        entry.synth_resources = make_resources(synth_res)
        entry.impl_resources = make_resources(impl_res)

        entry.toolchain = toolchain
        entry.versions = versions
        entry.status = status if status is not None else 'succeeded'
        entry.date = date

        # Sanitize family
        if family == "lifcl":
            family = "nexus"

        entry.device = f"{family}-{device}".upper()

        # Sanitize entry
        entry.sanitize()

        entries.append((board, entry.device, toolchain_name, entry))

    return entries
