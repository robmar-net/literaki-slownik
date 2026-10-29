# Plan wdrożenia: TEMATY, pierwsza fala — 9 tematów (#12)

## TL;DR
20 grup, 107 kroków. Na start równolegle: szkic słów oczywistych (1), schemat tematu (3) i ADR-012 (8). Strona słów dla operatora (2) idzie obok kodu.
Kod w `tematy.py` zmieniają grupy 3 → 4 → 5 → 6, potem checker i strona R2 (7). Następnie regresja morza (9), przepięcie ocen morza (10) i 9 plików tematów (11). Grupy 10 i 11 idą równolegle.
Potem 18 budów jedną serią bez commitów (12), oceny agenta (13), strony R2 (14), oceny operatora (15), zestawienie fali (16), dokumenty (17), wiki (18), pełny zestaw testów (19) i bramka (20).
Operator zatrzymuje pracę trzy razy: słowa oczywiste (2.4), oceny R2 (15.2) i bramka (20.2). Bez wydania.

## Kluczowe decyzje
- **Commity wprost na `main`, jak w #11.** Kod `feat(tematy): … (#12)`, poprawki `fix(tematy): … (#12)`, dokumenty `docs(tematy): … (#12)`, artefakty zadania `maister: #12 …`. Push po każdej grupie. Pakiety, `cache/` i `data/work/` zostają poza Git.
- **Słowa oczywiste zaczynamy pierwsze i niezależnie od kodu.** Agent pisze je na ślepo w osobnej sesji (grupa 1). Operator przegląda je, gdy powstaje kod (grupa 2). Zamrożony plik musi być w commicie przed grupą 11, a więc przed pierwszą budową nowego tematu.
- **`tematy.py` zmieniamy w czterech grupach po kolei, według przepływu danych.** Kolejność: schemat i metoda (3), wejścia i wykluczenia (4), teksty i raport (5), próba i `CZEKA` (6). Wszystkie cztery ruszają `tematy.py` i `tests/tematy_helpers.py`, więc żadna nie idzie równolegle z inną.
- **Seria budów to okno bez commitów.** `code_identity` zapisuje `git_commit` = HEAD (`run.py:30`). `git_dirty` patrzy tylko na `literaki_slownik/`, więc `config/` i `scripts/` sprawdza dodatkowo skrypt odbioru. Od pierwszej do ostatniej budowy serii nikt nie commituje, także grupy równoległe. Zapisy w `T/` są dozwolone, bo nie zmieniają HEAD. Serie są dwie: regresja morza (9, 2 budowy) i fala (12, 18 budów).
- **Budowy fali to jedna seria 18 budów, commit po ostatniej.** Gdy budowa padnie w środku serii, poprawka w kodzie dostaje commit `fix(tematy)`. Seria zaczyna się wtedy od nowa od tematu, który padł. Pakiety zbudowane wcześniej zostają, bo każdy ma własne a = b.
- **Skrypty jednorazowe żyją w `T/analysis/`, tak jak w #11.** Mają własne małe testy (`T/analysis/test_*.py`) i nie trafiają do `tests/`. Pełny zestaw z `tests/` uruchamiamy raz, w grupie 19.
- **Po grupie uruchamiamy jej nowe testy i moduły TEMATY, które grupa zmieniła.** Grupy 3–7 zmieniają istniejące testy (`dodatki` na górnym poziomie, metoda `tematy-v2`), więc uruchamiają też poprawione moduły. Pełnego zestawu przed grupą 19 nie puszczamy.
- **Instrukcja oceny agenta ma osobny commit przed ocenami.** Hash ocen każdego tematu trafia do commita przed jego stroną R2 (D12 z #11).

## Otwarte pytania / ryzyka
- **Pełny zestaw dopiero na końcu (grupa 19).** Czerwony test w kodzie generatora może wymusić poprawkę i ponowne budowy (9, 12). Ryzyko obniżają testy modułów TEMATY po każdej grupie 3–7.
- **Operator to wąskie gardło dwa razy.** Grupa 11 czeka na 2.4, a grupa 16 na 15.2. Do grupy 10 kod i regresja idą bez niego.
- **Okno bez commitów podczas budów (ok. 1–2 h).** Gdy operator odda JSON słów (2.4) w trakcie serii 9, zapis czeka do jej końca.
- **Małe tematy (pogoda 209, grzyby 351, matematyka 543 lematów T2)** mogą nie przejść progu słów oczywistych 0,70. Wynik idzie do bramki, nie do poprawki w tej fali.
- **Nakład agenta: ok. 950 ocen R2 i ok. 315 słów.** Oceny tematów dzielimy na sesje po temacie. Pliki ocen są rozłączne, więc sesje mogą iść równolegle.
- **Czas maszyny: 20 budów i co najmniej 30 przebiegów checkera, 2–3 h.** Wszystko w tle i po kolei. Czytamy werdykt, nie tylko kod wyjścia.
- **Stare pakiety (`tematy-v1-*`, `tematy-v2-20261029-*`)** nowy checker odrzuci (metoda `tematy-v1`). Regresja (9) porównuje je więc przez hashe i `diff`, a nie przez nowy checker.
- **Grupa 9 może pokazać różnicę bajtową morza.** To błąd kodu z grup 3–6. Wtedy robimy poprawkę `fix(tematy)` i powtarzamy grupę 9 przed grupą 11.

## Przegląd
- Kroki razem: 107
- Grupy: 20 (operator zatrzymuje pracę w grupach 2, 15 i 20)
- Testy: 41 nowych w grupach 1, 3–7, 10, 11, 16 (33 w `tests/`, 8 w `T/analysis/`), do 10 w grupie 19
- Polecenia testów:
  - grupa: `python3 -m unittest tests.<moduł>` albo `python3 -m unittest discover -s T/analysis -p 'test_<skrypt>.py'`;
  - pełny zestaw (raz, grupa 19): `python3 -m unittest discover -s tests -p 'test_*.py'` (dziś 520 OK) oraz `python3 -m unittest discover -s scripts -p 'test_audit_sgjp.py'` (5 OK).

Ścieżki są względem repo `literaki-slownik`. `T/` = `.maister/tasks/development/2026-10-29-12-tematy-fala-1/`. `WIKI/` = `/Users/robmar/Projects/Literaki/wiki-literaki-slownik/`. `<id>` to jeden z 9 tematów: `grzyby`, `pogoda`, `matematyka`, `muzyka`, `sport`, `kuchnia`, `rosliny`, `zwierzeta`, `medycyna`.

## Kroki wdrożenia

### Grupa 1: Szkic słów oczywistych i kontrola lematów (W10.1–2)
**Zależności:** brak
**Pliki:** `T/analysis/sprawdz_slowa.py`, `T/analysis/test_sprawdz_slowa.py`, `T/analysis/slowa-oczywiste.json`, `T/verification/slowa-oczywiste-check.json`
**Kroki:** 6

- [ ] 1.0 Napisać listy na ślepo i sprawdzić je tak, jak liczy test
  - [ ] 1.1 Napisać 3 testy w `T/analysis/test_sprawdz_slowa.py` (mała baza SQLite i mały STANDARD w katalogu tymczasowym):
    - lemat z klasą z `czesci_mowy` i formą w STANDARD przechodzi;
    - forma, która nie jest `lemma_base` (wzór `nuty`, `zawody`), odpada z powodem;
    - lemat tylko z klasą spoza `czesci_mowy` albo bez formy w STANDARD odpada.
  - [ ] 1.2 Agent w osobnej sesji dostaje tylko nazwy 9 tematów i granice z `T/analysis/clarifications.md`. Nie widzi kandydatów, Słowosieci, pakietów ani `codebase-analysis.md`. Pisze ok. 35 słów na temat: lematy małymi literami, jedno słowo.
  - [ ] 1.3 `T/analysis/sprawdz_slowa.py`: słowo musi być `lemma_base` leksemu SGJP z klasą z `czesci_mowy` (`inf`, `subst`, `depr`, `adv`, `adj`), a leksem musi mieć formę w STANDARD v31. Wzorem są `map_lemmas` (`tematy.py:552`) i `_read_forms`. `build.sqlite` otwieramy tylko do odczytu (`mode=ro`). Wynik: JSON z powodem dla każdego słowa, które odpadło.
  - [ ] 1.4 Uruchomić skrypt na prawdziwych danych. Słowo, które odpadło, agent z 1.2 wymienia na inne (dalej bez wglądu w dane) i skrypt sprawdza je ponownie. Wynik zapisujemy do `T/verification/slowa-oczywiste-check.json`.
  - [ ] 1.5 Zapisać `T/analysis/slowa-oczywiste.json`: `{szkic: {<id>: [...]}, wynik: null}`, posortowane, bez powtórzeń w temacie.
  - [ ] 1.6 Uruchomić tylko 3 nowe testy. Commit i push: `maister: #12 szkic słów oczywistych`.

**Kryteria odbioru:**
- 3 testy przechodzą.
- Każde słowo szkicu przechodzi skrypt; 9 list po ok. 35 słów.
- Historia sesji agenta pokazuje, że nie czytał danych tematów.

### Grupa 2: Strona słów oczywistych i zamrożenie list (W10.3–4) — ZATRZYMANIE: operator
**Zależności:** 1
**Pliki:** `T/verification/slowa-oczywiste.html`, `T/analysis/slowa-oczywiste.json`, `T/verification/slowa-oczywiste-check.json`
**Kroki:** 6

- [ ] 2.0 Dać operatorowi jedną stronę i zamrozić listy
  - [ ] 2.1 Kontrola zamiast testów: strona działa offline, ma 9 list, skreślanie, pole „dopisz” na temat, przycisk „kopiuj JSON” i szkic w `localStorage` w `try/catch`. Sprawdzamy to w wąskim oknie przeglądarki.
  - [ ] 2.2 `T/verification/slowa-oczywiste.html`: samodzielny HTML na iPhone'a z dużymi polami dotyku. JSON wyjściowy ma postać `{<id>: [słowa]}` dla 9 tematów.
  - [ ] 2.3 Opublikować stronę jako prywatny artefakt claude.ai i przekazać link orchestratorowi.
  - [ ] 2.4 **ZATRZYMANIE (orchestrator):** operator przegląda ok. 315 słów, skreśla, dopisuje i wkleja JSON. Kod (grupy 3–8) idzie w tym czasie dalej.
  - [ ] 2.5 Słowa dopisane przez operatora sprawdzić skryptem z 1.3. Słowo, które odpada, wraca do operatora z powodem: jako wybór „wymień” albo „usuń”, a nie po cichu. Wynik dopisujemy do `slowa-oczywiste-check.json`.
  - [ ] 2.6 Zapisać `wynik` w `T/analysis/slowa-oczywiste.json`. Commit i push: `maister: #12 słowa oczywiste zamrożone`. Gdy trwa seria budów (9), commit czeka do jej końca.

**Kryteria odbioru:**
- `wynik` ma 9 list, każde słowo przechodzi skrypt.
- Commit z listami jest w historii przed commitem plików tematów (grupa 11).

### Grupa 3: Schemat tematu i metoda `tematy-v2` (W1, W5)
**Zależności:** brak
**Pliki:** `literaki_slownik/tematy.py`, `config/generator/tematy.json`, `config/generator/tematy/morze.json`, `tests/tematy_helpers.py`, `tests/test_tematy_config.py`, `tests/test_tematy_dodatki.py`
**Kroki:** 7

- [ ] 3.0 Uogólnić plik tematu i podbić metodę
  - [ ] 3.1 Napisać 7 testów w `tests/test_tematy_config.py`:
    - temat bez `t3` przechodzi `load_topic`; `t3` z kluczem innym niż `iate` (np. `t3.dodatki`) daje kod 2;
    - `dodatki` na górnym poziomie przechodzą; para powtórzona albo powód z tabulacją daje kod 2;
    - `wykluczenia` niepuste przechodzą; para powtórzona, powód z tabulacją lub nową linią albo `czesc_mowy` spoza klas SGJP daje kod 2;
    - ta sama para w `dodatki` i `wykluczenia` daje kod 2;
    - `znaczniki_srodladowe` bez `t3` albo przy `t3` bez kodu `4821` dają kod 2; bez znaczników temat przechodzi;
    - `operator_warstwy`: pusty, z powtórzeniem albo spoza `PROBA` daje kod 2; `["T2", "T3"]` przechodzi;
    - prawdziwe `tematy.json` i `morze.json` ładują się z wersją `tematy-v2` i `morze-v2`.
  - [ ] 3.2 `load_topic`: nowe klucze według W1 (`t3` opcjonalne, `dodatki` i `wykluczenia` na górnym poziomie, `diagnostyka.znaczniki_srodladowe` opcjonalne). Usunąć wymóg „wykluczenia puste” (`tematy.py` ~139–140). Dodatki czytać z górnego poziomu wszędzie, gdzie dziś czyta się `t3.dodatki` (`_dodatek`, raport).
  - [ ] 3.3 `load_method`: `METHOD = 'tematy-v2'`, `ADR = 'docs/adr/ADR-012-tematy-fala-1.md'`, pole `operator_warstwy` z walidacją. `sampling` i `progi` bez zmian.
  - [ ] 3.4 `config/generator/tematy.json`: `version`, `adr`, `operator_warstwy: ["T2", "T3"]`. Hashe `teksty` zostają do grupy 5.
  - [ ] 3.5 `morze.json`: przenieść 6 dodatków z `t3.dodatki` na górny poziom, dodać `wykluczenia: []`. Wersja zostaje `morze-v2`, reszta bez zmian (porównać `json` przed i po bez pola `dodatki`).
  - [ ] 3.6 `tests/tematy_helpers.py` i `tests/test_tematy_dodatki.py`: dodatki na górnym poziomie, metoda `tematy-v2`; fikstura dostaje parametr `t3=True|False`.
  - [ ] 3.7 Uruchomić 7 nowych testów oraz `tests.test_tematy_config` i `tests.test_tematy_dodatki`. Commit i push: `feat(tematy): schemat tematu i metoda tematy-v2 (#12)`.

**Kryteria odbioru:**
- 7 testów przechodzi, poprawione moduły też.
- `grep -n "t3.*dodatki\|\['t3'\]\['dodatki'\]" literaki_slownik/tematy.py` nie daje trafień.

### Grupa 4: Wejścia zależne od tematu i wykluczenia (W2, W3, W1 osiągalność)
**Zależności:** 3
**Pliki:** `literaki_slownik/tematy.py`, `tests/tematy_helpers.py`, `tests/test_tematy_inputs.py`, `tests/test_tematy_wykluczenia.py`
**Kroki:** 6

- [ ] 4.0 Czytać IATE tylko przy `t3` i stosować wykluczenia lematów
  - [ ] 4.1 Napisać 6 testów (`tests/test_tematy_inputs.py`, nowy `tests/test_tematy_wykluczenia.py`):
    - temat bez `t3`: budowa przechodzi, T3 puste, IATE nie ma w rejestrze czytanych plików ani w `inputs` manifestu, `candidates` nie woła `t3_candidates`;
    - temat z `t3`: blok `iate` (`member`, `last_modified`, `bytes`) w manifeście bez zmian;
    - wykluczenie lematu usuwa leksem z TSV (w T1, T2 i T3) i daje wpis `{lemat, czesc_mowy, powód, klucze, warstwy}` w `summary.wykluczenia`;
    - wykluczenie bez trafienia wśród kandydatów daje kod 4;
    - wykluczenie poddrzewa nieosiągalne z korzeni (liczone bez wykluczeń) daje kod 4;
    - `raport.md` ma sekcję „Wykluczenia” tylko przy niepustej liście.
  - [ ] 4.2 `check_inputs`: rejestracja i hash `iate` tylko przy `t3`. `candidates`: `t3_candidates` tylko przy `t3`, inaczej T3 = {}. Manifest pakietu: `inputs` tylko z użytych wejść. `tematy-sources.json` bez zmian.
  - [ ] 4.3 `build_entries`: wykluczenia po zebraniu T1–T3, przed dodatkami, formami i diagnostyką. Dopasowanie `lemma_base` = `lemat` i `czesc_mowy` w klasach leksemu (wzór `map_lemmas`). Kod 4 przy braku trafienia.
  - [ ] 4.4 `t2_candidates`: osiągalność każdego `wykluczenia_poddrzew` w domknięciu bez wykluczeń; brak = kod 4. `summary.json` dostaje `wykluczenia`; `raport.md` sekcję „Wykluczenia”.
  - [ ] 4.5 `tests/tematy_helpers.py`: wariant `inputs_fixture` bez T3 i z drugim tematem (inny `id`, korzenie z małej Słowosieci fikstury).
  - [ ] 4.6 Uruchomić 6 nowych testów oraz `tests.test_tematy_inputs`, `tests.test_tematy_sources`, `tests.test_tematy_layers`. Commit i push: `feat(tematy): wejścia zależne od tematu i wykluczenia lematów (#12)`.

**Kryteria odbioru:**
- 6 testów przechodzi.
- Budowa bez `t3` na fiksturze nie otwiera zipa IATE (rejestr).

### Grupa 5: Teksty z odcinkami i raport zależny od tematu (W4)
**Zależności:** 4
**Pliki:** `literaki_slownik/tematy.py`, `config/generator/tematy-teksty/ATTRIBUTIONS-tematy.md`, `config/generator/tematy-teksty/LIMITATIONS.md`, `config/generator/tematy-teksty/TERMS.md`, `config/generator/tematy.json`, `tests/tematy_helpers.py`, `tests/test_tematy_teksty.py`, `tests/test_tematy_package.py`
**Kroki:** 7

- [ ] 5.0 Zdejmować odcinki T3 i SRODLADOWE według tematu
  - [ ] 5.1 Napisać 6 testów w nowym `tests/test_tematy_teksty.py`:
    - temat z T3 i znacznikami: `ATTRIBUTIONS-tematy.md` po zdjęciu znaczników ma stary hash `d6673156…`, a `TERMS.md` stary hash `b4250289…`;
    - `LIMITATIONS.md` równa się staremu tekstowi z podmienionymi tylko punktami T2 i T3 (W4);
    - temat bez T3: teksty pakietu bez „IATE” i bez „śródląd”;
    - odcinek niezamknięty, zagnieżdżony albo `@@SRODLADOWE@@` poza odcinkiem lub nie raz daje kod 2;
    - temat z T3 bez znaczników (wzór medycyny): `summary.srodladowe` = `null`, raport bez sekcji i wiersza TL;DR o śródlądowych, `summary.t3` niepuste;
    - temat o innym `id`: `raport.md` i komunikaty bez „MORZE”, lista użytych warstw zamiast „T1 < T2 < T3”; bez `t3` pole `summary.t3` = `null`.
  - [ ] 5.2 Jedna funkcja zdejmowania odcinków w `_write_package`, przed podmianą `@@SRODLADOWE@@`. Reguła bajtowa z W4: w zachowanym odcinku usuwamy tylko bajty znaczników; usunięty odcinek tracimy od `<!--X-->` do `<!--/X-->` włącznie.
  - [ ] 5.3 Teksty w `tematy-teksty/`: odcinek T3 obejmuje sekcję IATE w `ATTRIBUTIONS-tematy.md`, zdanie o IATE w `TERMS.md` (spacja wewnątrz odcinka) i punkt T3 w `LIMITATIONS.md`. Odcinek SRODLADOWE obejmuje punkt śródlądowy (od `\n- `). Nowe brzmienie punktów T2 i T3 według W4.
  - [ ] 5.4 `config/generator/tematy.json`: nowe hashe w `teksty`.
  - [ ] 5.5 `summary` i `raport`: nazwa listy z `id`, sekcje T3 i „Żegluga śródlądowa (T3)” tylko przy T3 albo znacznikach, `srodladowe` = `null` bez znaczników (D2), pole `t3` = `null` bez `t3`.
  - [ ] 5.6 `tests/tematy_helpers.py` i `tests/test_tematy_package.py`: fikstura tekstów ze znacznikami; poprawić asercje, które czytały stary `LIMITATIONS.md`.
  - [ ] 5.7 Uruchomić 6 nowych testów oraz `tests.test_tematy_package`. Commit i push: `feat(tematy): teksty i raport zależne od tematu (#12)`.

**Kryteria odbioru:**
- 6 testów przechodzi; stare hashe `ATTRIBUTIONS-tematy.md` i `TERMS.md` są przypięte w teście.
- `grep -n "MORZE" literaki_slownik/tematy.py` daje tylko komentarze albo nic.

### Grupa 6: Próba operatora i werdykt w pakiecie (W5, W6 w `tematy.py`)
**Zależności:** 5
**Pliki:** `literaki_slownik/tematy.py`, `tests/tematy_helpers.py`, `tests/test_tematy_package.py`
**Kroki:** 4

- [ ] 6.0 Ograniczyć próbę operatora do `operator_warstwy`
  - [ ] 6.1 Napisać 4 testy w `tests/test_tematy_package.py`:
    - `sample.json` losuje T1, T2 i T3 (pusta T3 ma `EMPTY_NOT_COVERAGE`), a `operator.strata` ma tylko T2 i T3;
    - `strata`, `items` i `unique_selected_units` są równe dla `tematy-v1` i `tematy-v2` na tej samej fiksturze (losowanie bez zmian);
    - temat bez `t3`: `summary.werdykt.nie_dotyczy` = `["t3_tak"]`, a `t3_tak` nie ma w `czeka`;
    - temat z `t3`: `nie_dotyczy` pusty; `t1_tak` nie ma w `czeka` (liczony z ocen agenta).
  - [ ] 6.2 `sample` i `review_template`: `operator.strata` tylko z `operator_warstwy`, `operator_per_stratum` bez zmian.
  - [ ] 6.3 `CZEKA` i `summary.werdykt`: progi warstw operatora i zgodność czekają; `nie_dotyczy` według W6.
  - [ ] 6.4 Uruchomić 4 nowe testy oraz `tests.test_tematy_package`. Commit i push: `feat(tematy): próba operatora według operator_warstwy (#12)`.

**Kryteria odbioru:**
- 4 testy przechodzą.
- Próba agenta dla morza ma te same pozycje co w #11.

### Grupa 7: Checker i strona R2 (W6, W7)
**Zależności:** 6
**Pliki:** `scripts/check_tematy_package.py`, `scripts/tematy_review.py`, `tests/test_check_tematy_package.py`, `tests/test_tematy_review.py`, `tests/tematy_helpers.py`
**Kroki:** 6

- [ ] 7.0 Dostosować odbiór pakietu i przeglądu
  - [ ] 7.1 Napisać 7 testów:
    - checker PASS na pakiecie bez `t3`; manifest wejść nadal wymaga `iate`, a piny porównujemy tylko dla użytych wejść; T3 musi być puste;
    - wiersz TSV z lematem i klasą z `wykluczenia` tematu daje odmowę;
    - `check_sample`: `operator.strata` różne od `operator_warstwy` daje odmowę;
    - `--review` bez ocen operatora: `t1_tak` z ocen agenta policzony, progi T2 i T3 oraz zgodność „czeka”;
    - `--review` temat bez `t3`: `t3_tak` = `nie_dotyczy` i nie blokuje „dalej”;
    - `--review` temat z `t3` i pustą T3: `t3_tak` niespełniony;
    - `tematy_review.py strona` i `zapisz` biorą warstwy z `sample.operator.strata`, więc na stronie są tylko T2 i T3.
  - [ ] 7.2 `check_tematy_package.py`: `METHOD`, `ADR`, `load_config` z `operator_warstwy`. Temat z pakietu czytamy przed porównaniem pinów (dziś wiersze 304–316) i porównujemy piny tylko użytych wejść. `addenda` czyta górne `dodatki`. Dochodzi kontrola wykluczeń (W3) i usuwamy wymóg „temat bez wykluczeń”.
  - [ ] 7.3 `verdict` i `check_review` według W6: progi warstw spoza `operator_warstwy` z ocen agenta, zawsze; `nie_dotyczy` przy braku `t3`; zgodność i kappa na pozycjach ocenionych przez obu.
  - [ ] 7.4 `tematy_review.py`: `page_items` i `record` iterują po `sample.operator.strata` zamiast `PROBA`. Wygląd strony bez zmian.
  - [ ] 7.5 Kontrola: `grep -n "literaki_slownik" scripts/check_tematy_package.py` bez importu.
  - [ ] 7.6 Uruchomić 7 nowych testów oraz `tests.test_check_tematy_package` i `tests.test_tematy_review`. Commit i push: `feat(tematy): checker i strona R2 dla tematy-v2 (#12)`.

**Kryteria odbioru:**
- 7 testów przechodzi.
- Checker nie importuje `literaki_slownik`.

### Grupa 8: ADR-012 i odsyłacz w ADR-010 (W15, część 1)
**Zależności:** brak
**Pliki:** `docs/adr/ADR-012-tematy-fala-1.md`, `docs/adr/ADR-010-tematy-v1.md`
**Kroki:** 4

- [ ] 8.0 Zapisać zmianę metody przy kodzie
  - [ ] 8.1 Kontrola zamiast testów: format jak `ADR-010` (TL;DR, Kluczowe decyzje, Otwarte pytania). Linki prowadzą do istniejących ścieżek. Jedyna nazwa gry to Literaki.
  - [ ] 8.2 `ADR-012-tematy-fala-1.md`: metoda `tematy-v2` i powód; T3 opcjonalne; `dodatki` na górnym poziomie; wykluczenia lematów i poddrzew z regułą „bez trafienia”; teksty z odcinkami (reguła bajtowa); `operator_warstwy` i `nie_dotyczy`. Dalej: granice tematów z `clarifications.md`, zgoda operatora na atomy i sport (2026-10-29), wycięcia z pomiarami (W11), nazwy pakietów. Regresja morza (W8) jako plan, wynik dopisuje grupa 17. Stare pakiety sprawdza checker z `a633136` (D8).
  - [ ] 8.3 `ADR-010-tematy-v1.md`: odsyłacz „Przegląd i schemat tematu zmienia ADR-012”.
  - [ ] 8.4 Commit i push: `docs(tematy): ADR-012 pierwsza fala tematów (#12)`.

**Kryteria odbioru:**
- Plik ADR-012 istnieje przed regresją morza (9), bo `tematy.json` na niego wskazuje.

### Grupa 9: Regresja morza (W8) — seria budów bez commitów
**Zależności:** 7, 8
**Pliki:** `T/analysis/verify_real.py`, `T/analysis/regresja_morze.py`, `T/verification/regresja-morze.json`, `T/work-log.md`
**Kroki:** 6

- [ ] 9.0 Potwierdzić, że morze-v2 się nie zmieniło
  - [ ] 9.1 Kontrola zamiast testów: `T/analysis/verify_real.py` (kopia z #11 z argumentami `--topic`, `--a`, `--b`) sprawdza `git_dirty: false`, pusty `git status --porcelain` dla `config/` i `scripts/`, równe `SHA256SUMS` a i b oraz checker PASS na obu.
  - [ ] 9.2 Przed serią: drzewo czyste i wypchnięte, HEAD zapisany w work-logu. Od tej chwili do 9.4 nie ma commitów (D1).
  - [ ] 9.3 W tle zbudować `data/work/tematy-morze-v2-<data>-a`, potem `-b`. Następnie checker na obu. Czas każdej budowy idzie do work-logu. Czytamy werdykt, nie tylko kod wyjścia.
  - [ ] 9.4 `T/analysis/regresja_morze.py` porównuje nowy pakiet a z `data/work/tematy-v2-20261029-a` według W8:
    - bajtowo równe `MORZE.txt.gz` (`6e78d1ef…`), `MORZE.tsv.gz` (`83037db1…`), `ATTRIBUTIONS.md` (`a3a221e9…`) i `TERMS.md` (`b4250289…`);
    - `LIMITATIONS.md` różni się tylko punktami T2 i T3 (`diff`);
    - `summary.json` równy po usunięciu `method`, `wykluczenia` i `werdykt.nie_dotyczy`;
    - `sample.json`: równe `strata`, `items`, `unique_selected_units` i `overlaps`, a `operator.strata` = T2, T3;
    - liczby: 970 wpisów, 11 035 form, test 37/37.
    Wynik zapisujemy do `T/verification/regresja-morze.json`.
  - [ ] 9.5 Różnica poza listą „mogą się różnić” z W8 = zatrzymanie. Poprawka idzie w grupach 3–7 (`fix(tematy)`), potem powtarzamy grupę 9.
  - [ ] 9.6 Po serii: commit i push `maister: #12 regresja morza`.

**Kryteria odbioru:**
- a = b, checker PASS na obu; wszystkie punkty W8 zgodne.
- Między budową a i commitem z 9.6 HEAD się nie zmienił.

### Grupa 10: Przepięcie ocen morza (W9)
**Zależności:** 9
**Pliki:** `T/analysis/przepnij_morze.py`, `T/analysis/test_przepnij_morze.py`, `T/verification/tematy-morze-review.json`, `T/verification/review-check-morze.json`
**Kroki:** 5

- [ ] 10.0 Przenieść oceny z #11 na nowy pakiet morza
  - [ ] 10.1 Napisać 2 testy w `T/analysis/test_przepnij_morze.py` (pliki syntetyczne):
    - wiązanie kopiuje z szablonu `sample_sha256`, `canonical_index_sha256`, `evidence_sha256` i `version`, a `sha256sums_sha256` = hash `SHA256SUMS`;
    - oceny agenta i `agent_sha256` bez zmian; od operatora zostają tylko klucze T2 i T3; `operator.agent_sha256` = `agent_sha256`.
  - [ ] 10.2 `T/analysis/przepnij_morze.py`: wejście `.maister/tasks/development/2026-10-28-11-tematy-morze/verification/tematy-morze-v2-review.json` i nowy pakiet a z grupy 9. Wyjście `T/verification/tematy-morze-review.json`. Na końcu skrypt woła checker `--review` i zapisuje wynik do `T/verification/review-check-morze.json`.
  - [ ] 10.3 Skrypt porównuje wynik z oczekiwanym (W9): `t1_tak` (agent) 23/25 spełniony, `t2_tak` i `t3_tak` (operator) 1, `t2_nie` 0, zgodność 20/57, kappa 0 niespełniona, werdykt „popraw”. Inny wynik daje kod 1 i zatrzymanie.
  - [ ] 10.4 Uruchomić 2 nowe testy.
  - [ ] 10.5 Commit i push: `maister: #12 przepięcie ocen morza`.

**Kryteria odbioru:**
- 2 testy przechodzą; checker `--review` daje werdykt z W9.

### Grupa 11: Pliki 9 tematów (W11, W10.5)
**Zależności:** 2, 7
**Pliki:** `config/generator/tematy/zwierzeta.json`, `config/generator/tematy/rosliny.json`, `config/generator/tematy/medycyna.json`, `config/generator/tematy/muzyka.json`, `config/generator/tematy/kuchnia.json`, `config/generator/tematy/sport.json`, `config/generator/tematy/matematyka.json`, `config/generator/tematy/pogoda.json`, `config/generator/tematy/grzyby.json`, `tests/test_tematy_fala.py`
**Kroki:** 5

- [ ] 11.0 Zapisać 9 tematów z zamrożonymi listami
  - [ ] 11.1 Napisać 3 testy w `tests/test_tematy_fala.py` (czytają tylko pliki konfiguracji i `T/analysis/slowa-oczywiste.json`, bez danych surowych):
    - każdy z 9 plików przechodzi `load_topic`; `id` = nazwa pliku, wersja `<id>-v1`;
    - `diagnostyka.slowa_oczywiste` każdego tematu = `wynik[<id>]` z `slowa-oczywiste.json`;
    - `t3` ma tylko `medycyna` (IATE `2841`); `znaczniki_srodladowe` nie ma żaden z 9; `dodatki` i `wykluczenia` puste.
  - [ ] 11.2 Napisać 9 plików według tabeli W11 (atomy, korzenie z nazwami, relacje, wykluczenia poddrzew, `t2.tryb: "pelne"`). Medycyna `t3.iate` ma te same pola co morze. W `uwagi` zapisujemy decyzje granic z `clarifications.md` i `scope-clarifications.md`.
  - [ ] 11.3 Kontrola na prawdziwej pochodnej (tylko odczyt): `_check_names` przechodzi dla każdego tematu. Liczby lematów T2 porównujemy z W11 (przypis D9: budowa nie zmienia wielkości liter). Wynik zapisujemy w work-logu.
  - [ ] 11.4 Uruchomić 3 nowe testy.
  - [ ] 11.5 Commit i push: `feat(tematy): 9 tematów pierwszej fali (#12)`.

**Kryteria odbioru:**
- 3 testy przechodzą; listy słów w 9 plikach są równe zamrożonemu plikowi.
- Commit z grupy 2.6 jest wcześniej w historii.

### Grupa 12: 18 budów fali (W12) — seria bez commitów
**Zależności:** 10, 11
**Pliki:** `T/analysis/verify_real.py`, `T/analysis/buduj_fale.sh`, `T/verification/builds.json`, `T/work-log.md`
**Kroki:** 6

- [ ] 12.0 Zbudować każdy temat dwa razy
  - [ ] 12.1 Kontrola zamiast testów: `verify_real.py` z grupy 9 dla każdego tematu. Rozszerzenie: T3 niepuste tylko w medycynie; IATE tylko w jej `inputs`, `ATTRIBUTIONS.md`, `TERMS.md` i `LIMITATIONS.md`; `srodladowe` = `null` we wszystkich 9.
  - [ ] 12.2 Przed serią: drzewo czyste i wypchnięte, HEAD zapisany. Od teraz do 12.6 nie ma commitów. Grupy 13–20 jeszcze nie ruszyły.
  - [ ] 12.3 `T/analysis/buduj_fale.sh` w tle, po kolei: grzyby, pogoda, matematyka, muzyka, sport, kuchnia, rośliny, zwierzęta, medycyna. Każdy temat buduje `data/work/tematy-<id>-v1-<data>-a`, potem `-b`, potem checker na obu. Nigdy równolegle. Czas każdej budowy idzie do logu.
  - [ ] 12.4 Po każdym temacie czytamy werdykt checkera i `verify_real.py`. Błąd = zatrzymanie serii. Poprawka `fix(tematy)` w grupach 3–7, a seria startuje od nowa od tematu, który padł.
  - [ ] 12.5 `T/verification/builds.json`: temat, katalog, `SHA256SUMS`, czas, wpisy, formy, warstwy, test słów. Liczbę T3 medycyny zapisujemy osobno (idzie do raportu bramki i ADR-012).
  - [ ] 12.6 Po ostatniej budowie: commit i push `maister: #12 budowy fali`.

**Kryteria odbioru:**
- 9 tematów: a = b, checker PASS na a i b.
- T3 i IATE tylko w medycynie; HEAD stały w czasie serii.

### Grupa 13: Oceny agenta R2 (W13.1–2)
**Zależności:** 12
**Pliki:** `T/analysis/instrukcja-oceny-agenta.md`, `T/analysis/record_agent_review.py`, `T/analysis/agent-ratings-<id>.json` (9 plików), `T/verification/tematy-<id>-review.json` (9 plików)
**Kroki:** 5

- [ ] 13.0 Ocenić próbę każdego tematu przed stroną operatora
  - [ ] 13.1 Kontrola zamiast testów: `record_agent_review.py` używa `tematy_review.agent_review`, który odrzuca brak klucza, obcy klucz i złą ocenę. Plik przeglądu przechodzi checker `--review` (bez ocen operatora: „czeka” tylko dla T2, T3 i zgodności).
  - [ ] 13.2 `T/analysis/instrukcja-oceny-agenta.md` według W13.1 (szeroki „tak”, „nie”, „niepewne”, granice z `clarifications.md`, lemat wspólny zostaje). Commit i push przed pierwszą oceną: `maister: #12 instrukcja oceny agenta`.
  - [ ] 13.3 Agent ocenia całą próbę każdego tematu (T1, T2, T3 po `min(50, N)`, z powodem). Jedna sesja na temat, sesje mogą iść równolegle. Agent czyta tylko instrukcję i `review-template.json` swojego tematu. Wynik: `T/analysis/agent-ratings-<id>.json`.
  - [ ] 13.4 `T/analysis/record_agent_review.py` (kopia z #11 z pętlą po tematach) zapisuje `T/verification/tematy-<id>-review.json` z `agent_sha256`.
  - [ ] 13.5 Commit i push: `maister: #12 oceny agenta R2` (9 hashy w treści commita). Ten commit musi być przed grupą 14.

**Kryteria odbioru:**
- 9 plików przeglądu; hash ocen agenta każdego tematu jest w commicie przed stroną R2.
- Ok. 950 ocen, każda z powodem.

### Grupa 14: Strony R2 i strona zbiorcza (W13.3–4)
**Zależności:** 13
**Pliki:** `T/verification/tematy-<id>-r2.html` (9 plików), `T/verification/r2-zbiorcza.html`
**Kroki:** 4

- [ ] 14.0 Dać operatorowi 9 stron i jedną stronę wejścia
  - [ ] 14.1 Kontrola zamiast testów: każda strona ma tylko pozycje T2 (i T3 w medycynie), nie pokazuje ocen agenta i powstała dopiero po commicie z 13.5 (`tematy_review.py strona` odmawia bez hasha).
  - [ ] 14.2 `tematy_review.py strona` dla 9 tematów → `T/verification/tematy-<id>-r2.html`. Każdą publikujemy jako prywatny artefakt claude.ai.
  - [ ] 14.3 `T/verification/r2-zbiorcza.html`: 9 linków z nazwą tematu, liczbą pozycji i stanem „ocenione / nie”. Kolejność jak budowy. Publikujemy jako prywatny artefakt.
  - [ ] 14.4 Przekazać orchestratorowi link do strony zbiorczej.

**Kryteria odbioru:**
- 9 stron i strona zbiorcza opublikowane; ok. 300 pozycji razem.

### Grupa 15: Oceny operatora R2 (W13.5) — ZATRZYMANIE: operator
**Zależności:** 14
**Pliki:** `T/verification/tematy-<id>-review.json` (9 plików), `T/verification/review-check-<id>.json` (9 plików), `T/verification/r2-zbiorcza.html`
**Kroki:** 5

- [ ] 15.0 Zebrać oceny operatora i policzyć werdykty
  - [ ] 15.1 Kontrola zamiast testów: checker `--review` na każdym pliku przeglądu.
  - [ ] 15.2 **ZATRZYMANIE (orchestrator):** operator ocenia na iPhonie 30 pozycji T2 w każdym temacie i 30 T3 w medycynie. JSON wkleja po każdej stronie.
  - [ ] 15.3 Po każdym JSON: `tematy_review.py zapisz`, potem checker `--review` → `T/verification/review-check-<id>.json`. Na stronie zbiorczej zmieniamy stan tematu i publikujemy ją ponownie pod tym samym adresem.
  - [ ] 15.4 Gdy temat nie ma JSON, orchestrator przypomina o nim ze strony zbiorczej. Nie pomijamy go po cichu.
  - [ ] 15.5 Po 9 tematach: commit i push `maister: #12 oceny operatora R2`.

**Kryteria odbioru:**
- 9 plików `review-check-<id>.json` i `review-check-morze.json`; ok. 300 ocen operatora.

### Grupa 16: Zestawienie fali i raport bramki (W14)
**Zależności:** 10, 15
**Pliki:** `T/analysis/zestawienie_fali.py`, `T/analysis/test_zestawienie_fali.py`, `T/verification/zestawienie-fali.json`, `T/verification/gate-report.md`
**Kroki:** 5

- [ ] 16.0 Zestawić 10 tematów dla wspólnej oceny
  - [ ] 16.1 Napisać 3 testy w `T/analysis/test_zestawienie_fali.py` (małe pakiety syntetyczne):
    - macierz nakładania: liczba wspólnych lematów dla pary i do 10 przykładów, posortowanych deterministycznie;
    - wiersz tematu bierze liczby z `summary.json`, `release-manifest.json` i `review-check-<id>.json`, a nie z pamięci;
    - temat bez T3 ma w kolumnie T3 „nie dotyczy”, a nie 0.
  - [ ] 16.2 `T/analysis/zestawienie_fali.py`: czyta 10 pakietów (9 z grupy 12, morze z grupy 9) i 10 plików `review-check-*`. Wynik: `T/verification/zestawienie-fali.json`.
  - [ ] 16.3 `T/verification/gate-report.md` (TL;DR, Kluczowe decyzje, Otwarte pytania). Tabela 10 tematów: wpisy i warstwy, formy, ∩ POP i ∩ POP00 (leksemy, formy), diagnostyka kandydaci → BROAD → STANDARD, test słów z brakującymi, trafność R2 (agent dla każdej warstwy, operator T2 i T3), zgodność, kappa, werdykt automatyczny. Do tego macierz nakładania, liczba T3 medycyny i puste pola na decyzje operatora.
  - [ ] 16.4 Uruchomić 3 nowe testy.
  - [ ] 16.5 Commit i push: `maister: #12 zestawienie fali`.

**Kryteria odbioru:**
- 3 testy przechodzą; tabela ma 10 wierszy, werdykty równe checkerowi.

### Grupa 17: Dokumenty generatora (W15, część 2)
**Zależności:** 12
**Pliki:** `docs/adr/ADR-012-tematy-fala-1.md`, `docs/generator/cli.md`, `docs/generator/raporty.md`, `docs/generator/jakosc.md`, `docs/runbook-wiki.md`, `.maister/docs/INDEX.md`
**Kroki:** 6

- [ ] 17.0 Opisać tematy-v2 w dokumentach projektu
  - [ ] 17.1 Kontrola zamiast testów: `python3 -m unittest tests.test_documented_names` przechodzi; linki prowadzą do istniejących ścieżek; jedyna nazwa gry to Literaki.
  - [ ] 17.2 `ADR-012`: wynik regresji (z `T/verification/regresja-morze.json`) i liczba T3 medycyny (z `builds.json`).
  - [ ] 17.3 `cli.md` (TEMATY): uogólnienie z morza, `<ID>.txt.gz`, opcjonalne T3, nazwy pakietów `tematy-<wersja tematu>-YYYYMMDD-{a,b}`. `raporty.md`: `counts.<id>`, `wykluczenia`, `srodladowe` tylko przy znacznikach, `werdykt.nie_dotyczy`. `jakosc.md`: `operator_warstwy`, progi z ocen agenta.
  - [ ] 17.4 `docs/runbook-wiki.md`, sekcja TEMATY: `counts.<id>`, przykłady sprawdzane w `<ID>.tsv.gz`, tabela tematów na jednej stronie.
  - [ ] 17.5 `.maister/docs/INDEX.md`: ADR-012 i zadanie #12.
  - [ ] 17.6 Commit i push: `docs(tematy): tematy-v2 w dokumentach generatora (#12)`.

**Kryteria odbioru:**
- Każda nowa nazwa z kodu (`operator_warstwy`, `wykluczenia`, `nie_dotyczy`) ma opis w `docs/`.

### Grupa 18: Wiki (W15, część 3)
**Zależności:** 16, 17
**Pliki:** `WIKI/Slownik-TEMATY.md`, `WIKI/Home.md`, `WIKI/Slownik-STANDARD.md`, `WIKI/_Sidebar.md`, `WIKI/Historia-zmian.md`
**Kroki:** 5

- [ ] 18.0 Pokazać 10 tematów na wiki, nadal „W przygotowaniu”
  - [ ] 18.1 Kontrola zamiast testów: lista z runbooka (`docs/runbook-wiki.md:79`). Jeden ekran na stronę, linki `[X](Slownik-X)`, bez list słów, jedyna nazwa gry to Literaki. Liczby pochodzą z `zestawienie-fali.json` i manifestów, a przykłady sprawdzamy w `<ID>.tsv.gz`.
  - [ ] 18.2 `git -C WIKI pull --ff-only`. `Slownik-TEMATY.md`: tabela 10 tematów (wersja, wpisy, formy, ∩ POP, ∩ POP00, test słów, stan) i krótki opis metody. Strona zostaje „W przygotowaniu”, bez linku pobrania.
  - [ ] 18.3 `Home.md`: wiersz TEMATY z liczbą tematów. `Slownik-STANDARD.md`: odsyłacz do TEMATY z liczbą tematów. `_Sidebar.md`: sprawdzić, że wpis TEMATY prowadzi do strony z 10 tematami.
  - [ ] 18.4 `Historia-zmian.md`: wpis #12.
  - [ ] 18.5 Commit i push w repo wiki: `wiki: TEMATY pierwsza fala (#12)`. Sprawdzić publiczny HTML strony; wpis w `T/work-log.md`.

**Kryteria odbioru:**
- Pięć stron zaktualizowanych; liczby zgodne z artefaktami; stan „W przygotowaniu”.

### Grupa 19: Przegląd testów i pełny zestaw
**Zależności:** 11, 16, 17
**Pliki:** `tests/test_tematy_*.py`, `tests/test_check_tematy_package.py`, `tests/test_tematy_review.py`, `tests/tematy_helpers.py`
**Kroki:** 5

- [ ] 19.0 Przejrzeć testy i uruchomić raz cały zestaw
  - [ ] 19.1 Przejrzeć 41 nowych testów z grup 1, 3–7, 10, 11 i 16 wobec listy „Do pokrycia” w spec.
  - [ ] 19.2 Wypisać luki tylko dla #12, np. wykluczenie trafiające w dodatek (kod 2) albo temat z `t3` i pustą T3 w `summary`.
  - [ ] 19.3 Dopisać najwyżej 10 testów.
  - [ ] 19.4 Raz uruchomić pełny zestaw: `python3 -m unittest discover -s tests -p 'test_*.py'` (oczekiwane ok. 553–563 OK) oraz `python3 -m unittest discover -s scripts -p 'test_audit_sgjp.py'` (5 OK). Czytamy linię wyniku, nie tylko kod wyjścia. Czerwony test w generatorze daje `fix(tematy)` i ponowne budowy tematów, których dotyczy.
  - [ ] 19.5 Commit i push: `test(tematy): domknij luki (#12)`.

**Kryteria odbioru:**
- Pełny zestaw przechodzi; dodano najwyżej 10 testów.

### Grupa 20: Bramka operatora (W14) — ZATRZYMANIE: operator
**Zależności:** 18, 19
**Pliki:** `T/verification/gate-report.md`, `T/decision-log.md`, `T/work-log.md`
**Kroki:** 4

- [ ] 20.0 Wspólna decyzja dla 10 tematów
  - [ ] 20.1 Kontrola: werdykt każdego tematu w `gate-report.md` = werdykt z `review-check-<id>.json`.
  - [ ] 20.2 **ZATRZYMANIE (orchestrator):** orchestrator pokazuje operatorowi raport bramki z treścią (tabela, macierz, werdykty). Operator wybiera dla każdego z 10 tematów: dalej, popraw albo stop.
  - [ ] 20.3 Decyzje z datą zapisujemy w `gate-report.md` i `T/decision-log.md`. Do tego lista lematów do wykluczenia w v2 tematów, bez budowy v2.
  - [ ] 20.4 Commit i push: `maister: #12 decyzja bramki`. Bez wydania, tarballa i linku pobrania.

**Kryteria odbioru:**
- Decyzja dla każdego z 10 tematów zapisana; wydania nie ma.

## Kolejność wykonania
1. Fala 1: grupy 1, 3, 8 równolegle (rozłączne pliki: `T/analysis`, kod, `docs/adr`).
2. Fala 2: grupa 2 (operator, 2.4) równolegle z grupą 4.
3. Grupy 4 → 5 → 6 → 7 po kolei (wspólne `tematy.py` i `tests/tematy_helpers.py`).
4. Grupa 9 (po 7 i 8): seria 2 budów bez commitów.
5. Grupy 10 i 11 równolegle (11 czeka też na 2.6).
6. Grupa 12 (po 10 i 11): seria 18 budów bez commitów.
7. Grupy 13 i 17 równolegle (po 12).
8. Grupa 14 (po 13), grupa 15 (operator, 15.2).
9. Grupa 16 (po 10 i 15).
10. Grupa 18 (po 16 i 17), grupa 19 (po 11, 16, 17).
11. Grupa 20 (operator, 20.2).

Zatrzymania operatora: 2.4 (słowa oczywiste), 15.2 (oceny R2), 20.2 (bramka). Okna bez commitów: 9.2–9.6 i 12.2–12.6.

## Zgodność ze standardami
Według `.maister/docs/INDEX.md` i `docs/`:
- `AGENTS.md`: polski, zwięźle; dane surowe w `cache/` i `data/work/` poza Git; wiki w tej samej pracy; bez kontaktu z autorami źródeł; z gier tylko Literaki.
- `docs/adr/ADR-010-tematy-v1.md`, `ADR-011-zrodla-slowosiec-iate.md`: reguły warstw i źródła bez zmian; różnice opisuje ADR-012.
- `docs/runbook-wiki.md`: „W przygotowaniu”, liczby z artefaktów, przykłady z TSV.
- `docs/generator/cli.md`: koperta `--json`, kody wyjścia 2–5 (wykluczenie bez trafienia i poddrzewo nieosiągalne = 4, konfiguracja = 2).

## Antywzorce
- Nie commitować w trakcie serii budów (D1), także z grup równoległych.
- Nie pokazywać agentowi piszącemu słowa oczywiste kandydatów ani pakietów.
- Nie zmieniać list słów oczywistych po commicie z 2.6.
- Nie generować strony R2 przed commitem hasha ocen agenta.
- Nie pokazywać operatorowi ocen agenta.
- Nie używać prawdziwych danych w `tests/`.
- Nie sprawdzać starych pakietów nowym checkerem (D8).
- Nie puszczać budów ani checkera równolegle.

## Uwagi
- TDD: każda grupa z kodem zaczyna od 2–8 testów; grupy danych i operatora mają kontrolę zamiast testów.
- Po grupie uruchamiamy tylko jej testy i zmienione moduły TEMATY; pełny zestaw raz, w grupie 19.
- Postęp: odhaczać kroki w tym pliku i w `implementation-plan.html`.
- Najpierw ponowne użycie: `map_lemmas`, `_read_forms`, `verify_real.py` i `record_agent_review.py` z #11, `tematy_review.py strona/zapisz`, `quality.sample_strata`.
