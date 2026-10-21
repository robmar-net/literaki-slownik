#!/usr/bin/env python3
"""Odtwórz pomocniczy pomiar form POP0; wejścia tylko do odczytu."""

from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import json
from pathlib import Path
import sqlite3


REPO = Path(__file__).resolve().parents[5]
PACKAGE = REPO / "data/work/pop-v3-20261014-022011-a"
DATABASE = REPO / "data/work/lists-v31-20261012-162111-a/build.sqlite"
ORTH = REPO / "cache/kwjp/kwjp100-slowa-orth-all.csv.gz"
OUTPUT = Path(__file__).resolve().parent / "evidence/lexeme-measurement.json"
DB_PIN = "4b0d17c6e75139042cf18d6ea9a24650d4e7906b999d3a0ce9331de2ecb27a45"


def fingerprint(path):
    with path.open("rb") as source:
        digest = hashlib.file_digest(source, "sha256").hexdigest()
    return {"path": str(path.relative_to(REPO)), "sha256_computed": digest}


def main():
    units_path = PACKAGE / "reports/units.json"
    pop_path = PACKAGE / "POP0.txt.gz"
    units = json.loads(units_path.read_text(encoding="utf-8"))["units"]
    chosen = {member for row in units for member in row["members_in"].get("POP0", [])}
    with gzip.open(pop_path, "rt", encoding="utf-8") as source:
        pop = set(source.read().splitlines())
    frequent = {}
    with gzip.open(ORTH, "rt", encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source):
            if row[""] in pop and float(row["ipm"]) >= 1:
                frequent[row[""]] = float(row["ipm"])

    db = sqlite3.connect(DATABASE.as_uri() + "?mode=ro", uri=True)
    try:
        ids = {
            ident: lemma + "@" + source
            for ident, source, lemma in db.execute("select id,source_id,lemma_id from lexeme")
            if lemma + "@" + source in chosen
        }
        assert set(ids.values()) == chosen
        forms = defaultdict(set)
        neuter = set()
        neuter_tags = Counter()
        id_list = sorted(ids)
        for offset in range(0, len(id_list), 400):
            chunk = id_list[offset:offset + 400]
            query = (
                "select i.lexeme_id,s.game_key,i.tag from interpretation i "
                "join surface_form s on s.id=i.form_id where i.lexeme_id in ("
                + ",".join("?" * len(chunk)) + ")"
            )
            for ident, word, tag in db.execute(query, chunk):
                if word in pop:
                    forms[ids[ident]].add(word)
                    fields = tag.split(":")
                    if "n" in fields and ("pri" in fields or "sec" in fields):
                        neuter.add(word)
                        neuter_tags[tag] += 1
        constructions = defaultdict(set)
        query = (
            "select c.game_key,c.lemma_id,p.source_id from derivation_candidate c "
            "join derivation_component p on p.candidate_key=c.candidate_key "
            "where p.kind='source_interpretation'"
        )
        for word, lemma, source in db.execute(query):
            member = lemma + "@" + source
            if member in chosen and word in pop:
                constructions[member].add(word)

        morphology = {}
        for word in ("remontowałoś", "przeczytałobym", "zrobiłem"):
            surface = db.execute(
                "select l.lemma_id,i.tag,i.qualifiers from surface_form s "
                "join interpretation i on i.form_id=s.id "
                "join lexeme l on l.id=i.lexeme_id where s.game_key=?",
                (word,),
            ).fetchall()
            constructed = db.execute(
                "select lemma_id,expanded_tag,rule_id from derivation_candidate where game_key=?",
                (word,),
            ).fetchall()
            morphology[word] = {
                "interpretation_columns": ["lemma_id", "tag", "qualifiers"],
                "interpretations": sorted(surface),
                "construction_columns": ["lemma_id", "expanded_tag", "rule_id"],
                "constructions": sorted(constructed),
            }
    finally:
        db.close()

    basic_union = set().union(*forms.values())
    full_union = basic_union.union(*constructions.values())
    assert full_union == pop, "Unia form wybranych leksemów różni się od pakietu POP0"
    lost_basic = sorted(member for member in chosen if not forms[member] & frequent.keys())
    lost_full = sorted(
        member for member in chosen
        if not (forms[member] | constructions[member]) & frequent.keys()
    )
    examples = [
        "administrować", "agencyjny", "agora", "aha", "aksamitny", "aktualizować",
        "alpejski", "analogowy", "animować", "anulować",
    ]
    assert all(lemma + "@sgjp-20260823" in lost_full for lemma in examples)
    result = {
        "schema_version": 1,
        "method": {
            "selection": "units[*].members_in.POP0",
            "filter": "dokładny zapis orth-all równy formie POP0; publikowane ipm >= 1",
            "basic_forms": "interpretation → surface_form, przecięte z POP0",
            "constructions": "derivation_candidate → derivation_component kind=source_interpretation, przecięte z POP0",
            "database_access": "SQLite mode=ro",
            "neuter_scope": "unikalne formy POP0 z interpretacją wybranego leksemu: osobne pola n oraz pri/sec",
            "neuter_caution": "To formy mające taką analizę, nie liczba usuwanych po uwzględnieniu pozostałych analiz.",
            "examples_caution": "Przykłady celowe, nie próbka losowa.",
        },
        "inputs": {
            "units": fingerprint(units_path),
            "pop0": fingerprint(pop_path),
            "orth": fingerprint(ORTH),
            "database": {
                "path": str(DATABASE.relative_to(REPO)),
                "sha256_pinned_not_recomputed": DB_PIN,
                "pin_source": "config/generator/pop-sources.json base.database_sha256",
            },
        },
        "counts": {
            "selected_lexemes": len(chosen),
            "mapped_lexeme_ids": len(ids),
            "lexemes_with_basic_forms": sum(bool(forms[member]) for member in chosen),
            "pop0_forms": len(pop),
            "basic_forms_union": len(basic_union),
            "full_forms_union": len(full_union),
            "full_union_equals_pop0": full_union == pop,
            "exact_orth_ipm_ge_1_forms": len(frequent),
            "lexemes_losing_all_basic_forms": len(lost_basic),
            "lexemes_losing_all_forms_with_constructions": len(lost_full),
            "neuter_pri_sec_unique_forms": len(neuter),
        },
        "lost_basic_lexemes": lost_basic,
        "lost_lexemes_with_constructions": lost_full,
        "lost_common_examples": examples,
        "neuter_tag_interpretation_counts": dict(sorted(neuter_tags.items())),
        "morphology": morphology,
    }
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["counts"], ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
