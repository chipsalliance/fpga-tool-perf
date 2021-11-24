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

import datetime
import gzip
import json
import os
import sys


def main():
    if len(sys.argv) < 3:
        print("Usage {} <directory> <output file>".format(sys.argv[0]))
        sys.exit(1)

    directory = sys.argv[1]
    out_file = sys.argv[2]

    results = dict()
    for f in os.listdir(directory):
        path = os.path.join(directory, f)
        with gzip.open(path, 'r') as file:
            data = json.loads(file.read().decode("utf-8"))

        data_results = data["results"]
        for k, v in data_results.items():
            if k not in results:
                results[k] = list()

            for elem in v:
                results[k].append(elem)

    date = datetime.datetime.utcnow()
    date_str = date.replace(microsecond=0).isoformat()

    json_data = dict()
    json_data["date"] = date_str
    json_data["results"] = results

    json_str = json.dumps(json_data)
    json_byte = json_str.encode("utf-8")

    with gzip.open(out_file, "wb") as f:
        f.write(json_byte)


if __name__ == "__main__":
    main()
