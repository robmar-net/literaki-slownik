"""Fikstury G7: mały przebieg doprowadzony do symulowanego stanu kompletnego.

Pełny build produkcyjny nadal kończy się INCOMPLETE. Te funkcje symulują
wyłącznie mechanikę przyszłych kompletnych etapów, aby sprawdzić verify/export.
Fikstura ma tryb test i nie może uzyskać VERIFIED przez publiczne CLI.
"""
import gzip
import hashlib
import json
import shutil
import sqlite3
from pathlib import Path
from literaki_slownik.build import build
from literaki_slownik.canonical import load_json, write_json, sha256, dumps
from literaki_slownik.database import connect
from literaki_slownik.reports import canonical_index, logical_content_report
from literaki_slownik.run import STAGES, code_identity
from tests.helpers import fixture_manifest, rewrite

ROOT = Path(__file__).resolve().parent.parent
SGJP = ('#</COPYRIGHT>\nkot\tkot\tsubst:sg:nom.acc:m2\t\t\n'
        'kotek\tkotek\tsubst:sg:nom:m2\t\t\n'
        'zamek\tzamek:a\tsubst:sg:nom:m3\t\t\nzamek\tzamek:b\tsubst:sg:nom:m3\t\t\n')
EXPLAIN_CASES = (('accept', 'kot'), ('reject', 'kotek'), ('unresolved', 'zamek'),
                 ('absent', 'pies'), ('reconstruction', 'kot'), ('homonyms', 'zamek'),
                 ('profile_reject', 'k'), ('no_kwjp', 'kotek'))


def pin(directory, name, path):
    return {'path': name, 'sha256': hashlib.sha256((Path(directory) / name).read_bytes()).hexdigest()}


def release_conditions(directory, *, lists_status='DECLARED', known=()):
    """Warunki fikstury; w repo właściciel uzupełnia je jawnie (bez domyślnej licencji)."""
    directory = Path(directory)
    (directory / 'TERMS-CODE.txt').write_text('Warunki kodu fikstury\n', encoding='utf-8')
    (directory / 'TERMS-DOCS.txt').write_text('Warunki dokumentacji fikstury\n', encoding='utf-8')
    (directory / 'PROJECT-ATTRIBUTIONS.md').write_text('# Atrybucje fikstury\n', encoding='utf-8')
    declared = lambda terms, name: {'status': 'DECLARED', 'terms': terms, 'basis': 'fikstura testowa',
                                    'files': [pin(directory, name, None)]}
    lists = (declared('Warunki list fikstury', 'TERMS-DOCS.txt') if lists_status == 'DECLARED'
             else {'status': lists_status, 'terms': None, 'basis': 'czeka na właściciela', 'files': []})
    config = {
        'schema_version': 1, 'kind': 'literaki-release-conditions', 'package_id': 'LL-PL-FIXTURE',
        'conditions': {'code': declared('Warunki kodu fikstury', 'TERMS-CODE.txt'),
                       'documentation': declared('Warunki dokumentacji fikstury', 'TERMS-DOCS.txt'),
                       'lists': lists,
                       'reports': declared('Warunki raportów fikstury', 'TERMS-DOCS.txt'),
                       'database': {'distributed': False, 'status': 'NOT_DISTRIBUTED',
                                    'note': 'Baza pozostaje w archiwum przebiegu.'}},
        'attributions': pin(directory, 'PROJECT-ATTRIBUTIONS.md', None),
        'limitations': ['Fikstura testowa: nie jest wydaniem.'],
        'known_limitations': list(known),
    }
    (directory / 'release.json').write_text(json.dumps(config, ensure_ascii=False), encoding='utf-8')
    return config


def fixture_inputs(directory, **conditions):
    """Manifest test: SGJP, jedna lista KWJP, quality i warunki pakietu."""
    directory = Path(directory)
    path, manifest = fixture_manifest(directory)
    source = directory / 'source.gz'
    with gzip.open(source, 'wt', encoding='utf-8') as stream:
        stream.write(SGJP)
    manifest['artifacts'][0]['sha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
    corpus = directory / 'lemma.csv.gz'
    with gzip.open(corpus, 'wt', encoding='utf-8') as stream:
        stream.write(',,freq,ipm,ARF,DP,DP_norm,1-DP,total_freq\nkot,subst,7,1,1,0,0,1,7\n')
    artifact = dict(manifest['artifacts'][0])
    artifact.update(source_id='corpus', kind='kwjp_lemma', role='corpus_evidence', path=corpus.name,
                    sha256=hashlib.sha256(corpus.read_bytes()).hexdigest(), genre='all',
                    publication_threshold=5)
    manifest['artifacts'].append(artifact)
    for name in ('quality', 'quality-words'):
        shutil.copy(ROOT / 'config/generator' / (name + '.json'), directory / (name + '.json'))
        manifest['configurations'][name] = pin(directory, name + '.json', None)
    release_conditions(directory, **conditions)
    manifest['configurations']['release'] = pin(directory, 'release.json', None)
    rewrite(path, manifest)
    return path


def repin_release(manifest_path, **conditions):
    directory = Path(manifest_path).parent
    release_conditions(directory, **conditions)
    manifest = load_json(manifest_path)
    manifest['configurations']['release'] = pin(directory, 'release.json', None)
    rewrite(Path(manifest_path), manifest)


def complete_run(run, standard_excluded=('kotek',)):
    """Symuluje przyszłe kompletne etapy: członkostwo, listy i raporty bez pending."""
    run = Path(run)
    db = sqlite3.connect(run / 'build.sqlite')
    try:
        db.execute("update variant_decision set membership_status='accept'")
        marks = ','.join('?' * len(standard_excluded))
        if standard_excluded:
            db.execute(f'''update variant_decision set membership_status='reject' where variant='standard'
                and analysis_key in (select analysis_key from analysis where game_key in ({marks}))''',
                       tuple(standard_excluded))
        db.commit()
    finally:
        db.close()
    (run / 'lists').mkdir(exist_ok=True)
    with connect(run / 'build.sqlite', readonly=True) as db:
        for variant in ('broad', 'standard'):
            keys = [r[0] for r in db.execute('''select distinct a.game_key from analysis a
                join variant_decision d on d.analysis_key=a.analysis_key
                where d.variant=? and d.membership_status='accept' order by a.game_key''', (variant,))]
            (run / 'lists' / (variant + '.txt')).write_bytes(''.join(k + '\n' for k in keys).encode('utf-8'))
        logical = logical_content_report(db)
    write_json(run / 'reports/logical-content.json', logical)
    for report in sorted((run / 'reports').glob('*.json')):
        if report.name in {'canonical-index.json', 'logical-content.json', 'performance.json'}:
            continue
        data = load_json(report)
        if not isinstance(data, dict):
            continue
        for key in list(data):
            if key.endswith('_pending') and data[key] is True:
                data[key] = False
        if data.get('status') == 'INCOMPLETE':
            data['status'] = 'COMPLETE'
        if report.name == 'coverage.json':
            data['source_semantic_population_complete'] = True
            for item in data['source_classes'].values():
                item['semantic_qualification'] = 'CLOSED'
        if report.name == 'links.json':
            data['stage_completion'] = {'complete': True, 'blocking': [],
                                        'verification': data['stage_completion']['verification']}
        if report.name == 'unresolved.json':
            data['rules'] = []
            for counts in data['variants'].values():
                counts['analysis_membership']['unresolved'] = 0
                counts['word_membership']['unresolved'] = 0
        write_json(report, data)
    manifest = load_json(run / 'manifest.json')
    for stage in STAGES:
        manifest['stages'][stage] = {'status': 'complete', 'updated': 'fixture'}
    manifest['code'] = {**code_identity(), 'git_commit': 'fixture-commit', 'git_dirty': False}
    write_json(run / 'manifest.json', manifest)
    write_json(run / 'reports/canonical-index.json', canonical_index(run))


def make_review(run, path, *, assessment='correct', blocking=False, drop_item=False):
    from literaki_slownik.explain import explain
    from literaki_slownik.quality import review_template
    run = Path(run)
    index_sha = sha256(run / 'reports/canonical-index.json')
    samples = {}
    for name in ('quality-analyses', 'quality-links', 'quality-words'):
        relative = f'reports/{name}.json'
        sample = load_json(run / relative)
        filled = review_template(sample, canonical_index_sha256=index_sha,
                                 evidence_sha256={relative: sha256(run / relative)})
        filled['status'] = 'REVIEWED'
        for item in filled['items']:
            item.update(assessment=assessment, reviewer='recenzent-testowy',
                        source_justification='SGJP fikstury, wiersz źródłowy',
                        affects_lists_or_links=blocking)
            item.pop('selected_unit', None)
        if drop_item:
            filled['items'] = filled['items'][1:]
            drop_item = False
        samples[relative] = filled
    cases = [{'category': category, 'word': word, 'variant': 'standard',
              'result_sha256': hashlib.sha256(dumps(explain(run, word, 'standard')).encode('utf-8')).hexdigest()}
             for category, word in EXPLAIN_CASES]
    review = {'schema_version': 1, 'kind': 'literaki-quality-review',
              'canonical_index_sha256': index_sha,
              'logical_content_sha256': load_json(run / 'reports/logical-content.json')['sha256'],
              'samples': samples, 'explain_runtime': cases}
    Path(path).write_text(json.dumps(review, ensure_ascii=False), encoding='utf-8')
    return Path(path)


def complete_pair(directory, **conditions):
    """Dwa niezależne przebiegi z tego samego manifestu oraz przegląd."""
    directory = Path(directory)
    inputs = directory / 'inputs'
    inputs.mkdir()
    manifest = fixture_inputs(inputs, **conditions)
    run, peer = directory / 'run-a', directory / 'run-b'
    build(manifest, run)
    build(manifest, peer)
    complete_run(run)
    complete_run(peer)
    review = make_review(run, directory / 'review.json')
    return manifest, run, peer, review


def tree_hashes(root, skip=()):
    root = Path(root)
    return {str(p.relative_to(root)): sha256(p) for p in sorted(root.rglob('*'))
            if p.is_file() and not any(str(p.relative_to(root)).startswith(s) for s in skip)}
