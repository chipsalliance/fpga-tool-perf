module top (
        input wire clk,
        output wire out);
    reg [23:0] counter;
    assign out = counter[23];

    always @(posedge clk) begin
        counter <= counter + 1;
    end
endmodule
