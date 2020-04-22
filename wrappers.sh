#!/usr/bin/env bash
#
# Copyright (C) 2020  The SymbiFlow Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

python3 wrapper.py --module VexRiscv src/vexriscv-verilog/VexRiscv.v >src/vexriscv-verilog_wrap.v

#python3 wrapper.py "src/picorv32/picosoc/picosoc.v" >src/picosoc_wrap.v
python3 wrapper.py "src/picosoc_def.v" >src/picosoc_wrap.v

#python3 wrapper.py "src/picorv32/picorv32.v" >src/picorv32_wrap.v
python3 wrapper.py "src/picorv32_def.v" >src/picorv32_wrap.v


# ok
python3 wrapper.py "src/picorv32/picosoc/simpleuart.v" >src/picosoc_simpleuart_wrap.v

# bidir
#python3 wrapper.py "src/picorv32/picosoc/spiflash.v" >src/picosoc_spiflash_wrap.v
#python3 wrapper.py "src/picosoc_spiflash_def.v" >src/picosoc_spiflash_wrap.v

#python3 wrapper.py "src/picorv32/picosoc/spimemio.v" >src/picosoc_spimemio_wrap.v
python3 wrapper.py "src/picosoc_spimemio_def.v" >src/picosoc_spimemio_wrap.v

