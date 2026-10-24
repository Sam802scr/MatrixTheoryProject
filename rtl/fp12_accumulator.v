
module fp12_accumulator (
    input  wire        clk,
    input  wire        rst,
    input  wire        enable,
    input  wire signed [11:0] addend,
    output reg  signed [11:0] accumulator
);

always @(posedge clk) begin
    if (rst) begin
        accumulator <= 12'sd0;
    end
    else if (enable) begin
        accumulator <= accumulator + addend;
    end
end

endmodule
