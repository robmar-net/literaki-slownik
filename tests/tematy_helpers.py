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


def config_fixture(root, t3=True):
    """Konfiguracja metody, temat i manifest wejść w `root`; pliki wejść to zaślepki.

    `t3=False`: temat bez `t3` i bez znaczników śródlądowych (W1 #12).
    """
    root = Path(root)
    texts, inputs = root/'tematy-teksty', root/'inputs'
    for p in (texts, inputs, root/'tematy'):
        p.mkdir(parents=True)
    for name in TEXTS:
        # LIMITATIONS ma znacznik, który budowa podmienia na udział śródlądowych (grupa 9).
        marker = 'Udział śródlądowych: @@SRODLADOWE@@.\n' if name == 'LIMITATIONS.md' else ''
        (texts/name).write_text('# Fikstura ' + name + '\n' + marker, encoding='utf-8')
    method = json.loads((CONFIG/'tematy.json').read_text(encoding='utf-8'))
    method['teksty'] = {name: {'path': 'tematy-teksty/' + name, 'sha256': sha256(texts/name)}
                        for name in TEXTS}
    config = root/'tematy.json'
    write_json(config, method)
    topic = root/'tematy/morze.json'
    topic.write_bytes((CONFIG/'tematy/morze.json').read_bytes())
    # Dodatki prawdziwego tematu nie istnieją w fikstury SGJP; testy warstwy D dopisują własne.
    rewrite(topic, lambda v: v.update(dodatki=[]))
    if not t3:
        rewrite(topic, lambda v: (v.pop('t3'), v['diagnostyka'].pop('znaczniki_srodladowe')))
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
# (forma, lemat, tag, kwalifikatory) → baza przebiegu; leksem = lemat (`lemma_id`),
# `lemma_base` = lemat bez sufiksu `:…` (homonimy jak w SGJP: `kuter`, `kuter:S2`).
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
    ('reja', 'reja', 'subst:sg:nom:f', 'daw.|mors.,wojsk.'),  # atom po `|`, potem `,`
    ('fok', 'fok', 'subst:sg:nom:m3', 'mors'),  # bez kropki: nie atom `mors.`
    # Grupa 8: homonim `kuter`, leksem spoza BROAD, leksem tylko T3.
    ('kutrem', 'kuter:S2', 'subst:sg:inst:m3', ''),
    ('kambuz', 'kambuz', 'subst:sg:nom:m3', ''),
    ('barka', 'barka', 'subst:sg:nom:f', ''),
]
NOT_STANDARD = {'szkuta'}  # w BROAD, poza STANDARD
NOT_BROAD = {'kambuz'}  # forma poza BROAD (i STANDARD)
# Konstrukcje (`derivation_candidate`): (forma gry, lemat leksemu składnika); w BROAD i STANDARD.
CONSTRUCTIONS = [('okrętże', 'okręt'), ('kotże', 'kot')]
POP_WORDS, POP0_WORDS, POP00_WORDS = {'kot', 'kotem', 'statek'}, {'kot', 'statek'}, {'kot'}
POP_MEMBERS = {'POP': ['kot@' + SOURCE, 'statek@' + SOURCE], 'POP0': ['kot@' + SOURCE]}
# Słowosieć: korzenie jak w `morze.json`; kierunek PARENT_ID → CHILD_ID.
PLWN = {
    'lexicalunit': [(1, 'statek', 2, 1), (2, 'okręt', 2, 1), (3, 'łódź', 2, 2), (4, 'marynarz', 2, 1),
                    (5, 'żegluga', 2, 1), (6, 'żeglarstwo', 2, 1), (7, 'kuter', 2, 1),
                    (8, 'jednostka', 2, 1), (9, 'szkuta', 2, 1), (10, 'ship', 6, 1),
                    (11, 'kot', 2, 1), (12, 'statek rzeczny', 2, 1),
                    # Grupa 8: `kambuz` w domknięciu, `łódź 1` poza nim, angielska `okręt` (kod 6), `ger`.
                    (13, 'kambuz', 2, 1), (14, 'łódź', 2, 1), (15, 'okręt', 6, 1), (16, 'żeglowanie', 2, 1)],
    'synset': [(7354, 0), (2149, 0), (4511, 0), (6214, 0), (14136, 0), (14515, 0), (900, 0), (901, 1),
               (902, 0), (500, 0), (903, 0), (501, 0)],
    'unitandsynset': [(1, 7354, 0), (10, 7354, 1), (2, 2149, 0), (3, 4511, 0), (4, 6214, 0), (5, 14136, 0),
                      (6, 14515, 0), (7, 900, 0), (12, 900, 1), (8, 901, 0), (9, 902, 0), (11, 500, 0),
                      (13, 903, 0), (14, 501, 0), (15, 500, 1), (16, 14136, 1)],
    'synsetrelation': [(7354, 2149, 11), (7354, 4511, 11), (7354, 900, 11), (7354, 901, 11), (901, 902, 11),
                       (7354, 903, 11)],
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
      <termEntry id="IATE-3">
        <descripGrp>
          <descrip type="subjectField">20, 48</descrip>
        </descripGrp>
        <langSet xml:lang="pl">
          <tig>
            <term>kotwica</term>
            <termNote type="termType">fullForm</termNote>
            <descrip type="reliabilityCode">4</descrip>
          </tig>
        </langSet>
      </termEntry>
      <termEntry id="IATE-4">
        <descripGrp>
          <descrip type="subjectField">1011, 4821</descrip>
        </descripGrp>
        <langSet xml:lang="en">
          <tig>
            <term>keel</term>
            <termNote type="termType">fullForm</termNote>
            <descrip type="reliabilityCode">3</descrip>
          </tig>
        </langSet>
        <langSet xml:lang="pl">
          <tig>
            <term>kil</term>
            <termNote type="termType">fullForm</termNote>
            <descrip type="reliabilityCode">3</descrip>
          </tig>
          <tig>
            <term>kl</term>
            <termNote type="termType">abbreviation</termNote>
            <descrip type="reliabilityCode">3</descrip>
          </tig>
          <tig>
            <term>maszt</term>
            <termNote type="termType">fullForm</termNote>
            <descrip type="reliabilityCode">3</descrip>
            <termNote type="administrativeStatus">supersededTerm-admn-sts</termNote>
          </tig>
          <tig>
            <term>ster</term>
            <termNote type="termType">fullForm</termNote>
            <descrip type="reliabilityCode">2</descrip>
          </tig>
          <tig>
            <term>Bałtyk</term>
            <termNote type="termType">fullForm</termNote>
            <descrip type="reliabilityCode">3</descrip>
          </tig>
          <tig>
            <term>statek rzeczny</term>
            <termNote type="termType">fullForm</termNote>
            <descrip type="reliabilityCode">4</descrip>
          </tig>
          <tig>
            <term>szkuta</term>
            <termNote type="termType">fullForm</termNote>
            <descrip type="reliabilityCode">4</descrip>
          </tig>
        </langSet>
      </termEntry>
      <termEntry id="IATE-5">
        <descripGrp>
          <descrip type="subjectField">4821</descrip>
        </descripGrp>
        <langSet xml:lang="en">
          <tig>
            <term>barge</term>
            <termNote type="termType">fullForm</termNote>
            <descrip type="reliabilityCode">3</descrip>
          </tig>
        </langSet>
        <langSet xml:lang="pl">
          <tig>
            <term>barka</term>
            <termNote type="termType">fullForm</termNote>
            <descrip type="reliabilityCode">3</descrip>
          </tig>
        </langSet>
      </termEntry>
    </body>
  </text>
</martif>
'''


def write_iate(path, text, member='iate.tbx'):
    """Zip IATE z jednym członkiem TBX (stała data, deterministyczny)."""
    import zipfile
    with zipfile.ZipFile(path, 'w') as archive:
        info = zipfile.ZipInfo(member, date_time=(2019, 9, 30, 0, 0, 0))
        archive.writestr(info, text.encode('utf-8'), compress_type=zipfile.ZIP_DEFLATED)


def repin_iate(f):
    """Po podmianie zipa IATE: nowy hash i rozmiar w manifeście wejść."""
    path = f['paths']['iate']
    rewrite(f['manifest'], lambda v: v['inputs']['iate'].update(sha256=sha256(path), bytes=path.stat().st_size))


def _plwordnet_writer():
    import importlib.util
    spec = importlib.util.spec_from_file_location('build_plwordnet_db', ROOT/'scripts/build_plwordnet_db.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def inputs_fixture(root, t3=True):
    """`config_fixture` z prawdziwymi małymi wejściami: przebieg, wydanie, POP, POP00, pochodna, IATE."""
    import hashlib
    import sqlite3
    from contextlib import closing
    from literaki_slownik.pop import write_gzip
    f = config_fixture(root, t3)
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
        db.executemany('insert into lexeme values (?,?,?,?)',
                       [(i, SOURCE, l, l.split(':', 1)[0]) for l, i in ids.items()])
        forms, rows = {}, {}
        for i, (form, lemma, tag, qual) in enumerate(SGJP, 1):
            if form not in forms:
                forms[form] = len(forms) + 1
                db.execute('insert into surface_form values (?,?,?,?,?)', (forms[form], form, form, form, len(form)))
            rows.setdefault(lemma, i)
            db.execute('insert into sgjp_record values (?,?,?,?,?,?,?)', (SOURCE, i, form, lemma, tag, '', qual))
            db.execute('insert into interpretation values (?,?,?,?,?,?,?,?)',
                       (i, SOURCE, i, forms[form], ids[lemma], tag, '', qual))
        for n, (word, lemma) in enumerate(CONSTRUCTIONS, 1):
            db.execute('insert into derivation_candidate values (?,?,?,?,?,?,?,?,?)',
                       (f'c{n}', 'fixture', word, word, lemma, 'subst:sg:nom:m3', '', '', '{}'))
            db.execute('insert into derivation_component values (?,?,?,?,?)',
                       (f'c{n}', 0, 'source_interpretation', SOURCE, rows[lemma]))
        db.commit()
    broad_words = sorted({form for form, _, _, _ in SGJP} - NOT_BROAD | {w for w, _ in CONSTRUCTIONS})
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
    write_iate(iate, TBX)
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


# --- Grupa 10: checker i przegląd R2 (skrypty bez importu pakietu). ---
def load_script(name):
    """Moduł z `scripts/<name>.py` (skrypty nie są pakietem)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, ROOT/'scripts'/(name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def package_fixture(root):
    """`inputs_fixture` i zbudowany pakiet `root/pkg` (wpisy: T1 4, T2 4, T3 1)."""
    from literaki_slownik.tematy import build_package
    f = inputs_fixture(root)
    package = Path(f['root'])/'pkg'
    build_package(f['manifest'], f['config'], f['topic'], package)
    return {**f, 'package': package}


def reseal(package):
    """Po zmianie pliku pakietu: nowe hashe w manifeście i SHA256SUMS (fałszerz z pełnym dostępem)."""
    package = Path(package)
    manifest = package/'release-manifest.json'
    for p in (manifest, package/'SHA256SUMS'):
        p.chmod(0o644)
    rewrite(manifest, lambda m: m.update(files={n: {'sha256': sha256(package/n), 'bytes': (package/n).stat().st_size}
                                                for n in m['files']}))
    (package/'SHA256SUMS').write_text(''.join(f'{sha256(p)}  {p.relative_to(package).as_posix()}\n'
                                              for p in sorted(package.rglob('*'))
                                              if p.is_file() and p.name != 'SHA256SUMS'), encoding='utf-8')
    for p in (manifest, package/'SHA256SUMS'):
        p.chmod(0o444)
