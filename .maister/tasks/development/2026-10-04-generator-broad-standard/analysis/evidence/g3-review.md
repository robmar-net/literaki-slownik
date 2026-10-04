# Przegląd dowodów G3

## TL;DR
Domknięto pełną inwentaryzację, nadgenerację próby fleksyjnej i mapowanie KWJP.
G3 pozostaje nieukończona: brakuje części semantyki etykiet i wymaganych poświadczeń growych.
Wykonano niezależny fragment G5 zgodnie z wyjątkiem zatwierdzonego planu, bez aktywacji niepełnej polityki.

## Key Decisions
- Koordynator zweryfikował discovery trzech niezależnych ścieżek, zachowując wyłączność zapisu kodu/planów.
- Wszystkie 150 rekordów 30 defektywnych leksemów porównano z bazą readonly; 120 nadmiarowych trójek i 14 różnic tagów winien sprawdzono. Pierwsze porównanie kolejności rekordów nie przeszło; porównanie posortowanej treści potwierdziło pełną zgodność. Nie zmieniono danych.
- KWJP odtworzono własnym wersjonowanym skryptem; pełne rozkłady POS/statusów i NFC są identyczne z delegowanym wynikiem. Inwentaryzacja etykiet zgadza się z G2 w każdym polu/liczniku.
- Przeczytano wskazane sekcje źródeł pierwotnych i kod eksportera; nie przyjęto raportów agentów bez kontroli.
- Konfiguracje discovery są jawnie nieaktywne. Nie dodano skrótu omijającego K4/K5.

## Open Questions / Risks
- ZDS zawiera warunki poświadczenia całych kontrakcji oraz pochodzenia opracowań; pięciopolowy eksport nie dostarcza pełnej metryki artykułu hasłowego. To rzeczywista luka, nie dowód odrzucenia wszystkich takich form.
- Żadne słowa, werdykty ani listy SJP nie stały się wejściem konstrukcyjnym. Odczytano wyłącznie reguły i wcześniej wyraźnie zlecone przykłady działania serwisu.
- Rozszerzenie źródeł dowodowych o opracowania słownikowe wymaga określenia roli i audytu warunków. Nie wolno zastąpić tego dowolną flagą operatora.
- Nadal trzeba domknąć semantykę złożonych kwalifikatorów, macierz hostów i kategorii oraz całą politykę pisowni. Nie ukończono G4 ani finalnego G5–G9.

## Kontrole i artefakty
Źródła/hash/zakres: `config/generator/evidence.json`; pokrycie i nierozstrzygnięcia: `coverage.json`. Literalnych etykiet kwalifikatorów po podziale wyłącznie `|` jest 605; wartości całego pola 615. Nie mylimy tych jednostek.

Dokumentacja: `docs/generator/{etykiety,konstrukcje,ortografia,mapowanie-kwjp}.md`. Pełne własne wyniki: label-coverage, kwjp-mapping, closure-excess-all, closure-lexemes-evidence, winien-evidence, winien-closure i mobile-ending-evidence. Surowe dokumenty i baza pozostają ignorowane.

G5 fragment: `links.py` i `test_links.py`, rzeczywisty red (brak modułu), następnie 4/4 green; cała suita 25/25. Nie włączono etapu do build, nie odnotowano całej grupy jako complete. Normalizacja jest jawna; pełne ID i F zostają przy własnych jednostkach; relacje mają FK. Brak NKJP i przyszłe decyzje wydaniowe pozostają zgodne ze specyfikacją.
