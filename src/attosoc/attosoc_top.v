module top (input clk_i, input [3:0] sw, output [11:0] led);

    wire clk_bufg;
    BUFG bufg_i (
        .I(clk_i),
        .O(clk_bufg)
    );

    reg clkdiv;
    reg [22:0] ctr;

    always @(posedge clk_bufg) {clkdiv, ctr} <= ctr + 1'b1;

    wire [7:0] soc_led;
    attosoc soc_i(
        .clk(clk_bufg),
        .reset(sw[0]),
        .led(soc_led)
    );

    generate
        genvar i;
        for (i = 0; i < 4; i = i+1) begin
            assign led[0 + i] = soc_led[2 * i]; // R
            assign led[4 + i] = soc_led[(2 * i) + 1]; // G
            assign led[8 + i] = &soc_led[2 * i +: 2]; // B
        end
    endgenerate
endmodule
