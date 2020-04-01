set_property -dict  { PACKAGE_PIN H16 IOSTANDARD LVCMOS33 } [get_ports clk];
set_property -dict { PACKAGE_PIN K17 IOSTANDARD LVCMOS33 } [get_ports { jtag_clk }];
set_property -dict { PACKAGE_PIN E17 IOSTANDARD LVCMOS33 } [get_ports { io_G15 }];
set_property -dict { PACKAGE_PIN E18 IOSTANDARD LVCMOS33 } [get_ports { io_G16 }];
set_property -dict { PACKAGE_PIN F16 IOSTANDARD LVCMOS33 } [get_ports { io_F15 }];
set_property -dict { PACKAGE_PIN F19 IOSTANDARD LVCMOS33 } [get_ports { io_B12 }];
set_property -dict { PACKAGE_PIN G17 IOSTANDARD LVCMOS33 } [get_ports { io_B10 }];
set_property -dict { PACKAGE_PIN G19 IOSTANDARD LVCMOS33 } [get_ports { io_led[0] }];
set_property -dict { PACKAGE_PIN H15 IOSTANDARD LVCMOS33 } [get_ports { io_led[1] }];
set_property -dict { PACKAGE_PIN J20 IOSTANDARD LVCMOS33 } [get_ports { io_led[2] }];
set_property -dict { PACKAGE_PIN K14 IOSTANDARD LVCMOS33 } [get_ports { io_led[3] }];
set_property -dict { PACKAGE_PIN K16 IOSTANDARD LVCMOS33 } [get_ports { io_led[4] }];
set_property -dict { PACKAGE_PIN K19 IOSTANDARD LVCMOS33 } [get_ports { io_led[5] }];
set_property -dict { PACKAGE_PIN L14 IOSTANDARD LVCMOS33 } [get_ports { io_led[6] }];
set_property -dict { PACKAGE_PIN L19 IOSTANDARD LVCMOS33 } [get_ports { io_led[7] }];

create_clock -name clk -period 20 [get_nets clk]
