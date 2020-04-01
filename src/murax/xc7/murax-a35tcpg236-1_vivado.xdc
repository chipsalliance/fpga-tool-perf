set_property -dict  { PACKAGE_PIN A16 IOSTANDARD LVCMOS33 } [get_ports clk];
set_property -dict { PACKAGE_PIN C16 IOSTANDARD LVCMOS33 } [get_ports { jtag_clk }];
set_property -dict { PACKAGE_PIN A14 IOSTANDARD LVCMOS33 } [get_ports { io_G15 }];
set_property -dict { PACKAGE_PIN B18 IOSTANDARD LVCMOS33 } [get_ports { io_G16 }];
set_property -dict { PACKAGE_PIN D18 IOSTANDARD LVCMOS33 } [get_ports { io_F15 }];
set_property -dict { PACKAGE_PIN E18 IOSTANDARD LVCMOS33 } [get_ports { io_B12 }];
set_property -dict { PACKAGE_PIN G3 IOSTANDARD LVCMOS33 } [get_ports { io_B10 }];
set_property -dict { PACKAGE_PIN G18 IOSTANDARD LVCMOS33 } [get_ports { io_led[0] }];
set_property -dict { PACKAGE_PIN H1 IOSTANDARD LVCMOS33 } [get_ports { io_led[1] }];
set_property -dict { PACKAGE_PIN H2 IOSTANDARD LVCMOS33 } [get_ports { io_led[2] }];
set_property -dict { PACKAGE_PIN H17 IOSTANDARD LVCMOS33 } [get_ports { io_led[3] }];
set_property -dict { PACKAGE_PIN H19 IOSTANDARD LVCMOS33 } [get_ports { io_led[4] }];
set_property -dict { PACKAGE_PIN J3 IOSTANDARD LVCMOS33 } [get_ports { io_led[5] }];
set_property -dict { PACKAGE_PIN J17 IOSTANDARD LVCMOS33 } [get_ports { io_led[6] }];
set_property -dict { PACKAGE_PIN K2 IOSTANDARD LVCMOS33 } [get_ports { io_led[7] }];

create_clock -name clk -period 20 [get_nets clk]
