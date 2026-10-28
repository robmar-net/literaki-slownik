#!/usr/bin/env python3
"""Pobranie źródeł TEMATY (#11, W1): IATE 2019 i Słowosieć 4.5, z rekordem pochodzenia.

Użycie:
  python3 scripts/fetch_tematy_sources.py iate [--target cache/iate/IATE_download.zip]
  python3 scripts/fetch_tematy_sources.py plwordnet [--target cache/plwordnet/wordnet_work_4_5.zip]

`curl -fL` pisze do pliku tymczasowego w katalogu celu. Skrypt liczy SHA-256 i bajty, potem
przenosi plik bez nadpisania (`link` + `unlink`). Na stdout wypisuje rekord JSON: `url`,
`retrieved_at` (UTC), `sha256`, `bytes`, `path`; dla IATE także `last_modified` (nagłówek)
i `member` (plik `.tbx` w zipie). Zip Słowosieci musi mieć przypięty hash.
Pobranych plików nie wykonujemy; zip IATE tylko listujemy. Kody: 1 błąd pobrania lub hasha.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

IATE_URL = 'https://iate.europa.eu/em-api/artifacts/full-tbx'
PLWORDNET_URL = 'https://clarin-pl.eu/server/api/core/bitstreams/3197cd0f-bb4e-41ba-93e0-eec99ab8d519/content'
PLWORDNET_SHA256 = '30edc5f85c06408d372a897f1d1ff3d03fa939b8680b176c1f97351f4a72dcbc'
SOURCES = {
    'iate': dict(url=IATE_URL, target='cache/iate/IATE_download.zip', iate=True, expected_sha256=None),
    'plwordnet': dict(url=PLWORDNET_URL, target='cache/plwordnet/wordnet_work_4_5.zip', iate=False,
                      expected_sha256=PLWORDNET_SHA256),
}


class FetchError(Exception):
    pass


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as handle:
        for block in iter(lambda: handle.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def last_header(headers_text, name):
    """Wartość nagłówka z ostatniej odpowiedzi (po przekierowaniach `-L`)."""
    value = None
    for line in headers_text.splitlines():
        if line.startswith('HTTP/'):
            value = None
        key, sep, rest = line.partition(':')
        if sep and key.strip().lower() == name.lower():
            value = rest.strip()
    return value


def tbx_member(path):
    with zipfile.ZipFile(path) as archive:
        members = sorted(n for n in archive.namelist() if n.lower().endswith('.tbx'))
    if len(members) != 1:
        raise FetchError(f'zip IATE: oczekiwany jeden plik .tbx, jest {len(members)}')
    return members[0]


def fetch(url, target, expected_sha256=None, iate=False):
    target = Path(target)
    if target.exists():
        raise FetchError(f'cel istnieje, nie nadpisuję: {target}')
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=target.parent, prefix='.fetch-', suffix='.part')
    os.close(fd)
    headers_name = tmp_name + '.headers'
    tmp = Path(tmp_name)
    try:
        retrieved_at = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        result = subprocess.run(['curl', '-fsSL', '--retry', '3', '-D', headers_name, '-o', tmp_name, url],
                                stdin=subprocess.DEVNULL, capture_output=True, text=True)
        if result.returncode != 0:
            raise FetchError(f'curl {result.returncode}: {result.stderr.strip()}')
        headers = Path(headers_name).read_text(encoding='latin-1') if os.path.exists(headers_name) else ''
        digest = sha256_file(tmp)
        if expected_sha256 is not None and digest != expected_sha256:
            raise FetchError(f'SHA-256 {digest} różny od przypiętego {expected_sha256}')
        record = dict(url=url, retrieved_at=retrieved_at, sha256=digest, bytes=tmp.stat().st_size, path=str(target))
        if iate:
            record['last_modified'] = last_header(headers, 'Last-Modified')
            if not record['last_modified']:
                raise FetchError('brak nagłówka Last-Modified')
            record['member'] = tbx_member(tmp)
        try:
            os.link(tmp, target)  # atomowo i bez nadpisania
        except FileExistsError:
            raise FetchError(f'cel powstał w trakcie, nie nadpisuję: {target}') from None
        return record
    finally:
        for leftover in (tmp_name, headers_name):
            try:
                os.unlink(leftover)
            except FileNotFoundError:
                pass


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('source', choices=sorted(SOURCES))
    parser.add_argument('--target')
    args = parser.parse_args(argv)
    spec = SOURCES[args.source]
    try:
        record = fetch(spec['url'], args.target or spec['target'], spec['expected_sha256'], spec['iate'])
    except (FetchError, OSError, zipfile.BadZipFile) as error:
        print(f'błąd: {error}', file=sys.stderr)
        return 1
    print(json.dumps(record, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == '__main__':
    sys.exit(main())
