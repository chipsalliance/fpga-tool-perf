# Clock Signal
set_property LOC R4 [get_ports clk]
set_property IOSTANDARD LVCMOS33 [get_ports clk]

# stb, di, do
set_property LOC E22 [get_ports stb]
set_property LOC F21 [get_ports di]
set_property LOC G21 [get_ports do]

set_property IOSTANDARD LVCMOS33 [get_ports stb]
set_property IOSTANDARD LVCMOS33 [get_ports di]
set_property IOSTANDARD LVCMOS33 [get_ports do]

create_clock -period 10.0 [get_ports clk]
