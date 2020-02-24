all: format

PYTHON_SRCS=$(shell find . -name "*py")

format: ${PYTHON_SRCS}
	yapf -i $?
