# Murax SoC

This test is the
[Murax SoC from VexRiscv](https://github.com/SpinalHDL/VexRiscv#murax-soc)
built from
[revision 373a3fcb909c3df6c03421b21f73f83b44cb5cc6](https://github.com/SpinalHDL/VexRiscv/commit/373a3fcb909c3df6c03421b21f73f83b44cb5cc6)
using `sbt "run-main vexriscv.demo.MuraxWithRamInit"`.

It uses about ~2500 LUTs and ~1500 flipflops meaning it should fit in all of;
 * up3k
 * lm4k
 * up5k
 * lp8k
 * hx8k

This makes it a great test for comparison of the FOSS tools with icecube2 and
Radiant as the only common part all these tools support is the up5k which is
too small to fit the other larger tests.
