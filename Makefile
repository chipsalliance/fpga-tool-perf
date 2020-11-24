# Copyright (C) 2020  The SymbiFlow Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

SHELL = bash

PWD = $(shell pwd)
INSTALL_DIR = ${PWD}/third_party/install

MULTIPLE_RUN_ITERATIONS ?= 2

all: format

TOP_DIR := $(realpath $(dir $(lastword $(MAKEFILE_LIST))))
TOOLCHAIN ?= symbiflow
REQUIREMENTS_FILE ?= conf/${TOOLCHAIN}/requirements.txt
ENVIRONMENT_FILE ?= conf/${TOOLCHAIN}/environment.yml

ENABLE_FAIL :=
ifeq ($(FAIL),1)
ENABLE_FAIL := --fail
endif


# FIXME: make this dynamic: https://github.com/SymbiFlow/fpga-tool-perf/issues/75
SYMBIFLOW_ARCHIVE = symbiflow.tar.xz
SYMBIFLOW_URL = https://storage.googleapis.com/symbiflow-arch-defs/artifacts/prod/foss-fpga-tools/symbiflow-arch-defs/continuous/install/98/20201120-093358/symbiflow-arch-defs-install-d5f8ce8d.tar.xz
QUICKLOGIC_ARCHIVE = quicklogic.tar.xz
QUICKLOGIC_URL = https://quicklogic-my.sharepoint.com/:u:/p/kkumar/EWuqtXJmalROpI2L5XeewMIBRYVCY8H4yc10nlli-Xq79g?download=1

third_party/make-env/conda.mk:
	git submodule init
	git submodule update --init --recursive

include third_party/make-env/conda.mk

env:: | $(CONDA_ENV_PYTHON)

install_symbiflow:
	mkdir -p env/symbiflow
	wget -O ${SYMBIFLOW_ARCHIVE} ${SYMBIFLOW_URL}
	tar -xf ${SYMBIFLOW_ARCHIVE} -C env/symbiflow
	rm ${SYMBIFLOW_ARCHIVE}
	# Adapt the environment file from symbiflow-arch-defs
	test -e env/symbiflow/environment.yml && sed -i 's/symbiflow_arch_def_base/symbiflow-env/g' env/symbiflow/environment.yml || true
	cat conf/common/requirements.txt conf/symbiflow/requirements.txt > env/symbiflow/requirements.txt

install_quicklogic:
	mkdir -p env/quicklogic
	wget -O ${QUICKLOGIC_ARCHIVE} ${QUICKLOGIC_URL}
	tar -xf ${QUICKLOGIC_ARCHIVE} -C env/quicklogic
	rm ${QUICKLOGIC_ARCHIVE}

run-tests:
	@$(IN_CONDA_ENV) python3 exhaust.py --build_type generic-all ${ENABLE_FAIL}

run-parameters-tests:
	@$(IN_CONDA_ENV) python3 exhaust.py --parameters parameters.json --toolchain vpr --project blinky --build_type parameters --only_required

run-multiple-samples-tests:
	@$(IN_CONDA_ENV) python3 exhaust.py --build_type multiple-samples --run_config run_configs/multiple_samples.json --only_required

run-all-multiple-samples-tests:
	@$(IN_CONDA_ENV) python3 exhaust.py --build_type all-multiple-samples --run_config run_configs/all_multiple_samples.json --only_required

run-seedable-tests:
	@$(IN_CONDA_ENV) python3 exhaust.py --build_type multiple-seeds --run_config run_configs/multiple_seeds.json --only_required

run-all-seedable-tests:
	@$(IN_CONDA_ENV) python3 exhaust.py --build_type all-multiple-seeds --run_config run_configs/all_multiple_seeds.json --only_required

run-all-devices-tests:
	@$(IN_CONDA_ENV) python3 exhaust.py --project oneblink blinky picosoc-simpleuart

run-all:
	$(MAKE) run-tests
	$(MAKE) run-parameters-tests
	$(MAKE) run-multiple-samples-tests
	$(MAKE) run-seedable-tests

PYTHON_SRCS=$(shell find . -name "*py" -not -path "./third_party/*" -not -path "./env/*" -not -path "./conf/*")

format: ${PYTHON_SRCS}
	yapf -i $?

clean::
	rm -rf build/

.PHONY: all env build-tools format run-all clean
