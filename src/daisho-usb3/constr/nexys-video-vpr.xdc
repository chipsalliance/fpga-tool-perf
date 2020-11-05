################################################################################
# IO constraints
################################################################################
# clk100:0
set_property LOC R4 [get_ports clk100]
set_property IOSTANDARD LVCMOS33 [get_ports clk100]

# cpu_reset:0
set_property LOC G4 [get_ports cpu_reset]
set_property IOSTANDARD LVCMOS15 [get_ports cpu_reset]

# serial:0.tx
set_property LOC AA19 [get_ports serial_tx]
set_property IOSTANDARD LVCMOS33 [get_ports serial_tx]

# serial:0.rx
set_property LOC V18 [get_ports serial_rx]
set_property IOSTANDARD LVCMOS33 [get_ports serial_rx]

# eth_clocks:0.tx
set_property LOC AA14 [get_ports eth_clocks_tx]
set_property IOSTANDARD LVCMOS25 [get_ports eth_clocks_tx]

# eth_clocks:0.rx
set_property LOC V13 [get_ports eth_clocks_rx]
set_property IOSTANDARD LVCMOS25 [get_ports eth_clocks_rx]

# eth:0.rst_n
set_property LOC U7 [get_ports eth_rst_n]
set_property IOSTANDARD LVCMOS25 [get_ports eth_rst_n]
set_property IOSTANDARD LVCMOS33 [get_ports eth_rst_n]

# eth:0.int_n
set_property LOC Y14 [get_ports eth_int_n]
set_property IOSTANDARD LVCMOS25 [get_ports eth_int_n]

# eth:0.mdio
set_property LOC Y16 [get_ports eth_mdio]
set_property IOSTANDARD LVCMOS25 [get_ports eth_mdio]

# eth:0.mdc
set_property LOC AA16 [get_ports eth_mdc]
set_property IOSTANDARD LVCMOS25 [get_ports eth_mdc]

# eth:0.rx_ctl
set_property LOC W10 [get_ports eth_rx_ctl]
set_property IOSTANDARD LVCMOS25 [get_ports eth_rx_ctl]

# eth:0.rx_data
set_property LOC AB16 [get_ports eth_rx_data[0]]
set_property IOSTANDARD LVCMOS25 [get_ports eth_rx_data[0]]

# eth:0.rx_data
set_property LOC AA15 [get_ports eth_rx_data[1]]
set_property IOSTANDARD LVCMOS25 [get_ports eth_rx_data[1]]

# eth:0.rx_data
set_property LOC AB15 [get_ports eth_rx_data[2]]
set_property IOSTANDARD LVCMOS25 [get_ports eth_rx_data[2]]

# eth:0.rx_data
set_property LOC AB11 [get_ports eth_rx_data[3]]
set_property IOSTANDARD LVCMOS25 [get_ports eth_rx_data[3]]

# eth:0.tx_ctl
set_property LOC V10 [get_ports eth_tx_ctl]
set_property IOSTANDARD LVCMOS25 [get_ports eth_tx_ctl]

# eth:0.tx_data
set_property LOC Y12 [get_ports eth_tx_data[0]]
set_property IOSTANDARD LVCMOS25 [get_ports eth_tx_data[0]]

# eth:0.tx_data
set_property LOC W12 [get_ports eth_tx_data[1]]
set_property IOSTANDARD LVCMOS25 [get_ports eth_tx_data[1]]

# eth:0.tx_data
set_property LOC W11 [get_ports eth_tx_data[2]]
set_property IOSTANDARD LVCMOS25 [get_ports eth_tx_data[2]]

# eth:0.tx_data
set_property LOC Y11 [get_ports eth_tx_data[3]]
set_property IOSTANDARD LVCMOS25 [get_ports eth_tx_data[3]]

# vadj:0
set_property LOC AA13 [get_ports vadj[0]]
set_property IOSTANDARD LVCMOS25 [get_ports vadj[0]]

# vadj:0
set_property LOC AB17 [get_ports vadj[1]]
set_property IOSTANDARD LVCMOS25 [get_ports vadj[1]]

# usb_reset_n:0
set_property LOC A16 [get_ports usb_reset_n0]
set_property IOSTANDARD LVCMOS25 [get_ports usb_reset_n0]

# usb_pipe_ctrl:0.phy_reset_n
set_property LOC L19 [get_ports usb_pipe_ctrl0_phy_reset_n]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_ctrl0_phy_reset_n]

# usb_pipe_ctrl:0.tx_detrx_lpbk
set_property LOC C15 [get_ports usb_pipe_ctrl0_tx_detrx_lpbk]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_ctrl0_tx_detrx_lpbk]

# usb_pipe_ctrl:0.tx_elecidle
set_property LOC B20 [get_ports usb_pipe_ctrl0_tx_elecidle]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_ctrl0_tx_elecidle]

# usb_pipe_ctrl:0.power_down
set_property LOC L20 [get_ports usb_pipe_ctrl0_power_down[0]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_ctrl0_power_down[0]]

# usb_pipe_ctrl:0.power_down
set_property LOC K17 [get_ports usb_pipe_ctrl0_power_down[1]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_ctrl0_power_down[1]]

# usb_pipe_ctrl:0.tx_oneszeros
set_property LOC A20 [get_ports usb_pipe_ctrl0_tx_oneszeros]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_ctrl0_tx_oneszeros]

# usb_pipe_ctrl:0.tx_deemph
set_property LOC E13 [get_ports usb_pipe_ctrl0_tx_deemph[0]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_ctrl0_tx_deemph[0]]

# usb_pipe_ctrl:0.tx_deemph
set_property LOC B13 [get_ports usb_pipe_ctrl0_tx_deemph[1]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_ctrl0_tx_deemph[1]]

# usb_pipe_ctrl:0.tx_margin
set_property LOC A13 [get_ports usb_pipe_ctrl0_tx_margin[0]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_ctrl0_tx_margin[0]]

# usb_pipe_ctrl:0.tx_margin
set_property LOC A14 [get_ports usb_pipe_ctrl0_tx_margin[1]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_ctrl0_tx_margin[1]]

# usb_pipe_ctrl:0.tx_swing
set_property LOC C14 [get_ports usb_pipe_ctrl0_tx_swing]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_ctrl0_tx_swing]

# usb_pipe_ctrl:0.rx_polarity
set_property LOC G18 [get_ports usb_pipe_ctrl0_rx_polarity]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_ctrl0_rx_polarity]

# usb_pipe_ctrl:0.rx_termination
set_property LOC J17 [get_ports usb_pipe_ctrl0_rx_termination]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_ctrl0_rx_termination]

# usb_pipe_ctrl:0.rate
set_property LOC C13 [get_ports usb_pipe_ctrl0_rate]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_ctrl0_rate]

# usb_pipe_ctrl:0.elas_buf_mode
set_property LOC K16 [get_ports usb_pipe_ctrl0_elas_buf_mode]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_ctrl0_elas_buf_mode]

# usb_pipe_status:0.rx_elecidle
set_property LOC L15 [get_ports usb_pipe_status0_rx_elecidle]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_status0_rx_elecidle]

# usb_pipe_status:0.rx_status
set_property LOC J22 [get_ports usb_pipe_status0_rx_status[0]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_status0_rx_status[0]]

# usb_pipe_status:0.rx_status
set_property LOC L16 [get_ports usb_pipe_status0_rx_status[1]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_status0_rx_status[1]]

# usb_pipe_status:0.rx_status
set_property LOC H22 [get_ports usb_pipe_status0_rx_status[2]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_status0_rx_status[2]]

# usb_pipe_status:0.phy_status
set_property LOC G17 [get_ports usb_pipe_status0_phy_status]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_status0_phy_status]

# usb_pipe_status:0.pwr_present
set_property LOC A15 [get_ports usb_pipe_status0_pwr_present]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_status0_pwr_present]

# usb_pipe_data:0.rx_clk
set_property LOC J20 [get_ports usb_pipe_data0_rx_clk]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_data0_rx_clk]

# usb_pipe_data:0.rx_valid
set_property LOC L14 [get_ports usb_pipe_data0_rx_valid]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_data0_rx_valid]

# usb_pipe_data:0.rx_data
set_property LOC K22 [get_ports usb_pipe_data0_rx_data[0]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_data0_rx_data[0]]

# usb_pipe_data:0.rx_data
set_property LOC K21 [get_ports usb_pipe_data0_rx_data[1]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_data0_rx_data[1]]

# usb_pipe_data:0.rx_data
set_property LOC G20 [get_ports usb_pipe_data0_rx_data[2]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_data0_rx_data[2]]

# usb_pipe_data:0.rx_data
set_property LOC H20 [get_ports usb_pipe_data0_rx_data[3]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_data0_rx_data[3]]

# usb_pipe_data:0.rx_data
set_property LOC L13 [get_ports usb_pipe_data0_rx_data[4]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_data0_rx_data[4]]

# usb_pipe_data:0.rx_data
set_property LOC M16 [get_ports usb_pipe_data0_rx_data[5]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_data0_rx_data[5]]

# usb_pipe_data:0.rx_data
set_property LOC L21 [get_ports usb_pipe_data0_rx_data[6]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_data0_rx_data[6]]

# usb_pipe_data:0.rx_data
set_property LOC N19 [get_ports usb_pipe_data0_rx_data[7]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_data0_rx_data[7]]

# usb_pipe_data:0.rx_data
set_property LOC M22 [get_ports usb_pipe_data0_rx_data[8]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_data0_rx_data[8]]

# usb_pipe_data:0.rx_data
set_property LOC M18 [get_ports usb_pipe_data0_rx_data[9]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_data0_rx_data[9]]

# usb_pipe_data:0.rx_data
set_property LOC N22 [get_ports usb_pipe_data0_rx_data[10]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_data0_rx_data[10]]

# usb_pipe_data:0.rx_data
set_property LOC N20 [get_ports usb_pipe_data0_rx_data[11]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_data0_rx_data[11]]

# usb_pipe_data:0.rx_data
set_property LOC N18 [get_ports usb_pipe_data0_rx_data[12]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_data0_rx_data[12]]

# usb_pipe_data:0.rx_data
set_property LOC M15 [get_ports usb_pipe_data0_rx_data[13]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_data0_rx_data[13]]

# usb_pipe_data:0.rx_data
set_property LOC M13 [get_ports usb_pipe_data0_rx_data[14]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_data0_rx_data[14]]

# usb_pipe_data:0.rx_data
set_property LOC M20 [get_ports usb_pipe_data0_rx_data[15]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_data0_rx_data[15]]

# usb_pipe_data:0.rx_datak
set_property LOC L18 [get_ports usb_pipe_data0_rx_datak[0]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_data0_rx_datak[0]]

# usb_pipe_data:0.rx_datak
set_property LOC M21 [get_ports usb_pipe_data0_rx_datak[1]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_data0_rx_datak[1]]

# usb_pipe_data:0.tx_clk
set_property LOC F19 [get_ports usb_pipe_data0_tx_clk]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_data0_tx_clk]

# usb_pipe_data:0.tx_data
set_property LOC B16 [get_ports usb_pipe_data0_tx_data[0]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_data0_tx_data[0]]

# usb_pipe_data:0.tx_data
set_property LOC E18 [get_ports usb_pipe_data0_tx_data[1]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_data0_tx_data[1]]

# usb_pipe_data:0.tx_data
set_property LOC B15 [get_ports usb_pipe_data0_tx_data[2]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_data0_tx_data[2]]

# usb_pipe_data:0.tx_data
set_property LOC F18 [get_ports usb_pipe_data0_tx_data[3]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_data0_tx_data[3]]

# usb_pipe_data:0.tx_data
set_property LOC E17 [get_ports usb_pipe_data0_tx_data[4]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_data0_tx_data[4]]

# usb_pipe_data:0.tx_data
set_property LOC D19 [get_ports usb_pipe_data0_tx_data[5]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_data0_tx_data[5]]

# usb_pipe_data:0.tx_data
set_property LOC F16 [get_ports usb_pipe_data0_tx_data[6]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_data0_tx_data[6]]

# usb_pipe_data:0.tx_data
set_property LOC E19 [get_ports usb_pipe_data0_tx_data[7]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_data0_tx_data[7]]

# usb_pipe_data:0.tx_data
set_property LOC E21 [get_ports usb_pipe_data0_tx_data[8]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_data0_tx_data[8]]

# usb_pipe_data:0.tx_data
set_property LOC D21 [get_ports usb_pipe_data0_tx_data[9]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_data0_tx_data[9]]

# usb_pipe_data:0.tx_data
set_property LOC A19 [get_ports usb_pipe_data0_tx_data[10]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_data0_tx_data[10]]

# usb_pipe_data:0.tx_data
set_property LOC A21 [get_ports usb_pipe_data0_tx_data[11]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_data0_tx_data[11]]

# usb_pipe_data:0.tx_data
set_property LOC B21 [get_ports usb_pipe_data0_tx_data[12]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_data0_tx_data[12]]

# usb_pipe_data:0.tx_data
set_property LOC D17 [get_ports usb_pipe_data0_tx_data[13]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_data0_tx_data[13]]

# usb_pipe_data:0.tx_data
set_property LOC A18 [get_ports usb_pipe_data0_tx_data[14]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_data0_tx_data[14]]

# usb_pipe_data:0.tx_data
set_property LOC F20 [get_ports usb_pipe_data0_tx_data[15]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_data0_tx_data[15]]

# usb_pipe_data:0.tx_datak
set_property LOC C17 [get_ports usb_pipe_data0_tx_datak[0]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_data0_tx_datak[0]]

# usb_pipe_data:0.tx_datak
set_property LOC B17 [get_ports usb_pipe_data0_tx_datak[1]]
set_property IOSTANDARD LVCMOS25 [get_ports usb_pipe_data0_tx_datak[1]]

# user_sw:0
set_property LOC E22 [get_ports user_sw0]
set_property IOSTANDARD LVCMOS25 [get_ports user_sw0]

# user_sw:1
set_property LOC F21 [get_ports user_sw1]
set_property IOSTANDARD LVCMOS25 [get_ports user_sw1]

################################################################################
# Design constraints
################################################################################

set_property INTERNAL_VREF 0.750 [get_iobanks 35]

create_clock -period 10.0 clk100
