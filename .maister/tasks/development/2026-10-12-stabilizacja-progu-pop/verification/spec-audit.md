# Audyt specyfikacji #4 i #6

## TL;DR

Specyfikacja obejmuje wybór 2382 form, trwały JSON, selekcję POP, diagnostykę, odbiór oraz wiki.
Na przypiętej bazie każda z 7192 trójek badawczych odpowiada dokładnie jednej rozwiniętej analizie.
Trzy doprecyzowania dotyczące tożsamości analizy, starego `explain` i przeglądu K9 wpisano do specyfikacji.
Po tych korektach nie ma blokera dla planowania; wyniki pełnego buildu pozostają do weryfikacji.

## Key Decisions

- status: `passed`; otwarte blokery: 0; otwarte usprawnienia: 0.
- Konfiguracja ma wiązać dokładny rekord źródła albo klucz istniejącej konstrukcji, nie sam napis lub lemat.
- Dwa buildy nie zastępują przeglądu próbek wymaganego przez K9 do `verify/export`.

## Open Questions / Risks

- Zgodność 7192 kluczy sprawdzono na zamrożonej bazie, a nie na nowym przebiegu. Nowy build musi powtórzyć tę kontrolę i odmówić rozjazdu.
- Stały próg POP nie jest merytoryczną granicą popularności; pozostaje otwarty w #6.

## Źródła audytu

Przeczytano `analysis/requirements.md`, `implementation/spec.md`, obie analizy zadania, `AGENTS.md`, ADR-007, `docs/generator/cli.md`, `docs/runbook-wiki.md` oraz ścieżki `inputs.py`, `build.py`, `decisions.py`, `policy.py`, `pop.py`, `explain.py`, `verify.py`. Dane badawcze: `round3/proposal-proof.json`, `round3/family-decisions.json`, `round3/validation.json`, `round5/*-measurements.json`.

## Ustalenia i poprawki

| Waga | Miejsce | Ustalenie i skutek | Rozwiązanie |
| --- | --- | --- | --- |
| warning, rozwiązane | Spec „Zawartość konfiguracji STANDARD” pkt 1–3 | Trójka forma–lemat–tag nie wyrażała tożsamości rekordu ani liczby dopasowań. Przez to późniejsza zmiana importu mogłaby po cichu rozszerzyć wyjątek. | Dopisano dokładny rekord źródła albo klucz kandydata, hash wejścia i obowiązek rozliczenia każdej pozycji dokładnie raz. Lokalny odczyt tylko do odczytu wykazał rozkład dopasowań `{1: 7192}` na bazie badania. |
| warning, rozwiązane | Spec „Zawartość konfiguracji STANDARD” pkt 5 | `explain` liczy część diagnostyki bieżącym kodem nawet dla starej bazy. Obietnica „zachowuje historyczny opis” była niejednoznaczna. | Spec odróżnia zapisaną historyczną ocenę od bieżącej diagnostyki i wymaga zgodności nowego przebiegu z przypiętym JSON-em. |
| warning, rozwiązane | Spec „Dokumentacja, wdrożenie i wycofanie” | Dwa identyczne buildy nie wystarczają do istniejącego `verify`: K9 wymaga oceny próbek związanej hashami. | Dopisano osobny przegląd próbek przed `verify/export` i zakaz publikacji bez niego. |

## Pokrycie wymagań i wykonalność

- Problem, użytkownicy i obieg: właściciel zatwierdza zakres, operator edytuje JSON, build zapisuje decyzje, verify porównuje listy, wiki objaśnia stan wydania.
- Funkcjonalność: S1–S3 obejmują dokładność STANDARD; P1–P3 obejmują POP/POP0 i zabezpieczenia; R1 i D1 obejmują odbiór, dokumentację oraz wiki. Każdy warunek da się sprawdzić z plików i raportów.
- Granice: osiem cofnięć, docelowa kalibracja, GitHub Release i integracja z grą są wyłączone. Zachowana jest ścieżka starszych pakietów.
- Dane i bezpieczeństwo: hashe wejść, nowy katalog buildu, brak surowych danych w repo, odmowa na niezgodności. Brak potrzeby zmiany serwera lub GitHub-hosted CI.
- Testowanie: lokalny skrypt audytu odczytał 2382 formy i 7192 wskazanych analiz z `proposal-proof.json`, po czym sprawdził przez indeks `analysis_game_key` dokładną tożsamość w zamrożonej bazie; wszystkie miały jedno dopasowanie. Ten odczyt nie zastępuje nowego pełnego buildu.

## Wynik

`passed`: specyfikacja po doprecyzowaniach jest spójna i wystarczająca do planowania. Nie ustala z góry wyników nowego buildu ani zgody na wydanie.
