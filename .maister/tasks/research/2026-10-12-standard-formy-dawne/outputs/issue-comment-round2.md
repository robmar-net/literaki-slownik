# Pogłębiony research Maister — runda 2

## TL;DR
Poszerzyłem badanie zgodnie z prośbą. Są mocne dowody, że reguła gubi żywe słowa, ale także że sam próg lematowy przywraca dawne odmiany i obce znaczenia.
Nie rekomenduję arbitralnego nowego progu. Trzeba rozdzielić współczesne znaczenie, współczesną odmianę i formy zachowane we frazeologizmach.
Wyniki są gotowe do omówienia; nie zmieniono polityki, kodu generatora ani list.

## Key Decisions
- Nadal tylko research; bez decyzji o wdrożeniu.
- SJP.pl nie wybierał kandydatów ani próbki.
- Zachowałem pierwszą rundę i jawnie skorygowałem jej uproszczenia.

## Open Questions / Risks
- Nie znamy odsetka rzeczywistych błędów w całym proponowanym przyroście. Jeden badacz, bez drugiego niezależnego przeglądu.
- Do uzgodnienia pozostaje dowód wystarczający do uchylenia etykiety dawności oraz zakres dopuszczonej odmiany.

### Zakres poszerzenia

- Pełny spis **1580 grup SGJP / 4559 nowych form**, w tym 404 grupy / 3364 formy po blokadzie `arch.`.
- **155 nowych form** z czterech warstw oraz **80 kontroli**: obecne przyjęcia i odrzucenia poza scenariuszem lematowym.
- **257 zapytań KWJP, 643 odczytane konkordancje**; osobno skan wszystkich 5500 plików KWJP½M i odczyt wszystkich **107** pasujących fragmentów. Te dwa zbiory mogą się pokrywać.
- **40 haseł SGJP / 47 artykułów**, porównania z WSJP, sprawdzenie formatu kwalifikatorów, źródła z lat 2024–2025.
- **40 sond** progów, gatunków i rozproszenia.

### Co wiemy znacznie lepiej

**1. Ryzyko lematowe jest policzone w całej populacji.** 1176/1580 grup daje wyłącznie dodatki oznaczone `arch.`. To zastępuje wcześniejsze 35/40 z małej próbki, ale nadal jest opisem oznaczeń źródła, nie odsetkiem niezależnie ocenionych archaizmów. Po blokadzie `arch.` zostaje 3364 form, w tym dawne warianty `dokumenta`, `klasztora`, `zasłonionemu` oznaczone inaczej.

**2. Brak wiersza w liście nie oznacza braku użycia.** 2587/3364 form nie ma publikowanego małoliterowego wiersza orth/all. W losowej próbie 50 takich form wyszukiwarka znalazła 7, m.in. `niezbędnikiem` i `konsultorzy`, ale także stylizowane `onemu`. Regularnej rzadkiej odmiany nie należy odrzucać wyłącznie za mały licznik.

**3. Konkretne znaczenie zmienia ocenę.** [Sołtyska w WSJP](https://wsjp.pl/haslo/podglad/120846/soltyska/5278353/pani-soltys) jako kobieta pełniąca urząd nie ma dawności; znaczenie żony sołtysa jest przestarzałe. Dzisiejsze użycie potwierdzają KWJP i ARiMR. Odwrotnie działa `wywrzeć`: SGJP rozdziela dawny czasownik o wygotowaniu się (`wywre`, `wywrzał`) od wywierania wpływu (`wywrze`, `wywarł`). Popularność drugiego nie może uzasadniać pierwszego.

**4. Problem występuje także w obecnych przyjęciach.** Dokładnie **290 napisów** zależy od dzisiejszego wyjątku częstościowego. Są tam zwykłe `edukować`, `ubezpieczyciel`, `wynegocjować`, ale także **sek**: przyjęty dawny rzeczownik z NF=301. W 10 obejrzanych kontekstach było 8 skrótów sekund i 2 urwane wyrazy. Żaden nie dowodzi tego rzeczownika. To wykazana słabość używanego dowodu, bez twierdzenia o przeczytaniu wszystkich trafień.

**5. Sam scenariusz 3364 form nadal jest za wąski.** Kontrole spoza niego wykazały żywe `aktuariusz`, `moderowana`, `upakowanych`, `pojazdowej`, `harcówki`, `spożytkuje`. Dobry wynik nie polega więc na zaakceptowaniu całej tej jednej paczki.

### Co koryguję względem pierwszej rundy

Książkowość, rzadkość i regionalność **już same w sobie nie wykluczają** w naszej polityce; nie trzeba ponownie podejmować tej ogólnej decyzji. `Przechwałka`, `sztaluga`, `szuwar` mają pozytywne dowody liczby pojedynczej. `Aliści`, `jakoż`, `nazad`, `trzykroć` mają również współczesne, nacechowane użycia autorskie — nie wszystkie są dawnymi cytatami. Poprawny przykład ograniczonej frazeologii to **na umór**, nie wcześniejsze do umoru.

### Wniosek do rozmowy

Rekomenduję oddzielną ocenę **współczesnego znaczenia i zakresu jego odmiany**. `Na umór` nie dowodzi swobodnego `umorach`; częste `desperacji` nie dowodzi dawnego `desperacyj`, ale przemawia za zbadaniem zwykłego `desperacja`.

Podwyższenie progu czy rozproszenia nie usuwa tego rozróżnienia. Nawet przy lemma+POS≥300 i blokadzie arch. pozostają 524 dodatki, z czego 454 bez publikowanego wiersza dokładnej formy. Nie wybrano progu ani listy zatwierdzonych dodatków.

**Pewność:** wysoka dla mechanizmu, liczb i konkretnych kontrprzykładów; średnia dla oceny rejestru. Materiał wystarcza do omówienia kryterium. Przed wdrożeniem nadal potrzebna będzie walidacja reguły według uzgodnionej definicji oraz ponowny pomiar STANDARD i POP/POP0.

[Pełny raport rundy 2, źródła i odtwarzanie](https://github.com/robmar-net/literaki-slownik/blob/main/.maister/tasks/research/2026-10-12-standard-formy-dawne/outputs/research-report.md) · [Pomiary, wszystkie notatki i kontrola bazy](https://github.com/robmar-net/literaki-slownik/tree/main/.maister/tasks/research/2026-10-12-standard-formy-dawne/analysis/findings/round2).
