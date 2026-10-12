# Maister Research — ocena kandydatów i wpływ na listy

## TL;DR
Według uzgodnionej zasady przygotowano **propozycję 2382 nowych form ze 110 rodzin**.
Sprawdzono wszystkie 290 obecnych przyjęć zależnych od wyjątku, 730 dodatkowych konkordancji i 207 pełnych tabel SGJP.
Wynik symulacji: STANDARD +2382; POP +2372 i −2430, czyli **netto −58**; POP0 +481.
To nadal research. Paczka, cofnięcia i wdrożenie nie są zatwierdzone; wyniki przekazujemy do omówienia.

## Key Decisions
- Współczesne znaczenie uzasadnia właściwą współczesną odmianę, także rzadką. Nie dobierano nowego progu częstości.
- Propozycja obejmuje **997 z wcześniejszych 3364 kandydatów oraz 1385 spoza tej paczki**. Ocena całych rodzin, zwłaszcza czasowników, ujawnia formy pominięte przez próg lemma+POS.
- Nie przenosimy dowodu na dawne końcówki, inny homonim ani cały rzeczownik zachowany tylko w zwrocie.
- Główny pomiar zachowuje obecne przyjęcia. Ich ewentualne cofnięcie zbadano osobno.

## Open Questions / Risks
- **2367** wcześniejszych kandydatów nie trafiło do propozycji. Nie oznacza to zbiorowego odrzucenia. Macierz 404 grup jest pełnym spisem statusów i zakresów dowodów, nie pełną ekspertyzą wszystkich znaczeń.
- Ocena językowa pochodzi od jednego badacza; pewność średnia. Pomiary na przypiętych danych mają wysoką pewność.
- Skutki rankingu POP wymagają omówienia przed wdrożeniem. Sama liczba dodatków STANDARD nie opisuje zmiany list gry.

### Konkretna paczka

Przykłady dodatków: `desperacja`, `ekscytacją`, `niezbędnik`, `sołtyska`, `sztaluga`, `szuwar`, `przechwałka`, `pryncypium`, `aktuariusz` oraz właściwa odmiana `edukować`, `moderować`, `wynegocjować`.

Nie wchodzą m.in. `desperacyj`, `atencyj`, `dokumenta`, `klasztora`, `wywre`, `umorach`, `premiów`, `zasłonionemu`, `mielszy`. `Zafrasować` pozostaje konfliktem rejestru, a `spękany` wymaga rozstrzygnięcia przypisania do właściwego leksemu.

[Lista 2382 form i zakresy rodzin](https://github.com/robmar-net/literaki-slownik/blob/67c06ecdef4ef5dac9734fa9d0acbe557c45eaa5/.maister/tasks/research/2026-10-12-standard-formy-dawne/analysis/findings/round3/proposal.json).

### Kontrola obecnego wyjątku

Dla **bad, dag, dyr, reż, sek, sie, sui, um, moko, wiosenno, świąteczno, tem** po 10 przeczytanych kontekstów nie daje dowodu przyjętych analiz. Występują tam skróty, obcy język, literówki albo człony złożeń. Nie jest to dowód nieistnienia tych słów ani kompletna ocena wszystkich trafień.

Przykładowo `dag` jest jednostką masy, a przyjęta analiza dotyczy dawnego `daga`; `moko` opisuje tatuaże, a nie wołacz od `moka`. Jednocześnie `ludzko` ma także poprawne samodzielne użycia. **Nie rekomenduję automatycznego usuwania całego wyjątku ani tej dwunastki.**

### Pełna symulacja POP

Odtworzono dokładnie obie opublikowane listy bazowe, po czym przeliczono ranking, grupy homonimów, całe bloki remisów i odmianę.

| Lista | Przed | Dodatki | Ubytki | Po |
|---|---:|---:|---:|---:|
| STANDARD | 3 090 194 | 2382 | 0 | 3 092 576 |
| POP | 1 227 250 | 2372 | 2430 | 1 227 192 |
| POP0 | 388 509 | 481 | 0 | 388 990 |

POP traci m.in. `cowboy`, `barion`, `kifoza`, `wakuola`, `anyżowy` i formy odmiany; pozostają w STANDARD. Powód: zmienia się granica rankingu przy limicie leksemów i niepodzielnych remisach. Po zmianie następny blok 116 leksemów nie mieści się w pozostałych 91 miejscach.

W wariancie cofnięcia 12 wątpliwych przyjęć POP0 traci dodatkowo odmianę `dekagram`. Izolowana kontrola potwierdza, że samo cofnięcie `dag` z bazowego STANDARD usuwa też te 10 form z POP0. To zależność rankingu, nie zmiana ich poprawności.

Obowiązujące straże 20 000 częstych form POP i 5000 POP0 przechodzą. SQL sprawdził wszystkie **7192 wskazane analizy** dodatków: jedyna odmowa to dawność. Baza pozostała identyczna; 3 istniejące testy POP przeszły.

**Rekomendacja:** omówić tę konkretną paczkę razem z ubytkami POP, a cofnięcia obecnych przyjęć rozpatrzyć osobno. Dalszy research kierować na wskazane granice znaczenia i rejestru.

[Pełny raport, metodologia, źródła, ograniczenia i wszystkie delty](https://github.com/robmar-net/literaki-slownik/blob/67c06ecdef4ef5dac9734fa9d0acbe557c45eaa5/.maister/tasks/research/2026-10-12-standard-formy-dawne/outputs/candidate-assessment.md). Kod generatora, kryteria, wydanie i wiki pozostają bez zmian. Ticket pozostaje otwarty.
