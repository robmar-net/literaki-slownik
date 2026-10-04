#!/usr/bin/env python3
"""Inspekcja formatu NKJP; nie buduje słownika ani nie łączy źródeł.

Surowe wejście pozostaje w ignorowanym cache. Wynik zawiera wyłącznie
agregaty techniczne, bez listy form ani częstości poszczególnych form.
"""
import argparse
import collections
import datetime
import gzip
import hashlib
import json
from pathlib import Path
import re
import struct
import unicodedata


def audit(path):
    raw = path.read_bytes()
    counters = collections.Counter({"not_matching_padded_frequency_space_token_lf": 0})
    frequency_sum = 0
    frequency_min = None
    frequency_max = None
    previous_frequency = None
    decompressed_hash = hashlib.sha256()
    decompressed_bytes = 0
    pl_alphabet = set("aąbcćdeęfghijklłmnńoóprsśtuwyzźż")
    for line in gzip.open(path, "rb"):
        decompressed_hash.update(line)
        decompressed_bytes += len(line)
        counters["lines"] += 1
        text = line.decode("utf-8")
        counters["lines_ending_lf"] += text.endswith("\n")
        counters["lines_with_cr"] += "\r" in text
        match = re.fullmatch(r" *([0-9]+) (.+)\n", text)
        if not match:
            counters["not_matching_padded_frequency_space_token_lf"] += 1
            continue
        frequency, token = int(match[1]), match[2]
        counters["frequency_field_width_7"] += len(text) - len(token) - 1 == 8
        counters["parsed_records"] += 1
        frequency_sum += frequency
        frequency_min = frequency if frequency_min is None else min(frequency, frequency_min)
        frequency_max = frequency if frequency_max is None else max(frequency, frequency_max)
        counters["frequency_equal_1"] += frequency == 1
        counters["frequency_below_5"] += frequency < 5
        counters["frequency_zero"] += frequency == 0
        if previous_frequency is not None:
            counters["descending_frequency_order_violations"] += frequency > previous_frequency
        previous_frequency = frequency
        counters["tokens_with_whitespace"] += any(ch.isspace() for ch in token)
        counters["tokens_changed_by_lower"] += token.lower() != token
        counters["tokens_changed_by_nfc"] += unicodedata.normalize("NFC", token) != token
        counters["tokens_only_unicode_letters"] += token.isalpha()
        counters["tokens_only_pl_alphabet"] += set(token) <= pl_alphabet
        counters["tokens_with_punctuation"] += any(unicodedata.category(ch).startswith("P") for ch in token)
        counters["tokens_with_digit"] += any(ch.isdigit() for ch in token)
        counters["tokens_with_hyphen_minus"] += "-" in token
        counters["tokens_with_period"] += "." in token
        counters["tokens_with_apostrophe"] += "'" in token or "’" in token
        counters["tokens_over_15_codepoints"] += len(token) > 15
    return {
        "purpose": "Inspekcja techniczna zablokowanego wejścia; bez generowania i dopasowywania źródeł",
        "input": str(path),
        "sha256_compressed": hashlib.sha256(raw).hexdigest(),
        "compressed_bytes": len(raw),
        "gzip_mtime_utc_not_release_date": datetime.datetime.fromtimestamp(struct.unpack("<I", raw[4:8])[0], datetime.timezone.utc).isoformat(),
        "gzip_flags": raw[3],
        "decompressed_bytes": decompressed_bytes,
        "sha256_decompressed": decompressed_hash.hexdigest(),
        "unicode_database_version": unicodedata.unidata_version,
        "counts": dict(sorted(counters.items())),
        "frequency_min": frequency_min,
        "frequency_max": frequency_max,
        "sum_published_frequencies_not_assumed_corpus_size": frequency_sum,
        "unique_tokens_measured": False,
        "status_for_generation": "BLOCKED",
        "block_reason": "Deklaracja CC-BY bez wersji i wskazania właściwego tekstu warunków; wymaga wyjaśnienia.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = audit(args.input)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
