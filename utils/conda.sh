#!/bin/bash
#
# Copyright (C) 2020  The SymbiFlow Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

export CONDA_DIR=$(pwd)/env/conda
(
    wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
    bash Miniconda3-latest-Linux-x86_64.sh -p $CONDA_DIR -b && rm Miniconda3-latest-Linux-x86_64.sh

    source $CONDA_DIR/etc/profile.d/conda.sh
    conda config --system --set always_yes yes --set changeps1 no
    conda config --add channels conda-forge
    conda config --add channels symbiflow
    conda update -q conda

    conda install -c symbiflow yosys
    conda install -c symbiflow yosys-plugins
    conda install -c symbiflow vtr=8.0.0.rc2_3935_g7d6424bb0
    conda install -c symbiflow nextpnr-xilinx
    conda install -c symbiflow prjxray
    conda install -c symbiflow pip

    conda activate
    pip install -r conf/requirements.txt
    conda deactivate

    conda info -a
)
