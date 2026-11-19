"""Runs the experiments of suite.py on all visible GPUs (one process per GPU), skipping experiments that already finished.
  python run_queue.py --group sweep --init W.pt --out /kaggle/working/ext [--data DIR] [--dry]
Results: <out>/results.csv (final accuracies), <out>/curves.csv (loss / accuracy curves), <out>/logs/<name>.txt, <out>/<name>.macstats.json.
Interrupted runs resume from <out>/ckpt/<name>.pt when the command is started again."""
import argparse, csv, os, subprocess, sys, time
import suite
ap = argparse.ArgumentParser()
ap.add_argument('--group', required=True, help="group name from suite.py, or several separated by commas")
ap.add_argument('--init', default=suite.INIT); ap.add_argument('--out', default='../results_ext'); ap.add_argument('--data', default='./data')
ap.add_argument('--eval-points', type=int, default=3); ap.add_argument('--gpus', type=int, default=0); ap.add_argument('--dry', action='store_true')
ap.add_argument('--seed', type=int, default=0)
a = ap.parse_args()
out = os.path.abspath(a.out); os.makedirs(os.path.join(out, 'logs'), exist_ok=True); os.makedirs(os.path.join(out, 'ckpt'), exist_ok=True)
try:
    import torch; ngpu = a.gpus or max(1, torch.cuda.device_count())
except Exception: ngpu = max(1, a.gpus)
done = set()
res = os.path.join(out, 'results.csv')
if os.path.exists(res): done = {r['name'] for r in csv.DictReader(open(res))}
jobs = [(n, args) for g in a.group.split(',') for n, args in suite.SUITE[g] if n not in done]
print(f"{len(jobs)} experiments to run on {ngpu} GPU(s); {len(done)} already finished", flush=True)
running = {}
def launch(gpu, name, args):
    cmd = [sys.executable, '-u', 'train.py', *args.split(), '--name', name, '--init', a.init, '--data', a.data, '--seed', str(a.seed),
           '--ckpt', os.path.join(out, 'ckpt', name + '.pt'), '--log', res, '--curve', os.path.join(out, 'curves.csv'),
           '--eval-points', str(a.eval_points), '--log-every', '20']
    print(f"[GPU {gpu}] {name}: {' '.join(cmd)}", flush=True)
    if a.dry: return None
    env = dict(os.environ, CUDA_VISIBLE_DEVICES=str(gpu))
    return subprocess.Popen(cmd, env=env, stdout=open(os.path.join(out, 'logs', name + '.txt'), 'a'), stderr=subprocess.STDOUT)
queue = list(jobs)
if a.dry:
    for i, (n, args) in enumerate(queue): launch(i % ngpu, n, args)
    sys.exit(0)
while queue or running:
    for gpu in range(ngpu):
        if gpu in running and running[gpu][1].poll() is not None:
            print(f"[GPU {gpu}] {running[gpu][0]} finished (exit {running[gpu][1].returncode})", flush=True); del running[gpu]
        if gpu not in running and queue:
            n, args = queue.pop(0); running[gpu] = (n, launch(gpu, n, args))
    time.sleep(20)
print("all done", flush=True)
