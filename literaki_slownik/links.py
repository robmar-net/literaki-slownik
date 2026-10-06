"""Kandydaci strukturalni KWJP; częstość pozostaje przy jednostce korpusu."""
from collections import Counter, defaultdict
import json
import unicodedata
from pathlib import Path
from .inputs import GeneratorError

SHARED_POS = frozenset('adj adja adjc adjp adv aglt bedzie brev comp conj depr fin frag ger imps impt inf interj num numcomp pact pant part pcon ppas ppron12 ppron3 praet pred prep subst winien'.split())
SGJP_POS = SHARED_POS | {'cond', 'pacta'}
DEFAULT_POS_MAP_VERSION = 'builtin-identity-shared-pos'

UNMATCHED_REASONS = {
    'NO_POS': 'Jednostka lemma bez POS; nie zgadujemy klasy.',
    'POS_OUTSIDE_EXPLICIT_MAP': 'POS KWJP poza jawnym mapowaniem; bez aliasu.',
    'NO_STRUCTURAL_CANDIDATE': 'Brak leksemu/formy o tym kluczu; brak w źródle słów nie jest częstością zero.',
}


def load_pos_map(path):
    """Jawne, wersjonowane mapowanie POS KWJP → SGJP; odmowa twierdzeń o sensie i F."""
    try:
        data = json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, UnicodeError, ValueError) as error:
        raise GeneratorError(f'Nieczytelne mapowanie POS: {error}', 4, str(path)) from error
    if not isinstance(data, dict) or data.get('schema_version') != 1 or not isinstance(data.get('version'), str):
        raise GeneratorError('Nieobsługiwany format mapowania POS', 4, str(path))
    if data.get('sense_identity_confirmed') is not False or data.get('allocate_frequency_to_candidates') is not False:
        raise GeneratorError('Mapowanie POS nie może potwierdzać sensu ani rozdzielać F', 4, str(path))
    pairs, kwjp_only, sgjp_only = data.get('confirmed_pairs'), data.get('kwjp_only'), data.get('sgjp_only')
    if (not isinstance(pairs, dict) or not pairs or not isinstance(kwjp_only, list) or not isinstance(sgjp_only, list)
            or not all(isinstance(k, str) and isinstance(v, str) for k, v in pairs.items())):
        raise GeneratorError('Niepełne mapowanie POS', 4, str(path))
    if set(pairs) & set(kwjp_only) or set(pairs.values()) & set(sgjp_only):
        raise GeneratorError('Klasa jednocześnie zmapowana i oznaczona jako bez odpowiednika', 4, str(path))
    if not set(pairs.values()) <= SGJP_POS:
        raise GeneratorError('Mapowanie POS wskazuje klasę spoza SGJP', 4, str(path))
    return {'version': data['version'], 'pairs': dict(sorted(pairs.items()))}


def _pos_pairs(allowed_pos):
    # Zbiór oznacza identyczne nazwy; słownik — jawne pary KWJP → SGJP.
    return dict(allowed_pos) if isinstance(allowed_pos, dict) else {p: p for p in allowed_pos}


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
    unmatched = 'NO_STRUCTURAL_CANDIDATE'
    if kind == 'kwjp_lemma':
        method = 'NFC_LEMMA_POS'
        pairs = _pos_pairs(allowed_pos)
        if pos is None:
            unmatched = 'NO_POS'
        elif pos not in pairs:
            unmatched = 'POS_OUTSIDE_EXPLICIT_MAP'
        else:
            _lemma_index(db)
            found = [{'lexeme_id': row[0], 'lemma_id': row[1], 'source_id': row[2]}
                     for row in db.execute('''select l.id,l.lemma_id,l.source_id
                         from link_lemma_pos p join lexeme l on l.id=p.lexeme_id
                         where p.lemma_nfc=? and p.pos=? order by l.source_id,l.lemma_id''', (unit, pairs[pos]))]
    elif kind in {'kwjp_orth', 'kwjp_orth_lc'}:
        method = 'NFC_FORM' if kind == 'kwjp_orth' else 'NFC_LOWER_FORM'
        column = 'nfc' if kind == 'kwjp_orth' else 'game_key'
        if kind == 'kwjp_orth_lc':
            unit = unicodedata.normalize('NFC', unit.lower())
        found = [{'form_id': row[0], 'original': row[1]}
                 for row in db.execute(f'select id,original from surface_form where {column}=? order by original', (unit,))]
        if db.execute("select 1 from sqlite_master where name='derivation_candidate'").fetchone():
            lookup = unicodedata.normalize('NFC', unit.lower())
            for candidate_key, original in db.execute('''select candidate_key,original
                    from derivation_candidate where game_key=? order by original,candidate_key''', (lookup,)):
                if kind == 'kwjp_orth_lc' or unicodedata.normalize('NFC', original) == unit:
                    found.append({'candidate_key': candidate_key, 'original': original})
    elif kind == 'kwjp_bigram':
        if unit_2 is None:
            raise ValueError('Bigram wymaga dwóch segmentów')
        return {'method': 'BIGRAM_SEGMENTS', 'status': 'NOT_APPLICABLE',
                'candidates': [], 'sense_identity_confirmed': False,
                'reason': 'Dwa segmenty nie dowodzą częstości sklejonej formy.'}
    else:
        raise ValueError('Nieznany rodzaj listy KWJP')
    if not found:
        return {'method': method, 'status': 'UNMATCHED', 'candidates': [],
                'sense_identity_confirmed': False, 'unmatched_reason': unmatched,
                'reason': UNMATCHED_REASONS[unmatched]}
    if len(found) > 1:
        reason = 'Wielu kandydatów strukturalnych; nie wybieramy sensu ani nie dzielimy F.'
    else:
        reason = 'Jeden kandydat strukturalny; bez potwierdzenia sensu i dopuszczalności.'
    return {'method': method, 'status': 'AMBIGUOUS' if len(found) > 1 else 'EXACT_CANDIDATE',
            'candidates': found, 'sense_identity_confirmed': False, 'reason': reason}


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
            candidate_key text references derivation_candidate,
            check ((lexeme_id is not null) + (form_id is not null) + (candidate_key is not null) = 1));
        create unique index candidate_lexeme on evidence_candidate(evidence_id,lexeme_id) where lexeme_id is not null;
        create unique index candidate_form on evidence_candidate(evidence_id,form_id) where form_id is not null;
        create index candidate_by_lexeme on evidence_candidate(lexeme_id);
        create index candidate_by_form on evidence_candidate(form_id);
        create unique index candidate_derivation on evidence_candidate(evidence_id,candidate_key) where candidate_key is not null;
        create index candidate_by_derivation on evidence_candidate(candidate_key);
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
        db.executemany('insert into evidence_candidate(evidence_id,lexeme_id,form_id,candidate_key) values (?,?,?,?)',
                       [(evidence_id, c.get('lexeme_id'), c.get('form_id'), c.get('candidate_key')) for c in result['candidates']])
        summary[source_id][result['status']] += 1
    return {source: dict(sorted(counts.items())) for source, counts in sorted(summary.items())}


def link_report(db, unavailable=(), details=False, pos_map_version=DEFAULT_POS_MAP_VERSION):
    """Mianowniki to jednostki danej listy, nigdy krawędzie kandydatów."""
    lists = {}
    for source_id, kind, raw_metadata in db.execute(
            "select source_id,kind,metadata from source_artifact where kind like 'kwjp_%' order by source_id"):
        metadata = json.loads(raw_metadata)
        units, freq = db.execute(
            'select count(*),coalesce(sum(freq),0) from corpus_evidence where source_id=?',
            (source_id,)).fetchone()
        statuses = dict(db.execute('''select l.status,count(*) from evidence_link l
            join corpus_evidence e on e.id=l.evidence_id where e.source_id=?
            group by l.status order by l.status''', (source_id,)))
        if sum(statuses.values()) != units:
            raise GeneratorError('Niepełne rozliczenie powiązań KWJP', 4, source_id)
        edges = db.execute('''select count(*) from evidence_candidate c
            join corpus_evidence e on e.id=c.evidence_id where e.source_id=?''',
            (source_id,)).fetchone()[0]
        lists[source_id] = {
            'kind': kind, 'genre': metadata.get('genre'),
            'publication_threshold': metadata.get('publication_threshold'),
            'evidence_units': units, 'observed_units': units,
            'sum_freq': freq, 'link_statuses': statuses, 'candidate_edges': edges,
        }
        if details:
            lists[source_id].update(_list_details(db, source_id, kind))
    report = {
        'scope': 'structural_links_only_not_game_or_sense_decisions',
        'denominator': 'published_evidence_units_per_source_list',
        'lists': lists,
        'unavailable': [{'source_id': item['source_id'],
                         **availability(unavailable_reason=item['reason'])}
                        for item in unavailable],
    }
    if details:
        report['pos_map_version'] = pos_map_version
        report['sense_identity_confirmed'] = False
        report['frequency_allocated_to_candidates'] = False
        derived = 'candidate_key' in {r[1] for r in db.execute('pragma table_info(evidence_candidate)')}
        total = db.execute('select count(*) from derivation_candidate').fetchone()[0] if _has_table(db, 'derivation_candidate') else 0
        report['derivation_candidates'] = {
            'total': total,
            'with_corpus_edge': db.execute(
                'select count(distinct candidate_key) from evidence_candidate where candidate_key is not null'
            ).fetchone()[0] if derived else 0,
            'note': 'Brak krawędzi nie jest częstością zero; konstrukcje segmentowane mogą być rozdzielone przez tokenizację.',
        }
    return report


def _has_table(db, name):
    return bool(db.execute("select 1 from sqlite_master where type='table' and name=?", (name,)).fetchone())


def _list_details(db, source_id, kind):
    """Liczebności metod, celów krawędzi, niejednoznaczności i niedopasowań jednej listy."""
    derived = 'candidate_key' in {r[1] for r in db.execute('pragma table_info(evidence_candidate)')}
    methods = dict(db.execute('''select l.method,count(*) from evidence_link l
        join corpus_evidence e on e.id=l.evidence_id where e.source_id=? group by l.method order by l.method''',
        (source_id,)))
    by_status = dict(db.execute('''select l.status,sum(e.freq) from evidence_link l
        join corpus_evidence e on e.id=l.evidence_id where e.source_id=? group by l.status order by l.status''',
        (source_id,)))
    targets = db.execute('''select count(c.lexeme_id),count(c.form_id),''' +
        ('count(c.candidate_key)' if derived else '0') + ''',count(distinct c.lexeme_id),count(distinct c.form_id),''' +
        ('count(distinct c.candidate_key)' if derived else '0') + '''
        from evidence_candidate c join corpus_evidence e on e.id=c.evidence_id where e.source_id=?''',
        (source_id,)).fetchone()
    histogram = {}
    for n, units in db.execute('''select coalesce(c.n,0) as n,count(*) from corpus_evidence e
            left join (select evidence_id,count(*) as n from evidence_candidate group by evidence_id) c
            on c.evidence_id=e.id where e.source_id=? group by n order by n''', (source_id,)):
        histogram[str(n)] = units
    result = {
        'methods': methods,
        'sum_freq_by_status': by_status,
        'candidate_edges_by_target': {'lexeme': targets[0], 'form': targets[1], 'derivation_candidate': targets[2]},
        'distinct_targets': {'lexeme': targets[3], 'form': targets[4], 'derivation_candidate': targets[5]},
        'candidates_per_unit': histogram,
    }
    if kind == 'kwjp_lemma':
        result['unmatched_by_pos'] = {str(pos): n for pos, n in db.execute('''select e.pos,count(*) from evidence_link l
            join corpus_evidence e on e.id=l.evidence_id where e.source_id=? and l.status='UNMATCHED'
            group by e.pos order by e.pos''', (source_id,))}
    return result


def verify_link_completeness(db, allowed_pos=SHARED_POS):
    """Niezależne odtworzenie w SQL oczekiwanych krawędzi i porównanie z zapisanymi.

    Sprawdza, czy każda jednostka ma powiązanie, czy każdy obecny leksem/forma/
    kandydat konstrukcji spełniający regułę ma krawędź oraz czy status odpowiada
    liczbie kandydatów. Nie ocenia sensu ani poprawności językowej.
    """
    pairs = _pos_pairs(allowed_pos)
    _lemma_index(db)
    db.execute('drop table if exists temp.link_pos_pair')
    db.execute('create temp table link_pos_pair (kwjp text primary key, sgjp text not null) without rowid')
    db.executemany('insert into temp.link_pos_pair values (?,?)', sorted(pairs.items()))
    derived = (_has_table(db, 'derivation_candidate')
               and 'candidate_key' in {r[1] for r in db.execute('pragma table_info(evidence_candidate)')})
    db.execute('drop table if exists temp.link_expected')
    db.execute('''create temp table link_expected (evidence_id integer not null, target text not null,
        primary key(evidence_id,target)) without rowid''')
    db.execute('''insert or ignore into temp.link_expected
        select e.id,'L'||p.lexeme_id from corpus_evidence e
        join source_artifact s on s.source_id=e.source_id and s.kind='kwjp_lemma'
        join temp.link_pos_pair m on m.kwjp=e.pos
        join temp.link_lemma_pos p on p.lemma_nfc=nfc(e.unit_1) and p.pos=m.sgjp''')
    db.execute('''insert or ignore into temp.link_expected
        select e.id,'F'||f.id from corpus_evidence e
        join source_artifact s on s.source_id=e.source_id and s.kind='kwjp_orth'
        join surface_form f on f.nfc=nfc(e.unit_1)''')
    db.execute('''insert or ignore into temp.link_expected
        select e.id,'F'||f.id from corpus_evidence e
        join source_artifact s on s.source_id=e.source_id and s.kind='kwjp_orth_lc'
        join surface_form f on f.game_key=game_key(e.unit_1)''')
    if derived:
        db.execute('''insert or ignore into temp.link_expected
            select e.id,'D'||d.candidate_key from corpus_evidence e
            join source_artifact s on s.source_id=e.source_id and s.kind in ('kwjp_orth','kwjp_orth_lc')
            join derivation_candidate d on d.game_key=game_key(e.unit_1)
            where s.kind='kwjp_orth_lc' or nfc(d.original)=nfc(e.unit_1)''')
    actual = '''select evidence_id,case when lexeme_id is not null then 'L'||lexeme_id
        when form_id is not null then 'F'||form_id else 'D'||''' + ('candidate_key' if derived else 'null') + ''' end
        from evidence_candidate'''
    missing = db.execute('select count(*) from (select evidence_id,target from temp.link_expected except ' + actual + ')').fetchone()[0]
    unexpected = db.execute('select count(*) from (' + actual + ' except select evidence_id,target from temp.link_expected)').fetchone()[0]
    without = db.execute('''select count(*) from corpus_evidence e
        join source_artifact s on s.source_id=e.source_id and s.kind like 'kwjp_%'
        where not exists (select 1 from evidence_link l where l.evidence_id=e.id)''').fetchone()[0]
    inconsistent = db.execute('''select count(*) from evidence_link l
        join corpus_evidence e on e.id=l.evidence_id join source_artifact s on s.source_id=e.source_id
        left join (select evidence_id,count(*) as n from evidence_candidate group by evidence_id) c on c.evidence_id=l.evidence_id
        where case when s.kind='kwjp_bigram' then l.status!='NOT_APPLICABLE' or coalesce(c.n,0)!=0
              when coalesce(c.n,0)=0 then l.status!='UNMATCHED'
              when c.n=1 then l.status!='EXACT_CANDIDATE' else l.status!='AMBIGUOUS' end''').fetchone()[0]
    db.execute('drop table temp.link_expected')
    db.execute('drop table temp.link_pos_pair')
    return {'missing_edges': missing, 'unexpected_edges': unexpected,
            'units_without_link': without, 'inconsistent_statuses': inconsistent,
            'derivation_candidates_checked': derived,
            'method': 'independent_sql_recomputation_of_structural_edges'}


def link_stage_gate(verified, constructions_status):
    """Pełny etap links tylko przy kompletnym zbiorze kandydatów i zerowych rozbieżnościach."""
    blocking = []
    if constructions_status != 'complete':
        blocking.append(f'constructions={constructions_status}: zbiór kandydatów konstrukcji nie jest pełny')
    for key in ('missing_edges', 'unexpected_edges', 'units_without_link', 'inconsistent_statuses'):
        if verified[key]:
            blocking.append(f'{key}={verified[key]}')
    if not verified.get('derivation_candidates_checked'):
        blocking.append('brak relacji kandydatów konstrukcji w powiązaniach')
    return {'complete': not blocking, 'blocking': blocking, 'verification': verified}


def _list_meta(db):
    for source_id, kind, raw in db.execute(
            "select source_id,kind,metadata from source_artifact where kind like 'kwjp_%' order by source_id"):
        meta = json.loads(raw)
        yield source_id, kind, meta.get('genre'), meta.get('publication_threshold')


def word_availability(db, key, unavailable=(), allowed_pos=SHARED_POS):
    """Status każdej listy KWJP dla wszystkich celów zapytania; bez imputacji zera.

    Cele: formy źródłowe (orth/orth_lc), kandydaci konstrukcji (orth/orth_lc)
    i pary leksem+POS (lemma). F pochodzi wyłącznie z rekordu korpusu.
    """
    key = unicodedata.normalize('NFC', unicodedata.normalize('NFC', key).lower())
    built = _has_table(db, 'evidence_link')
    derived = built and _has_table(db, 'derivation_candidate') and 'candidate_key' in {
        r[1] for r in db.execute('pragma table_info(evidence_candidate)')}
    forms = db.execute('select id,original from surface_form where game_key=? order by original', (key,)).fetchall()
    constructions = db.execute('select candidate_key,original,rule_id from derivation_candidate where game_key=? '
                               'order by original,candidate_key', (key,)).fetchall() if _has_table(db, 'derivation_candidate') else []
    lexemes = db.execute('''select distinct l.id,l.lemma_id,
        case when instr(i.tag,':')>0 then substr(i.tag,1,instr(i.tag,':')-1) else i.tag end
        from interpretation i join lexeme l on l.id=i.lexeme_id join surface_form f on f.id=i.form_id
        where f.game_key=? order by l.lemma_id,3''', (key,)).fetchall()
    segmented_homograph = bool(constructions)

    def observed(source_id, column, value, pos=None):
        if not built or (column == 'candidate_key' and not derived):
            return []
        # CROSS JOIN wymusza start od indeksu celu, bez skanu całej listy źródła.
        sql = ('''select e.row_number,e.typed_metrics,e.pos,l.status from evidence_candidate c
            cross join corpus_evidence e on e.id=c.evidence_id cross join evidence_link l on l.evidence_id=e.id
            where e.source_id=? and c.''' + column + '=?' + (' and e.pos in (select value from json_each(?))' if pos else '') +
            ' order by e.row_number')
        args = (source_id, value) + ((json.dumps(pos),) if pos else ())
        return [{'row_number': row, 'freq': json.loads(typed).get('freq'), 'typed_metrics': json.loads(typed),
                 'pos': epos, 'link_status': status} for row, typed, epos, status in db.execute(sql, args)]

    reverse = {}
    for kwjp_pos, sgjp_pos in _pos_pairs(allowed_pos).items():
        reverse.setdefault(sgjp_pos, []).append(kwjp_pos)
    lists = []
    for source_id, kind, genre, threshold in _list_meta(db):
        targets = []
        if kind == 'kwjp_bigram':
            targets.append({'target': {'type': 'word', 'game_key': key},
                            **availability(applicable=False)})
        elif kind in ('kwjp_orth', 'kwjp_orth_lc'):
            for fid, original in forms:
                found = observed(source_id, 'form_id', fid)
                if found:
                    status = availability(observed=found)
                elif segmented_homograph:
                    status = {'status': 'NOT_IN_PUBLISHED_LIST', 'metrics': None,
                              'reason': 'Homograf konstrukcji wielosegmentowej; tokenizacja niepewna, nie wyznaczamy F 0–4.'}
                else:
                    status = availability(threshold=threshold, comparable=True, genre=genre)
                targets.append({'target': {'type': 'form', 'original': original}, **status})
            for candidate_key, original, rule_id in constructions:
                found = observed(source_id, 'candidate_key', candidate_key)
                status = availability(observed=found) if found else {
                    'status': 'NOT_IN_PUBLISHED_LIST', 'metrics': None,
                    'reason': 'Konstrukcja może być rozdzielona na segmenty przez tokenizację; nie wyznaczamy F 0–4 ani sumy segmentów.'}
                targets.append({'target': {'type': 'derivation_candidate', 'candidate_key': candidate_key,
                                           'original': original, 'rule_id': rule_id}, **status})
        else:
            for lid, lemma_id, pos in lexemes:
                kwjp_pos = reverse.get(pos)
                found = observed(source_id, 'lexeme_id', lid, kwjp_pos) if kwjp_pos else []
                if found:
                    status = availability(observed=found)
                elif not kwjp_pos:
                    status = availability(mapped=False)
                else:
                    status = availability(threshold=threshold, comparable=True, genre=genre)
                targets.append({'target': {'type': 'lexeme', 'lemma_id': lemma_id, 'pos': pos}, **status})
        lists.append({'source_id': source_id, 'kind': kind, 'genre': genre,
                      'publication_threshold': threshold, 'targets': targets})
    return {'query_key': key, 'links_available': built, 'absence_is_not_zero': True,
            'sense_identity_confirmed': False, 'lists': lists,
            'tokenization_caveat': ('F formy to F opublikowanego segmentu. Homograf konstrukcji spoza bieżących '
                                    'klas (np. miałem jako miał+em) może mieć zaniżone F; nie korygujemy go.'),
            'unavailable': [{'source_id': item['source_id'], **availability(unavailable_reason=item['reason'])}
                            for item in unavailable]}
