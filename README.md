# fpga-tool-perf

## Setup

```
$ git submodule init
$ git submodule update
```
You'll need the following tools in your path:
* yosys
* vpr
* arachne-pnr
* icepack
* icetime
* icebox_hlc2asc

Variables you may need to set:

`SFAD_DIR`
    What: symbiflow-arch-defs repository directory
    Default: ~/symbiflow-arch-defs
    
`ICECUBEDIR`
    What: Lattice iCEcube2 software directory
    Default: /opt/lscc/iCEcube2.2017.08
`RADIANTDIR`
    What: Lattice Radiant software directory
    Default: /opt/lscc/radiant/1.0
    
`VPR`
    What: vpr tool to use
    Default: system path? I've always set this to binary
    ie: export VPR=~/vtr/vpr/vpr


To use VPR you'll need to create architecture XML files
As of this writing [symbiflow-arch-defs dd77600](https://github.com/SymbiFlow/symbiflow-arch-defs/tree/dd77600) 
is known to work

To generate architecture files for vpr:
```
$ ./vpr_xml.sh
```

## Running

Quick start example:
```
$ python3 main.py --toolchain arachne --project oneblink --device "hx8k" --package "ct256"
```

Use --help to see all argument options:
```
$ python3 main.py --help
usage: main.py [-h] [--verbose] [--overwrite] [--family FAMILY]
               [--device DEVICE] [--package PACKAGE] [--strategy STRATEGY]
               [--toolchain TOOLCHAIN] [--list-toolchains] [--project PROJECT]
               [--seed SEED] [--out-dir OUT_DIR] [--pcf PCF]

Analyze tool runtimes

optional arguments:
  -h, --help            show this help message and exit
  --verbose
  --overwrite
  --family FAMILY       Device family
  --device DEVICE       Device within family
  --package PACKAGE     Device package
  --strategy STRATEGY   Optimization strategy
  --toolchain TOOLCHAIN
                        Tools to use
  --list-toolchains
  --project PROJECT     Source code to run on
  --seed SEED           32 bit sSeed number to use, possibly directly mapped
                        to PnR tool
  --out-dir OUT_DIR     Output directory
  --pcf PCF
```

Supported toolchains can be queried as follows:
```
$ python3 main.py  --list-toolchains
Supported toolchains:
arachne
icecube2-lse
icecube2-synpro
icecube2-yosys
radiant-lse
radiant-synpro
spnr
vpr
```

Supported projects can be queried as follows:
```
$ python3 main.py  --list-projects
oneblink
picorv32-wrap
picosoc-hx8kdemo
picosoc-simpleuart-wrap
picosoc-spimemio-wrap
picosoc-wrap
vexriscv-verilog
```

Use exhaust.sh to automatically try project-toolchain permutations:
```
$ ./exhaust.sh -h
Exhaustively try project-toolchain combinations, seeding if possible
usage: exaust.sh [args]
--device <device>         device (default: hx8k)
--package <package>       device package (default: ct256)
--project <project>       run given project only (default: all)
--toolchain <toolchain>   run given toolchain only (default: all)
--pcf <pcf>               pin constraint file (default: none)
--dry                     print commands, don't invoke
--verbose                 verbose output
```

For example:
```
$ ./exhaust.sh --device hx8k --package ct256
```

Its also possible to run against a single toolchain and/or project:
```
$ ./exhaust.sh --device hx8k --package cm81 --project oneblink --toolchain spnr --pcf project/oneblink_lp8k-cm81.pcf
```

See build directory for output. Note in particular [build/all.csv](build/all.csv)

There is also [build/sow.csv](build/sow.csv) (a seed pun), which has seed results processed into min/max rows

Since pcf files are project specific, you can't easily use exaust.sh by itself to test all configurations. If you want to do this, use pcf_test.sh:
```
$ ./pcf_test.sh  -h
Exhaustively run all projects with valid .pcf
usage: pcf_test.sh
--out-prefix <dir>        output directory prefix (default: build)
```
