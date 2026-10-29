"""Builds the paper-vs-measured accuracy tables from ../results/accuracy.csv  ->  prints Markdown, writes ../results/tables.tex"""
import csv, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); CSV = os.path.join(HERE, '..', 'results', 'accuracy.csv')
# (model, mode, r) -> (label, paper accuracy %, note)
PAPER = {
 ('resnet20', 'fp32', '-'): ('FP32 baseline', 91.47, ''),
 ('resnet20', 'fp16', '-'): ('RN, FP16 acc. (E5M10)', 91.10, ''),
 ('resnet20', 'bf16', '-'): ('RN, BF16 acc. (E8M7)', 88.79, ''),
 ('resnet20', 'rn',   '-'): ('RN, E6M5 acc.', 83.03, 'paper row has subnormals; ours flushes'),
 ('resnet20', 'eager', '9'):  ('SR eager, E6M5, r=9', 43.11, 'paper row has subnormals'),
 ('resnet20', 'eager', '12'): ('SR eager, E6M5, r=12', 89.34, 'paper row has subnormals'),
 ('resnet20', 'eager', '16'): ('SR eager, E6M5, r=16, no sub', 90.67, ''),
 ('resnet20', 'eager', '18'): ('SR eager, E6M5, r=18, no sub', 91.39, ''),
 ('vgg16', 'fp32', '-'): ('FP32 baseline', 93.46, ''), ('vgg16', 'fp16', '-'): ('RN, FP16 acc.', 93.06, ''),
 ('vgg16', 'eager', '18'): ('SR eager, E6M5, r=18, no sub', 93.11, ''),
 ('resnet50', 'fp32', '-'): ('FP32 baseline', 80.94, ''), ('resnet50', 'fp16', '-'): ('RN, FP16 acc.', 80.30, ''),
 ('resnet50', 'eager', '18'): ('SR eager, E6M5, r=18, no sub', 80.33, ''),
}
ORDER = ['resnet20', 'vgg16', 'resnet50']
rows = list(csv.DictReader(open(CSV))) if os.path.exists(CSV) else []
meas = {}
for r in rows:
    if r['dataset'] == 'synthetic': continue
    meas[(r['model'], r['mode'], r['r'])] = (float(r['final_test_acc']), r['epochs'])
for k in list(meas):
    if k[1] == 'lazy' and (k[0], 'eager', k[2]) not in meas: meas[(k[0], 'eager', k[2])] = meas[k]
out, tex = [], []
for mdl in ORDER:
    out += [f"\n### {mdl}", "| Configuration | Paper % | Ours % | Epochs | Delta | Note |", "|---|---|---|---|---|---|"]
    tex += [r"\begin{table}[h]\centering\caption{%s: paper vs.\ our emulation}\begin{tabular}{lrrrr}\hline" % mdl,
            r"Configuration & Paper \% & Ours \% & Epochs & $\Delta$ \\\hline"]
    for key, (label, p, note) in PAPER.items():
        if key[0] != mdl: continue
        m = meas.get(key)
        ours, ep, dl = (f"{m[0]:.2f}", m[1], f"{m[0]-p:+.2f}") if m else ("--", "--", "--")
        out.append(f"| {label} | {p:.2f} | {ours} | {ep} | {dl} | {note} |")
        tex.append(f"{label} & {p:.2f} & {ours} & {ep} & {dl} \\\\")
    tex += [r"\hline\end{tabular}\end{table}"]
print("\n".join(out))
open(os.path.join(HERE, '..', 'results', 'tables.tex'), 'w').write("\n".join(tex))
