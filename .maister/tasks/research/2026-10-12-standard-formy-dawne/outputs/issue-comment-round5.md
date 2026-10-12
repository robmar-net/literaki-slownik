# Runda 5: czy granica POP jest we właściwym miejscu?

## TL;DR

Zbadano 27 wariantów na dwóch STANDARD, dodatkowe siatki dyspersji i 300 haseł z kolejnych pasm.
**Koryguję rekomendację z rundy 4: poprawność algorytmu nie uzasadnia zachowania limitu 60 tys.**
Większy limit dodaje sensowne słowa, lecz badanie nie wskazuje jednej właściwej granicy 70k, 80k ani 0,05.
To wyłącznie research. Nie zmieniono list, reguł, konfiguracji ani wydania.

## Key Decisions

- Rekomenduję **jawne wymagania dowodowe i rozmiar wynikowy**, zamiast traktować liczbę miejsc jako uzasadnienie popularności. Dokładna reguła pozostaje do omówienia.
- Oddzielić **stabilizację składu od poszerzenia**. Stały próg obecnego cięcia usuwa zbadane wypychanie słów, bez zmiany bazowego POP; nie potwierdza jednak trafności tej granicy.
- Nie rekomenduję doraźnego 60 025 ani zatwierdzenia 70k/80k/0,05 jako optimum. Dodatki STANDARD, cofnięcia i metoda POP pozostają osobnymi decyzjami.

## Open Questions / Risks

- Trzeba uzgodnić, jak szeroki ma być POP: także słowa szkolne, dziedzinowe, książkowe i regularne derywaty czy węższy zasób ogólnego użytku. Klasa „ograniczone” nie znaczy „odrzucić”.
- Korpusy mierzą użycie w swoich tekstach, nie znajomość przez graczy. Brak opublikowanego KWJP nie oznacza braku współczesnego użycia.
- Wysoka pewność pomiarów, średnia ocen językowych. Osobne tory tego samego modelu, dobór kontekstów i ograniczenia dostępu nie stanowią niezależnego badania ludzi.

## Wyniki liczbowe

Limit liczby działa przed przycięciem członków grup; nie jest docelową liczbą zachowanych leksemów.

| Wariant | Formy przy obecnym STANDARD | Formy po proponowanych +2382 STANDARD | Dodatki / ubytki po zmianie STANDARD |
|---|---:|---:|---:|
| Limit 60k | 1 227 250 | 1 227 192 | +2372 / −2430 |
| Limit 70k | 1 424 934 | 1 427 316 | +2382 / 0 |
| Limit 80k | 1 636 683 | 1 639 065 | +2382 / 0 |
| Stały próg obecnego 60k | 1 227 250 | 1 229 622 | +2372 / 0 |
| Stały próg 0,05 | 1 443 064 | 1 445 446 | +2382 / 0 |

Stały próg obecnego cięcia to score ≥ −1,042878629. Wariant 0,05 oznacza score ≥ log10(0,05), nie dosłowną częstość każdego słowa w jednym korpusie. Warianty te zmieniają także przycinanie: własna punktacja zamiast własnej rangi; zachowują istniejące wyjątki grupowe. Stabilność pokazano dla tej konkretnej zmiany, bez gwarancji przy nowych źródłach i grupowaniu.

## Co pokazały słowa

Oceniono wszystkie 300 haseł: 104 ogólne, 170 ograniczone rejestrem/tematem, 9 marginalnych, 2 błędne dopasowania i 15 niepewnych. Odczytano **632 wyniki z 386 dokumentów** spośród 1342 pobranych konkordancji. W powtórnej kontroli 30 ocen zgodne były 22 klasy; różnice zachowano jawnie.

W próbach po 40 słów z pasm 60–70k i 70–80k ocen ogólnych było **9 i 10**. Nie ma skoku uzasadniającego dokładnie 70k. Kontrprzykłady:

- **pomiaukiwać, podrzemać, szambiarka** mają zwykłe współczesne konteksty i wchodzą przy 70k;
- **aroniowy, nepotyczny** wchodzą przy 80k, lecz pozostają poza progiem 0,05;
- **odbąknąć, bezołowiówka** mają poprawne konteksty, ale pozostają poza 80k i 0,05;
- **siejba** wchodzi przy 70k i 0,05 mimo dawnego rejestru; **uherski** przy 80k ma w odczytanej próbce wyłącznie czeską nazwę miejscową jako dowód.

Brak własnego oryginalnego wiersza KWJP dotyczy **51%** nowych podstaw w paśmie 60–70k i **85%** w 70–80k. Wybór coraz bardziej zależy więc od NKJP i reguł braków. To nie odsetek złych słów. Filtry dyspersji też nie dały gotowego rozwiązania: dwa warianty o identycznym pokryciu różniły się o **345 639 form** zależnie od obsługi braków.

## Wniosek i trwały zapis

Nie zalecam dalszego poszerzania przypadkowej próbki przed rozmową o kryterium. **Najpierw uzgodnijmy zakres POP i akceptowane rodzaje dowodów.** Samo podniesienie limitu lub zamiana go na arbitralny próg nie rozwiązuje rozpoznawania sensu i współczesnego użycia.

Wszystkie liczby, przykłady, źródła, hashe i sposób odtworzenia: [raport rundy 5](https://github.com/robmar-net/literaki-slownik/blob/ed6fbb00a5a331aaf07a2d8bf446517e7f8d4fa2/.maister/tasks/research/2026-10-12-standard-formy-dawne/outputs/pop-calibration.md). [Niezależna kontrola](https://github.com/robmar-net/literaki-slownik/blob/ed6fbb00a5a331aaf07a2d8bf446517e7f8d4fa2/.maister/tasks/research/2026-10-12-standard-formy-dawne/analysis/findings/round5/measurement-review.md) potwierdziła pomiary; 25 istniejących testów POP przeszło. Kontrola nie odbudowywała niezależnie całego grafu i morfologii.

Próby otwarcia objęły 55 uzupełniających źródeł: 40 odczytanych fragmentów, 15 ograniczeń dostępu. Zamrożone klasy nie ukrywają późniejszych korekt źródłowych — opisano je w raporcie, zwłaszcza przy bojownicy, przedryndać i szampitrze. Nie są podstawą wyboru progu. Pełne teksty korpusów i surowy NKJP nie zostały opublikowane.
