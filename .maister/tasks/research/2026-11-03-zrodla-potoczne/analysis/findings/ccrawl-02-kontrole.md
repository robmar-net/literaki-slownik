# ccrawl: kontrole na większej próbce FineWeb-2 i HPLT v3

## TL;DR
- Próbka: **FineWeb-2 187,7 mln słów** (455 000 dok.; 12,4× więcej niż w #16) i **HPLT v3 475,0 mln słów** (708 892 dok.; 7,0× więcej niż w #16). Łącznie 662,7 mln słów, czyli 8,0× więcej niż w #16. Cel 10× osiągnęła tylko część FineWeb-2. Przyczyna: maszyna była obciążona (load 25–45, swap pełny), a skan pod `taskpolicy -b` dawał ok. 4–5 mln słów/min. Trzecia część HPLT (`7_1`) została przerwana po 40 mln słów.
- Kontrole dodatnie są mocne i datują się poprawnie: `lockdown` ma 0 przed 2020 i 1037/1776 trafień od 2020; `covidowy` podobnie.
- Cele: **wulwa** 3+3 trafienia (2+2 dok.), wszystkie w znaczeniu anatomii człowieka. **cringe** 9 / 16, prawie wszystkie potoczne. **ghosting** 33 / 79, ale w 80–50% to „anti-ghosting” i powidoki monitora; znaczenie relacyjne ma tylko 2/27 i 5/45 kontekstów. **boomer** 36 / 128, przy dużym szumie (manicure „baby boomer”, nicki).
- SJP.pl: 7 i 54 dokumenty z hosta `sjp.pl` (≤0,008%). Kopie z sygnaturą SJP na innych domenach: 7 i 36 dok. Żadna kontrola nie miała trafienia na stronach SJP ani na ich kopiach. Skażenie pomijalne po filtrze hosta i sygnatury.

## Kluczowe decyzje
- Liczę **dokładne formy** z `kontrole.json` (pełne paradygmaty), osobno małą (`lc`) i wielką literą (`cap`). Wzorzec prefiksowy z #16 (`pref`) podaję tylko dla porównania. Kalibracja: na próbce z #16 skrypt odtworzył liczby #16 co do jednego (hejt 165, lockdown 90, wulwa 2).
- Flagi dokumentu: `sjp` (host sjp.pl), `copy` (tekst zawiera „sjp.pl” lub „dopuszczalne w grach”), `en` (>2% tokenów to angielskie słowa funkcyjne), `ok` (reszta). Liczby `lc_ok` to wynik po filtrze szumu.
- Rok to **rok crawla** (`date` w FineWeb-2, `ts` w HPLT), a nie rok publikacji. Wzrost „po 2019” jest więc opóźniony i rozmyty.

## Otwarte pytania i ryzyka
- HPLT ma tylko kilka lat crawla na shard (np. 2020 i 2024), więc podział na lata jest tam nierówny. Lepsze do trendu jest FineWeb-2 (96 zrzutów 2013–2024).
- Kontekstów do oceny znaczenia było ≤40 na lemat w każdym kawałku po 40 mln słów, więc klasyfikacja znaczeń to próba, nie pełne liczenie.
- Liczby są **przed** filtrem opt-out ([`ccrawl-04-optout.md`](ccrawl-04-optout.md)).

## Wyniki: wystąpienia małą literą (dokumenty), filtr `ok`, `cap` = wielką literą

| Słowo | FW2 lc (dok.) | FW2 cap | FW2 ipm lc | HPLT lc (dok.) | HPLT cap | HPLT ipm lc | #16 FW2 / HPLT (prefiks) |
|---|---|---|---|---|---|---|---|
| hejt | 1009 (685) | 108 | 5,40 | 1718 (1216) | 174 | 3,68 | 165 / 81 |
| lockdown | 1019 (697) | 82 | 5,52 | 1740 (1155) | 171 | 3,74 | 90 / 51 |
| covidowy | 617 (421) | 52 | 3,31 | 1109 (734) | 46 | 2,34 | 56 / 28 |
| antyszczepionkowiec | 124 (96) | 39 | 0,67 | 181 (113) | 16 | 0,39 | 15 / 5 |
| boomer | 30 (17) | 28 | 0,19 | 125 (98) | 51 | 0,27 | 15 / 79 |
| ghosting | 32 (25) | 12 | 0,18 | 77 (39) | 24 | 0,17 | 3 / 1 |
| cringe | 9 (8) | 0 | 0,05 | 16 (15) | 8 | 0,03 | 0 / 2 |
| wulwa | 3 (2) | 3 | 0,016 | 3 (2) | 3 | 0,006 | 2 / 19 |

Wzorzec prefiksowy zawyża liczby: `boomer*` daje 260 i 648 (głównie „boomerang”), a `wulw*` 32 i 32 (m.in. „Wulwa” w zoologii).

## Lata crawla (FineWeb-2, lc, bez `sjp`)
| Słowo | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 (do IV) |
|---|---|---|---|---|---|---|---|---|
| hejt | 90 | 93 | 158 | 143 | 145 | 131 | 175 | 70 |
| lockdown | 0 | 0 | 0 | 101 | 502 | 230 | 156 | 48 |
| covidowy | 0 | 0 | 0 | 43 | 271 | 178 | 110 | 19 |
| antyszczepionkowiec | 1 | 6 | 14 | 7 | 43 | 28 | 22 | 3 |
| influencerka | 0 | 2 | 23 | 12 | 44 | 63 | 59 | 25 |
| boomer | 0 | 1 | 1 | 1 | 7 | 6 | 20 | 0 |
| ghosting | 1 | 5 | 7 | 1 | 4 | 1 | 11 | 3 |
| cringe | 0 | 1 | 1 | 0 | 3 | 0 | 2 | 2 |
| wulwa | 0 | 1 | 0 | 0 | 0 | 0 | 2 | 0 |

Słowa wg roku crawla są nierówne: ok. 90% przypada na lata 2017+ (jak w #16). Dlatego trend czytamy z ipm, nie z surowych liczb. `boomer` rośnie dopiero od 2021, czyli zgodnie z wejściem znaczenia „starszy, nienadążający”.

## Znaczenia (próba kontekstów, `scripts/sens.py`, reguły słów kluczowych)
| Słowo | FW2: kontekstów / hostów | FW2: podział | HPLT: kontekstów / hostów | HPLT: podział |
|---|---|---|---|---|
| ghosting | 27 / 26 | technika 22, relacje 2, inne 3 | 45 / 34 | technika 23, relacje 5, inne 17 |
| boomer | 25 / 20 | potoczne/ogólne 16, manicure 6, pokolenie 2, nick 1 | 111 / 50 | nick/powtórki 47, potoczne 40, manicure 19, pokolenie 5 |
| cringe | 8 / 8 | potoczne 5, cytat/tytuł 3 | 15 / 15 | potoczne 8, cytat/tytuł 7 |
| wulwa | 2 / 2 | anatomia człowieka 2 | 2 / 2 | anatomia człowieka 2 |

Wulwa: seksualnosc-kobiet.pl (2018), publio.pl (2023), wrownowadze.blogspot.com (2021), extradomy.com.pl (2024). Z #16 dochodzą archiwumosiatynskiego.pl i popaprana.pl. Razem to 6 niezależnych hostów z lat 2018–2024, wszystkie w znaczeniu anatomicznym, ale rzadko: ipm 0,006–0,016.

## Ekstrapolacja na całość (liniowo, 95% przedział Poissona, lc)
Mnożnik FW2: 73,12 mld / 187,7 mln = **389×**. HPLT v3 pol_Latn ma 406,6 GB `zst` (suma 19 shardów, HEAD 2026-11-03); przy 0,29–0,38 słowa/bajt (zmierzone na 5_1 i 9_1) daje to ok. 120–155 mld słów, czyli mnożnik **≈250–330×**.

| Słowo | FW2 cała (szac.) | HPLT cała (szac.) |
|---|---|---|
| wulwa | ~1 200 (240–3 400) | ~900 (160–2 900) |
| cringe | ~3 500 (1 600–6 700) | ~4 600 (2 300–8 600) |
| ghosting (wszystkie) / relacyjny ≈10–20% | ~12 500 / ~1 200–2 500 | ~22 000 / ~2 500 |
| boomer (bez szumu ≈60%) | ~11 700 / ~7 000 | ~36 000 / ~15 000 |
| lockdown | ~400 000 | ~500 000 |

Wniosek: w całych zbiorach każda kontrola-cel ma setki–tysiące trafień. Pobranie całości (432 GB / 407 GB) nie mieści się w limicie. Do kart wystarczy próbka 1–2 mld słów z filtrem znaczenia.

## Dowody (scratchpad, poza repo)
`/private/tmp/claude-501/-Users-robmar-Projects-Literaki/3ae5c44e-c8df-4ef9-924a-bcb0e5eaf7f8/scratchpad/potoczne/ccrawl/`
- skrypty: `scripts/fw2_sparse.py` (row groups przez HTTP Range do pliku rzadkiego), `scan.py`, `merge.py`, `sens.py`, `neo.py`, `neogroup.py`, `optout.py`, `hosts_fw2.py`, `probe.py` (nieuruchomiony)
- wyniki: `out/scan/*.part*.json.gz`, `out/merge.txt`, `out/ctx-*.json` (konteksty tylko lokalnie), `out/sens.json`, `out/pobrania.txt` (sha256 prefiksów HPLT i numery row groups)
- pobrania: FineWeb-2 `train/{000_00000,001_00001,002_00002}.parquet`, co druga z ~300 row groups rozłożonych po shardzie; HPLT v3 `sorted/pol_Latn/{9_1,5_1,7_1}` (pierwsze 650 MB). Wszystkie pobrania skasowane; łącznie pobrano ok. 8,9 GB, w tym 5 shardów FW2 i 3 prefiksy HPLT nieużyte z powodu czasu.
