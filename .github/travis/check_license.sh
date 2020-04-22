#!/bin/bash

# Check SPDX in source files
ERROR_FILES=""
FILES_TO_CHECK=`find . \
    -type f \( -name '*.sh' -o -name '*.py' -o -name 'Makefile' \) \
    \( -not -path "*/.*/*" -not -path "*/third_party/*" \)`

for file in $FILES_TO_CHECK; do
    grep -q "SPDX-License-Identifier" $file || ERROR_FILES="$ERROR_FILES $file"
done

if [ ! -z "$ERROR_FILES" ]; then
    for file in $ERROR_FILES; do
        echo "ERROR: $file does not have license information."
    done
    return 1
fi

# Check LICENSE file exists for third_party software

function check_if_submodule {
    for submodule in `git submodule --quiet foreach 'echo $sm_path'`; do
        if [ "$1" == "$submodule" ]; then
            return 1
        fi
    done
}

THIRD_PARTY_DIRS=`ls -d third_party/*`
ERROR_NO_LICENSE=""
for dir in $THIRD_PARTY_DIRS; do
    # Checks if we are not in a submodule
    if check_if_submodule $dir; then
        [ -f $dir/LICENSE ] || ERROR_NO_LICENSE="$ERROR_NO_LICENSE $dir"
    fi
done

if [ ! -z "$ERROR_NO_LICENSE" ]; then
    for dir in $ERROR_NO_LICENSE; do
        echo "ERROR: $dir does not have the LICENSE file."
    done
    return 1
fi
