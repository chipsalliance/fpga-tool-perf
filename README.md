# fpga-tool-perf

Analyze FPGA tool performance (MHz, resources, runtime, etc)

## Setup

```
$ git submodule init
$ git submodule update
```
You'll need the following tools in your path:
* vivado
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

Once all the required environmental variables are set, run the following:

```
$ source settings.sh
```

To prepare the python environment, run the following target:

```
$ make env
```

To use VPR you'll need to create architecture XML files
As of this writing [symbiflow-arch-defs dd77600](https://github.com/SymbiFlow/symbiflow-arch-defs/tree/dd77600)
is known to work

To generate architecture files for vpr:
```
$ ./vpr_xml.sh
```

### Recommended versions

These "releases" are tool suite combinations known to work well together. Primary testing platform is
Ubuntu 16.04 with some testing on Debian Buster/Sid

#### v0.0.1

Versions:
  * [arachne-pnr](https://github.com/cseed/arachne-pnr.git): git 5d830dd
  * [fpga-tool-perf](https://github.com/SymbiFlow/fpga-tool-perf.git): git v0.0.1
  * [iCEcube2](http://www.latticesemi.com/iCEcube2): release 2017.08.27940
  * [icestorm](https://github.com/elmsfu/icestorm.git) : git 542e9ef
    * Waiting on some PRs as of this writing
  * [nextpnr](https://github.com/YosysHQ/nextpnr.git): git 7da64ee
  * [Radiant](http://www.latticesemi.com/latticeradiant): release 1.0.0.350.6
  * [symbiflow-arch-defs](https://github.com/SymbiFlow/symbiflow-arch-defs.git): git 8232130
  * [vpr](https://github.com/SymbiFlow/vtr-verilog-to-routing.git): git vpr-7.0.5+ice40-v0.0.0
  * [yosys](https://github.com/YosysHQ/yosys.git): git e275692e

## Running

Quick start example:
```
$ python3 fpgaperf.py --toolchain arachne --project oneblink --device "hx8k" --package "ct256"
```
or
```
$ python3 fpgaperf.py --toolchain vivado --project oneblink --family "xc7" --device "a35ti" --package "csg324-1L"
```

For example to compare pure Vivado flow and Yosys -> Vivado flow for an xc7z device the following commands can be run:

```
# Yosys -> Vivado
$ python3 fpgaperf.py --toolchain vivado-yosys --project oneblink --family "xc7" --device "z020" --package "clg400-1"
# Pure Vivado
$ python3 fpgaperf.py --toolchain vivado --project oneblink --family "xc7" --device "z020" --package "clg400-1"
```

Use --help to see all argument options:
```
$ python3 fpgaperf.py --help
usage: fpgaperf.py [-h] [--verbose] [--overwrite] [--family FAMILY]
                   [--device DEVICE] [--package PACKAGE] [--strategy STRATEGY]
                   [--carry] [--no-carry]
                   [--toolchain {arachne,icecube2-lse,icecube2-synpro,icecube2-yosys,nextpnr,radiant-lse,radiant-synpro,vivado,vivado-yosys,vpr}]
                   [--list-toolchains]
                   [--project {baselitex,ibex,murax,oneblink,picorv32,picosoc,picosoc_hx8kdemo,picosoc_simpleuart,picosoc_spimemio,vexriscv}]
                   [--list-projects] [--seed SEED] [--list-seedable]
                   [--check-env] [--out-dir OUT_DIR] [--out-prefix OUT_PREFIX]
                   [--build BUILD]

Analyze FPGA tool performance (MHz, resources, runtime, etc)

optional arguments:
  -h, --help            show this help message and exit
  --verbose
  --overwrite
  --family FAMILY       Device family
  --device DEVICE       Device within family
  --package PACKAGE     Device package
  --strategy STRATEGY   Optimization strategy
  --carry               Force carry / no carry (default: use tool default)
  --no-carry            Force carry / no carry (default: use tool default)
  --toolchain {arachne,icecube2-lse,icecube2-synpro,icecube2-yosys,nextpnr,radiant-lse,radiant-synpro,vivado,vivado-yosys,vpr}
                        Tools to use
  --list-toolchains
  --project {baselitex,ibex,murax,oneblink,picorv32,picosoc,picosoc_hx8kdemo,picosoc_simpleuart,picosoc_spimemio,vexriscv}
                        Source code to run on
  --list-projects
  --seed SEED           31 bit seed number to use, possibly directly mapped to
                        PnR tool
  --list-seedable
  --check-env           Check if environment is present
  --out-dir OUT_DIR     Output directory
  --out-prefix OUT_PREFIX
                        Auto named directory prefix (default: build)
  --build BUILD         Build number
```

Supported toolchains can be queried as follows:
```
$ python3 fpgaperf.py  --list-toolchains
Supported toolchains:
arachne
icecube2-lse
icecube2-synpro
icecube2-yosys
nextpnr
radiant-lse
radiant-synpro
vivado
vivado-yosys
vpr
```

You can check if you have the toolchain environments correctly installed as
follows:
```
$ python3 fpgaperf.py --check-env --toolchain vpr
vpr
  yosys: True
  vpr: True
  icebox_hlc2asc: True
  icepack: True
  icetime: True
```

Supported projects can be queried as follows:
```
$ python3 fpgaperf.py  --list-projects
baselitex
ibex
murax
oneblink
picorv32
picosoc
picosoc_hx8kdemo
picosoc_simpleuart
picosoc_spimemio
vexriscv
```

Use exhaust.py to automatically try project-toolchain permutations:
```
$ python3 exhaust.py --help
usage: exhaust.py [-h] [--family FAMILY] [--device DEVICE] [--package PACKAGE]
                  [--project PROJECT] [--toolchain TOOLCHAIN]
                  [--out-prefix OUT_PREFIX] [--dry] [--fail] [--verbose]

Exhaustively try project-toolchain combinations

optional arguments:
  -h, --help            show this help message and exit
  --family FAMILY       device family
  --device DEVICE       device
  --package PACKAGE     device package
  --project PROJECT     run given project only (default: all)
  --toolchain TOOLCHAIN
                        run given toolchain only (default: all)
  --out-prefix OUT_PREFIX
                        output directory prefix (default: build)
  --dry                 print commands, don't invoke
  --fail                fail on error
  --verbose             verbose output
```

When executed without arguments, exhaust.py will try every project-toolchain-device
permutation. Only permutations with existing constraint files will be built:
```
$ python3 exhaust.py
```

Its also possible to run a test against a single toolchain and/or project and/or device:
```
$ python3 exhaust.py --device hx8k --package cm81 --project oneblink --toolchain nextpnr
```

See build directory for output. Note in particular [build/all.json](build/all.json)


## Development

### Project

Projects are .json files in the project directory. Copy an existing project to
suite your needs. Project names shouldn't contain underscores such that they
are clearly separated from other fields when combined into folder names.

### Wrapper

wrapper.py creates a simple verilog interface against an arbitrary verilog
module. This allows testing arbitrary verilog modules against a standard pin
configuration. The rough idea is taken from project x-ray.

Run wrappers.sh to regenerate all wrappers. Requires pyverilog

wrapper.py (iverilog based) has the following known limitations:
 * Bidrectional ports are not supported
 * Spaces inside numbers are not supported (ex: 8' h00 vs 8'h00)
 * Attributes (sometimes?) are not supported (ex: (* LOC="HERE" *) )

As a result, sometimes the module definition is cropped out to make running the
tool easier (ex: src/picorv32/picosoc/spimemio.v was cropped to
src/picosoc_spimemio_def.v).

### Python

If you change the python code, run the test suite in the test directory:

```
python3 run.py
```

As of this writing it takes about 6 minutes to complete. Note you can also run
a single test:
```
python3 run.py  TestCase.test_env_ready
```

