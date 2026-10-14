# Wyjątki dawności STANDARD

## TL;DR
Formę odrzuconą w STANDARD tylko za dawność przywracamy wpisem w `config/generator/standard-age-exceptions.json`.
Wpis wskazuje jedną dokładną analizę, nie napis. Po edycji: nowy hash w `sources.json` i nowy build.
Nie dopisujemy formy do gotowej listy. Lista wynika z ocen zapisanych w bazie przebiegu; `verify` to sprawdza.

## Key Decisions
- Reguła `linguistic-standard-age-exception-v1` (polityka `approved-conditions-v30`) uchyla tylko
  `linguistic-historical-form-v1` i tylko w STANDARD. Inne odmowy zostają. BROAD bez zmian.
- Wyjątek dotyczy jednej rozwiniętej analizy. Inny homonim, inny tag lub inna forma tego samego lematu nie wchodzą same.
- Plik jest wejściem pipeline jak inne konfiguracje: przypięty w `configurations.standard-age-exceptions`.
  Stary przebieg zachowuje swoje oceny. Zmiana działa tylko w nowym przebiegu.
- Zakres #4: 2 382 formy, 7 192 analizy (7 060 źródłowych, 132 konstrukcje), 110 rodzin.
  Wersja `standard-age-exceptions-v2`. Źródło decyzji: `provenance` w pliku.

## Open Questions / Risks
- Wpis wiąże rekord SGJP (wiersz, oryginał, tag, kwalifikatory) i hash importu. Nowe wydanie SGJP albo nowa reguła
  konstrukcji zmienia klucze: plik trzeba wtedy przeliczyć (tak było z 58 kluczami `nie-prefix-degree-v2`, #5).
- Ocena znaczenia rodziny to zapis redakcyjny z badania #4, z ograniczoną pewnością (`confidence`).

## Co zawiera plik

| pole | treść |
|---|---|
| `decision_version` | wersja decyzji; nowa przy każdej zmianie zakresu |
| `overrides_rule` | zawsze `linguistic-historical-form-v1` |
| `source_snapshot` | przebieg, z którego wzięto klucze (v30), hash jego bazy, `recomputed_constructions` |
| `sources` | hash każdego użytego importu (dziś `sgjp-20260823`) |
| `expected_counts` | `words`, `analyses`, `source_analyses`, `construction_analyses`, `families` |
| `families` | rodzina = lemat: zakres, znaczenie, pewność, artykuły czytnika, ≥ 2 dokumenty KWJP, dowód |
| `cases` | forma gry → lista analiz `source` (rekord + `tag`) albo `construction` (`candidate_key` + składniki) |

Walidator odmawia całego pliku przy pierwszym błędzie, bez częściowego dopuszczenia:
zły hash źródła, duplikat, zła kolejność, obcy lemat, forma poza `forms` rodziny, tag spoza rozwinięcia,
rodzina bez przypadków, liczby różne od `expected_counts`.

## Jak dodać lub zmienić wyjątek

1. Znajdź analizę w nowym przebiegu:
   `python3 -m literaki_slownik explain --run-dir <przebieg> --word <forma> --json`.
   Weź pola rekordu (`source_id`, `first_source_row`, `original`, `lemma_id`, `raw_tag`, `names`, `qualifiers`)
   i rozwinięty `tag`. Dla konstrukcji: `persisted_candidate_key` i składniki z `derivations`.
2. Dopisz analizę w `cases` (napisy rosnąco; analizy wg rodzaju, lematu, tagu, źródła, wiersza).
   Nowa rodzina wymaga wpisu w `families` z dowodem. Popraw `expected_counts` i `decision_version`.
3. Zapisz plik w układzie kanonicznym (jedna analiza w wierszu), żeby diff był czytelny:
   ```sh
   python3 -c "from literaki_slownik.standard_age_exceptions import render; from literaki_slownik.canonical import load_json
   p='config/generator/standard-age-exceptions.json'; text=render(load_json(p)); open(p,'w',encoding='utf-8').write(text)"
   ```
   Najpierw `render`, potem zapis: `open(p,'w')` czyści plik przed odczytem.
4. Przypnij hash: `shasum -a 256 config/generator/standard-age-exceptions.json` →
   `configurations.standard-age-exceptions.sha256` w `config/generator/sources.json`.
5. Sprawdź:
   ```sh
   python3 scripts/check_standard_age_exceptions.py
   python3 -m literaki_slownik inspect-sources --manifest config/generator/sources.json --json
   python3 scripts/check_standard_age_exceptions.py --database <przebieg>/build.sqlite --records-only
   ```
   Pierwsza komenda: hash, schemat, liczby. Ostatnia (tylko odczyt): każdy rekord i kandydat istnieje w bazie.
   `--allow-missing-recomputed` tylko dla starej migawki (v30), w której nie ma kandydatów reguły z
   `recomputed_constructions`; wynik podaje ich liczbę w `expected_missing_recomputed`.
6. Zacommituj kod i konfigurację (`verify` wymaga czystego `code_identity`), potem nowy build w nowym katalogu:
   `python3 -m literaki_slownik build --manifest config/generator/sources.json --run-dir data/work/lists-v<NN>-<stempel>-a`.

## Jak sprawdzić wynik buildu

- Faza `decisions` przerywa build (kod 4), gdy wpis nie trafił na analizę, analiza nie ma odmowy dawności
  albo ma inną odmowę. Każdy wpis musi być użyty dokładnie raz.
- `reports/decisions.json` → `standard_age_exceptions`: `rule_id`, `decision_version`, `sha256`, `entries`,
  `matched` (= `entries`), `unused` (= 0), `words`, `source_analyses`, `construction_analyses`.
- `explain --word <forma>`:
  - `assessment_basis.standard_age_exceptions.status`: `pinned` (z wersją i SHA256),
    `not_pinned_in_run` (stary przebieg) albo `pinned_file_unavailable` (plik w repo zmieniony po buildzie;
    podstawą zostają zapisane oceny);
  - `expanded_assessments`: ocena każdego rozwinięcia tagu, `standard_age_exception` = tak/nie;
  - `persisted_analyses`: zapisany check `linguistic-standard-age-exception-v1` z wersją decyzji i rodziną.
- `lists/standard.txt` zawiera formę, `lists/broad.txt` bez zmian w tej sprawie.

## Dlaczego nie dopisać formy do listy
- Lista to eksport ocen `membership_status='accept'` z bazy. Dopisana ręcznie forma nie ma oceny,
  więc `verify` odrzuci rozjazd listy i ocen, a `explain` nie pokaże podstawy.
- Napis nie wskazuje analizy. Dopisanie napisu przyjęłoby też homonimy i znaczenia, których nie sprawdzono.
- Nie przechodzą inne warunki gry i języka. Wyjątek uchyla tylko dawność.
- Ręczna zmiana gotowej listy łamie odtwarzalność i piny wydania.

Decyzja i zakres: [#4](https://github.com/robmar-net/literaki-slownik/issues/4),
[specyfikacja](../../.maister/tasks/development/2026-10-12-stabilizacja-progu-pop/implementation/spec.md).
Warunki wieku: [etykiety](etykiety.md).
