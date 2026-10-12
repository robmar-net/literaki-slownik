"""Najczęstsze słowa z BROAD i STANDARD, których nie ma w SJP.pl (miara, nie wejście).

Odwrotność sjp_missing_top.py. Baza buildu jest otwierana tylko do odczytu.
Popularność to liczba wystąpień formy (małe litery) w KWJP.

Użycie:
  python3 scripts/sjp_extra_top.py RUN_DIR SJP_TXT OUT_JSON [N]
"""
import json
import sqlite3
import sys
from collections import Counter
from pathlib import Path

from benchmark_sjp import KWJP_FORMS, in_scope, read_words, sha256
from sjp_missing_top import kwjp_freq


def accepted_sources(db, word, variant):
    """Lematy i źródła (`sgjp` albo reguła konstrukcji) analiz przyjętych do wariantu.

    Indeks po słowie wymuszony, jak w sjp_missing_top.reject_rules.
    """
    lemmas, sources = set(), set()
    rows = db.execute('''select coalesce(l.lemma_id, c.lemma_id), c.rule_id
                         from analysis a indexed by analysis_game_key
                         join variant_decision d on d.analysis_key=a.analysis_key
                         left join interpretation i on i.id=a.interpretation_id
                         left join lexeme l on l.id=i.lexeme_id
                         left join derivation_candidate c on c.candidate_key=a.candidate_key
                         where a.game_key=? and +d.variant=? and d.membership_status='accept' ''', (word, variant))
    for lemma, rule in rows:
        if lemma:
            lemmas.add(lemma)
        sources.add(rule or 'sgjp')
    return sorted(lemmas), sorted(sources)


def main(run_dir, sjp_path, out_path, n=2000):
    run = Path(run_dir)
    sjp = {w for w in read_words(sjp_path) if in_scope(w)}
    lists = {v: {w for w in read_words(run / 'lists' / f'{v}.txt') if in_scope(w)} for v in ('broad', 'standard')}
    db = sqlite3.connect(f'file:{run / "build.sqlite"}?mode=ro', uri=True)
    freq = kwjp_freq(db)
    result = {}
    for variant, ours in lists.items():
        extra = ours - sjp
        top = sorted(extra, key=lambda w: (-freq[w], w))[:n]
        rows, kinds = [], Counter()
        for word in top:
            lemmas, sources = accepted_sources(db, word, variant)
            rows.append({'word': word, 'kwjp': freq[word], 'in_standard': word in lists['standard'],
                         'sgjp_lemmas': lemmas, 'sources': sources})
            kinds.update(sources)
        result[variant] = {'extra_words': len(extra), 'with_kwjp': sum(1 for w in extra if freq[w]),
                           'top': rows, 'top_sources': dict(kinds.most_common())}
    out = {'schema_version': 1, 'purpose': 'SJP.pl jako miara, nie wejście budowy',
           'inputs': {'run': str(run), 'sjp_sha256': sha256(sjp_path), 'kwjp_forms_source': KWJP_FORMS,
                      'lists_sha256': {v: sha256(run / 'lists' / f'{v}.txt') for v in lists}},
           'n': n, **result}
    Path(out_path).write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], *(int(a) for a in sys.argv[4:5]))
