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

# Fetch test results from Google Storage

import gzip
import json
import logging
import os
import requests
from argparse import ArgumentParser
from datetime import datetime
from collections import defaultdict
from typing import List
from multiprocessing.pool import ThreadPool

STORAGE_API_AT = 'https://www.googleapis.com/storage/v1/b/fpga-tool-perf/o'
TESTRES_PREFIX = 'artifacts/prod/foss-fpga-tools/fpga-tool-perf'
TEST_RESULT_DELIMITER = 'results-generic-all.json.gz'
DOWNLOAD_BASE_URL = 'https://storage.googleapis.com/fpga-tool-perf'

logger = logging.getLogger(__name__)


# Iterage over all result pages in GCS JSON API.
def iter_result_pages(url: str):
    req_url = url
    while True:
        resp = requests.get(
            url=req_url, headers={'Content-Type': 'application/json'}
        )
        data = resp.json()

        yield data

        next_page_token = data.get('nextPageToken')
        if not next_page_token:
            break
        req_url = f'{url}&pageToken={next_page_token}'


def get_compound_result_file_path(test_run: int, builds: str):
    url = f'{STORAGE_API_AT}?delimiter={TEST_RESULT_DELIMITER}' \
          f'&prefix={TESTRES_PREFIX}/{builds}/{test_run}/'

    for data in iter_result_pages(url):
        prefixes = data.get('prefixes')
        if prefixes:
            return prefixes[0]


def download_meta(path: str, binary: bool = False):
    logger.debug(f'Downloading `{path}`')

    req_url = f'{DOWNLOAD_BASE_URL}/{path}'
    resp = requests.get(
        url=req_url, headers={"Content-Type": "application/json"}
    )

    if not binary:
        return resp.text
    return resp.content


def are_results_compound(prefixes: List[str]):
    return len(prefixes) == 1


def datetime_from_str(s: str):
    return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S')


def merge_results(metas, filter=None):
    earliest_dt = datetime.now()
    projects = defaultdict(lambda: {'results': defaultdict(lambda: [])})

    res_types = [
        'board', 'toolchain', 'runtime', 'resources', 'maximum_memory_use',
        'max_freq', 'device', 'status', 'versions'
    ]

    for meta in metas:
        try:
            dt = datetime_from_str(meta['date'])
            if dt < earliest_dt:
                earliest_dt = dt

            results = projects[meta['project']]['results']

            if filter is not None:
                if not filter(meta):
                    continue

            # This is a rather incomplete list, but it should do the job
            for res_type in res_types:
                results[res_type].append(meta[res_type])

        except KeyError as e:
            logger.debug(f'Skipping a meta file because of {e}')

    for project in projects.values():
        project['date'] = \
            f'{earliest_dt.year}-{earliest_dt.month}-{earliest_dt.day}T' \
            f'{earliest_dt.hour}:{earliest_dt.minute}:{earliest_dt.second}'

    return projects


def get_legacy_metas(gcs_paths: list, test_no: int):
    for path in gcs_paths:
        try:
            meta_json = download_meta(path)
        except requests.exceptions.ConnectionError as e:
            logger.error(f'failed to download {path}: {e}')
            continue
        meta: dict
        try:
            meta = json.loads(meta_json)
        except json.decoder.JSONDecodeError:
            logger.debug('Cannot decode the json from GCS')
            with open(f'faulty_json-{test_no}.json', 'w') as f:
                f.write(meta_json)
            continue
        yield meta


def download_and_merge_legacy(gcs_paths: list, test_no: int):
    def accept_generic_all_build_only(meta):
        return meta['build_type'] == 'generic-all' and meta['build'] == '000'

    metas = get_legacy_metas(gcs_paths, test_no)
    merged = merge_results(metas, filter=accept_generic_all_build_only)
    return merged


def download_and_split_compound(gcs_compound_path: str):
    meta_json_gz = download_meta(gcs_compound_path, binary=True)
    meta_json = gzip.decompress(meta_json_gz).decode()
    meta = json.loads(meta_json)

    projects = defaultdict(lambda: {'results': defaultdict(lambda: [])})

    meta_results = meta['results']

    meta_projects = meta_results['project']

    for idx, project in enumerate(meta_projects):
        project_res = projects[project]['results']

        for k, v in meta_results.items():
            if k in ['project']:
                continue

            project_res[k].append(v[idx])

    for project in projects.values():
        project['date'] = meta['date']

    return projects


def get_test_run_numbers(start: int, end: str, builds: str):
    url = f'{STORAGE_API_AT}?delimiter=/&prefix={TESTRES_PREFIX}/{builds}/'

    for data in iter_result_pages(url):
        for prefix in data['prefixes']:
            no = int(prefix.split('/')[-2])
            if no >= start and (end == '_' or no <= int(end)):
                yield no


# -------------------------------------------------------------------- #


def get_download_specs(test_info):
    test_no = test_info['test_no']
    builds = test_info['builds']

    logger.debug(f'Preparing downloads for test {test_no}')
    gcs_compound_path = None
    try:
        gcs_compound_path = get_compound_result_file_path(test_no, builds)
    except Exception as e:
        logging.error(
            f'Failed to fetch patches for test run no. {test_no}, cause: {e}'
        )
        return None

    if gcs_compound_path:
        return dict(test_no=test_no, paths=gcs_compound_path, compound=True)

    return None


def download_from_specs(specs):
    test_no = specs['test_no']
    if specs['compound']:
        merged = download_and_split_compound(specs['paths'])
    else:
        merged = download_and_merge_legacy(specs['paths'], test_no)

    for project_name, merged_data in merged.items():
        project_dir = os.path.join(specs['output_dir'], project_name)
        out_filename = os.path.join(project_dir, f'meta-{test_no}.json')
        os.makedirs(project_dir, exist_ok=True)
        merged_json = json.dumps(merged_data, indent=4)
        with open(out_filename, 'w') as f:
            f.write(merged_json)

    logger.debug(f'Downloaded test no. {test_no}')


def main():
    parser = ArgumentParser()
    parser.add_argument(
        '--builds', type=str, help='Builds type (e.g. `nightly`)'
    )
    parser.add_argument('--from-build', type=int, help='First test run number')
    parser.add_argument(
        '--to-build',
        default="_",
        type=str,
        help='Last test run number (use `_` for "latest")'
    )
    parser.add_argument(
        '--output-dir', type=str, help='Output directory for downloaded data'
    )
    parser.add_argument(
        '--pool-size', type=int, default=8, help='Size of thread pool'
    )
    parser.add_argument(
        '--verbose', action='store_true', help='Print DEBUG Statements'
    )
    args = parser.parse_args()

    if args.verbose:
        global logger
        logger = logging.getLogger('MyLogger')
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

    if not os.path.isdir(args.output_dir):
        logger.error('Output path is not a directory!')
        exit(-1)

    logger.debug(f'Using {args.pool_size} parallel threads.')
    pool = ThreadPool(args.pool_size)
    test_numbers = list(
        get_test_run_numbers(args.from_build, args.to_build, args.builds)
    )

    logger.debug('Preparing downloads ...')
    tests = [
        dict(test_no=test_no, builds=args.builds) for test_no in test_numbers
    ]
    download_specs = pool.map(get_download_specs, tests)
    download_specs = list(
        filter(None, download_specs)
    )  # removelogger.debug None resulting from errors

    for specs in download_specs:
        specs['output_dir'] = args.output_dir

    url_count = 0
    for specs in download_specs:
        if not specs['compound']:
            url_count += len(specs['paths'])
        else:
            url_count += 1

    logger.debug(f'Downloading {url_count} URLs ...')
    pool.map(download_from_specs, download_specs)

    logger.debug('Download completed!')


if __name__ == "__main__":
    main()
