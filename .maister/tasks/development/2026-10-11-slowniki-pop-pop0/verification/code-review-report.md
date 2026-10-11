# Przegląd kodu POP/POP0

**Data**: 2026-10-11 · **Zakres**: all (jakość, bezpieczeństwo zapisu, wydajność) · **Commit**: a18da79
**Pliki**: `literaki_slownik/pop.py`, `explain.py` (`explain_pop`, `_word_lexemes`), `cli.py` (`pop`, `explain`),
`quality.py` (`SEEDS`), `scripts/measure_pop.py`, `scripts/check_pop_package.py`, testy POP.
**Status**: ⚠️ Issues Found — 0 krytycznych, 2 ostrzeżenia, 8 informacyjnych.

## TL;DR

- Rdzeń metody jest poprawny. F nie jest ani dzielone, ani kopiowane między homonimami. Brak danych to `None` ze statusem, nigdy 0. Pakiet nie zawiera liczb NKJP (C14). Wynik nie zależy od kolejności haszowania.
- **W1**: `pop --output-dir` wskazujący katalog wewnątrz przebiegu FROZEN albo pakietu LL-PL nie jest odrzucany. Sprawdziłem to na fiksturze: pakiet powstał w `run-a/pop-inside`. To łamie C4 („zero zapisów w run-dir i release-dir”). `measure_pop.py` ma tę blokadę, `build_package` jej nie ma.
- **W2**: wyjątki inne niż `GeneratorError` (`sqlite3.Error`, `KeyError`, `ValueError`) wychodzą z CLI jako traceback z kodem 1, a nie jako kod 2/3/4/5 (C1).
- Testy POP: 90 zielonych w 7,7 s. Na v29 (work-log): 145 s i 3,2 GB RSS. Zapytania SQL mają ograniczony zakres i używają indeksów.

## Key Decisions

- Ocena „bez kopiowania F” dotyczy ścieżki produkcyjnej `units(..., 'e', eligible)` i `member_units`. Opcja `b` kopiuje F z założenia i służy tylko do porównań w `measure_pop.py`, więc nie liczę jej jako błędu.
- W1 ma rangę ostrzeżenia, nie błędu krytycznego. Wymaga pomyłki operatora i nie niszczy danych, ale łamie twarde ograniczenie spec. Ma najwyższy priorytet.
- Nie zmieniałem kodu. Jedyny zapis poza tym raportem to sonda W1 w scratchpadzie (fikstura w katalogu tymczasowym).

## Open Questions / Risks

- Czy `explain` ma zwracać kod 5 dla przebiegu, który nie jest FROZEN, tak jak `pop`? Dziś zwraca 3 (I3), a C16 tego nie rozstrzyga.
- Spec C3/C6 opisuje średnią percentyli F, a kod i ADR-007 rew. 3 używają log-ipm (I7). Trzeba uzgodnić tekst spec z kodem.

## Ostrzeżenia

### W1. `pop` zapisuje do przebiegu FROZEN albo do pakietu LL-PL — `literaki_slownik/pop.py:1749-1761`
`build_package` sprawdza tylko, czy cel nie istnieje i czy istnieje katalog nadrzędny. Sonda (`build_package(..., run/'pop-inside')`) zapisała cały pakiet w katalogu przebiegu.
**Naprawa** (jak w `scripts/measure_pop.py:695-697`): po `check_inputs` (czyli przed `mkdtemp`) porównać `target.resolve()` (rozwiązany także rodzic) z `paths['run_dir']` i `paths['release_dir']`: `t == p or p in t.parents` → `GeneratorError(..., 2)`. Dodać test dla obu katalogów. Do naprawienia od ręki: tak.

### W2. Wyjątki spoza `GeneratorError` dają traceback i kod 1 — `literaki_slownik/cli.py:91-101`
Przykłady: `sqlite3.DatabaseError` z `connect`/`execute` w `_lexicon` (`pop.py:1328`), `KeyError` przy braku `ARF`/`1-DP` w `typed_metrics` (`pop.py:263`), `KeyError` w `keys[lexeme_id]` (`pop.py:210`), wewnętrzne `ValueError` (`pop.py:559`, `776`). `explain_pop` już zamienia je na kod 4 (`explain.py:401-402`), a `pop` tego nie robi.
**Naprawa**: w `build_package`/`build_pop` zamienić `sqlite3.Error`, `KeyError` i `ValueError` na `GeneratorError(..., 4)` (dane niezgodne z oczekiwaną strukturą). Do naprawienia od ręki: tak.

## Informacyjne

- **I1. TOCTOU dla NKJP i STANDARD** — `pop.py:121-123`, `1327`, `1432`. Hash pliku jest liczony w `check_inputs`, a odczyt następuje później i nikt go nie powtarza. Hash bazy jest sprawdzany przed i po; tych plików nie. Sugestia: przy `read_nkjp`/`read_standard` liczyć hash strumieniowo i porównać z pinem.
- **I2. Rangi NKJP z luką** — `pop.py:669-670` i `1438`. Ranga i percentyl NKJP są liczone przed usunięciem jednostek złożonych z samych nazw własnych (D9), więc `nkjp_rank` w `units.json` ma luki, a populacja percentyla jest inna niż ta w pakiecie. Miara łączna (log-ipm) jest poprawna. Sugestia: przeliczyć rangę NKJP po filtrze D9 albo opisać to w LIMITATIONS.
- **I3. Niespójny kod błędu** — `explain.py:306`. Dla przebiegu, który nie jest FROZEN, `explain` zwraca kod 3, a `pop` kod 5 (`pop.py:107`).
- **I4. Słaba kontrola w `check_pop_package.py`.** `check_nkjp` (`:166-181`) szuka liczb NKJP po nazwach kluczy JSON i pomija `.md`. `check_lists` (`:192`) porównuje słowa `must_include_pop0` bez normalizacji, a `pop` normalizuje je przez `_game_key` (`pop.py:1457`). Słowo `Kot` w konfiguracji przejdzie w `pop` i nie przejdzie w kontroli. Sugestia: w `_validate_config` wymagać, by słowo było już kluczem gry.
- **I5. `explain_pop` parsuje cały `units.json`** (62 MB) przy każdym wywołaniu (`explain.py:369`). Dla narzędzia diagnostycznego to akceptowalne.
- **I6. Uprawnienia katalogów pakietu.** Pliki mają 0444, ale katalog z `mkdtemp` ma 0700, a `reports/` zależy od umask; oba zostają zapisywalne (`pop.py:1755-1760`). Kontrola wykryje dodany plik, ale można dać katalogom 0555.
- **I7. Spec rozjechał się z kodem.** C3/C6 opisują percentyle F, a kod ma log-ipm (`ADR_007_D3_D4`, `pop.py:1212`). C19 mówi „nie czyta 1grams.gz”, a `check_inputs` liczy hash tego pliku (opisane w `LIMITATIONS.md`).
- **I8. `NKJP_LINE` przepuszcza `\r`** — `pop.py:342`. `.+` dopasowuje też `\r`, więc plik CRLF nie dopasuje się do kluczy, a nie da błędu 4. Sugestia: `([^\r\n]+)`.
- **Jakość.** Długie funkcje: `units` (~160 wierszy), `build_pop` (~92), `measure` (~70), `member_units` (~88). Logika jest gęsta, ale opisana w docstringach; nie wymaga zmian.

## Co sprawdziłem i jest zgodne

- **F bez dzielenia i kopiowania (C7)**: w `units('e')` każdy wiersz EXACT i każda połączona grupa AMBIGUOUS trafia do dokładnie jednej jednostki, bo union-find łączy wszystkich członków grupy. Grupy i formy NKJP z obcym właścicielem zostają nieprzypisane (`unattributed`), z licznikiem `copied = 0`. `member_units` przypisuje masę wspólną tylko podjednostce, która obejmuje wszystkich właścicieli.
- **Brak ≠ 0**: `_kwjp_missing`, `NOT_IN_PUBLISHED_LIST`, `rank_units` bez rangi dla `None`, `_log_ipm` → `None`.
- **C14**: `_package_row` pomija `value`, `thresholds.json` zawiera tylko `kwjp_mass`, a `pop_summary` nie zawiera `mass`.
- **Determinizm**: brak zależności od kolejności `frozenset`/`set` na wyjściu (klucze to posortowane krotki, wszystkie listy są sortowane). gzip ma `mtime=0` i pustą nazwę. D-1 potwierdzono dwoma przebiegami.
- **Zapis**: staging w katalogu nadrzędnym celu, potem `rename_noreplace`. `BaseException` usuwa staging. Gdy cel istnieje, kod 4. Baza otwierana w `mode=ro`, hash przed i po.
- **SQL na 22 GB**: `_evidence_range` używa `UNIQUE(source_id,row_number)`, `evidence_candidate` używa częściowego indeksu `candidate_lexeme`, złączenia idą po PK albo `form_id`. Każda tabela jest skanowana liniowo, bez złączeń wielokrotnych. `explain` korzysta z `form_game_key`, `derivation_game_key`, `interpretation_lexeme` i `UNIQUE(source_id,lemma_id)`.

## Metryki

- Najdłuższa funkcja: `units` (~160 wierszy). Najgłębsze zagnieżdżenie: 4.
- Podatności: 0 krytycznych, 1 dotycząca zapisu (W1). Ryzyko N+1: 1, pomijalne (`_word_lexemes`, kilka leksemów na słowo).

## Priorytety

1. W1: blokada `--output-dir` w run-dir i release-dir oraz test.
2. W2: mapowanie `sqlite3.Error`, `KeyError` i `ValueError` w `pop` na kod 4.
3. I4: normalizacja `must_include_pop0` w konfiguracji.
4. I2 i I1: rangi NKJP po D9 i hash przy odczycie.
