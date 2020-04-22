SHELL = bash

PWD = $(shell pwd)
INSTALL_DIR = ${PWD}/third_party/install

all: format

conda:
	git submodule update --init --recursive
	mkdir -p env
	source utils/conda.sh
	# FIXME: make this dynamic
	wget "https://storage.googleapis.com/symbiflow-arch-defs/artifacts/prod/foss-fpga-tools/symbiflow-arch-defs/continuous/install/4/20200416-002215/symbiflow-arch-defs-install-a321d9d9.tar.xz"
	tar -xf symbiflow-arch-defs-install-a321d9d9.tar.xz -C env
	rm symbiflow-arch-defs-install-a321d9d9.tar.xz

run-all:
	./exhaust.py

PYTHON_SRCS=$(shell find . -name "*py" -not -path "./third_party/*" -not -path "./env/*")

format: ${PYTHON_SRCS}
	yapf -i $?

clean:
	rm -rf build/

.PHONY: all env build-tools format run-all clean
