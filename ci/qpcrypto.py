"""Cifratura del Quadrante: AES-256-GCM, formato file = IV(12 byte) || ciphertext+tag.
La chiave (32 byte, base64url senza padding) arriva SOLO da variabile d'ambiente QP_KEY o da file indicato:
non viene mai scritta su disco nel repository né stampata."""
import base64, gzip, io, os, secrets, tarfile

def load_key(keyfile=None):
    raw = os.environ.get('QP_KEY', '').strip()
    if not raw and keyfile:
        raw = open(keyfile).read().strip()
    if not raw:
        raise SystemExit("Manca la chiave: imposta il secret QP_KEY nel repository (Settings → Secrets and variables → Actions).")
    try:
        k = base64.urlsafe_b64decode(raw + '=' * (-len(raw) % 4))
    except Exception:
        raise SystemExit('Chiave QP_KEY non valida (non è base64url).')
    if len(k) != 32:
        raise SystemExit('Chiave QP_KEY non valida (lunghezza %d byte, attesi 32).' % len(k))
    return k

def encrypt(key, data: bytes) -> bytes:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    iv = secrets.token_bytes(12)
    return iv + AESGCM(key).encrypt(iv, data, None)

def decrypt(key, blob: bytes) -> bytes:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.exceptions import InvalidTag
    try:
        return AESGCM(key).decrypt(blob[:12], blob[12:], None)
    except InvalidTag:
        raise SystemExit('Decifratura fallita: la chiave QP_KEY non corrisponde a questi dati.')

def pack_dir(path) -> bytes:
    """tar.gz deterministico (ordine e metadati fissi) di una cartella."""
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode='wb', mtime=0, compresslevel=9) as gz:
        with tarfile.open(fileobj=gz, mode='w', format=tarfile.PAX_FORMAT) as tar:
            for root, dirs, files in os.walk(path):
                dirs[:] = sorted(d for d in dirs if d not in ('__pycache__', 'raw', 'out'))
                for f in sorted(files):
                    full = os.path.join(root, f); rel = os.path.relpath(full, path)
                    ti = tar.gettarinfo(full, rel); ti.mtime = 0; ti.uid = ti.gid = 0; ti.uname = ti.gname = ''
                    with open(full, 'rb') as fh:
                        tar.addfile(ti, fh)
    return buf.getvalue()

def unpack_to(data: bytes, path):
    os.makedirs(path, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as tar:
        for m in tar.getmembers():
            if m.name.startswith('/') or '..' in m.name.split('/') or not (m.isfile() or m.isdir()):
                raise SystemExit('Archivio privato non valido: ' + m.name)
        tar.extractall(path, filter='data') if hasattr(tarfile, 'data_filter') else tar.extractall(path)
