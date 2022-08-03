#!/bin/bash
#
# Copyright 2018-2022 F4PGA Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

echo
echo "==================================="
echo "Check python utf coding and shebang"
echo "==================================="
echo

ERROR_FILES_SHEBANG=""
ERROR_FILES_UTF_CODING=""
FILES_TO_CHECK=`find . \
    -size +0 -type f \( -name '*.py' \) \
    \( -not -path "*/.*/*" -not -path "*/third_party/*" -not -path "*/env/*" -not -path "*/conf/src/*" \)`

for file in $FILES_TO_CHECK; do
    echo "Checking $file"
    if [[ -x $file  ]]; then
        grep -q "\#\!/usr/bin/env python3" $file || ERROR_FILES_SHEBANG="$ERROR_FILES_SHEBANG $file"
    fi
    grep -q "\#.*coding: utf-8" $file || ERROR_FILES_UTF_CODING="$ERROR_FILES_UTF_CODING $file"
done

if [ ! -z "$ERROR_FILES_SHEBANG" ]; then
    for file in $ERROR_FILES_SHEBANG; do
        echo "ERROR: $file does not have the python3 shebang."
    done
    return 1
fi

if [ ! -z "$ERROR_FILES_UTF_CODING" ]; then
    for file in $ERROR_FILES_UTF_CODING; do
        echo "ERROR: $file does not have the utf encoding set."
    done
    return 1
fi

echo
