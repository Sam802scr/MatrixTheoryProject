"""
ResNet-20 / CIFAR-10 training with the paper's settings, FP32 baseline or emulated FP8->FP12 MAC.
  python train.py --mode fp32                       # baseline (paper: 91.47 %)
  python train.py --mode eager --r 18               # paper's design (paper: 91.39 %)
  python train.py --mode eager --r 9 --epochs 165   # r sweep (paper Table III)
  python train.py --model vgg16 --mode eager        # VGG-16 / CIFAR-10   (paper: 93.11 % vs 93.46 % FP32)
  python train.py --model resnet50 --mode eager --data D:/imagewoof2   # ResNet-50 / Imagewoof (paper: 80.33 % vs 80.94 %)
  python train.py --mode eager --synthetic --img 8 --epochs 1 --batch 2 --log /tmp/a.csv   # CPU smoke test
Paper settings: SGD m=0.9, lr 0.1, wd 1e-4, batch 128, cosine annealing, 165 epochs, dynamic loss scale init 1024.
"""
import argparse, csv, os, time, math, torch, torch.nn as nn
import fp12_layers as L
from models import get_model

p = argparse.ArgumentParser()
p.add_argument('--model', default='resnet20', choices=['resnet20', 'vgg16', 'resnet50'])
p.add_argument('--mode', default='fp32', choices=['fp32', 'rn', 'lazy', 'eager', 'fp16', 'bf16'])
p.add_argument('--r', type=int, default=18)
p.add_argument('--stream', default='lfsr', choices=['lfsr', 'ideal'])
p.add_argument('--epochs', type=int, default=None)
p.add_argument('--batch', type=int, default=None)
p.add_argument('--lr', type=float, default=None)
p.add_argument('--wd', type=float, default=None)
p.add_argument('--seed', type=int, default=0)
p.add_argument('--data', default='./data')
p.add_argument('--device', default='cuda' if torch.cuda.is_available() else 'cpu')
p.add_argument('--max-batches', type=int, default=0, help='debug: stop each epoch after N batches')
p.add_argument('--synthetic', action='store_true', help='random data instead of CIFAR-10 (smoke test)')
p.add_argument('--img', type=int, default=32, help='synthetic image size (use 8 for a fast CPU smoke test)')
p.add_argument('--log', default='../results/accuracy.csv')
a = p.parse_args()
# paper Sec. IV-A.  (resnet50 weight decay / schedule are NOT given in the paper: 1e-4 and cosine are our assumptions)
DEF = {'resnet20': dict(epochs=165, batch=128, lr=0.1, wd=1e-4), 'vgg16': dict(epochs=200, batch=128, lr=0.01, wd=5e-4),
       'resnet50': dict(epochs=100, batch=16, lr=0.01, wd=1e-4)}[a.model]
for k, v in DEF.items():
    if getattr(a, k) is None: setattr(a, k, v)

torch.manual_seed(a.seed)
emu = a.mode != 'fp32'
L.MACConfig.mode, L.MACConfig.r, L.MACConfig.stream, L.MACConfig.seed = a.mode if emu else 'eager', a.r, a.stream, a.seed * 100003
dev = torch.device(a.device)

# ---------------------------------------------------------------- data
if a.model == 'resnet50' and not a.synthetic:      # Imagewoof (ImageFolder layout: <data>/train/<class>/*.JPEG and <data>/val/...)
    import torchvision, torchvision.transforms as Tf
    norm = Tf.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))     # resolution/augmentation: ASSUMED (paper silent)
    tr = torchvision.datasets.ImageFolder(os.path.join(a.data, 'train'), Tf.Compose([Tf.RandomResizedCrop(224), Tf.RandomHorizontalFlip(), Tf.ToTensor(), norm]))
    te = torchvision.datasets.ImageFolder(os.path.join(a.data, 'val'), Tf.Compose([Tf.Resize(256), Tf.CenterCrop(224), Tf.ToTensor(), norm]))
elif a.synthetic:
    mk = lambda n: torch.utils.data.TensorDataset(torch.randn(n, 3, a.img, a.img), torch.randint(0, 10, (n,)))
    tr, te = mk(8), mk(4)
else:
    import torchvision, torchvision.transforms as Tf
    norm = Tf.Normalize((0.4914, 0.4822, 0.4465), (0.2470, 0.2435, 0.2616))
    tr = torchvision.datasets.CIFAR10(a.data, True, Tf.Compose([Tf.RandomCrop(32, 4), Tf.RandomHorizontalFlip(), Tf.ToTensor(), norm]), download=True)
    te = torchvision.datasets.CIFAR10(a.data, False, Tf.Compose([Tf.ToTensor(), norm]), download=True)
trl = torch.utils.data.DataLoader(tr, a.batch, shuffle=True, drop_last=True, num_workers=0 if a.synthetic else 2)
tel = torch.utils.data.DataLoader(te, 100, shuffle=False)

# ---------------------------------------------------------------- model / optimiser (paper Sec. IV-A)
model = get_model(a.model, emu).to(dev)
opt = torch.optim.SGD(model.parameters(), lr=a.lr, momentum=0.9, weight_decay=a.wd)
sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=a.epochs)
scale, good = 1024.0, 0                      # dynamic loss scaling (Micikevicius et al.), initial factor 1024

def evaluate():
    model.eval(); ok = n = 0
    with torch.no_grad():
        for i, (x, y) in enumerate(tel):
            if a.max_batches and i >= a.max_batches: break
            ok += (model(x.to(dev)).argmax(1).cpu() == y).sum().item(); n += len(y)
    model.train(); return 100.0 * ok / n

acc = 0.0
for ep in range(a.epochs):
    t0, tl, nb = time.time(), 0.0, 0
    for i, (x, y) in enumerate(trl):
        if a.max_batches and i >= a.max_batches: break
        loss = nn.functional.cross_entropy(model(x.to(dev)), y.to(dev))
        opt.zero_grad(set_to_none=True)
        if emu:
            (loss * scale).backward()
            if all(torch.isfinite(q.grad).all() for q in model.parameters() if q.grad is not None):
                for q in model.parameters():
                    if q.grad is not None: q.grad /= scale
                opt.step(); good += 1
                if good % 2000 == 0: scale *= 2
            else:
                scale /= 2; good = 0                      # overflow: skip step, halve the scale
        else:
            loss.backward(); opt.step()
        tl += loss.item(); nb += 1
    sched.step(); acc = evaluate()
    print(f"epoch {ep+1:3d}/{a.epochs}  loss {tl/max(nb,1):.4f}  test acc {acc:.2f}%  lr {sched.get_last_lr()[0]:.4f}  scale {scale:g}  {time.time()-t0:.0f}s", flush=True)

os.makedirs(os.path.dirname(os.path.abspath(a.log)), exist_ok=True)
new = not os.path.exists(a.log)
with open(a.log, 'a', newline='') as f:
    w = csv.writer(f)
    if new: w.writerow(['model', 'dataset', 'mode', 'r', 'stream', 'epochs', 'batch', 'seed', 'final_test_acc'])
    w.writerow([a.model, 'synthetic' if a.synthetic else ('imagewoof' if a.model == 'resnet50' else 'cifar10'), a.mode, a.r if emu else '-', a.stream if emu else '-', a.epochs, a.batch, a.seed, f'{acc:.2f}'])
print("final test accuracy:", f"{acc:.2f}%")
