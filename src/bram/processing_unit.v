/*
* Copyright 2018-2022 F4PGA Authors
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*     http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*
* SPDX-License-Identifier: Apache-2.0
*/

module processing_unit
(
// Closk & reset
input  wire CLK,
input  wire RST,

// Data input
input  wire         I_STB,
input  wire [31:0]  I_DAT,

// Data output
output wire         O_STB,
output wire [31:0]  O_DAT
);

// ============================================================================

wire [15:0] i_dat_a = I_DAT[15: 0];
wire [15:0] i_dat_b = I_DAT[31:16];

reg         o_stb;
reg  [31:0] o_dat;

always @(posedge CLK)
    o_dat <= i_dat_a * i_dat_b;

always @(posedge CLK or posedge RST)
    if (RST) o_stb <= 1'd0;
    else     o_stb <= I_STB;

assign O_STB = o_stb;
assign O_DAT = o_dat;

// ============================================================================

endmodule

