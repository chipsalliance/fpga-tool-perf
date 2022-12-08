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

from copy import copy
import random
import networkx as nx
from argparse import ArgumentParser


def lut_param_randomizer(len):
    r = ['0', '1']

    init = f'{len}\'b'
    for _ in range(0, len):
        init += random.choice(r)

    return {'INIT': init}


class Cell:
    name: str
    inputs: 'list[str]'
    outputs: 'list[str]'

    def __init__(
        self,
        name: str,
        inputs: 'list[str]',
        outputs: 'list[str]',
    ):
        self.name = name
        self.inputs = inputs
        self.outputs = outputs


class PlaceableCell:
    cell: Cell
    probability: float
    param_randomizer: None

    def __init__(
        self,
        name: str,
        inputs: 'list[str]',
        outputs: 'list[str]',
        probability: float,
        param_randomizer=None
    ):
        self.cell = Cell(name, inputs, outputs)
        self.probability = probability
        self.param_randomizer = param_randomizer


placeables = [
    PlaceableCell(
        name='LUT4',
        inputs=['I0', 'I1', 'I2', 'I3'],
        outputs=['O'],
        probability=1.0,
        param_randomizer=lambda: lut_param_randomizer(16)
    ),
    PlaceableCell(
        name='LUT5',
        inputs=['I0', 'I1', 'I2', 'I3', 'I4'],
        outputs=['O'],
        probability=1.0,
        param_randomizer=lambda: lut_param_randomizer(32)
    ),
    PlaceableCell(
        name='LUT6',
        inputs=['I0', 'I1', 'I2', 'I3', 'I4', 'I5'],
        outputs=['O'],
        probability=1.0,
        param_randomizer=lambda: lut_param_randomizer(64)
    )
]

io_cells = {
    'in':
        {
            'cell': Cell(name='IBUF', inputs=['I'], outputs=['O']),
            'i': 'I',
            'o': 'O',
            'params': {}
        },
    'out':
        {
            'cell': Cell(name='OBUF', inputs=['I'], outputs=['O']),
            'i': 'I',
            'o': 'O',
            'params': {}
        }
}

total_placeable_weight = 0.0
for p in placeables:
    total_placeable_weight += p.probability


def random_cell() -> PlaceableCell:
    global total_placeable_weight

    v = random.uniform(0.0, total_placeable_weight)

    acc = 0.0
    for c in placeables:
        if (v > acc) and (v <= acc + c.probability):
            return c
        else:
            acc += c.probability

    raise RuntimeError('Random value out-of-range')


class Netlist:
    cell_type_count: 'dict[str, int]'
    free_inpins: 'set[str]'
    free_outpins: 'set[str]'
    g: 'nx.DiGraph'
    cells: 'list[tuple[str, str, dict[str, str]]]'
    ports: 'list[str]'

    def __init__(self):
        self.cell_type_count = {}
        self.g = nx.DiGraph()
        self.free_inpins = set()
        self.free_outpins = set()
        self.cells = []
        self.ports = []

    def name_cell(self, c: Cell) -> str:
        if self.cell_type_count.get(c.name) is None:
            self.cell_type_count[c.name] = 0
        ccount = self.cell_type_count[c.name]
        self.cell_type_count[c.name] += 1
        return f'{c.name}_{ccount}'

    def add_cell(self, cell: Cell, **properties: 'str') -> str:
        cell_name = self.name_cell(cell)
        self.cells.append((cell, cell_name, properties))

        for input in cell.inputs:
            name = f'{cell_name}/{input}'
            self.g.add_node(name, cell_instance=cell_name)
            self.free_inpins.add(name)
        for output in cell.outputs:
            name = f'{cell_name}/{output}'
            self.g.add_node(name, cell_instance=cell_name)
            self.free_outpins.add(name)

        return cell_name

    def add_port(self, cell_pin: str, dir: str, name: str):
        self.ports.append(name)
        self.g.add_node(name)

        if dir.lower() == 'in':
            self.g.nodes[name]['net'] = f'net_{name}'
            self.connect_driver_sink(name, cell_pin)
        elif dir.lower() == 'out':
            self.g.nodes[cell_pin]['net'] = f'net_{name}'
            self.connect_driver_sink(cell_pin, name)
        else:
            raise RuntimeError(f'Incorrect pin direction `{dir}`')

    def connect_driver_sink(self, driver: str, sink: str):
        net = self.g.nodes.data('net', default=None)[driver]
        net_name = f'net_{driver}'
        if net is None:
            self.g.nodes[driver]['net'] = net_name
        self.g.nodes[sink]['net'] = net_name

        self.g.add_edge(driver, sink)
        if sink in self.free_inpins:
            self.free_inpins.remove(sink)

    def export_tcl(self) -> str:
        tcl = ''

        for port in self.ports:
            dir = 'IN' if len(self.g.out_edges(port)) > 0 else 'OUT'
            tcl += f'create_port -direction {dir} {port}\n'

        tcl += '\n'

        for (cell, cell_name, properties) in self.cells:
            tcl += f'create_cell -ref {cell.name} {cell_name}\n'
            for (prop_name, prop_value) in properties.items():
                tcl += f'set_property {prop_name} ' + '{' + prop_value + '}' + f' [get_cell {cell_name}]\n'

        tcl += '\n'

        nets = {}
        for (driver, sink) in self.g.edges:
            net = self.g.nodes[driver]['net']
            if net not in nets:
                tcl += f'create_net {net.replace("/", "__")}\n'
                nets[net] = set()

            nets[net].add(driver)
            nets[net].add(sink)

        tcl += '\n'

        for (net, objects) in nets.items():
            tcl += f'connect_net -net {net.replace("/", "__")} -objects ' + '{' + ' '.join(
                objects
            ) + '}\n'

        return tcl


def add_and_connect_cells(netlist: Netlist, no_of_cells: int):
    # Add random cells
    for _ in range(0, no_of_cells):
        cell = random_cell()
        properties = cell.param_randomizer(
        ) if cell.param_randomizer is not None else {}
        netlist.add_cell(cell.cell, **properties)

    # Make random connections
    free_outpins = list(netlist.free_outpins)
    for sink in copy(netlist.free_inpins):
        if len(netlist.g.in_edges(sink)) != 0:
            continue
        driver = random.choice(free_outpins)
        netlist.connect_driver_sink(driver, sink)


def add_io(netlist: Netlist, input_cnt: int, output_cnt: int):
    global io_cells

    in_def = io_cells['in']
    out_def = io_cells['out']

    for i in range(0, input_cnt):
        name = netlist.add_cell(in_def['cell'], **in_def['params'])
        netlist.add_port(f'{name}/{in_def["i"]}', 'IN', f'in{i}')
    for i in range(0, output_cnt):
        name = netlist.add_cell(out_def['cell'], **out_def['params'])
        outpin = f'{name}/{out_def["o"]}'
        netlist.add_port(outpin, 'OUT', f'out{i}')
        netlist.free_outpins.remove(outpin)


def main():
    parser = ArgumentParser()
    parser.add_argument(
        '--cell-count',
        '-c',
        type=int,
        default=10,
        help='Number of cells to place'
    )
    parser.add_argument(
        '--input-count',
        '-I',
        type=int,
        default=8,
        help='Number of inputs to add'
    )
    parser.add_argument(
        '--output-count',
        '-O',
        type=int,
        default=8,
        help='Number of outputs to add'
    )

    args = parser.parse_args()

    netlist = Netlist()
    add_io(netlist, args.input_count, args.output_count)
    add_and_connect_cells(netlist, args.cell_count)

    print(netlist.export_tcl())


if __name__ == '__main__':
    main()
