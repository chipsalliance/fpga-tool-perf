SHELL = bash

PWD = $(shell pwd)
INSTALL_DIR = ${PWD}/third_party/install

MULTIPLE_RUN_ITERATIONS ?= 2

SYMBIFLOW_ARCHIVE = symbiflow.tar.xz
# FIXME: make this dynamic: https://github.com/SymbiFlow/fpga-tool-perf/issues/75
SYMBIFLOW_URL = "https://storage.googleapis.com/symbiflow-arch-defs/artifacts/prod/foss-fpga-tools/symbiflow-arch-defs/continuous/install/6/20200504-160845/symbiflow-arch-defs-install-3f537c97.tar.xz"

all: format

conda:
	git submodule update --init --recursive
	mkdir -p env
	source utils/conda.sh
	wget -O ${SYMBIFLOW_ARCHIVE} ${SYMBIFLOW_URL}
	tar -xf ${SYMBIFLOW_ARCHIVE} -C env
	rm ${SYMBIFLOW_ARCHIVE}
	cd third_party/prjxray && $(MAKE) build -j`nproc`

run-tests:
	python3 exhaust.py --build_type generic --fail

run-parameters-tests:
	python3 exhaust.py --parameters parameters.json --toolchain vpr --build_type parameters

run-multiple-samples-tests:
	for run in {0..${MULTIPLE_RUN_ITERATIONS}}; do \
		python3 exhaust.py --project blinky --toolchain vpr --build_type multiple-samples --build $$run; \
	done

run-all:
	$(MAKE) run-tests
	$(MAKE) run-parameters-tests
	$(MAKE) run-multiple-samples-tests

PYTHON_SRCS=$(shell find . -name "*py" -not -path "./third_party/*" -not -path "./env/*")

format: ${PYTHON_SRCS}
	yapf -i $?

clean:
	rm -rf build/

.PHONY: all env build-tools format run-all clean
