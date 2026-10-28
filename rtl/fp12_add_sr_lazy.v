// FP12 adder with LAZY stochastic rounding (paper Fig. 3a): exact add -> normalize -> add R random bits to
// the r extra bits below the p-bit significand; the carry rounds up.
module fp12_add_sr_lazy #(parameter R = 18) (
    input  wire [11:0]  a,
    input  wire [11:0]  b,
    input  wire [R-1:0] random_bits,
    output reg  [11:0]  result
);
    localparam P = 6;
    reg        sx, sy, sub;
    reg [5:0]  ex, ey, mx, my, d;
    reg [P+R:0] Xs, Ys, T, Tn;
    reg [R:0]  sum;
    reg [6:0]  mz;
    integer    L, ez, i;

    always @* begin
        result = 12'd0;
        sx = 0; sy = 0; ex = 0; ey = 0; mx = 0; my = 0; d = 0; Xs = 0; Ys = 0; T = 0; Tn = 0;
        sum = 0; mz = 0; L = 0; ez = 0; sub = 0;
        if (a[10:5] == 6'd63)               result = a;
        else if (b[10:5] == 6'd63)          result = b;
        else if (a[10:5] == 0 && b[10:5] == 0) result = 12'd0;
        else if (a[10:5] == 0)              result = b;
        else if (b[10:5] == 0)              result = a;
        else begin
            if (a[10:0] >= b[10:0]) begin
                sx = a[11]; ex = a[10:5]; mx = {1'b1, a[4:0]};
                sy = b[11]; ey = b[10:5]; my = {1'b1, b[4:0]};
            end else begin
                sx = b[11]; ex = b[10:5]; mx = {1'b1, b[4:0]};
                sy = a[11]; ey = a[10:5]; my = {1'b1, a[4:0]};
            end
            d   = ex - ey;
            sub = sx ^ sy;
            Xs  = mx << (R - 1);
            Ys  = (my << (R - 1)) >> d;               // shifted-out bits truncated (no sticky)
            T   = sub ? (Xs - Ys) : (Xs + Ys);
            if (T != 0) begin
                L = 0;
                for (i = 0; i < P + R + 1; i = i + 1) if (T[i]) L = i + 1;   // bit length
                Tn  = T << (P + R - L);
                sum = {1'b0, Tn[R-1:0]} + {1'b0, random_bits};
                mz  = {1'b0, Tn[P+R-1:R]} + sum[R];
                ez  = ex + (L - (P + R - 1));
                if (mz[6]) begin mz = 7'd32; ez = ez + 1; end
                if (ez < 1)       result = 12'd0;
                else if (ez > 62) result = {sx, 6'd62, 5'h1F};
                else              result = {sx, ez[5:0], mz[4:0]};
            end
        end
    end
endmodule
