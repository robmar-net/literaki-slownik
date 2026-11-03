# korpusy: zestaw kontrolny 9 słów

## TL;DR
- `hejt` jest we wszystkich zmierzonych źródłach, więc jest kontrolą dodatnią dla każdego „brak”.
- ParlaMint-PL dobrze pokazuje datę wejścia słowa: `lockdown` i `covidowy` mają 0 do 2019 roku, a od 2020 setki wystąpień. `antyszczepionkowiec` skacze do 78 w 2021. Taki wzór powinna łapać metoda.
- `wulwa` w znaczeniu anatomii człowieka jest w próbkach sieciowych: FineWeb-2 ma 2 dokumenty (2020, 2022), HPLT 3 dokumenty. W ParlaMint i w LCC news 2024 jej nie ma.
- `cringe` i `ghosting` są rzadkie wszędzie i mają szum („Anti-ghosting”).

## Kluczowe decyzje
- Liczę formy wzorcem prefiksowym bez rozróżniania wielkości liter, na przykład `(?<!\w)hejt\w*` i `antyszczepionkow(?:iec|c)\w*`. To nie są lematy, bo wzorzec `hejt*` łapie też „hejter”. Liczby są górną granicą. Nie stroimy pod nie progów.
- Wikipedia: liczba stron z trafieniem w wyszukiwarce CirrusSearch (ze stemmingiem), nie wystąpień.

## Otwarte pytania
- Próbki sieciowe to <0,03% korpusu. „Brak” w próbce nie znaczy, że słowa nie ma w całym korpusie (zob. kolumnę „kontrola dodatnia”).

## Wyniki (2026-11-03)
Format: wystąpienia (dokumenty).

| Słowo | ParlaMint-PL 5.0, całość 37,0 mln słów | LCC `pol_news_2024_1M` (`-words.txt`, 15,7 mln tok.) | FineWeb-2 pol, próbka `test/000_00000` (15,1 mln słów, 36 574 dok.) | HPLT v3 pol, pierwsze 150 MB `10_1` (67,4 mln słów, 21 656 dok.) | Wikipedia pl, strony | Wikinews pl, strony |
|---|---|---|---|---|---|---|
| hejt | 366 | 294 | 165 (123) | 81 (42) | 187 („hejt” w cudzysłowie: 116) | 24 |
| lockdown | 316 | 31 | 90 (63) | 51 (35) | 508 | 3 |
| covidowy | 349 | 28 | 56 (39) | 28 (19) | 32 | 4 |
| influencerka | 1 | 96 | 25 (15) | 13 (11) | 119 | 1 |
| antyszczepionkowiec | 93 | 8 | 15 (11) | 5 (4) | 38 | 1 |
| boomer | 0 | 10 | 15 (11) | 79 (70) ⚠ szum | 142 | 1 |
| ghosting | 0 | 3 | 3 (3), 1 z nich „Anti-ghosting” | 1 (1) | 13 (w tym „Klawiatura (technologia)”) | 0 |
| cringe | 0 | 2 | 0 | 2 (2) | 23 (głównie nazwy zespołów) | 2 |
| wulwa | 0 | 0 | 2 (2): archiwumosiatynskiego.pl 2022-12-05, popaprana.pl 2020-11-29 | 19 (3) | 64 / „wulwy” 153 (głównie zoologia) | 0 |

Kontrola dodatnia przy każdym 0: `hejt` w tym samym źródle ma 24–366 wystąpień.

## ParlaMint-PL według lat (wystąpienia)
| Słowo | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 (do VI) |
|---|---|---|---|---|---|---|---|---|
| hejt | 1 | 38 | 55 | 7 | 89 | 88 | 44 | 44 |
| lockdown | 0 | 0 | 0 | 0 | 0 | 111 | 176 | 29 |
| covidowy | 0 | 0 | 0 | 0 | 0 | 153 | 153 | 43 |
| antyszczepionkowiec | 0 | 0 | 1 | 3 | 0 | 5 | 78 | 6 |
| influencerka | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |

## Rozkład lat w próbkach sieciowych (dokumenty)
- FineWeb-2: 2013: 114 · 2014: 429 · 2015: 209 · 2016: 593 · 2017: 3318 · 2018: 3765 · 2019: 4887 · 2020: 5000 · 2021: 5650 · 2022: 4776 · 2023: 5743 · 2024: 2090. Około 90% dokumentów jest z lat 2017+.
- HPLT (`ts`): 2024: 9139 · 2023: 2804 · 2016: 3342 · 2012: 1493 · 2018: 1293 · 2020: 1286 · 2015: 1047 · 2022: 905 · 2014: 209 · 2017: 138.

## Dowody (scratchpad, poza repo)
Katalog: `/private/tmp/claude-501/-Users-robmar-Projects-Literaki/3ae5c44e-c8df-4ef9-924a-bcb0e5eaf7f8/scratchpad/nowe-slowa/`
- `dl-parlamint/ParlaMint-PL.tgz`, sha256 `66739847c4454e21d524755cea17e41dd923c78cdefe03b6775e9f10720ba957`, z `https://www.clarin.si/repository/xmlui/bitstream/handle/11356/2004/ParlaMint-PL.tgz`
- `dl-lcc/pol_news_2024_1M.tar.gz`, sha256 `60f79d00b23afbeb48e9350937cb9c748b73d9a9ff6e7a06ea5197adca58762d`
- `dl-fw2/pol_test_000.parquet`, sha256 `70579d75902b50faa3a3fc6127357f1436719fcb71252b7c5b71a3c37b2d40da` (`HuggingFaceFW/fineweb-2`, `data/pol_Latn/test/000_00000.parquet`)
- `dl-hplt/pol_10_1.head.zst`: bajty 0–157286399 z `https://data.hplt-project.org/three/sorted/pol_Latn/10_1.jsonl.zst`
- skrypty: `scripts/scan.py`, `scripts/scanjsonl.py`, `scripts/ctx.py`
- Wikipedia i Wikinews: `api.php?action=query&list=search&srinfo=totalhits`
