"""Kandydaci strukturalni KWJP; częstość pozostaje przy jednostce korpusu."""
from collections import Counter, defaultdict
import unicodedata

SHARED_POS = frozenset('adj adja adjc adjp adv aglt bedzie brev comp conj depr fin frag ger imps impt inf interj num numcomp pact pant part pcon ppas ppron12 ppron3 praet pred prep subst winien'.split())


def _lemma_index(db):
    # Osobna relacja techniczna: żaden pełny ID nie jest skracany ani zmieniany.
    if db.execute("select 1 from sqlite_temp_master where name='link_lemma_pos'").fetchone():
        return
    db.execute('''create temp table link_lemma_pos (
        lemma_nfc text not null, pos text not null,
        lexeme_id integer not null, primary key(lemma_nfc,pos,lexeme_id)) without rowid''')
    db.execute('''insert into link_lemma_pos
        select distinct nfc(l.lemma_base),
        case when instr(i.tag,':')>0 then substr(i.tag,1,instr(i.tag,':')-1) else i.tag end,
        l.id from interpretation i join lexeme l on l.id=i.lexeme_id''')


def candidates(db, kind, unit_1, pos=None, unit_2=None, allowed_pos=SHARED_POS):
    unit = unicodedata.normalize('NFC', unit_1)
    found = []
    if kind == 'kwjp_lemma':
        method = 'NFC_LEMMA_POS'
        if pos in allowed_pos:
            _lemma_index(db)
            found = [{'lexeme_id': row[0], 'lemma_id': row[1], 'source_id': row[2]}
                     for row in db.execute('''select l.id,l.lemma_id,l.source_id
                         from link_lemma_pos p join lexeme l on l.id=p.lexeme_id
                         where p.lemma_nfc=? and p.pos=? order by l.source_id,l.lemma_id''', (unit, pos))]
    elif kind in {'kwjp_orth', 'kwjp_orth_lc'}:
        method = 'NFC_FORM' if kind == 'kwjp_orth' else 'NFC_LOWER_FORM'
        column = 'nfc' if kind == 'kwjp_orth' else 'game_key'
        if kind == 'kwjp_orth_lc':
            unit = unicodedata.normalize('NFC', unit.lower())
        found = [{'form_id': row[0], 'original': row[1]}
                 for row in db.execute(f'select id,original from surface_form where {column}=? order by original', (unit,))]
    elif kind == 'kwjp_bigram':
        if unit_2 is None:
            raise ValueError('Bigram wymaga dwóch segmentów')
        return {'method': 'BIGRAM_SEGMENTS', 'status': 'NOT_APPLICABLE',
                'candidates': [], 'sense_identity_confirmed': False,
                'reason': 'Dwa segmenty nie dowodzą częstości sklejonej formy.'}
    else:
        raise ValueError('Nieznany rodzaj listy KWJP')
    return {'method': method, 'status': 'UNMATCHED' if not found else
            'AMBIGUOUS' if len(found) > 1 else 'EXACT_CANDIDATE',
            'candidates': found, 'sense_identity_confirmed': False,
            'reason': 'Dopasowanie strukturalne; bez przypisania sensu i częstości leksemowi.'}


def availability(*, observed=None, threshold=None, comparable=False,
                 genre='all', unavailable_reason=None, applicable=True, mapped=True):
    if unavailable_reason:
        status, reason = 'UNAVAILABLE', unavailable_reason
    elif not applicable:
        status, reason = 'NOT_APPLICABLE', 'Miara nie dotyczy tej jednostki.'
    elif observed is not None:
        return {'status': 'OBSERVED', 'metrics': observed, 'reason': 'Rekord opublikowany w tej liście.'}
    elif not mapped:
        status, reason = 'UNMATCHED', 'Brak porównywalnej jednostki.'
    elif comparable and genre == 'all' and threshold is not None:
        status, reason = 'ABSENT_OR_BELOW_PUBLICATION_THRESHOLD', f'Brak porównywalnego rekordu; globalny próg publikacji {threshold}.'
    else:
        status, reason = 'NOT_IN_PUBLISHED_LIST', 'Brak rekordu; nie wyznaczamy zera ani częstości pełnej formy.'
    return {'status': status, 'metrics': None, 'reason': reason}


def create_links(db, allowed_pos=SHARED_POS):
    """Pełny etap w nowej bazie; ponowienie nie nadpisuje istniejących relacji."""
    db.executescript('''
        create table evidence_link (
            evidence_id integer primary key references corpus_evidence,
            method text not null, status text not null,
            sense_identity_confirmed integer not null check(sense_identity_confirmed=0),
            reason text not null);
        create table evidence_candidate (
            id integer primary key,
            evidence_id integer not null references evidence_link,
            lexeme_id integer references lexeme,
            form_id integer references surface_form,
            check ((lexeme_id is null) != (form_id is null)));
        create unique index candidate_lexeme on evidence_candidate(evidence_id,lexeme_id) where lexeme_id is not null;
        create unique index candidate_form on evidence_candidate(evidence_id,form_id) where form_id is not null;
        create index candidate_by_lexeme on evidence_candidate(lexeme_id);
        create index candidate_by_form on evidence_candidate(form_id);
    ''')
    _lemma_index(db)
    summary = defaultdict(Counter)
    rows = db.execute('''select e.id,e.source_id,s.kind,e.unit_1,e.pos,e.unit_2
        from corpus_evidence e join source_artifact s on s.source_id=e.source_id
        order by e.source_id,e.row_number''')
    for evidence_id, source_id, kind, unit, pos, second in rows:
        result = candidates(db, kind, unit, pos, second, allowed_pos)
        db.execute('insert into evidence_link values (?,?,?,?,?)',
                   (evidence_id, result['method'], result['status'], 0, result['reason']))
        db.executemany('insert into evidence_candidate(evidence_id,lexeme_id,form_id) values (?,?,?)',
                       [(evidence_id, c.get('lexeme_id'), c.get('form_id')) for c in result['candidates']])
        summary[source_id][result['status']] += 1
    return {source: dict(sorted(counts.items())) for source, counts in sorted(summary.items())}
