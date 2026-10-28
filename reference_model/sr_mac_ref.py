"""
Golden, integer-exact model of the DATE-2024 MAC (FP8 E5M2 x FP8 E5M2 -> FP12 E6M5 accumulate).

Policies (the paper does not specify them; they are fixed HERE and mirrored 1:1 in the RTL):
  * no subnormals: exponent field 0 => value 0 (inputs and results flushed)
  * exponent field all-ones (31 for FP8, 63 for FP12) = "special": never produced by arithmetic;
    multiplier emits FP12 exp 63, adder propagates a special operand unchanged
  * overflow saturates to max finite; zero result is +0; sign-magnitude rounding
Random word rand (r bits): rand[r-1:r-2] = R12 (2 MSBs), rand[r-3:0] = R3 (r-2 LSBs)
"""
P, E_BIAS, EMIN, EMAX = 6, 31, -30, 31          # FP12 E6M5: p=6, emax code 62 -> e=31
MAXFIN = (62 << 5) | 31                          # 0x7DF magnitude

# ---------------------------------------------------------------- formats
def fp12_unpack(b):
    s, ex, fr = (b >> 11) & 1, (b >> 5) & 63, b & 31
    if ex == 63: return None
    if ex == 0:  return (s, EMIN, 0)
    return (s, ex - E_BIAS, 32 | fr)

def fp12_pack(s, e, m):
    if m == 0 or e < EMIN: return 0
    if e > EMAX: return (s << 11) | MAXFIN
    return (s << 11) | ((e + E_BIAS) << 5) | (m & 31)

def fp12_value(b):
    from fractions import Fraction
    s, ex, fr = (b >> 11) & 1, (b >> 5) & 63, b & 31
    if ex == 0: return Fraction(0)
    v = Fraction(32 + fr, 32) * Fraction(2) ** (ex - E_BIAS)
    return -v if s else v

# ---------------------------------------------------------------- FP8 x FP8 -> FP12 (exact)
def fp8_mul(a, b):
    sa, ea, fa = a >> 7, (a >> 2) & 31, a & 3
    sb, eb, fb = b >> 7, (b >> 2) & 31, b & 3
    s = sa ^ sb
    if ea == 31 or eb == 31: return (s << 11) | (63 << 5)
    if ea == 0 or eb == 0:   return 0
    P_ = (4 | fa) * (4 | fb)                         # 5 or 6 bits
    top = (P_ >> 5) & 1
    m = P_ if top else P_ << 1                       # 6-bit significand
    E = ea + eb + 1 + top                            # biased FP12 exponent (3..62)
    return (s << 11) | (E << 5) | (m & 31)

# ---------------------------------------------------------------- shared front end
def _front(a, b):
    """returns ('ret', bits) or ('go', x, y) with x the larger-magnitude operand."""
    if (a >> 5) & 63 == 63: return ('ret', a)
    if (b >> 5) & 63 == 63: return ('ret', b)
    x, y = fp12_unpack(a), fp12_unpack(b)
    if x[2] == 0 and y[2] == 0: return ('ret', 0)
    if x[2] == 0: return ('ret', b)
    if y[2] == 0: return ('ret', a)
    if (x[1], x[2]) < (y[1], y[2]): x, y = y, x
    return ('go', x, y)

# ---------------------------------------------------------------- RN (nearest-even) baseline
def add_rn(a, b):
    f = _front(a, b)
    if f[0] == 'ret': return f[1]
    _, (sx, ex, mx), (sy, ey, my) = f
    d = ex - ey
    Xs = mx << 3
    Yfull = my << 3
    Ys = Yfull >> d
    if d > 0 and (Yfull & ((1 << d) - 1) if d < 40 else Yfull): Ys |= 1      # sticky into LSB
    T = Xs + Ys if sx == sy else Xs - Ys
    if T == 0: return 0
    L = T.bit_length()                               # nominal (no carry) length = P+3 = 9
    ez = ex + (L - 9)
    if L > P:                                        # keep P bits, GRS below
        sh = L - P
        top, rem = T >> sh, T & ((1 << sh) - 1)
        half = 1 << (sh - 1)
        if rem > half or (rem == half and (top & 1)): top += 1
    else:
        top = T << (P - L)
    if top == 1 << P: top >>= 1; ez += 1
    return fp12_pack(sx, ez, top)

# ---------------------------------------------------------------- lazy SR (add r bits to normalized result)
def add_lazy(a, b, rand, r=18):
    f = _front(a, b)
    if f[0] == 'ret': return f[1]
    _, (sx, ex, mx), (sy, ey, my) = f
    d = ex - ey
    Xs, Ys = mx << (r - 1), (my << (r - 1)) >> d
    T = Xs + Ys if sx == sy else Xs - Ys
    if T == 0: return 0
    L = T.bit_length()
    ez = ex + (L - (P + r - 1))
    Tn = T << (P + r - L)
    top, E = Tn >> r, Tn & ((1 << r) - 1)
    mz = top + ((E + rand) >> r)
    if mz == 1 << P: mz >>= 1; ez += 1
    return fp12_pack(sx, ez, mz)

# ---------------------------------------------------------------- eager SR (paper Fig. 3b / Fig. 4)
def add_eager(a, b, rand, r=18, info=None):
    f = _front(a, b)
    if f[0] == 'ret': return f[1]
    _, (sx, ex, mx), (sy, ey, my) = f
    d, sub = ex - ey, sx != sy
    mlo, m3, m4 = (1 << (r - 2)) - 1, (1 << (r - 3)) - 1, (1 << (r - 4)) - 1
    # swap/align: shifted y has P+r-1 bits; split into top P+1 bits (main adder) and low r-2 bits (Sticky Round)
    Ys = (my << (r - 1)) >> d
    Ytop, Ylow = Ys >> (r - 2), Ys & mlo
    Xtop = mx << 1
    # 2's complement of the full shifted word, then split
    if sub: Llow, borrow = (-Ylow) & mlo, int(Ylow != 0)
    else:   Llow, borrow = Ylow, 0
    Ttop = Xtop - Ytop - borrow if sub else Xtop + Ytop           # main adder, P+2 bits
    if Ttop == 0 and Llow == 0: return 0
    R12, R3 = rand >> (r - 2), rand & mlo
    # ---- first rounding stage ("Sticky Round"): carries of  Llow + R3
    S1 = (Llow + R3) >> (r - 2)                                   # carry-out of the (r-2)-bit adder
    S2 = ((Llow & m3) + (R3 & m3)) >> (r - 3)                     # carry into its MSB
    S3 = ((Llow & m4) + (R3 & m4)) >> (r - 4)                     # carry into bit r-4 (only needed for far-path SUBTRACTION, j=2)
    G2 = ((Llow >> (r - 4)) & 1) | ((Llow >> (r - 3)) & 1) << 1   # {G, G2}: two bits just below the main adder
    # ---- normalization: far path = carry-dependent 1-bit; close path = LZD (L==0 there)
    j = (P + 2) - Ttop.bit_length()                               # leading zeros in the P+2 bit field
    if d >= 2: assert j <= 2          # j=2 only for effective subtraction (paper analyses addition only)
    else:      assert Llow == 0
    V = (Ttop << 2) | G2                                          # {Ttop, G, G2}: G/G2 replace the shifted-in zeros
    Vn = (V << j) & ((1 << (P + 4)) - 1)
    sig, Rb, Sb = Vn >> 4, (Vn >> 3) & 1, (Vn >> 2) & 1
    # ---- second rounding stage + Round Correction
    cin = (S1, S2, S3)[min(j, 2)]
    up = (((Rb << 1) | Sb) + R12 + cin) >> 2
    mz, ez = sig + up, ex + 1 - j
    if mz == 1 << P: mz >>= 1; ez += 1
    if info is not None: info['j'] = j
    return fp12_pack(sx, ez, mz)

def lazy_equiv_rand(rand, j, r=18):
    """random word that makes LAZY reproduce EAGER bit-exactly: identical for j==0;
    j==1 / j==2: eager drops the top 1 / 2 bits of R3 and the result has 1 / 2 implicit zero LSBs;
    j>=3 (close path) the sum is exact so any word works."""
    hi = (rand >> (r - 2)) << (r - 2)
    if j == 1: return hi | ((rand & ((1 << (r - 3)) - 1)) << 1)
    if j == 2: return hi | ((rand & ((1 << (r - 4)) - 1)) << 2)
    return rand

# ---------------------------------------------------------------- LFSR / MAC
class GaloisLFSR:
    """x^18 + x^11 + 1 (primitive). Taps/seed/steps-per-word are ASSUMPTIONS (paper gives none)."""
    def __init__(s, n=18, mask=(1 << 17) | (1 << 10), seed=1, steps=18):
        s.n, s.mask, s.state, s.steps = n, mask, seed, steps
    def step(s):
        lsb = s.state & 1; s.state >>= 1
        if lsb: s.state ^= s.mask
    def word(s):
        for _ in range(s.steps): s.step()
        return s.state

def mac(acc, a8, b8, rand, mode='eager', r=18):
    p = fp8_mul(a8, b8)
    if mode == 'rn':    return add_rn(acc, p)
    if mode == 'lazy':  return add_lazy(acc, p, rand, r)
    return add_eager(acc, p, rand, r)
