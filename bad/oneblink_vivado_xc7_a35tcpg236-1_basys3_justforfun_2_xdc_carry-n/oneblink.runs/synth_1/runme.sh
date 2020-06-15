#!/bin/sh

# 
# Vivado(TM)
# runme.sh: a Vivado-generated Runs Script for UNIX
# Copyright 1986-2017 Xilinx, Inc. All Rights Reserved.
# 

if [ -z "$PATH" ]; then
  PATH=/home/student/Xilinx_2017.2/Vivado/2017.2/ids_lite/ISE/bin/lin64:/home/student/Xilinx_2017.2/Vivado/2017.2/bin
else
  PATH=/home/student/Xilinx_2017.2/Vivado/2017.2/ids_lite/ISE/bin/lin64:/home/student/Xilinx_2017.2/Vivado/2017.2/bin:$PATH
fi
export PATH

if [ -z "$LD_LIBRARY_PATH" ]; then
  LD_LIBRARY_PATH=/home/student/Xilinx_2017.2/Vivado/2017.2/ids_lite/ISE/lib/lin64
else
  LD_LIBRARY_PATH=/home/student/Xilinx_2017.2/Vivado/2017.2/ids_lite/ISE/lib/lin64:$LD_LIBRARY_PATH
fi
export LD_LIBRARY_PATH

HD_PWD='/home/student/fpga-tool-perf/bad/oneblink_vivado_xc7_a35tcpg236-1_basys3_justforfun_2_xdc_carry-n/oneblink.runs/synth_1'
cd "$HD_PWD"

HD_LOG=runme.log
/bin/touch $HD_LOG

ISEStep="./ISEWrap.sh"
EAStep()
{
     $ISEStep $HD_LOG "$@" >> $HD_LOG 2>&1
     if [ $? -ne 0 ]
     then
         exit
     fi
}

EAStep vivado -log top.vds -m64 -product Vivado -mode batch -messageDb vivado.pb -notrace -source top.tcl
