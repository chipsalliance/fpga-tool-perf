################################################################################
# IO constraints
################################################################################
# clk50:0
set_property LOC J19 [get_ports {clk50}]
set_property IOSTANDARD LVCMOS33 [get_ports {clk50}]

# flash:0.cs_n
set_property LOC T19 [get_ports {flash_cs_n}]
set_property IOSTANDARD LVCMOS33 [get_ports {flash_cs_n}]

# flash:0.mosi
set_property LOC P22 [get_ports {flash_mosi}]
set_property IOSTANDARD LVCMOS33 [get_ports {flash_mosi}]

# flash:0.miso
set_property LOC R22 [get_ports {flash_miso}]
set_property IOSTANDARD LVCMOS33 [get_ports {flash_miso}]

# flash:0.wp
set_property LOC P21 [get_ports {flash_wp}]
set_property IOSTANDARD LVCMOS33 [get_ports {flash_wp}]

# flash:0.hold
set_property LOC R21 [get_ports {flash_hold}]
set_property IOSTANDARD LVCMOS33 [get_ports {flash_hold}]

# ddram:0.a
set_property LOC U6 [get_ports {ddram_a[0]}]
set_property SLEW FAST [get_ports {ddram_a[0]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_a[0]}]

# ddram:0.a
set_property LOC V4 [get_ports {ddram_a[1]}]
set_property SLEW FAST [get_ports {ddram_a[1]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_a[1]}]

# ddram:0.a
set_property LOC W5 [get_ports {ddram_a[2]}]
set_property SLEW FAST [get_ports {ddram_a[2]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_a[2]}]

# ddram:0.a
set_property LOC V5 [get_ports {ddram_a[3]}]
set_property SLEW FAST [get_ports {ddram_a[3]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_a[3]}]

# ddram:0.a
set_property LOC AA1 [get_ports {ddram_a[4]}]
set_property SLEW FAST [get_ports {ddram_a[4]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_a[4]}]

# ddram:0.a
set_property LOC Y2 [get_ports {ddram_a[5]}]
set_property SLEW FAST [get_ports {ddram_a[5]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_a[5]}]

# ddram:0.a
set_property LOC AB1 [get_ports {ddram_a[6]}]
set_property SLEW FAST [get_ports {ddram_a[6]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_a[6]}]

# ddram:0.a
set_property LOC AB3 [get_ports {ddram_a[7]}]
set_property SLEW FAST [get_ports {ddram_a[7]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_a[7]}]

# ddram:0.a
set_property LOC AB2 [get_ports {ddram_a[8]}]
set_property SLEW FAST [get_ports {ddram_a[8]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_a[8]}]

# ddram:0.a
set_property LOC Y3 [get_ports {ddram_a[9]}]
set_property SLEW FAST [get_ports {ddram_a[9]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_a[9]}]

# ddram:0.a
set_property LOC W6 [get_ports {ddram_a[10]}]
set_property SLEW FAST [get_ports {ddram_a[10]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_a[10]}]

# ddram:0.a
set_property LOC Y1 [get_ports {ddram_a[11]}]
set_property SLEW FAST [get_ports {ddram_a[11]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_a[11]}]

# ddram:0.a
set_property LOC V2 [get_ports {ddram_a[12]}]
set_property SLEW FAST [get_ports {ddram_a[12]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_a[12]}]

# ddram:0.a
set_property LOC AA3 [get_ports {ddram_a[13]}]
set_property SLEW FAST [get_ports {ddram_a[13]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_a[13]}]

# ddram:0.ba
set_property LOC U5 [get_ports {ddram_ba[0]}]
set_property SLEW FAST [get_ports {ddram_ba[0]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_ba[0]}]

# ddram:0.ba
set_property LOC W4 [get_ports {ddram_ba[1]}]
set_property SLEW FAST [get_ports {ddram_ba[1]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_ba[1]}]

# ddram:0.ba
set_property LOC V7 [get_ports {ddram_ba[2]}]
set_property SLEW FAST [get_ports {ddram_ba[2]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_ba[2]}]

# ddram:0.ras_n
set_property LOC Y9 [get_ports {ddram_ras_n}]
set_property SLEW FAST [get_ports {ddram_ras_n}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_ras_n}]

# ddram:0.cas_n
set_property LOC Y7 [get_ports {ddram_cas_n}]
set_property SLEW FAST [get_ports {ddram_cas_n}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_cas_n}]

# ddram:0.we_n
set_property LOC V8 [get_ports {ddram_we_n}]
set_property SLEW FAST [get_ports {ddram_we_n}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_we_n}]

# ddram:0.dm
set_property LOC G1 [get_ports {ddram_dm[0]}]
set_property SLEW FAST [get_ports {ddram_dm[0]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_dm[0]}]

# ddram:0.dm
set_property LOC H4 [get_ports {ddram_dm[1]}]
set_property SLEW FAST [get_ports {ddram_dm[1]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_dm[1]}]

# ddram:0.dm
set_property LOC M5 [get_ports {ddram_dm[2]}]
set_property SLEW FAST [get_ports {ddram_dm[2]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_dm[2]}]

# ddram:0.dm
set_property LOC L3 [get_ports {ddram_dm[3]}]
set_property SLEW FAST [get_ports {ddram_dm[3]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_dm[3]}]

# ddram:0.dq
set_property LOC C2 [get_ports {ddram_dq[0]}]
set_property SLEW FAST [get_ports {ddram_dq[0]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_dq[0]}]
set_property IN_TERM UNTUNED_SPLIT_40 [get_ports {ddram_dq[0]}]

# ddram:0.dq
set_property LOC F1 [get_ports {ddram_dq[1]}]
set_property SLEW FAST [get_ports {ddram_dq[1]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_dq[1]}]
set_property IN_TERM UNTUNED_SPLIT_40 [get_ports {ddram_dq[1]}]

# ddram:0.dq
set_property LOC B1 [get_ports {ddram_dq[2]}]
set_property SLEW FAST [get_ports {ddram_dq[2]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_dq[2]}]
set_property IN_TERM UNTUNED_SPLIT_40 [get_ports {ddram_dq[2]}]

# ddram:0.dq
set_property LOC F3 [get_ports {ddram_dq[3]}]
set_property SLEW FAST [get_ports {ddram_dq[3]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_dq[3]}]
set_property IN_TERM UNTUNED_SPLIT_40 [get_ports {ddram_dq[3]}]

# ddram:0.dq
set_property LOC A1 [get_ports {ddram_dq[4]}]
set_property SLEW FAST [get_ports {ddram_dq[4]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_dq[4]}]
set_property IN_TERM UNTUNED_SPLIT_40 [get_ports {ddram_dq[4]}]

# ddram:0.dq
set_property LOC D2 [get_ports {ddram_dq[5]}]
set_property SLEW FAST [get_ports {ddram_dq[5]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_dq[5]}]
set_property IN_TERM UNTUNED_SPLIT_40 [get_ports {ddram_dq[5]}]

# ddram:0.dq
set_property LOC B2 [get_ports {ddram_dq[6]}]
set_property SLEW FAST [get_ports {ddram_dq[6]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_dq[6]}]
set_property IN_TERM UNTUNED_SPLIT_40 [get_ports {ddram_dq[6]}]

# ddram:0.dq
set_property LOC E2 [get_ports {ddram_dq[7]}]
set_property SLEW FAST [get_ports {ddram_dq[7]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_dq[7]}]
set_property IN_TERM UNTUNED_SPLIT_40 [get_ports {ddram_dq[7]}]

# ddram:0.dq
set_property LOC J5 [get_ports {ddram_dq[8]}]
set_property SLEW FAST [get_ports {ddram_dq[8]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_dq[8]}]
set_property IN_TERM UNTUNED_SPLIT_40 [get_ports {ddram_dq[8]}]

# ddram:0.dq
set_property LOC H3 [get_ports {ddram_dq[9]}]
set_property SLEW FAST [get_ports {ddram_dq[9]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_dq[9]}]
set_property IN_TERM UNTUNED_SPLIT_40 [get_ports {ddram_dq[9]}]

# ddram:0.dq
set_property LOC K1 [get_ports {ddram_dq[10]}]
set_property SLEW FAST [get_ports {ddram_dq[10]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_dq[10]}]
set_property IN_TERM UNTUNED_SPLIT_40 [get_ports {ddram_dq[10]}]

# ddram:0.dq
set_property LOC H2 [get_ports {ddram_dq[11]}]
set_property SLEW FAST [get_ports {ddram_dq[11]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_dq[11]}]
set_property IN_TERM UNTUNED_SPLIT_40 [get_ports {ddram_dq[11]}]

# ddram:0.dq
set_property LOC J1 [get_ports {ddram_dq[12]}]
set_property SLEW FAST [get_ports {ddram_dq[12]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_dq[12]}]
set_property IN_TERM UNTUNED_SPLIT_40 [get_ports {ddram_dq[12]}]

# ddram:0.dq
set_property LOC G2 [get_ports {ddram_dq[13]}]
set_property SLEW FAST [get_ports {ddram_dq[13]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_dq[13]}]
set_property IN_TERM UNTUNED_SPLIT_40 [get_ports {ddram_dq[13]}]

# ddram:0.dq
set_property LOC H5 [get_ports {ddram_dq[14]}]
set_property SLEW FAST [get_ports {ddram_dq[14]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_dq[14]}]
set_property IN_TERM UNTUNED_SPLIT_40 [get_ports {ddram_dq[14]}]

# ddram:0.dq
set_property LOC G3 [get_ports {ddram_dq[15]}]
set_property SLEW FAST [get_ports {ddram_dq[15]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_dq[15]}]
set_property IN_TERM UNTUNED_SPLIT_40 [get_ports {ddram_dq[15]}]

# ddram:0.dq
set_property LOC N2 [get_ports {ddram_dq[16]}]
set_property SLEW FAST [get_ports {ddram_dq[16]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_dq[16]}]
set_property IN_TERM UNTUNED_SPLIT_40 [get_ports {ddram_dq[16]}]

# ddram:0.dq
set_property LOC M6 [get_ports {ddram_dq[17]}]
set_property SLEW FAST [get_ports {ddram_dq[17]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_dq[17]}]
set_property IN_TERM UNTUNED_SPLIT_40 [get_ports {ddram_dq[17]}]

# ddram:0.dq
set_property LOC P1 [get_ports {ddram_dq[18]}]
set_property SLEW FAST [get_ports {ddram_dq[18]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_dq[18]}]
set_property IN_TERM UNTUNED_SPLIT_40 [get_ports {ddram_dq[18]}]

# ddram:0.dq
set_property LOC N5 [get_ports {ddram_dq[19]}]
set_property SLEW FAST [get_ports {ddram_dq[19]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_dq[19]}]
set_property IN_TERM UNTUNED_SPLIT_40 [get_ports {ddram_dq[19]}]

# ddram:0.dq
set_property LOC P2 [get_ports {ddram_dq[20]}]
set_property SLEW FAST [get_ports {ddram_dq[20]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_dq[20]}]
set_property IN_TERM UNTUNED_SPLIT_40 [get_ports {ddram_dq[20]}]

# ddram:0.dq
set_property LOC N4 [get_ports {ddram_dq[21]}]
set_property SLEW FAST [get_ports {ddram_dq[21]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_dq[21]}]
set_property IN_TERM UNTUNED_SPLIT_40 [get_ports {ddram_dq[21]}]

# ddram:0.dq
set_property LOC R1 [get_ports {ddram_dq[22]}]
set_property SLEW FAST [get_ports {ddram_dq[22]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_dq[22]}]
set_property IN_TERM UNTUNED_SPLIT_40 [get_ports {ddram_dq[22]}]

# ddram:0.dq
set_property LOC P6 [get_ports {ddram_dq[23]}]
set_property SLEW FAST [get_ports {ddram_dq[23]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_dq[23]}]
set_property IN_TERM UNTUNED_SPLIT_40 [get_ports {ddram_dq[23]}]

# ddram:0.dq
set_property LOC K3 [get_ports {ddram_dq[24]}]
set_property SLEW FAST [get_ports {ddram_dq[24]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_dq[24]}]
set_property IN_TERM UNTUNED_SPLIT_40 [get_ports {ddram_dq[24]}]

# ddram:0.dq
set_property LOC M2 [get_ports {ddram_dq[25]}]
set_property SLEW FAST [get_ports {ddram_dq[25]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_dq[25]}]
set_property IN_TERM UNTUNED_SPLIT_40 [get_ports {ddram_dq[25]}]

# ddram:0.dq
set_property LOC K4 [get_ports {ddram_dq[26]}]
set_property SLEW FAST [get_ports {ddram_dq[26]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_dq[26]}]
set_property IN_TERM UNTUNED_SPLIT_40 [get_ports {ddram_dq[26]}]

# ddram:0.dq
set_property LOC M3 [get_ports {ddram_dq[27]}]
set_property SLEW FAST [get_ports {ddram_dq[27]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_dq[27]}]
set_property IN_TERM UNTUNED_SPLIT_40 [get_ports {ddram_dq[27]}]

# ddram:0.dq
set_property LOC J6 [get_ports {ddram_dq[28]}]
set_property SLEW FAST [get_ports {ddram_dq[28]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_dq[28]}]
set_property IN_TERM UNTUNED_SPLIT_40 [get_ports {ddram_dq[28]}]

# ddram:0.dq
set_property LOC L5 [get_ports {ddram_dq[29]}]
set_property SLEW FAST [get_ports {ddram_dq[29]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_dq[29]}]
set_property IN_TERM UNTUNED_SPLIT_40 [get_ports {ddram_dq[29]}]

# ddram:0.dq
set_property LOC J4 [get_ports {ddram_dq[30]}]
set_property SLEW FAST [get_ports {ddram_dq[30]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_dq[30]}]
set_property IN_TERM UNTUNED_SPLIT_40 [get_ports {ddram_dq[30]}]

# ddram:0.dq
set_property LOC K6 [get_ports {ddram_dq[31]}]
set_property SLEW FAST [get_ports {ddram_dq[31]}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_dq[31]}]
set_property IN_TERM UNTUNED_SPLIT_40 [get_ports {ddram_dq[31]}]

# ddram:0.dqs_p
set_property LOC E1 [get_ports {ddram_dqs_p[0]}]
set_property SLEW FAST [get_ports {ddram_dqs_p[0]}]
set_property IOSTANDARD DIFF_SSTL15_R [get_ports {ddram_dqs_p[0]}]

# ddram:0.dqs_p
set_property LOC K2 [get_ports {ddram_dqs_p[1]}]
set_property SLEW FAST [get_ports {ddram_dqs_p[1]}]
set_property IOSTANDARD DIFF_SSTL15_R [get_ports {ddram_dqs_p[1]}]

# ddram:0.dqs_p
set_property LOC P5 [get_ports {ddram_dqs_p[2]}]
set_property SLEW FAST [get_ports {ddram_dqs_p[2]}]
set_property IOSTANDARD DIFF_SSTL15_R [get_ports {ddram_dqs_p[2]}]

# ddram:0.dqs_p
set_property LOC M1 [get_ports {ddram_dqs_p[3]}]
set_property SLEW FAST [get_ports {ddram_dqs_p[3]}]
set_property IOSTANDARD DIFF_SSTL15_R [get_ports {ddram_dqs_p[3]}]

# ddram:0.dqs_n
set_property LOC D1 [get_ports {ddram_dqs_n[0]}]
set_property SLEW FAST [get_ports {ddram_dqs_n[0]}]
set_property IOSTANDARD DIFF_SSTL15_R [get_ports {ddram_dqs_n[0]}]

# ddram:0.dqs_n
set_property LOC J2 [get_ports {ddram_dqs_n[1]}]
set_property SLEW FAST [get_ports {ddram_dqs_n[1]}]
set_property IOSTANDARD DIFF_SSTL15_R [get_ports {ddram_dqs_n[1]}]

# ddram:0.dqs_n
set_property LOC P4 [get_ports {ddram_dqs_n[2]}]
set_property SLEW FAST [get_ports {ddram_dqs_n[2]}]
set_property IOSTANDARD DIFF_SSTL15_R [get_ports {ddram_dqs_n[2]}]

# ddram:0.dqs_n
set_property LOC L1 [get_ports {ddram_dqs_n[3]}]
set_property SLEW FAST [get_ports {ddram_dqs_n[3]}]
set_property IOSTANDARD DIFF_SSTL15_R [get_ports {ddram_dqs_n[3]}]

# ddram:0.clk_p
set_property LOC R3 [get_ports {ddram_clk_p}]
set_property SLEW FAST [get_ports {ddram_clk_p}]
set_property IOSTANDARD DIFF_SSTL15_R [get_ports {ddram_clk_p}]

# ddram:0.clk_n
set_property LOC R2 [get_ports {ddram_clk_n}]
set_property SLEW FAST [get_ports {ddram_clk_n}]
set_property IOSTANDARD DIFF_SSTL15_R [get_ports {ddram_clk_n}]

# ddram:0.cke
set_property LOC Y8 [get_ports {ddram_cke}]
set_property SLEW FAST [get_ports {ddram_cke}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_cke}]

# ddram:0.odt
set_property LOC W9 [get_ports {ddram_odt}]
set_property SLEW FAST [get_ports {ddram_odt}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_odt}]

# ddram:0.reset_n
set_property LOC AB5 [get_ports {ddram_reset_n}]
set_property SLEW FAST [get_ports {ddram_reset_n}]
set_property IOSTANDARD LVCMOS15 [get_ports {ddram_reset_n}]

# ddram:0.cs_n
set_property LOC V9 [get_ports {ddram_cs_n}]
set_property SLEW FAST [get_ports {ddram_cs_n}]
set_property IOSTANDARD SSTL15_R [get_ports {ddram_cs_n}]

# eth_clocks:0.ref_clk
set_property LOC D17 [get_ports {eth_clocks_ref_clk}]
set_property IOSTANDARD LVCMOS33 [get_ports {eth_clocks_ref_clk}]

# eth:0.rst_n
set_property LOC F16 [get_ports {eth_rst_n}]
set_property IOSTANDARD LVCMOS33 [get_ports {eth_rst_n}]

# eth:0.rx_data
set_property LOC A20 [get_ports {eth_rx_data[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {eth_rx_data[0]}]

# eth:0.rx_data
set_property LOC B18 [get_ports {eth_rx_data[1]}]
set_property IOSTANDARD LVCMOS33 [get_ports {eth_rx_data[1]}]

# eth:0.crs_dv
set_property LOC C20 [get_ports {eth_crs_dv}]
set_property IOSTANDARD LVCMOS33 [get_ports {eth_crs_dv}]

# eth:0.tx_en
set_property LOC A19 [get_ports {eth_tx_en}]
set_property IOSTANDARD LVCMOS33 [get_ports {eth_tx_en}]

# eth:0.tx_data
set_property LOC C18 [get_ports {eth_tx_data[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {eth_tx_data[0]}]

# eth:0.tx_data
set_property LOC C19 [get_ports {eth_tx_data[1]}]
set_property IOSTANDARD LVCMOS33 [get_ports {eth_tx_data[1]}]

# eth:0.mdc
set_property LOC F14 [get_ports {eth_mdc}]
set_property IOSTANDARD LVCMOS33 [get_ports {eth_mdc}]

# eth:0.mdio
set_property LOC F13 [get_ports {eth_mdio}]
set_property IOSTANDARD LVCMOS33 [get_ports {eth_mdio}]

# eth:0.rx_er
set_property LOC B20 [get_ports {eth_rx_er}]
set_property IOSTANDARD LVCMOS33 [get_ports {eth_rx_er}]

# eth:0.int_n
set_property LOC D21 [get_ports {eth_int_n}]
set_property IOSTANDARD LVCMOS33 [get_ports {eth_int_n}]

# pcie_x1:0.rst_n
set_property LOC E18 [get_ports {pcie_x1_rst_n}]
set_property IOSTANDARD LVCMOS33 [get_ports {pcie_x1_rst_n}]

# pcie_x1:0.clk_p
set_property LOC F10 [get_ports {pcie_x1_clk_p}]

# pcie_x1:0.clk_n
set_property LOC E10 [get_ports {pcie_x1_clk_n}]

# pcie_x1:0.rx_p
set_property LOC D11 [get_ports {pcie_x1_rx_p}]

# pcie_x1:0.rx_n
set_property LOC C11 [get_ports {pcie_x1_rx_n}]

# pcie_x1:0.tx_p
set_property LOC D5 [get_ports {pcie_x1_tx_p}]

# pcie_x1:0.tx_n
set_property LOC C5 [get_ports {pcie_x1_tx_n}]

# hdmi_in:0.clk_p
set_property LOC L19 [get_ports {hdmi_in0_clk_p}]
set_property IOSTANDARD TMDS_33 [get_ports {hdmi_in0_clk_p}]

# hdmi_in:0.clk_n
set_property LOC L20 [get_ports {hdmi_in0_clk_n}]
set_property IOSTANDARD TMDS_33 [get_ports {hdmi_in0_clk_n}]

# hdmi_in:0.data0_p
set_property LOC K21 [get_ports {hdmi_in0_data0_p}]
set_property IOSTANDARD TMDS_33 [get_ports {hdmi_in0_data0_p}]

# hdmi_in:0.data0_n
set_property LOC K22 [get_ports {hdmi_in0_data0_n}]
set_property IOSTANDARD TMDS_33 [get_ports {hdmi_in0_data0_n}]

# hdmi_in:0.data1_p
set_property LOC J20 [get_ports {hdmi_in0_data1_p}]
set_property IOSTANDARD TMDS_33 [get_ports {hdmi_in0_data1_p}]

# hdmi_in:0.data1_n
set_property LOC J21 [get_ports {hdmi_in0_data1_n}]
set_property IOSTANDARD TMDS_33 [get_ports {hdmi_in0_data1_n}]

# hdmi_in:0.data2_p
set_property LOC J22 [get_ports {hdmi_in0_data2_p}]
set_property IOSTANDARD TMDS_33 [get_ports {hdmi_in0_data2_p}]

# hdmi_in:0.data2_n
set_property LOC H22 [get_ports {hdmi_in0_data2_n}]
set_property IOSTANDARD TMDS_33 [get_ports {hdmi_in0_data2_n}]

# hdmi_in:0.scl
set_property LOC T18 [get_ports {hdmi_in0_scl}]
set_property IOSTANDARD LVCMOS33 [get_ports {hdmi_in0_scl}]

# hdmi_in:0.sda
set_property LOC V18 [get_ports {hdmi_in0_sda}]
set_property IOSTANDARD LVCMOS33 [get_ports {hdmi_in0_sda}]

# hdmi_in:0.sda_pu
set_property LOC G20 [get_ports {hdmi_in0_sda_pu}]
set_property IOSTANDARD LVCMOS33 [get_ports {hdmi_in0_sda_pu}]

# hdmi_in:0.sda_pd
set_property LOC F20 [get_ports {hdmi_in0_sda_pd}]
set_property IOSTANDARD LVCMOS33 [get_ports {hdmi_in0_sda_pd}]

# hdmi_out:0.clk_p
set_property LOC W19 [get_ports {hdmi_out0_clk_p}]
set_property IOSTANDARD TMDS_33 [get_ports {hdmi_out0_clk_p}]

# hdmi_out:0.clk_n
set_property LOC W20 [get_ports {hdmi_out0_clk_n}]
set_property IOSTANDARD TMDS_33 [get_ports {hdmi_out0_clk_n}]

# hdmi_out:0.data0_p
set_property LOC W21 [get_ports {hdmi_out0_data0_p}]
set_property IOSTANDARD TMDS_33 [get_ports {hdmi_out0_data0_p}]

# hdmi_out:0.data0_n
set_property LOC W22 [get_ports {hdmi_out0_data0_n}]
set_property IOSTANDARD TMDS_33 [get_ports {hdmi_out0_data0_n}]

# hdmi_out:0.data1_p
set_property LOC U20 [get_ports {hdmi_out0_data1_p}]
set_property IOSTANDARD TMDS_33 [get_ports {hdmi_out0_data1_p}]

# hdmi_out:0.data1_n
set_property LOC V20 [get_ports {hdmi_out0_data1_n}]
set_property IOSTANDARD TMDS_33 [get_ports {hdmi_out0_data1_n}]

# hdmi_out:0.data2_p
set_property LOC T21 [get_ports {hdmi_out0_data2_p}]
set_property IOSTANDARD TMDS_33 [get_ports {hdmi_out0_data2_p}]

# hdmi_out:0.data2_n
set_property LOC U21 [get_ports {hdmi_out0_data2_n}]
set_property IOSTANDARD TMDS_33 [get_ports {hdmi_out0_data2_n}]

################################################################################
# Design constraints
################################################################################

################################################################################
# Clock constraints
################################################################################


create_clock -name clk50 -period 20.0 [get_nets clk50]

create_clock -name dna_clk -period 20.0 [get_nets dna_clk]

create_clock -name icap_clk -period 160.0 [get_nets icap_clk]

create_clock -name eth_clocks_ref_clk -period 20.0 [get_nets eth_clocks_ref_clk]

create_clock -name eth_rx_clk -period 20.0 [get_nets eth_rx_clk]

create_clock -name eth_tx_clk -period 20.0 [get_nets eth_tx_clk]

create_clock -name pcie_x1_clk_p -period 10.0 [get_nets pcie_x1_clk_p]

create_clock -name hdmi_in0_clk_p -period 13.468 [get_nets hdmi_in0_clk_p]

set_clock_groups -group [get_clocks -include_generated_clocks -of [get_nets sys_clk]] -group [get_clocks -include_generated_clocks -of [get_nets eth_rx_clk]] -asynchronous

set_clock_groups -group [get_clocks -include_generated_clocks -of [get_nets sys_clk]] -group [get_clocks -include_generated_clocks -of [get_nets eth_tx_clk]] -asynchronous

set_clock_groups -group [get_clocks -include_generated_clocks -of [get_nets sys_clk]] -group [get_clocks -include_generated_clocks -of [get_nets pcie_clk]] -asynchronous

set_clock_groups -group [get_clocks -include_generated_clocks -of [get_nets sys_clk]] -group [get_clocks -include_generated_clocks -of [get_nets hdmi_in0_pix_clk]] -asynchronous

set_clock_groups -group [get_clocks -include_generated_clocks -of [get_nets sys_clk]] -group [get_clocks -include_generated_clocks -of [get_nets pix1p25x_clk]] -asynchronous

set_clock_groups -group [get_clocks -include_generated_clocks -of [get_nets sys_clk]] -group [get_clocks -include_generated_clocks -of [get_nets hdmi_in0_pix5x_clk]] -asynchronous

set_clock_groups -group [get_clocks -include_generated_clocks -of [get_nets sys_clk]] -group [get_clocks -include_generated_clocks -of [get_nets hdmi_out0_pix_clk]] -asynchronous

set_clock_groups -group [get_clocks -include_generated_clocks -of [get_nets sys_clk]] -group [get_clocks -include_generated_clocks -of [get_nets hdmi_out0_pix5x_clk]] -asynchronous

set_clock_groups -group [get_clocks -include_generated_clocks -of [get_nets dna_clk]] -group [get_clocks -include_generated_clocks -of [get_nets sys_clk]] -asynchronous

set_clock_groups -group [get_clocks -include_generated_clocks -of [get_nets icap_clk]] -group [get_clocks -include_generated_clocks -of [get_nets sys_clk]] -asynchronous

set_clock_groups -group [get_clocks -include_generated_clocks -of [get_nets eth_rx_clk]] -group [get_clocks -include_generated_clocks -of [get_nets eth_tx_clk]] -asynchronous

set_clock_groups -group [get_clocks -include_generated_clocks -of [get_nets hdmi_in0_pix_clk]] -group [get_clocks -include_generated_clocks -of [get_nets pix1p25x_clk]] -asynchronous

set_clock_groups -group [get_clocks -include_generated_clocks -of [get_nets hdmi_in0_pix_clk]] -group [get_clocks -include_generated_clocks -of [get_nets hdmi_in0_pix5x_clk]] -asynchronous

set_clock_groups -group [get_clocks -include_generated_clocks -of [get_nets pix1p25x_clk]] -group [get_clocks -include_generated_clocks -of [get_nets hdmi_in0_pix5x_clk]] -asynchronous

set_clock_groups -group [get_clocks -include_generated_clocks -of [get_nets hdmi_out0_pix_clk]] -group [get_clocks -include_generated_clocks -of [get_nets hdmi_out0_pix5x_clk]] -asynchronous

################################################################################
# False path constraints
################################################################################


set_false_path -quiet -through [get_nets -hierarchical -filter {mr_ff == TRUE}]

set_false_path -quiet -to [get_pins -filter {REF_PIN_NAME == PRE} -of_objects [get_cells -hierarchical -filter {ars_ff1 == TRUE || ars_ff2 == TRUE}]]

set_max_delay 2 -quiet -from [get_pins -filter {REF_PIN_NAME == C} -of_objects [get_cells -hierarchical -filter {ars_ff1 == TRUE}]] -to [get_pins -filter {REF_PIN_NAME == D} -of_objects [get_cells -hierarchical -filter {ars_ff2 == TRUE}]]