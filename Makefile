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

PWD = $(shell pwd)
INSTALL_DIR = ${PWD}/third_party/install

MULTIPLE_RUN_ITERATIONS ?= 2

all: format

TOP_DIR := $(realpath $(dir $(lastword $(MAKEFILE_LIST))))
TOOLCHAIN ?= symbiflow
REQUIREMENTS_FILE ?= conf/${TOOLCHAIN}/requirements.txt
ENVIRONMENT_FILE ?= conf/${TOOLCHAIN}/environment.yml

# FIXME: currently the latest links are updated in the latest f4pga release. Fix this to point to the GCP URL bucket as soon as it is back online
SYMBIFLOW_LATEST_URL_BASE = https://github.com/SymbiFlow/f4pga-arch-defs/releases/download/latest
SYMBIFLOW_LATEST_URL = ${SYMBIFLOW_LATEST_URL_BASE}/symbiflow-install-xc7-latest
SYMBIFLOW_DEVICES ?= xc7a50t xc7a100t xc7a200t xc7z010 xc7z020

QUICKLOGIC_URL = https://storage.googleapis.com/symbiflow-arch-defs-install/quicklogic-arch-defs-63c3d8f9.tar.gz

INTERCHANGE_BASE_URL = https://storage.googleapis.com/fpga-interchange-tests/artifacts/prod/foss-fpga-tools/fpga-interchange-tests/continuous/50/20211008-072036
INTERCHANGE_VERSION = 6ff4159
INTERCHANGE_DEVICES ?= xc7a35t xc7a100t xc7a200t xc7z010
RAPIDWRIGHT_PATH = $(TOP_DIR)/third_party/RapidWright


third_party/make-env/conda.mk:
	git submodule init
	git submodule update --init --recursive

include third_party/make-env/conda.mk

env:: | $(CONDA_ENV_PYTHON)

install_symbiflow: | $(CONDA_ENV_PYTHON)
	mkdir -p env/symbiflow
	curl -fsSL ${SYMBIFLOW_LATEST_URL} | xargs curl -fsSL | tar -xJC env/symbiflow
	# Adapt the environment file from symbiflow-arch-defs
	test -e env/symbiflow/xc7_env/xc7_environment.yml && \
		sed -i 's/name: xc7/name: symbiflow-env/g' env/symbiflow/xc7_env/xc7_environment.yml
	cat conf/common/requirements.txt conf/symbiflow/requirements.txt > env/symbiflow/xc7_env/xc7_requirements.txt
	@$(IN_CONDA_ENV_BASE) conda env update --name symbiflow-env --file env/symbiflow/xc7_env/xc7_environment.yml
	# List the actual package versions installed
	@$(CONDA_ACTIVATE) symbiflow-env && conda list
	# Install all devices
	for device in ${SYMBIFLOW_DEVICES}; do \
		curl -fsSL ${SYMBIFLOW_LATEST_URL_BASE}/symbiflow-$${device}_test-latest | xargs curl -fsSL | tar -xJC env/symbiflow; \
	done

install_interchange:
	mkdir -p env/interchange/devices
	curl -fsSL ${INTERCHANGE_BASE_URL}/interchange-techmaps-${INTERCHANGE_VERSION}.tar.xz | tar -xJC env/interchange; \
	for device in ${INTERCHANGE_DEVICES}; do \
		curl -fsSL ${INTERCHANGE_BASE_URL}/interchange-$${device}-${INTERCHANGE_VERSION}.tar.xz | tar -xJC env/interchange/devices; \
	done
	pushd ${RAPIDWRIGHT_PATH} && \
		./gradlew updateJars --no-watch-fs && \
		make compile && \
	popd

install_quicklogic:
	mkdir -p env/quicklogic
	curl -fsSL ${QUICKLOGIC_URL} | tar -xzC env/quicklogic

PYTHON_SRCS=$(shell find . -name "*py" -not -path "./third_party/*" -not -path "./env/*" -not -path "./conf/*" -not -path "./results/env/*")

format: ${PYTHON_SRCS}
	yapf -i $?

clean::
	$(IN_CONDA_ENV_BASE) rm -rf build/

.PHONY: all env build-tools format run-all clean
