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

// UART transmitter.
module UART_TX(
    input rst, clk, baud_edge, data_ready,
    input [7:0] data,
    output reg tx, data_accepted
);
    localparam START = (1 << 0), DATA = (1 << 1), END = (1 << 2);

    reg [7:0] data_reg;
    reg [2:0] data_counter;
    reg [3:0] state;

    initial begin
        tx <= 1;
        data_accepted <= 0;
    end

    always @(posedge clk) begin
        if(rst) begin
            state <= END;
            tx <= 1;
            data_accepted <= 0;
        end else if(baud_edge) begin
            case(state)
            START: begin
                tx <= 0;
                data_counter <= 0;
                state <= DATA;
            end
            DATA: begin
                tx <= data_reg[data_counter];
                if(data_counter != 7) begin
                    data_counter <= data_counter + 1;
                end else begin
                    state <= END;
                    data_counter <= 0;
                end
            end
            END: begin
                tx <= 1;
                if(data_ready) begin
                    data_accepted <= 1;
                    data_reg <= data;
                    state <= START;
                end
            end
            default: begin
                tx <= 1;
                state <= END;
            end
            endcase
        end else begin
            data_accepted <= 0;
        end
    end
endmodule
