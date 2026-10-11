# Audyt specyfikacji: POP i POP0 (#3)

## TL;DR
- Werdykt: **pass-with-concerns**. Krytycznych 0, poważnych 6, drobnych 14.
- Piny, stan FROZEN i wydajność odczytu sprawdzone na danych: wszystko się zgadza, `pop` w ≤ 10 min jest realne.
- Przed etapem A poprawić 3 sprawy: listę opcji D3, D5 i D8. Bez nich raport nie pokaże opcji, które trzymają `rok`, `raz`, `dzień` w POP0.
- Przed etapem C poprawić 3 sprawy: próbki (`quality.py` przyjmuje tylko quality-v1), formy z konstrukcji (305 tys. analiz bez `lexeme_id`) i wiązanie przeglądu z wydaniem.

## Key Decisions
- Odroczenie D1–D8 do raportu A uznaję za spójne. Warunek: raport A musi mierzyć pełną listę opcji. Dlatego braki w listach opcji liczę jako poważne, nie drobne.
- Problem homonimów (D5) to poważny, nie krytyczny. To decyzja odłożona, a pomiar ma go ujawnić. Ale spec nie przewiduje jedynej opcji, która go rozwiązuje.
- Hash bazy w każdym `pop` liczę jako drobny. Spec uzasadnia rezygnację fałszywą przesłanką („minuty”), ale D-2 i tak pilnuje bazy.
- Wiki: twierdzenie o „przeciętnym graczu” liczę jako drobne. Etap E i tak przepisuje strony.

## Open Questions / Risks
- Czy grupa homonimów (np. `rok:Sm3~lata` + `rok:Sm3~roki`) może być jednostką rankingu, a POP przyjąć wszystkich jej członków? To nie kopiuje F (F zostaje przy grupie), ale „zna” oba leksemy. Decyzja właściciela.
- Czy forma wchodzi do POP, gdy jest w STANDARD dzięki innemu leksemowi niż wybrany? Spec tego nie mówi.
- POP jako słownik gry z D2 = „formy typowe” stoi w napięciu ze spec v3 §2.2 (pełna odmiana). Spec to notuje, ale nie mówi, kto i kiedy to rozstrzyga.
- Czy przegląd próbek ma trafić do wydania `pop-v1`? Dziś pakiet zawiera tylko szablon UNREVIEWED.

## Co sprawdziłem niezależnie

| sprawdzenie | wynik | dowód |
|---|---|---|
| hash bazy | 85b23ca5…338c, zgodny | sha256 pliku 22 GB, **14 s** |
| hash release-manifest v29 | 54705743…33ee, zgodny | `data/work/release-LL-PL-v29/release-manifest.json` |
| hash `standard.txt` | a432c7c5…d877, zgodny; 3 090 194 wierszy | `lists/standard.txt` |
| hash NKJP | 73af4909…3dc9, zgodny | `cache/nkjp/1grams.gz` |
| stan przebiegu | `readiness: FROZEN`, `export.release_manifest_sha256` = pin | `manifest.json` przebiegu |
| odczyt zbiorczy ro | 7 zapytań (cała `interpretation`, `surface_form`, `evidence_candidate`, `derivation_candidate`, `lexeme`, KWJP lemma-all): **14 s, 350 MB RSS** | sonda w scratchpadzie, `mode=ro` |
| zakresy `evidence_id` | ciągłe per `source_id` (184 917 = 184 917) | sonda |
| „pot.” w SGJP | jest: 62 090 interpretacji, 2 098 leksemów z samym `pot.` | `interpretation.qualifiers` |
| ADR-007 | wolny (jest tylko ADR-006 w `docs/adr/`) | `ls docs/adr` |
| wiki | strony `Slownik-POP`, `Slownik-POP0` „W przygotowaniu”, wiersze w Home i _Sidebar, link z `Slownik-STANDARD` | `~/Projects/Literaki/wiki-literaki-slownik` |

## Ustalenia poważne

### M1. D5: brak opcji „grupa homonimów” — najczęstsze słowa wypadną
- **Spec:** D5 „brak F / flaga / tylko formy jednoznaczne”; C7 zakazuje kopiowania i dzielenia F.
- **Dowód (KWJP lemma-all, AMBIGUOUS, top wg F):**

| lemat | F | kandydaci |
|---|---|---|
| rok | 315 221 | `rok:Sm3~lata`, `rok:Sm3~roki` |
| raz | 124 639 | `raz:Sm3~a~u`, `raz:Sm3~u` |
| dzień | 110 040 | `dzień:Sf`, `dzień:Sm3` |
| oko | 61 242 | `oko:Sn_col`, `oko:Sn_ncol` |
| ktoś | 55 549 | `ktoś:Sm1~ogoś`, `ktoś:Sm1~tosia` |
| stać | 54 396 | `stać:Vi`, `stać:Vp` |

  24 539 leksemów stoi w wierszach AMBIGUOUS; tylko 136 z nich ma też wiersz EXACT. Przy „brak F” `rok` i `dzień` nie mają danych i nie trafią do POP0. „Tylko formy jednoznaczne” też zawodzi: `lata` to także forma `lato`.
- **Druga luka:** „jednoznaczna forma NKJP” nie ma definicji. Jeśli liczyć ją tylko wśród leksemów STANDARD, to `polska` (głównie nazwa własna) da F przymiotnikowi `polski`. To przeniesienie F między homonimami, czyli łamie C7.
- **Poprawka:** dodać do D5 opcję „zbiór kandydatów jako jednostka rankingu; F przy zbiorze; zbiór wchodzi w całości albo wcale” (§8.1: „zachowaj jako niejednoznaczne poświadczenie”). Zdefiniować jednoznaczność formy wobec **wszystkich** leksemów SGJP, łącznie z nazwami własnymi i analizami odrzuconymi. A5 ma pokazać top 50 AMBIGUOUS wg masy dla każdej opcji.

### M2. D3: opcje miary pomijają wymagania §9.4
- **Spec:** D3 „sama KWJP lemma; KWJP + NKJP jako rangi, kilka wag”.
- **Spec v3 §9.4** wymaga rozważenia: częstość i ARF, 1-DP, obecność w gatunkach KWJP, poziom pewności dopasowania. §8.1: nie sumować ARF/1-DP ani całego korpusu z podkorpusami.
- **Dowód:** 10 510 leksemów ma kilka wierszy KWJP lemma (np. czasownik: `fin`, `praet`, `inf`, `ger`). F można zsumować, ARF i 1-DP nie. Spec nie mówi, jak liczyć miarę leksemu z kilku wierszy.
- **Poprawka:** w D3 wymienić miarę KWJP (F, ARF, 1-DP, liczba gatunków) i regułę agregacji wierszy leksemu (np. suma F; ARF/DP tylko dla leksemów z jednym wierszem, inaczej status). Dopisać zakaz §8.1 do C5.

### M3. D8: brak reguły dla braku częściowego
- **Spec:** D8 mierzy tylko leksemy „bez danych w żadnym źródle”.
- **Problem:** kombinacja rang KWJP + NKJP wymaga reguły, gdy jedno źródło ma dane, a drugie nie. To główne miejsce, gdzie „brak ≠ 0” może się złamać. §8.2 wymaga oceny wrażliwości na tę regułę. NKJP nie ma progu publikacji (2 989 804 wierszy z F=1), więc jego brak to co innego niż brak w KWJP (próg 5).
- **Poprawka:** D8 ma mierzyć opcje dla braku częściowego (tylko dostępne źródło / ranga dolna z flagą / wykluczenie) i wrażliwość progów na nie. Osobno statusy dla NKJP i KWJP.

### M4. C9: formy z konstrukcji nie mają `lexeme_id`
- **Spec:** „Leksem ↔ formy: `evidence_candidate.lexeme_id` → `interpretation` → `surface_form.game_key`”.
- **Dowód:** 305 107 kandydatów konstrukcji (`nie-prefix-degree-v1` 179 735, `impt-single-particle-v1` 93 438…) jest w `analysis` przez `candidate_key`, bez `interpretation_id`. Przykłady w STANDARD: `zróbże` (tylko `derivation_candidate`, `lemma_id=zrobić`), `nienajlepszy` (`lemma_id=dobry:A`). Ścieżka ze spec ich nie znajdzie.
- **Druga luka:** spec nie mówi, czy forma wchodzi do POP, gdy jest w STANDARD dzięki analizie innego leksemu (spec v3 §2.2: odrzucona interpretacja nie wraca).
- **Poprawka:** dopisać mapowanie `derivation_candidate.lemma_id` → `lexeme` (z `source_id` ze składnika) i decyzję, czy formy konstrukcji należą do odmiany leksemu (opcja w D2). Ustalić regułę „forma ∈ STANDARD” vs „analiza tego leksemu przyjęta w STANDARD”. Druga wymaga `analysis` (17,5 mln) i `variant_decision` (35 mln) — zmierzyć czas w A.

### M5. A7/C17: `quality.sample_strata` odrzuca każdą konfigurację poza quality-v1
- **Spec:** „`quality.sample_strata` z własną konfiguracją”.
- **Dowód:** `literaki_slownik/quality.py:13-21` wymaga `version == 'quality-v1'`, `seed == 'literaki-slownik-g1-v1'`, inaczej kod 2. `docs/generator/jakosc.md:26`: inna wersja wymaga jawnej zmiany kontraktu.
- **Poprawka:** wybrać jawnie: (a) `_config` przyjmuje też zamkniętą konfigurację `pop-v1` (zmiana `quality.py`, testy quality bez zmian), albo (b) `pop.py` używa `sampling_digest` i własnego doboru. Wpisać wybór do spec i do „Komponentów”. Do tego: `review_template` wymaga `canonical_index_sha256`; spec nie mówi, co go zastąpi w pakiecie POP (np. hash `SHA256SUMS`).

### M6. Przegląd próbek nie jest związany z wydaniem
- **Spec:** `pop` pisze od razu zamrożony pakiet (0444) z „szablonem przeglądu”. Odbiór D-4 dzieje się później. Brak `verify` dla POP.
- **Problem:** wydanie `pop-v1` będzie zawierać tylko szablon UNREVIEWED. Wypełniony i zatwierdzony przegląd nie trafia do pakietu, a żaden kod nie sprawdza jego hashy (w LL-PL robi to `verify.py:291-356`). `release-manifest` nie ma statusu odbioru.
- **Poprawka:** dodać do E1 osobny asset `pop-v1-review.json` z hashem `SHA256SUMS` pakietu i `sample_sha256`. D-3/D-5 mają sprawdzać te hashe skryptem. Nazwać status w `release-manifest` POP (np. `BUILT`, nie `FROZEN`) albo opisać, czemu FROZEN przed odbiorem.

## Ustalenia drobne

| # | ustalenie | dowód | poprawka |
|---|---|---|---|
| m1 | C2: „run-dir musi mieć release-manifest” jest fałszem. Run-dir ma `manifest.json` z `export.release_manifest_sha256` i ścieżką bezwzględną; plik leży w `data/work/release-LL-PL-v29/`. | `ls` przebiegu | dodać `--release-dir` albo pin ścieżki w `pop-sources.json`; sprawdzać oba hashe |
| m2 | Hash bazy trwa 14 s, nie „minuty”. Bez niego manifest `pop` deklaruje hash bazy bez pomiaru. | pomiar | liczyć hash bazy w każdym `pop` (przed i po) |
| m3 | „Klucz leksemu” w C5 bez definicji; `lexeme.id` to liczba z importu. Są 2 źródła leksemów (`sgjp-20260823`, `sgjp-supplement-v1`). | `source_artifact` | klucz = `(source_id, lemma_id)` |
| m4 | C3: progi D6 to liczby, nie „zamknięta lista”. Kod wyjścia dla przebiegu nie-FROZEN nieokreślony. | spec C1–C3 | typy i zakresy pól liczbowych; nie-FROZEN → kod 5 |
| m5 | `explain` bierze `VARIANTS` z `decisions.py` (broad/standard, też CHECK w `variant_decision`). Dodanie `pop` tam zepsuje `aggregate`. | `explain.py:8,134`, `cli.py` | osobna ścieżka `explain_pop`; rozszerzyć `choices` w CLI |
| m6 | Gzip: Python zapisuje nazwę pliku w nagłówku; poziom kompresji nieokreślony. | C11 | `GzipFile(filename='', mtime=0, compresslevel=9)` |
| m7 | Skąd `ATTRIBUTIONS/LIMITATIONS/TERMS` pakietu? W LL-PL generuje je `verify.py:553-555`. TERMS dla list POP (SGJP BSD + wybór miarą z CC BY) bez treści. | `verify.py` | generować z `pop-sources.json`; dopisać warunki list |
| m8 | Miara NKJP leksemu z jedną formą = surowa liczba formy. To obchodzi C14. | C11, C14 | w raportach i `explain` tylko rangi/percentyle NKJP; test na to |
| m9 | Wiki dziś: „słowa, które zna przeciętny gracz” (Slownik-POP, Home). Spec v3 §9.4 tego zakazuje bez przeglądu. „Typowe formy” przesądza D2. | wiki | E4: usunąć oba; dopisać link w `Slownik-STANDARD` i usunięcie „W przygotowaniu” wszędzie (runbook) |
| m10 | Kod `pop.py` zmieni się między A i C. „Te same liczby z tego samego kodu” nie jest gwarantowane. | spec „Podejście” | `measure.json` z `code_identity`; D-6: liczby pakietu = liczby raportu A dla wybranych opcji, albo ponowny pomiar |
| m11 | Brak testów dla C14 i dla „tylko KWJP i NKJP”. SJP.pl jako miara nie pojawia się w A ani C. | tabela ograniczeń | test skanu pakietu; test walidatora manifestu; dodać miarę `POP ∖ SJP.pl` (tylko raport) albo napisać, że jej nie ma |
| m12 | D7 nie jest decyzją („tylko miara, bez wpływu na skład”). Reguła „leksem potoczny” nieokreślona (kwalifikator jest per interpretacja). | A6, D7 | D7 = „akceptacja luki: tak / osobne zadanie”; leksem potoczny = token `pot.` w dowolnej interpretacji |
| m13 | Warstwy próbek bez „różnych części mowy”; brak rozdziału przykładów ilustracyjnych od losowej próby (§9.4). | C17 | dodać warstwę POS; oznaczyć przykłady w raporcie jako ilustracje |
| m14 | ADR-006: wycofanie = pakiet bez NKJP. „Kod obsługuje tylko opcje wybrane w ADR-007” może usunąć ścieżkę bez NKJP. | spec „Podejście” | walidator zawsze przyjmuje D3 = „sama KWJP” |

Dwie dalsze uwagi bez osobnej pozycji: D-2 powinno objąć też `manifest.json` i `reports/` przebiegu (pliki 0600/0644, zapisywalne). Po etapie B potrzebna rewizja spec i plan C; spec nie nazywa tej bramki.

## Spójność z decyzjami właściciela

| decyzja | w spec | ocena |
|---|---|---|
| leksem z typowymi formami | C5, D2 | zgodne |
| rozmiar wg pokrycia | D1, D6 | zgodne; sufit 93,5% opisany |
| potoczne tylko z korpusów, luka mierzona | A6, D7 | zgodne (m12) |
| oba warianty form mierzone | D2 | zgodne |
| 30 na warstwę, agent + właściciel | A7, C17, D-4 | zgodne, ale niewykonalne bez zmiany (M5) |
| osobny pakiet, Release `pop-v1` | C11, E1 | zgodne (M6) |
| z zamrożonego v29, minuty | C2, C4, C15 | zgodne; sprawdzone pomiarem |
| dwie stałe listy | poza zakresem: skala ciągła | zgodne |

## Ograniczenia projektu

| ograniczenie | ocena |
|---|---|
| brak ≠ 0 | zasada jest (C6), luka w braku częściowym (M3) |
| bez kopiowania F między homonimami | zasada jest (C7), luka w definicji jednoznaczności NKJP (M1) |
| POP0 ⊆ POP ⊆ STANDARD | dobrze: test, kontrola przed zapisem, D-3 niezależnie |
| odtwarzalność | dobrze; gzip do doprecyzowania (m6) |
| atrybucja ADR-006 | dobrze (E2, B4); TERMS list do dopisania (m7) |
| bez surowego NKJP | zasada jest; furtka przez miary leksemu (m8) |
| SJP.pl tylko jako miara | brak ryzyka, bo SJP.pl nie jest użyty wcale (m11) |
| baza tylko do odczytu | dobrze; `mode=ro` działa, sonda nic nie zapisała |

## Etapy A→E

Spójne. A mierzy, B decyduje, C buduje, D odbiera, E wydaje. Odroczenie D1–D8 jest uczciwe, bo C dostaje je jako konfigurację z walidatorem. Słabe miejsca:
- A musi mierzyć pełne listy opcji (M1–M3), inaczej B wybiera z niepełnego menu.
- Między B i C brak bramki „rewizja spec + plan” (uwaga wyżej).
- D nie ma kodu, który sprawdza przegląd (M6).

## Testowalność kryteriów

| etap | ocena |
|---|---|
| A | testowalne (bajty `measure.json`, hash bazy, tabele D1–D8) |
| B | testowalne (walidator `pop.json`); „zaakceptowany” = status w ADR |
| C | testowalne; ≤ 10 min realne (odczyt 14 s, hash 14 s) |
| D | D-1, D-2, D-3 testowalne; D-4 bez sprawdzenia hashy przeglądu (M6) |
| E | „linki działają” bez metody; dodać `curl -fI` na assety i strony wiki |

## Rekomendacje (kolejność)
1. Przed A: poprawić D3, D5, D8 (M1–M3) i dopisać pomiar mapowania form z konstrukcji (M4).
2. Przed C: wybrać wariant próbek (M5), wiązanie przeglądu z wydaniem (M6), `--release-dir` (m1), hash bazy w każdym `pop` (m2), klucz leksemu (m3).
3. Przed E: poprawić wiki wg m9; TERMS list (m7).
4. Pozostałe drobne poprawki wpisać do spec rew. 2.
