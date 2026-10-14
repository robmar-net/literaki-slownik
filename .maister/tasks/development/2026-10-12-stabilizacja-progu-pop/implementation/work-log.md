# Dziennik pracy

- 2026-10-12: Nowe zadanie development z przekazania research #4 i decyzji tymczasowej w #6. Analiza kodu wykonana inline; lokalnych szablonów agentów specjalistycznych brak. Faza zakresu czeka na odpowiedź właściciela. Kod i listy niezmienione.
- 2026-10-12T13:06:49Z: Właściciel zatwierdził 2382 dodatki STANDARD, trwały pipeline i wiki. Uzupełniono analizę kodu, wymagania i specyfikację. Testy, kod, build i wiki czekają na bramkę specyfikacji wymaganą przez Maister Development.
- 2026-10-12T13:32:13Z: Właściciel zatwierdził specyfikację odpowiedzią „ok”. Audyt specyfikacji wykonano inline (brak szablonu agenta): trzy luki doprecyzowano, wynik `passed`. Odczyt zamrożonej bazy potwierdził 7192 jednoznacznych dopasowań. Zapisano plan; implementacja czeka na wymaganą bramkę planu.
- 2026-10-12T13:44:55Z: Plan opublikowany w [#4](https://github.com/robmar-net/literaki-slownik/issues/4#issuecomment-6125514977). Właściciel wykona implementację osobno; kod, listy i wiki pozostają bez zmian.
- 2026-10-12T13:47:12Z: Właściciel zlecił implementację planu, pełną przebudowę STANDARD/POP/POP0 i wiki. Gałąź zsynchronizowana z `main` (zawiera #5 `nie-prefix-degree-v2` i `morph-index`). Uwaga do G3: delty względem v30 = 2382 dodatki #4 **oraz** ubytki #5 (pomiar: −336 STANDARD, −346 BROAD); obie przyczyny rozliczyć osobno.

## 2026-10-12 — G0 gotowa
- `config/generator/standard-age-exceptions.json` (2382 formy, 7192 analizy: 7060 źródłowych, 132 konstrukcje; 110 rodzin), SHA256 `1ad50b40…` przypięty w `sources.json`.
- Walidator `literaki_slownik/standard_age_exceptions.py` + `scripts/check_standard_age_exceptions.py`; audyt v30 (tylko odczyt, mtime bez zmian): `{1: 7192}`.
- Testy: nowe 9 + `test_inputs` = 17 OK; cały zestaw 416 OK.
- Standardy: AGENTS.md (po polsku, bez surowych danych), styl `build.py`/`canonical.load_json`.
- Uwaga: `implementation-plan.html` nie ma znaczników `class="step todo"`; synchronizacja HTML pominięta (stan w `.md`).

## 2026-10-12 — G1 gotowa
- Reguła `linguistic-standard-age-exception-v1` (tylko STANDARD, zastępuje wyłącznie `linguistic-historical-form-v1`); polityka `approved-conditions-v30`. Rozliczenie „każdy wpis dokładnie raz”, sekcja `standard_age_exceptions` w `reports/decisions.json`. `explain`: podstawa oceny (zapisana vs przeliczona), pin z manifestu przebiegu.
- Testy: 6 nowych; cały zestaw 422 OK.
- Pomiar v30 (ro): 7060 źródłowych + 74 `impt` → accept. **58 konstrukcji `nie-prefix-degree-v1` nie zaistnieje w nowym buildzie (#5).** Każda ma dokładnie jeden odpowiednik v2 (te same składniki), po wyjątku accept. Poprawka danych G0 przed G3: klucze v2, `standard-age-exceptions-v2`, nowy pin.
- Poprawka G0: 58 wpisów → `nie-prefix-degree-v2` (1:1, payload równy poza ID reguły), `standard-age-exceptions-v2`, pin `d41256af…`. Stara migawka: `--allow-missing-recomputed`. Testy 423 OK.
- Decyzja właściciela (2026-10-12): zwolnić dysk (cache Go, stare przebiegi lists-v25…v29, measure, diagnostyki import/links/g5; wolne 20 → 203 GB) i wykonać **jeden** pełny przebieg LL-PL zamiast dwóch. Odstępstwo od R1: brak porównania dwóch buildów LL-PL; deterministyczność POP nadal dwoma tanimi przebiegami. Zamrożony v30 a/b nietknięty (mtime 1791660525).

## 2026-10-12 — G2 gotowa
- `pop-v3`: POP `score ≥ −1.042878629` (remis włącznie, brak punktacji poza), przycinanie własną punktacją; POP0 `count 20000`; jawna kontrola `POP0 ⊆ POP`. `config/generator/pop-v2.json` = bajtowa kopia wydanej konfiguracji (hash zgodny z manifestem pop-v2). ADR-008; ADR-007 tylko link.
- P1 zmierzone na wydanym STANDARD v29: POP i POP0 bajtowo równe wydanemu pop-v2 (1 227 250 / 388 509), straż 0 braków, checker OK.
- Testy: 19 nowych; cały zestaw 442 OK.
- 3.1: 442 OK, kod zacommitowany `0560f20` (push). Pełny build LL-PL uruchomiony w tle: `data/work/lists-v31-20261012-162111-a` (v30 trwał ok. 12,5 h, w tym reports ~8 h).
- 4.1–4.2: `docs/generator/wyjatki-dawnosci-standard.md` (nowy), `cli.md` (pop-v3, odtworzenie pop-v2), `runbook-wiki.md` (opis pop-v3), nota w planie, INDEX. Liczby po buildzie dopisać w G4.3.
- 3.2 (jeden przebieg, decyzja właściciela): `reports/decisions.json` → 7192/7192 dopasowanych, 0 niewykorzystanych, 2382 słowa. STANDARD 3 090 194 → 3 092 240 = +2382 (dokładnie zbiór z JSON-a) −336 (#5); BROAD 3 479 364 → 3 479 018 = −346 (#5), 0 dodatków. Ubytki równe pomiarowi #5, wszystkie `nie…`. Faza reports trwa.
- 2026-10-13T06:07: przebieg A ukończony (rc 0, 13,8 h, RSS 1,9 GB). `verify` wymaga `--peer-run` (K8, cli.py:36), więc jeden przebieg nie wystarcza do verify/export/POP. Uruchomiono przebieg B `lists-v31-20261013-060725-b` (ten sam kod `f71d223d…`, do zatrzymania na życzenie właściciela). Równolegle: przegląd K9 dla A i wstępny pomiar POP w scratchpad.
- 3.3: przegląd K9 `verification/quality-review-v31.json` (1876 pozycji: 1810 przeniesionych z v30 przy identycznych jednostkach, 66 nowych; 0 błędnych, 23 niepewne). Dodatkowe warstwy: 40 dodatków #4 i 20 ubytków #5 — wszystkie trafne. K9 na A (ro) = pass. Przegląd zależy tylko od A i kodu.
- Wstępny POP na A (scratchpad, nieoficjalny): POP 1 227 250 → 1 229 303 (+2372 z #4, −319 z #5); POP0 388 509 → 388 763 (+481 z #4, −227 z #5). Brak zmian spoza #4/#5; straż 0 braków; podzbiory OK. Ryzyko: POP0 ma dokładnie 20 000 leksemów przed przycięciem (zero zapasu) — dopisać do #6.
- Optymalizacja buildu w osobnym PR #8 (cache 4 GB, `build_pair.sh`) i ticket #7; NIE łączyć z tą gałęzią przed verify (tree_sha256).
- 2026-10-13: właściciel — POP0 też stały próg punktacji (20 000 przypadkowy), od razu w pop-v3. Zmiana w worktree `tmp/wt-pop0` (gałąź `issue-6-pop0-score`); scalenie po verify/export, przed oficjalnym POP (verify wymaga niezmienionego `literaki_slownik/`).
- POP0 score: gałąź `issue-6-pop0-score` `dc6ce62` (push), stała 0.57370099, P1 bajtowo równe pop-v2, na A identyczne z cięciem 20 000. Scalić po export.
- 3.4: B ukończony (12,9 h, rc 0); listy A i B bajtowo równe. `verify` A/B + przegląd K9: **VERIFIED** (K1–K10 pass, 7,3 h). `export` → `data/work/release-LL-PL-v30` (FROZEN, release-manifest `cdc59511…`).
- 3.5–3.6: POP pop-v3 a=b, base29 = pop-v2 bajtowo, straż 0, checker OK. POP 1 229 303 (+2372/−319), POP0 388 763 (+481/−227). Raport: `verification/full-build-acceptance.md`.
- Właściciel zatwierdził wydanie. Opublikowano [llpl-v30](https://github.com/robmar-net/literaki-slownik/releases/tag/llpl-v30) (target `0560f20`) i [pop-v3](https://github.com/robmar-net/literaki-slownik/releases/tag/pop-v3) (target `015fb34`; przegląd 423: 416 trafnych, 4 błędne bez wpływu na listy, 3 niepewne). Pobrane zasoby: `shasum -c` OK.
- 4.3–4.4: wiki `8d44a44` + `0b08ee6` (linki do kodu przez tag `pop-v3`), wypchnięte po wydaniach. Strony: Home, STANDARD, BROAD, POP, POP0, Historia-zmian, Boty, trzy strony SJP.pl (przeliczone na v30: odzysk 131 z top 2000 braków dzięki #4). Benchmarki: `tmp/benchmark/sjp-*-llpl-v30.json`.
- G5: właściciel pominął weryfikację Maister. Komentarze w #4 i #6; PR #9 do main (scalenie należy do właściciela — automatyczne scalanie bez przeglądu zablokowane). Otwarte: PR #8 (cache/build_pair), #7.
