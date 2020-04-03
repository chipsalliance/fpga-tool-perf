SHELL = bash

PWD = $(shell pwd)
YOSYS_PREFIX = ${PWD}/third_party/yosys/install

all: format

IN_ENV = if [ -e env/bin/activate ]; then . env/bin/activate; fi; source utils/environment.python.sh;
env:
	git submodule update --init --recursive
	virtualenv --python=python3 env
	# Install fasm from third_party
	$(IN_ENV) pip install --upgrade -e third_party/fasm
	# Install edalize from third_party
	$(IN_ENV) pip install --upgrade -e third_party/edalize
	# Install requirements
	$(IN_ENV) pip install -r requirements.txt

build-tools:
	git submodule update --init --recursive
	# Build VtR
	cd third_party/vtr && $(MAKE) -j`nproc`
	# Build Yosys
	cd third_party/yosys && PREFIX=${YOSYS_PREFIX} $(MAKE) -j`nproc` && PREFIX=${YOSYS_PREFIX} $(MAKE) install
	# Build Yosys plugins
	cd third_party/yosys-plugins && export PATH=${PWD}/third_party/yosys:${PATH} && $(MAKE)

run-all:
	./exhaust.py

PYTHON_SRCS=$(shell find . -name "*py" -not -path "./third_party/*" -not -path "./env/*")

format: ${PYTHON_SRCS}
	yapf -i $?

clean:
	rm -rf build/

.PHONY: all env build-tools format run-all clean
