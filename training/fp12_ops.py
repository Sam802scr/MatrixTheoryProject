"""
Bit-accurate PyTorch emulation of the paper's MAC: FP8 E5M2 x FP8 E5M2 (exact) -> FP12 E6M5 accumulate with
EAGER stochastic rounding (or lazy SR / RN).  A vectorised port of reference_model/sr_mac_ref.py, verified
bit-for-bit against it (training/test_fp12_ops.py).  Works on CPU and CUDA tensors (int64 ops).
"""
import torch

P = 6
MAXFIN = (62 << 5) | 31

# ------------------------------------------------------------------ FP8 quantisation (float -> E5M2 code)
def fp8_encode(x: torch.Tensor) -> torch.Tensor:
    """float tensor -> uint8-valued int64 codes. RN-even to E5M2; subnormals flushed to 0; overflow saturates."""
    c = x.to(torch.float8_e5m2).view(torch.uint8).to(torch.int64)
    e = (c >> 2) & 31
    c = torch.where(e == 0, c & 0x80, c)                              # flush subnormal (keeps sign bit; -0 -> see below)
    c = torch.where(e == 31, (c & 0x80) | 0x7B, c)                    # inf/nan -> max finite (0x7B = 1.75*2^15)
    return torch.where((c & 0x7F) == 0, torch.zeros_like(c), c)       # +0 only

def fp8_decode(c: torch.Tensor) -> torch.Tensor:
    return c.to(torch.uint8).view(torch.float8_e5m2).to(torch.float32)

# ------------------------------------------------------------------ FP12 decode
def fp12_decode(c: torch.Tensor) -> torch.Tensor:
    s = (c >> 11) & 1
    e = (c >> 5) & 63
    m = 32 + (c & 31)
    v = torch.ldexp(m.to(torch.float32) / 32.0, (e - 31).to(torch.int32))
    v = torch.where(e == 0, torch.zeros_like(v), v)
    return torch.where(s == 1, -v, v)

# ------------------------------------------------------------------ exact multiplier
def fp8_mul(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    sa, sb = a >> 7, b >> 7
    ea, eb = (a >> 2) & 31, (b >> 2) & 31
    s = sa ^ sb
    prod = (4 | (a & 3)) * (4 | (b & 3))
    top = (prod >> 5) & 1
    m = torch.where(top == 1, prod, prod << 1)
    E = ea + eb + 1 + top
    res = (s << 11) | (E << 5) | (m & 31)
    res = torch.where((ea == 0) | (eb == 0), torch.zeros_like(res), res)
    return torch.where((ea == 31) | (eb == 31), (s << 11) | (63 << 5), res)

# ------------------------------------------------------------------ adders
def _front(a, b):
    ea, eb = (a >> 5) & 63, (b >> 5) & 63
    swap = (a & 0x7FF) < (b & 0x7FF)
    x, y = torch.where(swap, b, a), torch.where(swap, a, b)
    # special-case result (None where the normal datapath applies)
    spec = torch.where(ea == 63, a, torch.where(eb == 63, b, torch.where((ea == 0) & (eb == 0), torch.zeros_like(a),
           torch.where(ea == 0, b, torch.where(eb == 0, a, torch.full_like(a, -1))))))
    return x, y, spec

def _pack(sx, ez, mz):
    ovf = mz == (1 << P)
    mz = torch.where(ovf, torch.full_like(mz, 32), mz)
    ez = ez + ovf.to(ez.dtype)
    res = (sx << 11) | (ez << 5) | (mz & 31)
    res = torch.where(ez > 62, (sx << 11) | MAXFIN, res)
    return torch.where((ez < 1) | (mz == 0), torch.zeros_like(res), res)

def add_eager(a, b, rand, r=18):
    x, y, spec = _front(a, b)
    sx, ex, mx = x >> 11, (x >> 5) & 63, 32 | (x & 31)
    sy, ey, my = y >> 11, (y >> 5) & 63, 32 | (y & 31)
    d = (ex - ey).clamp(max=40); sub = sx != sy
    mlo, m3, m4 = (1 << (r - 2)) - 1, (1 << (r - 3)) - 1, (1 << (r - 4)) - 1
    Ys = (my << (r - 1)) >> d
    Ytop, Ylow = Ys >> (r - 2), Ys & mlo
    Xtop = mx << 1
    Llow = torch.where(sub, (-Ylow) & mlo, Ylow)
    borrow = (sub & (Ylow != 0)).to(torch.int64)
    Ttop = torch.where(sub, Xtop - Ytop - borrow, Xtop + Ytop)
    zero_res = (Ttop == 0) & (Llow == 0)
    R12, R3 = rand >> (r - 2), rand & mlo
    S1 = (Llow + R3) >> (r - 2)
    S2 = ((Llow & m3) + (R3 & m3)) >> (r - 3)
    S3 = ((Llow & m4) + (R3 & m4)) >> (r - 4)
    G2 = ((Llow >> (r - 4)) & 1) | (((Llow >> (r - 3)) & 1) << 1)
    bl = torch.zeros_like(Ttop)
    for i in range(P + 2): bl = torch.where(((Ttop >> i) & 1) == 1, torch.full_like(bl, i + 1), bl)
    j = (P + 2) - bl
    V = (Ttop << 2) | G2
    Vn = (V << j) & ((1 << (P + 4)) - 1)
    sig, Rb, Sb = Vn >> 4, (Vn >> 3) & 1, (Vn >> 2) & 1
    cin = torch.where(j == 0, S1, torch.where(j == 1, S2, S3))
    up = (((Rb << 1) | Sb) + R12 + cin) >> 2
    res = _pack(sx, ex + 1 - j, sig + up)
    res = torch.where(zero_res, torch.zeros_like(res), res)
    return torch.where(spec >= 0, spec, res)

def add_lazy(a, b, rand, r=18):
    x, y, spec = _front(a, b)
    sx, ex, mx = x >> 11, (x >> 5) & 63, 32 | (x & 31)
    sy, ey, my = y >> 11, (y >> 5) & 63, 32 | (y & 31)
    d = (ex - ey).clamp(max=40)
    Xs, Ys = mx << (r - 1), (my << (r - 1)) >> d
    T = torch.where(sx == sy, Xs + Ys, Xs - Ys)
    bl = torch.zeros_like(T)
    for i in range(P + r): bl = torch.where(((T >> i) & 1) == 1, torch.full_like(bl, i + 1), bl)
    Tn = T << (P + r - bl).clamp(min=0)
    E = Tn & ((1 << r) - 1)
    mz = (Tn >> r) + ((E + rand) >> r)
    res = _pack(sx, ex + (bl - (P + r - 1)), mz)
    res = torch.where(T == 0, torch.zeros_like(res), res)
    return torch.where(spec >= 0, spec, res)

def add_rn(a, b, rand=None, r=18):
    x, y, spec = _front(a, b)
    sx, ex, mx = x >> 11, (x >> 5) & 63, 32 | (x & 31)
    sy, ey, my = y >> 11, (y >> 5) & 63, 32 | (y & 31)
    d = (ex - ey).clamp(max=40)
    Yf = my << 3
    Ys = (Yf >> d) | ((Yf & ((1 << d) - 1)) != 0).to(torch.int64)
    T = torch.where(sx == sy, (mx << 3) + Ys, (mx << 3) - Ys)
    bl = torch.zeros_like(T)
    for i in range(10): bl = torch.where(((T >> i) & 1) == 1, torch.full_like(bl, i + 1), bl)
    sh = (bl - P).clamp(min=0)
    top, rem = T >> sh, T & ((1 << sh) - 1)
    half = torch.where(sh > 0, 1 << (sh - 1).clamp(min=0), torch.zeros_like(sh))
    inc = (sh > 0) & ((rem > half) | ((rem == half) & ((top & 1) == 1)))
    top = torch.where(sh > 0, top + inc.to(top.dtype), T << (P - bl).clamp(min=0))
    res = _pack(sx, ex + (bl - 9), top)
    res = torch.where(T == 0, torch.zeros_like(res), res)
    return torch.where(spec >= 0, spec, res)

ADDERS = {'eager': add_eager, 'lazy': add_lazy, 'rn': add_rn}

# ------------------------------------------------------------------ vectorised Galois LFSR (18 steps per word)
class LFSRStream:
    """One independent x^18+x^11+1 Galois LFSR per output element; 18 steps per MAC via 3 lookup tables."""
    MASK = (1 << 17) | (1 << 10)
    def __init__(self, shape, device, seed=1, steps=18, seeds=None):
        def adv(s):
            for _ in range(steps): s = (s >> 1) ^ self.MASK if s & 1 else s >> 1
            return s
        # the step map is linear over GF(2): state' = XOR of adv(basis_i) for set bits i
        cols = [adv(1 << i) for i in range(18)]
        tabs = []
        for k in range(3):
            t = []
            for v in range(64):
                acc = 0
                for b in range(6):
                    if (v >> b) & 1: acc ^= cols[6 * k + b]
                t.append(acc)
            tabs.append(torch.tensor(t, dtype=torch.int64, device=device))
        self.t0, self.t1, self.t2 = tabs
        if seeds is None:
            g = torch.Generator(device='cpu').manual_seed(seed)
            seeds = torch.randint(1, 1 << 18, shape, generator=g, dtype=torch.int64)
        self.state = seeds.to(device)
    def next(self):
        s = self.state
        self.state = self.t0[s & 63] ^ self.t1[(s >> 6) & 63] ^ self.t2[(s >> 12) & 63]
        return self.state

class IdealStream:
    """Uniform r-bit words from torch's PRNG (an ideal random source, instead of the LFSR)."""
    def __init__(self, shape, device, seed=1, r=18):
        self.shape, self.device, self.r = shape, device, r
        self.g = torch.Generator(device=device).manual_seed(seed)
    def next(self):
        return torch.randint(0, 1 << self.r, self.shape, generator=self.g, device=self.device, dtype=torch.int64)

# ------------------------------------------------------------------ GEMM
def _cuda_ok():
    try:
        from numba import cuda
        return cuda.is_available()
    except Exception:
        return False

def fp12_gemm_codes(A8, B8, mode='eager', stream='lfsr', seed=1, r=18, seeds=None, backend='auto'):
    """A8:(M,K) B8:(K,N) FP8 codes (int64) -> FP12 codes (M,N). Sequential accumulation along K, acc starts at +0.
    backend: 'torch' (portable, slow) | 'cuda' (fused Numba kernel, LFSR randomness only) | 'auto' (cuda if tensors are on a GPU)."""
    M, K = A8.shape; N = B8.shape[1]; dev = A8.device
    if backend == 'auto':
        backend = 'cuda' if (A8.is_cuda and stream == 'lfsr' and _cuda_ok()) else 'torch'
    if backend == 'cuda':
        if seeds is None:
            g = torch.Generator().manual_seed(seed)
            seeds = torch.randint(1, 1 << 18, (M, N), generator=g, dtype=torch.int64)
        import fp12_cuda
        return fp12_cuda.gemm_codes(A8, B8, mode, seeds.to(dev), r)
    add = ADDERS[mode]
    st = LFSRStream((M, N), dev, seed=seed, seeds=seeds) if stream == 'lfsr' else IdealStream((M, N), dev, seed, r)
    acc = torch.zeros(M, N, dtype=torch.int64, device=dev)
    for k in range(K):
        p = fp8_mul(A8[:, k:k + 1], B8[k:k + 1, :])
        acc = add(acc, p, st.next() if mode != 'rn' else None, r)
    return acc

def fp12_gemm(A, B, **kw):
    """float32 (M,K)x(K,N) -> float32 (M,N): quantise to FP8, emulated MAC, decode."""
    return fp12_decode(fp12_gemm_codes(fp8_encode(A), fp8_encode(B), **kw))


# ------------------------------------------------------------------ baselines: FP16 (E5M10) / BF16 (E8M7) accumulators
def gemm_float_acc(A8, B8, dtype):
    """Sequential MAC with an FP16/BF16 accumulator (round-to-nearest-even after every add, subnormals supported):
    FP8 inputs, exact product (held in fp32), sum rounded to `dtype`.  Software baseline for the paper's RN FP16/BF16 rows
    (fp32 sum then rounding = double rounding in rare cases; not bit-exact with a hardware FP16 adder)."""
    a, b = fp8_decode(A8), fp8_decode(B8)
    acc = torch.zeros(A8.shape[0], B8.shape[1], dtype=dtype, device=A8.device)
    for k in range(A8.shape[1]):
        acc = (acc.float() + a[:, k:k + 1] * b[k:k + 1, :]).to(dtype)
    return acc.float()
