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
- Użycie po 2020 potwierdzono punktowo w rundzie 2; udział rzeczywistych archaizmów w całej populacji pozostaje nieustalony.

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

## Rozszerzenie w rundzie 2

Plan: [expanded-plan.md](expanded-plan.md). Wszystkie osiem torów wykonano. Spis i siatka mają pełne pokrycie ilościowe, ocena semantyczna pozostaje próbkowa.

| Tor | Artefakt i pokrycie |
|---|---|
| Pełny spis i wrażliwość | [census-1580.json](../analysis/findings/round2/census-1580.json), [metrics.json](../analysis/findings/round2/metrics.json): 1580 grup, 30 par progów, 10 wariantów |
| Warstwy i kontrole | [sample-forms.json](../analysis/findings/round2/sample-forms.json): 155 form; [current-override.json](../analysis/findings/round2/current-override.json) i [controls.json](../analysis/findings/round2/controls.json): 40+40 |
| Publiczny KWJP½M | Skan całych 5500 plików; 492 fragmenty z dowolnym z 389160 kandydatów; z nich 107 dotyczy 4559 dodatków lematowych. Przeczytano wszystkie 107, w tym 106 z formami z podzbioru bez arch. |
| Pełna wyszukiwarka KWJP | [Manifest 257 zapytań](../analysis/findings/round2/kwjp-live-inventory.json), [643 odczytane konkordancje](../analysis/findings/round2/live-review.json); wliczone zaakceptowane formy rodzin, np. familii/konfuzji/preferowany/wynegocjować/ekscytacja |
| SGJP i WSJP | [40 haseł / 47 artykułów](../analysis/findings/round2/sgjp-review.json); [macierz 24 kontroli WSJP](../analysis/findings/round2/dictionary-evidence.md) z adresami i własną oceną |
| Kwalifikatory | Czytnik SGJP oraz przypięty eksport Kuźni 61daf78; ustalono utratę poziomu etykiety i wskazano ograniczenia historii redakcyjnej |
| Aktualność | ARiMR 2025, Senat 2024, UJ 2024, IPN 2025; odczytane źródła pierwotne, punktowe kontrprzykłady |
| Synteza i kontrola | [Raport](../outputs/research-report.md), [walidacja](../analysis/findings/round2/validation.json), HTML i dashboard |

Wyszukiwarka KWJP początkowo nie pokazywała wyników przy niepełnych parametrach; prawidłowe zapytanie zawiera `per_page=10` i `chosen_corpora=balanced`. Sandbox odmawiał DNS w skrypcie; autoryzowane ponowienie zadziałało. Czytnik SGJP wymagał pełnego `query_params`; pusty zwracał 502. Nie uznano tych błędów za dowód braku formy. Końcowe 257 odpowiedzi KWJP mają rozpoznany licznik, w tym 49 z zerem.

Publiczne manifesty zawierają identyfikatory, metryki, bibliografię, hashe i własne notatki. Pełne odpowiedzi czytnika i konkordancje są lokalnym cache, nie częścią publikowanego repo. Zapis SGJP służy kontroli badawczej; nie zmienia wcześniejszego statusu potencjalnego wejścia metadanych do generatora.

## Rozszerzenie w rundzie 3

Plan: [candidate-assessment-plan.md](candidate-assessment-plan.md). Wszystkie pięć kategorii ponownie pokryto; źródła z poprzednich rund zachowano. Dostęp 2026-10-12.

| Kategoria | Uzupełnienie |
|---|---|
| Kod | `pop.py`: odczyt `_lexicon`, `units`, `member_units`, `measure`, `threshold`, `prune_members`, `forms_for`, `frequent_guard`; `constructions.py`: składniki i reguły istniejących konstrukcji; `schema.sql`: pochodzenie analizy |
| Dokumentacja | Przyjęty kierunek, zasady STANDARD, ADR-006 i ADR-007; brak zmiany warunków użycia NKJP lub przyjęcia nowego źródła produkcyjnego |
| Konfiguracje/testy | Przypięte `pop.json` i `pop-sources.json`; odczyt testów progów/remisów/homonimów, 3 odpowiednie istniejące testy POP uruchomione poprawnie |
| Dane | Wszystkie 290 zależnych przyjęć i ich analizy; macierz 404/3364; pełne historyczne analizy badanych rodzin; dokładne odtworzenie opublikowanych POP/POP0; dwa scenariusze i izolowana kontrola `dag` |
| Źródła pierwotne | 501 wyszukań SGJP, 207 pełnych tabel, 309 sond KWJP, 730 ręcznie ocenionych konkordancji; celowe uzupełnienia WSJP i źródło zawodowe |

Manifesty, oceny i pomiary: [katalog rundy 3](../analysis/findings/round3/). 501 odpowiedzi SGJP i 309 sond KWJP zakończono bez błędu dostępu. Początkowe błędy DNS w sandboxie rozwiązano jawnym ponowieniem z dostępem sieciowym. Nie wyłączono żadnego wymaganego toru.

Celowe uzupełnienia:
- [WSJP — gawiedź](https://wsjp.pl/haslo/podglad/75561/gawiedz), [jagnięcina — mięso](https://wsjp.pl/haslo/podglad/57581/jagniecina/5160693/mieso), [pryncypium](https://wsjp.pl/haslo/podglad/87307/pryncypium), [szuwar](https://wsjp.pl/haslo/podglad/72148/szuwar): obie liczby; uwaga „zwykle” opisuje przewagę użyć, nie zakaz odmiany.
- [WSJP — surdut, marynarka](https://wsjp.pl/haslo/podglad/71964/surdut/5193113/marynarka): dawny przedmiot, bez etykiety dawnego wyrazu; przykłady i pełna odmiana. Pierwsza próba odczytu podstrony nie powiodła się, poprawny adres znaleziono w wyszukiwaniu i odczytano.
- [WSJP — edukować](https://wsjp.pl/haslo/podglad/98423/edukowac/5239639/w-jakiejs-dziedzinie), [preferować](https://wsjp.pl/haslo/podglad/39378/preferowac), [wynegocjować](https://wsjp.pl/haslo/podglad/21191/wynegocjowac), [moderować czat](https://wsjp.pl/haslo/podglad/78447/moderowac/5196592/czat): współczesne znaczenia i odpowiednie części odmiany.
- [WSJP — negocjator](https://wsjp.pl/haslo/podglad/21205/negocjator), [negocjacja](https://wsjp.pl/haslo/podglad/21192/negocjacja): kontrola współczesnego znaczenia i liczby pojedynczej; odczyt nie oznacza automatycznego dodania całej rodziny do propozycji.
- [WSJP — warzyć piwo](https://wsjp.pl/haslo/podglad/97671/warzyc/5238423/piwo): współczesne znaczenie przechodnie. [Zafrasować](https://wsjp.pl/haslo/podglad/88943/zafrasowac) i [zafrasować się](https://wsjp.pl/haslo/podglad/92641/zafrasowac-sie): także WSJP kwalifikuje jako przestarzałe; konflikt pozostaje otwarty.
- [Polskie Stowarzyszenie Aktuariuszy — aktuariat](https://actuary.org.pl/psa/aktuariat/): pierwotne dzisiejsze użycie nazwy zawodu. Nie jest osobnym źródłem fleksji ani poradą dotyczącą wykonywania zawodu.

Pełne konteksty przeczytane w rundzie 3 pozostają lokalne. Metryki 2021/2022 mogą opisywać wydanie tekstu pierwotnie wcześniejszego; nie rozszerzamy deklarowanego okresu KWJP. Jedna osoba oceniająca, dobór celowy. Zależność WSJP/SGJP i anotacji korpusu ujawniono w raporcie. Podgląd CUA był niedostępny w poprzedniej rundzie; HTML nadal wymaga uczciwego rozdziału kontroli strukturalnej od wizualnej.
