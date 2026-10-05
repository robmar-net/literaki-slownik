# Warunki publikacji generatora — zatwierdzone A

## TL;DR
Przygotowano konkretne warianty licencji własnego kodu oraz dokumentacji i raportów.
Warunki SGJP i KWJP zachowujemy oddzielnie, razem z pełną atrybucją i opisem zmian.
Użytkownik zatwierdził A: BSD-2-Clause dla własnego kodu oraz CC BY 4.0 dla własnej dokumentacji i raportów.
Gotowość list nadal zależy od pełnej kwalifikacji, dwóch odtworzeń i przeglądu.

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
