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
module top (input clk_i, output [11:0] led);

    //assign led = {&sw, |sw, ^sw, ~^sw};

    wire clk;
    BUFG bufg_i (
        .I(clk_i),
        .O(clk)
    );


  //  wire clk = clk_i;

    reg clkdiv;
    reg [22:0] ctr;

    always @(posedge clk) {clkdiv, ctr} <= ctr + 1'b1;

    reg [5:0] led_r = 4'b0000;

    always @(posedge clk) begin
        if (clkdiv)
            led_r <= led_r + 1'b1;
    end

    wire [11:0] led_s = led_r[3:0] << (4 * led_r[5:4]);

    assign led = &(led_r[5:4]) ? {3{led_r[3:0]}} : led_s;

endmodule
