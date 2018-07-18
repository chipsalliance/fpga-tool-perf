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
python3 main.py --toolchain arachne --project oneblink --device "hx8k" --package "ct256"
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

Supported projects are named after the .json files in the project directory. ie to get all supported projected:
```
$ ls project/*.json |sed "sXproject/\(.*\).jsonX\1X" |sort
oneblink
picorv32-wrap
picosoc-hx8kdemo
picosoc-simpleuart-wrap
picosoc-spimemio-wrap
picosoc-wrap
vexriscv-verilog
```

Additionally, there are a few scripts that exhaustively test all supported invocations and aggregate results:
 * [hx8k.sh](hx8k.sh)
 * [up5k.sh](up5k.sh)
 
See build for output. Note in particular [build/all.csv](build/all.csv)
