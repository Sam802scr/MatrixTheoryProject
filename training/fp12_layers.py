"""Autograd + layers that run EVERY GEMM (forward and both backward GEMMs) on the emulated MAC.
The number of random bits r can be chosen per GEMM through MACConfig.policy (see policies.py): phase = 'fwd' | 'dgrad' | 'wgrad'."""
import torch, torch.nn as nn, torch.nn.functional as F
import fp12_ops as T

class MACConfig:
    mode = 'eager'      # 'eager' | 'lazy' | 'rn' (all E6M5)   |  'fp16' | 'bf16' (RN accumulators of that width)
    r = 18              # default number of random bits (used when no policy is set)
    stream = 'lfsr'     # 'lfsr' (hardware-like) | 'ideal' (torch PRNG)
    seed = 1
    policy = None       # callable (phase, K) -> r
    count = True        # set False during evaluation so that stats only describe training GEMMs
    _calls = 0
    stats = {}          # phase -> [MAC count, sum of r over MACs, number of GEMM calls]   (for hardware-complexity accounting)
    hist = {}           # (phase, r) -> MAC count
    @classmethod
    def kw(cls, phase, K, M, N):
        cls._calls += 1                                   # different random streams for every GEMM call
        r = int(cls.policy(phase, K)) if cls.policy is not None else cls.r
        if cls.count:
            s = cls.stats.setdefault(phase, [0, 0.0, 0]); s[0] += M * N * K; s[1] += M * N * K * r; s[2] += 1
            cls.hist[(phase, r)] = cls.hist.get((phase, r), 0) + M * N * K
        return dict(mode=cls.mode, r=r, stream=cls.stream, seed=cls.seed + cls._calls)

def _gemm(A, B, phase):
    """float32 (M,K)@(K,N) on the emulated MAC."""
    A, B = A.float().contiguous(), B.float().contiguous()
    (M, K), N = A.shape, B.shape[1]
    return T.fp12_gemm(A, B, **MACConfig.kw(phase, K, M, N))

class FP12MatMul(torch.autograd.Function):
    @staticmethod
    def forward(ctx, A, B, wgrad_is_A):
        ctx.save_for_backward(A, B); ctx.wgrad_is_A = wgrad_is_A
        return _gemm(A, B, 'fwd')
    @staticmethod
    def backward(ctx, G):
        A, B = ctx.saved_tensors
        pA, pB = ('wgrad', 'dgrad') if ctx.wgrad_is_A else ('dgrad', 'wgrad')
        return _gemm(G, B.t(), pA), _gemm(A.t(), G, pB), None        # dA = G B^T , dB = A^T G  (both on the MAC)

class FP12Linear(nn.Linear):
    def forward(self, x):
        y = FP12MatMul.apply(x, self.weight.t(), False)              # weight is operand B: dB is the weight gradient
        return y + self.bias if self.bias is not None else y

class FP12Conv2d(nn.Conv2d):
    def forward(self, x):
        Nb, C, H, W = x.shape; kh, kw = self.kernel_size
        Ho = (H + 2 * self.padding[0] - kh) // self.stride[0] + 1
        Wo = (W + 2 * self.padding[1] - kw) // self.stride[1] + 1
        cols = F.unfold(x, self.kernel_size, padding=self.padding, stride=self.stride)      # (N, C*kh*kw, L)
        cols = cols.permute(1, 0, 2).reshape(C * kh * kw, Nb * Ho * Wo)
        out = FP12MatMul.apply(self.weight.view(self.out_channels, -1), cols, True)         # weight is operand A: dA is the weight gradient
        out = out.view(self.out_channels, Nb, Ho * Wo).permute(1, 0, 2).reshape(Nb, self.out_channels, Ho, Wo)
        return out + self.bias.view(1, -1, 1, 1) if self.bias is not None else out
