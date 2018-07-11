# fpga-tool-perf

Setup

$ git submodule init
$ git submodule update

You'll need the following tools in your path:
-yosys
-vpr
-arachne-pnr
-icepack
-icetime
-icebox_hlc2asc

Variables you may need to set:
SFAD_DIR
    What: symbiflow-arch-defs repository directory
    Default: ~/symbiflow-arch-defs
ICECUBEDIR
    What: Lattice iCEcube2 software directory
    Default: /opt/lscc/iCEcube2.2017.08
RADIANTDIR
    What: Lattice Radiant software directory
    Default: /opt/lscc/radiant/1.0
VPR
    What: vpr tool to use
    Default: system path? I've always set this to binary
    ie: export VPR=~/vtr/vpr/vpr


To use VPR you'll need to create architecture XML files
As of this writing symbiflow-arch-defs dd77600 is known to work

To generate architecture files for vpr:
$ ./vpr_xml.sh

Sampe invocations:
-hx8k.sh
-up5k.sh
See build for output. Note in particular build/all.csv

