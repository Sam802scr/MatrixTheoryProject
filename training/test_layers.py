import torch, torch.nn as nn
import fp12_layers as L
from models import ResNet20

def test_grad_matches_fp32():
    torch.manual_seed(0)
    for name, mk in (("Linear", lambda e: (L.FP12Linear if e else nn.Linear)(16, 8)),
                     ("Conv2d", lambda e: (L.FP12Conv2d if e else nn.Conv2d)(3, 4, 3, 1, 1, bias=False))):
        ref, emu = mk(False), mk(True); emu.load_state_dict(ref.state_dict())
        x = torch.randn(4, 16) if name == "Linear" else torch.randn(2, 3, 6, 6)
        outs = []
        for m in (ref, emu):
            xx = x.clone().requires_grad_(True); y = m(xx); (y ** 2).sum().backward()
            outs.append((y.detach(), xx.grad, next(m.parameters()).grad))
        for t, (a, b) in zip(("output", "dX", "dW"), zip(outs[0], outs[1])):
            cos = torch.nn.functional.cosine_similarity(a.flatten(), b.flatten(), dim=0).item()
            print(f"  {name:6s} {t}: cosine(FP32, emulated MAC) = {cos:.4f}"); assert cos > 0.97

def test_resnet_step():
    torch.manual_seed(0)
    m = ResNet20(emulate=True); x = torch.randn(2, 3, 8, 8); y = torch.tensor([1, 3])
    L.MACConfig.mode = 'eager'
    loss = nn.functional.cross_entropy(m(x), y); loss.backward()
    g = [p.grad for p in m.parameters()]
    assert all(t is not None and torch.isfinite(t).all() for t in g)
    print(f"  ResNet-20 (emulated MAC) forward+backward ok, loss={loss.item():.3f}, all {len(g)} grads finite")

if __name__ == "__main__":
    test_grad_matches_fp32(); test_resnet_step(); print("LAYER TESTS PASSED")
