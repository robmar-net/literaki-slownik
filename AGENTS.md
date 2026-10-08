# Zasady pracy w projekcie

W tym projekcie piszemy po polsku.

**Piszemy bardzo zwięźle i prosto.** Krótkie zdania, zwykłe słowa, bez żargonu. Najpierw wniosek, potem szczegóły. Jeśli coś da się powiedzieć krócej, mówimy krócej. Dotyczy to dokumentów, commitów, ticketów, wiki i odpowiedzi.

Jeśli włączamy materiały w innych językach, zachowujemy ich oryginalną treść i dodajemy tylko krótką polską metryczkę (np. tytuł, źródło, język i opis zawartości). Nie tłumaczymy całości.

## Dokumentacja i proces Maister

- Dokumentację projektu i materiały wejściowe przechowujemy w `docs/`.
- Konfigurację, stan i istotne artefakty Maister przechowujemy w `.maister/` w tym repozytorium i commitujemy razem ze skryptami oraz manifestami potrzebnymi do odtworzenia wyników.
- Pliki tymczasowe, pobrane surowe dane, cache i odtwarzalne pliki robocze trzymamy w katalogach wykluczonych przez `.gitignore`.
- Nie umieszczamy w publicznym repozytorium sekretów ani materiałów bez ustalonych warunków publikacji.
- Historyczny pierwszy etap specyfikacji v3 (rozdział 15) obejmował audyt, analizę i projekt; jego zatwierdzone wyniki pozostają zamrożone.
- Aktualna implementacja ma zatwierdzoną specyfikację i plan w `.maister/tasks/development/2026-10-04-generator-broad-standard/`. Nie oznaczamy pełnego wydania przy unresolved wpływających na listy; reguł gry nie zmieniamy.
- Decyzje zmieniające skład słownika lub kryteria dopuszczalności omawiamy z użytkownikiem przed ich wdrożeniem: przedstawiamy przykłady, alternatywy i przewidywany wpływ. Nie przejmujemy automatycznie polityki redakcyjnej ani ograniczeń źródłowych SJP.pl.
- **Zasady gry = Kurnik + ZDS (§1, §4, §5).** Kurnik odsyła do [ZDS](https://sjp.pl/sl/dp.phtml) jako do szczegółowych zasad. Przyjmujemy z niego wyjątki, dopuszczalne formy i pisownię łączną. Nie przyjmujemy jego wyboru źródeł (§2, §3, Dodatek A). Wersja jest przypięta w `config/generator/evidence.json`; nowej nie przejmujemy bez decyzji. Zob. [decyzję](.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/zds-game-rules-decision.md).

- Wiki projektu (https://github.com/robmar-net/literaki-slownik/wiki) opisuje dla odwiedzających rodzaje słowników, kryteria filtrowania, liczby i linki do pobrania. Każda praca, która zmienia kryteria, wersję list, źródła albo tworzy wydanie, aktualizuje też wiki według [runbooka wiki](docs/runbook-wiki.md). Praca bez aktualizacji wiki nie jest skończona.

- Nie kontaktujemy się z innymi grupami w ramach tego projektu. Brakujących danych i dowodów szukamy samodzielnie w dopuszczonych źródłach; nie wysyłamy zapytań do ich autorów.
