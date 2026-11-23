#!/usr/bin/env python3
"""Apre e richiude i file cifrati del Quadrante (private.enc = pipeline e dati personali; seed.enc = dati di mercato di riserva).
  python3 ci/private_tool.py unpack private.enc <cartella>      → estrae
  python3 ci/private_tool.py pack <cartella> private.enc        → ricifra
  python3 ci/private_tool.py decrypt-json data.enc <file.json>  → decifra i dati del sito (gzip+json)
La chiave si passa con la variabile d'ambiente QP_KEY (oppure --keyfile <file>)."""
import gzip, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qpcrypto import load_key, encrypt, decrypt, pack_dir, unpack_to
args = sys.argv[1:]
kf = None
if '--keyfile' in args:
    i = args.index('--keyfile'); kf = args[i + 1]; del args[i:i + 2]
if len(args) != 3 or args[0] not in ('unpack', 'pack', 'decrypt-json'):
    sys.exit(__doc__)
key = load_key(kf)
cmd, a, b = args
if cmd == 'unpack':
    unpack_to(decrypt(key, open(a, "rb").read()), b); print('estratto in', b)
elif cmd == 'pack':
    open(b, 'wb').write(encrypt(key, pack_dir(a))); print('cifrato', b, os.path.getsize(b), 'byte')
else:
    open(b, 'wb').write(gzip.decompress(decrypt(key, open(a, 'rb').read()))); print('decifrato', b)
