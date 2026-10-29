# Audyt specyfikacji: TEMATY, pierwsza fala (#12)

## TL;DR
Werdykt: **pass-with-concerns**. Specyfikację da się wdrożyć. Przed planem trzeba poprawić kilka miejsc, ale żadne nie jest krytyczne.
Liczba uwag: **0 krytycznych, 5 ważnych, 9 drobnych**.
Dane z W11 się zgadzają. Wszystkie 39 nazw synsetów, 9 liczb lematów T2, pomiary wycięć i 22 atomy SGJP policzyłem od nowa. Hashe i liczby z W8 też są zgodne.
Regresja bajtowa morza (W8) jest osiągalna. TXT i TSV nie zależą od nazwy metody, a losowanie nie zależy od `tematy-v2`.
Najważniejsze uwagi:
- przepięcie ocen morza (W9) pomija `evidence_sha256`, więc checker odrzuci plik;
- skrypt słów oczywistych (W10) sprawdza formę w STANDARD, a test sprawdza lemat;
- zgoda operatora na skład list nie ma swojego kroku w kolejności prac.

## Kluczowe decyzje
- **Brak uwagi krytycznej.** Każdy błąd poniżej wyjdzie przy pierwszym przebiegu (kod 4 albo czerwony test) i da się go naprawić w miejscu. Żaden nie psuje danych.
- **W9 i W10 oceniam jako ważne.** Wykonane dosłownie, W9 kończy się odmową checkera. W10 daje słowo, którego test nigdy nie zaliczy, a listy nie wolno potem zmienić.
- **Zgodę na skład list oceniam jako ważną (AGENTS.md).** Część decyzji operator już podjął (`scope-clarifications.md`: części ciała z rel. 25, organy roślin). Atomy `ogr.`, `psych.`, `wet.`, `farm.` i brak korzeni gier w T2 sportu nadal na nią czekają.
- **Bump do `tematy-v2` uznaję za poprawny.** To decyzja techniczna, a w specyfikacji jest uzasadniona. Seed losowania się nie zmienia (`quality.py:13-17`, `sample_strata` czyta tylko `sampling`).
- **Bazę `build.sqlite` czytałem tylko do odczytu.** Atomy policzyłem jednym zapytaniem `DISTINCT lexeme_id, qualifiers` (5 s). TBX IATE nie skanowałem.

## Otwarte pytania i ryzyka
- **`t1_tak` z ocen agenta to słaba bramka.** Dla morza agent dał T1 46/50 = 0,92, tuż nad progiem 0,90. Jego zgodność z operatorem na T2 i T3 wynosi 20/57, kappa 0. Operator zdecydował, że T1 ocenia tylko agent, więc to ryzyko, a nie błąd specyfikacji.
- **Wspólny seed dla wszystkich tematów.** Wspólny lemat ma w tej samej warstwie tę samą rangę w każdym temacie. Przez to próby tematów się korelują. To nie błąd, ale warto o tym wiedzieć przy macierzy nakładania.
- **„T3 jest mała” w medycynie** nie jest zmierzone (D7).

## Sprawdzone i zgodne
- **Nazwy w W11.** Sprawdziłem 39 synsetów (korzenie i wykluczenia) na `plwn45-tematy.sqlite` zapytaniem `_root_name`. Wszystkie nazwy się zgadzają, np. `441043 część ciała 1`, `27813 zarodnia 1`, `427828 sprzęt sportowy 1`, `4984 figura geometryczna 2`.
- **Lematy T2.** Liczyłem domknięcie jak `t2_candidates`: kody 1–4, `jedno_slowo`, bez synsetów sztucznych. Wyniki:

  | zwierzęta | rośliny | medycyna | muzyka | kuchnia | sport | matematyka | pogoda | grzyby |
  |---|---|---|---|---|---|---|---|---|
  | 4452 | 3111 | 4063 | 1148 | 2432 | 757 | 543 | 209 | 351 |

  Wszystkie są równe tabeli W11.
- **Wycięcia:**
  - zwierzęta: 4727 lematów po relacjach 11, 25, 27, a 4452 po 11, 27 (tyle samo po samej 11);
  - relacja 25 ma 269 celów, żaden nie leży w domknięciu po 11, 27;
  - odpada 275 lematów, w tym `dziób`, `kieł`, `jelito`, `guzik`, `poroże`, `wymię`;
  - medycyna: 4477 → 4063, odpadają `batat`, `bazylia`, `cytryna`, `groch`, `kawa`, `sporangium`;
  - `24994` jest w domknięciu medycyny, a w domknięciu grzybów go nie ma;
  - każde wykluczenie poddrzewa jest osiągalne z korzeni, więc nowa reguła z W1 nie da kodu 4.
- **Atomy SGJP** (leksemy, `build.sqlite`): `zool.` 665, `zootechn.` 16, `hip.` 4, `paleont.` 28, `bot.` 407, `ogr.` 21, `med.` 195, `anat.` 69, `psych.` 24, `wet.` 5, `farm.` 6, `muz.` 172, `chor.` 76, `kulin.` 162, `spoż.` 4, `sport.` 123, `gry` 16, `szach.` 5, `karc.` 44, `mat.` 62, `meteor.` 56, `mikol.` 54. Każdy istnieje jako cały atom.
- **W8:**
  - `SHA256SUMS` pakietu `tematy-v2-20261029-a`: `MORZE.txt.gz` 6e78d1ef…, `MORZE.tsv.gz` 83037db1…, `ATTRIBUTIONS.md` a3a221e9…, `TERMS.md` b4250289…;
  - liczby: 970 wpisów, 11 035 form, warstwy T1 246, T2 691, T3 27, D 6;
  - od `a633136` (kod, z którego zbudowano pakiet) nie ma żadnego commitu w `literaki_slownik/`, `scripts/`, `config/` ani `tests/`.
- **Numery wierszy** w tabeli „Istniejący kod” zgadzają się co do wiersza: `tematy.py`, checker i `tematy_review.py`.
- **Próba.** Operator dostaje pierwsze 30 z 50 pozycji agenta (`tematy.py:977-979`), więc jego próba jest podzbiorem próby agenta. Pusta T3 daje `EMPTY_NOT_COVERAGE` (`quality.py:76`). `operator_per_stratum` 30 ≤ 50.
- **Kody wyjścia** są spójne z obecnymi: 2 to konfiguracja (`_bad`), 4 to dane. Wykluczenie bez trafienia i wykluczenie poddrzewa nieosiągalne z korzeni dają kod 4.
- **AGENTS.md.** Specyfikacja jest po polsku i zwięzła. Z gier wymienia tylko atomy SGJP `gry`, `szach.`, `karc.`; innej gry słownej nie ma.

## Uwagi

### Ważne (W)

**W1. W9: przepięcie pomija `evidence_sha256`. Checker odrzuci plik przeglądu.**
- Spec: „Wiązanie z nowym pakietem: `SHA256SUMS` i `sample_sha256`” (W9).
- Kod: `binding` porównuje z szablonem cztery pola: `sample_sha256`, `canonical_index_sha256`, `evidence_sha256`, `version` (`check_tematy_package.py:374-376`). `evidence_sha256` zawiera hash `reports/summary.json` (`tematy.py:1014`). `summary.json` zawiera `method` (`tematy.py:846`), które zmienia się na `tematy-v2`. W8 też podaje, że `summary.json` się różni.
- Skutek: plik przepięty według W9 dostaje kod 4 („Przegląd niepowiązany z próbą: evidence_sha256”).
- Poprawka: przepięcie kopiuje z nowego `review-template.json` `sample_sha256`, `canonical_index_sha256` i `evidence_sha256`, a z `SHA256SUMS` jego hash. Ustawia też `method: tematy-v2`. Do W9 dopisać wynik oczekiwany (D4).

**W2. W10: skrypt sprawdza formę w STANDARD, a test liczy lematy.**
- Spec: „Każde słowo musi mieć formę w STANDARD” (W10.2).
- Kod: słowo jest pokryte, gdy jest równe `lemat` wpisu, czyli `lemma_base` (`tematy.py:796-802`, checker `obvious_words` 227-232).
- Skutek: słowo, które jest formą, ale nie lematem (np. `nuty`, `zawody`), przejdzie skrypt i nigdy nie zostanie pokryte. Listy po commicie nie wolno już zmienić.
- Poprawka: skrypt wymaga, by słowo było `lemma_base` leksemu SGJP z klasą z `czesci_mowy` (`inf`, `subst`, `depr`, `adv`, `adj`) i miało formę w STANDARD. Wzór to `map_lemmas` (`tematy.py:552`).

**W3. Zgoda operatora na skład list nie ma kroku w kolejności prac.**
- Spec: „Do akceptacji operatora przy specyfikacji: atomy `ogr.`, `psych.`, `wet.`, `farm.`; relacje zwierząt `[11, 27]`; pięć poddrzew medycyny”. Kolejność prac (kroki 1–8) nie ma jednak bramki przed krokiem 4.
- `codebase-analysis.md` (tabela atomów) oznacza te atomy jako „do decyzji”. Operator zgodził się wcześniej tylko na wycięcie części ciała z rel. 25 i organów roślin (`scope-clarifications.md`).
- Sport: operator przypisał gry, szachy i karty do sportu (`clarifications.md`). Spec daje im tylko T1, a korzenie T2 dla gier sama wpisuje w „Poza zakresem”. To też jest decyzja o składzie listy.
- Poprawka: dodać krok „0. Zgoda operatora” przed krokiem 4: atomy, relacje zwierząt, poddrzewa medycyny, korzenie gier w sporcie (tak albo nie). Wynik zapisać w `scope-clarifications.md`.

**W4. Test z W8 jest sprzeczny z W4, a sposób zdejmowania znaczników nie jest określony.**
- W8: „temat z T3 i znacznikami daje teksty z odcinkami zdjętymi bajtowo równe obecnym”. W4 zmienia jednak punkt T2 w `LIMITATIONS.md`, więc ten plik nie może być równy obecnemu.
- Spec nie mówi, co dzieje się ze znakiem nowej linii przy znaczniku na osobnym wierszu. Nie mówi też, gdzie leży spacja przy znaczniku w środku akapitu. W `TERMS.md` zdanie o IATE stoi w środku akapitu (`TERMS.md:3`).
- Poprawka:
  - reguła zdejmowania: dla zachowanego odcinka usuwamy dokładnie bajty znaczników; dla usuniętego odcinka usuwamy bajty od `<!--X-->` do `<!--/X-->` włącznie;
  - znaczniki stawiamy tak, żeby oba warianty dawały poprawny tekst (np. spacja wewnątrz odcinka w `TERMS.md`);
  - test przypina stare hashe `ATTRIBUTIONS-tematy.md` (`d6673156…`) i `TERMS.md` (`b4250289…`);
  - `LIMITATIONS.md` porównujemy ze starym tekstem z podmienionym tylko punktem T2.

**W5. Szacunek czasu i pracy jest za niski.**
- Spec liczy „20 budów i 20 przebiegów checkera”. Dochodzi do tego 10 przebiegów `--review` (W13.5, w tym morze). Każdy z nich także dwa razy haszuje 22 GB (`check_tematy_package.py:307, 357`).
- Ocen agenta jest ok. 950: 9 tematów × (T1 do 50 + T2 50) + T3 medycyny 50. Spec ich nie wycenia.
- Poprawka: liczyć ≥ 30 przebiegów checkera i dopisać czas ocen agenta.

### Drobne (D)

**D1. Commit między budową a i b psuje a = b.** `code_identity` zapisuje `git_commit` = HEAD (`run.py:30`), a ta wartość trafia do manifestu i `SHA256SUMS`. Commit `verification/builds.json` (zasada „commit po zapisie w .maister”) między a i b da różne pakiety. Poprawka: w W12 zapisać, że między budowami a i b tematu nie robimy commitu. Najlepiej commitować dopiero po wszystkich budowach.

**D2. `srodladowe` dla tematu z T3, ale bez znaczników (medycyna), nie jest określone.** W4 mówi tylko o temacie „bez t3”. `_inland` wymaga znaczników (`tematy.py:824`). Poprawka: `srodladowe` = `null` zawsze, gdy brak `znaczniki_srodladowe`. To samo dla wiersza TL;DR raportu (`tematy.py:890`).

**D3. Kiedy liczyć `t1_tak` z ocen agenta?** Bez ocen operatora checker daje dziś „czeka” wszystkim progom (`check_tematy_package.py:475`). Spec nie mówi, czy `t1_tak` z ocen agenta liczymy już przed oceną operatora. Poprawka: dopisać regułę, np. progi z ocen agenta liczymy zawsze.

**D4. Brak oczekiwanego werdyktu morza po W6.** Policzyłem z `tematy-morze-v2-review.json`:
- `t1_tak` (agent) 23/25, spełniony;
- `t2_tak` i `t3_tak` (operator) 1;
- zgodność 20/57 (N = 57), kappa 0;
- wynik: „popraw”.

Poprawka: wpisać to do W9 jako wynik testu.

**D5. W15 pomija dwie strony wiki.** Runbook każe przy gotowym pakiecie aktualizować TEMATY, Home, STANDARD, `_Sidebar` i historię (`docs/runbook-wiki.md:79`). Spec wymienia tylko Slownik-TEMATY, Home i Historia-zmian. Poprawka: dopisać STANDARD i `_Sidebar` albo uzasadnić, czemu nie.

**D6. W7: „`INPUTS` zależą od `t3`” można źle odczytać.** Walidacja manifestu wejść ma dalej wymagać `iate` (W2, `check_tematy_package.py:304`). Od `t3` zależy tylko porównanie pinów (`305-308`). Checker czyta temat dopiero w wierszach 313-316, po pinach, więc kolejność trzeba zmienić. Poprawka: zapisać to wprost.

**D7. Teksty T3 i znaczników są pisane pod morze.** Punkt „T3 jest mała” (`LIMITATIONS.md:7`) zostanie w medycynie. Tam IATE 2841 ma ok. 950 terminów, a wielkości T3 nikt nie zmierzył. Punkt śródlądowy ma na sztywno „4821” i listę znaczników (`LIMITATIONS.md:8`), a W1 dopuszcza znaczniki przy każdym temacie z `t3`. Poprawka: zmierzyć T3 medycyny w pierwszej budowie i w razie potrzeby zmienić zdanie. Znaczniki ograniczyć do morza albo wstawiać listę z pliku tematu.

**D8. Nowy checker odrzuci stare pakiety.** Po zmianie `METHOD` na `tematy-v2` checker nie przyjmie pakietów `tematy-v1-*` ani `tematy-v2-20261029-*`, bo oba mają metodę `tematy-v1`. Poprawka: zapisać w ADR-012, że stare pakiety sprawdza checker z commitu `a633136`.

**D9. Liczby T2 w W11 liczono po małych literach, a budowa liczy z wielkimi literami.** `jedno_slowo` dopuszcza lemat pisany wielką literą (`tematy.py:300`), a klucze `t2.lematy` zachowują wielkość liter. Kuchnia daje 2432 po zmianie na małe litery, a 2434 bez zmiany. Spec mówi „liczby wiążące poda raport budowy”, więc wystarczy przypis.

## Rekomendacje
1. Poprawić W9 (W1) i regułę w skrypcie słów oczywistych (W2), zanim powstanie plan.
2. Dodać krok zgody operatora (W3) i zapisać jego decyzje przed plikami tematów.
3. Określić zdejmowanie znaczników i test regresji tekstów (W4).
4. Dopisać do W12 zakaz commitu między budowami a i b (D1). W9 uzupełnić o oczekiwany werdykt (D4).
5. Pozostałe drobne uwagi poprawić w tekście specyfikacji, bez zmiany zakresu.
