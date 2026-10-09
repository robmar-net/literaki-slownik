# Warunki publikacji generatora — zatwierdzone A

## TL;DR
Przygotowano konkretne warianty licencji własnego kodu oraz dokumentacji i raportów.
Warunki SGJP i KWJP zachowujemy oddzielnie, razem z pełną atrybucją i opisem zmian.
Użytkownik zatwierdził A: BSD-2-Clause dla własnego kodu oraz CC BY 4.0 dla własnej dokumentacji i raportów.
Gotowość list nadal zależy od pełnej kwalifikacji, dwóch odtworzeń i przeglądu. Verify/export (G7) opisuje sekcja na końcu.

## Key Decisions
- Licencja projektu dotyczy tylko praw do naszych wkładów. Nie przypisuje nam praw do materiałów zewnętrznych ani nie zmienia warunków źródeł.
- Generator nie publikuje surowych cache ani baz roboczych. Warunki redystrybucji konkretnej bazy muszą być sprawdzone osobno, jeśli taki plik ma wejść do pakietu.
- Zewnętrzne oryginały zachowują własne warunki i polską metryczkę; nie zastępujemy ich treści lub licencji własnym oznaczeniem.
- Zatwierdzenie wariantu licencji nie nadaje VERIFIED/FROZEN i nie zwalnia z K1–K10.

## Open Questions / Risks
- Wybór A zatwierdzono; zapisano LICENSE, LICENSE-DOCS.md oraz ATTRIBUTIONS.md. Gotowość wydania i osobne warunki ewentualnie publikowanej bazy nadal wymagają K1–K10.
- Pełna polityka i wymagane dowody językowe pozostają nieukończone; decyzja licencyjna jest odrębna od dopuszczalności słów.

## Proponowany zakres

| Materiał | A — rekomendowane | B — alternatywa |
|---|---|---|
| Nasz kod w literaki_slownik, scripts, tests; własne konfiguracje i narzędzia | BSD-2-Clause | MIT |
| Nasza narracyjna dokumentacja, README/AGENTS i własne raporty Maister | CC BY 4.0 | CC BY 4.0 |
| Materiał tekstowego eksportu SGJP użyty w listach i śladach | Zachowane źródłowe warunki BSD-2-Clause i pełna atrybucja | Tak samo |
| Dane/miary KWJP obecne w raportach | Zachowane źródłowe CC BY 4.0, atrybucja i opis zmian | Tak samo |
| Materiały zewnętrzne o innych lub nieustalonych warunkach | Ich odrębne warunki; brak nowego zezwolenia przez licencję projektu | Tak samo |

A utrzymuje tę samą rodzinę licencji kodu co tekstowy eksport SGJP. B stosuje MIT do naszego kodu. Oba warianty pozostawiają dane źródłowe pod ich własnymi warunkami. Oznaczenie przyszłych list wskazuje źródło SGJP i zakres zmian, bez deklarowania wyłącznej własności zbioru.

Źródła tekstów licencji: [BSD-2-Clause — SPDX](https://spdx.org/licenses/BSD-2-Clause.html), [MIT — SPDX](https://spdx.org/licenses/MIT.html), [CC BY 4.0 — Creative Commons](https://creativecommons.org/licenses/by/4.0/). Rekordy warunków użytych danych są przypięte w config/generator/sources.json; pełne teksty powiązanych licencji i ich hashe pozostają w zatwierdzonym audycie.

## Pliki po zatwierdzeniu

- LICENSE — pełny oryginalny tekst wybranej licencji kodu, z polską metryczką i nazwą autorów projektu, bez zmiany warunków tekstu.
- LICENSE-DOCS.md — wskazanie CC BY 4.0 i zakres własnej dokumentacji/raportów; wyraźne zachowanie warunków zewnętrznych oryginałów.
- ATTRIBUTIONS.md — źródła, autorzy, wersje, warunki oraz opis operacji projektu.
- Deklaracja w README i konfiguracja pakietu, którą sprawdzi verify K10.
- Pakiet wydania zawiera właściwe ATTRIBUTIONS.md, LIMITATIONS.md, deklarację warunków i manifest wiążący bajty; powstaje dopiero po pełnym verify.

## Historia wyboru

A: BSD-2-Clause dla własnego kodu, CC BY 4.0 dla naszej dokumentacji i raportów, źródła z zachowaniem własnych warunków.

B: MIT dla własnego kodu, pozostały zakres jak A.

C: inne warunki wskazane przez użytkownika przed wdrożeniem licencji.

Konieczność wyboru wynika z zatwierdzonego planu G7/7.2: „ustalić jawnie warunki kodu/dokumentacji/list/raportów (…) bez narzucania licencji”. Pytanie zadano podczas dalszej niezależnej implementacji; użytkownik odpowiedział A.

2026-10-05T02:04:26.057030+00:00 — Zatwierdzone warunki wdrożono w repozytorium. Nie oznacza to ukończenia G7 ani wydania list.

## Verify i export — wdrożenie G7

`verify --run-dir A --peer-run B --review PLIK` sprawdza K1–K10 i niczego nie buduje ani nie poprawia. Każde wywołanie zapisuje nową próbę `A/verification/attempt-NNNN/`: `package-plan.json` (zawsze INCOMPLETE, I1), katalog `candidate/` z przyszłym pakietem i `verification.json` z wynikiem per K. Manifest przebiegu zmienia się tylko przy pełnym powodzeniu: dostaje readiness VERIFIED i pieczęć hashy. Przy odmowie kod wyjścia to 5, a JSON ma `status: refused`.

| K | Co sprawdza verify |
|---|---|
| wszystkie | Każdy etap ma status complete. Running po awarii albo pending blokuje każde K (§9). |
| K1 | Ponowny inspect-sources: wejścia, hashe i tryb. Fikstura (`mode: test`) nigdy nie przechodzi przez publiczne CLI. |
| K2 | `import-counts.json` rozlicza dokładnie aktywne źródła i zgadza się z `expected_counts`. |
| K3 | `lists/{broad,standard}.txt`: UTF-8 bez BOM, LF, klucze NFC/lower, unikalne i posortowane. Każda lista jest równa członkostwu accept w bazie, a STANDARD ⊆ BROAD. |
| K4 | Raporty coverage/decisions/construction-candidates bez znaczników `*_pending`, wszystkie klasy źródła CLOSED, brak ocen pominiętych. |
| K5 | Żadne nierozstrzygnięcie nie zmienia list. Pozostałe reguły muszą być w `known_limitations` z przypiętym dowodem braku wpływu. |
| K6 | Bramka etapu links jest zamknięta i nic jej nie blokuje. |
| K7 | Przegląd ma runtime explain dla accept, reject, unresolved, absent, rekonstrukcji, homonimów, odrzucenia przez profil i braku KWJP. Hash każdego wyniku zgadza się z bieżącym explain. |
| K8 | Kod jest niezmieniony od build, z commitu i nie dirty. Canonical-index zgadza się z plikami, logical-content z bazą, integrity_check i FK są w porządku. Drugi, niezależny build z tych samych wejść ma identyczne pliki kanoniczne. Czasy, log i performance nie są porównywane. |
| K9 | Przegląd jest związany hashami canonical-index i logical-content. Obejmuje każdą pozycję każdej próbki quality-v1, każda ma ocenę, przeglądającego i uzasadnienie źródłowe. Pozycja oznaczona jako wpływająca na listy lub linki blokuje werdykt. |
| K10 | Dla `configurations.release` warunki code/documentation/lists/reports mają status DECLARED i przypięte pliki, jest jawna decyzja o dystrybucji bazy oraz atrybucje i ograniczenia. |

Warunki pakietu zapisuje [config/generator/release.json](../../config/generator/release.json) według zatwierdzonego A. `known_limitations` ma trzy reguły w obu wariantach. Żadna nie zmienia list ([dowód](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/known-limitations-g8.md)).

`export --run-dir A --output-dir NOWY` przyjmuje tylko przebieg VERIFIED. Najpierw sprawdza pieczęć: manifest przebiegu, wejścia, canonical-index wraz z plikami, bajty `build.sqlite`, plan i każdy plik kandydata. Każda zmiana po verify daje odmowę 5. Następnie kopiuje zweryfikowane bajty do `.NOWY.staging-*` obok celu, dopisuje `reports/verification.json` i `release-manifest.json` (hashe wszystkich plików poza nim samym), porównuje hashe i ustawia pliki tylko do odczytu. Na koniec przenosi staging przez rename bez zamiany (macOS `renamex_np`, Linux `renameat2`). Istniejący cel, nawet pusty i nawet powstały w trakcie, nie zostaje nadpisany. Po awarii zostaje oznaczony staging, a przebieg pozostaje VERIFIED i można ponowić export do nowego celu. Po sukcesie przebieg ma status FROZEN, baza jest tylko do odczytu, a każda zmiana etapu, ponowne verify lub export kończy się odmową.

Pakiet zawiera: `LL-PL-BROAD.txt`, `LL-PL-STANDARD.txt`, kanoniczne raporty z `canonical-index.json`, `reports/verification.json`, `ATTRIBUTIONS.md` (wszystkie użyte źródła i atrybucje projektu), `LIMITATIONS.md`, `TERMS.md` i `release-manifest.json`. Baza nie jest plikiem pakietu. Wiążą ją hash logical-content i hash pliku w archiwum przebiegu.

Stan na 2026-10-07: dzisiejszy build nie zapisuje list, a etapy constructions/decisions/reports zostają pending, więc verify prawdziwego przebiegu zawsze odmawia. Mechanikę VERIFIED → FROZEN sprawdzają testy na fiksturze (`tests/test_verify.py`, `tests/test_export.py`, `tests/test_lifecycle.py`). Pierwszy prawdziwy odbiór to G8.
