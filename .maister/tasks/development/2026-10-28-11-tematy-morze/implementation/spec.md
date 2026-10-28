# Specyfikacja: pilotaż TEMATY „morze” (#11)

## TL;DR
Nowa podkomenda `tematy` buduje lokalny pakiet TEMATY z tematem `morze`, według wzoru POP00: wsadowo, deterministycznie, bez sieci.
Lista to leksemy SGJP ∩ STANDARD w trzech rozłącznych warstwach: T1 etykiety SGJP, T2 Słowosieć 4.5, T3 IATE 2019.
Pakiet podaje przecięcia z POP i POP00, diagnostykę kandydatów wobec BROAD i STANDARD, test 37 słów i udział żeglugi śródlądowej w T3.
Pobranie źródeł i pochodna Słowosieci to osobne skrypty. Próba R2 (90 słów) idzie do operatora przez stronę z przyciskami.
Wydanie publiczne dopiero po bramce. Teraz: ADR-010, ADR-011 i strona wiki „W przygotowaniu”.

## Kluczowe decyzje
- **Rejestr czytanych plików.** Każdy plik czytany w budowie (także wewnątrz pakietów POP i POP00) trafia do jednego rejestru z hashem. `confirm_unchanged` re-hashuje cały rejestr. To strukturalna naprawa błędu f33fe05.
- **Pochodna Słowosieci wiąże się z zipem.** Pochodna SQLite ma tabelę `meta` z SHA-256 zipa i wersją skryptu. Budowa czyta tylko pochodną i sprawdza `meta` z przypiętym hashem zipa.
- **Pochodzenie źródeł w manifeście źródeł.** URL, data UTC, SHA-256 i bajty zapisujemy w `config/generator/tematy-sources.json` (w Git). Daty nie bierzemy z `mtime`. Słowosieć pobieramy ponownie z tego samego adresu; hash musi się zgadzać z przypiętym.
- **Próba agenta 50 przez `quality`.** `quality._config` dostaje rozmiar zależny od wersji (`tematy-quality-v1` → 50, reszta → 30). Operator dostaje pierwsze 30 z 50 każdej warstwy w kolejności rangi. Bez drugiego ziarna.
- **Jedna skala ocen: tak / nie / niepewne.** Dla agenta i operatora. „tak” to trafne, „nie” to błędne.
- **Werdykt automatyczny tylko „dalej” albo „popraw”.** „dalej”, gdy spełnione są wszystkie progi; inaczej „popraw” z listą niespełnionych. „stop” wybiera tylko operator na bramce.
- **Bez `explain --variant tematy` w v1.** TSV już podaje warstwę, źródła i znaczenie źródłowe.
- **Bez refaktoru POP00.** TEMATY importuje publiczne `pop00.read_words` i `pop00.package_file`. Z `pop` upubliczniamy tylko `write_gzip`.
- **Teksty pakietu z plików.** `TERMS`, `LIMITATIONS` i noty plWordNet/IATE leżą w `config/generator/tematy-teksty/` i są przypięte hashem w konfiguracji metody.
- **Kontrola śródlądowa przez znaczniki.** Lista znaczników w pliku tematu (pole diagnostyczne). Liczymy hasła T3, których terminy PL lub EN zawierają znacznik jako początek słowa. Nic nie wykluczamy.

## Otwarte pytania / ryzyka
- **Kierunek relacji 11.** W 4.5 relacja 11 to „hiperonimia” (10 to „hiponimia”). Kierunek `PARENT_ID`/`CHILD_ID` sprawdzamy na `statek 1` przed domknięciem i zapisujemy w ADR-011. Zły kierunek wciąga ogólne słownictwo. To samo dla 25 i 27.
- **Struktura TBX 2019 nieznana do pobrania.** Nazwy elementów (dziedzina, typ terminu, niezawodność) potwierdzamy na pobranym pliku. Parser odrzuca DTD i encje.
- **Licencja Słowosieci 4.5** („4.2 © 2020”, link 404). Opisane w `LIMITATIONS.md` i ADR-011.
- **POP00 r2-a ma stan BUILT.** Nowa budowa POP00 zmieni liczby przecięć.
- **Koszt czasu.** Dwa hashe `build.sqlite` (22 GB) i dwa skany `interpretation` (STANDARD, BROAD) na budowę. Minuty.
- **Nakład operatora.** 90 ocen.
- **Determinizm bajtów SQLite.** Pochodna zależy od wersji SQLite. Sprawdzamy dwiema budowami; hash przypinamy.

## Cel
Zbudować i zmierzyć pilotażowy temat `morze`, tak by operator mógł zdecydować na bramce: dalej, popraw albo stop.

## Historie użytkownika
- Jako operator chcę zbudować temat jednym poleceniem z przypiętych wejść, żeby wynik dało się odtworzyć.
- Jako operator chcę widzieć, ile tematu jest w POP i POP00, żeby ocenić, czy bot na mniejszym słowniku z niego skorzysta.
- Jako operator chcę ocenić 90 słów przyciskami, bez wglądu w oceny agenta, żeby bramka miała drugiego oceniającego.
- Jako odwiedzający wiki chcę wiedzieć, że TEMATY powstaje i z czego.

## Wymagania

### W1. Pobranie źródeł (osobny krok, z siecią)
- Skrypt `scripts/fetch_tematy_sources.py`:
  - IATE: `https://iate.europa.eu/em-api/artifacts/full-tbx` → `cache/iate/IATE_download.zip`;
  - Słowosieć 4.5: `https://clarin-pl.eu/server/api/core/bitstreams/3197cd0f-bb4e-41ba-93e0-eec99ab8d519/content` → `cache/plwordnet/wordnet_work_4_5.zip`.
- Pobiera `curl -fL` do pliku tymczasowego w katalogu celu, liczy SHA-256 i bajty, przenosi bez nadpisywania.
- Wypisuje rekord JSON: `url`, `retrieved_at` (UTC, ISO 8601), `sha256`, `bytes`, `path`.
- Słowosieć: hash musi równać się `30edc5f85c06408d372a897f1d1ff3d03fa939b8680b176c1f97351f4a72dcbc`; inaczej błąd.
- Budowa (`tematy`) nigdy nie używa sieci.

### W2. Pochodna Słowosieci
- Skrypt `scripts/build_plwordnet_db.py`: zip (zrzut SQL, 2,6 GB) → nowy plik SQLite, strumieniowo, deterministycznie, bez nadpisywania.
- Kopiuje tylko:
  - `lexicalunit`: `ID`, `lemma`, `pos`, `variant`;
  - `synset`: `ID`, `unitsstr`;
  - `unitandsynset`: `LEX_ID`, `SYN_ID`, `unitindex`;
  - `synsetrelation`: `PARENT_ID`, `CHILD_ID`, `REL_ID`;
  - `relationtype`: `ID`, `name`;
  - `meta`: SHA-256 zipa, wersja skryptu.
- Bez kolumn `owner`, `comment`, `error_comment` i żadnych innych tabel (w tym logu IP).
- Sprawdza nazwy relacji 11, 25, 27 (`hiperonimia`, `część`, `miejsce`); inna nazwa = błąd.
- Wiersze wstawia w stałej kolejności (po kluczu). Dwa uruchomienia dają ten sam hash.
- Wynik: `cache/plwordnet/plwn45-tematy.sqlite`. Stary `data/work/plwordnet/plwn45.sqlite` nie jest wejściem budowy.

### W3. Manifest źródeł `config/generator/tematy-sources.json`
- Wersja `tematy-sources-v1`. Wejścia (ścieżka + SHA-256):
  - `base_run` (manifest v31), `database` (`build.sqlite`), `standard`, `broad`;
  - `base_pop` (manifest pop-v3), `base_pop00` (manifest POP00 r2-a);
  - `plwordnet_zip` (z `url`, `retrieved_at`, `bytes`), `plwordnet_db`;
  - `iate` (z `url`, `retrieved_at`, `bytes`).
- Nieznane klucze odrzucamy (wzór `pop00.load_sources`).

### W4. Konfiguracja metody `config/generator/tematy.json`
- `version: tematy-v1`, `adr: docs/adr/ADR-010-tematy-v1.md`.
- `sampling`: `tematy-quality-v1`, ziarno `literaki-slownik-tematy-v1`, 50 na warstwę; `operator_per_stratum: 30`.
- `progi`: test 37 słów ≥ 70%; T1 ≥ 27/30 „tak”; T2 ≥ 20/30 „tak” i ≤ 3 „nie”; T3 ≥ 20/30 „tak”; zgodność ≥ 80%.
- `slowa_oczywiste`: 37 słów z `scope-clarifications.md`, bez zmian.
- `czesci_mowy`: mapa części mowy Słowosieci na klasy tagów SGJP (rzeczownik → `subst`, `depr`; czasownik → `inf`; przymiotnik → `adj`; przysłówek → `adv`).
- `teksty`: ścieżki i SHA-256 plików w `config/generator/tematy-teksty/`.
- Walidacja: zbiór kluczy i typy; nieznane pola = błąd (kod 2).

### W5. Plik tematu `config/generator/tematy/morze.json`
- Schemat jak w projekcie (`high-level-design.md`, „Schemat pliku konfiguracji tematu”):
  - `t1.atomy_sgjp`: `mors.`, `żegl.`, `ryb.`;
  - `t2.korzenie`: 7354 `statek 1`, 2149 `okręt 1`, 4511 `łódź 2`, 6214 `marynarz 1`, 14136 `żegluga 1`, 14515 `żeglarstwo 1`; `t2.relacje`: 11, 25, 27; `t2.wykluczenia_poddrzew`: puste;
  - `t3.iate.kody_dziedzin`: `4821`; filtry: typ `term`, jedno słowo, niezawodność ≥ 3;
  - `t3.iate.znaczniki_srodladowe`: lista do pomiaru W10;
  - `t3.dodatki`: puste; `wykluczenia`: puste.
- Walidacja: zbiór kluczy i typy, nieznane pola = błąd. Relacja spoza {11, 25, 27} = błąd. Nazwa korzenia niezgodna z synsetem = błąd. Dodatek spoza STANDARD = błąd.

### W6. Podkomenda `tematy`
- `python3 -m literaki_slownik tematy --manifest M --config C --topic T --output-dir D [--json]`.
- Koperta `--json`, kody wyjścia i komunikaty jak w `pop00`.
- Nie nadpisuje: `D` nie może istnieć ani leżeć w wejściach. Staging obok celu, `chmod 0444`, `rename_noreplace`.
- Sprawdza wejścia: hashe, `FROZEN` przebiegu, zgodność POP i POP00 z bazą i STANDARD, `meta` pochodnej.
- Przed przeniesieniem re-hashuje każdy czytany plik z rejestru (manifest, konfiguracja, temat, teksty, wejścia, pliki wewnątrz POP i POP00).

### W7. Warstwy i pliki listy
- **T1:** leksemy z interpretacją, w której kwalifikatory po podziale `|`, potem `,` zawierają atom tematu jako cały atom.
- **T2:** domknięcie od korzeni po relacjach 11, 25, 27 (kierunek zgodnie z ADR-011), z hiponimami części i miejsc. Lematy jednostek o pasującej części mowy → leksemy przez `lexeme.lemma_base`.
- **T3:** polskie terminy IATE z kodów dziedzin, typu `term`, jednowyrazowe, z małych liter polskich, niezawodność ≥ 3 → leksemy przez `lemma_base`.
- Lematy wszystkich warstw: NFC, małe litery, jedno słowo.
- Wpis = leksem (`lemma_id@source_id`). Warstwa = najniższa z T1 < T2 < T3. Źródła = wszystkie.
- Flaga `wieloznaczny`: `tak` / `nie` / `brak_danych`, według reguły ADR-007 badania.
- Formy leksemu jak w POP (`pop.load_forms` i `pop.load_constructions`) ∩ STANDARD.
- `MORZE.txt.gz`: formy tematu, posortowane, gzip deterministyczny.
- `MORZE.tsv.gz`: wiersz na leksem: klucz, lemat, części mowy, warstwa, źródła, znaczenie źródłowe, `wieloznaczny`.

### W8. Raporty
- `reports/summary.json` i czytelny `reports/raport.md` (z tych samych liczb).
- Przecięcie z POP i POP00: liczba i % względem tematu; razem i T1/T2/T3; w leksemach i formach.
  - Leksem w POP: członek POP w `reports/units.json` pop-v3. Leksem w POP00: członek POP0.
  - Forma w POP / POP00: napis z `POP.txt.gz` / `POP00.txt.gz`.
- Diagnostyka przed ∩ STANDARD: kandydaci, ∩ BROAD, ∩ STANDARD, udziały; razem i na warstwę; leksemy i formy.
- Odrzuceni: `BRAK_LEKSEMU` (w lematach, osobno), `POZA_BROAD`, `POZA_STANDARD`; liczba i do 10 przykładów na powód i warstwę, wybór deterministyczny.
- Udział `wieloznaczny` z 10 przykładami.
- Manifest: `counts.morze` z liczbami warstw i `overlap`.

### W9. Pokrycie T2 (test 37 słów)
- Słowo pokryte, gdy któryś wpis tematu ma ten lemat.
- Wynik osobno dla T1, T1 ∪ T2 i całości; liczba, % i lista brakujących. W `summary.json` i `raport.md`.

### W10. Żegluga śródlądowa w T3
- Liczba i udział haseł T3 ze znacznikiem śródlądowym, do 20 przykładów.
- Wynik w raporcie; `LIMITATIONS.md` opisuje problem i podaje udział.

### W11. Próby i przegląd R2
- Próba deterministyczna 50 na warstwę (`quality.sample_strata`), szablon (`quality.review_template`) z danymi wpisu do oceny.
- Skrypt `scripts/tematy_review.py`:
  - `strona`: samodzielna strona HTML z 90 pozycjami operatora (30 na warstwę), przyciski tak / nie / niepewne, bez ocen agenta; eksport JSON;
  - `zapisz`: łączy eksport operatora z plikiem przeglądu, sprawdza klucze i hashe.
- Plik przeglądu: `verification/tematy-morze-review.json` w folderze zadania. Ocena agenta (150 pozycji, z powodem) i operatora (90). Związany z `SHA256SUMS` pakietu i `sample_sha256`. Commit raz.

### W12. Checker `scripts/check_tematy_package.py`
- Nie importuje pakietu `literaki_slownik`.
- Sprawdza: `SHA256SUMS` i manifest, `MORZE.txt` ⊆ STANDARD, spójność TSV z TXT, warstwy rozłączne, przeliczone przecięcia z POP/POP00, brak kolumn `owner`/`comment` w przypiętej pochodnej.
- `--review`: kompletność i powiązanie przeglądu, trafność na warstwę, zgodność i kappa, test 37 słów, werdykt „dalej” / „popraw” z listą progów.

### W13. Dokumenty
- `docs/adr/ADR-010-tematy-v1.md` (lokalne ADR-001, 002, 005–010 badania) i `docs/adr/ADR-011-zrodla-slowosiec-iate.md` (003, 004, pochodna, kierunek relacji, pobranie).
- `ATTRIBUTIONS.md`: nota i zastrzeżenie plWordNet; „Download IATE, European Union, 2019”.
- `docs/generator/cli.md`, `raporty.md`, `jakosc.md`; `docs/runbook-wiki.md`, sekcja TEMATY; `.maister/docs/INDEX.md`.

### W14. Wiki
- Strona `Slownik-TEMATY` „W przygotowaniu” na starcie: cel, źródła, link do #11.
- Po budowie: liczby z manifestu, nadal „W przygotowaniu”, bez linku pobrania.
- Wiersz na `Home`, wpis w `_Sidebar`, link ze `Slownik-STANDARD`, wiersz w `Historia-zmian`.

### W15. Determinizm
- Dwie budowy a/b z tych samych wejść: identyczne `SHA256SUMS`. Checker PASS na obu.

## Kod do ponownego użycia

### Istniejący kod
| Element | Plik | Użycie |
|---|---|---|
| `load_sources`, `check_inputs`, `build_package`, `confirm_unchanged` | `literaki_slownik/pop00.py` | wzór struktury; staging, `chmod`, obsługa błędów |
| `read_words`, `package_file` | `literaki_slownik/pop00.py` | import bez zmian (komunikat `read_words` uogólnić) |
| `checked_file`, `GeneratorError` | `literaki_slownik/inputs.py` | kontrola pinów |
| `dumps`, `load_json`, `sha256`, `write_json` | `literaki_slownik/canonical.py` | kanoniczny JSON i hashe |
| `load_forms`, `load_constructions`, `_label` | `literaki_slownik/pop.py` | formy ∩ STANDARD i ∩ BROAD, klucz leksemu |
| `_write_gzip` → `write_gzip` | `literaki_slownik/pop.py` | upublicznić; poprawić `pop`, `pop00`, `tests/pop00_helpers.py` |
| `sample_strata`, `review_template`, `SEEDS` | `literaki_slownik/quality.py` | próba i szablon; nowy wpis i rozmiar 50 |
| `code_identity` | `literaki_slownik/run.py` | manifest |
| `rename_noreplace` | `literaki_slownik/export.py` | przeniesienie bez nadpisania |
| wzór CLI | `literaki_slownik/cli.py` (51–55, 97–99, 147) | parser, leniwy import, `_finish` |
| wzór checkera | `scripts/check_pop00_package.py` | `Refused`, `require`, `--review` |
| wzór pobrania | `scripts/audit_kwjp.py` (`--fetch`) | `curl` w podprocesie |
| wzór zapisu oceny | `.maister/tasks/quick-plan/2026-10-21-10-pop00-generator-wiki/analysis/record_review.py` | łączenie ocen z plikiem przeglądu |
| fikstura | `tests/pop00_helpers.py` | mała baza z `schema.sql`, pakiety POP |

### Nowe składniki
| Plik | Dlaczego nowy |
|---|---|
| `literaki_slownik/tematy.py` | nowe źródła (SGJP etykiety, Słowosieć, IATE), warstwy i raporty; POP00 tego nie ma |
| `scripts/fetch_tematy_sources.py` | brak skryptu pobrania z rekordem pochodzenia |
| `scripts/build_plwordnet_db.py` | brak odtwarzalnej pochodnej bez danych redaktorów |
| `scripts/check_tematy_package.py` | niezależny checker innego formatu pakietu |
| `scripts/tematy_review.py` | dwóch oceniających i strona z przyciskami; `record_review.py` POP00 leży w folderze zadania i obsługuje jednego |
| `config/generator/tematy.json`, `tematy-sources.json`, `tematy/morze.json`, `tematy-teksty/*` | dane metody, wejść i tematu |
| `tests/tematy_helpers.py`, `tests/test_tematy*.py` | fikstura z Słowosiecią i TBX |

## Podejście techniczne
- Przepływ: wejścia → T1/T2/T3 kandydaci → mapowanie na leksemy → diagnostyka BROAD/STANDARD → ∩ STANDARD → scalenie warstw → przecięcia z POP/POP00 → test 37 słów i śródlądowe → próba → pakiet (`high-level-design.md`, „Przepływ danych”).
- Moduł funkcyjny, bez klas, jak `pop00.py`. Jeden skan `interpretation` z cache po `(tag, names, qualifiers)` daje T1 i klasy części mowy leksemów.
- TBX czytamy strumieniowo z zipa (`iterparse`), zbierając tylko hasła z kodów dziedzin. DTD i encje = błąd.
- Odczyt SQLite tylko do odczytu (`mode=ro`), zapytania porcjami jak w `read_analyses`.
- Determinizm: sortowanie wszędzie, `canonical.dumps`, gzip z `mtime=0`, `code_identity()` w manifeście.
- Stan pakietu: BUILT. Przegląd żyje poza pakietem (jak POP00).

### Pliki pakietu
`MORZE.txt.gz`, `MORZE.tsv.gz`, `tematy/morze.json`, `method.json`, `reports/summary.json`, `reports/raport.md`, `reports/sample.json`, `reports/review-template.json`, `ATTRIBUTIONS.md`, `LIMITATIONS.md`, `TERMS.md`, `release-manifest.json`, `SHA256SUMS`.

### Kolejność prac
Wiki „W przygotowaniu” → ADR-010/011 → pobranie i pochodna (z kontrolą kierunku relacji) → moduł i testy → budowy a/b → checker → przegląd agenta → strona R2 → bramka.

## Wskazówki wdrożeniowe

### Testy
- 2–8 testów na grupę kroków. Weryfikacja uruchamia tylko nowe testy grupy, nie cały zestaw.
- Fikstura: mała baza z `schema.sql`, mała pochodna Słowosieci, mały TBX w zipie, małe pakiety POP i POP00.
- Do pokrycia: podział `|` i `,` z całymi atomami; kierunek domknięcia; leksem w kilku warstwach; homonimy i `wieloznaczny`; nieznane pole konfiguracji; dodatek spoza STANDARD; zmiana pliku wewnątrz POP podczas budowy; brak `owner` w pochodnej i jej determinizm; DTD w TBX; budowy a/b; checker z przeglądem.
- Polecenie: `python3 -m unittest discover -s tests -p 'test_*.py'` (pełny zestaw raz na końcu).

### Zgodność ze standardami
- `AGENTS.md`: polski, zwięźle; dane surowe poza Git; wiki w tej samej pracy; bez kontaktu z autorami.
- `docs/generator/publikacja.md`: atrybucje źródeł; bez wydania przed odbiorem.
- `docs/runbook-wiki.md`: układ strony słownika, liczby z artefaktów.
- ADR-009 (POP00): wzór pakietu, dwie budowy, przegląd przed wydaniem.
- Commity: `feat(tematy): … (#11)`; po zapisie w `.maister/tasks` commit i push.

## Poza zakresem
- Kolejne tematy i fala ~10 tematów.
- Wydanie publiczne (tarball) i pełna strona wiki przed bramką.
- Dodatki ręczne i wykluczenia w `morze-v1`.
- `explain --variant tematy`.
- Wikisłownik, LLM, Słowosieć 5.0, konto EU Login, kontakt z autorami.
- Terminy wielowyrazowe, listy na poziomie znaczeń, ranking w temacie.
- Integracja z botami Literaki.
- Zmiany POP, POP0, POP00, BROAD i STANDARD.

## Kryteria sukcesu
1. `tematy` buduje pakiet offline; dwie budowy a/b mają identyczne `SHA256SUMS`.
2. Każdy wpis to leksem z formą w STANDARD v31, z warstwą, źródłami i `wieloznaczny`.
3. `summary.json` i `raport.md` podają przecięcia z POP/POP00, diagnostykę BROAD/STANDARD z odrzuconymi, test 37 słów (T1, T1 ∪ T2, całość) i udział śródlądowych.
4. Zmiana dowolnego czytanego pliku w trakcie budowy kończy się błędem (kod 5) i brakiem pakietu.
5. Pochodna Słowosieci nie ma `owner`, `comment` ani logu IP; dwa uruchomienia skryptu dają ten sam hash.
6. Checker PASS na pakiecie; z `--review` podaje trafność, zgodność i werdykt.
7. Operator ocenił 90 pozycji; raport bramki gotowy; decyzja operatora zapisana.
8. ADR-010, ADR-011, `ATTRIBUTIONS.md`, dokumenty i wiki „W przygotowaniu” zaktualizowane.
