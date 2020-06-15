SHELL=/bin/bash
NAME := oneblink
BITSTREAM := oneblink.bit
PART := xc7a35tcpg236-1

all: $(BITSTREAM)

$(NAME).runs/synth_1/__synthesis_is_complete__: $(NAME)_synth.tcl $(NAME).xpr
	source /home/student/Xilinx_2017.2/Vivado/2017.2/settings64.sh && vivado -notrace -mode batch -source $^

synth: $(NAME).runs/synth_1/__synthesis_is_complete__

$(BITSTREAM): $(NAME)_run.tcl synth
	source /home/student/Xilinx_2017.2/Vivado/2017.2/settings64.sh && vivado -notrace -mode batch -source $< $(NAME).xpr

$(NAME).xpr: $(NAME).tcl
	source /home/student/Xilinx_2017.2/Vivado/2017.2/settings64.sh && vivado -notrace -mode batch -source $<

build-gui: $(NAME).xpr
	source /home/student/Xilinx_2017.2/Vivado/2017.2/settings64.sh && vivado $<

pgm: $(NAME)_pgm.tcl $(BITSTREAM)
	export HW_TARGET=$(HW_TARGET); \
	export JTAG_FREQ=$(JTAG_FREQ); \
	source /home/student/Xilinx_2017.2/Vivado/2017.2/settings64.sh && vivado -quiet -nolog -notrace -mode batch -source $< -tclargs $(PART) $(BITSTREAM)
