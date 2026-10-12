# Pomiar `morph-index` (#1862, 2026-10-12)

**Wniosek:** indeks ma 30,3 MB (gzip -9: 11,1 MB), mieści się w budżecie 40 MB. Dwa przebiegi dały identyczny plik. Budowa trwa ok. 36 s.

Zadanie i specyfikacja leżą w repo workspace Literaki: `.maister/tasks/development/2026-10-12-polish-explanations-base-word/` (etap B). Próba formatu: `.maister/tasks/research/2026-10-12-polskie-definicje-dla-broad/analysis/index-spike/`.

## Wejścia

| Plik | SHA-256 |
|---|---|
| `tmp/release-v29/LL-PL-BROAD.txt.gz` (po rozpakowaniu) | `9be96245f5156af1879b68b85d870f65f5da9e46d1d575277e40456341f72f1a` |
| `cache/sgjp/sgjp-20260823.tab.gz` | `3b2ee079143bc95186370fd528735779c4ba62f4ce14e30cf6622ceb566e9810` |
| `--broad-dawg-sha256` (z `lexicons/pl-broad-20261011.sha256` w `origin/main` serwera) | `84611043cbe483199e8da94f94a367159cee1056f61c04785a2406bb7a48c59c` |

Kod: commit `208f7fc` (pole `builder` = `literaki-slownik 208f7fc`). Maszyna: Apple M3 Pro, Python 3.14.0.

```sh
python3 -m literaki_slownik morph-index --broad tmp/release-v29/LL-PL-BROAD.txt.gz \
  --sgjp cache/sgjp/sgjp-20260823.tab.gz --broad-lexicon-id pl-broad-20261011 \
  --broad-dawg-sha256 84611043cbe483199e8da94f94a367159cee1056f61c04785a2406bb7a48c59c --out <plik>.bin
```

## Wyniki

| Miara | Przebieg 1 | Przebieg 2 |
|---|---:|---:|
| Bajty | 30 261 866 | 30 261 866 |
| gzip -9 (`mtime=0`) | 11 147 869 | 11 147 869 |
| SHA-256 | `f7964de159457537469eec36ebe5d5b931030030d5d350a6c4cb8dded6aff2a4` | to samo |
| Czas (real) | 35,71 s | 35,57 s |

Szczytowa pamięć (przebieg próbny, `/usr/bin/time -l`): 2,74 GB.

Liczby: 3 382 115 form z analizą z 3 479 364 form BROAD; 5 007 162 wiersze SGJP dla tych form; 609 118 reguł, 456 354 list reguł, 29 628 końcówek lematów, 670 tagów, 582 zestawy kwalifikatorów.

Sekcje (bajty): końcówki 415 036, tagi 19 885, kwalifikatory 9 155, reguły 5 482 062, listy 4 291 146, formy 20 044 291.

## Zgodność z eksportem

Niezależny czytnik z `tests/test_morph_index.py` odczytał cały plik. Dla każdej z 3 382 115 form lista (lemat, tag, kwalifikatory) jest równa wierszom eksportu tej formy, w kolejności eksportu, bez powtórzeń. Różnic: 0.

## Różnice względem próby (#1857)

| Miara | Próba | v1 | Powód |
|---|---:|---:|---|
| Bajty | 30 257 269 | 30 261 866 (+4 597) | nagłówek v1 (ok. 260 B) i więcej list |
| gzip | 12 517 982 (`gzip -9`) | 11 147 869 | numery reguł i końcówek w kolejności eksportu, nie mapy Go |
| Listy reguł | 455 445 | 456 354 (+909) | lista zachowuje kolejność eksportu; ten sam zbiór reguł w innej kolejności to inna lista |
| Końcówki lematów | 29 644 | 29 628 (−16) | `cut` do granicy znaku: końcówka zawsze jest poprawnym UTF-8 (np. `mąk` → `męka`: cut 3, końcówka `ęka`) |
| Reguły | 609 118 | 609 118 | — |
| Formy z analizą | 3 382 115 | 3 382 115 | — |
