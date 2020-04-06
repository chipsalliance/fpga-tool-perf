# FIXME: fasm should be installed into the running Python environment.
BASE_DIR=${FPGA_TOOL_PERF_DIR}
export PYTHONPATH="${SYMBIFLOW}/python:$BASE_DIR:$BASE_DIR/third_party/fasm:$BASE_DIR/third_party/edalize:$PYTHONPATH"

# Suppress the following warnings;
# - env/lib/python3.7/distutils/__init__.py:4: DeprecationWarning: the imp module is deprecated in favour of importlib; see the module's documentation for alternative uses
export PYTHONWARNINGS=ignore::DeprecationWarning:distutils
