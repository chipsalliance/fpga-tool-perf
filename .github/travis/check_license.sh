#!/bin/bash

# Check SPDX in source files
ERROR_FILES=""

for file in `find . -not -path "./.**" -type f -name "*.sh" -o -name "*.py" -o -name "Makefile"`; do
    grep -q "SPDX-License-Identifier" $file || ERROR_FILES="$ERROR_FILES $file"
done

if [ ! -z "$ERROR_FILES" ]; then
    for file in $ERROR_FILES; do
        echo "ERROR: $file does not have license information."
    done
    return 1
fi

# Check LICENSE file exists for third_party software
ERROR_NO_LICENSE=""
for dir in `ls -d ./third_party/*`; do
    # If the third_party directory is empty skip it as it is a submodule
    if [ "$(ls -A $dir)" ]; then
        [ -f $dir/LICENSE ] || ERROR_NO_LICENSE="$ERROR_NO_LICENSE $dir"
    fi
done

if [ ! -z "$ERROR_NO_LICENSE" ]; then
    for dir in $ERROR_NO_LICENSE; do
        echo "ERROR: $dir does not have the LICENSE file."
    done
    return 1
fi
