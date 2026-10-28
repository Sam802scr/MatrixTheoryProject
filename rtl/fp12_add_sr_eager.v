// FP12 adder with EAGER stochastic rounding (paper Fig. 3b / Fig. 4).
//   swap/align -> split shifted y into top P+1 bits (main adder) and low R-2 bits (Sticky Round, first rounding
//   stage, done BEFORE normalization) -> normalize (far path: carry-dependent shift; close path: LZD)
//   -> Round Correction (second stage) -> increment.
// random_bits = {R1,R2, R3[R-3:0]}.
module fp12_add_sr_eager #(parameter R = 18) (
    input  wire [11:0]  a,
    input  wire [11:0]  b,
    input  wire [R-1:0] random_bits,
    output reg  [11:0]  result
);
    localparam P = 6;
    reg        sx, sy, sub, far;
    reg [5:0]  ex, ey, mx, my, d;
    reg [P+R-2:0] Ys;
    reg [P:0]  Ytop;
    reg [R-3:0] Ylow, Llow;
    reg        borrow;
    reg [P+1:0] Ttop;
    reg [P+3:0] V, Vn;
    reg [3:0]  j, jfar, jclose;
    reg [5:0]  sig;
    reg [6:0]  mz;
    reg [1:0]  g;
    integer    ez, i;

    wire [R-3:0] R3  = random_bits[R-3:0];
    wire [1:0]   R12 = random_bits[R-1:R-2];

    // ---- first rounding stage (uses Llow = low bits of the 2's-complemented aligned operand)
    wire s1, s2, s3;
    fp12_sticky_round #(.R(R)) u_sticky (.y_low(Llow), .rand_low(R3), .s1(s1), .s2(s2), .s3(s3));

    // ---- second stage + correction
    wire up;
    fp12_round_correction u_corr (.j(j), .norm_rs(Vn[3:2]), .g(g), .r12(R12), .s1(s1), .s2(s2), .s3(s3), .up(up));

    always @* begin
        result = 12'd0;
        sx = 0; sy = 0; sub = 0; far = 0; ex = 0; ey = 0; mx = 0; my = 0; d = 0; Ys = 0; Ytop = 0; Ylow = 0;
        Llow = 0; borrow = 0; Ttop = 0; V = 0; Vn = 0; j = 0; jfar = 0; jclose = 0; sig = 0; mz = 0; g = 0; ez = 0;
        if (a[10:5] == 6'd63)               result = a;
        else if (b[10:5] == 6'd63)          result = b;
        else if (a[10:5] == 0 && b[10:5] == 0) result = 12'd0;
        else if (a[10:5] == 0)              result = b;
        else if (b[10:5] == 0)              result = a;
        else begin
            // (i) reorder / swap (exponent first, significand on a tie)
            if (a[10:0] >= b[10:0]) begin
                sx = a[11]; ex = a[10:5]; mx = {1'b1, a[4:0]};
                sy = b[11]; ey = b[10:5]; my = {1'b1, b[4:0]};
            end else begin
                sx = b[11]; ex = b[10:5]; mx = {1'b1, b[4:0]};
                sy = a[11]; ey = a[10:5]; my = {1'b1, a[4:0]};
            end
            d   = ex - ey;
            sub = sx ^ sy;
            far = (d >= 2);
            // (ii) alignment: shifted y is P+R-1 bits; main adder gets the top P+1, Sticky Round the low R-2
            Ys   = (my << (R - 1)) >> d;
            Ytop = Ys[P+R-2:R-2];
            Ylow = Ys[R-3:0];
            // 2's complement of the full word, split
            Llow   = sub ? (~Ylow + 1'b1) : Ylow;
            borrow = sub & (Ylow != 0);
            // (iii) main adder  (P+2 bits: carry, P significand bits, 1 guard)
            Ttop = sub ? ({1'b0, mx, 1'b0} - {1'b0, Ytop} - borrow)
                       : ({1'b0, mx, 1'b0} + {1'b0, Ytop});
            if (Ttop != 0 || Llow != 0) begin
                // (iv) normalization.  far path: j in {0,1,2}; close path: LZD (Llow == 0 there)
                jfar = Ttop[P+1] ? 4'd0 : (Ttop[P] ? 4'd1 : 4'd2);
                jclose = 4'd0;
                for (i = 0; i < P + 2; i = i + 1) if (Ttop[i]) jclose = (P + 1) - i;
                j  = far ? jfar : jclose;
                g  = {Llow[R-3], Llow[R-4]};
                V  = {Ttop, 2'b00};                      // zero fill: normalizer knows nothing below the adder
                Vn = V << j;
                sig = Vn[P+3:4];
                // (v) Round Correction + increment
                mz = {1'b0, sig} + up;
                ez = ex + 1 - j;
                if (mz[6]) begin mz = 7'd32; ez = ez + 1; end
                if (ez < 1)       result = 12'd0;
                else if (ez > 62) result = {sx, 6'd62, 5'h1F};
                else              result = {sx, ez[5:0], mz[4:0]};
            end
        end
    end
endmodule
