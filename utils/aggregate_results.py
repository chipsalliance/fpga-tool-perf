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

import datetime
import gzip
import json
import os
import sys


def main():
    if len(sys.argv) < 3:
        print("Usage {} <directory> <out dir>".format(sys.argv[0]))
        sys.exit(1)

    directory = sys.argv[1]
    now = datetime.datetime.now()
    date_str = now.strftime("%Y%m%d-%H%M%S")
    out_file = f"results-{date_str}.json.gz"
    out_path = os.path.join(sys.argv[2], out_file)

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

    with gzip.open(out_path, "wb") as f:
        f.write(json_byte)


if __name__ == "__main__":
    main()
