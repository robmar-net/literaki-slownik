"""Fikstura POP: zamrożony przebieg i pakiet LL-PL z własnym SGJP, KWJP i małym 1grams.gz.

SGJP i KWJP są tu osobne od `release_helpers.SGJP`, więc testy LL-PL się nie zmieniają.
"""
import gzip
import hashlib
import json
import os
from pathlib import Path
from literaki_slownik.build import build
from literaki_slownik.canonical import load_json, sha256
from literaki_slownik.export import export
from literaki_slownik.verify import verify
from tests.helpers import rewrite
from tests.release_helpers import SGJP, complete_run, fixture_inputs, make_review

# kot/kotek/zamek zostają dla przypadków explain z przeglądu fikstury LL-PL.
POP_SGJP = SGJP + (
    'rok\trok:S1\tsubst:sg:nom.acc:m3\t\t\n'
    'lata\trok:S1\tsubst:pl:nom.acc:m3\t\t\n'
    'rok\trok:S2\tsubst:sg:nom.acc:m3\t\t\n'
    'lato\tlato\tsubst:sg:nom.acc:n\t\t\n'
    'lata\tlato\tsubst:pl:nom.acc:n\t\t\n'
    'Polska\tPolska\tsubst:sg:nom:f\tnazwa_geograficzna\t\n'
    'polska\tpolski\tadj:sg:nom:f:pos\t\t\n'
    'polski\tpolski\tadj:sg:nom:m3:pos\t\t\n'
    'fajny\tfajny\tadj:sg:nom:m3:pos\t\tpot.\n'
    'duży\tduży\tadj:sg:nom:m3:pos\t\t\n'
    'ul\tul\tsubst:sg:nom.acc:m3\t\t\n'
    'boi\tbać\tfin:sg:ter:imperf\t\t\n'
    'bał\tbać\tpraet:sg:m1.m2.m3:imperf\t\t\n'
    'bojąc\tbać\tpcon:imperf\t\t\n'
    'kumpel\tkumpel\tsubst:sg:nom:m1\t\t\n'
    'kumple\tkumpel\tsubst:pl:nom:m1\t\tpot.\n'
)
POP_KWJP = (',,freq,ipm,ARF,DP,DP_norm,1-DP,total_freq\n'
            'kot,subst,7,1,1,0,0,1,7\n'
            'zamek,subst,30,3,3,0.2,0.2,0.8,30\n'
            'rok,subst,90,9,8,0.1,0.1,0.9,90\n'
            'lato,subst,20,2,2,0.3,0.3,0.7,20\n'
            'Polska,subst,60,6,5,0.2,0.2,0.8,60\n'
            'polski,adj,50,5,4,0.2,0.2,0.8,50\n'
            'fajny,adj,12,1,1,0.4,0.4,0.6,12\n'
            'duży,adj,40,4,4,0.1,0.1,0.9,40\n'
            'ul,subst,6,1,1,0.5,0.5,0.5,6\n'
            # Trzy wiersze jednego leksemu: max F = 30 dwa razy, remis rozstrzyga numer wiersza (fin).
            'bać,pcon,10,1,1,0.5,0.5,0.5,10\n'
            'bać,fin,30,3,3,0.2,0.2,0.8,30\n'
            'bać,praet,30,3,2.5,0.3,0.3,0.7,30\n'
            'kwiat,subst,8,1,1,0.4,0.4,0.6,8\n')
# Listy gatunków: obecność wiersza (lemat, POS); F gatunku nigdy nie trafia do sumy.
POP_KWJP_GENRES = {
    'fakt': ',,freq,ipm,ARF,DP,DP_norm,1-DP,total_freq\nbać,fin,10,1,1,0.3,0.3,0.7,10\n',
    'fikcja': (',,freq,ipm,ARF,DP,DP_norm,1-DP,total_freq\nbać,fin,12,1,1,0.3,0.3,0.7,12\n'
               'rok,subst,40,4,4,0.1,0.1,0.9,40\n'),
    'publicystyka': (',,freq,ipm,ARF,DP,DP_norm,1-DP,total_freq\nbać,praet,9,1,1,0.3,0.3,0.7,9\n'
                     'kot,subst,5,1,1,0.5,0.5,0.5,5\n'),
}
# Format NKJP: ' *liczba napis\n' (wzór scripts/audit_nkjp.py).
NKJP_1GRAMS = ('     50 ul.\n     10 ul\n     30 ok.\n     40 polska\n     15 Polska\n'
               '     25 lata\n     20 rok\n      8 duży\n      1 fajny\n')
# NKJP polecenia `pop`: liczby o rzadkich ciągach cyfr, żeby skan pakietu (C14) wykrył każdy wyciek.
# `ul.` ma dużą liczbę: gdyby skleił się z `ul`, `ul` byłoby pierwsze w NKJP. `polska` dzieli nazwa własna.
NKJP_POP_1GRAMS = ('  7340919 kot\n  6182537 polski\n  5093746 lata\n  4718293 Polska\n      317 polska\n'
                   '  9182736 ul.\n       12 ul\n  2837465 duży\n       41 fajny\n')


def gz_write(path, text):
    """Gzip bez nazwy i czasu, żeby hash fikstury był stały."""
    with open(path, 'wb') as raw, gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as stream:
        stream.write(text.encode('utf-8'))
    return Path(path)


def write_pop_sources(path, run, release, nkjp, *, database_sha256=None, release_manifest_sha256=None,
                      standard_sha256=None, nkjp_sha256=None):
    """Manifest POP przypięty do fikstury; nadpisania służą testom złych pinów."""
    path, run, release, nkjp = Path(path), Path(run), Path(release), Path(nkjp)
    rel = lambda target: os.path.relpath(Path(target).resolve(), path.parent.resolve())
    lemma = {genre: source for source, genre in kwjp_lemma_sources(run).items()}
    manifest = {
        'schema_version': 1, 'project': 'literaki-slownik', 'version': 'pop-sources-v1',
        'base': {'package_id': 'LL-PL', 'run_dir': rel(run), 'release_dir': rel(release),
                 'database_sha256': database_sha256 or sha256(run / 'build.sqlite'),
                 'release_manifest_sha256': release_manifest_sha256 or sha256(release / 'release-manifest.json'),
                 'standard_sha256': standard_sha256 or sha256(run / 'lists/standard.txt')},
        'inputs': [
            {'source_id': 'kwjp', 'kind': 'kwjp', 'origin': 'database', 'lemma_sources': lemma,
             'used_for': 'POP: miara użycia leksemu (fikstura)'},
            {'source_id': 'nkjp-1grams', 'kind': 'nkjp_1gram', 'path': rel(nkjp),
             'sha256': nkjp_sha256 or sha256(nkjp), 'title': 'fikstura 1grams',
             'creator': 'projekt (fikstura)', 'url': 'synthetic:own', 'license': 'własna fikstura',
             'used_for': 'POP: ranga leksemu (fikstura)'},
        ],
    }
    path.write_text(json.dumps(manifest, ensure_ascii=False), encoding='utf-8')
    return path


def kwjp_lemma_sources(run):
    """source_id list lemma KWJP z manifestu przebiegu → gatunek."""
    artifacts = load_json(Path(run) / 'manifest.json')['inputs']['artifacts']
    return {a['source_id']: a['genre'] for a in artifacts if a['kind'] == 'kwjp_lemma'}


def pop_config(directory, pop, pop0, **changes):
    """`pop.json` z repo z małymi progami fikstury; `changes` nadpisuje klucze najwyższego poziomu."""
    config = load_json(Path(__file__).resolve().parent.parent / 'config/generator/pop.json')
    config['d6'] = {'pop': {'by': 'count', 'value': pop}, 'pop0': {'by': 'count', 'value': pop0}}
    config.update(changes)
    path = Path(directory) / 'pop.json'
    path.write_text(json.dumps(config, ensure_ascii=False), encoding='utf-8')
    return path


def pop_fixture(directory, nkjp_text=NKJP_1GRAMS):
    """Przebieg FROZEN, pakiet LL-PL, 1grams.gz i pop-sources.json fikstury."""
    directory = Path(directory)
    directory.mkdir(parents=True)
    inputs = directory / 'inputs'
    inputs.mkdir()
    manifest_path = fixture_inputs(inputs, sgjp=POP_SGJP)
    corpus = gz_write(inputs / 'lemma.csv.gz', POP_KWJP)
    manifest = load_json(manifest_path)
    for artifact in manifest['artifacts']:
        if artifact['source_id'] == 'corpus':
            artifact['sha256'] = hashlib.sha256(corpus.read_bytes()).hexdigest()
            base = dict(artifact)
    for genre, text in POP_KWJP_GENRES.items():
        path = gz_write(inputs / f'lemma-{genre}.csv.gz', text)
        manifest['artifacts'].append(dict(base, source_id=f'corpus-{genre}', genre=genre, path=path.name,
                                          sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    rewrite(manifest_path, manifest)
    run, peer = directory / 'run-a', directory / 'run-b'
    build(manifest_path, run)
    build(manifest_path, peer)
    complete_run(run)
    complete_run(peer)
    review = make_review(run, directory / 'review.json')
    report = verify(run, peer, review, allow_test_fixture=True)
    if report['verdict'] != 'VERIFIED':
        raise AssertionError(f'Fikstura POP nie przeszła verify: {report}')
    release = directory / 'release'
    export(run, release, allow_test_fixture=True)
    nkjp = gz_write(directory / '1grams.gz', nkjp_text)
    sources = write_pop_sources(directory / 'pop-sources.json', run, release, nkjp)
    return {'directory': directory, 'run': run, 'release': release, 'nkjp': nkjp,
            'sources': sources, 'database': run / 'build.sqlite'}


def pop_package(directory, name='package', pop=9, pop0=6, **changes):
    """Pakiet POP fikstury (C11) dla grup 13–14: przebieg, LL-PL, NKJP z rzadkimi liczbami i `pop.json`.

    Progi 9/6 jak w `PopBuildTests`; `changes` nadpisuje klucze `pop.json` (np. wycofanie NKJP).
    """
    from literaki_slownik.pop import build_package
    directory = Path(directory)
    fixture = pop_fixture(directory / 'pop', NKJP_POP_1GRAMS)
    config = pop_config(directory, pop, pop0, **changes)
    package = directory / name
    summary = build_package(fixture['sources'], config, package)
    return {**fixture, 'config': config, 'package': package, 'summary': summary}
