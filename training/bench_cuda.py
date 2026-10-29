"""Measures the fused CUDA kernel on a real GPU and projects training time.  Run on a GPU machine:  python bench_cuda.py"""
import sys, time, torch
import fp12_ops as T, fp12_cuda as C
if not torch.cuda.is_available():
    sys.exit("No CUDA GPU visible to PyTorch (torch.cuda.is_available() is False).")
print("GPU:", torch.cuda.get_device_name(0))
dev = 'cuda'
def run(M, K, N, mode='eager'):
    A = T.fp8_encode(torch.randn(M, K, device=dev)); B = T.fp8_encode(torch.randn(K, N, device=dev))
    seeds = torch.randint(1, 1 << 18, (M, N), device=dev, dtype=torch.int64)
    C.gemm_codes(A, B, mode, seeds); torch.cuda.synchronize()               # warm-up / JIT compile
    t = time.time(); C.gemm_codes(A, B, mode, seeds); torch.cuda.synchronize(); dt = time.time() - t
    return dt, M * K * N / dt / 1e9
# 1) correctness on the real GPU: kernel vs the portable torch emulator (bit-exact)
A = T.fp8_encode(torch.randn(8, 50, device=dev)); B = T.fp8_encode(torch.randn(50, 9, device=dev)); s = torch.randint(1, 1 << 18, (8, 9), device=dev, dtype=torch.int64)
for mode in ('eager', 'lazy', 'rn'):
    ok = torch.equal(C.gemm_codes(A, B, mode, s), T.fp12_gemm_codes(A.cpu(), B.cpu(), mode=mode, seeds=s.cpu(), backend='torch').to(dev))
    print(f"real-GPU kernel vs torch emulator, {mode}: {'BIT-EXACT' if ok else 'MISMATCH'}")
# 2) throughput on ResNet-20-like GEMM shapes at batch 128 (conv1, a mid layer, last stage)
tot = []
for name, (M, K, N) in {'conv1': (16, 27, 128 * 1024), 'stage2 3x3': (32, 288, 128 * 256), 'stage3 3x3': (64, 576, 128 * 64)}.items():
    dt, gmacs = run(M, K, N); tot.append(gmacs); print(f"{name:11s} M={M} K={K} N={N}: {dt*1e3:8.1f} ms  {gmacs:7.2f} GMAC/s")
g = sum(tot) / len(tot)
macs_epoch = 50000 * 41e6 * 3                     # ResNet-20 ~41M MACs/image forward, x3 for forward+backward GEMMs
print(f"\nprojected ResNet-20 epoch  : {macs_epoch / (g * 1e9) / 60:.1f} min  (at {g:.2f} GMAC/s)")
print(f"projected 165-epoch run    : {165 * macs_epoch / (g * 1e9) / 3600:.1f} hours")
