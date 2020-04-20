SHELL = bash

PWD = $(shell pwd)
INSTALL_DIR = ${PWD}/third_party/install

all: format

conda:
	git submodule update --init --recursive
	mkdir -p env
	source utils/conda.sh

run-all:
	# TODO: enable other toolchains once full support is complete
	./exhaust.py --toolchain vivado-yosys

PYTHON_SRCS=$(shell find . -name "*py" -not -path "./third_party/*" -not -path "./env/*")

format: ${PYTHON_SRCS}
	yapf -i $?

clean:
	rm -rf build/

.PHONY: all env build-tools format run-all clean
