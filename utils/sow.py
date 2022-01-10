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

import json


def merge(a, b, exclude_keys=[]):
    for key in b:
        if key in exclude_keys:
            continue
        if key in a:
            a[key].append(b[key])
        else:
            a[key] = [b[key]]
    return a


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='Merge B json file into A json file'
    )
    parser.add_argument('fn_a', help='A json file')
    parser.add_argument('fn_b', help='B json file')
    args = parser.parse_args()

    fa = open(args.fn_a, 'r')
    fb = open(args.fn_b, 'r')
    ja = json.load(fa)
    jb = json.load(fb)
    fa.close()
    fb.close()

    # Merge b into a
    ja = merge(ja, jb)

    # Truncate file and write merged json
    fout = open(args.fn_a, 'w')
    json.dump(merged_dict, fout)


if __name__ == '__main__':
    main()
