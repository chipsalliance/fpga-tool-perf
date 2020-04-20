#!/bin/bash

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
    conda activate fpga-tool-perf-env

    conda info -a
)
