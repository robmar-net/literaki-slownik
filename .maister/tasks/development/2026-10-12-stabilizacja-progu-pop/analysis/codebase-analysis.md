# Analiza kodu: tymczasowa stabilizacja POP (#6)

## TL;DR

POP wybiera grupy według limitu 60 000 leksemów przed przycięciem; potem przycina ich członków według własnej rangi.
Badany stały próg wymaga zmiany obu kroków tylko dla POP. POP0 pozostaje przy limicie 20 000.
Konfiguracja, raport progów, `explain`, testy, ADR, CLI i wiki opisują obecny limit; zmiana musi być spójna w tych miejscach.
Badanie odtworzyło obecny POP i pokazało dla proponowanego STANDARD +2372/0, ale nie dowodzi merytorycznej trafności progu.

## Key Decisions

- Właściciel wybrał tymczasową stabilizację stałym progiem dzisiejszego cięcia (`score ≥ −1,042878629`); docelowa granica POP pozostaje otwarta w #6.
- Ten etap analizy nie zmienia kodu ani wydanej listy. Zakres dodatków STANDARD z #4 wymaga doprecyzowania.

## Open Questions / Risks

- Próg zapisany z dziewięcioma miejscami trzeba porównać z rzeczywistą wartością graniczną; zaokrąglenie nie może zmienić zbioru bazowego.
- Ta sama wartość punktacji przy zmianie korpusów, mapowania lub grup może dać ubytki. Nie wolno obiecywać ogólnej monotoniczności.
- Dotychczasowy warunek konfiguracji wymaga obu progów typu `count` oraz `POP0 < POP` w jednej mierze. Mieszany układ potrzebuje jawnej walidacji własności `POP0 ⊆ POP`.

## Interpretacja i zakres

Zadanie dotyczy selekcji POP po zbudowaniu STANDARD, bez zmiany reguł dopuszczalności ani POP0. Źródłem są [raport kalibracji](research-context/pop-calibration.md) i [pierwszy raport badania](research-context/research-report.md) z zadania research `2026-10-12-standard-formy-dawne`. Dodatki +2382 form i osobne cofnięcia nie należą automatycznie do implementacji #6.

## Ścieżka wykonania

1. `config/generator/pop.json` ustala wersję, D3, D5 i D6; `pop.load_config()` sprawdza ścisły schemat oraz zgodność z ADR-007 (`literaki_slownik/pop.py:1246–1368`). Obecnie D6 dopuszcza tylko dwa limity liczby.
2. `build_pop()` wczytuje przypięty, zamrożony STANDARD, bazę i NKJP, buduje jednostki `e-common`, odrzuca grupy samych nazw własnych, mierzy ich log-ipm i ranguje (`pop.py:1543–1577`).
3. `threshold()` wybiera prefiks jednostek do limitu, nie dzieląc remisu miary (`pop.py:893–973`). Wariant punktacyjny musi uwzględniać wszystkie jednostki o wyniku nie mniejszym od progu.
4. `member_units()`, `measure()` i `prune_members()` wyliczają własne dowody członków grup; dziś warunkiem jest własna ranga w granicy listy (`pop.py:980–1127`). Badany wariant POP porównuje własną punktację z progiem, zachowując najmocniejszy człon i grupy bez odrębnego dowodu.
5. `forms_for()` pobiera pełne formy zachowanych leksemów z STANDARD; następnie kontrolowane są `POP0 ⊆ POP ⊆ STANDARD`, wymagany `kot`, straż częstych form i hash bazy (`pop.py:1585–1659`).
6. `write_package()` zapisuje deterministyczne listy, `reports/thresholds.json`, manifest i hashe (`pop.py:1861–1903`). `scripts/check_pop_package.py` jest niezależnym czytnikiem pakietu. `literaki_slownik/explain.py:343–412` pokazuje powód braku formy; jego tekst dziś mówi o randze członka.

## Wzorce do ponownego użycia

- Punktacja `measure()` jest wspólna dla jednostek i członków. Nie trzeba tworzyć nowej miary ani ruszać źródeł.
- Badawczy `analysis/round5_measure.py` z poprzedniego zadania ma referencyjne `score_cut()` i `value_prune()`. To kod badawczy, nie import produkcyjny.
- Konfiguracja i pakiet są wersjonowane oraz przypięte hashami; nowe uruchomienie nie nadpisuje katalogu. `docs/adr/ADR-007-metoda-pop-v1.md` wymaga nowej wersji metody lub rewizji ADR przy zmianie.

## Testy i konsumenci

- `tests/test_pop.py` sprawdza D6, remisy, przycinanie, podzbiory, raport i pakiet. `tests/test_pop_v2.py` sprawdza warianty lematu, straż, konfigurację i budowę.
- `tests/pop_helpers.py:165` zastępuje D6 małymi limitami fikstury; powinien zachować możliwość testowania starej ścieżki oraz dopuścić nową konfigurację testową.
- `docs/generator/cli.md` i `docs/runbook-wiki.md` opisują obecną metodę. Lokalny `AGENTS.md` wymaga aktualizacji wiki w tej samej pracy przy zmianie kryterium.
- Serwer gry nie jest częścią tego repo ani tego etapu. Wydanie pakietu i integracja z grą wymagają osobnej decyzji zapisanej w #6.

## Status

- status: analiza ukończona
- summary: Zlokalizowano obie zmiany algorytmu, ścisły kontrakt konfiguracji i powierzchnie dokumentacyjne.
- files_found: `literaki_slownik/pop.py`, `literaki_slownik/explain.py`, `config/generator/pop.json`, `tests/test_pop.py`, `tests/test_pop_v2.py`, `tests/pop_helpers.py`, `scripts/check_pop_package.py`, `docs/adr/ADR-007-metoda-pop-v1.md`, `docs/generator/cli.md`, `docs/runbook-wiki.md`
- complexity: średnia
- risk_level: wysokie dla integralności list, ograniczone przez porównanie pełnych zbiorów na przypiętych danych
