// FP12 adder with ADAPTIVE Stochastic Rounding (ASR).
// Supports dynamic run-time selection of random bit precision r in {4, 7, 9, 11, 13}
// via MSB-aligned operand and PRNG bit gating.
// Enables fine-grained stochastic rounding during critical convergence phases while
// suppressing dynamic switching activity in early/coarse training phases.
module fp12_add_sr_adaptive (
    input  wire [11:0] a,
    input  wire [11:0] b,
    input  wire [12:0] random_bits, // up to 13 bits of random input
    input  wire [2:0]  r_sel,       // 0: r=4, 1: r=7, 2: r=9, 3: r=11, 4: r=13
    output reg  [11:0] result
);
    localparam P = 6;
    localparam R_MAX = 13;

    reg        sx, sy, sub, far;
    reg [5:0]  ex, ey, mx, my, d;
    reg [P+R_MAX-2:0] Ys;
    reg [P:0]  Ytop;
    reg [10:0] Ylow_raw, Ylow, Llow;
    reg        borrow;
    reg [P+1:0] Ttop;
    reg [P+3:0] V, Vn;
    reg [3:0]  j, jfar, jclose;
    reg [5:0]  sig;
    reg [6:0]  mz;
    reg [1:0]  g;
    integer    ez, i;

    reg [1:0]  R12;
    reg [10:0] R3_ext;
    reg [10:0] mask;

    // Dynamic operand gating and bit extraction according to r_sel
    always @* begin
        case (r_sel)
            3'b000: begin // r = 4 (k = 2)
                R12    = random_bits[3:2];
                R3_ext = {random_bits[1:0], 9'b0};
                mask   = 11'h600;
            end
            3'b001: begin // r = 7 (k = 5)
                R12    = random_bits[6:5];
                R3_ext = {random_bits[4:0], 6'b0};
                mask   = 11'h7C0;
            end
            3'b010: begin // r = 9 (k = 7)
                R12    = random_bits[8:7];
                R3_ext = {random_bits[6:0], 4'b0};
                mask   = 11'h7F0;
            end
            3'b011: begin // r = 11 (k = 9)
                R12    = random_bits[10:9];
                R3_ext = {random_bits[8:0], 2'b0};
                mask   = 11'h7FC;
            end
            default: begin // r = 13 (k = 11)
                R12    = random_bits[12:11];
                R3_ext = random_bits[10:0];
                mask   = 11'h7FF;
            end
        endcase
    end

    // Sticky round stage instantiated for R_MAX = 13 (11-bit carry chain)
    wire s1, s2, s3;
    fp12_sticky_round #(.R(R_MAX)) u_sticky (
        .y_low(Llow),
        .rand_low(R3_ext),
        .s1(s1),
        .s2(s2),
        .s3(s3)
    );

    // Second stage + Round Correction
    wire up;
    fp12_round_correction u_corr (
        .j(j),
        .norm_rs(Vn[3:2]),
        .g(g),
        .r12(R12),
        .s1(s1),
        .s2(s2),
        .s3(s3),
        .up(up)
    );

    always @* begin
        result = 12'd0;
        sx = 0; sy = 0; sub = 0; far = 0; ex = 0; ey = 0; mx = 0; my = 0; d = 0;
        Ys = 0; Ytop = 0; Ylow_raw = 0; Ylow = 0; Llow = 0; borrow = 0; Ttop = 0;
        V = 0; Vn = 0; j = 0; jfar = 0; jclose = 0; sig = 0; mz = 0; g = 0; ez = 0;

        if (a[10:5] == 6'd63)               result = a;
        else if (b[10:5] == 6'd63)          result = b;
        else if (a[10:5] == 0 && b[10:5] == 0) result = 12'd0;
        else if (a[10:5] == 0)              result = b;
        else if (b[10:5] == 0)              result = a;
        else begin
            // (i) Reorder / swap
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

            // (ii) Alignment with dynamic operand gating
            Ys       = (my << (R_MAX - 1)) >> d;
            Ytop     = Ys[P+R_MAX-2:R_MAX-2];
            Ylow_raw = Ys[R_MAX-3:0];
            Ylow     = Ylow_raw & mask;

            Llow   = sub ? ((~Ylow + 1'b1) & 11'h7FF) : Ylow;
            borrow = sub & (Ylow != 0);

            // (iii) Main adder (P+2 bits)
            Ttop = sub ? ({1'b0, mx, 1'b0} - {1'b0, Ytop} - borrow)
                       : ({1'b0, mx, 1'b0} + {1'b0, Ytop});

            if (Ttop != 0 || Llow != 0) begin
                // (iv) Normalization
                jfar = Ttop[P+1] ? 4'd0 : (Ttop[P] ? 4'd1 : 4'd2);
                jclose = 4'd0;
                for (i = 0; i < P + 2; i = i + 1) if (Ttop[i]) jclose = (P + 1) - i;
                j  = far ? jfar : jclose;
                g  = {Llow[10], Llow[9]};
                V  = {Ttop, 2'b00};
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
