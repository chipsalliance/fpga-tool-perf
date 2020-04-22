#!/bin/bash

BASE_DIR=${FPGA_TOOL_PERF_BASE_DIR}
# FIXME: fasm should be installed into the running Python environment.
export PYTHONPATH="${SYMBIFLOW}/bin/python:$PYTHONPATH"

# Suppress the following warnings;
# - env/lib/python3.7/distutils/__init__.py:4: DeprecationWarning: the imp module is deprecated in favour of importlib; see the module's documentation for alternative uses
export PYTHONWARNINGS=ignore::DeprecationWarning:distutils
