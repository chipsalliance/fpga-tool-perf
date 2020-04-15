#!/usr/bin/env bash
# Copyright (C) 2020  The SymbiFlow Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

set -ex

# Jenkins script

# JOB_NAME=fpga-tool-perf
# BUILD_NUMBER=0
# Don't clean workspace
# quick about 12 min
# long => at least 4 hours
QUICK=N

PREFIX=/opt/fpga-tool-perf/$JOB_NAME/prefix/
rm -rf $PREFIX
mkdir $PREFIX
META_DIR=/opt/fpga-tool-perf/$JOB_NAME/data/$BUILD_NUMBER
MAKEP="make PREFIX=$PREFIX"

# Build yosys
# Everything currently uses yosys
pushd yosys
$MAKEP -j$(nproc)
$MAKEP install
popd

if [ "$RUN_ARACHNE" = true -o "$RUN_NEXTPNR" = true -o "$RUN_VPR" = true ] ; then
  # Build icestorm
  pushd icestorm
  $MAKEP -j$(nproc)
  $MAKEP install
  popd
fi

# Build arachne
if [ "$RUN_ARACHNE" = true ] ; then
  pushd arachne-pnr
  $MAKEP -j$(nproc)
  $MAKEP install
  popd
fi

# Build nextpnr
if [ "$RUN_NEXTPNR" = true ] ; then
  pushd nextpnr
  mkdir build || true
  cd build
  cmake -DCMAKE_INSTALL_PREFIX=$PREFIX -DARCH=ice40 ..
  make -j$(nproc)
  make install
  popd
fi

# Build VPR
if [ "$RUN_VPR" = true ] ; then
  pushd vtr-verilog-to-routing
  mkdir build || true
  cd build
  cmake -DCMAKE_INSTALL_PREFIX=$PREFIX ..
  make -j$(nproc)
  make install
  cd ..
  export VPR=$PWD/vpr/vpr
  stat $VPR
  popd
fi

pushd symbiflow-arch-defs
export SFAD_DIR=$PWD
popd

# build VPR XML
if [ "$RUN_VPR" = true -a "$QUICK" != Y ] ; then
  pushd fpga-tool-perf
  ./vpr_xml.sh
  popd
fi

export PATH=$PREFIX/bin/:$PATH


# Tools built, do the real work
cd fpga-tool-perf

# Verify basic operation
# if tools keep breaking, maybe just warn on this
pushd test
python3 test_all.py
popd
rm -rf build
# Now run the full suite
if [ "$QUICK" = Y ] ; then
    ./exhaust.sh --toolchain icecube2-synpro --project oneblink
    ./exhaust.sh --toolchain vpr --project oneblink
fi
if [ "$RUN_ARACHNE" = Y ] ; then
    ./exhaust.sh --toolchain arachne
fi
if [ "$RUN_ICECUBE2" = Y ] ; then
    ./exhaust.sh --toolchain icecube2-yosys
    ./exhaust.sh --toolchain icecube2-lse
    ./exhaust.sh --toolchain icecube2-synpro
fi
if [ "$RUN_NEXTPNR" = Y ] ; then
    ./exhaust.sh --toolchain nextpnr
fi
if [ "$RUN_RADIANT" = Y ] ; then
    #./exhaust.sh --toolchain radiant-yosys
    ./exhaust.sh --toolchain radiant-lse
    ./exhaust.sh --toolchain radiant-synpro
fi
if [ "$RUN_VPR" = Y ] ; then
    ./exhaust.sh --toolchain vpr
fi


# Export current run
mkdir $META_DIR
# ISO format date
date -u +"%Y-%m-%dT%H:%M:%SZ" >$META_DIR/date.txt
pushd build
cp --parents $(find . -name "*.csv") $META_DIR
cp --parents $(find . -name "*.json") $META_DIR
popd

# TODO: post process
# python3 graph.py

