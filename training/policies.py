"""
Random-bit policies for adaptive stochastic rounding.  A policy maps (phase, K) -> r, where
  phase in {'fwd', 'dgrad', 'wgrad'}  (forward GEMM, input-gradient GEMM, weight-gradient GEMM) and
  K = length of the dot products accumulated in that GEMM.
String syntax used on the command line (train.py --r-policy ...):
  fixed:13                      r = 13 everywhere
  phase:7,7,13                  r_fwd = 7, r_dgrad = 7, r_wgrad = 13
  k:c=3,min=4,max=13            r = clamp(ceil(log2 K) + c, min, max)     (accumulation-length-aware)
"""
import math

def parse_policy(s):
    if not s: return None
    kind, _, arg = s.partition(':')
    if kind == 'fixed':
        r = int(arg); return lambda phase, K: r
    if kind == 'phase':
        f, d, w = [int(x) for x in arg.split(',')]; m = {'fwd': f, 'dgrad': d, 'wgrad': w}
        return lambda phase, K: m[phase]
    if kind == 'k':
        kv = dict(x.split('=') for x in arg.split(',')); c = int(kv.get('c', 3)); lo = int(kv.get('min', 4)); hi = int(kv.get('max', 13))
        return lambda phase, K: max(lo, min(hi, math.ceil(math.log2(max(K, 2))) + c))
    raise ValueError("unknown policy: " + s)
