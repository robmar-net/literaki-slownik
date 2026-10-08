# Runbook: aktualizacja wiki projektu

## TL;DR
[Wiki](https://github.com/robmar-net/literaki-slownik/wiki) to krótka strona dla odwiedzających: cel projektu, rodzaje słowników, kryteria filtrowania, liczby i linki do pobrania. Szczegóły i dowody zostają w repozytorium, a wiki do nich linkuje.

**Wiki aktualizujemy w tej samej pracy, która zmienia słowniki, a nie później.** Zmiana kryteriów, nowa wersja list albo wydanie bez aktualizacji wiki to praca nieskończona.

## Key Decisions
- **Gdzie:** wiki to osobne repozytorium `robmar-net/literaki-slownik.wiki`. Lokalnie klonujemy je obok projektu: `~/Projects/Literaki/wiki-literaki-slownik` (katalog pasuje do wzorca `/wiki-*/` w `.gitignore` workspace).
- **Strony:** `Home`, `Slownik-BROAD`, `Slownik-STANDARD`, `Porownanie-z-SJP.pl`, `Historia-zmian`, `_Sidebar`. Nowy rodzaj słownika dostaje nową stronę `Slownik-<NAZWA>` z tym samym układem.
- **Układ strony słownika:**
  - cel w 1–2 zdaniach;
  - stan: liczba słów, wersja polityki i link do pobrania albo „jeszcze niewydany”;
  - co wchodzi;
  - tabela filtrów: filtr, przykłady, podstawa;
  - linki do dokumentów decyzji.
- **Styl:** po polsku, dla gracza, bez żargonu. Przykład słowa przy każdym filtrze. Strona ma się mieścić na jednym ekranie.

## Kiedy aktualizować

| zdarzenie | co zmienić |
|---|---|
| nowa reguła lub zmiana kryterium (`policy.py`, konfiguracja, dokument decyzji) | tabela filtrów na stronie słownika i wiersz w `Historia-zmian` |
| build z nową wersją polityki, który dał listy | liczby słów i wersja na `Home` i stronach słowników, wiersz w `Historia-zmian` |
| nowe lub zmienione źródło (manifest `sources.json`) | tabela źródeł na `Home` |
| nowy benchmark SJP.pl | strona `Porownanie-z-SJP.pl` |
| `export` lub wydanie | link do pobrania, sha256 i wersja; „wersja robocza” zamienia się w numer wydania |
| nowy rodzaj słownika (ATTESTED, popularne, tematyczne) | nowa strona, wiersz w tabeli na `Home`, wpis w `_Sidebar` |

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
   - porównanie z SJP.pl: wynik `scripts/benchmark_sjp.py`.
   Przy liczbach podaj wersję i datę. Dopóki `verify` nie odbierze wydania, pisz „wersja robocza”.
3. Przykład przy filtrze sprawdź w liście albo przez `python3 -m literaki_slownik explain --run-dir <run> --word <słowo>`. Przykład „odpada” nie może być na liście, a przykład „zostaje” musi na niej być.
4. Lista kontrolna przed commitem:
   - stara wersja polityki nie występuje nigdzie poza `Historia-zmian`: `grep -rn "v<poprzednia>" wiki-literaki-slownik`;
   - linki do plików w repo prowadzą do istniejących ścieżek na `main` (po pushu kodu);
   - z SJP.pl nie ma skopiowanych list słów, tylko liczby i pojedyncze przykłady; atrybucja CC BY 4.0 jest obecna;
   - każda strona ma najwyżej jeden ekran tekstu.
5. Zapisz i wypchnij:
   ```bash
   git -C wiki-literaki-slownik add -A
   git -C wiki-literaki-slownik commit -m "wiki: <co się zmieniło> (v<NN>)"
   git -C wiki-literaki-slownik push
   ```

## Open Questions / Risks
- Wiki nie ma testów ani CI, więc zestarzeje się po cichu. Jedyną ochroną jest ta procedura w kroku, który zmienia słowniki (zob. `AGENTS.md`).
- Repozytorium wiki istnieje dopiero po utworzeniu pierwszej strony w przeglądarce. Po jego usunięciu trzeba je odtworzyć ręcznie.
