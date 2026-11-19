"""Experiment suite for the extension study (professor's items 1-4).  Every experiment is a short fine-tuning run that starts from the
FP32 ResNet-20 weights (91.47 % after 165 epochs) and runs ALL GEMMs of forward and backward pass on the emulated MAC.
Name -> (train.py arguments).  Groups are run with run_queue.py --group <name>."""
INIT = "/kaggle/input/datasets/samagnapotham/fp32-resnet20/fp32_resnet20.pt"

def ft(name, mode, extra="", epochs=1, lr=0.01):
    return name, f"--mode {mode} {extra} --epochs {epochs} --lr {lr}".replace("  ", " ")

SUITE = {
 # item 3: random-bit sweep (eager SR) + lazy SR reference at r = 13
 'sweep': [ft(f"eager_r{r}", "eager", f"--r {r}") for r in (4, 7, 9, 11, 13)] + [ft("lazy_r13", "lazy", "--r 13")],
 # item 2 baselines (1 epoch): FP32, FP16 / BF16 / E6M5 round-to-nearest accumulators
 'baselines': [ft("fp32", "fp32"), ft("fp16_rn", "fp16"), ft("bf16_rn", "bf16"), ft("e6m5_rn", "rn")],
 # item 4a: sensitivity of each GEMM type to a very low r (r = 4), others at r = 13
 'sens': [ft("phase_4_13_13", "eager", "--r-policy phase:4,13,13"), ft("phase_13_4_13", "eager", "--r-policy phase:13,4,13"),
          ft("phase_13_13_4", "eager", "--r-policy phase:13,13,4")],
 # item 4b: adaptive candidates (low r where the network is insensitive, r = 13 where it is not)
 'adaptive': [ft("ad_7_7_13", "eager", "--r-policy phase:7,7,13"), ft("ad_4_4_13", "eager", "--r-policy phase:4,4,13"),
              ft("ad_4_7_13", "eager", "--r-policy phase:4,7,13"), ft("ad_k3", "eager", "--r-policy k:c=3,min=4,max=13")],
 # item 2: convergence over 3 epochs (5 evaluation points per epoch on 2000 test images)
 'conv': [ft("c3_fp32", "fp32", epochs=3), ft("c3_fp16_rn", "fp16", epochs=3), ft("c3_e6m5_rn", "rn", epochs=3),
          ft("c3_eager_r13", "eager", "--r 13", epochs=3), ft("c3_lazy_r13", "lazy", "--r 13", epochs=3)],
}
