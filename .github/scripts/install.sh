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

set -e

echo '::group::Installing packages'
$(command -v sudo) apt update -qq
DEBIAN_FRONTEND=noninteractive $(command -v sudo) apt install -qq -y --no-install-recommends \
  curl \
  git \
  make \
  python3 \
  python3-pip \
  wget \
  unzip \
  default-jdk \
  xz-utils \
  libtinfo5 \
  locales
echo '::endgroup::'

echo '::group::Locales setup'
$(command -v sudo) locale-gen en_US.UTF-8
$(command -v sudo) dpkg-reconfigure --frontend=noninteractive locales
echo '::endgroup::'

echo '::group::Installing Python packages'
python3 -m pip install -r conf/requirements.txt
echo '::endgroup::'

USE_VIVADO=""
RW_LINK=""
TOOLCHAIN=""
BOARD=""
while getopts vl:t:b: opt; do
  case "${opt}" in
    v) USE_VIVADO="TRUE";;
    l) RW_LINK=${OPTARG};;
    t) TOOLCHAIN=${OPTARG};;
    b) BOARD=${OPTARG};;
    *) echo "ERROR: option not recognized!"; exit ;;
  esac
done

if [ ! -z "$USE_VIVADO" ]; then
  echo '::group::Creating Vivado Symbolic Link'
  ln -s /mnt/aux/Xilinx /opt/Xilinx
  echo "Available Vivado versions:"
  find /opt/Xilinx/Vivado/ -regex ".*[0-90-90-90-9].[0-9]/settings64.sh" \
    -exec bash -c "echo {} | sed \"s/.*\([0-9]\{4\}\.[0-9]\).*/- \1/g\"" \;
  echo '::endgroup::'
fi

if [ ! -z "$RW_LINK" ]; then
  echo '::group::Export RapidWright JARs Link'
  export RW_LINK=$RW_LINK
  echo '::endgroup::'
fi

echo '::group::Generate Test environment'
eval $(PYTHONPATH=$(pwd) ./.github/scripts/get_env_cmd.py $TOOLCHAIN $BOARD)
echo '::endgroup::'
