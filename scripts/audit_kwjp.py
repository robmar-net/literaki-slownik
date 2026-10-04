#!/usr/bin/env python3
"""Odtwarzalny audyt 13 plików KWJP100; nie buduje słownika gry.

Uruchomienie: python3 scripts/audit_kwjp.py [--fetch]
Surowe dane pozostają w cache/kwjp, raporty w katalogu zadania.
Źródło: IPI PAN, kwjp100-varia, CC BY 4.0; wersja poniżej.
"""
import argparse
import csv
import gzip
import hashlib
import json
import math
import subprocess
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

COMMIT = "26d82bd8b906dfed1cfcf8f903b1650b56daeabf"
ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "cache/kwjp"
OUT = ROOT / ".maister/tasks/research/2026-10-04-audyt-zrodel-polskich-slownikow/analysis/findings"
BASE = f"https://raw.githubusercontent.com/ipipan/kwjp100-varia/{COMMIT}/"
FILES = [f"kwjp100-slowa-{kind}-{genre}.csv.gz" for kind in ("lemma", "orth", "orth_lc")
         for genre in ("all", "fakt", "fikcja", "publicystyka")] + ["kwjp100-2grams-lemma-all.csv.gz"]
QUERIES = {"zamek", "mam", "Róża", "róża", "czytałem", "czytał", "em", "bym", "kot", "kotem", "słownik", "spacjalny", "nie", "Warszawa"}


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def rows(path):
    with gzip.open(path, "rt", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        keys = (["lemma", "pos"] if "-slowa-lemma-" in path.name else
                ["unit_1", "unit_2"] if "-2grams-" in path.name else ["form"])
        assert header[:len(keys)] == [""] * len(keys), header
        keys += header[len(keys):]
        for rank, raw in enumerate(reader, 1):
            assert len(raw) == len(keys), (path, rank, raw)
            yield header, keys, rank, dict(zip(keys, raw))


def inspect(path):
    numeric = ("freq", "ipm", "ARF", "DP", "DP_norm", "1-DP", "Dice", "total_freq")
    mins, maxs, blanks, zero = {}, {}, Counter(), Counter()
    n = 0
    counts = Counter()
    pos = Counter()
    selected, first, last, low, anomalies = [], [], [], [], []
    previous = float("inf")
    total = 0
    seen = set()
    unit_col = "lemma" if "-slowa-lemma-" in path.name else "unit_1" if "-2grams-" in path.name else "form"
    for header, keys, rank, r in rows(path):
        n += 1
        unit = r[unit_col]
        key = tuple(r[k] for k in keys if k not in numeric)
        if key in seen:
            counts["duplicate_keys"] += 1
        seen.add(key)
        for k in numeric:
            if k not in r:
                continue
            if not r[k]:
                blanks[k] += 1
                continue
            v = float(r[k])
            assert math.isfinite(v), (path.name, rank, k, r[k])
            mins[k], maxs[k] = min(mins.get(k, v), v), max(maxs.get(k, v), v)
            zero[k] += v == 0
        f = float(r["freq"])
        total += int(f)
        counts["noninteger_freq"] += not f.is_integer()
        counts["freq_increases"] += f > previous
        previous = f
        counts["freq_below_5"] += f < 5
        counts["total_freq_below_5"] += float(r["total_freq"]) < 5
        counts["freq_gt_total_freq"] += f > float(r["total_freq"])
        counts["non_nfc_units"] += unicodedata.normalize("NFC", unit) != unit
        counts["uppercase_units"] += unit != unit.lower()
        counts["hyphen_units"] += "-" in unit
        counts["whitespace_units"] += any(c.isspace() for c in unit)
        counts["non_latin_letter_or_hyphen_units"] += any(c != "-" and (not c.isalpha() or "LATIN" not in unicodedata.name(c, "")) for c in unit)
        if (any(c.isspace() for c in unit) or unicodedata.normalize("NFC", unit) != unit or
                any(c != "-" and (not c.isalpha() or "LATIN" not in unicodedata.name(c, "")) for c in unit)) and len(anomalies) < 20:
            anomalies.append({"derived_file_row_rank": rank, **r})
        if "pos" in r:
            pos[r["pos"]] += 1
        if rank <= 3:
            first.append({"derived_file_row_rank": rank, **r})
        last = [{"derived_file_row_rank": rank, **r}]
        if unit in QUERIES and len(selected) < 100:
            selected.append({"derived_file_row_rank": rank, **r})
        if f < 5 and len(low) < 3:
            low.append(r)
    max_ipm_difference = max(abs(float(r["ipm"]) - float(r["freq"]) * 1000000 / total)
                             for _, _, _, r in rows(path))
    return dict(file=path.name, bytes=path.stat().st_size, sha256=sha(path), rows=n,
                header=header, parsed_columns=keys, minimum=mins, maximum=maxs,
                empty_values=dict(blanks), observed_zero_counts=dict(zero), checks=dict(counts),
                pos_counts=dict(pos), sum_published_freq=total, first_rows=first, last_rows=last,
                illustrative_query_matches=selected, illustrative_below_5=low,
                illustrative_unit_anomalies=anomalies,
                max_ipm_difference_from_published_list_sum=max_ipm_difference,
                implied_ipm_denominator_first_row=float(first[0]["freq"]) / float(first[0]["ipm"]) * 1000000)


def genre_check(kind):
    values = {}
    for genre in ("all", "fakt", "fikcja", "publicystyka"):
        for _, _, _, r in rows(CACHE / f"kwjp100-slowa-{kind}-{genre}.csv.gz"):
            key = (r["lemma"], r["pos"]) if kind == "lemma" else (r["form"],)
            values.setdefault(key, {})[genre] = int(float(r["freq"]))
    counts = Counter()
    mismatches = []
    for key, v in values.items():
        if len(v) != 4:
            counts["keys_missing_genre_row"] += 1
            continue  # Missing is not zero.
        counts["keys_with_all_four_rows"] += 1
        if sum(v[g] for g in ("fakt", "fikcja", "publicystyka")) != v["all"]:
            counts["frequency_sum_mismatch"] += 1
            if len(mismatches) < 5:
                mismatches.append({"key": key, "values": v})
    return {"kind": kind, "counts": dict(counts), "mismatch_examples": mismatches}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch", action="store_true")
    args = parser.parse_args()
    CACHE.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    if args.fetch:
        for name in FILES:
            if not (CACHE / name).exists():
                subprocess.run(["curl", "-fL", "--max-time", "120", BASE + "freqlists/" + name,
                                "-o", str(CACHE / name)], check=True)
    previous_registry = OUT / "kwjp-source-registry.json"
    if previous_registry.exists():
        expected = {r["ARTIFACT_NAME"]: r["SHA256"] for r in json.loads(previous_registry.read_text())}
        for name in FILES:
            if name in expected:
                assert sha(CACHE / name) == expected[name], (name, "SHA256 inny niż utrwalony rejestr")
    tree_path = CACHE / "tree.json"
    tree_verification = "UNAVAILABLE — brak metadanych drzewa Git; pozostają SHA256 pobranych plików"
    if tree_path.exists():
        tree = {r["path"]: r for r in json.loads(tree_path.read_text())["tree"]}
        for name in FILES:
            data = (CACHE / name).read_bytes()
            actual = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
            assert actual == tree["freqlists/" + name]["sha"], (name, "Niezgodny obiekt Git")
        tree_verification = "13/13 pobranych plików zgodnych z identyfikatorem obiektu blob drzewa przypiętego commitu"
    result = {"commit": COMMIT, "method": "Pełny odczyt każdego wybranego CSV UTF-8; bez filtrowania wierszy.",
              "git_tree_verification": tree_verification,
              "artifacts": [inspect(CACHE / name) for name in FILES],
              "genre_consistency": [genre_check(k) for k in ("lemma", "orth", "orth_lc")]}
    (OUT / "kwjp-statistics.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    artifacts = []
    for stats in result["artifacts"]:
        name = stats["file"]
        artifacts.append({
            "SOURCE_ID": "KWJP100-" + name.removesuffix(".csv.gz"),
            "SOURCE_NAME": "Korpus Współczesnego Języka Polskiego — listy KWJP100",
            "ARTIFACT_NAME": name, "VERSION": COMMIT, "RELEASE_DATE": "2026-05-28T10:34:44Z (commit repozytorium, nie data wygenerowania CSV)",
            "DOWNLOAD_URL": BASE + "freqlists/" + name,
            "RETRIEVED_AT": datetime.fromtimestamp((CACHE / name).stat().st_mtime, timezone.utc).isoformat(),
            "SHA256": stats["sha256"], "OWNER_AUTHORS": "Instytut Podstaw Informatyki PAN; zespół KWJP (Marciniak i in., 2023; Kieraś i in., 2025)",
            "LICENSE_NAME": "Creative Commons Attribution", "LICENSE_VERSION": "4.0",
            "LICENSE_URL": "https://creativecommons.org/licenses/by/4.0/",
            "LICENSE_EVIDENCE": f"https://github.com/ipipan/kwjp100-varia/blob/{COMMIT}/README.md",
            "LICENSE_SCOPE": "Wszystkie zasoby zamieszczone w repozytorium, w tym ten plik freqlists; nie przenosimy deklaracji na pełne teksty całego korpusu ani witrynę.",
            "USED_FOR": "Audyt struktury i pomiary; pilotaż dopasowania SGJP oraz projekt miar znajomości; nie rozszerzanie leksemów.",
            "ATTRIBUTION_REQUIRED": True,
            "ATTRIBUTION_TEXT": f"Źródło danych: Korpus Współczesnego Języka Polskiego (IPI PAN), kwjp100-varia, commit {COMMIT}, CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Audyt i wyliczenia: projekt literaki-slownik; przetworzono format i obliczono statystyki. Autorzy i zalecane cytowanie: https://kwjp.pl/overview.",
            "KNOWN_DERIVATION_ANNOTATION_DEPENDENCIES": "Listy z KWJP100; automatyczna Hydra, korekta lematów Morfeusz SGJP. Składnia Hydra/HerBERT, PDB/Składnica; nazwy PolDeepNer2/NKJP1M. Nieustalone wersje modeli/słownika anotacji i pełne pochodzenie danych treningowych; nie są to bezpośrednie wejścia generatora.",
            "STATUS": "ALLOWED", "BLOCK_REASON": None,
            "NOTES": "Próg total_freq >=5; freq gatunkowe ma minimum 1 w pobranych danych. Opublikowane 1-DP=0 zachowujemy jako OBSERVED; brak wiersza nie jest zerem. Rank jest wyliczonym numerem wiersza, nie dostarczoną kolumną R."
        })
    (OUT / "kwjp-source-registry.json").write_text(json.dumps(artifacts, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"artifacts": len(artifacts), "rows": {a["file"]: a["rows"] for a in result["artifacts"]}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
