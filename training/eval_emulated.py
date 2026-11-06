"""
Cheap experiment: take FP32-trained weights and measure test accuracy when every conv / linear layer accumulates with each
emulated accumulator (FP16, BF16, RN-E6M5, eager SR with r = 9, 12, 16, 18).  Forward pass only: ~1-2 min per setting on a T4.
  python eval_emulated.py --ckpt /kaggle/working/fp32_resnet20.pt --data /kaggle/input/...  [--n-test 10000]
"""
import argparse, csv, os, time, warnings, torch
warnings.filterwarnings('ignore', message='.*Grid size.*')
import fp12_layers as L
from models import get_model

ap = argparse.ArgumentParser()
ap.add_argument('--ckpt', required=True); ap.add_argument('--model', default='resnet20')
ap.add_argument('--data', default='./data'); ap.add_argument('--n-test', type=int, default=10000)
ap.add_argument('--device', default='cuda' if torch.cuda.is_available() else 'cpu')
ap.add_argument('--synthetic', action='store_true'); ap.add_argument('--img', type=int, default=32)
ap.add_argument('--log', default='../results/inference_emulated.csv')
a = ap.parse_args(); dev = torch.device(a.device)

if a.synthetic:
    ds = torch.utils.data.TensorDataset(torch.randn(a.n_test, 3, a.img, a.img), torch.randint(0, 10, (a.n_test,)))
else:
    import torchvision, torchvision.transforms as Tf
    norm = Tf.Normalize((0.4914, 0.4822, 0.4465), (0.2470, 0.2435, 0.2616))
    ds = torchvision.datasets.CIFAR10(a.data, False, Tf.Compose([Tf.ToTensor(), norm]), download=True)
    ds = torch.utils.data.Subset(ds, range(min(a.n_test, len(ds))))
dl = torch.utils.data.DataLoader(ds, 100, shuffle=False)
sd = torch.load(a.ckpt, map_location=dev)['model']

def acc_of(model):
    model.eval(); ok = n = 0
    with torch.no_grad():
        for x, y in dl: ok += (model(x.to(dev)).argmax(1).cpu() == y).sum().item(); n += len(y)
    return 100.0 * ok / n

CONFIGS = [('fp32', '-'), ('fp16', '-'), ('bf16', '-'), ('rn', '-'), ('eager', 9), ('eager', 12), ('eager', 16), ('eager', 18)]
rows = []
for mode, r in CONFIGS:
    t0 = time.time()
    m = get_model(a.model, mode != 'fp32').to(dev); m.load_state_dict(sd)
    if mode != 'fp32':
        L.MACConfig.mode, L.MACConfig.r, L.MACConfig.stream, L.MACConfig.seed = mode, (r if r != '-' else 18), 'lfsr', 1
    acc = acc_of(m)
    print(f"{mode:6s} r={r!s:>2}  test acc {acc:6.2f}%   ({time.time()-t0:.0f}s)", flush=True)
    rows.append([a.model, 'synthetic' if a.synthetic else 'cifar10', mode, r, len(ds), f'{acc:.2f}'])
os.makedirs(os.path.dirname(os.path.abspath(a.log)), exist_ok=True)
new = not os.path.exists(a.log)
with open(a.log, 'a', newline='') as f:
    w = csv.writer(f)
    if new: w.writerow(['model', 'dataset', 'mode', 'r', 'n_test', 'acc'])
    w.writerows(rows)
