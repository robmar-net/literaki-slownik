# projekt: zasady źródeł i droga wejścia nowego słowa

## TL;DR
- Leksem wchodzi do list tylko z danych SGJP albo z `sgjp-supplement.tab`. Korpus może być tylko dowodem użycia (§2.4, §4.4).
- Kod przyjmuje dziś tylko 6 rodzajów artefaktów (`inputs.py: KINDS`) i w trybie produkcyjnym dokładnie: 1 SGJP + 13 list KWJP + najwyżej 1 suplement. Nowe źródło leksykalne to zmiana kodu, testów i ADR.
- Najkrótsza droga dla pojedynczych słów: nowe wiersze w suplemencie (nowa wersja), po decyzji użytkownika, z plikiem dowodów. Najczystsza: nowe wydanie SGJP.
- Dziś obowiązuje wariant A z `source-extension-decision.md`: „nie rozszerzać zasobu leksemów”. Każde słowo spoza SGJP wymaga, by użytkownik to uchylił.

## Kluczowe decyzje
Do podjęcia przez użytkownika (agent ich nie rozstrzyga):
1. **Czy w ogóle dopuszczamy leksemy spoza SGJP.** Uchyla to wariant A i zmienia rozumienie §2.4 („podstawą … są leksemy udokumentowane w danych SGJP”).
2. **Droga wejścia:** (a) suplement v2, (b) nowe źródło leksykalne w kodzie, (c) tylko czekanie na nowe SGJP.
3. **Próg dowodu dla jednego słowa.** Propozycja liczb jest w `projekt-metoda.md`. SJP.pl nie może być dowodem (§3.1, §3.2).
4. **Czy nowy leksem trafia do STANDARD i BROAD.** Wiersz w suplemencie trafia do obu, jeśli nie ma kwalifikatora.
5. **Rytm przeglądu:** przy każdym nowym wydaniu KWJP albo SGJP, czy częściej.

## Otwarte pytania
- `sources.md` tego badania mówi o „15 artefaktach KWJP100”. W `sources.json` jest ich 13 (12 list słów + 1 lista 2-gramów). Razem z SGJP i suplementem daje to 15 artefaktów.
- Słowosieć 4.5 ma niejasną licencję (ADR-011). Jako filtr kandydatów nic nie publikuje, ale jako źródło leksykalne wymagałaby nowej decyzji.

## 1. Zasady wiążące (cytaty)
| Źródło | Zasada | Skutek dla nowych słów |
|---|---|---|
| spec v3 §2.4 | „Podstawą wszystkich początkowych dużych wariantów, także BROAD, są **leksemy udokumentowane w danych SGJP** …”; „Nie rozszerzaj automatycznie zasobu leksemów przez … reguły słowotwórcze”. | Prefiksowe `anty-`, `post-`, `trans-` nie wchodzą z reguły. Wchodzą tylko udokumentowane. |
| spec v3 §4.4 | „Korpusy mogą dostarczać dowodów użycia … **Nie mogą automatycznie rozszerzać** początkowego zasobu leksemów poza dane SGJP”. | Metoda daje tylko listę kandydatów do decyzji. |
| spec v3 §4.4 | WSJP i pełna baza SGJP online „nie są wejściami w podstawowym wariancie” bez ustalenia uprawnień. | Nowe hasła z WSJP lub SGJP online to tylko ręczny dowód. |
| spec v3 §4.5 | „nieustalone warunki … oznaczają BLOCKED”. | Źródło bez licencji danych nie wchodzi nawet jako dowód w buildzie. |
| spec v3 §3.1–3.2 | Bez SJP.pl, OSPS i PoliMorfa jako wejścia. Poprawka po benchmarku musi mieć uzasadnienie „niezależne od samej obecności słowa w SJP.pl” i dotyczyć „ogólnej reguły, a nie dopisania słów z listy różnic”. | Kandydatów nie wolno brać z różnic z SJP.pl. Progów nie stroimy pod SJP.pl. |
| spec v3 §2.3 | STANDARD obejmuje też potocyzmy, wulgaryzmy i słowa rzadkie. | Rzadkość nie wyklucza. Brak w SGJP wyklucza. |
| AGENTS.md | Decyzje zmieniające skład słownika „omawiamy z użytkownikiem przed ich wdrożeniem: przykłady, alternatywy, wpływ”. Bez kontaktu z autorami. Każda zmiana źródeł aktualizuje wiki. | Krok decyzji użytkownika jest obowiązkowy. |
| `source-extension-decision.md` (wariant A) | „Dopuścić do manifestu wyłącznie artefakty z pozytywnym audytem, **w roli uzupełniających dowodów** dla … istniejących leksemów SGJP. **Nie rozszerzać zasobu leksemów**”. | Obowiązuje dziś. Blokuje nowe leksemy. |
| `round4-sjp-benchmark-fixes-decision.md` | Przymiotniki przedrostkowe spoza SGJP (`antydumpingowy`, `neoliberalny`, `prorosyjski`, `postsowiecki`, `prorodzinny`) to „osobna luka źródła; wymagałaby konstruktora lub nowego źródła”. | Precedens: luki SGJP są znane od rundy 4 i odłożone. |
| ADR-006 | NKJP 1grams: CC BY bez wersji; spełniamy sumę wymagań CC BY 1.0–4.0. Zakres: tylko POP i POP0. | NKJP wolno używać jako miary. Manifest generatora nadal ma `unavailable: NKJP (BLOCKED_LICENSE_VERSION_UNRESOLVED)`, bo LL-PL go nie używa. Użycie w metodzie wymaga rozszerzenia zakresu ADR-006. |
| ADR-011 | Słowosieć 4.5: z pochodnej publikujemy tylko lematy. Licencja to tekst noty („plWordNet 4.2 © 2020”), link do licencji zwraca 404. | Słowosieć nadaje się na filtr kandydatów. Jako źródło leksemów nie, bo nie ma fleksji, a licencja jest niejasna. |

## 2. Jak kod przyjmuje źródło
Źródło: `literaki_slownik/inputs.py:16-22, 60-101`, `build.py:107`.

- `KINDS`: `sgjp_tab` i `lexical_supplement` mają rolę `lexical`; `kwjp_lemma`, `kwjp_orth`, `kwjp_orth_lc` i `kwjp_bigram` mają rolę `corpus_evidence`. Inny `kind` dostaje odmowę: „Niedopuszczony typ lub rola źródła”.
- `origin` musi pasować do rodzaju: SGJP, `project` albo KWJP.
- Wymagane pola: `source_id, version, url, retrieved_at, authors, license, license_scope, used_for, attribution, dependencies`, do tego `status: ALLOWED`, `path` + `sha256`, a także `evidence` (niepusta lista plików z sha256, każdy sprawdzany).
- `expected_counts`: dla rodzajów leksykalnych dozwolone są klucze `records, interpretations, duplicates, expanded_alternatives, lexemes, original_forms`, a dla korpusów `records, sum_freq`. W trybie produkcyjnym są obowiązkowe.
- Tryb produkcyjny: `len(artifacts) == 14 + supplements`, `supplements ≤ 1`, a 13 slotów KWJP musi zgadzać się dokładnie. **Drugiego suplementu ani nowego korpusu nie da się dodać bez zmiany kodu.**
- Do tabeli leksemów importuje tylko `import_sgjp`, dla `sgjp_tab` i `lexical_supplement`. Dane korpusowe idą do `corpus_evidence` i nie tworzą leksemów.

## 3. Rola `sgjp-supplement.tab`
- Dziś 4 wiersze: się (`part`), siebie, sobie, sobą. Format eksportu SGJP: forma, lemat, tag, kategoria, kwalifikatory.
- Nagłówek uzasadnia wpis tak: „brak w eksporcie TSV, obecne w opisie SGJP i w KWJP”. Każdy nowy leksem spoza SGJP łamie to zdanie, więc trzeba nowej wersji (`sgjp-supplement-v2`) z nowym nagłówkiem.
- Wpis w `sources.json` (`sgjp-supplement-v1`): `license_scope` „4 formy zaimka zwrotnego”, `dependencies` „KWJP jako dowód istnienia lematów”, `expected_counts` {records 4, interpretations 4, duplicates 0, expanded_alternatives 6, lexemes 2, original_forms 4}.
- Wycofanie: usunięcie wierszy i nowy build (runda 4).

## 4. Drogi wejścia: co trzeba zrobić
| Droga | Zmiany | Zgodność dziś | Wysiłek |
|---|---|---|---|
| **A. Nowe wydanie SGJP** | nowy artefakt `sgjp_tab`: url, sha256, `version`, `retrieved_at`, `expected_counts.records`, dowód licencji; build, benchmark i wiki | pełna, bez nowej decyzji o polityce | mały |
| **B. Suplement v2** | decyzja użytkownika (uchyla wariant A) → plik decyzji z dowodami (KWJP + ręczny dowód z dopuszczonego źródła) → wiersze z pełną fleksją w tagsecie SGJP → nowy nagłówek → `sources.json`: sha256, `version`, `license_scope`, `dependencies`, `evidence`, wszystkie 6 liczników `expected_counts` → testy → build, benchmark, wiki | wymaga decyzji 1 | mały na słowo, ręczny |
| **C. Nowe źródło leksykalne** (np. lista neologizmów z fleksją) | nowy `kind` w `KINDS`, zmiana reguły „14 + supplements”, importer, testy odmowy, ADR, audyt licencji §4.5 | wymaga decyzji 1 i źródła z fleksją i licencją | duży |
| **D. Tylko dowód** (bez zmiany list) | kandydaci w raporcie, wpis „luka źródła” jak w rundzie 4 | pełna | minimalny |

Ograniczenie B: każdy paradygmat pisze się ręcznie. §2.2 wymaga pełnej poprawnej fleksji, a SGJP nie podaje wzoru dla słowa, którego nie ma. Wzór trzeba wziąć z podobnego leksemu SGJP (np. `wagina` dla `wulwa`), a to jest decyzja redakcyjna.
