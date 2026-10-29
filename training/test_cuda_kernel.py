"""Run with the CUDA *simulator* (no GPU needed):   set NUMBA_ENABLE_CUDASIM=1  then  python test_cuda_kernel.py
On a machine with a real GPU just run it without the variable."""
import os, sys, random
import numpy as np, torch
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reference_model"))
import sr_mac_ref as ref
import fp12_ops as T
import fp12_cuda as C

def test_adders(n=3000):
    rng = random.Random(5); A, B, Rw = [], [], []
    for _ in range(n):
        d = rng.choice([0, 1, 2, 3, 6, 9, 20, 50]); e = rng.randrange(1, 64); e2 = max(0, min(63, e - d))
        A.append(rng.randrange(2) << 11 | e << 5 | rng.randrange(32)); B.append(rng.randrange(2) << 11 | e2 << 5 | rng.randrange(32))
        if rng.random() < .1: B[-1] = rng.choice([0, 0x800, 0xFE0, 0x7E0])
        Rw.append(rng.randrange(1 << 18))
    a, b, rd = (np.array(v, dtype=np.int32) for v in (A, B, Rw))
    for name, mode, f in (('eager', 0, lambda x, y, r_: ref.add_eager(x, y, r_)), ('lazy', 1, lambda x, y, r_: ref.add_lazy(x, y, r_)),
                          ('rn', 2, lambda x, y, r_: ref.add_rn(x, y))):
        out = np.zeros(n, dtype=np.int32)
        C.add_kernel[(n + 127) // 128, 128](a, b, rd, out, mode, 18)
        for i in range(n): assert int(out[i]) == f(A[i], B[i], Rw[i]), (name, hex(A[i]), hex(B[i]), int(out[i]), f(A[i], B[i], Rw[i]))
        print(f"  CUDA add_{name}: {n} vectors bit-exact vs reference_model")

def test_gemm():
    torch.manual_seed(0)
    M, K, N = 3, 40, 4
    A8 = T.fp8_encode(torch.randn(M, K) * 2); B8 = T.fp8_encode(torch.randn(K, N))
    seeds = torch.randint(1, 1 << 18, (M, N), dtype=torch.int64)
    for mode in ('eager', 'lazy', 'rn'):
        got = C.gemm_codes(A8.numpy(), B8.numpy(), mode, seeds.numpy())
        want = T.fp12_gemm_codes(A8, B8, mode=mode, seeds=seeds).numpy()
        assert (got == want).all(), mode
        print(f"  CUDA GEMM {mode}: bit-exact vs torch emulator (and therefore vs scalar MAC loop)")

if __name__ == "__main__":
    test_adders(); test_gemm(); print("CUDA KERNEL TESTS PASSED")
