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

# pip install --user pyverilog
import pyverilog
from pyverilog.vparser.parser import parse
import sys
import os


def port_child(port):
    children = port.children()
    # when register may have more than one
    # but eh this seems to work
    #assert len(children) == 1
    return children[0]


def calc_port_width(m, clks):
    dinn = 0
    doutn = 0
    for port in m.portlist.ports:
        c0 = port_child(port)
        # Connect to clock net, not general I/O
        if c0.name in clks:
            continue

        if c0.width:
            widthn = int(c0.width.msb.value) - int(c0.width.lsb.value) + 1
        else:
            widthn = 1

        if type(c0) is pyverilog.vparser.ast.Input:
            dinn += widthn
        elif type(c0) is pyverilog.vparser.ast.Output:
            doutn += widthn
        else:
            raise ValueError("Bidirectional port not supported")
    return dinn, doutn


def find_iclks(m):
    '''Return input signals containing clock like names'''
    ret = set()
    for port in m.portlist.ports:
        c0 = port_child(port)
        if type(c0) is pyverilog.vparser.ast.Input and c0.name.lower().find(
                'clk') >= 0:
            ret.add(c0.name)
    return ret


def run(src_fn, fout, module=None, top='top', iclks=None, verbose=False):
    ast, directives = parse([src_fn])

    def get_top_module(ast, module=None):
        # Only one module?
        if len(ast.children()) == 1 and len(ast.children()[0].definitions
                                            ) == 1:
            ret = ast.children()[0].definitions[0]
            if module:
                assert ret.name == module
            return ret
        else:
            if not module:
                raise ValueError("Multiple modules and module not given")
            for child in ast.children():
                for m in child.definitions:
                    if m.name == module:
                        return m
            else:
                raise ValueError("Failed to find given module name")

    m = get_top_module(ast, module)
    dut = m.name
    assert type(m) == pyverilog.vparser.ast.ModuleDef

    if iclks is None:
        iclks = find_iclks(m)

    dinn, doutn = calc_port_width(m, iclks)

    fout.write(
        '''\
/*
 * Generated by harness_gen.py
 * From: %s
 */
module %s(input wire clk, input wire stb, input wire di, output wire do);
    localparam integer DIN_N = %u;
    localparam integer DOUT_N = %u;

    reg [DIN_N-1:0] din;
    wire [DOUT_N-1:0] dout;

    reg [DIN_N-1:0] din_shr;
    reg [DOUT_N-1:0] dout_shr;

    always @(posedge clk) begin
        din_shr <= {din_shr, di};
        dout_shr <= {dout_shr, din_shr[DIN_N-1]};
        if (stb) begin
            din <= din_shr;
            dout_shr <= dout;
        end
    end

    assign do = dout_shr[DOUT_N-1];
''' % (os.path.basename(src_fn), top, dinn, doutn)
    )

    for port in m.portlist.ports:
        c0 = port_child(port)

    dini = 0
    douti = 0

    fout.write('    %s dut(\n' % (dut, ))
    for porti, port in enumerate(m.portlist.ports):
        c0 = port_child(port)

        def get_to():
            nonlocal dini
            nonlocal douti

            if c0.width:
                widthn = int(c0.width.msb.value) - int(c0.width.lsb.value) + 1
            else:
                widthn = 1

            # Connect to clock net, not general I/O
            if c0.name in iclks:
                return 'clk'
            elif type(c0) is pyverilog.vparser.ast.Input:
                if c0.width:
                    slice_ = '%u:%u' % (dini + widthn - 1, dini)
                else:
                    slice_ = dini

                dini += widthn
                assert dini <= dinn
                return 'din[%s]' % slice_
            elif type(c0) is pyverilog.vparser.ast.Output:
                if c0.width:
                    slice_ = '%u:%u' % (douti + widthn - 1, douti)
                else:
                    slice_ = douti

                douti += widthn
                assert douti <= doutn
                return 'dout[%s]' % slice_
            else:
                assert 0

        comma = ',' if porti < len(m.portlist.ports) - 1 else ''
        fout.write('            .%s(%s)%s\n' % (c0.name, get_to(), comma))
    fout.write('            );\n')

    fout.write('endmodule\n')


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=
        'Generate a simple wrapper to test synthesizing an arbitrary verilog module'
    )

    parser.add_argument('--verbose', action='store_true', help='')
    parser.add_argument('--top', default='top', help='')
    # if we were really smart we could figure this out maybe
    parser.add_argument(
        '--module',
        default=None,
        help='must be specified if more than one module'
    )
    parser.add_argument(
        '--iclks',
        default=None,
        help='comma separated input clock signal names'
    )
    parser.add_argument('fn_in', help='Verilog file name')
    parser.add_argument(
        'fn_out', default='/dev/stdout', nargs='?', help='Verilog file name'
    )
    args = parser.parse_args()

    iclks = None
    if args.iclks:
        iclks = args.iclks.split(',')
    run(
        args.fn_in,
        open(args.fn_out, 'w'),
        module=args.module,
        top=args.top,
        iclks=iclks,
        verbose=args.verbose
    )


if __name__ == '__main__':
    main()
