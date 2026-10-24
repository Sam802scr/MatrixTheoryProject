
module lfsr #(
    parameter WIDTH = 8,
    parameter SEED  = 8'hA5
)(
    input  wire             clk,
    input  wire             rst,
    input  wire             enable,
    output reg  [WIDTH-1:0] random_bits
);

    wire feedback;

    // 8-bit LFSR feedback taps: bits 7, 5, 4, 3
    assign feedback = random_bits[7] ^
                      random_bits[5] ^
                      random_bits[4] ^
                      random_bits[3];

    always @(posedge clk) begin
        if (rst) begin
            random_bits <= SEED;
        end
        else if (enable) begin
            random_bits <= {random_bits[WIDTH-2:0], feedback};
        end
    end

endmodule
