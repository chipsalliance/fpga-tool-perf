# Auto-generated project tcl file

create_project oneblink -force

set_property part xc7a35tcpg236-1 [current_project]



set_property verilog_define {VIVADO=1 } [get_filesets sources_1]
read_verilog /home/student/fpga-tool-perf/src/oneblink/oneblink.v
read_xdc /home/student/fpga-tool-perf/src/oneblink/constr/basys3.xdc

set_property include_dirs [list .] [get_filesets sources_1]
set_property top top [current_fileset]
set_property source_mgmt_mode None [current_project]
