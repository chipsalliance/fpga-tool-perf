## Based on https://github.com/Digilent/digilent-xdc/blob/master/Arty-A7-100-Master.xdc
## This file is a general .xdc for the Arty A7-100 Rev. D
## To use it in a project:
## - uncomment the lines corresponding to used pins
## - rename the used ports (in each line, after get_ports) according to the top level signal names in the project

## Clock signal
set_property LOC R4 [get_ports IO_CLK]
set_property IOSTANDARD LVCMOS33 [get_ports IO_CLK]

## LEDs
set_property LOC T14 [get_ports LED[0]]
set_property LOC T15 [get_ports LED[1]]
set_property LOC T16 [get_ports LED[2]]
set_property LOC U16 [get_ports LED[3]]
set_property IOSTANDARD LVCMOS33 [get_ports LED[0]]
set_property IOSTANDARD LVCMOS33 [get_ports LED[1]]
set_property IOSTANDARD LVCMOS33 [get_ports LED[2]]
set_property IOSTANDARD LVCMOS33 [get_ports LED[3]]

## Reset signal
set_property LOC AB22 [get_ports IO_RST_N]
set_property IOSTANDARD LVCMOS33 [get_ports IO_RST_N]

