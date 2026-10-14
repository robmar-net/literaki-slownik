# Runbook: aktualizacja wiki projektu

## TL;DR
[Wiki](https://github.com/robmar-net/literaki-slownik/wiki) to krótka strona dla odwiedzających: cel projektu, rodzaje słowników, kryteria filtrowania, liczby i linki do pobrania. Szczegóły i dowody zostają w repozytorium, a wiki do nich linkuje.

**Wiki aktualizujemy w tej samej pracy, która zmienia słowniki, a nie później.** Zmiana kryteriów, nowa wersja list albo wydanie bez aktualizacji wiki to praca nieskończona.

## Key Decisions
- **Gdzie:** wiki to osobne repozytorium `robmar-net/literaki-slownik.wiki`. Lokalnie klonujemy je obok projektu: `~/Projects/Literaki/wiki-literaki-slownik` (katalog pasuje do wzorca `/wiki-*/` w `.gitignore` workspace).
- **Strony:** `Home`, `Slownik-BROAD`, `Slownik-STANDARD`, `Slownik-POP`, `Slownik-POP0`, `Boty-na-mniejszych-slownikach`, `Porownanie-z-SJP.pl`, `Brakujace-slowa-SJP.pl`, `Slowa-spoza-SJP.pl`, `Historia-zmian`, `_Sidebar`. Nowy rodzaj słownika dostaje nową stronę `Slownik-<NAZWA>` z tym samym układem.
- **Układ strony słownika:**
  - cel w 1–2 zdaniach;
  - stan: liczba słów, wersja polityki i link do pobrania albo „jeszcze niewydany”;
  - co wchodzi;
  - tabela filtrów: filtr, przykłady, podstawa;
  - linki do dokumentów decyzji.
- **Styl:** po polsku, dla gracza, bez żargonu. **Bardzo zwięźle:** krótkie punkty zamiast akapitów. W tabelach linkuj `[POP](Slownik-POP)`, nie `[[POP|Slownik-POP]]`: znak `|` rozbija kolumny. Przykład słowa przy każdym filtrze. Strona ma się mieścić na jednym ekranie.

## Kiedy aktualizować

| zdarzenie | co zmienić |
|---|---|
| nowa reguła lub zmiana kryterium (`policy.py`, konfiguracja, dokument decyzji) | tabela filtrów na stronie słownika i wiersz w `Historia-zmian` |
| build z nową wersją polityki, który dał listy | liczby słów i wersja na `Home` i stronach słowników, wiersz w `Historia-zmian` |
| nowe lub zmienione źródło (manifest `sources.json`) | tabela źródeł na `Home` |
| nowy benchmark SJP.pl | strona `Porownanie-z-SJP.pl` i wygenerowane `Brakujace-slowa-SJP.pl`, `Slowa-spoza-SJP.pl` (zob. „Porównanie z SJP.pl” w [runbooku](plan-dalszych-prac-runbook.md)) |
| `export` lub wydanie | link do pobrania, sha256 i wersja; „wersja robocza” zamienia się w numer wydania |
| start prac nad nowym słownikiem | od razu wstępna strona „W przygotowaniu”: cel, do czego, jak powstanie; link do ticketu; wiersz na `Home`, wpis w `_Sidebar`, link ze strony słownika bazowego |
| wydanie nowego słownika | ta sama strona: liczby, kryteria, pobieranie; usuń „W przygotowaniu” na wszystkich stronach |

## Procedura
1. Przygotuj klon wiki:
   ```bash
   cd ~/Projects/Literaki
   [ -d wiki-literaki-slownik ] || git clone https://github.com/robmar-net/literaki-slownik.wiki.git wiki-literaki-slownik
   git -C wiki-literaki-slownik pull --ff-only
   ```
2. Weź liczby z artefaktów, nie z pamięci:
   - liczby słów: `wc -l <run>/lists/broad.txt <run>/lists/standard.txt`;
   - wersja polityki: `VERSION` w `literaki_slownik/policy.py` (musi być zgodna z `policy_version` w `<run>/reports/decisions.json`);
   - porównanie z SJP.pl: wynik `scripts/benchmark_sjp.py`; pliki `tmp/benchmark/sjp-llpl-v<NN>.json`, `sjp-missing-llpl-v<NN>.json`, `sjp-extra-llpl-v<NN>.json`, gdzie `<NN>` to numer wydania LL-PL, nie przebiegu (`sjp-v30.json` to jeszcze przebieg v30 = wydanie v29). Zrzut listy SJP.pl: p. 1 w [runbooku](plan-dalszych-prac-runbook.md); sha256 musi się zgadzać (kolejność przejścia DAWG, bez sortowania: posortowany plik ma inny hash); strona brakujących słów: `scripts/sjp_missing_top.py` + `scripts/render_sjp_missing.py`; strona słów spoza SJP.pl: `scripts/sjp_extra_top.py` + `scripts/render_sjp_extra.py`; bez ręcznych zmian.
   - POP/POP0: formy i leksemy z `counts` w `release-manifest.json` pakietu, progi i przycięcia z `reports/thresholds.json`. Wydane: `pop-v3` (POP 1 229 303 / 53 033, POP0 388 763 / 13 896), [Release pop-v3](https://github.com/robmar-net/literaki-slownik/releases/tag/pop-v3), metoda [ADR-008](adr/ADR-008-pop-v3-staly-prog.md), opis niżej. Poprzednie: `pop-v2` (POP 1 227 250, POP0 388 509), metoda [ADR-007](adr/ADR-007-metoda-pop-v1.md). Strony `Slownik-POP` i `Slownik-POP0` idą tą samą procedurą.
   Przy liczbach podaj wersję i datę. Dopóki `verify` nie odbierze wydania, pisz „wersja robocza”.
3. Przykład przy filtrze sprawdź w liście albo przez `python3 -m literaki_slownik explain --run-dir <run> --word <słowo>`. Dla POP/POP0: `explain ... --variant pop|pop0 --pop-dir <pakiet>`. Przykład „odpada” nie może być na liście, a przykład „zostaje” musi na niej być.
4. Lista kontrolna przed commitem:
   - stara wersja polityki nie występuje nigdzie poza `Historia-zmian`: `grep -rn "v<poprzednia>" wiki-literaki-slownik`;
   - linki do plików w repo prowadzą do istniejących ścieżek na `main` (po pushu kodu);
   - z SJP.pl nie ma skopiowanych list słów, tylko liczby i pojedyncze przykłady; atrybucja CC BY 4.0 jest obecna. Wyjątek (właściciel, 2026-10-12): `Brakujace-slowa-SJP.pl` i `Slowa-spoza-SJP.pl`, po 2000 najczęstszych słów na listę, z atrybucją; nazwa innej gry słownej na liście jest ukryta;
   - każda strona ma najwyżej jeden ekran tekstu (poza wygenerowanymi `Brakujace-slowa-SJP.pl` i `Slowa-spoza-SJP.pl`).
5. Zapisz i wypchnij:
   ```bash
   git -C wiki-literaki-slownik add -A
   git -C wiki-literaki-slownik commit -m "wiki: <co się zmieniło> (v<NN>)"
   git -C wiki-literaki-slownik push
   ```

## Opis POP przy metodzie `pop-v3`
- **Kryterium:** POP i POP0 to słowa o punktacji użycia co najmniej progu listy (`thresholds.json`: `by: score`, `score`), nie „60 000” ani „20 000 najczęstszych leksemów”. Liczbę leksemów podaj jako wynik, nie jako limit.
- **Tymczasowość:** przy każdym progu napisz, że to stała tymczasowa (cięcie wydanego pop-v2), a docelowy próg ustala [#6](https://github.com/robmar-net/literaki-slownik/issues/6). Link do #6 bierz z `provisional` w `thresholds.json`.
- **Status (od 2026-10-14):** `pop-v3` wydane; strony podają jego liczby i link, a limity 60 000 i 20 000 są tylko w `Historia-zmian`. Nowa metoda (np. z #6) idzie tą samą drogą: „wersja robocza” z liczbami i datą do czasu Release.
- **Przykład:** słowo „zostaje” sprawdź przez `explain --variant pop|pop0`; dla przyciętego członka grupy podaj powód `PRUNED_WEAK_MEMBER`.

## Open Questions / Risks
- Wiki nie ma testów ani CI, więc zestarzeje się po cichu. Jedyną ochroną jest ta procedura w kroku, który zmienia słowniki (zob. `AGENTS.md`).
- Repozytorium wiki istnieje dopiero po utworzeniu pierwszej strony w przeglądarce. Po jego usunięciu trzeba je odtworzyć ręcznie.
