# Paper-coverage checklist  (DATE 2024, "A Stochastic Rounding-Enabled Low-Precision FP MAC for DNN Training")
Status: DONE = implemented + verified · PROXY = open-source substitute, trend only · TODO = not done / needs resources

| Paper item | Where | Status |
|---|---|---|
| Sec. II-A SR definition, Eq. (1)-(2), Fig. 1 (add random bits, carry rounds up) | `reference_model/sr_mac_ref.py` `add_lazy`; `test_probability` | DONE |
| Fig. 2 MAC = exact multiplier + adder + PRNG + register | `rtl/fp_mac.v` | DONE |
| III-a exact FP8 E5M2 multiplier -> FP12 E6M5 | `rtl/fp8_multiplier.v` (all 65,536 pairs checked) | DONE |
| III-c Galois LFSR PRNG | `rtl/lfsr_galois.v` (x^18+x^11+1; taps/seed/steps are ASSUMED) | DONE (assumed polynomial) |
| III-A RN dual-path adder baseline | `rtl/fp12_add.v` (nearest-even, vs exact oracle on 300k pairs) | DONE |
| Fig. 3a lazy SR adder | `rtl/fp12_add_sr_lazy.v` | DONE |
| Fig. 3b + Fig. 4 eager SR adder, Sticky Round, Round Correction | `rtl/fp12_add_sr_eager.v`, `fp12_sticky_round.v`, `fp12_round_correction.v` | DONE (+ extra j=2 path for far-path subtraction, not in the paper) |
| III-B brute-force probability test (10000 pairs x 1000 random words) | `training/paper_probability_test.py` | DONE (0 violations) |
| RTL == golden model, r = 9,12,14,16,18 | `./run_all.sh` (180,993 + 4x30,000 adder vectors, 4000 MAC steps) | DONE |
| Table I ASIC area / delay (Synopsys, 28nm FDSOI) | `synth/run_nangate.sh` -> `results/hardware_proxy.csv` (Yosys+ABC, Nangate45, adders only) | PROXY |
| Table I FP32 / FP16 / BF16 adders (E8M23, E5M10, E8M7) | RTL is E6M5 only | TODO |
| Table I energy (nW/MHz) | needs power tool + switching activity | TODO |
| Table I "W/ Sub" (subnormal support) | adders flush subnormals | TODO |
| Table II FPGA LUT / FF / delay (Vivado 2022.1, VU9P) | `synth/run_yosys.sh` gives LUT proxy only | PROXY |
| Table V area/delay/energy vs r | `results/hardware_proxy.csv` (area, delay vs r) | PROXY |
| IV-A training settings (ResNet-20, VGG-16, ResNet-50) | `training/train.py` defaults (ResNet-50 weight decay / schedule assumed) | DONE |
| IV: bit-accurate PyTorch emulation of FWD+BWD GEMMs | `training/fp12_ops.py`, `fp12_layers.py` (bit-exact vs golden model) | DONE |
| IV: custom CUDA kernels | `training/fp12_cuda.py` (bit-exact in Numba CUDA simulator; NOT yet run on a real GPU) | DONE in simulator / TODO on GPU |
| Dynamic loss scaling, init 1024 | `training/train.py` | DONE |
| Table III ResNet-20 rows W/O subnormals (FP32, FP16, BF16, SR r=16, 18) | `run_experiments.py --table 3` | TODO (needs GPU time) |
| Table III rows WITH subnormals (RN E6M5, SR r=9,12,16,18) | needs subnormal support in multiplier/adder | TODO |
| Table IV VGG-16 / CIFAR-10, ResNet-50 / Imagewoof | `run_experiments.py --table 4` | TODO (needs GPU time) |
| Conclusion headline: ~50% vs FP32, >20% delay and ~10% area vs FP16 | needs FP16/FP32 adders in the same synthesis flow | TODO |

## Deviations / assumptions to state in the report
1. LFSR polynomial, seed, 18 steps per MAC: not given in the paper.
2. FP8 inputs: subnormals flushed, overflow saturates; FP12: exponent code 63 reserved, overflow saturates, +0 result.
3. Eager adder: far-path *subtraction* can need a 2-bit normalization (j=2); the paper only analyses addition. Added a third carry (S3).
4. In the left-shift cases the eager adder effectively uses r-1 (j=1) / r-2 (j=2) random bits (still exactly unbiased).
5. Hardware numbers: Yosys+ABC on Nangate45; synthesis area for identical logic varies up to ~7% with netlist structure, so only ratios >10% are meaningful.
6. FP16 / BF16 baselines are software RN accumulators (fp32 sum then rounding), not bit-exact hardware adders.
7. ResNet-50 / Imagewoof: resolution 224, RandomResizedCrop + flip, weight decay 1e-4, cosine schedule: ASSUMED.
