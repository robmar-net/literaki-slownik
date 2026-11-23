# Dalszy plan projektu i runbook przekazania

## TL;DR

Stan na 2026-10-11: wydane LL-PL v29 (BROAD, STANDARD) i pop-v2 (POP, POP0; pop-v1 wycofane). Projekt buduje niezależne polskie słowniki dla Literaki Lounge: najpierw bazę dopuszczalności BROAD/STANDARD, następnie warianty poświadczone, zasoby popularnych słów i specjalizacje tematyczne. SJP.pl będzie późniejszym punktem odniesienia, dopiero po zamrożeniu porównywanych kandydatów.

Import oraz znaczna część mechaniki generatora działają. Nie istnieje jeszcze odebrane pełne wydanie. Najbliższa praca to domknięcie dowodów i mapowania językowego na zatwierdzonych wejściach; następnie pełna kwalifikacja, verify/export i dwa odtworzenia.

Ten dokument i powiązany ticket przekazują cały dalszy kierunek. Nie zastępują zatwierdzonej specyfikacji, decyzji użytkownika ani aktualnego stanu Maister. Kolejne etapy wymagają własnych specyfikacji i planów przed implementacją.

## Key Decisions

- Zachowujemy rozdzielenie: wpis źródłowy → kwalifikacja językowa → reguły gry → profil płytek → członkostwo w liście. Obecność słowa w źródle nie przesądza o dopuszczeniu do gry.
- Słowniki znajomości i tematyczne są podzbiorami wybranej, wersjonowanej bazy dopuszczalności. Nie zmieniają zasad gry ani listy obowiązującej przy stole.
- Źródłami obecnej budowy są przypięte SGJP i KWJP. Nie dodajemy losowych list ani domyślnych rozstrzygnięć brakujących danych.
- Zmiany kryteriów lub składu słownika wymagają wcześniejszego omówienia z właścicielem projektu: przykłady, alternatywy, dowody i przewidywany wpływ.

## Open Questions / Risks

- Nieukończona pełna semantyka `frag`, ortografia i klasy nazw mieszkańców. Poprawna mechanika nie zastępuje brakującego dowodu językowego.
- Nowe opisowe dowody z czytnika SGJP odłożono. Nie wracamy automatycznie do ich aktywacji; wcześniej zatwierdzone dowody pozostają w swoim dokładnym zakresie.
- Brakujące źródła, dane lub infrastruktura mogą pozostawić etap nieukończony. Nie zmniejszamy zakresu ani nie oznaczamy pełnego wydania przez samo opisanie ograniczeń.
- Nie ma wiarygodnego terminu zakończenia: największą niewiadomą jest domknięcie dowodów, a koszt dwóch pełnych buildów wymaga pomiaru.

## 1. Materiały do przeczytania i hierarchia

1. [AGENTS.md](../AGENTS.md): zasady repozytorium i decyzje wymagające rozmowy.
2. [Specyfikacja projektu v3](literaki-niezalezne-slowniki-prompt-v3.md): całe przedsięwzięcie, w szczególności rozdziały 3, 7–14. Rozdział 15 opisuje historyczny pierwszy audyt, nie obecny zakres implementacji.
3. [Raport i przekazanie zamkniętego research](../.maister/tasks/research/2026-10-04-audyt-zrodel-polskich-slownikow/outputs/research-handoff.md) oraz [rejestr decyzji](../.maister/tasks/research/2026-10-04-audyt-zrodel-polskich-slownikow/outputs/decision-log.md).
4. Bieżące zadanie: [stan Maister](../.maister/tasks/development/2026-10-04-generator-broad-standard/orchestrator-state.yml), [specyfikacja wykonawcza](../.maister/tasks/development/2026-10-04-generator-broad-standard/implementation/spec.md), [plan implementacji](../.maister/tasks/development/2026-10-04-generator-broad-standard/implementation/implementation-plan.md). Stan zapisano jako JSON mimo rozszerzenia `.yml`.
5. Najnowsze ustalenia: [kontynuacja na zatwierdzonych danych](../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/clean-inputs-continuation.md), [pozostała macierz](../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/remaining-matrix-review.md), [wdrożenie wspólnego dowodu](../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/shared-lexical-proof-implementation-review.md).
6. [Bieżące CLI](generator/cli.md), [odtwarzanie audytu](odtwarzanie-audytu.md), [warunki publikacji](generator/publikacja.md), [atrybucje](../ATTRIBUTIONS.md) i [dalsze kierunki minimum leksykalnego](literaki-prosty-jezyk-minimum-leksykalne-kierunki.md).

Pliki planu mają również historyczne dopiski. Przy wznowieniu czytać najnowsze decyzje i stan, zamiast traktować dawne „pending” lub dawny przykład wersji polityki jako aktualny werdykt. Rozbieżność dokumentacji trzeba wyjaśnić, nie rozstrzygać intuicyjnie.

## 2. Co jest gotowe, a co nie

- Zatwierdzono architekturę: Python 3.11+, biblioteka standardowa, SQLite, lokalny proces wsadowy, jedna baza na przebieg.
- Zamknięto audyt źródeł oraz grupy G1/G2: manifesty, CLI, pełny import. SGJP zawiera 7 458 520 kompaktowych interpretacji i 17 234 910 rozwinięć tagów. Importowane są wszystkie 13 aktywnych list KWJP.
- G3–G6 są częściowe: implementacja warstw ocen i konstrukcji, powiązania korpusowe, explain, raporty i deterministyczny dobór próbek. Polityka diagnostyczna v21 nie jest pełnym wydaniem.
- Przegląd 605 etykiet wykazał 604 ze znanym warunkiem; jedna niemapowana dotyczy dwóch interpretacji `ń`, mających niezależne powody odrzucenia. Znany pojedynczy warunek nie oznacza pełnej kwalifikacji analizy.
- Mechanika 70 źródłowych definicji hostów konstrukcji została sprawdzona; pełna kwalifikacja językowa/growa pozostaje odrębna.
- Ostatnia wykonana pełna suita: 247 testów generatora i 5 audytu, wszystkie przeszły (2026-10-08). To wynik historyczny, nie zastępstwo za testy przyszłych zmian.
- Maister: `development`, `phase_8`, zadanie `in_progress`; G7 ukończone 2026-10-08, G8–G9 oczekują. W głównym planie zaznaczono 15 z 36 pozycji (21 otwartych, stan 2026-10-08), lecz to nie miara czasu: dotyczą dużych etapów pełnych przebiegów i odbioru. Nie zamykać częściowych G3–G6 na podstawie liczby checkboxów.
- Dostępne komendy publicznego CLI: `inspect-sources`, `build`, `explain`, `verify`, `export`, `pop` (opis: `docs/generator/cli.md`). Wydanie LL-PL v29 przeszło verify K1–K10 i export. Nie ma zmiany działającej gry.
- POP/POP0 wydane 2026-10-11: [Release pop-v2](https://github.com/robmar-net/literaki-slownik/releases/tag/pop-v2). POP 1 227 250 form / 53 002 leksemów, POP0 388 509 / 13 896. Metoda: [ADR-007](adr/ADR-007-metoda-pop-v1.md) rew. 4 (limit 60 000 leksemów POP). Wycofane pop-v1 (rew. 3): POP 1 219 614 / 51 805, POP0 380 489 / 13 181.
- Nota 2026-10-12: kod ma metodę `pop-v3` ([ADR-008](adr/ADR-008-pop-v3-staly-prog.md)): POP = stały próg punktacji ≥ −1,042878629 zamiast limitu 60 000, POP0 ≥ 0,57370099 zamiast 20 000 (2026-10-13), tymczasowo do [#6](https://github.com/robmar-net/literaki-slownik/issues/6). STANDARD ma dostać 2 382 formy z wyjątków dawności #4 (pomiar na zamrożonym v30; nowy build w toku) ([opis](generator/wyjatki-dawnosci-standard.md)). Obie zmiany są robocze, dopóki nowy przebieg nie przejdzie odbioru i wydania; wydane pozostają LL-PL v29 i pop-v2.

## 3. Granice pracy i źródeł

- Nie zmieniamy reguł gry. Nie przejmujemy automatycznie polityki redakcyjnej SJP.pl.
- SJP.pl wyłącznie jako późniejszy benchmark; bez jego danych leksykalnych, wyjątków lub list różnic jako wejść budowy. OSPS i PoliMorf nie są wejściami. Odczyt zasad SJP.pl wykonany wcześniej na zlecenie nie jest benchmarkiem ani importem słów.
- NKJP (1-gramy) wolno użyć jako CC BY do rang POP: [ADR-006](adr/ADR-006-nkjp-cc-by-bez-wersji.md); sposób użycia: [ADR-007](adr/ADR-007-metoda-pop-v1.md). Pakiet nie zawiera surowego NKJP. NKJP nie dopuszcza słów do BROAD/STANDARD.
- Wikisłownik i podobne źródła społecznościowe oraz nowe opisowe dowody czytnika SGJP są odłożone. Brak kontaktu z innymi grupami: nie wysyłamy pytań do autorów źródeł.
- Zachowujemy homonimy, oryginalne pola i nierozpoznaną pozostałość znaczeń. Dowód konkretnego użycia nie kwalifikuje automatycznie wszystkich znaczeń rekordu.
- Brak w opublikowanej liście KWJP nie oznacza częstości zero ani błędności słowa; częstość pozostaje przy jednostce korpusu, bez wielokrotnego przypisywania homonimom. KWJP nie jest dowodem poprawności konstrukcji.
- Własny kod/konfiguracje: BSD-2-Clause; własna dokumentacja/raporty: CC BY 4.0. Źródła zachowują własne warunki. Osobno sprawdzić warunki każdej publikowanej bazy lub nowego zbioru.
- Istotne artefakty procesu commitujemy. Cache, surowe pobrania, bazy i pliki tymczasowe pozostają ignorowane. Piszemy po polsku; obce materiały zachowujemy z polską metryczką.

## 4. Dalsze etapy i zależności

### A. Dokończenie pierwszego generatora — bieżące zadanie

- [ ] **G3: dowody i pełna macierz.** Z zatwierdzonych danych wyprowadzić pozostałe przypadki, rozliczyć populacje, dowody i wpływ na całe słowa. Domknąć semantykę, fleksję/konstrukcje, ortografię i mapowanie KWJP. Zachować `unresolved` tam, gdzie brak rozstrzygnięcia; wskazać dokładnie brakującą informację i dlaczego jest potrzebna. Nie aktywować odłożonych opisów czytnika. Propozycje zmieniające skład lub kryteria przedstawić właścicielowi przed wdrożeniem.
- [ ] **G4: pełna kwalifikacja i konstrukcje.** Zintegrować udokumentowane reguły, dziedziczenie ograniczeń, agregację jednej spójnej analizy i `STANDARD ⊆ BROAD`. Odrzucenie homonimu nie usuwa niezależnej poprawnej analizy. Pełna macierz musi odpowiadać konfiguracjom i testom.
- [ ] **G5/G6: kompletne powiązania i diagnostyka.** Domknąć linki wszystkich kandydatów, statusy dostępności i niepewności, explain, wpływ filtrów i próbki jakości. Dobór próbki nie zastępuje jej rzeczywistego przeglądu.
- [x] **G7: verify/export.** Wdrożyć kontrolę K1–K10, związanie review i peer-run hashami, atomowy eksport do nowego celu, manifest, atrybucje i odmowę wydania niekompletnego wyniku. Sprawdzić awarie i ochronę wcześniejszych plików.
- [ ] **G8: dwa pełne przebiegi.** Najpierw utrwalić użyty kod; potem dwa nowe katalogi na tych samych przypiętych wejściach. Porównać listy i kanoniczną treść, nie fizyczne bajty SQLite ani czasy. Zmierzyć czas/RSS/rozmiar, wykonać explain i pełny przegląd próbki, odebrać K1–K10. Nierozstrzygnięcia wpływające na wymaganą kompletność blokują pełne wydanie.
- [ ] **G9 i pozostałe fazy Maister.** Uzupełnić sprawdzony runbook wydania, dokumentację i przekazanie; zachować obowiązkową bramkę wyboru weryfikacji w fazie 10 i przeprowadzić wymagany odbiór. Commit/push wszystkich istotnych zmian na koniec.

Kolejność zależna: G3 → G4 → G5 → G6 → G7 → G8 → G9. Plan dopuszcza niezależne techniczne prace importu/KWJP/explain przy rzeczywistej luce dowodowej; nie pozwala przez to pominąć G3 lub odbioru.

### B. Warianty poświadczone ATTESTED

- [ ] Przygotować osobną specyfikację i eksperymenty dla `ATTESTED-LEXEME` (poświadczenie leksemu, jego dopuszczalne formy) i `ATTESTED-FORM` (poświadczenie konkretnej formy, możliwa niepełna odmiana).
- [ ] Wskazać bazę BROAD albo STANDARD; przetestować niewielką rodzinę progów na rozkładach KWJP i próbkach jakości. Niejednoznaczne dopasowania raportować osobno.
- [ ] Jeśli warianty mają wejść do pierwszego porównania z SJP.pl, wybrać progi i zamrozić je **przed** tym porównaniem. Nie dopasowywać progów do zgodności z SJP.pl. NKJP tylko na warunkach ADR-006.

### C. Porównanie z SJP.pl i rekomendacja bazy

- [ ] Po odebraniu i zamrożeniu kandydatów wydzielić osobny proces benchmarku. Utrwalić kod, konfiguracje, źródła, listy i hashe; potwierdzić warunki konkretnego wydania oficjalnej listy SJP.pl przed pozyskaniem/użyciem.
- [ ] Porównać unikalne klucze w tym samym jawnym zakresie znaków, pisowni i długości. Raportować liczebności przed i po ograniczeniu zakresu, przecięcie, obie różnice, Jaccard i pokrycie z mianownikami.
- [ ] Wyjaśnić różnice z podziałem na długości, rodziny fleksyjne, anagramy, częstość i przyczyny kwalifikacji. Różnica zbiorów nie jest automatycznie błędem.
- [ ] Zbadać wpływ na grę na wspólnych stojakach, rozkładzie płytek, blankach i seedzie, w tym możliwość wyłożenia siedmiu płytek. Przy dostępnej infrastrukturze także te same pozycje planszy i punktację; udokumentować pochodzenie próby. Brak pomiaru oznaczyć, dostarczając projekt eksperymentu.
- [ ] Przedstawić tabelę kompromisów i rekomendację jednego lub dwóch wariantów. Nie zmieniać kandydatów w tym przebiegu. Ujawniony ogólny błąd można naprawić w nowej wersji z niezależnym dowodem i testem; nie kopiować brakujących słów z SJP.pl.

### D. Popularne słowa i stopnie wiedzy

- [ ] Zaprojektować `COMMONNESS` na częstości, ARF, 1-DP, gatunkach KWJP oraz pewności/dostępności mapowania. Porównać rangi/percentyle i transformacje, uzasadnić wagi i zbadać wrażliwość. Częstość nie jest bezpośrednim pomiarem znajomości przez człowieka.
- [ ] Zbadać **LEXEME**, **FORM** i **HYBRID**: odpowiednio całe dopuszczalne rodziny odmiany, konkretne formy i model mieszany. Punkty startowe 5k/10k/20k/40k/80k leksemów są do oceny, nie zatwierdzonymi poziomami produktu.
- [ ] Raportować liczby leksemów/form, kompletność odmiany i próbki przy progach. Zapewnić odtwarzalne, zagnieżdżone poziomy przy stałej konfiguracji; ewentualna losowa wiedza ma stały seed i trwałość, bez ponownego losowania przy każdym ruchu.

### E. Słowniki tematyczne i branżowe

- [ ] Wybrać tematy pilotażu, np. kulinaria, sport, botanika, informatyka lub kolej. Klasyfikować istniejące leksemy, potem dołączać dopuszczalne formy; dopuścić wiele tematów i zachować niepewność znaczenia.
- [ ] Porównać trzy metody: zalążki/sąsiedztwo w KWJP; korpus dziedzinowy względem odniesienia; pomocniczy klasyfikator semantyczny/LLM. Nowy korpus wymaga audytu warunków. LLM nie dodaje leksemów ani nie rozstrzyga dopuszczalności.
- [ ] Utrwalać modele/prompty/konfiguracje/wyniki i przeglądać próbki. Zasób tematyczny może uzupełniać podstawową wiedzę bota, a po scaleniu nadal musi być podzbiorem przypisanej bazy.

B/D/E można rozwijać na ukończonej, wersjonowanej bazie niezależnie od benchmarku C. Cały kierunek jest zachowany; szczegółowe wagi, progi, tematy i kolejność tych eksperymentów nie są jeszcze zatwierdzone.

### F. Przekazanie do aplikacji i późniejsze aktualizacje

- [ ] Dopiero po rekomendacji i osobnej decyzji przygotować zadanie integracji z Literaki Lounge, testy zgodności silnika, wydajność i plan wdrożenia/powrotu do wcześniejszego pakietu. Ten ticket nie upoważnia do zmiany słownika działającej gry.
- [ ] Aktualizacja źródeł lub polityki tworzy nowe wydanie i katalog; wymagane diffy decyzji/liczebności, ponowny odbiór i atrybucje. Nie podmieniać zamrożonych wyników.

## 5. Runbook wznowienia teraz

Wszystkie komendy uruchamiać z katalogu głównego `literaki-slownik`.

### Kontrola stanu i środowiska

```sh
git status --short
git rev-parse HEAD
python3 --version
python3 -m literaki_slownik --help
python3 -m literaki_slownik build --help
```

Przeczytać materiały z rozdziału 1, aktualny `orchestrator-state.yml` i zakończone artefakty. Przy użyciu Maister wznowić istniejące zadanie przez `maister-work`; nie zakładać nowego zadania zamiast utrwalonego stanu i nie omijać bramek. Nie resetować ani usuwać cudzych zmian.

### Wejścia i preflight

`config/generator/sources.json` przypina pliki źródeł, dowodów i konfiguracji. Cache nie jest w Git, więc świeży klon nie ma wszystkich wejść. Pozyskiwać dokładne wersje według rejestrów audytu i dokumentacji odtwarzania, nie „najnowsze” zamienniki. Nie uruchamiać skryptów zapisujących historyczne raporty bez sprawdzenia ich docelowych ścieżek.

SGJP: wydanie `20261018` (od LL-PL v31; wcześniej `20260823`), SHA256 `346bd7bc2695cb69c323de16c4c6d93afc514055fab96b458b8ead2523dae5be`. KWJP: commit `26d82bd8b906dfed1cfcf8f903b1650b56daeabf`; hashe poszczególnych list w rejestrach. Dokumenty dowodowe mają własne przypięcia. Jeśli któregoś pliku brakuje, zarejestrować konkretny brak; nie usuwać go z manifestu dla uzyskania sukcesu.

```sh
python3 -m literaki_slownik inspect-sources --manifest config/generator/sources.json --json
```

### Testy i diagnostyka

```sh
python3 -m unittest discover -s tests -p 'test_*.py'
python3 -m unittest discover -s scripts -p 'test_audit_sgjp.py'
```

Po zmianie uruchamiać właściwe testy i wymagane kontrole planu. Dla dokumentacji wystarcza kontrola linków/komend; nie powtarzać pełnej suity bez potrzeby.

Istniejący pełny import lokalny: `data/work/import-20261004-1302`. Jego fizyczny SHA256 SQLite zapisany w dowodach to `e0371fdf8b4be3187c864a2f2dcb5544d8445d99f79dbbe24c04bbaa5007f35e`. To historyczny import, nie pełny build v21 ani artefakt dostępny w świeżym klonie. Nie migrować/nadpisywać go dla nowych ocen.

Przykład odczytu, tylko jeśli ten katalog istnieje:

```sh
python3 -m literaki_slownik explain --run-dir data/work/import-20261004-1302 --word wznak --variant broad --json
```

Wyjaśnienie bieżącego kodu i utrwalone historyczne oceny mogą mieć różne wersje. `present` nie oznacza `accept`; `unresolved` nie oznacza błędnego słowa. Kod wyjścia 0 diagnostyki nie oznacza odebranego wydania.

### Porównanie z SJP.pl

SJP.pl to tylko miara. Wynik nie jest wejściem budowy i nie dopisujemy z niego słów.

1. Lista SJP.pl: zrzut słów z `lexicons/pl-sjp-20260820.dawg` repozytorium serwera (przejście `dawg.Open` + `ForEachEdge`, litery z `packs/pl.json`), jedno słowo w wierszu. Dziś: 3 240 471 słów, sha256 `2a593404…70b8`. Plik trzymaj poza repo.
2. Benchmark (liczby do strony wiki `Porownanie-z-SJP.pl`):
   ```sh
   python3 scripts/benchmark_sjp.py <run> <sjp.txt> tmp/benchmark/sjp-v<NN>.json
   ```
3. Najczęstsze brakujące słowa (strona wiki `Brakujace-slowa-SJP.pl`):
   ```sh
   python3 scripts/sjp_missing_top.py <run> <sjp.txt> tmp/benchmark/sjp-missing-v<NN>.json 2000
   python3 scripts/render_sjp_missing.py tmp/benchmark/sjp-missing-v<NN>.json > ../wiki-literaki-slownik/Brakujace-slowa-SJP.pl.md
   ```
   Kolejność: liczba wystąpień formy w KWJP (małe litery). Dla każdego słowa: lemat SGJP i reguła odrzucenia albo „brak w SGJP”. Czas: ok. 1 min. Skrypt wymusza indeks po słowie; bez tego SQLite skanuje wszystkie analizy dla każdego słowa (ponad 4 h).
4. Najczęstsze nasze słowa spoza SJP.pl (strona wiki `Slowa-spoza-SJP.pl`, kierunek odwrotny do p. 3):
   ```sh
   python3 scripts/sjp_extra_top.py <run> <sjp.txt> tmp/benchmark/sjp-extra-v<NN>.json 2000
   python3 scripts/render_sjp_extra.py tmp/benchmark/sjp-extra-v<NN>.json > ../wiki-literaki-slownik/Slowa-spoza-SJP.pl.md
   ```
   Kolejność jak w p. 3. Dla każdego słowa: lemat SGJP i źródło (SGJP albo nasza konstrukcja). Słowa bez wystąpień w KWJP idą na koniec, alfabetycznie. Renderer ukrywa nazwę innej gry słownej. Czas: ok. 40 s.

### Nowy przebieg i awaria

Para A/B buduje się na dysku roboczym (T7), pod nadzorcą, który sam wznawia pracę po zniknięciu dysku.
Opis poleceń i kodów: [cli.md](generator/cli.md#build-na-dysku-roboczym-i-wznawianie-22), decyzje: ADR-014..021.
`<wolumen>` to punkt montowania T7, `<nazwa>` to prefiks pary.

1. **Raz na wolumen:** `python3 scripts/init_work_volume.py <wolumen>/literaki-slownik/work`. Na T7 znacznik już jest
   (2026-11-23); powtórka kończy się kodem 4 i niczego nie zmienia.
2. **Utrwalić kod** (`git status` czysty w `literaki_slownik/`), potem para, odpięta od terminala:
   ```sh
   mkdir -p logs && LITERAKI_WORK_ROOT=<wolumen>/literaki-slownik/work \
     nohup scripts/build_pair.sh <nazwa> > logs/pair-<nazwa>.log 2>&1 & disown
   # → data/work/<nazwa>-<stempel>-a i -b (symlinki na T7), logi w logs/
   ```
   `build_pair.sh` sam uruchamia obu nadzorców pod `caffeinate -dimsu`. Bez `& disown` zamknięcie okna terminala
   wysyła SIGHUP: nadzorca przekazuje go buildowi i kończy pracę jego kodem (129), bez wznowienia.
   Para trwa ok. 13 h, zajmuje ok. 12 GB RAM i 2 × 22 GB na T7 (start wymaga ≥ 100 GB wolnego).
3. **Zniknięcie dysku:** build kończy się kodem 75, nadzorca czeka do 30 min i robi `build --resume` (najwyżej 3 razy).
   Strata: bieżący etap albo raport. Przebieg śledzić w `logs/<przebieg>.supervisor.log`. Build, który przez
   2 h nie zmienia plików przebiegu ani nie zużywa CPU (zawieszone I/O), nadzorca zatrzymuje (`stalled`):
   gdy dysku nie ma, czeka i wznawia jak po 75, a przy zdrowym dysku kończy kodem 4.
   Inny kod niż 75 zatrzymuje pracę: przeczytać `logs/<przebieg>.err`. 76 zły wolumen, 77 uszkodzona baza i 78 brak
   miejsca wymagają decyzji człowieka.
4. **Po restarcie maszyny** nadzorcę uruchamia się ręcznie, dla każdej strony osobno, odpiętego od terminala
   i pod `caffeinate` (inaczej wznowiona strona zaśnie razem z maszyną):
   ```sh
   nohup caffeinate -dimsu python3 scripts/build_supervised.py --manifest config/generator/sources.json \
     --run-dir data/work/<przebieg> > logs/<przebieg>.supervisor.out 2>> logs/<przebieg>.err & disown
   ```
5. **Odbiór:** przegląd próbek (K7), potem `verify` i od razu promocja A. Promocja kopiuje A na dysk wewnętrzny
   i kasuje B oraz kopię A na T7:
   ```sh
   python3 -m literaki_slownik verify --run-dir data/work/<A> --peer-run data/work/<B> --review <przegląd> --json \
     && python3 scripts/promote_run.py --run-dir data/work/<A> --peer data/work/<B>
   ```
   Przerwaną promocję wznawia to samo polecenie. Po skasowaniu B ponowny `verify` A wymaga nowej pary.
6. **Wydanie:** `export --run-dir data/work/<A> --output-dir NOWY` tylko na dysku wewnętrznym (przebieg na T7 → kod 5)
   → kontrola hashy pakietu → GitHub Release. Wzór: `llpl-v29`, opis w `docs/generator/publikacja.md`.
7. **Sprzątanie:** `python3 scripts/clean_work.py --work-root <wolumen>/literaki-slownik/work` wypisuje listę
   i niczego nie kasuje. `--apply` kasuje tylko przerwane, nieukończone i porzucone przebiegi na T7 oraz resztki
   startu starsze niż 24 h. Kompletna para czekająca na verify zostaje („kompletny, czeka na verify”).
   Przerwane kasowanie (`.<nazwa>.deleting`) dokańcza następne `--apply`. Stare wydania kasuje się
   wyłącznie po „tak” właściciela dla konkretnej listy: `--apply --delete-releases PLIK`.

Build bez `--work-root` (np. `--run-dir data/work/<nazwa>` na dysku wewnętrznym) działa jak wcześniej; przerwany
dokańcza `build --resume --manifest config/generator/sources.json --run-dir data/work/<nazwa>`.
Nie uznawać częściowego importu za dowód braku słowa.

## 6. Odbiór i utrzymanie ticketu

Ticket jest nadrzędnym planem przekazania, nie jednym PR-em. Dla B–F tworzyć zadania wykonawcze ze specyfikacją, zależnościami, kryteriami i linkami zwrotnymi; A kontynuować w istniejącym zadaniu Maister. Aktualizować statusy po rzeczywistym odbiorze, z linkiem do dowodów, commitów i wydań.

Minimalny odbiór A: wszystkie K1–K10, dwie powtarzalne pełne budowy, przejrzane próbki, explain i zamrożony pakiet. Odbiór dalszych etapów: odtwarzalne eksperymenty, raporty jakości/ograniczeń, własności podzbiorów i rekomendacja. Integracja z aplikacją wymaga odrębnego odbioru i decyzji.

Commitować większe spójne przyrosty, rzadko; na koniec commit/push wszystkiego należącego do zadania. Nie commitować surowych danych ani sekretów. Ten dokument nie zmienia obecnych kryteriów dopuszczalności, zakresu odłożonych źródeł ani statusu zadania Maister.
