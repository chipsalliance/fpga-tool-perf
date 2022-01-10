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

SHELL = bash

PYTHON := python3

RESULTS_DIR ?= build-results

IN_ENV = if [ -e env/bin/activate ]; then . env/bin/activate; fi;
env:
	git submodule update --init --recursive
	virtualenv --python=$(PYTHON) env
	$(IN_ENV) pip install --no-cache-dir --upgrade -r requirements.txt

preprocess:
	mkdir -p meta
	$(IN_ENV) python3 process_results.py --in-dir $(RESULTS_DIR) --out-dir meta

build:
	mkdir -p build
	$(IN_ENV) python3 generate_html.py -i meta -o build
	touch build/.nojekyll

clean:
	rm -rf env build meta

.PHONY: clean env fetch build
