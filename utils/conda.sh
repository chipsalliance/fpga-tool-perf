# SPDX-License-Identifier: Apache-2.0
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

export CONDA_DIR=$(pwd)/env/conda
export PATH=$CONDA_DIR/bin:${PATH}
(
    if [[ ! -e ${CONDA_DIR}/bin/conda ]]; then
        cd env && \
        wget --no-verbose --continue https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
        chmod a+x Miniconda3-latest-Linux-x86_64.sh
        (
            export HOME=$CONDA_DIR
            ./Miniconda3-latest-Linux-x86_64.sh -p $CONDA_DIR -b -f || exit 1
        )

        conda config --system --add envs_dirs $CONDA_DIR/envs
        conda config --system --add pkgs_dirs $CONDA_DIR/pkgs
    fi
    conda config --system --set always_yes yes
    conda config --system --set changeps1 no
    conda update -q conda

    conda env create --file ../conf/environment.yml
    conda init bash
    source ~/.bashrc

    conda info -a
)
