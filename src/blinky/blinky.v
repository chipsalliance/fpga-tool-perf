/*
* Copyright (C) 2020  The SymbiFlow Authors.
*
*  Use of this source code is governed by a ISC-style
*  license that can be found in the LICENSE file or at
*  https://opensource.org/licenses/ISC
*
*  SPDX-License-Identifier: ISC
*/
module top (
    input clk_i,
    output [11:0] led
);

  // assign led = {&sw, |sw, ^sw, ~^sw};

  wire clk;
  BUFG bufg_i (
      .I(clk_i),
      .O(clk)
  );

  // wire clk = clk_i;

  reg clkdiv;
  reg [22:0] ctr;

  always @(posedge clk) {clkdiv, ctr} <= ctr + 1'b1;

  reg [5:0] led_r = 4'b0000;

  always @(posedge clk) begin
    if (clkdiv) led_r <= led_r + 1'b1;
  end

  wire [11:0] led_s = led_r[3:0] << (4 * led_r[5:4]);

  assign led = &(led_r[5:4]) ? {3{led_r[3:0]}} : led_s;

endmodule
