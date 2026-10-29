# Analiza luk — #12 TEMATY, pierwsza fala

**Data**: 2026-10-29. Stan kodu: `45517d8` (grupa 16 #11 jest w drzewie: `2bd0dab`, `a633136`).

## TL;DR
- Dziewięciu tematów nie da się dziś zbudować. Kod wymaga T3 (IATE) i znaczników śródlądowych. Temat bez T3 zawsze dostaje werdykt „popraw”, bo `t3_tak` = `None` (checker ~485).
- Dane na wszystkie 9 tematów są zmierzone. Brakuje uogólnienia kodu (~10–15 miejsc), 9 plików tematów, 9 list słów oczywistych i 9 par budów.
- Najcięższy element to przegląd operatora. Przy zasadach z morza to ok. 570 słów (8 × 60 + 90). Do tego dochodzi problem zgodności agenta: dla morza wyszło 47/87.
- Luka w cyklu danych: przegląd może wskazać złe słowo, ale nie da się go usunąć. Pole `wykluczenia` musi być puste (`tematy.py` ~139), działają tylko wykluczenia poddrzew.

## Kluczowe decyzje
- **Cechy zadania**: zmienia istniejący kod i tworzy nowe byty (9 tematów i pakietów). Operuje na danych. Nie jest to defekt ani zadanie UI (strona R2 jest ogólna i już działa).
- **Decyzje techniczne podjęte przez nas** (do ADR-012, bez pytania operatora):
  - jeden pakiet na temat;
  - T3 opcjonalne;
  - `t3_tak` = „nie dotyczy”, gdy T3 jest puste;
  - znaczniki śródlądowe tylko w morzu;
  - `dodatki` przenosimy z `t3` na górny poziom pliku tematu.
- **Regresja morza**: lista i TSV `morze-v2` mają być identyczne bajt w bajt. Manifest może się różnić tylko haszem pliku tematu, bo `dodatki` zmieniają miejsce.
- **Metoda zostaje `tematy-v1`**: zmienia się schemat pliku tematu, a nie reguły warstw. Zapisujemy to w ADR-012.
- **Ograniczenie w `orchestrator-state.yml` jest nieaktualne.** Zakaz „nie ruszać tematy.py do końca grupy 16” już nie obowiązuje, bo grupa 16 jest zakończona (raport bramki, „Poprawka v2”).

## Otwarte pytania i ryzyka
- Rozmiar przeglądu i próg zgodności decydują o tym, czy ocena wspólna jest wykonalna (pytania K1, K2).
- Szum w zwierzętach (części ciała z relacji 25, guzik, trąba) i w medycynie (organy roślin, biochemia), pytanie W2.
- Małe tematy (pogoda ~230, grzyby ~380, matematyka ~560) mogą nie przejść progu 0,70 słów oczywistych bez warstwy D.
- Wiki: strona `Slownik-TEMATY` i sekcja TEMATY w `docs/runbook-wiki.md` mówią tylko o morzu (`MORZE.tsv.gz`, `counts.morze`). Trzeba je uogólnić w tej samej pracy.

## Podsumowanie
- **Ryzyko**: średnie. Kod jest wspólny z działającym pakietem morza, a granice tematów są subiektywne.
- **Nakład**: średni. Kod umiarkowanie, dane zmierzone. Najwięcej pracy to przegląd: agent ok. 9 × 100–150 pozycji, operator patrz K1.
- **Cechy**: `modifies_existing_code`, `creates_new_entities`, `involves_data_operations`.

## Cechy zadania
- Odtwarzalny defekt: nie. Werdykt bez T3 to ograniczenie kodu, a nie zgłoszony błąd.
- Zmienia istniejący kod: tak.
- Tworzy nowe byty: tak.
- Operacje na danych: tak.
- Głównie UI: nie.

## Luki

### Brakujące
- 9 plików `config/generator/tematy/<id>.json`. Id muszą pasować do `[a-z]+`: `zwierzeta`, `rosliny`, `medycyna`, `muzyka`, `kuchnia`, `sport`, `matematyka`, `pogoda`, `grzyby`.
- 9 list słów oczywistych (~35 słów), ustalonych i zacommitowanych przed pierwszą budową.
- Fikstura testowa tematu bez T3. Testy: werdykt „nie dotyczy”, LIMITATIONS bez znacznika, drugi temat.
- ADR-012 (uogólnienie, granice z `clarifications.md`).
- Wiersze 9 tematów na wiki („W przygotowaniu”).
- Zestawienie lematów wspólnych między tematami fali (decyzja: słowa wspólne zostają w każdym temacie, ale operator powinien je widzieć).

### Niepełne
- `load_topic`, `INPUTS`/`load_sources`/`check_inputs`, `candidates`: T3 i IATE są obowiązkowe. Ma być: opcjonalne.
- `diagnostyka.znaczniki_srodladowe`, `ZNACZNIK`, LIMITATIONS i ATTRIBUTIONS: dziś zawsze o morzu i IATE. Mają być warianty zależne od tematu.
- Checker: `PROBA` = T1, T2, T3 na sztywno (~245) i IATE w INPUTS. Ma się dostosować do warstw tematu.
- Raport i komunikaty: literał „MORZE”, „T1 < T2 < T3”.
- `wykluczenia` (lematy): schemat je zna, ale budowa ich nie czyta i wymaga pustej listy.

### Zmiany zachowania
- Werdykt: `t3_tak` z „niespełnione” na „nie dotyczy” przy pustej populacji T3.
- Wejścia: temat bez T3 nie haszuje ani nie parsuje IATE (szybsza budowa).

## Ścieżka operatora (ocena ~9 tematów)

| Wymiar | Teraz (morze) | Po (fala) | Ocena |
|---|---|---|---|
| Dotarcie | 1 artefakt R2, iPhone, „kopiuj JSON” | 9 artefaktów, 9 wklejeń JSON | ⚠️ łatwo pominąć temat |
| Odkrywalność | 9/10 (link w rozmowie) | 7/10 (9 linków) | −2 |
| Nakład | 87 słów | ~570 przy 30/warstwę | ❌ bez zmiany zasad |
| Spójność ocen | agent wąsko, operator szeroko | to samo ryzyko × 9 | ⚠️ (K2) |

Przy obecnych zasadach operator dostaje:
- 9 stron R2;
- 9 list słów oczywistych do wglądu;
- 9 raportów przecięć z POP/POP00;
- zestawienie lematów wspólnych.

Proponujemy jedną stronę zbiorczą z linkami do 9 stron R2 i stanem „ocenione / nie” (W5).

## Cykl danych

### Byt: pakiet tematu (`tematy-v1-YYYYMMDD-<id>-{a,b}`)

| Operacja | Backend | Wynik | Dostęp | Stan |
|---|---|---|---|---|
| CREATE | `cli --topic <id>` → `build_package` | pakiet, raport, LIMITATIONS | CLI | ⚠️ tylko z T3 |
| READ | `summary.json`, `raport.md`, checker | strona R2, wiki | artefakt, wiki | ⚠️ wiki tylko o morzu |
| UPDATE | nowa wersja tematu (`<id>-v<n>`) | poddrzewa i dodatki D działają | edycja JSON | ❌ brak usuwania lematów (`wykluczenia` puste) |
| DELETE | nie dotyczy (nowy katalog na budowę) | — | — | ✅ |

### Byt: ocena przeglądu

| Operacja | Backend | Wynik | Dostęp | Stan |
|---|---|---|---|---|
| CREATE (agent) | `tematy_review.agent_review` | plik przeglądu | skrypt zadania | ✅ |
| CREATE (operator) | `tematy_review.record` | JSON ze strony R2 | artefakt iPhone | ✅ |
| READ | checker `--review` | werdykt | raport bramki | ❌ bez T3 zawsze „popraw” |

**Kompletność: 75%.**
- Osierocone: UPDATE treści. Ocena wskazuje złe słowo, a konfiguracja nie umie go usunąć.
- Brakujące punkty styku: wiki dla 9 tematów, zestawienie lematów wspólnych.

## Decyzje dla operatora

### Krytyczne

**K1. Ile słów ocenia operator?** Przy 30 na warstwę wychodzi ~570: 8 tematów × (T1 + T2) + medycyna z T3.
- A: 30 na warstwę, jak w morzu (~570).
- B: 15 na warstwę (~285).
- C: operator ocenia tylko T2 (oraz T3 w medycynie) po 30, czyli ~300. T1 ocenia tylko agent, bo etykiety SGJP mają trafność 29–30/30 (badanie) i 30/30 (morze).
- **Rekomendacja: C.** Szum siedzi w T2. T1 jest trzy razy zmierzone jako trafne.

**K2. Zgodność agent–operator.** W morzu wyszło 47/87, bo agent oceniał wąsko.
- A: agent dostaje szerokie granice z `clarifications.md` jako instrukcję. Próg 0,80 zostaje.
- B: jak A, ale zgodność tylko raportujemy, bez progu w tej fali.
- C: bez oceny agenta.
- **Rekomendacja: A.** Przyczyną była instrukcja, a nie metoda. Próg nadal mierzy, czy agent może później odciążyć operatora.

**K3. Usuwanie pojedynczych słów po ocenie** (osierocone UPDATE).
- A: włączyć `wykluczenia` lematów już teraz. To mała zmiana kodu, a ADR-007 to przewiduje.
- B: tylko wykluczenia poddrzew.
- C: odłożyć do v2 po ocenie wspólnej.
- **Rekomendacja: A.** Ocena wspólna da listę słów do usunięcia, a v2 pójdzie wtedy bez nowego kodu.

### Ważne

**W1. Progi jak dla morza?** Słowa oczywiste ≥ 0,70; T1 ≥ 0,90; T2 ≥ 2/3, „nie” ≤ 0,10; T3 ≥ 2/3.
- A: tak, wspólne.
- B: osobne dla małych tematów.
- **Domyślnie: A.** Jedna metoda daje porównywalne wyniki.

**W2. Szum w zwierzętach i medycynie.**
- A: dodatkowe wykluczenia poddrzew przed budową:
  - zwierzęta: oprócz koniecznego `6047 człowiek 1` także `78303 hominid 1` i poddrzewa części ciała z relacji 25;
  - medycyna: organy roślin pod `2180 organ 3` i `5999 tkanka 1`.
- B: przyjąć szum i zmierzyć go w R2.
- **Domyślnie: A** dla szumu zmierzonego w analizie. Resztę ocenia R2.

**W3. Słowa oczywiste.**
- A: agent pisze ~35 słów na temat bez patrzenia na wynik i robi commit przed budową. Operator przegląda listy jednym rzutem oka (~315 słów) i może je zawetować.
- B: bez wglądu operatora.
- C: 20 słów na temat.
- **Domyślnie: A.** Po budowie listy nie wolno już zmieniać.

**W4. IATE (2841) w medycynie?** 950 terminów PL, 247 wspólnych z T2, dużo farmakologii i chemii.
- A: tak.
- B: bez T3 we wszystkich tematach.
- **Domyślnie: A.** To jedyna dziedzina IATE, która pasuje. Kosztuje 30 słów oceny.

**W5. Strona R2.**
- A: 9 stron i strona zbiorcza z linkami i stanem oceny.
- B: same strony tematów.
- **Domyślnie: A.**

**W6. Warstwa D w pierwszej wersji tematów.**
- A: v1 bez D. Brakujące słowa oczywiste dopisujemy w v2 po ocenie wspólnej, tak jak w morzu.
- B: D od razu.
- **Domyślnie: A.** D zbudowane z brakujących słów oczywistych czyni test pustym.

## Rekomendacje
1. Najpierw kod: T3 opcjonalne, `dodatki` na górnym poziomie, „nie dotyczy”, teksty warunkowe, `wykluczenia` lematów (K3). Test regresji morza.
2. Potem tematy od małych: grzyby, pogoda, matematyka; dalej muzyka, sport, kuchnia; na końcu rośliny, zwierzęta, medycyna.
3. Raport fali: lematy wspólne, przecięcia z POP/POP00, słowa oczywiste dla każdego tematu.
4. Wiki i `docs/runbook-wiki.md` uogólnić w tej samej pracy.

## Ryzyka
- **Złożoność**: średnia, ~8 plików kodu i dokumentów, 9 plików JSON.
- **Integracja**: checker, `tematy_review.py` i 9 plików testów zakładają T3.
- **Regresja**: pakiet `morze-v2` (970 wpisów, 37/37). Pilnuje go test bajt w bajt.
