# arty 100 MHz CLK
set_property LOC N3 [get_ports clk]
set_property LOC V14 [get_ports out]
set_property IOSTANDARD LVCMOS33 [get_ports clk]
set_property IOSTANDARD LVCMOS33 [get_ports out]

create_clock -period 10.0 [get_ports clk]
