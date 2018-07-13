#!/usr/bin/env bash
python3 harness_gen.py --module VexRiscv src/vexriscv-verilog/VexRiscv.v >src/vexriscv-verilog_wrap.v

#python3 harness_gen.py "src/picorv32/picosoc/picosoc.v" >src/picosoc_wrap.v
python3 harness_gen.py "src/picosoc_def.v" >src/picosoc_wrap.v

#python3 harness_gen.py "src/picorv32/picorv32.v" >src/picorv32_wrap.v
python3 harness_gen.py "src/picorv32_def.v" >src/picorv32_wrap.v

