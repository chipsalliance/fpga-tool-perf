all: format

PYTHON_SRCS=$(shell find . -name "*py" -not -path "./third_party/*")

format: ${PYTHON_SRCS}
	yapf -i $?
