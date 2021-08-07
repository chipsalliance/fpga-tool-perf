/*
* Copyright (C) 2020  The SymbiFlow Authors.
*
*  Use of this source code is governed by a ISC-style
*  license that can be found in the LICENSE file or at
*  https://opensource.org/licenses/ISC
*
*  SPDX-License-Identifier: ISC
*/

// Baudrate generator for asyncronous data transmitters (e.g. UARTs).
module BAUDGEN (
    input clk,
    input rst,
    output reg baud_edge
);
  parameter COUNTER = 200;

  reg [$clog2(COUNTER)-1:0] counter;

  always @(posedge clk) begin
    if (rst) begin
      counter   <= 0;
      baud_edge <= 0;
    end else begin
      if (counter == COUNTER - 1) begin
        baud_edge <= 1;
        counter   <= 0;
      end else begin
        baud_edge <= 0;
        counter   <= counter + 1;
      end
    end
  end

endmodule
