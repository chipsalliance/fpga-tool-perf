set_property LOC L16 [get_ports IO_CLK]
set_property IOSTANDARD LVCMOS33 [get_ports IO_CLK]
create_clock -add -name sys_clk_pin -period 8.00 -waveform {0 4} [get_ports IO_CLK];

set_property PACKAGE_PIN M14 [get_ports LED[0]]
set_property PACKAGE_PIN M15 [get_ports LED[1]]
set_property PACKAGE_PIN G14 [get_ports LED[2]]
set_property PACKAGE_PIN D18 [get_ports LED[3]]

set_property IOSTANDARD LVCMOS33 [get_ports LED[0]]
set_property IOSTANDARD LVCMOS33 [get_ports LED[1]]
set_property IOSTANDARD LVCMOS33 [get_ports LED[2]]
set_property IOSTANDARD LVCMOS33 [get_ports LED[3]]

set_property PACKAGE_PIN E17 [get_ports IO_RST_N]
set_property IOSTANDARD LVCMOS33 [get_ports IO_RST_N]
