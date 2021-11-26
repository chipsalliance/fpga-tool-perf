# Copyright (C) 2021  The Symbiflow Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

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
