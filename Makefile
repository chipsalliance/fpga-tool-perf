SHELL = bash

PWD = $(shell pwd)
INSTALL_DIR = ${PWD}/third_party/install

all: format

IN_ENV = if [ -e env/conda/bin/activate ]; then . env/conda/bin/activate; fi;
conda:
	git submodule update --init --recursive
	mkdir -p env
	source utils/conda.sh
	# Install requirements
	$(IN_ENV) pip install -r requirements.txt

run-all:
	# TODO: enable other toolchains once full support is complete
	${IN_ENV} ./exhaust.py --toolchain vivado

PYTHON_SRCS=$(shell find . -name "*py" -not -path "./third_party/*" -not -path "./env/*")

format: ${PYTHON_SRCS}
	yapf -i $?

clean:
	rm -rf build/

.PHONY: all env build-tools format run-all clean
