SHELL = bash

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

run-all:
	${IN_ENV} ./exhaust.py

PYTHON_SRCS=$(shell find . -name "*py" -not -path "./third_party/*" -not -path "./env/*")

format: ${PYTHON_SRCS}
	yapf -i $?

.PHONY: all env format run-all
