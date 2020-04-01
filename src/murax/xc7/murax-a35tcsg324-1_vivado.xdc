set_property -dict  { PACKAGE_PIN B8 IOSTANDARD LVCMOS33 } [get_ports clk];
set_property -dict { PACKAGE_PIN C11 IOSTANDARD LVCMOS33 } [get_ports { jtag_clk }];
set_property -dict { PACKAGE_PIN A6 IOSTANDARD LVCMOS33 } [get_ports { io_G15 }];
set_property -dict { PACKAGE_PIN A13 IOSTANDARD LVCMOS33 } [get_ports { io_G16 }];
set_property -dict { PACKAGE_PIN A15 IOSTANDARD LVCMOS33 } [get_ports { io_F15 }];
set_property -dict { PACKAGE_PIN B1 IOSTANDARD LVCMOS33 } [get_ports { io_B12 }];
set_property -dict { PACKAGE_PIN B3 IOSTANDARD LVCMOS33 } [get_ports { io_B10 }];
set_property -dict { PACKAGE_PIN B7 IOSTANDARD LVCMOS33 } [get_ports { io_led[0] }];
set_property -dict { PACKAGE_PIN B11 IOSTANDARD LVCMOS33 } [get_ports { io_led[1] }];
set_property -dict { PACKAGE_PIN B13 IOSTANDARD LVCMOS33 } [get_ports { io_led[2] }];
set_property -dict { PACKAGE_PIN B16 IOSTANDARD LVCMOS33 } [get_ports { io_led[3] }];
set_property -dict { PACKAGE_PIN B18 IOSTANDARD LVCMOS33 } [get_ports { io_led[4] }];
set_property -dict { PACKAGE_PIN C2 IOSTANDARD LVCMOS33 } [get_ports { io_led[5] }];
set_property -dict { PACKAGE_PIN C6 IOSTANDARD LVCMOS33 } [get_ports { io_led[6] }];
set_property -dict { PACKAGE_PIN C12 IOSTANDARD LVCMOS33 } [get_ports { io_led[7] }];

create_clock -name clk -period 20 [get_nets clk]
