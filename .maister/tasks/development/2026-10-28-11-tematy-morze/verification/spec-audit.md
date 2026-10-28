# Audyt specyfikacji: pilotaż TEMATY „morze” (#11)

## TL;DR
Werdykt: **fail**. Specyfikację trzeba poprawić przed planem, ale poprawki są małe i lokalne.
Liczba uwag: **1 krytyczna, 9 ważnych, 16 drobnych**.
Uwaga krytyczna: plik IATE 2019 nie zna typu `term`. Filtr z W5 i W7 dałby pustą warstwę T3.
Specyfikacja zgadza się z decyzjami operatora i pokrywa wszystkie punkty #11. Nazwy, sygnatury, hashe i ścieżki zgadzają się z drzewem.

## Kluczowe decyzje
- **Pierwsze 4,9 MB IATE TBX sprawdziłem zapytaniem Range** (300 kB zipa, rozpakowane w scratchpadzie, bez zapisu w repo). Na tej próbce opieram K1, W1 i W2. Pełnego pliku nie pobierałem.
- **Kierunek i zakres T2 zmierzyłem na starej pochodnej** `data/work/plwordnet/plwn45.sqlite` (sha `b8cc27b8…4eb9`, tylko odczyt). Ta pochodna nie będzie wejściem budowy, więc wyniki trzeba powtórzyć na nowej.
- **K1 uznałem za krytyczną.** Wartość `term` siedzi w walidowanej konfiguracji tematu, a bez T3 bramka T3 jest nie do spełnienia.
- **Zakres domknięcia T2 (W3) to pytanie do operatora, nie decyzja techniczna.** Zmienia skład listy (AGENTS.md: decyzje o składzie omawiamy).
- **`build.sqlite` (22 GB) nie hashowałem.** Pin `4b0d17c6…7a45` jest zgodny z manifestem POP00 i z `verification.database_sha256` przebiegu.

## Otwarte pytania / ryzyka
- **Pytanie do operatora (W3): pełne domknięcie T2 czy ograniczone?** Pełne domknięcie po 11, 25 i 27 daje 874 lematy jednowyrazowe. Wersja ograniczona (hiponimy, potem jeden krok części i miejsc z ich hiponimami) daje 504. Pełne dokłada `achtersztag`, `bakburta`, `burta`, `cuma`, `bukszpryt`, ale też `angora`, `anilana`, `bungee`, `chłodziwo`. Trzy z tych słów są na liście 37 słów, więc wybór po wynikach byłby dopasowaniem do testu. Trzeba zdecydować przed budową.
- **Ryzyko licencyjne plWordNet** (nota 4.2, link 404) zostaje, jak w projekcie.
- **Struktura TBX jest znana tylko z próbki.** Rzadsze pola mogą pojawić się dalej w pliku.

## Sprawdzone i zgodne (skrót)
- **Decyzje operatora:**
  - R2: 30 słów na warstwę, razem 90 (`spec.md:75,130`);
  - progi jak w projekcie (`spec.md:76`);
  - IATE 4821 zostaje, żeglugę śródlądową mierzymy (W10);
  - bez dodatków (`spec.md:88`);
  - 6 korzeni T2 (`spec.md:85`); w 4.5 istnieją z tymi nazwami: `statek 1`, `okręt 1`, `łódź 2`, `marynarz 1*`, `żegluga 1*`, `żeglarstwo 1*`;
  - lista 37 słów bez zmian (liczba sprawdzona: 37);
  - wydanie dopiero po bramce.

  Automatyczny werdykt „dalej / popraw” plus „stop” operatora zgadza się z `scope-clarifications.md`.
- **#11:** każdy punkt listy kontrolnej ma wymaganie (W1, W5–W15, W13).
- **Kod:**
  - funkcje istnieją: `pop00.read_words` (107), `package_file` (137), `check_inputs` (145), `confirm_unchanged` (331), `build_package` (337); `pop.load_forms` (287), `load_constructions` (315), `_label` (1762), `_write_gzip` (1767); `inputs.checked_file` (27); `run.code_identity` (16); `export.rename_noreplace` (33); `record_review.py` istnieje;
  - wiersze z `cli.py:51–55, 97–99, 147` są poprawne;
  - `quality._config` wymusza 30 (`quality.py:24`), więc potrzebna jest zmiana z W4;
  - `units.json` ma `members_in` z kluczami `POP` i `POP0`.
- **Hashe:**
  - pop-v3: `4acb7014…1d58`;
  - POP00 r2-a: `3db703ef…2dbbf`, stan BUILT, wejścia zgodne z pop-v3, bazą i STANDARD;
  - STANDARD: `dab4f3bc…fa7d`;
  - zip Słowosieci: `30edc5f8…dcbc`, 465 563 957 B (to samo zwraca HEAD na URL z W1);
  - przebieg: FROZEN.
- **Kwalifikatory:** `qualifiers.json` ma etykietę `daw.|żegl.`, więc podział po `|`, potem po `,` jest potrzebny. `pop.load_lexemes` dzieli kwalifikatory tylko po `,`.
- **BROAD przechodzi `read_words`:** 3 479 018 słów, 0 odrzuconych.
- **Zrzut Słowosieci ma tabele `iplog`, `iplimit` i `tracker_*`.** Lista dozwolonych tabel z W2 je pomija.

---

## Krytyczne

### K1. IATE 2019 nie ma typu terminu `term`
- **Spec:** `spec.md:86` (filtr `typ: term`), `spec.md:101`.
- **Dowód:** w próbce TBX (`IATE_export_26022019.tbx`, 1,86 GB po rozpakowaniu) `termNote type="termType"` ma wartości `fullForm` 18 598, `abbreviation` 523, `shortForm` 37 i `phraseologicalUnit` 5. Wartości `term` nie ma ani razu. Polskie hasła mają typ `fullForm`. Słowo „term” pochodzi z filtra obecnej strony IATE (badanie, `wide-zewnetrzne-zrodla.md:35`), a nie z pliku 2019.
- **Skutek:** T3 jest pusta, próg T3 niespełnialny, W10 bez danych.
- **Poprawka:** w `morze.json` wpisać `typ: fullForm`. W ADR-011 zapisać, że „term” z projektu odpowiada `fullForm`. Fikstura TBX ma używać prawdziwych wartości. Rozważyć też odrzucenie terminów z `administrativeStatus = deprecatedTerm-admn-sts`: w próbce jest ich 8.

## Ważne

### W1. Prawdziwy TBX ma DOCTYPE, a spec każe go odrzucić
- **Spec:** `spec.md:24,186,202` („DTD i encje = błąd”, test „DTD w TBX”).
- **Dowód:** drugi wiersz pliku to `<!DOCTYPE martif SYSTEM "TBXcoreStructV02.dtd">`.
- **Poprawka:** dopuścić DOCTYPE bez podzbioru wewnętrznego. Odrzucać `<!ENTITY` i każdy podzbiór wewnętrzny. Zewnętrznego DTD nie pobierać. Test ma sprawdzać encję, nie samo DOCTYPE.

### W2. Brak reguły dopasowania kodu dziedziny
- **Spec:** `spec.md:86,101`.
- **Dowód:** `subjectField` to lista kodów rozdzielona `, ` (`1011, 2011`; `20, 2036, 48`). Są w niej kody 2-cyfrowe (`48`) i 4-cyfrowe (`4821`).
- **Poprawka:** dzielić po `,`, przycinać spacje i porównywać cały kod. Hasła z samym `48` nie wchodzą. Zapisać to w ADR-011.

### W3. Zakres domknięcia T2 jest niejednoznaczny
- **Spec:** `spec.md:100` („domknięcie … po relacjach 11, 25, 27”). `high-level-design.md` mówi: „domknięcie hiponimii; części i miejsca z ich hiponimami”.
- **Dowód:** pomiar na `plwn45.sqlite` (`valid=1`, pos 1–4, jedno słowo): pełne domknięcie daje 1 092 synsety i 874 lematy, ograniczone 715 synsetów i 504 lematy. Przykłady z obu stron są w sekcji „Otwarte pytania”.
- **Poprawka:** przed budową zapytać operatora i pokazać mu te przykłady. Decyzję zapisać w ADR-010 i w `morze.json`, np. jako pole `t2.tryb`.

### W4. Kody części mowy Słowosieci nie są przypięte
- **Spec:** `spec.md:78` mapuje nazwy („rzeczownik → subst”), a nie kody.
- **Dowód:** `lexicalunit.pos` ma wartości 1–8. Wartości 5–8 to jednostki angielskie: 218 597 wierszy.
- **Skutek:** angielskie lematy, np. `port`, mogą trafić na `lemma_base` i fałszywie ustawić `wieloznaczny = tak`.
- **Poprawka:** w `czesci_mowy` użyć kodów: 2 → `subst`, `depr`; 1 → `inf`; 4 → `adj`; 3 → `adv`. Kody 5–8 pomijać wszędzie, także w regule `wieloznaczny`. Znaczenie kodów potwierdzić na danych i zapisać w ADR-011.

### W5. T3 nie ma części mowy, a rzeczowniki odczasownikowe nie mają leksemu
- **Spec:** `spec.md:101` (T3 mapuje tylko przez `lemma_base`), `spec.md:100`.
- **Dowód:** IATE nie podaje części mowy. W `build.sqlite` nie ma leksemu z `lemma_base` `żeglowanie` ani `cumowanie` (ger należą do leksemu czasownika). `pływanie` jest jako `subst`.
- **Poprawka:**
  - ustalić, że T3 bierze tylko leksemy klasy `subst` i `depr`, albo jawnie wszystkie;
  - zapisać, że rzeczowniki odczasownikowe ze Słowosieci trafiają do `BRAK_LEKSEMU`, i podać ich liczbę w raporcie;
  - zdefiniować „jedno słowo” i „małe litery polskie”: alfabet, łącznik, apostrof.

### W6. Brak reguły dla małej warstwy
- **Spec:** `spec.md:75–76,132` (150 i 90 pozycji, progi „x/30”).
- **Ryzyko:** T3 po odjęciu T1 i T2 oraz po ∩ STANDARD może mieć mniej niż 50, a nawet mniej niż 30 leksemów. Jednowyrazowe hasła to 7–21% z ≥1155 haseł PL.
- **Poprawka:** gdy populacja jest mniejsza niż rozmiar próby, bierzemy całą warstwę. Progi zapisać jako udziały: 90%, 66,7%, „nie” ≤ 10%. Checker podaje rzeczywiste N.

### W7. Nie wiadomo, który wynik testu 37 słów idzie do progu
- **Spec:** `spec.md:76` (≥ 70%) wobec `spec.md:121` (trzy wyniki).
- **Poprawka:** do progu idzie wynik dla całości (podstawa w projekcie: „SGJP ∪ C 78%”). T1 oraz T1 ∪ T2 są tylko diagnostyką. Zapisać to w `progi` i w checkerze.

### W8. Brak definicji zgodności i kappy przy „niepewne”
- **Spec:** `spec.md:76,137`.
- **Poprawka:** zgodność to odsetek identycznych ocen (3 kategorie) na 90 wspólnych pozycjach. Kappa Cohena też liczy 3 kategorie. W progach trafności „niepewne” nie liczy się jako „tak”.

### W9. `ATTRIBUTIONS.md` pakietu bez SGJP
- **Spec:** `spec.md:141` wymienia tylko plWordNet i IATE.
- **Dowód:** pakiet publikuje formy SGJP (BSD-2 wymaga zawiadomienia). POP00 dokleja atrybucje POP przez `package_file` (`pop00.py:164,303`).
- **Poprawka:** `ATTRIBUTIONS.md` pakietu ma mieć sekcję SGJP z pakietu POP albo z pliku w `tematy-teksty/`, a do tego plWordNet i IATE.

## Drobne

- **D1. `_write_gzip` używa też test.** `tests/test_pop.py:1352` podmienia `pop_module._write_gzip`, a `spec.md:162` go nie wymienia. Alias nie pomoże, bo mock nie trafi w nową nazwę. Test trzeba poprawić. Zmiana komunikatu w `read_words` jest bezpieczna: żaden test go nie sprawdza (grep; checker ma własny komunikat, `check_pop00_package.py:63`).
- **D2. Klucze `sampling`.** `quality._config` wymaga dokładnie `{version, seed, size_per_stratum, encoding}` (`quality.py:19`). `spec.md:75` stawia obok `operator_per_stratum` i pomija `encoding`. `operator_per_stratum` przenieść na górny poziom, `encoding` dopisać.
- **D3. Kolumny `valid`, `status` i `isabstract`.** `synsetrelation.valid` ma 2 wiersze z 0, `lexicalunit.status` ma wartości 0–5, a `synset.isabstract` ma 1 118 synsetów sztucznych. `spec.md:53–60` tego nie rozstrzyga. Proponuję filtrować `valid=1` już w pochodnej. O `status` i `isabstract` zdecydować w ADR-011 (np. przechodzić przez synset sztuczny, ale nie brać z niego lematów).
- **D4. Kontrola nazwy korzenia.** `unitsstr` ma postać `(statek 1 (wytw) [wytw] | statek wodny 1* (wytw))`, a gwiazdka (`marynarz 1*`) jest częścią napisu. Nazwę porównywać jako `lemma + ' ' + variant` jednostki o najniższym `unitindex`, nie przez `unitsstr`.
- **D5. BROAD niezwiązany z przebiegiem.** Manifest przebiegu nie zawiera hasha `broad.txt` (`4f1aace9…1271`). Hash jest w `release-LL-PL-v30/release-manifest.json`, a ten jest związany przez `export.release_manifest_sha256`. Ten manifest przypiąć i sprawdzić na nim BROAD i STANDARD.
- **D6. Parser zrzutu MySQL.** Zrzut ma wielowierszowe `INSERT` i znaki ucieczki (`\'`). Potrzebny test z ucieczkami i kontrola liczności względem starej pochodnej: 1 491 277 relacji i 514 016 jednostek.
- **D7. Czy budowa hashuje zip?** `spec.md:69` przypina `plwordnet_zip` ze ścieżką. Trzeba napisać, czy budowa hashuje zip (465 MB), czy tylko porównuje `meta` z pinem.
- **D8. Pochodzenie źródeł.** Ponowne pobieranie Słowosieci odbiega od `clarifications.md` („przenosimy”). Jest dopuszczalne, ale odstępstwo trzeba zapisać w ADR-011. Dla IATE zapisać też `Last-Modified` (30.09.2019) i nazwę pliku z zipa.
- **D9. Stan REVIEWED.** ADR-008 i projekt mówią o stanach BUILT i REVIEWED oraz przeglądzie w pakiecie. Spec ma tylko BUILT i przegląd poza pakietem (`spec.md:189`). Odstępstwo zapisać w ADR-010.
- **D10. Znaczniki śródlądowe.** Lista (`spec.md:87`) nie ma treści. Ustalić ją przed pierwszą budową, nie po wynikach, i wypisać w `LIMITATIONS.md`. Napisać, czy mierzymy kandydatów T3, czy wpisy T3 po ∩ STANDARD.
- **D11. Miejsce listy 37 słów.** Lista leży w `tematy.json` (metoda), więc następny temat wymusi nową wersję metody. Lepiej trzymać ją w pliku tematu, jako pole diagnostyczne.
- **D12. Kolejność ocen.** Hash ocen agenta trzeba zapisać, zanim operator dostanie stronę. Wtedy oceny agenta nie mogą się dopasować do ocen operatora.
- **D13. Wiki.** Runbook wymaga tabeli źródeł na `Home` przy nowym źródle, a `spec.md:147` jej nie ma. Bez `explain` przykłady na wiki sprawdzamy w `MORZE.tsv.gz`, co trzeba zapisać w sekcji TEMATY runbooka.
- **D14. Strona R2 na iPhonie.** Operator gra na iPhonie. Spec (`spec.md:130`) nie mówi, jak otworzy stronę i jak odda JSON. Podać kanał (np. artefakt z przyciskiem „kopiuj JSON”) i sprawdzić go na telefonie.
- **D15. Koszt BROAD.** `pop.load_forms(db, broad)` to trzeci pełny skan `interpretation` i duży słownik w pamięci. Formy wystarczy czytać dla leksemów kandydatów, porcjami po `lexeme_id`, jak w `pop00.read_analyses`.
- **D16. Kierunek relacji da się zamknąć już teraz** (`spec.md:23`). W starej pochodnej `PARENT_ID → CHILD_ID` daje dla 11: `statek` → `łódź 2`, `okręt 1`, `łajba`; dla 25: `pokład 3`, `kadłub 3`; dla 27: `kambuz`, `messa/mesa`, `ładownia`. Nazwy relacji: 11 „hiperonimia”, 25 „część”, 27 „miejsce” (zgodne z W2). Na nowej pochodnej wystarczy to potwierdzić jednym testem.

## Rekomendacje (kolejność)
1. Poprawić K1, W1 i W2 w W5, W7 i w podejściu technicznym. Fiksturę TBX oprzeć na prawdziwych polach.
2. Zadać operatorowi pytanie W3 z przykładami.
3. Uzupełnić W4–W9 i D2 w `tematy.json`, `morze.json` i W12.
4. Drobne zapisać w ADR-010 i ADR-011 przy ich pisaniu.
