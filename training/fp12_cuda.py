"""
Fused CUDA kernel (Numba) for the emulated FP8 x FP8 -> FP12 MAC: one GPU thread owns one output element and runs the
whole K-long accumulation chain in registers (multiplier -> eager/lazy/RN adder -> LFSR step), like the paper's kernels.
Same arithmetic as fp12_ops.py / reference_model/sr_mac_ref.py; checked bit-exact by test_cuda_kernel.py.
Needs an NVIDIA GPU + CUDA toolkit (pip install numba-cuda[cu12]  or  conda install numba cudatoolkit).
Mode ints: 0 = eager SR, 1 = lazy SR, 2 = RN.
"""
import numpy as np
from numba import cuda

MODES = {'eager': 0, 'lazy': 1, 'rn': 2}
P = 6
MASK = (1 << 17) | (1 << 10)          # x^18 + x^11 + 1 (Galois)

@cuda.jit(device=True)
def _bitlen(x, n):
    bl = 0
    for i in range(n):
        if (x >> i) & 1:
            bl = i + 1
    return bl

@cuda.jit(device=True)
def _pack(sx, ez, mz):
    if mz == 64:
        mz = 32
        ez += 1
    if ez < 1 or mz == 0:
        return 0
    if ez > 62:
        return (sx << 11) | 0x7DF
    return (sx << 11) | (ez << 5) | (mz & 31)

@cuda.jit(device=True)
def _lfsr18(s):                        # 18 Galois steps (one random word per MAC)
    for _ in range(18):
        if s & 1:
            s = (s >> 1) ^ MASK
        else:
            s = s >> 1
    return s

@cuda.jit(device=True)
def _mul(a, b):
    sa = a >> 7
    sb = b >> 7
    ea = (a >> 2) & 31
    eb = (b >> 2) & 31
    s = sa ^ sb
    if ea == 31 or eb == 31:
        return (s << 11) | (63 << 5)
    if ea == 0 or eb == 0:
        return 0
    prod = (4 | (a & 3)) * (4 | (b & 3))
    top = (prod >> 5) & 1
    m = prod if top == 1 else prod << 1
    return (s << 11) | ((ea + eb + 1 + top) << 5) | (m & 31)

@cuda.jit(device=True)
def _add(a, b, rand, mode, r):
    ea = (a >> 5) & 63
    eb = (b >> 5) & 63
    if ea == 63:
        return a
    if eb == 63:
        return b
    if ea == 0 and eb == 0:
        return 0
    if ea == 0:
        return b
    if eb == 0:
        return a
    if (a & 0x7FF) < (b & 0x7FF):
        x = b
        y = a
    else:
        x = a
        y = b
    sx = x >> 11
    ex = (x >> 5) & 63
    mx = 32 | (x & 31)
    sy = y >> 11
    ey = (y >> 5) & 63
    my = 32 | (y & 31)
    d = ex - ey
    if d > 40:
        d = 40
    sub = sx != sy

    if mode == 2:                                           # ---------- RN (nearest-even)
        Yf = my << 3
        Ys = Yf >> d
        if (Yf & ((1 << d) - 1)) != 0:
            Ys = Ys | 1
        T = (mx << 3) - Ys if sub else (mx << 3) + Ys
        if T == 0:
            return 0
        bl = _bitlen(T, 10)
        sh = bl - P
        if sh > 0:
            top = T >> sh
            rem = T & ((1 << sh) - 1)
            half = 1 << (sh - 1)
            if rem > half or (rem == half and (top & 1) == 1):
                top += 1
        else:
            top = T << (P - bl)
        return _pack(sx, ex + (bl - 9), top)

    if mode == 1:                                           # ---------- lazy SR
        Xs = mx << (r - 1)
        Ys = (my << (r - 1)) >> d
        T = Xs - Ys if sub else Xs + Ys
        if T == 0:
            return 0
        bl = _bitlen(T, P + r)
        Tn = T << (P + r - bl)
        E = Tn & ((1 << r) - 1)
        mz = (Tn >> r) + ((E + rand) >> r)
        return _pack(sx, ex + (bl - (P + r - 1)), mz)

    # ------------------------------------------------------ eager SR (paper Fig. 3b / 4)
    mlo = (1 << (r - 2)) - 1
    m3 = (1 << (r - 3)) - 1
    m4 = (1 << (r - 4)) - 1
    Ys = (my << (r - 1)) >> d
    Ytop = Ys >> (r - 2)
    Ylow = Ys & mlo
    Xtop = mx << 1
    if sub:
        Llow = (-Ylow) & mlo
        borrow = 1 if Ylow != 0 else 0
        Ttop = Xtop - Ytop - borrow
    else:
        Llow = Ylow
        Ttop = Xtop + Ytop
    if Ttop == 0 and Llow == 0:
        return 0
    R12 = rand >> (r - 2)
    R3 = rand & mlo
    S1 = (Llow + R3) >> (r - 2)
    S2 = ((Llow & m3) + (R3 & m3)) >> (r - 3)
    S3 = ((Llow & m4) + (R3 & m4)) >> (r - 4)
    G2 = ((Llow >> (r - 4)) & 1) | (((Llow >> (r - 3)) & 1) << 1)
    j = (P + 2) - _bitlen(Ttop, P + 2)
    V = (Ttop << 2) | G2
    Vn = (V << j) & ((1 << (P + 4)) - 1)
    sig = Vn >> 4
    Rb = (Vn >> 3) & 1
    Sb = (Vn >> 2) & 1
    if j == 0:
        cin = S1
    elif j == 1:
        cin = S2
    else:
        cin = S3
    up = (((Rb << 1) | Sb) + R12 + cin) >> 2
    return _pack(sx, ex + 1 - j, sig + up)

@cuda.jit
def gemm_kernel(A, B, out, seeds, M, N, K, mode, r):
    i, j = cuda.grid(2)
    if i < M and j < N:
        st = np.int64(seeds[i, j])
        acc = np.int64(0)
        for k in range(K):
            p = _mul(np.int64(A[i, k]), np.int64(B[k, j]))
            if mode != 2:
                st = _lfsr18(st)
            acc = _add(acc, p, st, mode, r)
        out[i, j] = acc

@cuda.jit
def add_kernel(a, b, rand, out, mode, r):            # test helper: element-wise adder
    i = cuda.grid(1)
    if i < a.shape[0]:
        out[i] = _add(np.int64(a[i]), np.int64(b[i]), np.int64(rand[i]), mode, r)

def gemm_codes(A8, B8, mode='eager', seeds=None, r=18):
    """numpy/torch-cuda int tensors -> FP12 codes. Accepts numpy arrays (simulator) or torch CUDA tensors."""
    is_torch = hasattr(A8, 'is_cuda')
    if is_torch:
        import torch
        M, K = A8.shape; N = B8.shape[1]
        out = torch.zeros(M, N, dtype=torch.int32, device=A8.device)
        a, b, s = A8.to(torch.int32).contiguous(), B8.to(torch.int32).contiguous(), seeds.to(torch.int32).contiguous()
        args = (cuda.as_cuda_array(a), cuda.as_cuda_array(b), cuda.as_cuda_array(out), cuda.as_cuda_array(s))
    else:
        M, K = A8.shape; N = B8.shape[1]
        out = np.zeros((M, N), dtype=np.int32)
        args = (A8.astype(np.int32), B8.astype(np.int32), out, seeds.astype(np.int32))
    tpb = (8, 32)
    blocks = ((M + tpb[0] - 1) // tpb[0], (N + tpb[1] - 1) // tpb[1])
    gemm_kernel[blocks, tpb](*args, M, N, K, MODES[mode], r)
    if is_torch:
        cuda.synchronize(); return out.to(torch.int64)
    return args[2].astype(np.int64)
