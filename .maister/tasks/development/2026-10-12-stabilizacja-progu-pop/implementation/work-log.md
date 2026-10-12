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
