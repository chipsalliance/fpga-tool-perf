SHELL = bash

PWD = $(shell pwd)
INSTALL_DIR = ${PWD}/third_party/install

MULTIPLE_RUN_ITERATIONS ?= 2

all: format

TOP_DIR := $(realpath $(dir $(lastword $(MAKEFILE_LIST))))
TOOLCHAIN ?= symbiflow
REQUIREMENTS_FILE := conf/$(TOOLCHAIN)/requirements.txt
ENVIRONMENT_FILE := conf/$(TOOLCHAIN)/environment.yml

SYMBIFLOW_ARCHIVE = symbiflow.tar.xz
# FIXME: make this dynamic: https://github.com/SymbiFlow/fpga-tool-perf/issues/75
SYMBIFLOW_URL = "https://storage.googleapis.com/symbiflow-arch-defs/artifacts/prod/foss-fpga-tools/symbiflow-arch-defs/presubmit/install/599/20200819-032039/symbiflow-arch-defs-install-918694f9.tar.xz"
ifeq ("${TOOLCHAIN}", "quicklogic")
SYMBIFLOW_ARCHIVE = quicklogic.tar.xz
SYMBIFLOW_URL = https://quicklogic-my.sharepoint.com/:u:/p/kkumar/Eb7341Bq-XRAukVQ6oQ6PrgB-qdFbrsrPEON1yTa4krFSA?download=1
endif

third_party/make-env/conda.mk:
	git submodule init
	git submodule update --init --recursive

include third_party/make-env/conda.mk

env:: | $(CONDA_ENV_PYTHON)
	mkdir -p env/${TOOLCHAIN}
	wget -O ${SYMBIFLOW_ARCHIVE} ${SYMBIFLOW_URL}
	tar -xf ${SYMBIFLOW_ARCHIVE} -C env/${TOOLCHAIN}
	rm ${SYMBIFLOW_ARCHIVE}
ifeq ("${TOOLCHAIN}", "quicklogic")
	cp -r env/conda/envs/quicklogic/share/yosys/* env/conda/envs/quicklogic/share/
	sed -i "s/\/home\/kkumar\/symbiflow-arch-defs\/build\/env\/conda\/bin\/python3/\/usr\/bin\/env python3/" env/${TOOLCHAIN}/install/bin/python/qlfasm #fix path to interpreter, see https://github.com/QuickLogic-Corp/quicklogic-fpga-toolchain/issues/16
endif

run-tests:
	@$(IN_CONDA_ENV) python3 exhaust.py --build_type generic --fail

run-parameters-tests:
	@$(IN_CONDA_ENV) python3 exhaust.py --parameters parameters.json --toolchain vpr --project blinky --build_type parameters

run-multiple-samples-tests:
	@$(IN_CONDA_ENV) python3 exhaust.py --build_type multiple-samples --run_config run_configs/multiple_samples.json

run-seedable-tests:
	@$(IN_CONDA_ENV) python3 exhaust.py --build_type multiple-seeds --run_config run_configs/multiple_seeds.json

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
