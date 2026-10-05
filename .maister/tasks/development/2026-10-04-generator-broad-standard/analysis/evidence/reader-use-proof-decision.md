# Własny przegląd opisów i przykładów oficjalnego czytnika SGJP

## TL;DR
Wspólny dowód leksykalny z autorskiej dokumentacji jest już zatwierdzony. Oficjalny czytnik zawiera dodatkowe opisy konkretnych użyć, których nie ma w dotychczasowym zakresie dowodu. Użytkownik odłożył ten ruch, aby zachować kontrolę nad danymi bazy. Nowy próg nie został aktywowany; obserwacje pozostają historyczne.

## Key Decisions
**A — rekomendowane:** dopuścić własny ręczny przegląd jednoznacznych opisów i przykładów w oficjalnym czytniku jako dowód konkretnego użycia istniejącego rekordu SGJP. Weryfikować źródłowy hash, pełny ID, wszystkie pięć pól i wiersz, publiczny artykuł oraz hash odpowiedzi. Powiązanie dotyczy sprawdzonego użycia, nie tożsamości wszystkich znaczeń internetowego i eksportowego ID. Nie importować glos/metadanych ani nie tworzyć nowych leksemów.

Próg leksykalny obu wariantów: wyłącznie jednoznacznie rozpoznane polskie użycie, nie sama etykieta człon frazeologizmu. Klasa nazw i inne ograniczenia są osobnymi dowodami/warunkami. Sprzeczności, różnice wersji, nieustalona polskość lub obcy cytat pozostają unresolved. Zatwierdzone wymagania wieku i pisowni nie są omijane.

**B:** czytnik pozostaje pomocą wyszukiwania i źródłem wcześniej zatwierdzonych jawnych relacji mieszkańców; dodatniego dowodu leksykalnego oraz innych nowych opisowych dowodów klasy szukamy w dotychczas dopuszczonej dokumentacji. Niejasne przypadki nadal unresolved.

## Open Questions / Risks
DEFERRED_BY_USER: nowych opisowych dowodów czytnika nie aktywujemy. Publiczny słownik i snapshot eksportu mogą dzielić znaczenia inaczej. Użycia i nierozpoznana pozostałość zachowane. Dane maszynowe czytnika nadal BLOCKED_as_machine_input; ta decyzja nie znosi audytu licencji snapshotu ani nie pozwala wykorzystać ich jako importera. Nie wykorzystujemy źródeł społecznościowych, SJP/OSPS/PoliMorf ani kontaktu z autorami.

## Konkretny przegląd do oceny
[Własne przypadki i hashe](reader-use-proof-review-cases.json) sprawdzono ponownie względem wszystkich sześciu zachowanych odpowiedzi. Surowy HTML i pełne glosy pozostają poza Git.

| Przypadek | Rozpoznanie do dalszego ręcznego przeglądu | Granica wnioskowania |
|---|---|---|
| [bezcen](https://sgjp.pl/leksemy/#91238/bezcen), źródło wiersz1221841 | konkretne polskie użycie z przyimkiem | dowód tego użycia; nie wszystkich możliwych znaczeń |
| [oścież](https://sgjp.pl/leksemy/#91689/oścież), oścież:F, wiersz4320577 | konkretne polskie użycie przysłówkowe z przyimkiem | oścież:S i inne homonimy osobno |
| [bin](https://sgjp.pl/leksemy/#91246/bin), wiersz1252933 | konkretne użycie jako człon nazwiska | uzupełnienie klasy tego użycia; nie odmowa wszystkim homonimom |
| [don](https://sgjp.pl/leksemy/#91612/don), wiersz1554730 | odrębne użycie wykrzyknikowe i drugi artykuł tytularny | dwa użycia, bez utożsamienia obu internetowych ID z całym eksportowym ID |
| [eleison](https://sgjp.pl/leksemy/#91346/eleison), wiersz1709262 | opis uwikłania frazeologicznego z obcym kontekstem | sama etykieta nie pozwala nadać dodatniego wyniku leksykalnego |

Oścież i bezcen po A mogą uzyskać dodatni wynik jednego warunku po właściwym przeglądzie; bin może otrzymać udokumentowaną grową odmowę konkretnego użycia. Finalnych delt list nie deklarujemy: inne warunki, pozostałość i pełna macierz nadal otwarte. A nie nadaje automatycznego werdyktu stu internetowym etykietom frazeologicznym; B pozostawia ich role obserwacyjne.

## Przyczyna bramki
[AGENTS.md](../../../../../../AGENTS.md): „Decyzje zmieniające skład słownika lub kryteria dopuszczalności omawiamy z użytkownikiem przed ich wdrożeniem”. Wcześniejsze zgody obejmują autorską dokumentację i jawne relacje mieszkańców, a nie ten ogólny próg opisów artykułu. [maister-implementation-plan-executor](/Users/robmar/.codex/plugins/cache/maister-plugins/maister-codex/2.2.3/skills/maister-implementation-plan-executor/SKILL.md): „ask the equivalent concise question in the final response and pause”. Bramka dotyczy konkretnego rozszerzenia dowodu, nie zgody na dalszą pracę lub kontakt.

## Odroczenie przez użytkownika

2026-10-05T20:26:52Z — „odlozmy ten ruch, zeby nie zanieczyscic losowymi danymi naszej bazy”. To odroczenie propozycji, nie zatwierdzenie A/B. Dotychczasowe dopuszczone dane i reguły pozostają; nowego rozszerzenia nie wdrożono. Obserwacje są wyłącznie historią research, nie wejściem kwalifikacji. Nie wracamy do tej bramki bez ponownego podjęcia tematu przez użytkownika.
