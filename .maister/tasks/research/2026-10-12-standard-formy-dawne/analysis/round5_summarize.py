"""Łączy zamrożone oceny dopiero po zakończeniu ślepego przeglądu."""
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

TASK = Path(__file__).resolve().parents[1]
OUT = TASK / 'analysis/findings/round5'
ROOT = TASK.parents[3]


def read(name):
    return json.loads((OUT / name).read_text())


def sha(name):
    return hashlib.sha256((OUT / name).read_bytes()).hexdigest()


def contexts(case):
    return case['kwjp_live']['contexts'] if 'kwjp_live' in case else case['read_contexts']


def main():
    lanes = [read(f'quality-{lane}.json') for lane in ('a', 'b')]
    cases = [c for lane in lanes for c in lane['cases']]
    memberships = {c['id']: c for c in read('sample-membership.json')['cases']}
    blind = {c['id']: c for c in read('sample-blind.json')['cases']}
    raw = {c['id']: c for c in json.loads((ROOT / 'tmp/research-issue4/round5/contexts-raw.json').read_text())}
    assert len(cases) == len({c['id'] for c in cases}) == 300
    assert {c['id'] for c in cases} == set(blind) == set(memberships) == set(raw)
    strata = defaultdict(list)
    docids, sentences, case_sentences = set(), set(), set()
    for c in cases:
        assert c['lemma'] == blind[c['id']]['lemma'] == memberships[c['id']]['lemma']
        assert c['class'] in ('ogólne', 'ograniczone', 'marginalne', 'błędne_dopasowanie', 'niepewne')
        assert c.get('rationale', c.get('reason')) and c['confidence']
        rows = raw[c['id']]['rows']
        for item in contexts(c):
            idx = item.get('row_index', item.get('hit_index_zero_based'))
            r = rows[idx]
            assert (r['document_id'], r['sentence']) == (item['document_id'], item['sentence'])
            docids.add(item['document_id'])
            sentences.add((item['document_id'], item['sentence']))
            case_sentences.add((c['id'], item['document_id'], item['sentence']))
        strata[memberships[c['id']]['stratum']].append(c)

    def summarize(group):
        return {'n': len(group), 'classes': dict(Counter(c['class'] for c in group)),
                'confidence': dict(Counter(c['confidence'] for c in group)),
                'zero_live': sum(not raw[c['id']]['rows'] for c in group),
                'general_with_read_context': [c['lemma'] for c in group if c['class'] == 'ogólne' and contexts(c)],
                'general_without_read_context': [c['lemma'] for c in group if c['class'] == 'ogólne' and not contexts(c)]}

    summary = {'assessment_scope': 'Opis rejestru i zgodności dowodu; nie znajomość graczy, nie decyzje o przyjęciu.',
               'source_hashes': {n: sha(n) for n in ('quality-a.json', 'quality-b.json', 'quality-crosscheck.json', 'sample-membership.json')},
               'all_cases': summarize(cases), 'strata': {s: summarize(group) for s, group in sorted(strata.items())},
               'contexts': {'queries': len(raw), 'returned': sum(len(c['rows']) for c in raw.values()),
                            'read_case_contexts': sum(len(contexts(c)) for c in cases),
                            'unique_case_sentences': len(case_sentences), 'distinct_documents': len(docids),
                            'distinct_document_sentences': len(sentences)},
               'variant_sample_counts_not_population_accuracy': {}, 'crosscheck': {}}
    for name in next(iter(memberships.values()))['membership']:
        selected = [c for c in cases if memberships[c['id']]['membership'][name]]
        summary['variant_sample_counts_not_population_accuracy'][name] = summarize(selected)
    cm = {c['id']: c for c in cases}
    cross = read('quality-crosscheck.json')
    mismatches = []
    for c in cross['cases']:
        lane = cm[c['id']]
        for r in c['reviewed_contexts']:
            assert any((r['document_id'], r['sentence']) == (x['document_id'], x['sentence']) for x in raw[c['id']]['rows'])
        if c['class'] != lane['class']:
            mismatches.append({'id': c['id'], 'lemma': c['lemma'], 'coordinator': c['class'], 'lane': lane['class'],
                               'lane_confidence': lane['confidence'], 'coordinator_reason': c['rationale'],
                               'lane_reason': lane.get('rationale', lane.get('reason'))})
    summary['crosscheck'] = {'n': len(cross['cases']), 'agreement': len(cross['cases']) - len(mismatches),
                            'mismatches': mismatches, 'scope': cross['scope'],
                            'reconciliation': 'Oceny pierwotne zachowane. Różnice nie stanowią automatycznych błędów; nowe źródła i ocena rejestru omawiane w syntezie.'}
    assert all(v['n'] == (40 if k.startswith('band-') else 20) for k, v in summary['strata'].items())
    for name in ('baseline', 'proposal'):
        assert len(read(f'{name}-measurements.json')['variants']) == 27
        assert len(read(f'{name}-dispersion-grid.json')['grid']) == 25
    (OUT / 'quality-summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: summary[k] for k in ('all_cases', 'contexts', 'strata', 'crosscheck')}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
