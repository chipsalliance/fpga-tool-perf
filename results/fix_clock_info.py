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
""" Unify clock names in legacy data """

from argparse import ArgumentParser
import os
import re
import json


def create_renames_dict(renames_file_path: str):
    data: dict
    with open(renames_file_path, 'r') as f:
        data = json.loads(f.read())

    rd = {}

    for project, clocks in data.items():
        projdict = {}
        for rename_to, rename_from_list in clocks.items():
            for rename_from in rename_from_list:
                projdict[rename_from] = rename_to

        rd[project] = projdict

    return rd


def unify_clock_name(project: str, clock_name: str, renames_dict: dict):
    projdict = renames_dict.get(project)
    if not projdict:
        return clock_name
    new_name = projdict.get(clock_name)
    if not new_name:
        return clock_name
    return new_name


def fix_clocks(project: str, data: dict, renames_dict: dict):
    new_max_freq = []
    for clock_entries in data['results']['max_freq']:
        new_entries = {}
        # icebreaker fix
        if type(clock_entries) is float:
            new_entries = {
                'clk': {
                    'actual': clock_entries,
                    'hold_violation': 0.0,
                    'met': True,
                    'requested': 0.0,
                    'setup_violation': 0.0
                }
            }
        else:
            for clock_name, clock_values in clock_entries.items():
                new_name = unify_clock_name(project, clock_name, renames_dict)
                if new_name != clock_name:
                    print(f'{clock_name} -> {new_name}')
                new_entries[new_name] = clock_values

        new_max_freq.append(new_entries)

    data['results']['max_freq'] = new_max_freq


def main():
    parser = ArgumentParser()
    parser.add_argument('meta_dir', type=str)
    parser.add_argument('renames_file', type=str)
    parser.add_argument('from_no', type=int)
    parser.add_argument('to_no', type=int)

    args = parser.parse_args()

    if not os.path.isdir(args.meta_dir):
        print('`meta_dir` has to be a valid directory path')
        exit(-1)

    renames_dict = create_renames_dict(args.renames_file)

    for project in os.listdir(args.meta_dir):
        subdir = os.path.join(args.meta_dir, project)
        if not os.path.isdir(subdir):
            continue

        for meta in os.listdir(subdir):
            m = re.match('meta-([0-9]*)\\.json', meta)
            if not m:
                continue

            fpath = os.path.join(subdir, meta)
            no = int(m.groups()[0])
            if (no < args.from_no) or (no > args.to_no):
                continue

            print(f'Fixing `{fpath}`')

            data: dict
            with open(fpath, 'r') as f:
                data = json.loads(f.read())

            fix_clocks(project, data, renames_dict)

            with open(fpath, 'w') as f:
                f.write(json.dumps(data, indent=4))
