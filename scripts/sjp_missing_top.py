"""Najczęstsze słowa SJP.pl, których brak w BROAD i STANDARD (miara, nie wejście).

SJP.pl jest tu wyłącznie miarą, jak w benchmark_sjp.py. Baza buildu jest
otwierana tylko do odczytu. Popularność to liczba wystąpień formy (małe
litery) w KWJP.

Użycie:
  python3 scripts/sjp_missing_top.py RUN_DIR SJP_TXT OUT_JSON [N]
"""
import json
import sqlite3
import sys
from collections import Counter
from pathlib import Path

from benchmark_sjp import KWJP_FORMS, in_scope, read_words, sha256


def reject_rules(db, word, variant, cache):
    """Lematy SGJP i reguły odrzucenia wspólne dla wszystkich analiz słowa.

    Indeks po słowie wymuszony: bez niego SQLite wybiera indeks po wariancie
    i każde słowo skanuje wszystkie analizy (godziny zamiast minut).
    """
    lemmas, sets = set(), []
    rows = db.execute('''select coalesce(l.lemma_id, c.lemma_id), d.assessment_key
                         from analysis a indexed by analysis_game_key
                         join variant_decision d on d.analysis_key=a.analysis_key
                         left join interpretation i on i.id=a.interpretation_id
                         left join lexeme l on l.id=i.lexeme_id
                         left join derivation_candidate c on c.candidate_key=a.candidate_key
                         where a.game_key=? and +d.variant=?''', (word, variant))
    for lemma, key in rows:
        if lemma:
            lemmas.add(lemma)
        value = cache.get(key)
        if value is None:
            text = db.execute('select assessment from decision_payload where assessment_key=?', (key,)).fetchone()[0]
            value = cache[key] = json.loads(text)
        sets.append({c['rule_id'] for layer in ('language', 'game', 'profile', 'release_scope')
                     for c in value[layer]['checks'] if c['status'] == 'reject'})
    if not sets:
        return [], None
    common = set.intersection(*sets)
    return sorted(lemmas), sorted(common) if common else sorted(set().union(*sets))


def main(run_dir, sjp_path, out_path, n=2000):
    run = Path(run_dir)
    sjp = {w for w in read_words(sjp_path) if in_scope(w)}
    lists = {v: {w for w in read_words(run / 'lists' / f'{v}.txt') if in_scope(w)} for v in ('broad', 'standard')}
    db = sqlite3.connect(f'file:{run / "build.sqlite"}?mode=ro', uri=True)
    freq = Counter()
    for form, value in db.execute('select unit_1,freq from corpus_evidence where source_id=?', (KWJP_FORMS,)):
        if form and value:
            freq[form] += int(value)
    cache, result = {}, {}
    for variant, ours in lists.items():
        missing = sjp - ours
        top = sorted(missing, key=lambda w: (-freq[w], w))[:n]
        rows, rules = [], Counter()
        for word in top:
            lemmas, rule = reject_rules(db, word, variant, cache)
            rows.append({'word': word, 'kwjp': freq[word], 'in_broad': word in lists['broad'],
                         'sgjp_lemmas': lemmas, 'reject_rules': rule})
            rules[' + '.join(rule) if rule else 'brak w SGJP'] += 1
        result[variant] = {'missing_words': len(missing), 'with_kwjp': sum(1 for w in missing if freq[w]),
                           'top': rows, 'top_reasons': dict(rules.most_common())}
    out = {'schema_version': 1, 'purpose': 'SJP.pl jako miara, nie wejście budowy',
           'inputs': {'run': str(run), 'sjp_sha256': sha256(sjp_path), 'kwjp_forms_source': KWJP_FORMS,
                      'lists_sha256': {v: sha256(run / 'lists' / f'{v}.txt') for v in lists}},
           'n': n, **result}
    Path(out_path).write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], *(int(a) for a in sys.argv[4:5]))
