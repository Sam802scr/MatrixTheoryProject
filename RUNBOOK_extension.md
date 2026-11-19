# Extension study - run book (Kaggle)

Order of work: (0) push the patch, (1) sanity check on the GPU, (2) three background runs, (3) download results and send them back.
Every run is a 1-3 epoch FINE-TUNE from the FP32 ResNet-20 weights (dataset `fp32-resnet20`), all GEMMs of forward+backward on the emulated MAC.

## 0. Laptop (once)
Unzip `sr_mac_extension_patch.zip` into the repo folder (merge, overwrite), then
    git add -A
    git commit -m "Extension: r sweep, FP16/BF16 accumulators, adaptive random bits, hardware comparison"
    git push

## 1. Kaggle sanity check (5 min). Settings: Internet ON, Accelerator = GPU T4 x2, Input = fp32-resnet20 (+ optional CIFAR-10 dataset)
    %cd /kaggle/working
    !git clone https://github.com/Sam802scr/MatrixTheoryProject
    %cd MatrixTheoryProject/training
    !python bench_cuda.py
Expect: "BIT-EXACT" five times (eager, lazy, rn, fp16, bf16).

## 2. Background runs (use "Save Version" -> "Save & Run All"; the notebook may be closed afterwards)
Notebook cell, one group per version (each version = one cell like this):
    %cd /kaggle/working
    !git clone https://github.com/Sam802scr/MatrixTheoryProject
    %cd MatrixTheoryProject/training
    !python -u run_queue.py --group GROUP --out /kaggle/working/ext
with GROUP =
  1. `sweep,baselines`  r = 4,7,9,11,13 (eager), lazy r=13, FP32, FP16, BF16, E6M5-RN    about 9 GPU-h  -> about 4.5 h on 2 GPUs
  2. `sens,adaptive`    sensitivity (r=4 in one GEMM type) + 4 adaptive candidates       about 6 GPU-h  -> about 3 h
  3. `conv`             3-epoch convergence runs (FP32, FP16, RN, eager13, lazy13)        about 10 GPU-h -> about 5 h
(Times are estimates from 7.1 s per batch measured earlier.  Quota is about 30 h per week.)

## 3. Results
Download the folder `ext` from the notebook Output (results.csv, curves.csv, *.macstats.json, logs/) and send / upload it.
Analysis:  python analyze_extension.py --res <ext folder> --ppa ../results/ppa_compare.csv --out ../report_ext
