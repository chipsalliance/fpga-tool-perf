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
from argparse import ArgumentParser
import os
import shutil

from generate_graph_page import generate_graph_html
from generate_index_page import generate_index_html
from project_results import ProjectResults


def main():
    env = jinja2.Environment(loader=jinja2.FileSystemLoader('html'))

    parser = ArgumentParser()

    parser.add_argument(
        'data_dir', type=str, help='Directory containing json data files'
    )
    parser.add_argument(
        '-o',
        '--out_dir',
        nargs=1,
        type=str,
        help='Save outputs in a given directory'
    )

    args = parser.parse_args()

    if not os.path.isdir(args.data_dir):
        print('Path needs to be a path to a directory')
        exit(-1)

    graph_pages = {}

    graph_viz_template = env.get_template('graphviz.html')
    index_template = env.get_template('index.html')

    results = []

    for project_name in os.listdir(args.data_dir):
        project_dir = os.path.join(args.data_dir, project_name)
        if not os.path.isdir(project_dir):
            print(f'Skipping `{project_dir}` because it' 's not a directory.')
            continue

        project_results = ProjectResults(project_name, project_dir)
        results.append(project_results)

        graph_pages[project_name] = \
            generate_graph_html(graph_viz_template, project_results)

    index_page = generate_index_html(index_template, results)

    if args.out_dir:
        graphs_dir = os.path.join(args.out_dir[0], 'graphs')
        os.makedirs(graphs_dir, exist_ok=True)
        for project_name, html in graph_pages.items():
            page_path = os.path.join(graphs_dir, f'{project_name}.html')
            try:
                with open(page_path, 'w') as out_file:
                    out_file.write(html)
            except Exception as e:
                print(f'Unable to write to the output file {page_path}: {e}')
                exit(-1)

        index_path = os.path.join(args.out_dir[0], 'index.html')
        with open(index_path, 'w') as out_file:
            out_file.write(index_page)


if __name__ == "__main__":
    main()
