import sys, os, random, torch
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reference_model"))
import sr_mac_ref as ref
import fp12_ops as T

def test_multiplier():
    a = torch.arange(256).repeat_interleave(256); b = torch.arange(256).repeat(256)
    got = T.fp8_mul(a, b).tolist()
    for i, (x, y) in enumerate(zip(a.tolist(), b.tolist())): assert got[i] == ref.fp8_mul(x, y), (x, y)
    print("  fp8_mul: all 65536 pairs bit-exact")

def test_adders(n=100000):
    rng = random.Random(11); A, B, Rw = [], [], []
    for _ in range(n):
        d = rng.choice([0, 0, 1, 1, 2, 3, 4, 6, 9, 14, 30, 61]); e = rng.randrange(1, 64)
        e2 = max(0, min(63, e - d))
        a = rng.randrange(2) << 11 | e << 5 | rng.randrange(32); b = rng.randrange(2) << 11 | e2 << 5 | rng.randrange(32)
        if rng.random() < .1: b = rng.choice([0, 0x800, 0xFE0, 0x7E0, 0x3E0])
        A.append(a); B.append(b); Rw.append(rng.randrange(1 << 18))
    At, Bt, Rt = (torch.tensor(v, dtype=torch.int64) for v in (A, B, Rw))
    for name, tf, rf in (('eager', T.add_eager, lambda a, b, r: ref.add_eager(a, b, r)),
                         ('lazy',  T.add_lazy,  lambda a, b, r: ref.add_lazy(a, b, r)),
                         ('rn',    T.add_rn,    lambda a, b, r: ref.add_rn(a, b))):
        got = tf(At, Bt, Rt).tolist()
        for i in range(n): assert got[i] == rf(A[i], B[i], Rw[i]), (name, hex(A[i]), hex(B[i]), got[i], rf(A[i], B[i], Rw[i]))
        print(f"  add_{name}: {n} vectors bit-exact vs reference_model")

def test_lfsr_stream():
    seeds = torch.tensor([[1, 5], [77, 262143]], dtype=torch.int64)
    st = T.LFSRStream((2, 2), 'cpu', seeds=seeds)
    refs = [[ref.GaloisLFSR(seed=int(seeds[i, j]), steps=18) for j in range(2)] for i in range(2)]
    for _ in range(50):
        w = st.next()
        for i in range(2):
            for j in range(2): assert int(w[i, j]) == refs[i][j].word()
    print("  LFSRStream (3-table jump) == scalar Galois LFSR, 50 words x 4 streams")

def test_gemm():
    torch.manual_seed(0)
    M, K, N = 3, 40, 4
    A8 = T.fp8_encode(torch.randn(M, K) * 2); B8 = T.fp8_encode(torch.randn(K, N))
    seeds = torch.randint(1, 1 << 18, (M, N), dtype=torch.int64)
    for mode in ('eager', 'lazy', 'rn'):
        got = T.fp12_gemm_codes(A8, B8, mode=mode, seeds=seeds)
        for i in range(M):
            for j in range(N):
                lf, acc = ref.GaloisLFSR(seed=int(seeds[i, j]), steps=18), 0
                for k in range(K): acc = ref.mac(acc, int(A8[i, k]), int(B8[k, j]), lf.word() if mode != 'rn' else 0, mode)
                assert int(got[i, j]) == acc, (mode, i, j)
    print("  GEMM (3x40x4) bit-exact vs scalar MAC loop, modes eager/lazy/rn")

def test_swamping_gemm():
    """the point of the paper: long dot product of small terms. FP32 truth vs RN vs eager SR."""
    K = 4096
    A8 = T.fp8_encode(torch.full((1, K), 2.0 ** -3)); B8 = T.fp8_encode(torch.full((K, 1), 2.0 ** -4))
    A8[0, 0] = T.fp8_encode(torch.tensor(1.0)); B8[0, 0] = T.fp8_encode(torch.tensor(1.0))    # start the sum at 1.0
    exact = 1 + (K - 1) * 2.0 ** -7
    rn = float(T.fp12_decode(T.fp12_gemm_codes(A8, B8, mode='rn'))[0, 0])
    sr = [float(T.fp12_decode(T.fp12_gemm_codes(A8, B8, mode='eager', seed=s))[0, 0]) for s in range(1, 21)]
    print(f"  K=4096 sum: exact={exact:.2f}  RN={rn:.2f}  eager SR mean(20 seeds)={sum(sr)/len(sr):.2f}")
    assert rn < 2 and abs(sum(sr) / len(sr) - exact) < 4

if __name__ == "__main__":
    for t in (test_multiplier, test_adders, test_lfsr_stream, test_gemm, test_swamping_gemm):
        print(t.__name__); t()
    print("ALL TORCH EMULATOR TESTS PASSED")
