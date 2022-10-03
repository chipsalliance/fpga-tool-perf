set_property LOC B4 [get_ports clk]
set_property LOC A3 [get_ports out]

set_property IOSTANDARD LVCMOS33 [get_ports clk]
set_property IOSTANDARD LVCMOS33 [get_ports out]

create_clock -name clk -period 13.333 [get_ports clk]
