# Raport końcowy i przekazanie projektu generatora

## TL;DR

Etap audytu i projektu został zakończony; użytkownik zatwierdził projekt odpowiedzią „ok”.
Pierwszy generator ma przygotować BROAD i STANDARD z pełną dopuszczalną fleksją i sprawdzonymi konstrukcjami.
Przyjęto lokalny proces Python/SQLite, wyjaśnienia decyzji i kontrolę kompletności przed wydaniem.
SGJP/KWJP są podstawą pierwszego wyniku; NKJP pozostaje zablokowany do czasu wyjaśnienia warunków.
Następny krok to osobne zadanie maister-development; generator nie został jeszcze zaimplementowany.

## Key Decisions

- G1: dwa kompletne w przyjętym zakresie kandydaty, nie niepełny pilot jako wynik końcowy.
- N1: pierwszy wynik SGJP/KWJP; NKJP pozostaje wymaganiem całego projektu, do dołączenia w nowym wydaniu.
- C1: udokumentowane konstrukcje istniejących leksemów w głównych kandydatach po kontroli każdej klasy.
- Zatwierdzono architekturę i kryteria K1–K10; nie zatwierdzono nieznanej semantyki reguł ani nie rozpoczęto implementacji.

## Open Questions / Risks

- Semantyka mieszanych kwalifikatorów i pól nazw, kategorie skrótowców, macierz fleksji/konstrukcji i zgodność pisowni wymagają dowodów przed pełnym wydaniem.
- NKJP nie bierze udziału w konstrukcji ani dopasowaniach. Nieustalone warunki nie oznaczają technicznej niedostępności.
- Wydajność SQLite oraz koszty pełnego przebiegu wymagają pomiaru. Warunki publikacji własnego kodu i wyników pozostają do ustalenia przed wydaniem.

## 1. Co wykazał audyt

[Raport pomiarowy](research-report.md) pozostaje niezmiennym zapisem dowodów etapu 1, związanym z [manifestem](audit-manifest.json) i commitem `6137e23`. Ten raport końcowy dopisuje późniejsze rozstrzygnięcia bez zmiany pierwotnych wyników. Historyczne zapisy „oczekuje” w manifestach audytu odnoszą się do chwili ich utworzenia; aktualne zatwierdzenia są w stanie zadania i niniejszym przekazaniu.

Audyt daje podstawę do rozpoczęcia pierwszego generatora: zbadano 7 458 520 rekordów SGJP, 13 plików KWJP oraz technicznie cały artefakt unigramów NKJP. Pełne formy osobowe są już obecne w eksporcie; mechaniczne składanie może nadgenerować. Korpusowe poświadczenie, jednostka leksykalna i dopuszczalność wymagają odrębnego modelowania. Scenariusze przesiewu pozostają pomiarami wariantów, nie gotowymi słownikami.

Pewność jest wysoka dla zmierzonych formatów i konkretnych bajtów, umiarkowana dla finalnej polityki językowej. Zatwierdzenie projektu nie zwiększa samo w sobie pewności brakujących dowodów.

## 2. Pokrycie i granice źródeł

| Kategoria | Wykonane | Ograniczenie |
|---|---|---|
| SGJP/Morfeusz | Pełny eksport, nagłówek warunków, format, statystyki, kod reguł i próby kontrolne | Nie udowodniono jeszcze kompletności wszystkich klas |
| KWJP100 | Audyt 13 przypiętych plików, warunków, jednostek i pilotaż dopasowań | Homonimia, segmentacja i historia anotacji mają jawne ograniczenia |
| NKJP | Dokumentacja, warunki i pełny pomiar techniczny unigramów | BLOCKED do konstrukcji i dopasowań |
| PoliMorf | Dokumentacja pochodzenia | Wyłączony jako wejście zgodnie ze specyfikacją |
| Reguły gry | Publiczny profil PL i odnotowana kontrola lokalnych reguł | Część źródeł aplikacji jest prywatna; nie kopiowano ich do repo |
| Konstrukcje / ortografia | Wskazane rozdziały dokumentów RJP i SGJP, porównanie z kodem reguł | Audyt celowany, nie pełna macierz językowa |

Sprawdzono osiem wymaganych oficjalnych punktów startowych. Opcjonalne źródła z §4.4 specyfikacji nie są obowiązkowymi wejściami pierwszego audytu. Szczegóły: [pokrycie](../planning/sources.md), [uzupełnienie konstrukcji](../analysis/findings/construction-scope.md). Dane benchmarku i OSPS nie były używane.

## 3. Przyjęty projekt

[Projekt wysokiego poziomu](high-level-design.md) opisuje sześć modułów jednego lokalnego narzędzia: kontrolę wejść, import, reguły, powiązania KWJP, kontrolę i wydanie oraz wyjaśnianie. [Pięć ADR](decision-log.md) utrwala rozważone alternatywy i konsekwencje.

Przebiegi mają jawne manifesty i własne katalogi; nie nadpisują poprzednich wydań. Oryginalne interpretacje i rekonstrukcje zachowują ślad pochodzenia. Niepewność jest wynikiem unresolved, a nie domyślnym odrzuceniem. Warunki K1–K10 rozdzielają działający proces techniczny od pełnego kandydata do oceny.

ATTESTED, modele znajomości, tematy, benchmark i integracja gry pozostają późniejszymi etapami. Nie rozpoczęto generatora produkcyjnego ani nie zmieniono działającej aplikacji.

## 4. Przekazanie do maister-development

Katalog wejściowy następnego zadania:

```text
.maister/tasks/research/2026-10-04-audyt-zrodel-polskich-slownikow
```

Zlecenie do użycia przy rozpoczęciu następnego etapu:

> Przygotuj implementację pierwszego generatora LL-PL-BROAD i LL-PL-STANDARD według zatwierdzonego projektu i decyzji G1/N1/C1. Zacznij od analizy istniejących skryptów, uzupełnienia specyfikacji i planu. Uwzględnij osobne zadania dowodowe dla semantyki etykiet, skrótowców, fleksji, konstrukcji i ortografii. Nie traktuj audytowego przesiewu jako finalnej polityki. Realizuj K1–K10; nie uznawaj pilota za pełny wynik. Nie używaj NKJP, benchmarku ani wyłączonych źródeł jako wejść pierwszego generatora.

To przygotowany opis przyszłego zadania, nie uruchomiona implementacja. Research nie zastępuje analizy repo, specyfikacji, planu ani weryfikacji w maister-development. Przy nowym rzeczywistym wyborze polityki należy przedstawić dowody i warianty użytkownikowi; spraw ustalonych w §2 specyfikacji oraz D1–D3 nie otwierać ponownie bez nowego powodu.

## 5. Artefakty i weryfikacja

- [Specyfikacja wejściowa v3](../../../../../docs/literaki-niezalezne-slowniki-prompt-v3.md) — zachowana bez zmian bajtowych.
- [Raport audytu](research-report.md), [synteza](../analysis/synthesis.md) i [manifest](audit-manifest.json) — pierwotne dowody i pomiary.
- [Porównanie rozwiązań](solution-exploration.md) — wybory i odrzucone alternatywy.
- [Projekt](high-level-design.md) i [rejestr decyzji](decision-log.md) — zatwierdzona podstawa następnego etapu.
- [Odtwarzanie audytu](../../../../../docs/odtwarzanie-audytu.md) — skrypty, cache i organizacja repozytorium.

Przy zamknięciu kontrolujemy obecność artefaktów, linki i zgodność hashy pierwotnego audytu. Widoki HTML projektu były sprawdzone przy szerokościach 390 i 1280 pikseli; oznaczenia zatwierdzenia aktualizujemy z Markdown. Nie wykonujemy ponownie kosztownych pomiarów źródeł przy zmianie statusu dokumentów.
