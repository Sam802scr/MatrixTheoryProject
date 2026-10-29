"""
Replicates the paper's verification of the eager adder (Sec. III-B): 10000 input pairs, 1000 random words each, and check that
the measured probability of rounding UP equals the stochastic-rounding definition q = (x - floor)/(ceil - floor).
Also checks every result is one of the two neighbouring FP12 values.  Usage: python paper_probability_test.py [--r 18] [--mode eager]
"""
import argparse, math, torch
import fp12_ops as T

def binom_p(k, n, q):
    """two-sided exact binomial tail probability of seeing k round-ups in n draws when the true probability is q"""
    lp = [math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1) + (i * math.log(q) if i else 0) + ((n - i) * math.log1p(-q) if n - i else 0) for i in range(n + 1)]
    pmf = [math.exp(x) for x in lp]
    return min(1.0, 2 * min(sum(pmf[:k + 1]), sum(pmf[k:])))

ap = argparse.ArgumentParser(); ap.add_argument('--r', type=int, default=18); ap.add_argument('--mode', default='eager')
ap.add_argument('--pairs', type=int, default=10000); ap.add_argument('--words', type=int, default=1000); a = ap.parse_args()
g = torch.Generator().manual_seed(7)
add = T.ADDERS[a.mode]
worst_z, bad_nb, bad_stat, tested = 1.0, 0, 0, 0
CH = 500
for c0 in range(0, a.pairs, CH):
    n = CH
    d = torch.tensor([0, 0, 1, 1, 2, 3, 4, 6, 8, 12, 20, 30, 40])[torch.randint(0, 13, (n,), generator=g)]
    e = torch.randint(12, 50, (n,), generator=g)
    e2 = (e - d).clamp(min=12)
    A = (torch.randint(0, 2, (n,), generator=g) << 11) | (e << 5) | torch.randint(0, 32, (n,), generator=g)
    B = (torch.randint(0, 2, (n,), generator=g) << 11) | (e2 << 5) | torch.randint(0, 32, (n,), generator=g)
    S = T.fp12_decode(A).double() + T.fp12_decode(B).double()                # exact in float64 (span <= 46 bits)
    nz = S != 0
    m = S.abs(); f, k = torch.frexp(m); ulp = torch.ldexp(torch.ones_like(m), (k - 1 - 5).to(torch.int32))
    lo = torch.floor(m / ulp) * ulp; q = (m - lo) / ulp
    R = torch.randint(0, 1 << a.r, (n, a.words), generator=g, dtype=torch.int64)
    res = add(A[:, None].expand(-1, a.words), B[:, None].expand(-1, a.words), R, a.r)
    v = T.fp12_decode(res).double().abs()
    ok_nb = ((v - lo[:, None]).abs() < 1e-300) | ((v - (lo + ulp)[:, None]).abs() < 1e-300 * 1) | ((v - (lo + ulp)[:, None]).abs() <= ulp[:, None] * 1e-9)
    ok_nb = ok_nb | ~nz[:, None]
    bad_nb += int((~ok_nb).sum())
    up = ((v - lo[:, None]).abs() > ulp[:, None] * 0.5).double().mean(1)       # fraction rounded up
    sd = torch.sqrt((q * (1 - q)).clamp(min=1e-12) / a.words)
    sel = nz & (q > 0) & (q < 1)
    zall = (up - q).abs() / sd
    tested += int(sel.sum())
    for i in torch.nonzero(sel & (zall > 3.0)).flatten().tolist():          # only suspicious pairs need the exact test
        pv = binom_p(int(round(float(up[i]) * a.words)), a.words, float(q[i]))
        worst_z = min(worst_z, pv)
        if pv < 1e-6: bad_stat += 1
print(f"mode={a.mode} r={a.r}: {tested} pairs with inexact sums x {a.words} random words")
print(f"  results outside the two neighbouring FP12 values : {bad_nb}")
print(f"  pairs whose P(round up) is inconsistent with q (exact binomial p < 1e-6): {bad_stat}   (smallest p-value seen = {worst_z:.2e})")
print("PASS" if bad_nb == 0 and bad_stat == 0 else "FAIL")
