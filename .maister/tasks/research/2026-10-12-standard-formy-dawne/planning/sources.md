# Rejestr i pokrycie źródeł

## TL;DR
Wszystkie pięć kategorii dowodów zostało sprawdzonych.
Bazą kodu jest commit `1b6f4b66803f312bffea3b32593c202faa0eea40`, zgodny z main GitHuba przy odczycie.
Liczby pochodzą z przypiętego wydania; kontrola znaczeń jest próbkowa.

## Key Decisions
- Dane nie zmieniają generatora. SJP.pl pozostaje wyłącznie miarą.
- Wyniki zawierają własne analizy i metryki, bez surowego NKJP i tekstów korpusu.

## Open Questions / Risks
- Nie badano całych konkordancji KWJP100 ani wszystkich znaczeń 3364 kandydatów; przeprowadzono zaplanowany przegląd próbki.
- Użycie po 2020 oraz udział rzeczywistych archaizmów w całej populacji pozostają nieustalone.

## Pokrycie
| Kategoria | Odczytane źródła i rola | Status |
|---|---|---|
| Kod | policy.py, decisions.py, explain.py, pop.py, schema.sql; przyczyna i jednostka oceny | sprawdzono |
| Dokumentacja | AGENTS, README, INDEX, decyzje rundy 4 i 7, ADR-006/007, mapowanie KWJP, dotychczasowy audyt próbek | sprawdzono |
| Konfiguracja i testy | sources.json, pop-sources.json, pos-map.json, historyczne warunki polityki, tests.test_round4_sjp_fixes | sprawdzono; 6/6 testów |
| Przypięte dane | baza v30/LL-PL v29, listy KWJP, NKJP 1grams, benchmark, KWJP½M | sprawdzono; hashe i sondy |
| Źródła pierwotne online | SGJP, KWJP/IPI PAN, autorzy NKJP, WSJP/IJP PAN, wiki z ticketu | sprawdzono |

## Rejestr szczegółowy
Dostęp do źródeł: **2026-10-12**.
- [Zgłoszenie #4](https://github.com/robmar-net/literaki-slownik/issues/4): pytanie i oczekiwane wyniki; odczytano body i komentarze (brak wcześniejszych).
- [SGJP — oznaczenia](https://sgjp.pl/oznaczenia/) i [instrukcja](https://sgjp.pl/instrukcja/): interpretacja nazw etykiet, odrębność nazw i znaczeń.
- [KWJP — opis](https://kwjp.pl/overview): zakres 2011–2020, gatunki i braki reprezentacji.
- [KWJP — opis list](https://kwjp.pl/lists/doc/about/): automatyczna anotacja, F≥5 globalnie, dyspersja/ARF.
- [IPI PAN kwjp100-varia](https://github.com/ipipan/kwjp100-varia): dane CC BY 4.0; w pomiarach commit `26d82bd8b906dfed1cfcf8f903b1650b56daeabf`.
- [KWJP½M](https://github.com/ipipan/kwjp100-varia/tree/26d82bd8b906dfed1cfcf8f903b1650b56daeabf/KWJP%C2%BDM): 5500 plików próbek; SHA256 `aedad77022508fe10d0d537e6a082884b8e7a97d4836a184ff744a5261db55b1`, git blob `bed4e3e2ca289db6da8a65cab183e007f01e3e35`, zgodny z wcześniejszym przypiętym audytem.
- [NKJP n-gramy](https://zil.ipipan.waw.pl/NKJPNGrams): reprezentacja tokenów i deklaracja CC BY; strona ostatnio edytowana 2021-01-26. SHA256 1grams `73af49094621b2f86b594beba783c14aee8c8212f1aff3d61f281ab5d99e3dc9`.
- [WSJP — kontrola znaczeń](../analysis/findings/external-evidence.md): dokładne adresy haseł desperacja, niezbędnik, familia, odzienie, surdut, archaizm; ponadto [kalkulator](https://wsjp.pl/haslo/podglad/18446/kalkulator/1895592/bezwzgledny) i [osiem](https://wsjp.pl/haslo/podglad/37492/osiem). Tylko odczyt do badania, bez importu.
- [Wiki braków SJP](https://github.com/robmar-net/literaki-slownik/wiki/Brakujace-slowa-SJP.pl): po błędzie cache web odczytano [surową stronę](https://raw.githubusercontent.com/wiki/robmar-net/literaki-slownik/Brakujace-slowa-SJP.pl.md). Benchmark `tmp/benchmark/sjp-missing-v29.json`, SJP SHA256 `2a593404f2f3f31df42f461cfc8d365e4b426bc73563fe9925702096bfdc70b8`.
- Baza i lista STANDARD: pełne hashe w [measurements.json](../analysis/findings/measurements.json), zgodne z config/generator/pop-sources.json. Weryfikacja przykładów: [validation.json](../analysis/findings/validation.json).

## Dostęp i wyłączenia
Brak `.codex/agents/` w repo i workspace: specjalistyczne etapy wykonano w głównym kontekście. Workspace nie miał konfiguracji i indeksu Maister; repo słownika je ma i z nich skorzystano. Przejściowy błąd sieci GitHub usunięto ponownym autoryzowanym odczytem. Nie pozostała wymagana kategoria źródeł zablokowana przez dostęp.
Użytkownik wykluczył dalszy workflow implementacyjny. Reguły, wydanie i wiki pozostają bez zmian. Pełny audyt wszystkich znaczeń jest dalszą pracą zależną od uzgodnienia kryterium, nie zadeklarowanym wynikiem tego researchu.

## Atrybucje
KWJP: IPI PAN, autorzy i cytowanie według kwjp.pl/overview, CC BY 4.0 dla publicznych danych repo; własne pomiary i oceny. SGJP: autorzy i warunki według repozytoryjnego ATTRIBUTIONS.md. NKJP: Zespół Inżynierii Lingwistycznej IPI PAN / Narodowy Korpus Języka Polskiego, „N-grams from the balanced subcorpus of the National Corpus of Polish”, CC BY — wersja nieokreślona; szczegółowe obowiązujące atrybucje i opis zmian w [ATTRIBUTIONS.md](../../../../../ATTRIBUTIONS.md). Autorzy źródeł nie popierają tego projektu; nie redystrybuujemy surowych danych NKJP.
