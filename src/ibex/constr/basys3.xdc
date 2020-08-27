set_property LOC W5 [get_ports IO_CLK]
set_property IOSTANDARD LVCMOS33 [get_ports IO_CLK]
create_clock -add -name sys_clk_pin -period 10.00 -waveform {0 5} [get_ports IO_CLK]

set_property LOC U16 [get_ports {LED[0]}]
set_property LOC E19 [get_ports {LED[1]}]
set_property LOC U19 [get_ports {LED[2]}]
set_property LOC V19 [get_ports {LED[3]}]

set_property IOSTANDARD LVCMOS33 [get_ports {LED[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {LED[1]}]
set_property IOSTANDARD LVCMOS33 [get_ports {LED[2]}]
set_property IOSTANDARD LVCMOS33 [get_ports {LED[3]}]

set_property LOC A18 [get_ports IO_RST_N]
set_property IOSTANDARD LVCMOS33 [get_ports IO_RST_N]
