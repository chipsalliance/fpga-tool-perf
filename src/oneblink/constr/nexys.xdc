set_property PACKAGE_PIN R4 [get_ports clk]
set_property PACKAGE_PIN T14 [get_ports out]

set_property IOSTANDARD LVCMOS33 [get_ports clk]
set_property IOSTANDARD LVCMOS33 [get_ports out]

create_clock -period 10.0 [get_ports clk]
