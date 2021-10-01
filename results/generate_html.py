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
from generate_stats_page import generate_stats_html
from project_results import ProjectResults


def main():
    env = jinja2.Environment(loader=jinja2.FileSystemLoader('html'))

    parser = ArgumentParser()

    parser.add_argument(
        '-i',
        '--in-dir',
        type=str,
        help='Directory containing json data files'
    )
    parser.add_argument(
        '-o', '--out-dir', type=str, help='Save outputs in a given directory'
    )

    args = parser.parse_args()

    if not os.path.isdir(args.in_dir):
        os.makedirs(args.in_dir)

    graph_template = env.get_template('graphs.html')
    stats_template = env.get_template('stats.html')
    index_template = env.get_template('index.html')

    results = list()
    graph_pages = dict()
    stats_pages = dict()

    for project_name in os.listdir(args.in_dir):
        project_dir = os.path.join(args.in_dir, project_name)
        if not os.path.isdir(project_dir):
            print(f'Skipping `{project_dir}` because it' 's not a directory.')
            continue

        # Do not filter failed tests
        project_results = ProjectResults(project_name, project_dir)
        results.append(project_results)

        stats = generate_stats_html(stats_template, project_results)
        stats_pages[project_name] = stats

        graph = generate_graph_html(graph_template, project_results)
        graph_pages[project_name] = graph

    index_page = generate_index_html(index_template, results)

    if args.out_dir:
        graphs_dir = os.path.join(args.out_dir, 'graphs')
        stats_dir = os.path.join(args.out_dir, 'stats')

        os.makedirs(graphs_dir, exist_ok=True)
        os.makedirs(stats_dir, exist_ok=True)

        # Write graph pages
        for project_name, html in graph_pages.items():
            page_path = os.path.join(graphs_dir, f'{project_name}.html')
            with open(page_path, 'w') as out_file:
                out_file.write(html)

        # Write stats pages
        for project_name, boards in stats_pages.items():
            for board, html in boards.items():
                page_path = os.path.join(
                    stats_dir, f'{project_name}_{board}.html'
                )
                with open(page_path, 'w') as out_file:
                    out_file.write(html)

        index_path = os.path.join(args.out_dir, 'index.html')
        with open(index_path, 'w') as out_file:
            out_file.write(index_page)


if __name__ == "__main__":
    main()
