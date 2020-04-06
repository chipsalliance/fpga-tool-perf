SHELL = bash

PWD = $(shell pwd)
INSTALL_DIR = ${PWD}/third_party/install

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
	cd third_party/vtr && CMAKE_PARAMS="-DCMAKE_INSTALL_PREFIX=${INSTALL_DIR}" $(MAKE) -j`nproc`
	# Build Yosys
	cd third_party/yosys && PREFIX=${INSTALL_DIR} $(MAKE) -j`nproc` && PREFIX=${INSTALL_DIR} $(MAKE) install
	# Build Yosys plugins
	cd third_party/yosys-plugins && export PATH=${INSTALL_DIR}/bin:${PATH} && $(MAKE)

run-all:
	${IN_ENV} ./exhaust.py

PYTHON_SRCS=$(shell find . -name "*py" -not -path "./third_party/*" -not -path "./env/*")

format: ${PYTHON_SRCS}
	yapf -i $?

clean:
	rm -rf build/

.PHONY: all env build-tools format run-all clean
