// FP12 E6M5 adder, round-to-nearest-even (the RN baseline). Synthesizable (no while loops).
// 3 extra bits + sticky-OR into the LSB; subnormals flushed; overflow saturates.
module fp12_add (
    input  wire [11:0] a,
    input  wire [11:0] b,
    output reg  [11:0] result
);
    reg        sx, sy, sub;
    reg [5:0]  ex, ey, mx, my, d;
    reg [8:0]  Xs, Yf, Ys, lostmask;
    reg [9:0]  T, Tn;
    reg [3:0]  lz, msb;
    reg [5:0]  top;
    reg [3:0]  rem_;
    reg        inc;
    reg [6:0]  mz;
    integer    ez, i;

    always @* begin
        result = 12'd0;
        sx = 0; sy = 0; ex = 0; ey = 0; mx = 0; my = 0; d = 0; Xs = 0; Yf = 0; Ys = 0; lostmask = 0;
        T = 0; Tn = 0; lz = 0; msb = 0; top = 0; rem_ = 0; inc = 0; mz = 0; ez = 0; sub = 0;
        if (a[10:5] == 6'd63)               result = a;
        else if (b[10:5] == 6'd63)          result = b;
        else if (a[10:5] == 0 && b[10:5] == 0) result = 12'd0;
        else if (a[10:5] == 0)              result = b;
        else if (b[10:5] == 0)              result = a;
        else begin
            // swap so that x has the larger magnitude
            if (a[10:0] >= b[10:0]) begin
                sx = a[11]; ex = a[10:5]; mx = {1'b1, a[4:0]};
                sy = b[11]; ey = b[10:5]; my = {1'b1, b[4:0]};
            end else begin
                sx = b[11]; ex = b[10:5]; mx = {1'b1, b[4:0]};
                sy = a[11]; ey = a[10:5]; my = {1'b1, a[4:0]};
            end
            d   = ex - ey;
            sub = sx ^ sy;
            Xs  = {mx, 3'b000};
            Yf  = {my, 3'b000};
            Ys  = (d >= 9) ? 9'd0 : (Yf >> d);
            lostmask = (d >= 9) ? 9'h1FF : ~(9'h1FF << d);
            if ((Yf & lostmask) != 0) Ys[0] = 1'b1;           // sticky
            T = sub ? ({1'b0, Xs} - {1'b0, Ys}) : ({1'b0, Xs} + {1'b0, Ys});
            if (T != 0) begin
                msb = 0;
                for (i = 0; i < 10; i = i + 1) if (T[i]) msb = i;
                lz  = 9 - msb;
                Tn  = T << lz;
                top  = Tn[9:4];
                rem_ = Tn[3:0];
                inc  = (rem_ > 4'd8) || (rem_ == 4'd8 && top[0]);
                mz   = {1'b0, top} + inc;
                ez   = ex + 1 - lz;
                if (mz[6]) begin mz = 7'd32; ez = ez + 1; end
                if (ez < 1)       result = 12'd0;
                else if (ez > 62) result = {sx, 6'd62, 5'h1F};
                else              result = {sx, ez[5:0], mz[4:0]};
            end
        end
    end
endmodule
