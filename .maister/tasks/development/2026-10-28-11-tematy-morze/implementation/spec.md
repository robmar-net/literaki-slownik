# Specyfikacja: pilotaż TEMATY „morze” (#11)

## TL;DR
Nowa podkomenda `tematy` buduje lokalny pakiet TEMATY z tematem `morze`, według wzoru POP00: wsadowo, deterministycznie, bez sieci.
Lista to leksemy SGJP ∩ STANDARD w trzech rozłącznych warstwach: T1 etykiety SGJP, T2 Słowosieć 4.5 (pełne domknięcie od 6 korzeni), T3 IATE 2019 (`fullForm`, kod 4821).
Pakiet podaje przecięcia z POP i POP00, diagnostykę wobec BROAD i STANDARD, test 37 słów i udział żeglugi śródlądowej w T3.
Pobranie źródeł i pochodna Słowosieci to osobne skrypty. Operator ocenia 90 słów na stronie-artefakcie z przyciskiem „kopiuj JSON”.
Wydanie publiczne dopiero po bramce. Teraz: ADR-010, ADR-011 i strona wiki „W przygotowaniu”.

## Kluczowe decyzje
- **T2: pełne domknięcie** po relacjach 11, 25, 27 od 6 korzeni, kierunek `PARENT_ID → CHILD_ID`. Decyzja operatora z 2026-10-29, przed budową. W `morze.json`: `t2.tryb: "pelne"`.
- **T3: typ `fullForm`.** IATE 2019 nie zna typu `term`. Odrzucamy terminy `deprecatedTerm-admn-sts`. Kod dziedziny porównujemy jako cały kod z listy po przecinkach.
- **Kody części mowy Słowosieci przypięte:** 2 → `subst`, `depr`; 1 → `inf`; 4 → `adj`; 3 → `adv`. Kody 5–8 (angielskie) pomijamy wszędzie.
- **Rejestr czytanych plików.** Każdy plik czytany w budowie (także wewnątrz POP i POP00) trafia do rejestru z hashem. `confirm_unchanged` re-hashuje cały rejestr. To strukturalna naprawa błędu f33fe05.
- **Pochodna Słowosieci wiąże się z zipem przez `meta`.** Budowa nie hashuje zipa (465 MB). Hashuje pochodną i porównuje `meta` z pinem zipa.
- **BROAD i STANDARD przez manifest wydania.** Przypinamy `release-LL-PL-v30/release-manifest.json`. Jego hash musi równać się `export.release_manifest_sha256` przebiegu, a hashe BROAD i STANDARD muszą zgadzać się z wpisami w nim.
- **Próba agenta 50 przez `quality`.** `quality._config` dostaje rozmiar zależny od wersji (`tematy-quality-v1` → 50, reszta → 30). Operator dostaje pierwsze 30 z 50 każdej warstwy w kolejności rangi. Mała warstwa: cała.
- **Progi jako udziały.** Mianownik to rzeczywiste N ocen operatora w warstwie. „niepewne” nie jest „tak”.
- **Werdykt automatyczny tylko „dalej” albo „popraw”.** „stop” wybiera tylko operator na bramce.
- **Bez `explain --variant tematy` w v1 i bez refaktoru POP00.** Z `pop` upubliczniamy tylko `write_gzip`.

## Otwarte pytania / ryzyka
- **Szum pełnego domknięcia T2.** Na starej pochodnej 874 lematy, wśród nich `angora`, `anilana`, `bungee`, `chłodziwo`. Oceni to przegląd R2; wykluczeń poddrzew w v1 nie ma.
- **Struktura TBX znana z próbki 4,9 MB.** Rzadsze pola mogą wystąpić dalej. Parser odrzuca nieznane wartości `termType` tylko przez filtr (nie przerywa budowy) i liczy je w raporcie.
- **Mała T3.** Po odjęciu T1, T2 i ∩ STANDARD może zostać < 30 leksemów. Wtedy ocena obejmuje całą warstwę, a próg działa na udziałach.
- **Licencja Słowosieci 4.5** („4.2 © 2020”, link 404). Opisane w `LIMITATIONS.md` i ADR-011.
- **POP00 r2-a ma stan BUILT.** Nowa budowa POP00 zmieni liczby przecięć.
- **Koszt czasu.** Dwa hashe `build.sqlite` (22 GB) i jeden pełny skan `interpretation` na budowę. Minuty.
- **Nakład operatora.** Do 90 ocen.
- **Determinizm bajtów SQLite.** Pochodna zależy od wersji SQLite. Sprawdzamy dwiema budowami; hash przypinamy.

## Zmiany po audycie
Audyt: `verification/spec-audit.md` (1 krytyczna, 9 ważnych, 16 drobnych). Wszystkie przyjęte.
- **K1:** filtr T3 `typ: fullForm`; odrzucenie `deprecatedTerm-admn-sts`; zapis w ADR-011 (W5, W7).
- **W1:** DOCTYPE dozwolone; błąd tylko przy `<!ENTITY` lub podzbiorze wewnętrznym; zewnętrznego DTD nie pobieramy (W7, testy).
- **W2:** `subjectField` dzielony po `,`, porównanie całych kodów (W7).
- **W3:** decyzja operatora: pełne domknięcie, `t2.tryb: "pelne"` (W5, ADR-010).
- **W4:** przypięte kody części mowy, 5–8 pomijane, także w `wieloznaczny` (W4, W7).
- **W5:** T3 bierze tylko leksemy klasy `subst`/`depr`; definicja „jednego słowa”; rzeczowniki odczasownikowe jako `BRAK_LEKSEMU` z osobną liczbą (W7, W8).
- **W6:** mała warstwa: cała populacja; progi jako udziały (W4, W11).
- **W7:** do progu idzie wynik całości; T1 i T1 ∪ T2 diagnostycznie (W9).
- **W8:** definicja zgodności i kappy na 3 kategoriach (W11, W12).
- **W9:** `ATTRIBUTIONS.md` z sekcją SGJP z pakietu POP (W13).
- **D1:** `tests/test_pop.py:1352` dostaje nową nazwę `write_gzip` w `mock.patch.object`; bez aliasu.
- **D2:** klucze `sampling` jak w `quality._config`; `operator_per_stratum` na górnym poziomie.
- **D3:** `valid=1` w pochodnej; `status` bez filtra; synsety sztuczne przechodzimy, lematów z nich nie bierzemy.
- **D4:** nazwa korzenia = `lemma + ' ' + variant` jednostki o najniższym `unitindex`.
- **D5:** przypięty manifest `release-LL-PL-v30`.
- **D6:** test parsera z wielowierszowym `INSERT` i `\'`; liczności wobec starej pochodnej w ADR-011.
- **D7:** budowa nie hashuje zipa.
- **D8:** odstępstwo „pobieramy ponownie” w ADR-011; IATE z `last_modified` i nazwą pliku w zipie.
- **D9:** tylko stan BUILT, przegląd poza pakietem; odstępstwo w ADR-010.
- **D10:** lista znaczników śródlądowych ustalona teraz (W5); mierzymy hasła kandydatów T3, wpisy końcowe dodatkowo.
- **D11:** lista 37 słów w `morze.json`, nie w `tematy.json`.
- **D12:** hash ocen agenta zapisany przed wygenerowaniem strony operatora.
- **D13:** wiersz w tabeli źródeł `Home`; przykłady na wiki sprawdzane w `MORZE.tsv.gz`.
- **D14:** strona R2 jako prywatny artefakt claude.ai, działa na iPhonie, przycisk „kopiuj JSON”.
- **D15:** formy tylko dla leksemów kandydatów, porcjami po `lexeme_id`; bez `pop.load_forms` na BROAD.
- **D16:** kierunek `PARENT_ID → CHILD_ID` zamknięty; na nowej pochodnej potwierdza go jeden test.

## Cel
Zbudować i zmierzyć pilotażowy temat `morze`, tak by operator mógł zdecydować na bramce: dalej, popraw albo stop.

## Historie użytkownika
- Jako operator chcę zbudować temat jednym poleceniem z przypiętych wejść, żeby wynik dało się odtworzyć.
- Jako operator chcę widzieć, ile tematu jest w POP i POP00, żeby ocenić, czy bot na mniejszym słowniku z niego skorzysta.
- Jako operator chcę ocenić 90 słów przyciskami na iPhonie, bez wglądu w oceny agenta, żeby bramka miała drugiego oceniającego.
- Jako odwiedzający wiki chcę wiedzieć, że TEMATY powstaje i z czego.

## Wymagania

### W1. Pobranie źródeł (osobny krok, z siecią)
- Skrypt `scripts/fetch_tematy_sources.py`:
  - IATE: `https://iate.europa.eu/em-api/artifacts/full-tbx` → `cache/iate/IATE_download.zip`;
  - Słowosieć 4.5: `https://clarin-pl.eu/server/api/core/bitstreams/3197cd0f-bb4e-41ba-93e0-eec99ab8d519/content` → `cache/plwordnet/wordnet_work_4_5.zip`.
- Pobiera `curl -fL` do pliku tymczasowego w katalogu celu, liczy SHA-256 i bajty, przenosi bez nadpisywania.
- Wypisuje rekord JSON: `url`, `retrieved_at` (UTC, ISO 8601), `sha256`, `bytes`, `path`. Dla IATE także `last_modified` (nagłówek; oczekiwany 30.09.2019) i `member` (nazwa pliku TBX w zipie).
- Słowosieć: hash musi równać się `30edc5f85c06408d372a897f1d1ff3d03fa939b8680b176c1f97351f4a72dcbc`; inaczej błąd.
- Budowa (`tematy`) nigdy nie używa sieci.

### W2. Pochodna Słowosieci
- Skrypt `scripts/build_plwordnet_db.py`: zip (zrzut SQL, 2,6 GB) → nowy plik SQLite, strumieniowo, deterministycznie, bez nadpisywania.
- Parser zrzutu obsługuje wielowierszowe `INSERT` i znaki ucieczki MySQL (`\'`, `\\`).
- Kopiuje tylko:
  - `lexicalunit`: `ID`, `lemma`, `pos`, `variant`;
  - `synset`: `ID`, `isabstract`;
  - `unitandsynset`: `LEX_ID`, `SYN_ID`, `unitindex`;
  - `synsetrelation`: `PARENT_ID`, `CHILD_ID`, `REL_ID`, tylko wiersze `valid=1`;
  - `relationtype`: `ID`, `name`;
  - `meta`: SHA-256 zipa, wersja skryptu.
- Lista dozwolonych tabel; wszystko inne pomijamy (m.in. `iplog`, `iplimit`, `tracker_*`). Bez kolumn `owner`, `comment`, `error_comment`.
- Sprawdza nazwy relacji 11, 25, 27 (`hiperonimia`, `część`, `miejsce`); inna nazwa = błąd.
- Wypisuje liczności tabel. ADR-011 porównuje je ze starą pochodną (1 491 277 relacji, 514 016 jednostek; różnica relacji = wiersze `valid=0`).
- Wiersze wstawia w stałej kolejności (po kluczu). Dwa uruchomienia dają ten sam hash.
- Wynik: `cache/plwordnet/plwn45-tematy.sqlite`. Stary `data/work/plwordnet/plwn45.sqlite` nie jest wejściem budowy.

### W3. Manifest źródeł `config/generator/tematy-sources.json`
- Wersja `tematy-sources-v1`. Wejścia (ścieżka + SHA-256):
  - `base_run` (manifest v31), `database` (`build.sqlite`);
  - `release_manifest` (`data/work/release-LL-PL-v30/release-manifest.json`), `standard`, `broad` (`4f1aace9…1271`);
  - `base_pop` (manifest pop-v3), `base_pop00` (manifest POP00 r2-a);
  - `plwordnet_zip` (bez ścieżki do hashowania; `url`, `retrieved_at`, `bytes`, `sha256`), `plwordnet_db`;
  - `iate` (z `url`, `retrieved_at`, `last_modified`, `member`, `bytes`).
- Budowa sprawdza: hash `release_manifest` = `export.release_manifest_sha256` przebiegu; hashe `standard` i `broad` = wpisy w tym manifeście.
- Nieznane klucze odrzucamy (wzór `pop00.load_sources`).

### W4. Konfiguracja metody `config/generator/tematy.json`
- `version: tematy-v1`, `adr: docs/adr/ADR-010-tematy-v1.md`.
- `sampling`: dokładnie klucze `quality._config`: `version: tematy-quality-v1`, `seed: literaki-slownik-tematy-v1`, `size_per_stratum: 50`, `encoding` (stała `quality.ENCODING`).
- `operator_per_stratum: 30` na górnym poziomie.
- `progi` (udziały, porównanie dokładnych ułamków):
  - test 37 słów, wynik całości ≥ 0,70;
  - T1: „tak” ≥ 0,90;
  - T2: „tak” ≥ 2/3 i „nie” ≤ 0,10;
  - T3: „tak” ≥ 2/3;
  - zgodność ≥ 0,80.
- `czesci_mowy`: kody Słowosieci → klasy tagów SGJP: `"2": ["subst","depr"]`, `"1": ["inf"]`, `"4": ["adj"]`, `"3": ["adv"]`. Inny kod = jednostka pomijana.
- `t3_klasy`: `["subst","depr"]`.
- `teksty`: ścieżki i SHA-256 plików w `config/generator/tematy-teksty/`.
- Walidacja: zbiór kluczy i typy; nieznane pola = błąd (kod 2).

### W5. Plik tematu `config/generator/tematy/morze.json`
- Schemat jak w projekcie (`high-level-design.md`, „Schemat pliku konfiguracji tematu”), z polami:
  - `t1.atomy_sgjp`: `mors.`, `żegl.`, `ryb.`;
  - `t2.korzenie`: 7354 `statek 1`, 2149 `okręt 1`, 4511 `łódź 2`, 6214 `marynarz 1`, 14136 `żegluga 1`, 14515 `żeglarstwo 1`;
  - `t2.relacje`: 11, 25, 27; `t2.tryb: "pelne"`; `t2.wykluczenia_poddrzew`: puste;
  - `t3.iate.kody_dziedzin`: `4821`; `t3.iate.typ: fullForm`; `t3.iate.niezawodnosc_min: 3`; `t3.iate.odrzuc_status: deprecatedTerm-admn-sts`;
  - `t3.dodatki`: puste; `wykluczenia`: puste;
  - `diagnostyka.slowa_oczywiste`: 37 słów z `scope-clarifications.md`, bez zmian;
  - `diagnostyka.znaczniki_srodladowe`: PL `śródląd`, `rzek`, `rzeczn`, `kanał`, `jezior`, `śluz`, `barka`; EN `inland`, `river`, `canal`, `lake`, `lock`, `barge`. Ustalone przed pierwszą budową; nie zmieniamy po wynikach.
- Walidacja: zbiór kluczy i typy, nieznane pola = błąd. Relacja spoza {11, 25, 27} = błąd. `t2.tryb` inny niż `pelne` = błąd (v1).
- Nazwa korzenia: `lemma + ' ' + variant` jednostki o najniższym `unitindex` w synsecie; niezgodna = błąd.
- Dodatek spoza STANDARD = błąd.

### W6. Podkomenda `tematy`
- `python3 -m literaki_slownik tematy --manifest M --config C --topic T --output-dir D [--json]`.
- Koperta `--json`, kody wyjścia i komunikaty jak w `pop00`.
- Nie nadpisuje: `D` nie może istnieć ani leżeć w wejściach. Staging obok celu, `chmod 0444`, `rename_noreplace`.
- Sprawdza wejścia: hashe, `FROZEN` przebiegu, manifest wydania (W3), zgodność POP i POP00 z bazą i STANDARD, `meta` pochodnej.
- Przed przeniesieniem re-hashuje każdy czytany plik z rejestru (manifest, konfiguracja, temat, teksty, wejścia, pliki wewnątrz POP i POP00).

### W7. Warstwy i pliki listy
- **Jedno słowo:** lemat po NFC i zmianie na małe litery składa się wyłącznie z liter alfabetu polskiego (a–z oraz ą ć ę ł ń ó ś ź ż). Spacja, łącznik, apostrof, cyfra = nie jedno słowo (pomijany, liczony w raporcie).
- **Klasa leksemu:** zbiór klas tagów (pierwszy segment tagu) jego interpretacji SGJP.
- **T1:** leksemy z interpretacją, w której kwalifikatory po podziale `|`, potem `,` zawierają atom tematu jako cały atom.
- **T2:**
  - pełne domknięcie od korzeni po relacjach 11, 25, 27, kierunek `PARENT_ID → CHILD_ID`;
  - przez synsety sztuczne (`isabstract=1`) przechodzimy, ale lematów z nich nie bierzemy;
  - `lexicalunit.status` bez filtra (znaczenie wartości 0–5 nieudokumentowane; zapis w ADR-011);
  - jednostka z kodem spoza `czesci_mowy` (m.in. 5–8) pomijana;
  - lemat → leksemy z równym `lexeme.lemma_base` i klasą z `czesci_mowy` dla kodu jednostki.
- **T3:**
  - hasła TBX, których `subjectField` po podziale `,` i przycięciu spacji zawiera cały kod z `kody_dziedzin` (samo `48` nie pasuje do `4821`);
  - terminy PL o `termType` = `fullForm`, bez `administrativeStatus` = `deprecatedTerm-admn-sts`, niezawodność ≥ 3, jedno słowo bez wielkich liter w źródle;
  - termin → leksemy z równym `lemma_base` i klasą z `t3_klasy`.
- **`BRAK_LEKSEMU`:** lemat bez pasującego leksemu. Rzeczowniki odczasownikowe (lemat = forma o tagu `ger`, bez własnego leksemu, np. `żeglowanie`) trafiają tu i mają osobną liczbę.
- Wpis = leksem (`lemma_id@source_id`). Warstwa = najniższa z T1 < T2 < T3. Źródła = wszystkie.
- Flaga `wieloznaczny`: `tak` / `nie` / `brak_danych`, według reguły ADR-007 badania; liczymy tylko jednostki z kodami 1–4.
- Formy: dla leksemów kandydatów czytamy `interpretation` porcjami po `lexeme_id` (wzór `pop00.read_analyses`), plus konstrukcje (`pop.load_constructions` z podzbiorem leksemów). Przecinamy ze zbiorami BROAD i STANDARD z `pop00.read_words`.
- `MORZE.txt.gz`: formy tematu ∩ STANDARD, posortowane, gzip deterministyczny (`pop.write_gzip`).
- `MORZE.tsv.gz`: wiersz na leksem: klucz, lemat, części mowy, warstwa, źródła, znaczenie źródłowe, `wieloznaczny`.

### W8. Raporty
- `reports/summary.json` i czytelny `reports/raport.md` (z tych samych liczb).
- Przecięcie z POP i POP00: liczba i % względem tematu; razem i T1/T2/T3; w leksemach i formach.
  - Leksem w POP: członek POP w `reports/units.json` pop-v3. Leksem w POP00: członek POP0.
  - Forma w POP / POP00: napis z `POP.txt.gz` / `POP00.txt.gz`.
- Diagnostyka przed ∩ STANDARD: kandydaci, ∩ BROAD, ∩ STANDARD, udziały; razem i na warstwę; leksemy i formy.
- Odrzuceni: `BRAK_LEKSEMU` (w lematach, z podliczbą `ger`), `NIE_JEDNO_SLOWO`, `POZA_BROAD`, `POZA_STANDARD`; liczba i do 10 przykładów na powód i warstwę, wybór deterministyczny.
- T3: liczby haseł według `termType` i odrzuconych `deprecatedTerm`.
- Udział `wieloznaczny` z 10 przykładami.
- Manifest: `counts.morze` z liczbami warstw i `overlap`.

### W9. Test 37 słów
- Słowo pokryte, gdy któryś wpis tematu ma ten lemat.
- Do progu idzie wynik całości (T1 ∪ T2 ∪ T3). T1 oraz T1 ∪ T2 są tylko diagnostyką.
- Dla każdego: liczba, %, lista brakujących. W `summary.json` i `raport.md`.

### W10. Żegluga śródlądowa w T3
- Hasło śródlądowe: termin PL lub EN zawiera znacznik jako początek słowa.
- Główna miara: hasła T3 kandydatów (po filtrach W7). Dodatkowo: wpisy T3 po ∩ STANDARD.
- Liczba, udział, do 20 przykładów. Nic nie wykluczamy.
- Wynik w raporcie; `LIMITATIONS.md` opisuje problem, podaje udział i listę znaczników.

### W11. Próby i przegląd R2
- Próba deterministyczna `min(50, N)` na warstwę (`quality.sample_strata`); operator: pierwsze `min(30, N)` w kolejności rangi. Gdy N mniejsze od rozmiaru, bierzemy całą warstwę.
- Szablon (`quality.review_template`) z danymi wpisu do oceny.
- Skala: tak / nie / niepewne.
  - Trafność warstwy = „tak” / N; „niepewne” nie liczy się jako „tak” ani jako „nie”.
  - Zgodność = odsetek identycznych ocen (3 kategorie) na pozycjach ocenionych przez obu.
  - Kappa Cohena na tych samych pozycjach, 3 kategorie.
- Kolejność: agent ocenia wszystkie pozycje i hash jego ocen trafia do pliku przeglądu (commit) przed wygenerowaniem strony operatora.
- Skrypt `scripts/tematy_review.py`:
  - `strona`: samodzielna strona HTML z pozycjami operatora, przyciski tak / nie / niepewne, bez ocen agenta. Odmawia, gdy brak hasha ocen agenta.
  - `zapisz`: łączy JSON operatora z plikiem przeglądu, sprawdza klucze, hashe i hash ocen agenta.
- Kanał: strona publikowana jako prywatny artefakt claude.ai. Działa na iPhonie (wąski ekran, duże przyciski). Przycisk „kopiuj JSON” plus pole tekstowe z JSON do ręcznego zaznaczenia. Szkic ocen w `localStorage` (w `try/catch`). Operator wkleja JSON w rozmowę. Przed przeglądem sprawdzamy stronę na telefonie operatora.
- Plik przeglądu: `verification/tematy-morze-review.json` w folderze zadania. Ocena agenta (do 150 pozycji, z powodem) i operatora (do 90). Związany z `SHA256SUMS` pakietu i `sample_sha256`.

### W12. Checker `scripts/check_tematy_package.py`
- Nie importuje pakietu `literaki_slownik`.
- Sprawdza: `SHA256SUMS` i manifest, `MORZE.txt` ⊆ STANDARD, spójność TSV z TXT, warstwy rozłączne, przeliczone przecięcia z POP/POP00, brak kolumn `owner`/`comment` w przypiętej pochodnej.
- `--review`: kompletność i powiązanie przeglądu, trafność na warstwę z rzeczywistym N, zgodność i kappa (W11), test 37 słów (wynik całości), werdykt „dalej” / „popraw” z listą progów.

### W13. Dokumenty
- `docs/adr/ADR-010-tematy-v1.md`: lokalne ADR-001, 002, 005–010 badania; `t2.tryb: pelne` (decyzja operatora); stan tylko BUILT i przegląd poza pakietem (odstępstwo od ADR-008); progi jako udziały.
- `docs/adr/ADR-011-zrodla-slowosiec-iate.md`: 003, 004; pochodna (tabele, `valid=1`, `isabstract`, `status`, liczności); kierunek relacji; kody części mowy; `term` z projektu = `fullForm`; dopasowanie `subjectField`; DOCTYPE; ponowne pobranie Słowosieci (odstępstwo od `clarifications.md`); `last_modified` i `member` IATE.
- `ATTRIBUTIONS.md` pakietu: `ATTRIBUTIONS.md` z pakietu POP (`package_file`, zawiera SGJP BSD-2), potem nota i zastrzeżenie plWordNet oraz „Download IATE, European Union, 2019”.
- `docs/generator/cli.md`, `raporty.md`, `jakosc.md`; `docs/runbook-wiki.md`, sekcja TEMATY (przykłady na wiki sprawdzamy w `MORZE.tsv.gz`); `.maister/docs/INDEX.md`.

### W14. Wiki
- Strona `Slownik-TEMATY` „W przygotowaniu” na starcie: cel, źródła, link do #11.
- Po budowie: liczby z manifestu, nadal „W przygotowaniu”, bez linku pobrania.
- Wiersz na `Home` (także w tabeli źródeł: Słowosieć, IATE), wpis w `_Sidebar`, link ze `Slownik-STANDARD`, wiersz w `Historia-zmian`.

### W15. Determinizm
- Dwie budowy a/b z tych samych wejść: identyczne `SHA256SUMS`. Checker PASS na obu.

## Kod do ponownego użycia

### Istniejący kod
| Element | Plik | Użycie |
|---|---|---|
| `load_sources`, `check_inputs`, `build_package`, `confirm_unchanged` | `literaki_slownik/pop00.py` | wzór struktury; staging, `chmod`, obsługa błędów |
| `read_words`, `package_file` | `literaki_slownik/pop00.py` | import bez zmian (komunikat `read_words` uogólnić; żaden test go nie sprawdza) |
| `read_analyses` | `literaki_slownik/pop00.py` (184) | wzór odczytu form porcjami po `lexeme_id` |
| `checked_file`, `GeneratorError` | `literaki_slownik/inputs.py` | kontrola pinów |
| `dumps`, `load_json`, `sha256`, `write_json` | `literaki_slownik/canonical.py` | kanoniczny JSON i hashe |
| `load_constructions`, `_label` | `literaki_slownik/pop.py` | konstrukcje dla podzbioru leksemów, klucz leksemu |
| `_write_gzip` → `write_gzip` | `literaki_slownik/pop.py` (1767) | upublicznić; poprawić `pop.py`, `pop00.py:289`, `tests/pop00_helpers.py:9`, `tests/test_pop.py:1352` (cel `mock.patch.object`) |
| `sample_strata`, `review_template`, `SEEDS`, `ENCODING`, `_config` | `literaki_slownik/quality.py` | próba i szablon; nowy wpis w `SEEDS`, rozmiar 50 dla `tematy-quality-v1` |
| `code_identity` | `literaki_slownik/run.py` | manifest |
| `rename_noreplace` | `literaki_slownik/export.py` | przeniesienie bez nadpisania |
| wzór kontroli manifestu wydania | `literaki_slownik/pop.py` (115–117) | `export.release_manifest_sha256` |
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
- Przepływ: wejścia → T1/T2/T3 kandydaci → mapowanie na leksemy → formy kandydatów → diagnostyka BROAD/STANDARD → ∩ STANDARD → scalenie warstw → przecięcia z POP/POP00 → test 37 słów i śródlądowe → próba → pakiet (`high-level-design.md`, „Przepływ danych”).
- Moduł funkcyjny, bez klas, jak `pop00.py`. Jeden pełny skan `interpretation` z cache po `(tag, names, qualifiers)` daje T1 i klasy leksemów. Formy tylko dla kandydatów, porcjami.
- TBX czytamy strumieniowo z zipa (`iterparse`), zbierając tylko hasła z pasującym kodem. DOCTYPE bez podzbioru wewnętrznego dozwolone; `<!ENTITY` lub podzbiór wewnętrzny = błąd; zewnętrznego DTD nie ładujemy.
- Odczyt SQLite tylko do odczytu (`mode=ro`).
- Determinizm: sortowanie wszędzie, `canonical.dumps`, gzip z `mtime=0`, `code_identity()` w manifeście.
- Stan pakietu: tylko BUILT. Przegląd żyje poza pakietem (jak POP00); odstępstwo w ADR-010.

### Pliki pakietu
`MORZE.txt.gz`, `MORZE.tsv.gz`, `tematy/morze.json`, `method.json`, `reports/summary.json`, `reports/raport.md`, `reports/sample.json`, `reports/review-template.json`, `ATTRIBUTIONS.md`, `LIMITATIONS.md`, `TERMS.md`, `release-manifest.json`, `SHA256SUMS`.

### Kolejność prac
Wiki „W przygotowaniu” → ADR-010/011 → pobranie i pochodna (test kierunku na nowej pochodnej) → moduł i testy → budowy a/b → checker → ocena agenta i jej hash → strona R2 (artefakt, sprawdzony na iPhonie) → bramka.

## Wskazówki wdrożeniowe

### Testy
- 2–8 testów na grupę kroków. Weryfikacja uruchamia tylko nowe testy grupy, nie cały zestaw.
- Fikstura: mała baza z `schema.sql`, mała pochodna Słowosieci, mały TBX w zipie z prawdziwymi polami (DOCTYPE, `fullForm`, `abbreviation`, `deprecatedTerm-admn-sts`, `subjectField` z listą kodów), małe pakiety POP i POP00.
- Do pokrycia:
  - podział `|` i `,` z całymi atomami;
  - kierunek domknięcia (`statek` → `łódź`, `okręt`; jeden test na nowej pochodnej);
  - pominięcie kodów 5–8, także w `wieloznaczny`;
  - synset sztuczny przechodni bez lematów;
  - `subjectField` `48` nie pasuje do `4821`;
  - DOCTYPE przechodzi, `<!ENTITY` = błąd;
  - `ger` jako `BRAK_LEKSEMU`;
  - mała warstwa (N < 30) i progi na udziałach; „niepewne” w trafności i kappie;
  - parser zrzutu: wielowierszowy `INSERT`, `\'`;
  - leksem w kilku warstwach; nieznane pole konfiguracji; dodatek spoza STANDARD;
  - zmiana pliku wewnątrz POP podczas budowy; brak `owner` w pochodnej i jej determinizm;
  - `strona` odmawia bez hasha ocen agenta;
  - budowy a/b; checker z przeglądem.
- Polecenie: `python3 -m unittest discover -s tests -p 'test_*.py'` (pełny zestaw raz na końcu).

### Zgodność ze standardami
- `AGENTS.md`: polski, zwięźle; dane surowe poza Git; wiki w tej samej pracy; bez kontaktu z autorami.
- `docs/generator/publikacja.md`: atrybucje źródeł; bez wydania przed odbiorem.
- `docs/runbook-wiki.md`: układ strony słownika, tabela źródeł na `Home`, liczby z artefaktów.
- ADR-009 (POP00): wzór pakietu, dwie budowy, przegląd przed wydaniem.
- Commity: `feat(tematy): … (#11)`; po zapisie w `.maister/tasks` commit i push.

## Poza zakresem
- Kolejne tematy i fala ~10 tematów.
- Wydanie publiczne (tarball) i pełna strona wiki przed bramką.
- Dodatki ręczne, wykluczenia i wykluczenia poddrzew w `morze-v1`.
- Domknięcie ograniczone T2 (odrzucone przez operatora).
- `explain --variant tematy`.
- Wikisłownik, LLM, Słowosieć 5.0, konto EU Login, kontakt z autorami.
- Terminy wielowyrazowe, listy na poziomie znaczeń, ranking w temacie.
- Integracja z botami Literaki.
- Zmiany POP, POP0, POP00, BROAD i STANDARD.

## Kryteria sukcesu
1. `tematy` buduje pakiet offline; dwie budowy a/b mają identyczne `SHA256SUMS`.
2. Każdy wpis to leksem z formą w STANDARD v31, z warstwą, źródłami i `wieloznaczny`.
3. T3 nie jest pusta; raport podaje liczby haseł według `termType`.
4. `summary.json` i `raport.md` podają przecięcia z POP/POP00, diagnostykę BROAD/STANDARD z odrzuconymi (z podliczbą `ger`), test 37 słów (całość do progu; T1, T1 ∪ T2 diagnostycznie) i udział śródlądowych.
5. Zmiana dowolnego czytanego pliku w trakcie budowy kończy się błędem (kod 5) i brakiem pakietu.
6. Pochodna Słowosieci nie ma `owner`, `comment`, `iplog`, `iplimit` ani `tracker_*`; dwa uruchomienia skryptu dają ten sam hash.
7. Checker PASS na pakiecie; z `--review` podaje trafność z rzeczywistym N, zgodność, kappę i werdykt.
8. Hash ocen agenta zapisany przed stroną operatora; operator ocenił pozycje na iPhonie; raport bramki gotowy; decyzja operatora zapisana.
9. ADR-010, ADR-011, `ATTRIBUTIONS.md` (SGJP, plWordNet, IATE), dokumenty i wiki „W przygotowaniu” zaktualizowane.
