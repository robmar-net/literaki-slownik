"""Porównanie zamrożonych list BROAD/STANDARD z listą SJP.pl (plan C runbooka).

SJP.pl jest tu wyłącznie miarą: skrypt niczego nie zapisuje w buildzie ani w
konfiguracji generatora, a jego wynik nie jest wejściem budowy. Baza buildu
jest otwierana tylko do odczytu.

Użycie:
  python3 scripts/benchmark_sjp.py RUN_DIR SJP_TXT OUT_JSON

SJP_TXT to oficjalna lista słów SJP.pl, jedno słowo w wierszu (np. zrzut
lexicons/pl-sjp-20260820.dawg serwera gry). Wynik zawiera agregaty i krótkie
próbki słów; atrybucja SJP.pl: CC BY 4.0.
"""
import hashlib
import json
import sqlite3
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

ALPHABET = frozenset('aąbcćdeęfghijklłmnńoóprsśtuwyzźż')
MIN_LEN, MAX_LEN = 2, 15
KWJP_FORMS = 'KWJP100-kwjp100-slowa-orth_lc-all'
FREQ_BUCKETS = ((1000, '≥1000'), (100, '100–999'), (10, '10–99'), (1, '1–9'), (0, '0 (brak w KWJP)'))
TOP = 60


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def read_words(path):
    with open(path, encoding='utf-8') as f:
        return [w for w in f.read().split('\n') if w]


def in_scope(word):
    return MIN_LEN <= len(word) <= MAX_LEN and set(word) <= ALPHABET


def bucket(freq):
    return next(label for low, label in FREQ_BUCKETS if freq >= low)


def top_by_freq(words, freq, n=TOP):
    return [[w, freq.get(w, 0)] for w in sorted(words, key=lambda w: (-freq.get(w, 0), w))[:n]]


def overlap(ours, sjp):
    inter = len(ours & sjp)
    return {'ours': len(ours), 'sjp': len(sjp), 'intersection': inter,
            'only_ours': len(ours - sjp), 'only_sjp': len(sjp - ours),
            'jaccard': round(inter / len(ours | sjp), 6),
            'sjp_covered_by_ours': round(inter / len(sjp), 6),
            'ours_confirmed_by_sjp': round(inter / len(ours), 6)}


def token_coverage(words, freq):
    total = sum(freq.values())
    return round(sum(f for w, f in freq.items() if w in words) / total, 6)


def main(run_dir, sjp_path, out_path):
    started = time.monotonic()
    run = Path(run_dir)
    lists = {v: run / 'lists' / f'{v}.txt' for v in ('broad', 'standard')}
    raw_sjp = read_words(sjp_path)
    raw = {v: read_words(p) for v, p in lists.items()}
    sjp = {w for w in raw_sjp if in_scope(w)}
    broad, standard = ({w for w in raw[v] if in_scope(w)} for v in ('broad', 'standard'))
    if not standard <= broad:
        raise SystemExit('STANDARD ⊄ BROAD')
    out_of_scope = Counter('litery spoza 32' if not set(w) <= ALPHABET else 'długość' for w in raw_sjp if not in_scope(w))

    db = sqlite3.connect(f'file:{run / "build.sqlite"}?mode=ro', uri=True)
    freq = {}
    for form, value in db.execute('select unit_1,freq from corpus_evidence where source_id=?', (KWJP_FORMS,)):
        if form and in_scope(form) and value:
            freq[form] = freq.get(form, 0) + int(value)

    miss_b = sjp - broad
    miss_s = (sjp & broad) - standard
    ours_b = broad - sjp
    ours_s = standard - sjp

    # Przyczyny i skład: jeden przebieg po analizach; powody tylko dla potrzebnych słów.
    payload_cache = {}
    reasons = {'broad': defaultdict(set), 'standard': defaultdict(set)}
    accepted_shape = defaultdict(lambda: {'classes': set(), 'construction': False, 'source': False, 'labels': set()})
    seen = set()
    query = '''select a.game_key,a.expanded_tag,a.candidate_key is not null,coalesce(i.qualifiers,''),
                      d.variant,d.membership_status,d.assessment_key
               from analysis a join variant_decision d on d.analysis_key=a.analysis_key
               left join interpretation i on i.id=a.interpretation_id'''
    rows = 0
    for key, tag, construction, qualifiers, variant, membership, assessment_key in db.execute(query):
        rows += 1
        if key in miss_b or key in miss_s:
            seen.add(key)
            target = miss_b if variant == 'broad' else miss_s
            if key in target and membership == 'reject':
                value = payload_cache.get(assessment_key)
                if value is None:
                    text = db.execute('select assessment from decision_payload where assessment_key=?',
                                      (assessment_key,)).fetchone()[0]
                    value = payload_cache[assessment_key] = json.loads(text)
                    if len(payload_cache) > 200000:
                        payload_cache.clear()
                rules = set()
                for layer in ('language', 'game', 'profile', 'release_scope'):
                    rules.update(c['rule_id'] for c in value[layer]['checks'] if c['status'] == 'reject')
                reasons[variant][key].add(frozenset(rules))
        elif key in ours_b and variant == 'broad' and membership == 'accept':
            shape = accepted_shape[key]
            shape['classes'].add(tag.split(':', 1)[0])
            shape['construction'] |= bool(construction)
            shape['source'] |= not construction
            shape['labels'].update(label for label in qualifiers.split('|') if label)

    def explain(target, variant):
        absent = sorted(target - seen)
        signature = Counter()
        per_rule = Counter()
        examples = defaultdict(list)
        for key in target - set(absent):
            sets = reasons[variant].get(key, set())
            # Reguła rozstrzygająca słowo: obecna w każdej analizie (część wspólna), inaczej mieszanka.
            common = frozenset.intersection(*sets) if sets else frozenset()
            sig = ' + '.join(sorted(common)) if common else 'różne reguły w różnych analizach'
            signature[sig] += 1
            for rule in set().union(*sets) if sets else ():
                per_rule[rule] += 1
            examples[sig].append(key)
        return {
            'words': len(target),
            'absent_from_sgjp_and_constructions': len(absent),
            'absent_by_frequency': dict(Counter(bucket(freq.get(w, 0)) for w in absent)),
            'absent_top_by_frequency': top_by_freq(absent, freq),
            'rejected_by_common_rule': [{'rule': sig, 'words': n, 'top_by_frequency': top_by_freq(examples[sig], freq, 15)}
                                        for sig, n in signature.most_common()],
            'words_with_rule_in_any_analysis': dict(per_rule.most_common()),
        }

    class_counter = Counter()
    label_counter = Counter()
    construction_only = 0
    for key, shape in accepted_shape.items():
        class_counter[' | '.join(sorted(shape['classes']))] += 1
        for label in shape['labels']:
            label_counter[label] += 1
        construction_only += shape['construction'] and not shape['source']
    by_length = {}
    for n in range(MIN_LEN, MAX_LEN + 1):
        s_n = {w for w in sjp if len(w) == n}
        b_n = {w for w in broad if len(w) == n}
        st_n = {w for w in standard if len(w) == n}
        by_length[n] = {'sjp': len(s_n), 'broad': len(b_n), 'standard': len(st_n),
                        'broad_and_sjp': len(s_n & b_n), 'only_sjp_vs_broad': len(s_n - b_n),
                        'only_broad': len(b_n - s_n), 'only_sjp_vs_standard': len(s_n - st_n)}
    short = {n: {'only_sjp_vs_broad': sorted(w for w in miss_b if len(w) == n),
                 'only_broad': sorted(w for w in ours_b if len(w) == n),
                 'sjp_and_broad_not_standard': sorted(w for w in miss_s if len(w) == n)} for n in (2, 3)}
    result = {
        'schema_version': 1,
        'purpose': 'benchmark: SJP.pl jako miara, nie wejście budowy',
        'inputs': {'run': str(run), 'lists_sha256': {v: sha256(p) for v, p in lists.items()},
                   'sjp_list': str(sjp_path), 'sjp_sha256': sha256(sjp_path), 'kwjp_forms_source': KWJP_FORMS},
        'scope': {'alphabet': ''.join(sorted(ALPHABET)), 'min_length': MIN_LEN, 'max_length': MAX_LEN,
                  'before': {'sjp': len(raw_sjp), 'broad': len(raw['broad']), 'standard': len(raw['standard'])},
                  'after': {'sjp': len(sjp), 'broad': len(broad), 'standard': len(standard)},
                  'sjp_out_of_scope': dict(out_of_scope),
                  'sjp_out_of_scope_examples': sorted(w for w in raw_sjp if not in_scope(w))[:40]},
        'overlap': {'broad': overlap(broad, sjp), 'standard': overlap(standard, sjp),
                    'sjp_and_broad_not_standard': len(miss_s)},
        'kwjp_token_coverage': {'forms': len(freq), 'tokens': sum(freq.values()),
                                'sjp': token_coverage(sjp, freq), 'broad': token_coverage(broad, freq),
                                'standard': token_coverage(standard, freq),
                                'only_sjp_vs_broad': token_coverage(miss_b, freq),
                                'only_broad': token_coverage(ours_b, freq)},
        'frequency_buckets': {name: dict(Counter(bucket(freq.get(w, 0)) for w in words))
                              for name, words in (('only_sjp_vs_broad', miss_b), ('only_sjp_vs_standard', sjp - standard),
                                                  ('only_broad', ours_b), ('only_standard', ours_s),
                                                  ('sjp_and_broad_not_standard', miss_s))},
        'by_length': by_length,
        'short_words': short,
        'only_sjp_vs_broad': explain(miss_b, 'broad'),
        'sjp_and_broad_not_standard': explain(miss_s, 'standard'),
        'only_broad': {'words': len(ours_b), 'top_by_frequency': top_by_freq(ours_b, freq),
                       'accepted_classes': dict(class_counter.most_common(40)),
                       'qualifier_labels_on_accepting_analyses': dict(label_counter.most_common(60)),
                       'construction_only': construction_only},
        'only_standard_top_by_frequency': top_by_freq(ours_s, freq),
        'measurement': {'analysis_rows_scanned': rows, 'seconds': round(time.monotonic() - started)},
    }
    Path(out_path).write_text(json.dumps(result, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('scope', 'overlap', 'kwjp_token_coverage', 'measurement')},
                     ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main(*sys.argv[1:4])
