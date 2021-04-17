# fpga-tool-perf

Analyze FPGA tool performance (MHz, resources, runtime, etc)

## Setup environment

fpga-tool-perf uses the Miniconda (conda) package manager to install and get all the required tools.
Currently, the following tools that are available in conda are:

- vtr
- nextpnr-xilinx
- yosys (+ yosys-plugins)
- prjxray

Prior to setting up the conda environment, the symbiflow and quicklogic data files need to be installed through the following commands:

```bash
make install_symbiflow
make install_quicklogic
```

The install packages are extracted in the `env/<toolchain>/` location.

To setup the conda environment, run the following commands:

```bash
TOOLCHAIN=symbiflow make env
TOOLCHAIN=quicklogic make env
TOOLCHAIN=nextpnr make env
```

fpga-tool-perf can also run the Vivado EDA tool. The tool is not available in the conda environment and it needs to be installed by the user.
The user needs also to set the `VIVADO_SETTINGS` environmental variable, which points to the `settings64.sh` file to enable Vivado.

## Running

With the conda environment correctly installed, run the following to activate the environment:

```bash
source env.sh
```

Once the environment settings has been sourced, you are ready to proceed with the tests

### Quick start example

```bash
python3 fpgaperf.py toolchain=vivado project=oneblink board=arty-a35t
```

or

```bash
python3 fpgaperf.py toolchain=vpr project=oneblink board=basys3
```

For example to compare pure Vivado flow and Yosys -> Vivado flow for an xc7z device the following commands can be run:

```bash
# Yosys -> Vivado
python3 fpgaperf.py toolchain=yosys-vivado project=oneblink board=basys3
# Pure Vivado
python3 fpgaperf.py toolchain=vivado project=oneblink board=basys3
```

Use `--help` to see additional parameters for the `fpgaperf.py` script.

Supported toolchains can be queried as follows:
```bash
$ python3 fpgaperf.py list=toolchains
nextpnr-ice40
nextpnr-xilinx
nextpnr-xilinx-fasm2bels
vivado
vpr
vpr-fasm2bels
yosys-vivado
```

You can check if you have the toolchain environments correctly installed as
follows:
```bash
$ python3 fpgaperf.py check=env toolchain=vpr
vpr
  yosys: True
  vpr: True
  prjxray-config: True
```

Supported projects can be queried as follows:
```bash
$ python3 fpgaperf.py  list=projects
baselitex
blinky
bram-n1
bram-n2
bram-n3
dram-test-64x1d
hamsternz-hdmi
ibex
murax
oneblink
picorv32
picosoc
picosoc-simpleuart
picosoc-spimemio
vexriscv
vexriscv-smp
```

### Exhaustive build
  
Use `fpgaperf.py` to automatically test all projects, toolchain and boards supported

```bash
python3 fpgaperf.py
```

Its also possible to run a test against specific project(s), toolchain(s), and/or board(s):
```bash
python3 exhaust.py --project blinky oneblink --toolchain vpr
```

See `build` directory for output. Note in particular `all.json`.

### Parallel build

To build multiple benchmarks in parallel on a multi-core machine, use:
```bash
python3 fpgaperf.py --multirun hydra/launcher=joblib project=blinky,oneblink toolchain=vpr board=basys3
``` 

It's also possible to run multiple benchmarks on a slurm cluster (e.g. [slurm-gcp](https://github.com/SchedMD/slurm-gcp)) in parallel:
```bash
python3 fpgaperf.py --multirun hydra/launcher=slurm project=blinky,oneblink toolchain=vpr board=basys3
```

## Project Structure

This section describes the structure of this project to better understand its mechanisms.

- the `project` directory contains all the information relative to a specific test. This includes:
  - srcs: all the source files needed to run the test
  - top: top level module name of the design
  - name: project name
  - data: all of the data/memory files needed to run the test
  - clocks: all the input clocks of the design
  - required\_toolchains: all the toolchains that are required to correctly run to completion.
  - vendors: all the vendors that are enabled for this project (e.g. xilinx, lattice). Each vendor requires a list of boards enabled for the test project.

- the `src` directory contains all the source files needed to build the test project. It also contains the constraints files relative to the various boards supported.
- the `other` directory contains two json files, describing all the supported boards and vendors in this test suite.
- the `toolchains` directory contains the python scripts that enable a toolchain to be run within fpga-tool-perf.
- the `infrastructure` directory contains python scripts to control the fpga-tool-perf framework to run the tests

## Development

### Wrapper

`wrapper.py` creates a simple verilog interface against an arbitrary verilog module.
This allows testing arbitrary verilog modules against a standard pin configuration. The rough idea is taken from project x-ray.

Run `wrappers.sh` to regenerate all wrappers. Requires pyverilog

`wrapper.py` (iverilog based) has the following known limitations:
 * Bidrectional ports are not supported
 * Spaces inside numbers are not supported (ex: 8' h00 vs 8'h00)
 * Attributes (sometimes?) are not supported (ex: (* LOC="HERE" *) )

As a result, sometimes the module definition is cropped out to make running the tool easier
(ex: src/picorv32/picosoc/spimemio.v was cropped to src/picosoc_spimemio_def.v).

### Project

Projects are .json files in the project directory. Project names shouldn't contain underscores such that they are clearly separated from other fields when combined into folder names.

### Inserting a New Project into fpga-tool-perf

These are the basic steps to inserting an existing project into fpga-tool-perf:

#### *Step 1.*
Add a folder within `fpga-tool-perf/src` under the name of the project (make sure there are no underscores '_' in the name). For example, for the project named counter:
```
cd ~/fpga-tool-perf/src
mkdir counter
cd counter
```
Add the source (verilog) and data/memory files to this directory.

Create a `constr` subdirectory, and within it, add the project's `.pcf` (for symbiflow) and `.xdc` (for vivado) files under the name of the board it uses.
```
mkdir constr
touch constr/basys3.pcf
touch constr/basys3.xdc
```
If you don't have both the `.pcf` and `.xdc` files, You can look at the other projects for examples of how the `.xdc` and `.pcf` code correspond.

#### *Step 2.*
Within the `project` directory, create a `.json` file under the name of the project. Copy the contents of another project's `.json` file and modify it to match your project's specs. It will look like somthing like this:
```json
{
    "srcs": [
        "src/counter/counter.v"
        ],
    "top": "top",
    "name": "counter",
    "clocks": {
        "clk": 10.0
    },
    "required_toolchains": [
        "vpr", "vpr-fasm2bels", "vivado", "yosys-vivado"
    ],
    "vendors": {
        "xilinx": ["arty-a35t", "basys3"]
    }
}
```

#### *Step 3.*
Test the newly added project with vpr and vivado. For example:
```
python3 fpgaperf.py --project counter --toolchain vpr --board basys3
python3 fpgaperf.py --project counter --toolchain vivado --board basys3
```
There may be errors if your `.xdc` or `.pcf` files have the wrong syntax. Debug, modify, and run until it works, and you have successfully added a new project to fpga-tool-perf.
