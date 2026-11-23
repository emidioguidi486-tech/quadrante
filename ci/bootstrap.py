#!/usr/bin/env python3
"""Punto d'ingresso dell'automazione: decifra la pipeline privata (private.enc) e i dati di riserva (seed.enc)
in una cartella temporanea fuori dal repository e lancia run.py. Nessun dato in chiaro finisce nel repository.
Uso (da GitHub Actions): python3 ci/bootstrap.py --cache <dir> --event <evento> [--mode auto|full|rebuild]"""
import argparse, os, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from qpcrypto import load_key, decrypt, unpack_to
ap = argparse.ArgumentParser(); ap.add_argument('--cache', required=True); ap.add_argument('--event', default='workflow_dispatch')
ap.add_argument('--mode', default='auto'); ap.add_argument('--raw-in')
a = ap.parse_args()
key = load_key()
# collaudo: ci/collaudo.json = {"simula": "SIMBOLO,qs:*", "mode": "full"} (usato solo durante gli stress test)
import json
ctl = os.path.join(HERE, 'collaudo.json')
if os.path.exists(ctl):
    c = json.load(open(ctl))
    if c.get('simula') and not os.environ.get('QP_FAIL'): os.environ['QP_FAIL'] = c['simula']
    if c.get('mode') and a.mode == 'auto': a.mode = c['mode']
    print('[collaudo]', 'simula=' + os.environ.get('QP_FAIL', ''), 'mode=' + a.mode, flush=True)
work = tempfile.mkdtemp(prefix='qp_', dir=os.environ.get('RUNNER_TEMP'))
unpack_to(decrypt(key, open(os.path.join(REPO, 'private.enc'), 'rb').read()), os.path.join(work, 'private'))
seed = os.path.join(work, 'seed'); os.makedirs(seed)
if os.path.exists(os.path.join(REPO, 'seed.enc')):
    import shutil; shutil.copy(os.path.join(REPO, 'seed.enc'), os.path.join(seed, 'raw.enc'))
cmd = [sys.executable, '-I', os.path.join(work, 'private', 'pipeline', 'run.py'), '--repo', REPO, '--cache', os.path.abspath(a.cache),
       '--seed', seed, '--event', a.event, '--mode', a.mode] + (['--raw-in', a.raw_in] if a.raw_in else [])
sys.exit(subprocess.run(cmd).returncode)
