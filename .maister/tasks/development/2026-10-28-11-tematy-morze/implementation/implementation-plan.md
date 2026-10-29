# Plan wdrożenia: pilotaż TEMATY „morze” (#11)

## TL;DR
15 grup, 89 kroków. Najpierw wiki „W przygotowaniu”, wspólny kod i źródła (grupy 1–3 mogą iść równolegle), potem ADR-010/011.
Moduł `tematy.py` powstaje w pięciu grupach po kolei (5–9), bo wszystkie zmieniają ten sam plik. Checker i dokumenty (10, 11) idą równolegle.
Potem jeden pełny zestaw testów (12), budowy a/b w tle i ocena agenta (13), strona R2 i wiki z liczbami (14), bramka operatora (15).
Testy: 50 nowych w grupach 2–10, do 10 w grupie 12. Wydania publicznego w tym planie nie ma.

## Kluczowe decyzje
- **Commity wprost na `main`, bez PR.** Tak wylądowało POP00 (c14df5d, f33fe05, 59d93d1). Kod: `feat(tematy): … (#11)`, poprawki `fix(tematy): …`, dokumenty `docs(tematy): …`, artefakty zadania `maister: #11 …`. Commit i push po każdej grupie.
- **Budowy rzeczywiste tylko z czystego drzewa.** `code_identity()` musi mieć `git_dirty: false` (wzór `verify_real.py`). Dlatego grupa 13 idzie po commicie grup 2–12.
- **Wiki na starcie to osobna grupa 1, bez zależności.** Runbook i spec wymagają strony „W przygotowaniu” przed kodem. Liczby dochodzą w grupie 14.
- **ADR-011 po pobraniu (grupa 4 po 3).** ADR potrzebuje liczności nowej pochodnej, `last_modified` i `member` IATE. ADR-010 piszemy w tej samej grupie.
- **Kontrola kierunku relacji na prawdziwej pochodnej to skrypt w folderze zadania, nie test w `tests/`.** Testy nie czytają prawdziwych danych. Wynik idzie do `verification/plwordnet-derivative.json`.
- **Oceny agenta zapisuje skrypt w folderze zadania** (`analysis/record_agent_review.py`, wzór `record_review.py` POP00). `scripts/tematy_review.py` ma tylko `strona` i `zapisz`, jak w spec.
- **`tematy.py` dzielimy na grupy według przepływu danych:** konfiguracja → wejścia i rejestr → kandydaci → leksemy i formy → raporty i pakiet. Każda grupa ma 2–8 testów.
- **Fikstura `tests/tematy_helpers.py` rośnie z grupami.** Bazuje na `tests/pop00_helpers.py` (baza z `schema.sql`, pakiety POP i POP00), dokłada małą pochodną Słowosieci i mały TBX w zipie z prawdziwymi polami.

## Otwarte pytania / ryzyka
- **Liczba testów (50–60) przekracza typowe 16–34.** Spec wymienia 18 przypadków do pokrycia, a zadanie ma 4 nowe skrypty. Każda grupa trzyma się 2–8.
- **`tematy.py` i `tests/tematy_helpers.py` są wspólne dla grup 5–9.** Te grupy nie mogą iść równolegle.
- **Budowa trwa minuty (2 × hash 22 GB na budowę).** Grupa 13 puszcza budowy w tle i zapisuje czasy. Budowy a i b po kolei, nie razem (dysk).
- **Pełny TBX może mieć pola spoza próbki 4,9 MB.** Grupa 3 liczy wartości `termType` na pełnym pliku przed kodem T3.
- **T3 może mieć < 30 leksemów.** Wtedy ocena obejmuje całą warstwę (W11); plan tego nie zmienia.
- **Strona R2 wymaga operatora** (sprawdzenie na iPhonie, 90 ocen). Grupa 14 czeka na jego JSON.
- **Wiki to osobne repo** (`~/Projects/Literaki/wiki-literaki-slownik`, gałąź `master`). Commit i push osobno.

## Przegląd
- Kroki razem: 89
- Grupy: 15
- Testy: 50 w grupach 2–10, do 10 w grupie 12 (razem do 60)
- Polecenia testów:
  - grupa: `python3 -m unittest tests.<moduł>` (tylko nowe testy grupy);
  - pełny zestaw (raz, grupa 12): `python3 -m unittest discover -s tests -p 'test_*.py'` oraz `python3 -m unittest discover -s scripts -p 'test_audit_sgjp.py'`.

Ścieżki względem repo `literaki-slownik`. `T/` = `.maister/tasks/development/2026-10-28-11-tematy-morze/`. `WIKI/` = `/Users/robmar/Projects/Literaki/wiki-literaki-slownik/`.

## Kroki wdrożenia

### Grupa 1: Wiki „W przygotowaniu”
**Zależności:** brak
**Pliki:** `WIKI/Slownik-TEMATY.md`, `WIKI/Home.md`, `WIKI/_Sidebar.md`, `WIKI/Slownik-STANDARD.md`, `WIKI/Historia-zmian.md`, `T/work-log.md`
**Kroki:** 6

- [x] 1.0 Opublikować wstępną stronę TEMATY
  - [x] 1.1 Przygotować klon według runbooka: `git -C WIKI pull --ff-only`. Testów jednostkowych tu nie ma; kontrolą jest lista z kroku 4 runbooka.
  - [x] 1.2 Napisać `Slownik-TEMATY.md` według układu strony słownika: cel (1–2 zdania), stan „W przygotowaniu, jeszcze niewydany”, co wchodzi (T1 etykiety SGJP, T2 Słowosieć 4.5, T3 IATE 2019 dziedzina 4821, tylko formy z STANDARD), link do [#11](https://github.com/robmar-net/literaki-slownik/issues/11). Bez liczb.
  - [x] 1.3 `Home.md`: wiersz TEMATY w tabeli słowników („W przygotowaniu”); w tabeli źródeł wiersze Słowosieć 4.5 i IATE (planowane); zmienić zdanie „Planowane dalej: … słowniki tematyczne” tak, by linkowało stronę.
  - [x] 1.4 `_Sidebar.md`: wpis TEMATY. `Slownik-STANDARD.md`: link do TEMATY jako podzbioru. `Historia-zmian.md`: wiersz z datą „start prac nad TEMATY (#11)”.
  - [x] 1.5 Lista kontrolna runbooka: jeden ekran na stronę, linki tabel w formie `[X](Slownik-X)`, brak nazw innych gier słownych, brak list słów.
  - [x] 1.6 Commit `wiki: TEMATY w przygotowaniu (#11)` i push w repo wiki; sprawdzić publiczny HTML strony; wpis w `T/work-log.md`.

**Kryteria odbioru:**
- Strona `Slownik-TEMATY` jest publiczna, ma „W przygotowaniu” i link do #11.
- `Home`, `_Sidebar`, `Slownik-STANDARD`, `Historia-zmian` linkują stronę.

### Grupa 2: Wspólny kod (`write_gzip`, `quality._config`, `read_words`)
**Zależności:** brak
**Pliki:** `literaki_slownik/pop.py`, `literaki_slownik/pop00.py`, `literaki_slownik/quality.py`, `tests/pop00_helpers.py`, `tests/test_pop.py`, `tests/test_quality.py`
**Kroki:** 5

- [x] 2.0 Przygotować wspólny kod bez zmiany zachowania POP i POP00
  - [x] 2.1 Napisać 3 testy w `tests/test_quality.py`: `tematy-quality-v1` przyjmuje rozmiar 50; odrzuca 30; `pop00-quality-v1` nadal przyjmuje tylko 30.
  - [x] 2.2 `pop._write_gzip` → `write_gzip`, bez aliasu. Poprawić wywołania: `pop.py:1955`, `pop00.py:289–291`, `tests/pop00_helpers.py:9,52`, cel `mock.patch.object` w `tests/test_pop.py:1352`.
  - [x] 2.3 `quality.SEEDS['tematy-quality-v1'] = 'literaki-slownik-tematy-v1'`. W `_config` rozmiar zależny od wersji: mapa `{tematy-quality-v1: 50}`, reszta 30. Komunikat błędu bez nazwy „quality-v1” na sztywno.
  - [x] 2.4 `pop00.read_words`: komunikat „Niekanoniczna lista wejściowa” bez „POP00” (żaden test go nie sprawdza).
  - [x] 2.5 Uruchomić tylko: 3 nowe testy oraz `tests.test_pop`, `tests.test_pop00`, `tests.test_pop00_package` (moduły dotknięte zmianą nazwy). Commit `feat(tematy): przygotuj wspólny kod (#11)`.

**Kryteria odbioru:**
- 3 nowe testy przechodzą; testy POP i POP00 bez zmian wyniku.
- `grep -rn "_write_gzip"` nie daje trafień.

### Grupa 3: Pobranie źródeł i pochodna Słowosieci
**Zależności:** brak
**Pliki:** `scripts/fetch_tematy_sources.py`, `scripts/build_plwordnet_db.py`, `tests/test_fetch_tematy_sources.py`, `tests/test_build_plwordnet_db.py`, `T/analysis/verify_plwordnet.py`, `T/verification/sources.json`, `T/verification/plwordnet-derivative.json`, `T/verification/iate-scan.json`, `T/work-log.md`
**Kroki:** 9

- [x] 3.0 Pobrać źródła i zbudować odtwarzalną pochodną
  - [x] 3.1 Napisać 6 testów (bez sieci, dane syntetyczne):
    - pobranie z `file://` daje rekord `url`, `retrieved_at`, `sha256`, `bytes`, `path`; istniejący cel = błąd, plik tymczasowy usunięty;
    - zły hash Słowosieci = błąd, pliku docelowego nie ma;
    - parser zrzutu: wielowierszowy `INSERT`, `\'` i `\\` dają poprawne wiersze;
    - pochodna ma tylko tabele z listy i kolumny z W2; brak `owner`, `comment`, `iplog`, `iplimit`, `tracker_*`; tylko `valid=1`;
    - zła nazwa relacji 11/25/27 = błąd;
    - dwa uruchomienia na tym samym zipie dają ten sam SHA-256; istniejące wyjście = błąd.
  - [x] 3.2 `scripts/fetch_tematy_sources.py` (wzór `scripts/audit_kwjp.py --fetch`): `curl -fL` do pliku tymczasowego w katalogu celu, SHA-256 i bajty, przeniesienie bez nadpisywania, rekord JSON na stdout. IATE: `last_modified` z nagłówka i `member` (nazwa `.tbx` w zipie). Słowosieć: hash musi równać się `30edc5f8…dcbc`.
  - [x] 3.3 `scripts/build_plwordnet_db.py`: strumieniowy odczyt zrzutu z zipa, lista dozwolonych tabel i kolumn (W2), `valid=1`, wstawianie w kolejności klucza, `meta` (SHA-256 zipa, wersja skryptu), kontrola nazw relacji, liczności na stdout, wynik przez plik tymczasowy i `rename_noreplace`.
  - [x] 3.4 Uruchomić 6 nowych testów.
  - [x] 3.5 Dane rzeczywiste (sieć): pobrać IATE do `cache/iate/IATE_download.zip` i Słowosieć do `cache/plwordnet/wordnet_work_4_5.zip`. Rekordy zapisać w `T/verification/sources.json`. Sprawdzić `last_modified` (oczekiwany 30.09.2019).
  - [x] 3.6 Zbudować `cache/plwordnet/plwn45-tematy.sqlite` dwa razy (drugi raz do pliku w scratchpadzie); hashe muszą być równe. Zapisać czas, hash, liczności; porównać ze starą pochodną (1 491 277 relacji, 514 016 jednostek; różnica relacji = wiersze `valid=0`).
  - [x] 3.7 `T/analysis/verify_plwordnet.py`: na nowej pochodnej `statek 1` (7354) → `łódź 2`, `okręt 1` po relacji 11 w kierunku `PARENT_ID → CHILD_ID`; nazwy 6 korzeni = `lemma + ' ' + variant` jednostki o najniższym `unitindex`; kody `pos` 1–4 zgodne z przypiętą mapą (przykłady). Wynik do `T/verification/plwordnet-derivative.json`.
  - [x] 3.8 Pełny skan TBX (jednorazowy, skrypt w scratchpadzie): wartości `termType`, liczba `deprecatedTerm-admn-sts`, liczba haseł z kodem `4821` w `subjectField`, czy pojawia się `<!ENTITY`. Wynik do `T/verification/iate-scan.json`. Nieznane pola zapisać jako ryzyko w work-logu.
  - [x] 3.9 Commit kodu `feat(tematy): pobranie źródeł i pochodna Słowosieci (#11)`; artefakty zadania `maister: #11 źródła i pochodna`. Push.

**Kryteria odbioru:**
- 6 testów przechodzi.
- Zip Słowosieci ma przypięty hash; pochodna powtarzalna bajtowo; brak kolumn i tabel z danymi redaktorów.
- Kierunek relacji potwierdzony na nowej pochodnej; T3 ma kandydatów `fullForm` w 4821.

### Grupa 4: ADR-010 i ADR-011
**Zależności:** 3
**Pliki:** `docs/adr/ADR-010-tematy-v1.md`, `docs/adr/ADR-011-zrodla-slowosiec-iate.md`
**Kroki:** 4

- [x] 4.0 Zapisać metodę i źródła przed modułem
  - [x] 4.1 Kontrola zamiast testów: format jak `ADR-009-pop00-v1.md` (TL;DR, Kluczowe decyzje, Otwarte pytania); linki do istniejących ścieżek.
  - [x] 4.2 `ADR-010-tematy-v1.md`: lokalne ADR-001, 002, 005–010 badania (z mapą numerów); `t2.tryb: pelne` jako decyzja operatora z 2026-10-29; stan tylko BUILT i przegląd poza pakietem (odstępstwo od ADR-008 badania); progi jako udziały; werdykt automatyczny „dalej”/„popraw”, „stop” tylko operator; lista 37 słów w pliku tematu.
  - [x] 4.3 `ADR-011-zrodla-slowosiec-iate.md`: lokalne 003, 004; pochodna (tabele, kolumny, `valid=1`, `isabstract`, `status` bez filtra); liczności z grupy 3 wobec starej pochodnej; kierunek relacji; kody części mowy 1–4, pominięcie 5–8; `term` z projektu = `fullForm`, odrzucenie `deprecatedTerm-admn-sts`; dopasowanie całych kodów `subjectField`; DOCTYPE dozwolone, `<!ENTITY` = błąd; ponowne pobranie Słowosieci (odstępstwo od `clarifications.md`); `last_modified` i `member` IATE; licencja Słowosieci (nota 4.2, link 404).
  - [x] 4.4 Commit `docs(tematy): ADR-010 i ADR-011 (#11)`, push.

**Kryteria odbioru:**
- Oba ADR mają liczby z `T/verification/*.json`, nie z pamięci.
- Każde odstępstwo z „Zmian po audycie” ma zapis w jednym z ADR.

### Grupa 5: Konfiguracja i walidacja
**Zależności:** 2, 3
**Pliki:** `config/generator/tematy.json`, `config/generator/tematy-sources.json`, `config/generator/tematy/morze.json`, `config/generator/tematy-teksty/*`, `literaki_slownik/tematy.py`, `tests/tematy_helpers.py`, `tests/test_tematy_config.py`
**Kroki:** 7

- [x] 5.0 Dodać pliki metody, wejść i tematu z walidacją
  - [x] 5.1 Napisać 6 testów:
    - poprawne `tematy.json` i `morze.json` (fikstura) przechodzą;
    - nieznane pole w każdym z trzech plików = kod 2;
    - relacja spoza {11, 25, 27} = błąd; `t2.tryb` ≠ `pelne` = błąd;
    - `sampling` z innym zbiorem kluczy albo rozmiarem ≠ 50 = błąd (przez `quality._config`);
    - kod części mowy spoza mapy w `czesci_mowy` = błąd;
    - zły hash pliku w `teksty` = kod 3.
  - [x] 5.2 `tests/tematy_helpers.py`: start fikstury — kopie plików konfiguracji z hashami fikstury (bez prawdziwych pinów).
  - [x] 5.3 `config/generator/tematy-teksty/`: `ATTRIBUTIONS-tematy.md` (nota plWordNet z zastrzeżeniem, „Download IATE, European Union, 2019”), `LIMITATIONS.md` (śródlądowe: problem, lista znaczników, miejsce na udział), `TERMS.md`. Bez tekstu SGJP: ten idzie z pakietu POP (W13).
  - [x] 5.4 `tematy.json` (W4): `version`, `adr`, `sampling` (4 klucze `quality._config`), `operator_per_stratum: 30`, `progi` jako ułamki w tekście (`"0.70"`, `"0.90"`, `"2/3"`, `"0.10"`, `"0.80"`), `czesci_mowy`, `t3_klasy`, `teksty` z hashami.
  - [x] 5.5 `morze.json` (W5): pola i wartości ze spec, 37 słów bez zmian, znaczniki śródlądowe PL i EN. `tematy-sources.json` (W3): piny z grupy 3 i z istniejących wejść (`release-LL-PL-v30/release-manifest.json`, BROAD `4f1aace9…1271`, pop-v3, POP00 r2-a); `plwordnet_zip` bez ścieżki do hashowania.
  - [x] 5.6 `tematy.py`: `load_method`, `load_topic`, `load_sources` (zbiór kluczy i typy, wzór `pop00.load_sources`; kody 2 i 3).
  - [x] 5.7 Uruchomić 6 nowych testów; dodatkowo załadować prawdziwe trzy pliki (bez budowy). Commit `feat(tematy): konfiguracja metody i tematu (#11)`, push.

**Kryteria odbioru:**
- 6 testów przechodzi; prawdziwe pliki konfiguracji ładują się bez błędu.
- Lista 37 słów i znaczniki śródlądowe są w `morze.json` przed pierwszą budową.

### Grupa 6: Wejścia i rejestr czytanych plików
**Zależności:** 5
**Pliki:** `literaki_slownik/tematy.py`, `tests/tematy_helpers.py`, `tests/test_tematy_inputs.py`
**Kroki:** 6

- [x] 6.0 Sprawdzać wejścia i pilnować ich do końca budowy
  - [x] 6.1 Napisać 6 testów:
    - poprawna fikstura przechodzi `check_inputs`;
    - przebieg nie `FROZEN` = kod 5;
    - hash `release_manifest` ≠ `export.release_manifest_sha256` przebiegu albo hash BROAD/STANDARD ≠ wpis w manifeście wydania = kod 3;
    - `meta` pochodnej ≠ pin zipa = kod 3;
    - zmiana pliku wewnątrz pakietu POP po `check_inputs` → `confirm_unchanged` = kod 5;
    - każdy plik otwarty przez `check_inputs` jest w rejestrze (porównanie z listą oczekiwaną).
  - [x] 6.2 Fikstura: przebieg (wzór `pop00_helpers.fixture`), `release-manifest.json` wydania, BROAD i STANDARD, pakiet POP (`POP.txt.gz`, `POP0.txt.gz`, `reports/units.json`, `ATTRIBUTIONS.md`), pakiet POP00 (`POP00.txt.gz`), mała pochodna Słowosieci z `meta`, zip z TBX.
  - [x] 6.3 Rejestr: jedna funkcja `register(data, path, expected_sha)`; każdy odczyt wejścia przechodzi przez nią. `confirm_unchanged` re-hashuje cały rejestr (naprawa klasy błędu f33fe05).
  - [x] 6.4 `check_inputs`: hashe przez `inputs.checked_file`, `FROZEN`, manifest wydania, zgodność POP i POP00 z bazą i STANDARD (wzór `pop00.check_inputs`), pliki pakietów przez `pop00.package_file`, `meta` pochodnej (SQLite `mode=ro`).
  - [x] 6.5 Odczyt list: `pop00.read_words` dla BROAD, STANDARD, POP, POP00; członkowie POP i POP0 z `units.json` (`members_in`).
  - [x] 6.6 Uruchomić 6 nowych testów. Commit `feat(tematy): wejścia i rejestr plików (#11)`, push.

**Kryteria odbioru:**
- 6 testów przechodzi.
- Żaden plik nie jest czytany poza rejestrem.

### Grupa 7: Kandydaci T1, T2, T3
**Zależności:** 6
**Pliki:** `literaki_slownik/tematy.py`, `tests/tematy_helpers.py`, `tests/test_tematy_sources.py`
**Kroki:** 6

- [x] 7.0 Wyznaczyć kandydatów z trzech źródeł
  - [x] 7.1 Napisać 8 testów:
    - T1: kwalifikatory dzielone po `|`, potem `,`; atom cały (`mors.` w `daw.|mors.,wojsk.` tak; `mors` bez kropki nie);
    - T2: kierunek domknięcia `statek` → `łódź`, `okręt` (bez odwrotnego);
    - T2: synset sztuczny przechodni, jego lematy nie wchodzą;
    - T2: jednostka z kodem 5–8 pominięta;
    - T2: nazwa korzenia niezgodna = błąd;
    - T3: `subjectField` `20, 48` nie pasuje do `4821`; `1011, 4821` pasuje;
    - T3: DOCTYPE przechodzi; `<!ENTITY` = błąd;
    - T3: odrzucone `abbreviation`, `deprecatedTerm-admn-sts`, niezawodność < 3, wielka litera, wiele słów; liczniki według `termType`.
  - [x] 7.2 T1: jeden pełny skan `interpretation` z cache po `(tag, names, qualifiers)`. Wynik: leksemy T1 i klasy tagów każdego leksemu (potrzebne grupie 8).
  - [x] 7.3 T2: kontrola nazw korzeni (D4), domknięcie BFS po relacjach z `morze.json`, kolejność deterministyczna; lematy z jednostek o kodach z `czesci_mowy`; znaczenie źródłowe (`lemma variant`).
  - [x] 7.4 T3: `iterparse` z zipa (członek `member`); przed parsowaniem odczyt nagłówka: DOCTYPE dozwolone, `<!ENTITY` lub podzbiór wewnętrzny = błąd kod 4; zewnętrznego DTD nie ładujemy. Zbieramy tylko hasła z pasującym kodem; terminy PL i EN (EN do miary śródlądowej).
  - [x] 7.5 Reguła „jedno słowo” (W7): NFC, małe litery, tylko litery polskiego alfabetu. Odrzuceni liczeni z powodem `NIE_JEDNO_SLOWO`.
  - [x] 7.6 Uruchomić 8 nowych testów. Commit `feat(tematy): kandydaci T1–T3 (#11)`, push.

**Kryteria odbioru:**
- 8 testów przechodzi.
- `interpretation` czytamy w całości jeden raz.

### Grupa 8: Leksemy, warstwy i formy
**Zależności:** 7
**Pliki:** `literaki_slownik/tematy.py`, `tests/tematy_helpers.py`, `tests/test_tematy_layers.py`
**Kroki:** 6

- [x] 8.0 Zmienić kandydatów w wpisy z formami w STANDARD
  - [x] 8.1 Napisać 7 testów:
    - lemat T2 → leksem z równym `lemma_base` i klasą z mapy kodu; T3 tylko `subst`/`depr`;
    - `żeglowanie` (tylko forma `ger`) → `BRAK_LEKSEMU` z podliczbą `ger`;
    - leksem w T1 i T2 → warstwa T1, źródła oba;
    - `wieloznaczny`: `tak`/`nie`/`brak_danych`; jednostka angielska (kod 5–8) nie ustawia `tak`;
    - formy z konstrukcjami (`pop.load_constructions` z podzbiorem leksemów);
    - diagnostyka: leksem tylko w BROAD → `POZA_STANDARD`; poza BROAD → `POZA_BROAD`;
    - wynik `MORZE` ⊆ STANDARD i warstwy rozłączne.
  - [x] 8.2 Mapowanie lemat → leksem (`lemma_id@source_id` przez `pop._label`), osobno dla T2 i T3; `BRAK_LEKSEMU` z podliczbą `ger`.
  - [x] 8.3 Warstwa = najniższa z T1 < T2 < T3; źródła = wszystkie; znaczenie źródłowe.
  - [x] 8.4 `wieloznaczny` według reguły ADR-007 badania, tylko jednostki 1–4.
  - [x] 8.5 Formy kandydatów porcjami po `lexeme_id` (wzór `pop00.read_analyses`) plus konstrukcje; przecięcie z BROAD i STANDARD; liczniki diagnostyki na warstwę, w leksemach i formach.
  - [x] 8.6 Uruchomić 7 nowych testów. Commit `feat(tematy): leksemy, warstwy i formy (#11)`, push.

**Kryteria odbioru:**
- 7 testów przechodzi.
- Bez `pop.load_forms` na całym BROAD.

### Grupa 9: Raporty, próba, pakiet i CLI
**Zależności:** 8
**Pliki:** `literaki_slownik/tematy.py`, `literaki_slownik/cli.py`, `tests/tematy_helpers.py`, `tests/test_tematy_package.py`
**Kroki:** 7

- [x] 9.0 Zapisać pakiet i podłączyć podkomendę
  - [x] 9.1 Napisać 7 testów:
    - dwie budowy na fiksturze dają identyczne `SHA256SUMS`;
    - pakiet ma pliki z listy spec; pliki `0444`; `MORZE.txt.gz` posortowane i ⊆ STANDARD;
    - `summary.json`: przecięcia z POP/POP00 (razem i T1/T2/T3, leksemy i formy) zgodne z ręcznie policzonymi;
    - test 37 słów: całość, T1, T1 ∪ T2, lista brakujących; śródlądowe na kandydatach T3 i na wpisach;
    - próba: `min(50, N)` na warstwę; warstwa N < 30 bierze całość; operator = pierwsze `min(30, N)` w kolejności rangi;
    - istniejący cel albo cel w wejściach = kod 4/2; zmiana konfiguracji w trakcie = kod 5 i brak pakietu;
    - CLI `tematy --json`: koperta jak `pop00`, kody wyjścia.
  - [x] 9.2 Raporty (W8–W10): `summary.json`, `raport.md` z tych samych liczb; odrzuceni z 10 przykładami na powód i warstwę (deterministycznie); liczby haseł T3 według `termType` i odrzuconych `deprecatedTerm`; udział `wieloznaczny` z 10 przykładami; do 20 przykładów śródlądowych.
  - [x] 9.3 Próba: `quality.sample_strata` z warstwami jako strata; `review_template` z danymi wpisu; `reports/sample.json`, `reports/review-template.json`.
  - [x] 9.4 Pakiet (wzór `pop00._write_package`): `MORZE.txt.gz` przez `pop.write_gzip`, `MORZE.tsv.gz`, kopia `tematy/morze.json`, `method.json`, `ATTRIBUTIONS.md` (atrybucje z pakietu POP + `ATTRIBUTIONS-tematy.md`), `LIMITATIONS.md` z udziałem śródlądowych, `TERMS.md`, `release-manifest.json` (stan BUILT, `counts.morze`, `overlap`, `code_identity`), `SHA256SUMS`.
  - [x] 9.5 `build_package` (wzór `pop00.build_package`): staging obok celu, `confirm_unchanged` na rejestrze, `chmod 0444`, `rename_noreplace`, mapowanie wyjątków na kody.
  - [x] 9.6 `cli.py`: parser `tematy --manifest --config --topic --output-dir [--json]`, leniwy import, `_finish`.
  - [x] 9.7 Uruchomić 7 nowych testów. Commit `feat(tematy): pakiet, raporty i podkomenda (#11)`, push.

**Kryteria odbioru:**
- 7 testów przechodzi.
- Budowa na fiksturze działa bez sieci.

### Grupa 10: Checker i skrypt przeglądu
**Zależności:** 9
**Pliki:** `scripts/check_tematy_package.py`, `scripts/tematy_review.py`, `tests/test_check_tematy_package.py`, `tests/test_tematy_review.py`, `tests/tematy_helpers.py`
**Kroki:** 6

- [x] 10.0 Niezależnie sprawdzić pakiet i przegląd
  - [x] 10.1 Napisać 7 testów:
    - checker PASS na pakiecie z fikstury; zmieniony bajt w `MORZE.txt.gz` = odmowa;
    - forma spoza STANDARD albo leksem w dwóch warstwach = odmowa;
    - `--review`: trafność na warstwę z rzeczywistym N; „niepewne” nie jest „tak”; zgodność i kappa na 3 kategoriach (wartości policzone ręcznie);
    - `--review`: werdykt „dalej” albo „popraw” z listą progów; mała warstwa liczy udziały;
    - `strona` odmawia bez hasha ocen agenta;
    - `strona` nie zawiera ocen agenta; ma przyciski, „kopiuj JSON”, pole tekstowe, `localStorage` w `try/catch`;
    - `zapisz` odrzuca brak klucza, obcy klucz i zły hash ocen agenta.
  - [x] 10.2 `check_tematy_package.py` (wzór `check_pop00_package.py`, bez importu `literaki_slownik`): `SHA256SUMS`, manifest, `MORZE.txt` ⊆ STANDARD, TSV spójny z TXT, warstwy rozłączne, przecięcia z POP/POP00 liczone od nowa, brak `owner`/`comment` w przypiętej pochodnej.
  - [x] 10.3 `--review`: kompletność, powiązanie z `SHA256SUMS` i `sample_sha256`, trafność, zgodność, kappa, test 37 słów (całość), werdykt.
  - [x] 10.4 `tematy_review.py strona`: samodzielny HTML na wąski ekran, duże przyciski tak/nie/niepewne, „kopiuj JSON”, pole z JSON, szkic w `localStorage`; odmowa bez hasha ocen agenta.
  - [x] 10.5 `tematy_review.py zapisz`: łączy JSON operatora z plikiem przeglądu; sprawdza klucze, hashe i hash ocen agenta.
  - [x] 10.6 Uruchomić 7 nowych testów. Commit `feat(tematy): checker i skrypt przeglądu (#11)`, push.

**Kryteria odbioru:**
- 7 testów przechodzi.
- Checker nie importuje pakietu `literaki_slownik` (`grep`).

### Grupa 11: Dokumenty
**Zależności:** 9
**Pliki:** `docs/generator/cli.md`, `docs/generator/raporty.md`, `docs/generator/jakosc.md`, `docs/runbook-wiki.md`, `.maister/docs/INDEX.md`, `ATTRIBUTIONS.md`
**Kroki:** 5

- [x] 11.0 Opisać TEMATY w dokumentach projektu
  - [x] 11.1 Kontrola zamiast testów: `tests/test_documented_names.py` i testy dokumentów przechodzą; linki prowadzą do istniejących ścieżek.
  - [x] 11.2 `cli.md`: podkomenda `tematy`, argumenty, kody wyjścia, skrypty pobrania i pochodnej. `raporty.md`: pliki pakietu i pola `summary.json`. `jakosc.md`: próba 50/30, skala, progi jako udziały, zgodność i kappa.
  - [x] 11.3 `runbook-wiki.md`: sekcja TEMATY (liczby z `counts` i `summary.json`; przykłady sprawdzamy w `MORZE.tsv.gz`, bo `explain` nie ma wariantu tematy; „W przygotowaniu” do wydania).
  - [x] 11.4 `ATTRIBUTIONS.md` repo: noty plWordNet i IATE. `.maister/docs/INDEX.md`: ADR-010, ADR-011 i nowe dokumenty.
  - [x] 11.5 Commit `docs(tematy): CLI, raporty, jakość, runbook (#11)`, push.

**Kryteria odbioru:**
- Każdy nowy plik i nazwa z kodu ma opis w `docs/`.

### Grupa 12: Przegląd testów i luki
**Zależności:** 10, 11
**Pliki:** `tests/test_tematy_*.py`, `tests/test_check_tematy_package.py`, `tests/test_tematy_review.py`, `tests/test_fetch_tematy_sources.py`, `tests/test_build_plwordnet_db.py`, `tests/tematy_helpers.py`
**Kroki:** 5

- [ ] 12.0 Przejrzeć testy i domknąć luki
  - [ ] 12.1 Przejrzeć testy grup 2–10 (50) wobec listy „Do pokrycia” w spec.
  - [ ] 12.2 Wypisać luki tylko dla TEMATY (np. leksem w trzech warstwach, dodatek spoza STANDARD = błąd, błąd danych SQLite → kod 4).
  - [ ] 12.3 Dopisać do 10 testów.
  - [ ] 12.4 Uruchomić raz pełny zestaw: `python3 -m unittest discover -s tests -p 'test_*.py'` oraz `python3 -m unittest discover -s scripts -p 'test_audit_sgjp.py'`. Przeczytać wynik, nie tylko kod wyjścia.
  - [ ] 12.5 Commit `test(tematy): domknij luki (#11)`, push.

**Kryteria odbioru:**
- Pełny zestaw przechodzi; dodano najwyżej 10 testów.

### Grupa 13: Budowy rzeczywiste i ocena agenta
**Zależności:** 12
**Pliki:** `T/analysis/verify_real.py`, `T/analysis/record_agent_review.py`, `T/verification/real-builds.json`, `T/verification/tematy-morze-review.json`, `T/work-log.md`
**Kroki:** 7

- [ ] 13.0 Zbudować pakiet dwa razy i ocenić próbę
  - [ ] 13.1 Kontrola zamiast testów: `verify_real.py` (wzór POP00) sprawdza `git_dirty: false`, identyczne bajty a/b, checker PASS na obu.
  - [ ] 13.2 Puścić w tle budowę `data/work/tematy-v1-<data>-a`, potem `-b` (po kolei). Zapisać czasy startu i końca w work-logu. Czytać wynik, nie tylko zakończenie.
  - [ ] 13.3 `verify_real.py`: identyczne `SHA256SUMS`, checker PASS na a i b; dowód do `T/verification/real-builds.json` z `summary.json`.
  - [ ] 13.4 Sprawdzić wynik wobec kryteriów sukcesu: T3 niepusta, liczby `termType`, przecięcia, diagnostyka z podliczbą `ger`, test 37 słów, udział śródlądowych. Odstępstwo od spec = zatrzymanie i poprawka w grupach 5–9 (nowe budowy).
  - [ ] 13.5 Agent ocenia wszystkie pozycje próby (do 150): tak/nie/niepewne z powodem.
  - [ ] 13.6 `record_agent_review.py` zapisuje `T/verification/tematy-morze-review.json`: oceny agenta, ich hash, `SHA256SUMS` pakietu, `sample_sha256`.
  - [ ] 13.7 Commit i push `maister: #11 budowy a/b i ocena agenta` — przed wygenerowaniem strony operatora (D12).

**Kryteria odbioru:**
- Dwie budowy mają identyczne `SHA256SUMS`; checker PASS na obu.
- Hash ocen agenta jest w commicie na `main`, zanim powstanie strona R2.

### Grupa 14: Strona R2, wiki z liczbami, raport bramki
**Zależności:** 13
**Pliki:** `T/verification/tematy-morze-r2.html`, `T/verification/tematy-morze-review.json`, `T/verification/review-check.json`, `T/verification/gate-report.md`, `WIKI/Slownik-TEMATY.md`, `WIKI/Home.md`, `WIKI/Historia-zmian.md`
**Kroki:** 7

- [ ] 14.0 Zebrać oceny operatora i przygotować bramkę
  - [ ] 14.1 Kontrola zamiast testów: `check_tematy_package.py --review` na pliku przeglądu.
  - [ ] 14.2 `tematy_review.py strona` → `T/verification/tematy-morze-r2.html`. Opublikować jako prywatny artefakt claude.ai.
  - [ ] 14.3 Operator sprawdza stronę na iPhonie (wąski ekran, przyciski, „kopiuj JSON”). Poprawki strony = grupa 10 i nowa strona.
  - [ ] 14.4 Operator ocenia do 90 pozycji i wkleja JSON. `tematy_review.py zapisz` dopisuje oceny do pliku przeglądu.
  - [ ] 14.5 `check_tematy_package.py --review` → `T/verification/review-check.json`: trafność z rzeczywistym N, zgodność, kappa, test 37 słów, werdykt „dalej”/„popraw”.
  - [ ] 14.6 Wiki: liczby z manifestu i `summary.json` na `Slownik-TEMATY` i `Home`; nadal „W przygotowaniu”, bez linku pobrania; przykłady sprawdzone w `MORZE.tsv.gz`; wiersz w `Historia-zmian`. Commit i push wiki.
  - [ ] 14.7 `T/verification/gate-report.md`: przecięcia z POP/POP00, diagnostyka, test 37 słów, śródlądowe, wyniki R2, werdykt automatyczny. Commit i push `maister: #11 przegląd R2 i raport bramki`.

**Kryteria odbioru:**
- Plik przeglądu ma oceny agenta i operatora, powiązane z pakietem.
- Wiki ma liczby z artefaktów i nadal „W przygotowaniu”.

### Grupa 15: Bramka operatora
**Zależności:** 14
**Pliki:** `T/decision-log.md`, `T/work-log.md`
**Kroki:** 3

- [ ] 15.0 Decyzja operatora
  - [ ] 15.1 Orchestrator przedstawia raport bramki (z treścią, nie zapowiedzią). Kontrola: werdykt w raporcie = werdykt checkera.
  - [ ] 15.2 Operator wybiera „dalej”, „popraw” albo „stop”. Zapis decyzji z datą w `T/decision-log.md`.
  - [ ] 15.3 Commit i push `maister: #11 decyzja bramki`. Bez wydania publicznego i bez kolejnych tematów w tym zadaniu.

**Kryteria odbioru:**
- Decyzja operatora zapisana. Tarballa ani Release nie ma.

## Kolejność wykonania
1. Grupy 1, 2, 3 — równolegle (różne pliki). Grupa 3 ma długi krok z siecią.
2. Grupa 4 (po 3).
3. Grupa 5 (po 2 i 3).
4. Grupy 6 → 7 → 8 → 9 — po kolei (wspólny `tematy.py`).
5. Grupy 10 i 11 — równolegle (po 9).
6. Grupa 12 (po 10 i 11).
7. Grupa 13 (po 12; czyste drzewo, budowy w tle).
8. Grupa 14 (po 13; czeka na operatora).
9. Grupa 15 (po 14).

## Zgodność ze standardami
Według `.maister/docs/INDEX.md` i `docs/`:
- `AGENTS.md`: polski, zwięźle; surowe dane w `cache/` i `data/work/` (poza Git); wiki w tej samej pracy; bez kontaktu z autorami.
- `docs/generator/publikacja.md`: atrybucje źródeł; bez wydania przed odbiorem.
- `docs/runbook-wiki.md`: układ strony, tabela źródeł na `Home`, liczby z artefaktów.
- `docs/adr/ADR-009-pop00-v1.md`: wzór pakietu, dwie budowy, przegląd przed wydaniem.
- `docs/generator/cli.md`: koperta `--json`, kody wyjścia 2–5.

## Antywzorce (z spec i z POP00)
- Nie czytać pliku wejścia poza rejestrem.
- Nie hashować zipa Słowosieci w budowie.
- Nie zmieniać listy 37 słów ani znaczników po wynikach.
- Nie commitować dwa razy dużych JSON-ów przeglądu.
- Nie pokazywać operatorowi ocen agenta.
- Nie używać prawdziwych danych w `tests/`.

## Uwagi
- TDD: każda grupa z kodem zaczyna od 2–8 testów.
- Po grupie uruchamiamy tylko jej testy; pełny zestaw raz, w grupie 12.
- Postęp: odhaczać kroki w tym pliku i w `implementation-plan.html`.
- Najpierw ponowne użycie: `pop00`, `pop`, `quality`, `canonical`, `inputs`, `export`, `run`.
