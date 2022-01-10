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

// Baudrate generator for asyncronous data transmitters (e.g. UARTs).
module BAUDGEN(
    input clk,
    input rst,
    output reg baud_edge
);
    parameter COUNTER = 200;

    reg [$clog2(COUNTER)-1:0] counter;

    always @(posedge clk) begin
        if(rst) begin
            counter <= 0;
            baud_edge <= 0;
        end else begin
            if(counter == COUNTER-1) begin
                baud_edge <= 1;
                counter <= 0;
            end else begin
                baud_edge <= 0;
                counter <= counter + 1;
            end
        end
    end
endmodule
