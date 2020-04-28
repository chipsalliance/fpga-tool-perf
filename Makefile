SHELL = bash

PWD = $(shell pwd)
INSTALL_DIR = ${PWD}/third_party/install

SYMBIFLOW_ARCHIVE = symbiflow.tar.xz

all: format

conda:
	git submodule update --init --recursive
	mkdir -p env
	source utils/conda.sh
	# FIXME: make this dynamic: https://github.com/SymbiFlow/fpga-tool-perf/issues/75
	wget -O ${SYMBIFLOW_ARCHIVE} "https://storage.googleapis.com/symbiflow-arch-defs/artifacts/prod/foss-fpga-tools/symbiflow-arch-defs/presubmit/install/96/20200428-024849/symbiflow-arch-defs-install-555b32cb.tar.xz"
	tar -xf ${SYMBIFLOW_ARCHIVE} -C env
	rm ${SYMBIFLOW_ARCHIVE}
	cd third_party/prjxray && $(MAKE) build -j`nproc`

run-all:
	python3 exhaust.py

PYTHON_SRCS=$(shell find . -name "*py" -not -path "./third_party/*" -not -path "./env/*")

format: ${PYTHON_SRCS}
	yapf -i $?

clean:
	rm -rf build/

.PHONY: all env build-tools format run-all clean
