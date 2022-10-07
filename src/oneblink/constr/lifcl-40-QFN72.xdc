set_property LOC L13 [get_ports clk]
set_property LOC G19 [get_ports out]

set_property IOSTANDARD LVCMOS33 [get_ports clk]
set_property IOSTANDARD LVCMOS33 [get_ports out]

create_clock -name clk -period 13.333 [get_ports clk]
