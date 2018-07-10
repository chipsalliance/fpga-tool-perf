# fpga-tool-perf

See run.sh for example invocations

Output goes to build/auto_named_directory

Summary printed at end of run. Also note .json file

You'll need the following tools in your path:
-yosys
-vpr
-arachne-pnr
-icepack
-icetime
-icebox_hlc2asc

also
git submodule init
git submodule update


variables
sfad_build = os.getenv("SFAD_BUILD", os.getenv("HOME") + "/symbiflow-arch-defs/tests/build/ice40-top-routing-virt-hx8k")
    export ARCH=ice40
    cd tests/ice40/iceblink
    make all
    make rr_graph.real.xml
icecubedir = os.getenv("ICECUBEDIR", "/opt/lscc/iCEcube2.2017.08")
radiantdir = os.getenv("RADIANTDIR", "/opt/lscc/radiant/1.0")


To generate architecture files for vpr
(I used symbiflow-arch-defs dd77600)
export VPR=~/vtr/vpr/vpr
cd ~/symbiflow-arch-defs/tests/ice40/tiny-b2_blink
make BOARD=icestick bit
This will generate hx1k-tq144 (about 3 min on carbon x1)
also can easily do:
make BOARD=tinyfpga-b2 bit
to get hx8k-cm81 (about 15 min on carbon x1)

To generate other archs you need to hack around a bit
touch ~/symbiflow-arch-defs/tests/ice40/blink/test-upk5-uwg30.pcf
make BOARD=test-upk5-uwg30 DEVICE=up5k PACKAGE=uwg30 PROG_TOOL=/dev/null bit

To create a performance .csv:
./hx8k.sh

