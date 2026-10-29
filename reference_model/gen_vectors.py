"""Generates RTL test vectors from the golden model. Run from repo root: python3 reference_model/gen_vectors.py"""
import random, os
from sr_mac_ref import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vectors")
os.makedirs(OUT, exist_ok=True)
rng = random.Random(2024)
R = 18

def rnd_word():
    k = rng.random()
    if k < .08: return 0
    if k < .16: return (1 << R) - 1
    if k < .24: return 1 << rng.randrange(R)
    return rng.randrange(1 << R)

pairs = []
# directed corners: zero / subnormal-pattern / special / overflow / underflow / cancellation / ties
nz = [0x000, 0x800, 0x00F, 0x81F, 0x7E0, 0xFE0, 0x7E1, 0xFC0, 0x3E0, 0xBE0, 0x3E1, 0x020, 0x820, 0x021, 0x7DF, 0xFDF, 0x7FF, 0xFE0 | 0x1]
for a in nz:
    for b in nz: pairs.append((a, b))
pairs += [(0x7DF, 0x7DF), (0xFDF, 0xFDF), (0x020, 0xA20), (0x020, 0xA21), (0x021, 0xA20), (0x3E0, 0xBE0), (0x3E1, 0xBE0)]
# random with emphasis on every exponent difference
for _ in range(60000):
    d = rng.choice([0, 0, 1, 1, 2, 2, 3, 4, 5, 6, 7, 8, 10, 14, 20, 28, 40, 61])
    e = rng.randrange(1, 63)
    e2 = max(1, min(62, e - d))
    a = rng.randrange(2) << 11 | e << 5 | rng.randrange(32)
    b = rng.randrange(2) << 11 | e2 << 5 | rng.randrange(32)
    if rng.random() < .5: a, b = b, a
    pairs.append((a, b))

with open(os.path.join(OUT, "vec.hex"), "w") as f:
    for a, b in pairs:
        for _ in range(3):
            w = rnd_word()
            f.write(f"{a:03x}{b:03x}{w:05x}{add_rn(a,b):03x}{add_lazy(a,b,w,R):03x}{add_eager(a,b,w,R):03x}\n")
n_add = 3 * len(pairs)

# MAC sequences: each mode has its own LFSR (seed 1, 18 steps/word), accumulator starts at +0
N = 4000
A = [rng.randrange(2) << 7 | rng.randrange(8, 24) << 2 | rng.randrange(4) for _ in range(N)]
B = [rng.randrange(2) << 7 | rng.randrange(8, 24) << 2 | rng.randrange(4) for _ in range(N)]
acc = {'rn': 0, 'lazy': 0, 'eager': 0}
lf = {m: GaloisLFSR(seed=1, steps=18) for m in acc}
with open(os.path.join(OUT, "mac_vec.hex"), "w") as f:
    for a, b in zip(A, B):
        for m in acc:
            w = lf[m].word() if m != 'rn' else 0
            acc[m] = mac(acc[m], a, b, w, m, R)
        f.write(f"{a:02x}{b:02x}{acc['rn']:03x}{acc['lazy']:03x}{acc['eager']:03x}\n")
print(f"vec.hex: {n_add} adder vectors   mac_vec.hex: {N} MAC steps")


# ---- vectors for other random-bit widths (paper sweeps r = 9, 12, 14, 16, 18)
for rr in (9, 12, 14, 16):
    rg = random.Random(100 + rr)
    with open(os.path.join(OUT, f"vec_r{rr}.hex"), "w") as f:
        for _ in range(30000):
            d = rg.choice([0, 0, 1, 1, 2, 3, 4, 6, 8, 12, 30]); e = rg.randrange(1, 63); e2 = max(1, min(62, e - d))
            a = rg.randrange(2) << 11 | e << 5 | rg.randrange(32); b = rg.randrange(2) << 11 | e2 << 5 | rg.randrange(32)
            w = rg.randrange(1 << rr)
            f.write(f"{a:03x}{b:03x}{w:05x}{add_rn(a,b):03x}{add_lazy(a,b,w,rr):03x}{add_eager(a,b,w,rr):03x}\n")
print("vec_r{9,12,14,16}.hex written")
