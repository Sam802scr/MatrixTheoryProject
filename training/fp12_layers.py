"""Autograd + layers that run EVERY GEMM (forward and both backward GEMMs) on the emulated FP8 x FP8 -> FP12 SR MAC.
Supports:
  1. Fixed random bit precision (r)
  2. Callable policy mapping (phase, K) -> r (see policies.py, used by run_queue.py)
  3. Dynamic Adaptive Stochastic Rounding controller (AdaptiveSRController in adaptive_sr.py)
  4. FP16 and BF16 baseline accumulation
"""
import torch, torch.nn as nn, torch.nn.functional as F
import fp12_ops as T

class MACConfig:
    mode = 'eager'      # 'eager' | 'lazy' | 'rn' (all E6M5)   |  'fp16' | 'bf16' (RN accumulators of that width)
    r = 18              # default number of random bits (used when no policy is set)
    stream = 'lfsr'     # 'lfsr' (hardware-like) | 'ideal' (torch PRNG)
    seed = 1
    policy = None       # callable (phase, K) -> r
    controller = None   # AdaptiveSRController instance if using adaptive rounding
    count = True        # set False during evaluation so that stats only describe training GEMMs
    _calls = 0
    stats = {}          # phase -> [MAC count, sum of r over MACs, number of GEMM calls]
    hist = {}           # (phase, r) -> MAC count

    @classmethod
    def get_effective_r(cls, phase='fwd', K=1, layer_name=None):
        if cls.policy is not None:
            return int(cls.policy(phase, K))
        if cls.controller is not None:
            return int(cls.controller.get_r(layer_name=layer_name or phase, cin=K))
        return cls.r

    @classmethod
    def kw(cls, phase, K, M, N, layer_name=None):
        cls._calls += 1
        r = cls.get_effective_r(phase=phase, K=K, layer_name=layer_name)
        if cls.count:
            s = cls.stats.setdefault(phase, [0, 0.0, 0])
            s[0] += M * N * K
            s[1] += M * N * K * r
            s[2] += 1
            cls.hist[(phase, r)] = cls.hist.get((phase, r), 0) + M * N * K
        return dict(mode=cls.mode, r=r, stream=cls.stream, seed=cls.seed + cls._calls)

def _gemm(A, B, phase='fwd', layer_name=None):
    """float32 (M,K)@(K,N) on the emulated MAC."""
    A, B = A.float().contiguous(), B.float().contiguous()
    (M, K), N = A.shape, B.shape[1]
    if MACConfig.mode in ('fp16', 'bf16'):
        dt = torch.float16 if MACConfig.mode == 'fp16' else torch.bfloat16
        return T.gemm_float_acc(T.fp8_encode(A), T.fp8_encode(B), dt)
    return T.fp12_gemm(A, B, **MACConfig.kw(phase, K, M, N, layer_name=layer_name))

class FP12MatMul(torch.autograd.Function):
    @staticmethod
    def forward(ctx, A, B, wgrad_is_A, layer_name=None):
        ctx.save_for_backward(A, B)
        ctx.wgrad_is_A = wgrad_is_A
        ctx.layer_name = layer_name
        return _gemm(A, B, 'fwd', layer_name=layer_name)

    @staticmethod
    def backward(ctx, G):
        A, B = ctx.saved_tensors
        pA, pB = ('wgrad', 'dgrad') if ctx.wgrad_is_A else ('dgrad', 'wgrad')
        return _gemm(G, B.t(), pA, layer_name=ctx.layer_name), _gemm(A.t(), G, pB, layer_name=ctx.layer_name), None, None

class FP12Linear(nn.Linear):
    def __init__(self, in_features, out_features, bias=True, name='fc'):
        super().__init__(in_features, out_features, bias=bias)
        self.layer_name = name

    def forward(self, x):
        y = FP12MatMul.apply(x, self.weight.t(), False, self.layer_name)
        return y + self.bias if self.bias is not None else y

class FP12Conv2d(nn.Conv2d):
    def __init__(self, in_channels, out_channels, kernel_size, stride=1, padding=0, dilation=1, groups=1, bias=True, name='conv'):
        super().__init__(in_channels, out_channels, kernel_size, stride=stride, padding=padding, dilation=dilation, groups=groups, bias=bias)
        self.layer_name = name

    def forward(self, x):
        Nb, C, H, W = x.shape
        kh, kw = self.kernel_size
        Ho = (H + 2 * self.padding[0] - kh) // self.stride[0] + 1
        Wo = (W + 2 * self.padding[1] - kw) // self.stride[1] + 1
        cols = F.unfold(x, self.kernel_size, padding=self.padding, stride=self.stride)
        cols = cols.permute(1, 0, 2).reshape(C * kh * kw, Nb * Ho * Wo)
        out = FP12MatMul.apply(self.weight.view(self.out_channels, -1), cols, True, self.layer_name)
        out = out.view(self.out_channels, Nb, Ho * Wo).permute(1, 0, 2).reshape(Nb, self.out_channels, Ho, Wo)
        return out + self.bias.view(1, -1, 1, 1) if self.bias is not None else out
