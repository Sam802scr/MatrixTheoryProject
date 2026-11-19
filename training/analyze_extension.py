"""Builds the tables and figures of the extension study from the experiment outputs.
  python analyze_extension.py --res <dir with results.csv, curves.csv, *.macstats.json> --ppa ../results/ppa_compare.csv --out ../report_ext
Hardware-complexity model of a policy: the MAC operations of each GEMM type are executed by MAC units whose random-bit width equals
the r chosen for that type, so that   relative_cost = sum_{phase,r} (MAC share of (phase,r)) * cost(r) / cost(13);   cost(r) is interpolated from
the synthesis sweep (adder area, switching energy or LUTs of the eager adder).  Without separate arrays per phase the saving is smaller
(the unit must then be built for the widest r) -- both numbers are reported."""
import argparse, csv, json, os, glob
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
ap = argparse.ArgumentParser()
ap.add_argument('--res', required=True); ap.add_argument('--ppa', required=True); ap.add_argument('--out', default='report_ext')
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
plt.rcParams.update({'font.size': 9.5, 'axes.spines.top': False, 'axes.spines.right': False, 'font.family': 'serif'})
rd = lambda p: list(csv.DictReader(open(p))) if os.path.exists(p) else []
ppa = rd(a.ppa); res = {r['name']: float(r['final_test_acc']) for r in rd(os.path.join(a.res, 'results.csv'))}
curves = rd(os.path.join(a.res, 'curves.csv'))
def cost_fn(metric):
    """linear least-squares fit of the eager-adder cost against r (single synthesis runs differ by up to ~10 % from tool noise, so the
    fitted trend is used instead of the individual, non-monotonic points)"""
    pts = sorted((int(r['r']), float(r[metric])) for r in ppa if r['design'] == 'eager')
    xs, ys = zip(*pts); b, a0 = np.polyfit(xs, ys, 1); return lambda r: float(a0 + b * r)
metrics = {'adder_area_um2': 'area', 'adder_energy_fJ': 'energy', 'mac_lut': 'LUTs'}
# ---------------- hardware table
with open(os.path.join(a.out, 'hw_table.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['design', 'r', 'adder_area_um2', 'adder_delay_ps', 'mac_area_um2', 'mac_delay_ps', 'mac_lut', 'mac_ff', 'adder_energy_fJ'])
    for r in sorted(ppa, key=lambda r: (r['design'], int(r['r']))):
        w.writerow([r['design'], r['r'], r['adder_area_um2'], r['adder_delay_ps'], r['mac_area_um2'], r['mac_delay_ps'], r['mac_lut'], r['mac_ff_fpga'], r['adder_energy_fJ']])
# ---------------- accuracy vs r
rs = [4, 7, 9, 11, 13]; acc = [res.get(f'eager_r{r}') for r in rs]
fig, ax = plt.subplots(figsize=(4.8, 3.0))
ax.plot([r for r, v in zip(rs, acc) if v], [v for v in acc if v], 'o-', color='#1e8449', label='eager SR')
for k, c, l in (('fp32', '#555', 'FP32'), ('fp16_rn', '#2e6da4', 'FP16 RN'), ('e6m5_rn', '#b03a2e', 'E6M5 RN')):
    if k in res: ax.axhline(res[k], color=c, ls='--', lw=1, label=l)
ax.set_xlabel('random bits $r$'); ax.set_ylabel('test accuracy (%)'); ax.legend(frameon=False, fontsize=8); plt.tight_layout(); plt.savefig(os.path.join(a.out, 'fig_acc_vs_r.pdf')); plt.close()
# ---------------- convergence curves
names = sorted({c['name'] for c in curves if c['name'].startswith('c3_')})
if names:
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 2.9))
    for n in names:
        L = [(int(c['epoch']), int(c['iter']), float(c['value'])) for c in curves if c['name'] == n and c['kind'] == 'train_loss']
        x = [(e - 1) * 390 + i for e, i, _ in L]; y = np.convolve([v for *_, v in L], np.ones(5) / 5, mode='same') if len(L) > 5 else [v for *_, v in L]
        a1.plot(x, y, label=n[3:], lw=1.3)
        P = [(int(c['epoch']), int(c['iter']), float(c['value'])) for c in curves if c['name'] == n and c['kind'] in ('test_acc_2k',)]
        a2.plot([(e - 1) * 390 + i for e, i, _ in P], [v for *_, v in P], 'o-', ms=3, lw=1.1, label=n[3:])
    a1.set_xlabel('iteration'); a1.set_ylabel('training loss'); a1.set_yscale('log'); a2.set_xlabel('iteration'); a2.set_ylabel('test accuracy, 2000 images (%)'); a1.legend(frameon=False, fontsize=7); plt.tight_layout(); plt.savefig(os.path.join(a.out, 'fig_convergence.pdf')); plt.close()
# ---------------- adaptive policies: accuracy vs complexity
rows = []
for p in sorted(glob.glob(os.path.join(a.res, '*.macstats.json'))):
    n = os.path.basename(p).replace('.macstats.json', ''); st = json.load(open(p)); tot = sum(st['hist'].values())
    row = {'name': n, 'acc': res.get(n), 'mean_r': sum(int(k.split(':')[1]) * v for k, v in st['hist'].items()) / tot}
    for m, lab in metrics.items():
        c = cost_fn(m); ref = c(13)
        row['rel_' + lab + '_separate'] = sum(v * c(int(k.split(':')[1])) for k, v in st['hist'].items()) / tot / ref
        row['rel_' + lab + '_single'] = c(max(int(k.split(':')[1]) for k in st['hist'])) / ref       # one unit built for the widest r
    rows.append(row)
if rows:
    with open(os.path.join(a.out, 'adaptive_table.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    fig, ax = plt.subplots(figsize=(4.8, 3.2))
    for r in rows:
        if r['acc'] is None: continue
        ax.scatter(r['rel_area_separate'], r['acc'], s=26, color='#1e8449' if r['name'].startswith('ad_') else '#2e6da4'); ax.annotate(r['name'], (r['rel_area_separate'], r['acc']), fontsize=6.5, xytext=(3, 2), textcoords='offset points')
    ax.set_xlabel('relative adder area (eager $r{=}13$ = 1)'); ax.set_ylabel('test accuracy (%)'); plt.tight_layout(); plt.savefig(os.path.join(a.out, 'fig_adaptive_pareto.pdf')); plt.close()
print('written to', a.out)
