"""Autograd + layers that run EVERY GEMM (forward and both backward GEMMs) on the emulated FP8 x FP8 -> FP12 SR MAC."""
import torch, torch.nn as nn, torch.nn.functional as F
import fp12_ops as T

class MACConfig:
    mode = 'eager'      # 'eager' | 'lazy' | 'rn' (all E6M5)   |  'fp16' | 'bf16' (RN baselines with a 16-bit accumulator)
    r = 18
    stream = 'lfsr'     # 'lfsr' (hardware-like) | 'ideal' (torch PRNG)
    seed = 1
    _calls = 0
    @classmethod
    def kw(cls):
        cls._calls += 1                                   # different random streams for every GEMM call
        return dict(mode=cls.mode, r=cls.r, stream=cls.stream, seed=cls.seed + cls._calls)

def _gemm(A, B):
    """float32 (M,K)@(K,N) on the emulated MAC."""
    if MACConfig.mode in ('fp16', 'bf16'):
        dt = torch.float16 if MACConfig.mode == 'fp16' else torch.bfloat16
        return T.gemm_float_acc(T.fp8_encode(A.float()), T.fp8_encode(B.float()), dt)
    return T.fp12_gemm(A.float().contiguous(), B.float().contiguous(), **MACConfig.kw())

class FP12MatMul(torch.autograd.Function):
    @staticmethod
    def forward(ctx, A, B):
        ctx.save_for_backward(A, B)
        return _gemm(A, B)
    @staticmethod
    def backward(ctx, G):
        A, B = ctx.saved_tensors
        return _gemm(G, B.t()), _gemm(A.t(), G)           # dA = G B^T , dB = A^T G  (both on the MAC)

class FP12Linear(nn.Linear):
    def forward(self, x):
        y = FP12MatMul.apply(x, self.weight.t())
        return y + self.bias if self.bias is not None else y

class FP12Conv2d(nn.Conv2d):
    def forward(self, x):
        Nb, C, H, W = x.shape; kh, kw = self.kernel_size
        Ho = (H + 2 * self.padding[0] - kh) // self.stride[0] + 1
        Wo = (W + 2 * self.padding[1] - kw) // self.stride[1] + 1
        cols = F.unfold(x, self.kernel_size, padding=self.padding, stride=self.stride)      # (N, C*kh*kw, L)
        cols = cols.permute(1, 0, 2).reshape(C * kh * kw, Nb * Ho * Wo)
        out = FP12MatMul.apply(self.weight.view(self.out_channels, -1), cols)               # (Cout, N*L)
        out = out.view(self.out_channels, Nb, Ho * Wo).permute(1, 0, 2).reshape(Nb, self.out_channels, Ho, Wo)
        return out + self.bias.view(1, -1, 1, 1) if self.bias is not None else out
