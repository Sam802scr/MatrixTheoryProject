"""
Experiment matrix of the paper (Tables III and IV).  Prints the train.py commands; add --run to execute them one after another.
  python run_experiments.py --table 3                 # ResNet-20 / CIFAR-10  (random-bit sweep + baselines)
  python run_experiments.py --table 4                 # VGG-16 / CIFAR-10 and ResNet-50 / Imagewoof (--imagewoof PATH)
  python run_experiments.py --table 3 --epochs 10     # reduced-length version for a quick trend check
Rows of the paper that need SUBNORMAL support (Table III: RN E6M5 83.03, SR W/ Sub r=9/12/16/18) are not runnable yet:
the emulated adder implements the paper's main 'W/O Sub' configuration only.
"""
import argparse, subprocess, sys
ap = argparse.ArgumentParser()
ap.add_argument('--table', type=int, choices=[3, 4], required=True)
ap.add_argument('--epochs', type=int, default=None, help='override the paper epoch count (reduced runs are NOT comparable with the paper)')
ap.add_argument('--imagewoof', default='./imagewoof2')
ap.add_argument('--seed', type=int, default=0)
ap.add_argument('--run', action='store_true')
a = ap.parse_args()

def cmd(model, mode, r=None, extra=()):
    c = [sys.executable, 'train.py', '--model', model, '--mode', mode, '--seed', str(a.seed)]
    if r: c += ['--r', str(r)]
    if a.epochs: c += ['--epochs', str(a.epochs)]
    return c + list(extra)

jobs = []
if a.table == 3:
    jobs += [cmd('resnet20', 'fp32'), cmd('resnet20', 'fp16'), cmd('resnet20', 'bf16'), cmd('resnet20', 'rn')]
    jobs += [cmd('resnet20', 'eager', r) for r in (9, 12, 16, 18)]
else:
    jobs += [cmd('vgg16', m, 18 if m == 'eager' else None) for m in ('fp32', 'fp16', 'eager')]
    jobs += [cmd('resnet50', m, 18 if m == 'eager' else None, ['--data', a.imagewoof]) for m in ('fp32', 'fp16', 'eager')]
for j in jobs:
    print(' '.join(j))
    if a.run: subprocess.run(j, check=True)
