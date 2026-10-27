# Decyzje i dokumenty: etykiety, źródła, słowniki tematyczne

## TL;DR
Słowniki tematyczne są w planie od początku (prompt v3, Zadanie E), jako podzbiory bazy dopuszczalności.
Prompt v3 wymienia trzy metody (zalążki w n-gramach KWJP, korpus dziedzinowy, LLM). Etykiet dziedzin SGJP wśród nich nie ma.
Źródła: SGJP (BSD-2-Clause), KWJP (CC BY 4.0), NKJP (CC BY, ADR-006). WSJP i Wikisłownik: nie hurtowo. Kontaktu z autorami nie ma.
Każdy nowy słownik wymaga strony wiki od startu prac.

## Key Decisions
Decyzje użytkownika, które wiążą filtr tematyczny:
- **Temat nie zmienia gry.** Słowniki znajomości i tematyczne są podzbiorami wersjonowanej bazy (`docs/plan-dalszych-prac-runbook.md:14`; `docs/literaki-niezalezne-slowniki-prompt-v3.md:412, 514`).
- **Klasyfikujemy leksemy, potem formy. Leksem może mieć wiele tematów.** Etykieta tematu nie znaczy, że każde użycie dotyczy tematu (`prompt-v3.md:412, 422`).
- **Raportujemy jakość próbek, nie tylko liczby** (`prompt-v3.md:426`).
- **SJP.pl nie służy do klasyfikacji tematycznej** (`prompt-v3.md:77`).
- **Dziedzina nie wyklucza słowa** (reguła opisowa, `docs/generator/etykiety.md:54-60`; `qualifiers.json` `approved_partial_rules`: „approved prompt §2.3 and spec §5”).
- **Etykiety bez objaśnienia (25, m.in. `astron.`, `kolej.`, `fot.`) — wariant A:** zachowane, „objaśnienie nieustalone”, bez zgadywania skrótów (`…/evidence/unexplained-labels-first-release-decision.md`, TL;DR i „Przykłady”).
- **WSJP (2026-10-08, „utrzymajmy obecny tryb”):** tylko pojedyncze hasła przy konkretnej decyzji, z cytatem i linkiem. Nie hurtowo. Brak licencji, `robots.txt` blokuje pobieranie (`…/evidence/wsjp-terms-audit.md`, „Decyzja właściciela”).
- **Wikisłownik:** odłożony (`…/evidence/wiktionary-attestation-decision.md`, TL;DR; `plan-dalszych-prac-runbook.md:54`).
- **Bez kontaktu z autorami.** Zapytanie do zespołu SGJP o metadane semantyczne nie zostało wysłane (`…/evidence/sgjp-semantic-metadata-request.md`, TL;DR; `AGENTS.md`).
- **Delegacja (2026-10-08):** decyzje o składzie i kryteriach agent podejmuje sam, z dowodem, jako odwracalne. Nie dotyczy nowych źródeł ani kontaktu z grupami (pamięć operatora, `dictionary-decisions-are-delegated-and-revisable.md`).

## Open Questions / Risks
- Etykiety SGJP to „czwarta metoda” spoza listy prompt v3. Użycie ich jako głównego kryterium tematu to zmiana metody; warto to zapisać w ADR.
- Kolejność, tematy pilotażu, progi i wagi E nie są zatwierdzone (`plan-dalszych-prac-runbook.md:99`).
- Korpus dziedzinowy (metoda 2) wymaga audytu warunków; bez niego metoda jest zablokowana (`prompt-v3.md:424-426`; `prompt-v3.md:150`).

## 1. Plan i specyfikacja
- `docs/literaki-niezalezne-slowniki-prompt-v3.md:24` — cel 4: „słowniki tematyczne pozwalające modelować zainteresowania i specjalizacje botów”.
- `prompt-v3.md:408-426` — Zadanie E. Przykładowe tematy: kulinaria, żywność, marynistyka, matematyka, sport, medycyna, botanika, muzyka, informatyka, kolej. Trzy metody pilotażu. LLM tylko ocenia istniejące jednostki. Licencje: preferowane CC0, domena publiczna, CC BY; CC BY-SA osobno.
- `prompt-v3.md:149` — WSJP i pełna baza SGJP nie są wejściami bez ustalenia uprawnień.
- `prompt-v3.md:152` — korpusy dają dowody i konteksty, ale nie rozszerzają zasobu poza SGJP.
- `docs/plan-dalszych-prac-runbook.md:93-99` — E: wybrać pilotaż, porównać trzy metody, utrwalać modele i wyniki. Issue #1 (otwarte) to ten runbook.
- Spec POP wyłącza tematy z zakresu POP (`.maister/tasks/development/2026-10-11-slowniki-pop-pop0/implementation/spec.md:217`).

## 2. Dokumentacja etykiet
- `docs/generator/etykiety.md:4-11` — 79 wartości nazw, 615 kwalifikatorów; rejestr to discovery, nie filtr.
- `etykiety.md:20` — tabela oznaczeń SGJP objaśnia proste etykiety; nie uzasadnia rozbicia złożonych na alternatywne sensy.
- `etykiety.md:56-60` — mapa opisowa: 357 etykiet, 73 dziedziny, 18 stylu, 2 warianty.
- `etykiety.md:82` — pełny ID SGJP może łączyć znaczenia; adnotacji jednego użycia nie przenosimy na wszystkie.
- `cache/sgjp/oznaczenia.html:242, 251, 298, 342` — `mat.` matematyczne, `mors.` morskie, `roln.` rolnicze, `żegl.` żeglarskie.

## 3. Audyt źródeł 2026-10-04
`.maister/tasks/research/2026-10-04-audyt-zrodel-polskich-slownikow/outputs/research-report.md`:
- w. 30 — SGJP tekstowy 20260823, BSD-2-Clause, główne wejście. Też `config/generator/sources.json:10-25`.
- w. 32 — KWJP100, CC BY 4.0, 13 plików.
- w. 24 — „pozostałe n-gramy KWJP służą późniejszym badaniom tematycznym”.
- w. 35 — pełna baza SGJP/WSJP: nie pozyskiwano.
- w. 144 — nie uruchomiono modeli tematycznych.
- NKJP n-gramy: CC BY bez wersji, przyjęte (`docs/adr/ADR-006-nkjp-cc-by-bez-wersji.md`).

## 4. Wiki i publikacja nowego słownika
`docs/runbook-wiki.md`:
- w. 10 — nowy rodzaj słownika dostaje stronę `Slownik-<NAZWA>` o tym samym układzie (cel, stan, co wchodzi, tabela filtrów z przykładem, linki do decyzji).
- w. 28 — przy starcie prac od razu strona „W przygotowaniu”, wiersz na `Home`, wpis w `_Sidebar`, link ze strony słownika bazowego.
- w. 29 — przy wydaniu: liczby, kryteria, pobieranie.
- Krok 3 — przykład przy filtrze sprawdzony przez `explain` (`--variant`).
- Wzór pakietu i licencji: `docs/generator/publikacja.md` (własny kod BSD-2-Clause, dokumenty CC BY 4.0, warunki źródeł osobno).

## Kandydaci spoza PAN
Wyszły przy okazji, nie szukano ich celowo:
- H. Zgółkowa, „Słownik minimum języka polskiego” (Universitas) — hasła według pól tematycznych. Status w projekcie: BLOCKED, licencja nieustalona (`docs/literaki-prosty-jezyk-minimum-leksykalne-kierunki.md:50-54, 90, 116`).
- Wikisłownik — CC BY-SA, odłożony decyzją użytkownika (`wiktionary-attestation-decision.md`; `wsjp-terms-audit.md`, opcja 3).
