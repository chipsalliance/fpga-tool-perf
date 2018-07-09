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
-icebox_hlc2asc.py

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

