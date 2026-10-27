# Dane lokalne: KWJP100 i NKJP — metadane

## TL;DR
- Lokalne pliki KWJP i NKJP **nie mają dziedziny słowa**. KWJP ma tylko 3 podkorpusy gatunkowe, a NKJP ma same unigramy bez metadanych.
- Podkorpus „fakt” lekko faworyzuje słowa fachowe (udział 0,47–0,51 wobec 0,35 bazowo), ale nie odróżnia jednego tematu od drugiego.
- Metadane tekstów (tytuł, dziedzina książki) są tylko w sieci (zakładka „Texts” KWJP) i w próbkach `KWJP½M`, których nie mamy lokalnie.

## Key Decisions
- Nie pobierałem `KWJP½M_samples.tar.gz` (2,86 MB wg `cache/kwjp/tree.json`). To decyzja dla zbieracza `pan-resources` albo dla kolejnego kroku.

## Open Questions / Risks
- Czy `KWJP½M` albo spis tekstów KWJP ma pole dziedziny lub tematu? Lokalnie tego nie widać. `cache/kwjp/article.pdf` ma skompresowany tekst, a `pdftotext` nie jest zainstalowany, więc artykułu nie przeszukałem.

## KWJP100 (`cache/kwjp/`)
- 12 list słów: `kwjp100-slowa-{lemma,orth,orth_lc}-{all,fakt,fikcja,publicystyka}.csv.gz`, plus `kwjp100-2grams-lemma-all.csv.gz`.
- Kolumny listy lematów: lemat, POS, `freq`, `ipm`, `ARF`, `DP`, `DP_norm`, `1-DP`, `total_freq`. Bigramy mają dodatkowo `Dice`. Nie ma żadnej kolumny dziedziny.
- `cache/kwjp/lists-doc.html`: listy powstały „w podziale na trzy główne podzbiory gatunkowe korpusu: fikcję, fakt i publicystykę prasową”, z progiem „co najmniej 5 razy”.
- `cache/kwjp/overview.html`: książki wybrano „from various thematic areas”, a spis tekstów jest „in the Texts tab”. Obszar tematyczny jest więc cechą tekstu w serwisie, nie słowa na liście.
- `cache/kwjp/README.source.md`: `KWJP½M` to próbki po 40–60 słów, pół miliona słów; licencja CC BY 4.0 dla całego repozytorium `kwjp100-varia`.
- Pomiar (`kwjp.py` w `/private/tmp/claude-501/-Users-robmar-Projects-Literaki/7eed58b5-7e1f-4a3f-8359-d9bc24330c2b/scratchpad/td/`): tokeny lematów: all 81 664 894, fakt 28 579 794 (udział 0,35). Udział „fakt” we frekwencji leksemów z etykietą: morze 0,51 (75 lematów w KWJP), matematyka 0,466 (25), rolnictwo 0,348 (17 lematów; sumę zawyża pospolity homograf). Sygnał mówi „literatura faktu”, nie „temat”.

## NKJP (`cache/nkjp/`)
- `1grams.gz`: format `liczba forma`, np. `7692997 w`. Formy z małej litery, bez lematu, bez POS, bez metadanych.
- `nkjp-page.html`: n-gramy z podkorpusu zrównoważonego (300 mln segmentów), „made available on CC-BY licence”. Strona nie podaje podziału na gatunki ani dziedziny.
- `polimorf-page.html`, `Morfeusz2.pdf`: słownik morfologiczny. Kwalifikatory dziedzin pochodzą tu z SGJP (zob. `local-data-sgjp-dziedziny.md`); nic nowego lokalnie.

## Baza przebiegu
`build.sqlite` v31 ma źródła `sgjp-20260823`, `sgjp-supplement-v1`, 13 źródeł KWJP100 i `own-semantic-use-review-v1` (`select source_id, kind from source_artifact`, `?mode=ro`). NKJP nie jest w bazie. Żadne źródło poza SGJP nie niesie dziedziny.
