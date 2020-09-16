# arty 100 MHz CLK
set_property LOC W5  [get_ports clk]
set_property LOC U16 [get_ports stb]
set_property LOC V17 [get_ports di]
set_property LOC E19 [get_ports do]

set_property IOSTANDARD LVCMOS33 [get_ports clk]
set_property IOSTANDARD LVCMOS33 [get_ports stb]
set_property IOSTANDARD LVCMOS33 [get_ports di]
set_property IOSTANDARD LVCMOS33 [get_ports do]

set_property DRIVE 12 [get_ports do]

create_clock -period 10.0 [get_ports clk]
