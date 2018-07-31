#!/usr/bin/env bash

set -ex

if [ '!' -d "$SFAD_DIR" ] ; then
    echo "SFAD_DIR invalid. Expect symbiflow-arch-defs directory"
    exit 1
fi

# FIXME: as of this writing SFAD has broken vpr in conda
# https://github.com/SymbiFlow/fpga-tool-perf/issues/10
if [ -z "$VPR" ] ; then
    echo "VPR invalid"
    exit 1
fi

cd $SFAD_DIR/ice40/tests/blink || cd $SFAD_DIR/tests/ice40/blink

# hx1k (about 3 min on carbon x1)
echo "Building hx1k XML"
time make BOARD=icestick dist-clean rr_graph.real.xml &>icestick.txt
exit 1
# hx8k (about 15 min on carbon x1)
echo "Building hx8k XML"
time make BOARD=tinyfpga-b2 dist-clean rr_graph.real.xml &>tinyfpga-b2.txt

# up5k
touch test-upk5-uwg30.pcf
echo "Building up5k XML"
time make BOARD=test-upk5-uwg30 DEVICE=up5k PACKAGE=uwg30 PROG_TOOL=/dev/null rr_graph.real.xml  &>test-upk5-uwg30.txt

