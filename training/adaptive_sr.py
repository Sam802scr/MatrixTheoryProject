"""
Adaptive Stochastic Rounding (ASR) Controller and Energy Modeling.
Supports:
  1. Phase-Adaptive SR (Phase-ASR): selects r based on training progress/epoch (cosine or step schedule).
  2. Layer-Adaptive SR (Layer-ASR): selects r based on GEMM accumulation depth K / layer depth.
  3. Hybrid-ASR: combines temporal (phase) annealing with spatial (layer) sensitivity.
Computes analytical hardware complexity, dynamic switching energy, and PRNG bit reduction.
"""
import math

class AdaptiveSRController:
    def __init__(self, policy='phase', r_min=7, r_max=13, total_epochs=165, schedule='cosine'):
        self.policy = policy
        self.r_min = r_min
        self.r_max = r_max
        self.total_epochs = total_epochs
        self.schedule = schedule
        self.current_epoch = 0

    def set_epoch(self, epoch):
        self.current_epoch = epoch

    def get_phase_r(self, epoch=None):
        if epoch is None:
            epoch = self.current_epoch
        t = min(max(epoch, 0), self.total_epochs)
        if self.schedule == 'cosine':
            # Cosine annealing from r_min to r_max
            progress = 0.5 * (1.0 - math.cos(math.pi * t / max(1, self.total_epochs)))
            r = round(self.r_min + (self.r_max - self.r_min) * progress)
        elif self.schedule == 'step':
            # 3-step schedule: early (r_min), mid (average), late (r_max)
            frac = t / max(1, self.total_epochs)
            if frac < 0.35:
                r = self.r_min
            elif frac < 0.70:
                r = round((self.r_min + self.r_max) / 2)
            else:
                r = self.r_max
        else: # linear
            r = round(self.r_min + (self.r_max - self.r_min) * (t / max(1, self.total_epochs)))
        return int(max(4, min(self.r_max, r)))

    def get_layer_r(self, layer_name, cin=None, cout=None):
        """
        Determines r based on GEMM reduction dimension K = cin * kh * kw.
        In ResNet-20:
          conv1: cin=3, kh=kw=3 -> K = 27 -> r = 7
          stage 1: cin=16, kh=kw=3 -> K = 144 -> r = 9
          stage 2: cin=32, kh=kw=3 -> K = 288 -> r = 11
          stage 3: cin=64, kh=kw=3 -> K = 576 -> r = 13
          fc: cin=64 -> K = 64 -> r = 9
        """
        if layer_name == 'conv1' or (cin is not None and cin <= 3):
            return 7
        elif 'layers.0' in layer_name or (cin is not None and cin <= 16):
            return 9
        elif 'layers.1' in layer_name or (cin is not None and cin <= 32):
            return 11
        elif 'layers.2' in layer_name or (cin is not None and cin >= 64):
            return 13
        elif 'fc' in layer_name:
            return 9
        return 11

    def get_r(self, layer_name='conv', epoch=None, cin=None):
        if self.policy == 'fixed':
            return self.r_max
        elif self.policy == 'phase':
            return self.get_phase_r(epoch)
        elif self.policy == 'layer':
            return self.get_layer_r(layer_name, cin=cin)
        elif self.policy == 'hybrid':
            rp = self.get_phase_r(epoch)
            rl = self.get_layer_r(layer_name, cin=cin)
            # Hybrid blends phase progress with layer requirement
            base_delta = rl - 11  # relative to center
            r = rp + base_delta
            return int(max(4, min(self.r_max, r)))
        return self.r_max

    def compute_energy_metrics(self):
        """
        Calculates average bits, PRNG energy reduction, and sticky-adder dynamic switching reduction
        compared to fixed 13-bit and fixed 18-bit baselines.
        """
        # Phase schedule bit sequence over all epochs
        r_hist = [self.get_phase_r(ep) for ep in range(self.total_epochs)]
        avg_r_phase = sum(r_hist) / len(r_hist)

        # Dynamic power in sticky round scales with (r - 2) active bits
        # Dynamic power in LFSR scales with r active bits
        active_sticky_fixed13 = 13 - 2 # 11
        active_sticky_fixed18 = 18 - 2 # 16
        active_sticky_phase = sum(r - 2 for r in r_hist) / len(r_hist)

        savings_vs_fixed13 = (1.0 - (active_sticky_phase / active_sticky_fixed13)) * 100.0
        savings_vs_fixed18 = (1.0 - (active_sticky_phase / active_sticky_fixed18)) * 100.0
        prng_savings_vs_fixed13 = (1.0 - (avg_r_phase / 13.0)) * 100.0
        prng_savings_vs_fixed18 = (1.0 - (avg_r_phase / 18.0)) * 100.0

        return {
            'avg_r': avg_r_phase,
            'sticky_power_savings_vs_fixed13_pct': savings_vs_fixed13,
            'sticky_power_savings_vs_fixed18_pct': savings_vs_fixed18,
            'prng_power_savings_vs_fixed13_pct': prng_savings_vs_fixed13,
            'prng_power_savings_vs_fixed18_pct': prng_savings_vs_fixed18,
        }

if __name__ == '__main__':
    ctrl = AdaptiveSRController(policy='phase', r_min=7, r_max=13, total_epochs=165)
    metrics = ctrl.compute_energy_metrics()
    print("Adaptive SR Phase Controller Metrics (Cosine Schedule):")
    for k, v in metrics.items():
        print(f"  {k}: {v:.2f}")
