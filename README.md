# fpga-tool-perf

Analyze FPGA tool performance (MHz, resources, runtime, etc)

## Setup environment

FPGA tool perf uses the Anaconda (conda) package manager to install and get all the required tools.
Currently, the following tools that are available in conda are:

- vtr
- nextpnr-xilinx
- yosys (+ yosys-plugins)
- prjxray

To setup the conda environment, run the following command:

```bash
make conda
```

FPGA tool perf enables also to run the Vivado EDA tool. The tool is not available in the conda environment and it needs to be installed by the user.
The user needs also to set the `VIVADO_SETTINGS` environmental variable, which points to the `settings64.sh` file to enable Vivado.

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

## Project structure

This section is to describe the structure of this project to better understand its mechanisms.

- the `project` directory contains all the information relative to a specific test. These information include:
  - srcs: all the source files needed to run the test
  - top: top level module name of the design
  - name: project name
  - clocks: all the input clocks of the design
  - toolchains: all the toolchains that are enabled for this project. Moreover, each toolchain has a specific set of available boards with the various constraints files.

- the `src` directory contains all the source files needed to build the test project. It also contains the constraints files relative to the various boards supported.
- the `boards` directory contains a json file describing all the supported boards in this test suite.

## Running

With the conda environment correctly installed, run the following to activate the environment:

```bash
source env.sh
```

Once the environment settings has been sourced, you are ready to proceed with the tests

### Quick start example

```
$ python3 fpgaperf.py --toolchain vivado --project oneblink --board arty
```

or

```
$ python3 fpgaperf.py --toolchain vpr --project oneblink --board basys3
```

For example to compare pure Vivado flow and Yosys -> Vivado flow for an xc7z device the following commands can be run:

```
# Yosys -> Vivado
$ python3 fpgaperf.py --toolchain vivado-yosys --project oneblink --board basys3
# Pure Vivado
$ python3 fpgaperf.py --toolchain vivado --project oneblink --board basys3
```

Use `--help` to see additional parameters for the `fpgaperf.py` script.

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

### Exhaustive build

Use `exhaust.py` to automatically test all projects, toolchain and boards supported

```
$ python3 exhaust.py
```

Its also possible to run a test against a single toolchain and/or project and/or device:
```
$ python3 exhaust.py --project blinky --toolchain nextpnr
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

