"""ResNet-20 for CIFAR-10 (He et al. 2016 CIFAR variant, 0.27M params). conv/linear classes are swappable."""
import torch.nn as nn, torch.nn.functional as F
from fp12_layers import FP12Conv2d, FP12Linear

class Block(nn.Module):
    def __init__(s, cin, cout, stride, Conv):
        super().__init__()
        s.c1 = Conv(cin, cout, 3, stride, 1, bias=False); s.b1 = nn.BatchNorm2d(cout)
        s.c2 = Conv(cout, cout, 3, 1, 1, bias=False);     s.b2 = nn.BatchNorm2d(cout)
        s.sc = None
        if stride != 1 or cin != cout:
            s.sc = nn.Sequential(Conv(cin, cout, 1, stride, 0, bias=False), nn.BatchNorm2d(cout))
    def forward(s, x):
        o = F.relu(s.b1(s.c1(x))); o = s.b2(s.c2(o))
        return F.relu(o + (x if s.sc is None else s.sc(x)))

class ResNet20(nn.Module):
    def __init__(s, emulate=False, num_classes=10, n=3):
        super().__init__()
        Conv = FP12Conv2d if emulate else nn.Conv2d
        Lin = FP12Linear if emulate else nn.Linear
        s.conv1 = Conv(3, 16, 3, 1, 1, bias=False); s.bn1 = nn.BatchNorm2d(16)
        layers, cin = [], 16
        for cout, stride in ((16, 1), (32, 2), (64, 2)):
            for i in range(n):
                layers.append(Block(cin, cout, stride if i == 0 else 1, Conv)); cin = cout
        s.layers = nn.Sequential(*layers)
        s.fc = Lin(64, num_classes)
        for m in s.modules():
            if isinstance(m, nn.Conv2d): nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
    def forward(s, x):
        x = F.relu(s.bn1(s.conv1(x))); x = s.layers(x)
        return s.fc(F.adaptive_avg_pool2d(x, 1).flatten(1))


# ----------------------------------------------------------------------------- VGG-16 (BN) for CIFAR-10
class VGG16(nn.Module):
    CFG = [64, 64, 'M', 128, 128, 'M', 256, 256, 256, 'M', 512, 512, 512, 'M', 512, 512, 512, 'M']
    def __init__(s, num_classes=10):
        super().__init__()
        layers, cin = [], 3
        for v in s.CFG:
            if v == 'M': layers.append(nn.MaxPool2d(2))
            else: layers += [nn.Conv2d(cin, v, 3, padding=1, bias=False), nn.BatchNorm2d(v), nn.ReLU(inplace=True)]; cin = v
        s.features = nn.Sequential(*layers)
        s.classifier = nn.Linear(512, num_classes)
    def forward(s, x): return s.classifier(s.features(x).flatten(1))

# ----------------------------------------------------------------------------- layer swapping + factory
def swap_to_emulated(module):
    """Replace every nn.Conv2d / nn.Linear (recursively) by the emulated-MAC version, keeping the weights."""
    import fp12_layers as L
    for name, ch in module.named_children():
        if type(ch) is nn.Conv2d:
            assert ch.groups == 1 and ch.dilation == (1, 1)
            n = L.FP12Conv2d(ch.in_channels, ch.out_channels, ch.kernel_size, ch.stride, ch.padding, bias=ch.bias is not None)
            n.load_state_dict(ch.state_dict()); setattr(module, name, n)
        elif type(ch) is nn.Linear:
            n = L.FP12Linear(ch.in_features, ch.out_features, bias=ch.bias is not None)
            n.load_state_dict(ch.state_dict()); setattr(module, name, n)
        else:
            swap_to_emulated(ch)
    return module

def get_model(name, emulate):
    if name == 'resnet20': return ResNet20(emulate=emulate)
    if name == 'vgg16':
        m = VGG16()
    elif name == 'resnet50':
        import torchvision
        m = torchvision.models.resnet50(num_classes=10)
    else: raise ValueError(name)
    return swap_to_emulated(m) if emulate else m
