/*
* Copyright (C) 2020  The SymbiFlow Authors.
*
*  Use of this source code is governed by a ISC-style
*  license that can be found in the LICENSE file or at
*  https://opensource.org/licenses/ISC
*
*  SPDX-License-Identifier: ISC
*/

// Linear feedback shift register.
//
// Useful as a simple psuedo-random number generator.
module LFSR #(
    parameter WIDTH = 16,
    parameter POLY  = 16'hD008
) (
    input rst,
    input clk,
    input [WIDTH-1:0] seed,
    output reg [WIDTH-1:0] r
);
  wire feedback = ^(r & POLY);

  always @(posedge clk) begin
    if (rst) begin
      r <= seed;
    end else begin
      r <= {r[WIDTH-2:0], feedback};
    end
  end

endmodule
