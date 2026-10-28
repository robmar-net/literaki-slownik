"""Mała fikstura TEMATY: własne kopie konfiguracji i hashe fikstury, bez prawdziwych pinów."""
import json
import os
from pathlib import Path
from literaki_slownik.canonical import sha256, write_json

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT/'config/generator'
TEXTS = ('ATTRIBUTIONS-tematy.md', 'LIMITATIONS.md', 'TERMS.md')
PATH_INPUTS = ('base_run', 'database', 'release_manifest', 'standard', 'broad',
               'base_pop', 'base_pop00', 'plwordnet_db', 'iate')


def config_fixture(root):
    """Konfiguracja metody, temat i manifest wejść w `root`; pliki wejść to zaślepki."""
    root = Path(root)
    texts, inputs = root/'tematy-teksty', root/'inputs'
    for p in (texts, inputs, root/'tematy'):
        p.mkdir(parents=True)
    for name in TEXTS:
        (texts/name).write_text('# Fikstura ' + name + '\n', encoding='utf-8')
    method = json.loads((CONFIG/'tematy.json').read_text(encoding='utf-8'))
    method['teksty'] = {name: {'path': 'tematy-teksty/' + name, 'sha256': sha256(texts/name)}
                        for name in TEXTS}
    config = root/'tematy.json'
    write_json(config, method)
    topic = root/'tematy/morze.json'
    topic.write_bytes((CONFIG/'tematy/morze.json').read_bytes())
    refs = {}
    for key in PATH_INPUTS:
        path = inputs/(key + '.bin')
        path.write_bytes(key.encode() + b'\n')
        refs[key] = {'path': os.path.relpath(path, root), 'sha256': sha256(path)}
    refs['plwordnet_zip'] = {'url': 'https://example.invalid/plwn.zip', 'retrieved_at': '2026-10-28T00:00:00Z',
                             'bytes': 1, 'sha256': '0' * 64}
    refs['iate'].update({'url': 'https://example.invalid/iate.zip', 'retrieved_at': '2026-10-28T00:00:00Z',
                         'last_modified': 'Mon, 30 Sep 2019 07:41:10 GMT', 'member': 'iate.tbx', 'bytes': 5})
    manifest = root/'tematy-sources.json'
    write_json(manifest, {'schema_version': 1, 'version': 'tematy-sources-v1', 'inputs': refs})
    return {'root': root, 'config': config, 'topic': topic, 'manifest': manifest, 'texts': texts}


def rewrite(path, change):
    """Wczytaj JSON, zmień go funkcją `change` i zapisz kanonicznie."""
    path = Path(path)
    value = json.loads(path.read_text(encoding='utf-8'))
    change(value)
    write_json(path, value)


# --- Grupa 6: prawdziwe (małe) wejścia. Grupy 7–10 dopisują wiersze do stałych poniżej. ---
SOURCE = 'sgjp'
# (forma, lemat, tag, kwalifikatory) → baza przebiegu; leksem = lemat.
SGJP = [
    ('statek', 'statek', 'subst:sg:nom:m3', ''), ('statkiem', 'statek', 'subst:sg:inst:m3', ''),
    ('łódź', 'łódź', 'subst:sg:nom:f', ''), ('łodzią', 'łódź', 'subst:sg:inst:f', ''),
    ('okręt', 'okręt', 'subst:sg:nom:m3', ''),
    ('kuter', 'kuter', 'subst:sg:nom:m3', 'ryb.'),
    ('bosman', 'bosman', 'subst:sg:nom:m1', 'mors.|pot.'),
    ('żeglować', 'żeglować', 'inf:imperf', 'żegl.,przen.'),
    ('żeglowanie', 'żeglować', 'ger:sg:nom:n:imperf:aff', ''),
    ('szkuta', 'szkuta', 'subst:sg:nom:f', ''),
    ('kot', 'kot', 'subst:sg:nom:m2', ''), ('kotem', 'kot', 'subst:sg:inst:m2', ''),
]
NOT_STANDARD = {'szkuta'}  # w BROAD, poza STANDARD
POP_WORDS, POP0_WORDS, POP00_WORDS = {'kot', 'kotem', 'statek'}, {'kot', 'statek'}, {'kot'}
POP_MEMBERS = {'POP': ['kot@' + SOURCE, 'statek@' + SOURCE], 'POP0': ['kot@' + SOURCE]}
# Słowosieć: korzenie jak w `morze.json`; kierunek PARENT_ID → CHILD_ID.
PLWN = {
    'lexicalunit': [(1, 'statek', 2, 1), (2, 'okręt', 2, 1), (3, 'łódź', 2, 2), (4, 'marynarz', 2, 1),
                    (5, 'żegluga', 2, 1), (6, 'żeglarstwo', 2, 1), (7, 'kuter', 2, 1),
                    (8, 'jednostka pływająca', 2, 1), (9, 'szkuta', 2, 1), (10, 'ship', 6, 1),
                    (11, 'kot', 2, 1)],
    'synset': [(7354, 0), (2149, 0), (4511, 0), (6214, 0), (14136, 0), (14515, 0), (900, 0), (901, 1),
               (902, 0), (500, 0)],
    'unitandsynset': [(1, 7354, 0), (10, 7354, 1), (2, 2149, 0), (3, 4511, 0), (4, 6214, 0), (5, 14136, 0),
                      (6, 14515, 0), (7, 900, 0), (8, 901, 0), (9, 902, 0), (11, 500, 0)],
    'synsetrelation': [(7354, 2149, 11), (7354, 4511, 11), (7354, 900, 11), (7354, 901, 11), (901, 902, 11)],
    'relationtype': [(11, 'hiperonimia'), (25, 'część'), (27, 'miejsce')],
}
TBX = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE martif SYSTEM "TBXcoreStructV02.dtd">
<martif type="TBX-Default" xml:lang="en">
  <text>
    <body>
      <termEntry id="IATE-1">
        <descripGrp>
          <descrip type="subjectField">4821, 2846</descrip>
        </descripGrp>
        <langSet xml:lang="en">
          <tig>
            <term>inland waterway vessel</term>
            <termNote type="termType">fullForm</termNote>
            <descrip type="reliabilityCode">3</descrip>
          </tig>
        </langSet>
        <langSet xml:lang="pl">
          <tig>
            <term>szkuta</term>
            <termNote type="termType">fullForm</termNote>
            <descrip type="reliabilityCode">3</descrip>
          </tig>
          <tig>
            <term>bosman</term>
            <termNote type="termType">fullForm</termNote>
            <descrip type="reliabilityCode">3</descrip>
            <termNote type="administrativeStatus">deprecatedTerm-admn-sts</termNote>
          </tig>
        </langSet>
      </termEntry>
      <termEntry id="IATE-2">
        <descripGrp>
          <descrip type="subjectField">48</descrip>
        </descripGrp>
        <langSet xml:lang="pl">
          <tig>
            <term>kot</term>
            <termNote type="termType">fullForm</termNote>
            <descrip type="reliabilityCode">4</descrip>
          </tig>
        </langSet>
      </termEntry>
    </body>
  </text>
</martif>
'''


def _plwordnet_writer():
    import importlib.util
    spec = importlib.util.spec_from_file_location('build_plwordnet_db', ROOT/'scripts/build_plwordnet_db.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def inputs_fixture(root):
    """`config_fixture` z prawdziwymi małymi wejściami: przebieg, wydanie, POP, POP00, pochodna, IATE."""
    import hashlib
    import sqlite3
    import zipfile
    from contextlib import closing
    from literaki_slownik.pop import write_gzip
    f = config_fixture(root)
    root = f['root']
    run, release, pop, pop00, cache = (root/n for n in ('run', 'release', 'pop', 'pop00', 'cache'))
    for p in (run/'lists', release, pop/'reports', pop00, cache):
        p.mkdir(parents=True)
    database = run/'build.sqlite'
    lemmas = sorted({lemma for _, lemma, _, _ in SGJP})
    with closing(sqlite3.connect(database)) as db:
        db.executescript((ROOT/'literaki_slownik/schema.sql').read_text(encoding='utf-8'))
        db.execute('insert into source_artifact values (?,?,?)', (SOURCE, 'sgjp_tab', '{}'))
        ids = {lemma: i for i, lemma in enumerate(lemmas, 1)}
        db.executemany('insert into lexeme values (?,?,?,?)', [(i, SOURCE, l, l) for l, i in ids.items()])
        for i, (form, lemma, tag, qual) in enumerate(SGJP, 1):
            db.execute('insert into surface_form values (?,?,?,?,?)', (i, form, form, form, len(form)))
            db.execute('insert into sgjp_record values (?,?,?,?,?,?,?)', (SOURCE, i, form, lemma, tag, '', qual))
            db.execute('insert into interpretation values (?,?,?,?,?,?,?,?)',
                       (i, SOURCE, i, i, ids[lemma], tag, '', qual))
        db.commit()
    broad_words = sorted({form for form, _, _, _ in SGJP})
    broad, standard = run/'lists/broad.txt', run/'lists/standard.txt'
    broad.write_text(''.join(w + '\n' for w in broad_words), encoding='utf-8')
    standard.write_text(''.join(w + '\n' for w in broad_words if w not in NOT_STANDARD), encoding='utf-8')
    db_sha, standard_sha = sha256(database), sha256(standard)
    release_manifest = release/'release-manifest.json'
    write_json(release_manifest, {'kind': 'literaki-release-manifest', 'package_id': 'LL-PL', 'status': 'FROZEN',
                                  'files': {'LL-PL-BROAD.txt': {'sha256': sha256(broad)},
                                            'LL-PL-STANDARD.txt': {'sha256': standard_sha}}})
    release_sha = sha256(release_manifest)
    write_json(run/'manifest.json', {'readiness': 'FROZEN', 'verification': {'database_sha256': db_sha},
                                     'export': {'release_manifest_sha256': release_sha}})
    write_gzip(pop/'POP.txt.gz', sorted(POP_WORDS))
    write_gzip(pop/'POP0.txt.gz', sorted(POP0_WORDS))
    write_json(pop/'reports/units.json', {'units': [{'members_in': {k: sorted(v) for k, v in POP_MEMBERS.items()}}]})
    (pop/'ATTRIBUTIONS.md').write_text('# Atrybucje POP (fikstura)\n\nSGJP: BSD-2.\n', encoding='utf-8')
    pop_files = ('POP.txt.gz', 'POP0.txt.gz', 'reports/units.json', 'ATTRIBUTIONS.md')
    write_json(pop/'release-manifest.json', {
        'kind': 'literaki-pop-manifest', 'method': 'pop-v3', 'package_id': 'POP', 'status': 'BUILT',
        'inputs': {'database_sha256': db_sha, 'standard_sha256': standard_sha, 'release_manifest_sha256': release_sha},
        'files': {n: {'sha256': sha256(pop/n)} for n in pop_files}})
    write_gzip(pop00/'POP00.txt.gz', sorted(POP00_WORDS))
    write_json(pop00/'release-manifest.json', {
        'kind': 'literaki-pop00-manifest', 'method': 'pop00-v1', 'package_id': 'POP00', 'status': 'BUILT',
        'inputs': {'base_pop': sha256(pop/'release-manifest.json'), 'base_run': sha256(run/'manifest.json'),
                   'database': db_sha, 'standard': standard_sha, 'orth': '0' * 64},
        'files': {'POP00.txt.gz': {'sha256': sha256(pop00/'POP00.txt.gz')}}})
    zip_sha = hashlib.sha256(b'plwordnet-fixture').hexdigest()
    plwn = cache/'plwn-tematy.sqlite'
    _plwordnet_writer().write_db(str(plwn), {t: list(r) for t, r in PLWN.items()},
                                 {'script_version': 'plwn-tematy-v1', 'zip_member': 'plwn.sql', 'zip_sha256': zip_sha})
    iate = cache/'iate.zip'
    with zipfile.ZipFile(iate, 'w') as archive:
        info = zipfile.ZipInfo('iate.tbx', date_time=(2019, 9, 30, 0, 0, 0))
        archive.writestr(info, TBX.encode('utf-8'), compress_type=zipfile.ZIP_DEFLATED)
    paths = {'base_run': run/'manifest.json', 'database': database, 'release_manifest': release_manifest,
             'standard': standard, 'broad': broad, 'base_pop': pop/'release-manifest.json',
             'base_pop00': pop00/'release-manifest.json', 'plwordnet_db': plwn, 'iate': iate}

    def change(value):
        refs = value['inputs']
        for key, path in paths.items():
            refs[key].update(path=os.path.relpath(path, root), sha256=sha256(path))
        refs['plwordnet_zip']['sha256'] = zip_sha
        refs['iate']['bytes'] = iate.stat().st_size
    rewrite(f['manifest'], change)
    return {**f, 'run': run, 'release': release, 'pop': pop, 'pop00': pop00, 'paths': paths,
            'pop_files': pop_files, 'zip_sha256': zip_sha}
