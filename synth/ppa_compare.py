#!/usr/bin/env python3
"""
Quantitative hardware comparison of FP12 round-to-nearest, lazy SR and eager SR (and of the number of random bits r).
For every configuration it reports
  * adder only, ASIC proxy (Yosys + ABC, Nangate 45 nm): area, delay, cell count
  * complete MAC (exact FP8 multiplier + adder + accumulator register + LFSR), ASIC proxy: area, delay, flip-flops
  * complete MAC, FPGA proxy (Yosys synth_xilinx): LUTs and flip-flops
  * switching-energy proxy of the adder: gate-level toggle simulation of the mapped Nangate netlist on operand streams
    taken from simulated dot products; E = 0.5 * V^2 * sum_nets(alpha_net * C_net), C = input-pin capacitances of the fan-out
    (leakage, internal power and wire capacitance are NOT included)
Usage: python3 synth/ppa_compare.py [--quick] ; results in results/ppa_compare.csv
"""
import re, os, sys, subprocess, random, csv, math, tempfile, argparse
import numpy as np
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(ROOT, 'reference_model'))
from sr_mac_ref import *
LIB = os.path.join(ROOT, 'synth', 'NangateOpenCellLibrary_typical.lib')
R_ = lambda *f: ' '.join(os.path.join(ROOT, 'rtl', x) for x in f)
F_RN, F_LAZY = R_('fp12_add.v'), R_('fp12_add_sr_lazy.v')
F_EAGER = R_('fp12_sticky_round.v', 'fp12_round_correction.v', 'fp12_add_sr_eager.v')
F_MAC = R_('fp8_multiplier.v', 'lfsr_galois.v', 'fp12_add.v', 'fp12_add_sr_lazy.v', 'fp12_sticky_round.v',
           'fp12_round_correction.v', 'fp12_add_sr_eager.v', 'fp_mac.v')
MASK = {4: 0xC, 5: 0x14, 6: 0x30, 7: 0x60, 9: 0x110, 11: 0x500, 13: 0x100D, 18: 0x20400}   # primitive Galois polynomials (period 2^r-1)
ABC = "abc -liberty %s -script +strash;dch;map;topo;stime,-p;buffer,-c;upsize,-c;dnsize,-c;stime,-p" % LIB

def yosys(script, timeout=900):
    p = subprocess.run(['yosys', '-p', script], capture_output=True, text=True, timeout=timeout)
    return p.stdout + p.stderr

def parse_area_delay(log):
    a = re.findall(r"Chip area for (?:top )?module '\\?\w+': ([\d.]+)", log)
    d = re.findall(r"Delay =\s*([\d.]+) ps", log)
    return (float(a[-1]) if a else float('nan')), (float(d[-1]) if d else float('nan'))

def cells_of(log):
    return {m.group(1): int(m.group(2)) for m in re.finditer(r"^\s+(\w+)\s+(\d+)\s*$", log, re.M)} | \
           {m.group(1): int(m.group(2)) for m in re.finditer(r"^\s+(\w+)\s+(\d+)\s+[\d.]+\s*$", log, re.M)}

# ---------------------------------------------------------------- liberty parsing (functions + pin capacitance)
def parse_liberty():
    txt = open(LIB).read()
    cells = {}
    parts = re.split(r"\n\s*cell \((\w+)\)\s*\{", txt)
    for i in range(1, len(parts), 2):
        name, body = parts[i], parts[i + 1]
        pins = {}
        segs = re.split(r"\n\s*pin \((\w+)\)\s*\{", body)
        for j in range(1, len(segs), 2):
            pn, pb = segs[j], segs[j + 1]
            d = re.search(r"direction\s*:\s*(\w+)", pb)
            if not d: continue
            if d.group(1) == 'input':
                c = re.search(r"\n\s*capacitance\s*:\s*([\d.]+)", pb)
                pins[pn] = ('in', float(c.group(1)) if c else 0.0)
            else:
                f = re.search(r"function\s*:\s*\"([^\"]+)\"", pb)
                pins[pn] = ('out', f.group(1) if f else None)
        cells[name] = pins
    return cells

def parse_netlist(path, cells):
    txt = open(path).read()
    inst = []
    for m in re.finditer(r"^\s*(\w+)\s+(\S+)\s*\((.*?)\);", txt, re.M | re.S):
        if m.group(1) in cells:
            conns = dict((k, v.strip()) for k, v in re.findall(r"\.(\w+)\(([^)]*)\)", m.group(3)))
            inst.append((m.group(1), conns))
    assigns = re.findall(r"^\s*assign\s+(.+?)\s*=\s*(.+?);", txt, re.M)
    return inst, assigns

def energy_proxy(netlist, cells, inputs):
    """inputs: dict name -> bool array (T,)  (bit-blasted port names such as 'a[3]').  Returns fJ/op, mean toggles/op, #cells."""
    inst, assigns = parse_netlist(netlist, cells)
    val = dict(inputs); T = len(next(iter(inputs.values())))
    val["1'h0"] = np.zeros(T, bool); val["1'h1"] = np.ones(T, bool)
    alias = {l: r for l, r in assigns}
    def get(n):
        n = n.strip()
        if n in val: return val[n]
        if n in alias and alias[n].strip() in val: return val[alias[n].strip()]
        return None
    pending = list(inst); loads = {}
    ncell = len(pending); guard = 0
    while pending and guard < 400:
        guard += 1; nxt = []
        for cname, conns in pending:
            pins = cells[cname]
            ins = {p: get(n) for p, n in conns.items() if pins.get(p, ('',))[0] == 'in'}
            if any(v is None for v in ins.values()): nxt.append((cname, conns)); continue
            for p, n in conns.items():
                if pins.get(p, ('',))[0] == 'out':
                    expr = pins[p][1]
                    env = {k: v for k, v in ins.items()}
                    val[n.strip()] = eval(expr.replace('!', '~'), {}, env).astype(bool)
            for p, n in conns.items():
                if pins.get(p, ('',))[0] == 'in': loads[n.strip()] = loads.get(n.strip(), 0.0) + pins[p][1]
        if len(nxt) == len(pending): break
        pending = nxt
    if pending: raise RuntimeError("netlist evaluation incomplete: %d cells" % len(pending))
    tot = 0.0; tg = 0.0
    for n, c in loads.items():
        v = val.get(n)
        if v is None: v = get(n)
        if v is None: continue
        a = float(np.mean(v[1:] != v[:-1])); tot += a * c; tg += a
    return 0.5 * 1.1 ** 2 * tot, tg, ncell

# ---------------------------------------------------------------- operand streams
def fp8_encode_py(x):
    if x == 0: return 0
    s = 1 if x < 0 else 0; ax = abs(x); e = math.floor(math.log2(ax))
    if e < -14: return 0
    m = round(ax / 2.0 ** e * 4) / 4.0
    if m >= 2: m = 1.0; e += 1
    if e > 15: e, m = 15, 1.75
    return (s << 7) | ((e + 15) << 2) | int(round((m - 1) * 4))

def stream(mode, r, T=20000, K=576, seed=3):
    rng = random.Random(seed); lf = GaloisLFSR(seed=1, steps=18); acc = 0; A, B, W = [], [], []
    for t in range(T):
        if t % K == 0: acc = 0
        a8 = fp8_encode_py(rng.gauss(0, 1)); b8 = fp8_encode_py(rng.gauss(0, 1))
        prod = fp8_mul(a8, b8); w = lf.word() & ((1 << r) - 1) if mode != 'rn' else 0
        A.append(acc); B.append(prod); W.append(w)
        acc = {'rn': lambda: add_rn(acc, prod), 'lazy': lambda: add_lazy(acc, prod, w, r),
               'eager': lambda: add_eager(acc, prod, w, r)}[mode]()
    return np.array(A), np.array(B), np.array(W)

def bits(arr, name, n):
    return {"%s[%d]" % (name, i): ((arr >> i) & 1).astype(bool) for i in range(n)}

# ---------------------------------------------------------------- one configuration
def run_config(mode, r, cells, quick=False):
    top = {'rn': 'fp12_add', 'lazy': 'fp12_add_sr_lazy', 'eager': 'fp12_add_sr_eager'}[mode]
    files = {'rn': F_RN, 'lazy': F_LAZY, 'eager': F_EAGER}[mode]
    chp = "" if mode == 'rn' else "chparam -set R %d %s;" % (r, top)
    net = os.path.join(tempfile.gettempdir(), "net_%s_%s.v" % (mode, r))
    log = yosys("read_verilog %s; %s synth -top %s -flatten; %s; write_verilog -noattr -noexpr %s; tee stat -liberty %s" %
                (files, chp, top, ABC, net, LIB))
    area_a, delay_a = parse_area_delay(log)
    # complete MAC, ASIC proxy
    steps = r if mode != 'rn' else 1
    mp = "chparam -set MODE %d -set R %d -set STEPS %d -set SEED 1 -set MASK %d fp_mac;" % ({'rn': 0, 'lazy': 1, 'eager': 2}[mode], r if mode != 'rn' else 18, steps, MASK[r if mode != 'rn' else 18])
    logm = yosys("read_verilog %s; %s synth -top fp_mac -flatten; dfflibmap -liberty %s; %s; tee stat -liberty %s" % (F_MAC, mp, LIB, ABC, LIB))
    area_m, delay_m = parse_area_delay(logm)
    cm = cells_of(logm); ff_asic = sum(v for k, v in cm.items() if k.startswith('DFF'))
    # FPGA proxy
    logf = yosys("read_verilog %s; %s synth_xilinx -top fp_mac -flatten; tee stat" % (F_MAC, mp))
    cf = cells_of(logf)
    lut = sum(v for k, v in cf.items() if re.fullmatch(r"LUT[1-6]", k)); ff = sum(v for k, v in cf.items() if k.startswith('FD'))
    # energy proxy
    T = 3000 if quick else 20000
    A, B, W = stream(mode, r, T)
    ins = {**bits(A, 'a', 12), **bits(B, 'b', 12)}
    if mode != 'rn': ins.update(bits(W, 'random_bits', r))
    e_fj, tog, ncell = energy_proxy(net, cells, ins)
    return dict(design=mode, r=(r if mode != 'rn' else 0), adder_area_um2=area_a, adder_delay_ps=delay_a, adder_cells=ncell,
                mac_area_um2=area_m, mac_delay_ps=delay_m, mac_ff_asic=ff_asic, mac_lut=lut, mac_ff_fpga=ff,
                adder_energy_fJ=round(e_fj, 2), adder_toggles_per_op=round(tog, 1))

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--quick', action='store_true'); ap.add_argument('--only', default='')
    ap.add_argument('--out', default=os.path.join(ROOT, 'results', 'ppa_compare.csv')); a = ap.parse_args()
    cells = parse_liberty()
    cfgs = [('rn', 18)] + [(m, r) for r in (4, 7, 9, 11, 13) for m in ('lazy', 'eager')]
    if a.only: cfgs = [(c.split(':')[0], int(c.split(':')[1])) for c in a.only.split(',')]
    os.makedirs(os.path.dirname(a.out), exist_ok=True); new = not os.path.exists(a.out)
    for mode, r in cfgs:
        row = run_config(mode, r, cells, a.quick); print(row, flush=True)
        with open(a.out, 'a', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(row)); 
            if new: w.writeheader(); new = False
            w.writerow(row)
