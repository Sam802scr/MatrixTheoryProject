import random, sys
from fractions import Fraction
from sr_mac_ref import *

def rnd12(rng, lo=1, hi=62): return rng.randrange(2) << 11 | rng.randrange(lo, hi + 1) << 5 | rng.randrange(32)

def neigh(S):
    a = abs(S); e = a.numerator.bit_length() - a.denominator.bit_length()
    if Fraction(2) ** e > a: e -= 1
    ulp = Fraction(2) ** (e - 5); lo = (a // ulp) * ulp
    return e, lo, lo + ulp, ulp

def test_multiplier():
    for a in range(256):
        for b in range(256):
            if (a >> 2) & 31 in (0, 31) or (b >> 2) & 31 in (0, 31): continue
            def v8(x):
                s, e, f = x >> 7, (x >> 2) & 31, x & 3
                v = Fraction(4 + f, 4) * Fraction(2) ** (e - 15); return -v if s else v
            assert fp12_value(fp8_mul(a, b)) == v8(a) * v8(b), (a, b)

def test_rn(n=300000):
    rng = random.Random(1)
    for _ in range(n):
        d = rng.choice([0, 0, 1, 2, 3, 5, 6, 7, 8, 9, 12, 40])
        e = rng.randrange(10, 50)
        a = rng.randrange(2) << 11 | e << 5 | rng.randrange(32)
        b = rng.randrange(2) << 11 | max(1, e - d) << 5 | rng.randrange(32)
        if rng.random() < .5: a, b = b, a
        S = fp12_value(a) + fp12_value(b)
        got = add_rn(a, b)
        if S == 0: assert got == 0; continue
        e2, lo, hi, ulp = neigh(S)
        if e2 < EMIN: assert got == 0; continue
        q = (abs(S) - lo) / ulp
        up = q > Fraction(1, 2) or (q == Fraction(1, 2) and int(lo / ulp) % 2 == 1)
        ref = hi if up else lo
        assert abs(fp12_value(got)) == ref and (fp12_value(got) < 0) == (S < 0), (hex(a), hex(b), hex(got), float(S))

def test_eager_vs_lazy(n=200000, r=18):
    rng = random.Random(2); c = {0: 0, 1: 0, 2: 0}
    for _ in range(n):
        d = rng.choice([0, 0, 1, 1, 2, 3, 4, 6, 8, 12, 20, 40])
        e = rng.randrange(10, 50)
        a = rng.randrange(2) << 11 | e << 5 | rng.randrange(32)
        b = rng.randrange(2) << 11 | max(1, e - d) << 5 | rng.randrange(32)
        if rng.random() < .5: a, b = b, a
        R = rng.randrange(1 << r); info = {}
        ge = add_eager(a, b, R, r, info)
        gl = add_lazy(a, b, lazy_equiv_rand(R, info.get('j', 0), r), r)
        assert ge == gl, (hex(a), hex(b), R, info, hex(ge), hex(gl))
        c[min(info.get('j', 0), 2)] += 1
    print("  eager==lazy(mapped) bit-exact; cases by normalization shift j=0/1/>=2:", c)

def test_probability(r=7, pairs=3000):
    """exhaustive over all 2^r random words: P(up) must equal the ideal q within truncation error."""
    rng = random.Random(3); worst = 0
    for _ in range(pairs):
        d = rng.choice([0, 1, 2, 3, 5, 8, 20]); e = rng.randrange(12, 45)
        a = rng.randrange(2) << 11 | e << 5 | rng.randrange(32)
        b = rng.randrange(2) << 11 | max(1, e - d) << 5 | rng.randrange(32)
        S = fp12_value(a) + fp12_value(b)
        if S == 0: continue
        e2, lo, hi, ulp = neigh(S); q = (abs(S) - lo) / ulp
        ups = 0
        for R in range(1 << r):
            v = abs(fp12_value(add_eager(a, b, R, r)))
            assert v in (lo, hi), (hex(a), hex(b), R)
            ups += (v == hi and q != 0)
        err = abs(Fraction(ups, 1 << r) - q); worst = max(worst, err)
        assert err <= Fraction(1, 1 << (r - 3)), (hex(a), hex(b), float(q), ups / (1 << r))
    print("  P(up) vs ideal q, r=%d exhaustive: worst |error| = %.5f (bound 2^-(r-3) = %.5f)" % (r, float(worst), 2 ** -(r - 3)))

def test_lfsr():
    l = GaloisLFSR(steps=1); s0 = l.state; n = 0
    while True:
        l.step(); n += 1
        if l.state == s0: break
    assert n == (1 << 18) - 1

def test_stagnation(N=4096):
    one = 0x3E0; a8 = (12 << 2); b8 = (11 << 2)       # 2^-3 * 2^-4 = 2^-7
    acc = one
    for _ in range(N): acc = mac(acc, a8, b8, 0, 'rn')
    runs = []
    for s in range(1, 31):
        l, acc2 = GaloisLFSR(seed=s), one
        for _ in range(N): acc2 = mac(acc2, a8, b8, l.word(), 'eager')
        runs.append(float(fp12_value(acc2)))
    m = sum(runs) / len(runs)
    print("  exact=33  RN ->", float(fp12_value(acc)), "  eager SR mean(30 seeds) ->", round(m, 2))
    assert fp12_value(acc) == 1 and 29 < m < 37

if __name__ == "__main__":
    for t in (test_lfsr, test_multiplier, test_rn, test_eager_vs_lazy, test_probability, test_stagnation):
        print(t.__name__); t()
    print("ALL PYTHON TESTS PASSED")
