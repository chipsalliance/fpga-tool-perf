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
    input wire clk,
    output wire out
);

    reg [23:0] counter;
    
    always @(posedge clk) begin
        counter <= counter + 1;
    end

    assign out = counter[23];

endmodule
