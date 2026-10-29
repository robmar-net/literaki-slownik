# ADR-012: Metoda `tematy-v2` i pierwsza fala tematów

## TL;DR
Dziewięć nowych tematów, każdy w osobnym pakiecie: zwierzęta, rośliny, medycyna i ciało, muzyka, kuchnia,
sport, matematyka, pogoda, grzyby. Warstwy liczymy jak dla morza ([ADR-010](ADR-010-tematy-v1.md)).
Zmienia się przegląd i schemat pliku tematu, więc metoda to `tematy-v2`.
T3 jest opcjonalne, `dodatki` leżą na górnym poziomie, wykluczenia lematów działają.
Operator miał oceniać tylko warstwy z `operator_warstwy` (T2, T3), a T1 agent. W fali 1 operator nie ocenił
R2; trafność T2 i T3 na bramce liczymy z ocen agenta ([Zmiana metody R2](#zmiana-metody-r2-2026-10-29)).
Bramka (operator, 2026-10-29): dalej — kuchnia, rośliny, zwierzęta, morze; popraw — grzyby, pogoda, sport,
matematyka, muzyka, medycyna. Bez wydania; v2 poza #12.
Morze zostaje `morze-v2`; przebudowa dała bajtowo tę samą listę.

## Kluczowe decyzje
- **Metoda `tematy-v2`.** Reguły warstw się nie zmieniają. Zmienia się przegląd (`operator_warstwy`,
  `nie_dotyczy`) i schemat tematu. Pakiet zbudowany według innych reguł musi mieć inną nazwę metody.
  Losowanie bez zmian: `tematy-quality-v1`, ten sam seed, 50 na warstwę.
- **Jeden pakiet na temat.** Kontrakt pakietu, checker i przegląd zostają jednotematowe.
- **T3 tylko w medycynie** (IATE `2841`, 342 wpisy T3). Bez `t3` budowa nie czyta IATE, a IATE nie trafia do tekstów
  ani do `inputs` manifestu.
- **Wykluczenia lematów i poddrzew bez trafienia dają kod 4.**
- **Granice tematów szerokie**, z decyzji operatora. Atomy `ogr.`, `psych.`, `wet.`, `farm.` i sport bez
  korzeni T2 dla gier, szachów i kart zatwierdził operator 2026-10-29.
- **Nazwy pakietów:** `data/work/tematy-<wersja tematu>-YYYYMMDD-{a,b}`.
- **Stare pakiety sprawdza checker z commitu `a633136`.** Nowy checker ich nie przyjmuje.

## Otwarte pytania / ryzyka
- **Bump metody** zmienia decyzję techniczną z
  [scope-clarifications.md](../../.maister/tasks/development/2026-10-29-12-tematy-fala-1/analysis/scope-clarifications.md)
  („metoda `tematy-v1`”). Reguły warstw zostają.
- **Małe tematy.** Testu słów oczywistych (0,70) nie przeszły grzyby, pogoda i sport. W v1 tematu nie ma
  dodatków D.
- **`t1_tak` z ocen agenta to słaba bramka.** Dla morza agent dał T1 46/50, a zgodność z operatorem
  wyniosła 20/57. Decyzja operatora.
- **Zgodność agent–operator** w fali 1 nie dotyczy (operator nie ocenił R2). Agent ocenia surowiej
  niż operator (morze, niżej).
- **Wspólny seed.** Wspólny lemat ma tę samą rangę w każdym temacie, więc próby tematów się korelują.

## Dlaczego `tematy-v2`
W `tematy-v1` operator oceniał 30 słów w każdej warstwie, a progi liczyły się tylko z jego ocen.
Przy 9 tematach to ok. 810 ocen. Operator zdecydował: ocenia tylko T2 (i T3 medycyny), ok. 300 słów.
T1 było trafne w trzech pomiarach. To zmienia regułę werdyktu, więc pakiet musi to nazwać w metodzie.

## Plik tematu
Klucze: `id`, `nazwa`, `wersja`, `t1`, `t2`, `dodatki`, `wykluczenia`, `diagnostyka`, `uwagi`
i opcjonalnie `t3`. Nieznany klucz to kod 2.
- **`t3`** ma dokładnie `{iate}`, w tym samym schemacie co w morzu. `t3.dodatki` to błąd.
- **`dodatki`** przechodzą z `t3` na górny poziom. Reguły jak w ADR-010 (warstwa D).
  `morze.json` zostaje `morze-v2`: wersja tematu opisuje treść listy, a lista się nie zmienia.
- **`wykluczenia`**: lista `{lemat, czesc_mowy, powód}`, może być niepusta. `czesc_mowy` to klasa tagu SGJP.
  Ta sama para w `dodatki` i `wykluczenia` to kod 2.
- **`diagnostyka.znaczniki_srodladowe`** są opcjonalne. Dozwolone tylko przy `t3` z kodem `4821`,
  bo tekst w `LIMITATIONS.md` opisuje tę dziedzinę. W tej fali ma je tylko morze.

## Wykluczenia
- **Lematy.** Budowa usuwa każdy leksem kandydata z `lemma_base` = `lemat` i klasą `czesc_mowy`,
  w każdej warstwie T1–T3. Dzieje się to przed dodatkami, formami i diagnostyką.
  Wykluczenie bez trafienia daje kod 4. `summary.json` ma klucz `wykluczenia`, a `raport.md` sekcję
  „Wykluczenia”, gdy lista jest niepusta. Checker sprawdza, że żaden wiersz TSV nie ma wykluczonej pary.
- **Poddrzewa** (`t2.wykluczenia_poddrzew`). Schemat bez zmian. Nowa reguła: synset nieosiągalny z korzeni
  po relacjach tematu (liczone bez wykluczeń) daje kod 4.

Reguła „bez trafienia” łapie literówkę i wykluczenie, które przestało działać po zmianie źródła.

## Teksty z odcinkami
Pliki `tematy-teksty/` mają dwa rodzaje odcinków: `<!--T3-->…<!--/T3-->`
i `<!--SRODLADOWE-->…<!--/SRODLADOWE-->`. Odcinek T3 zostaje tylko przy `t3`, odcinek SRODLADOWE tylko
przy `znaczniki_srodladowe`.
- **Reguła bajtowa.** W zachowanym odcinku usuwamy dokładnie bajty obu znaczników. Usunięty odcinek znika
  w całości, od `<!--X-->` do `<!--/X-->` włącznie. Spacje i nowe linie poza tym zostają.
- Znaczniki stoją tak, żeby oba warianty dawały poprawny tekst (punkt listy od `\n- `, zdanie ze spacją
  przed nim).
- Odcinek niezamknięty albo zagnieżdżony to kod 2. `@@SRODLADOWE@@` występuje dokładnie raz,
  wewnątrz odcinka SRODLADOWE.
- `LIMITATIONS.md` zmienia dwa punkty: T2 bez przykładów morza, T3 bez „T3 jest mała”
  (medycyna ma ok. 950 terminów IATE).

## Przegląd i werdykt
- **`operator_warstwy`** w `tematy.json`: niepusty podzbiór warstw próby bez powtórzeń, inaczej kod 2.
  Dla fali: `["T2", "T3"]`. `operator.strata` w próbie ma tylko te warstwy. `operator_per_stratum` = 30.
- **Progi** liczymy z ocen operatora dla warstw z `operator_warstwy`, a w pozostałych z ocen agenta.
  `t1_tak` pochodzi więc z ocen agenta. Progi z ocen agenta liczymy zawsze; „czeka” dostają tylko progi
  z warstw operatora i zgodność.
- **`nie_dotyczy`.** Temat bez `t3` ma `t3_tak` = `nie_dotyczy`. Ten status nie blokuje „dalej”.
  Temat z `t3` i pustą T3 daje `niespelniony`, żeby błąd konfiguracji był widoczny.
- Zgodność i kappa jak w ADR-010, na pozycjach ocenionych przez obu. Próg 0,80. Progi jak dla morza.

## Granice tematów
Decyzje operatora z 2026-10-29
([clarifications.md](../../.maister/tasks/development/2026-10-29-12-tematy-fala-1/analysis/clarifications.md)):

| Pytanie | Decyzja |
|---|---|
| Lemat w kilku tematach | zostaje w każdym |
| Taniec (`chor.`, taniec 1/2) | muzyka |
| Gry, szachy, karty (`gry`, `szach.`, `karc.`) | sport |
| Napoje, też alkoholowe | kuchnia |
| Wymarłe zwierzęta (`paleont.`) | zwierzęta |
| Gwara łowiecka (`łow.`) | nie |
| Grzybica (24994) | medycyna, nie grzyby |

Na bramce specyfikacji (2026-10-29, „Tak, audyt”) operator zatwierdził atomy SGJP `ogr.` (rośliny) oraz
`psych.`, `wet.`, `farm.` (medycyna). Nie dodajemy `biol.`, `biochem.`, `hydrol.` ani `łow.`.
Zatwierdził też sport bez korzeni T2 dla gier, szachów i kart: te dziedziny niesie T1.

Grzybica (24994) jest osiągalna z medycyny, a z grzybów nie, więc w grzybach jej nie wykluczamy.

## Wycięcia i pomiary
Operator zdecydował wyciąć zmierzony szum przed budową
([scope-clarifications.md](../../.maister/tasks/development/2026-10-29-12-tematy-fala-1/analysis/scope-clarifications.md)).
Pomiar 2026-10-29 na `plwn45-tematy.sqlite` (`aa65ad79…`); lematy jednowyrazowe, małe litery, kody 1–4.
Liczby wiążące poda raport budowy.
- **Zwierzęta: relacje `[11, 27]`** zamiast `[11, 25, 27]`. Przejrzałem wszystkie 269 celów krawędzi 25
  z domknięcia: części ciała, wytwory zwierząt (`angora`, `lanolina`, `edredon`) i gwara łowiecka
  (`farba`, `świece`, `chorągiew`). Żaden nie leży w domknięciu po 11, 27. 4 727 → 4 452 lematów
  (−275); odpadają m.in. `dziób`, `kieł`, `jelito`, `poroże`, `wymię`. Wykluczamy też poddrzewa
  6047 `człowiek 1` i 78303 `hominid 1`.
- **Medycyna: 5 poddrzew roślinnych** — 244560 `organ roślinny 1`, 38995 `narząd płciowy rośliny 1`,
  32240 `tkanka roślinna 1`, 4722 `nasiono 1`, 27813 `zarodnia 1`. 4 477 → 4 063 lematów (−414);
  odpadają m.in. `batat`, `bazylia`, `cytryna`, `groch`, `kawa`, `sporangium`. Komórki i biochemię
  ocenia R2.

Wykluczeń lematów w v1 tematów fali nie ma. Pojedyncze złe słowa usuwa v2 tematu po wspólnej ocenie.

## Nazwy pakietów
`data/work/tematy-<wersja tematu>-YYYYMMDD-{a,b}`, np. `tematy-grzyby-v1-20261029-a`.
Stary schemat `tematy-v2-…` mylił wersję tematu (`morze-v2`) z wersją metody.

## Regresja morza
Po zmianie kodu budujemy `tematy-morze-v2-YYYYMMDD-{a,b}` i porównujemy z `data/work/tematy-v2-20261029-a`:
- bajtowo równe `MORZE.txt.gz`, `MORZE.tsv.gz`, `ATTRIBUTIONS.md`, `TERMS.md`;
- `LIMITATIONS.md` różni się tylko punktami T2 i T3;
- `summary.json` równy po usunięciu `method`, `wykluczenia` i `werdykt.nie_dotyczy`;
- `sample.json`: równe `strata`, `items`, `unique_selected_units`, `overlaps`; `operator.strata` ma T2 i T3;
- a = b, checker PASS; 970 wpisów, 11 035 form, test 37/37.

**Wynik (2026-10-29): ZGODNE.** Cztery pliki bajtowo równe (`MORZE.txt.gz` `6e78d1ef…`,
`MORZE.tsv.gz` `83037db1…`), różnice tylko w plikach z listy, `summary.json` i `sample.json` jak wyżej,
970 wpisów, 11 035 form, test 37/37, bez błędów. W `summary.json` porównaliśmy też bez
`werdykt.czeka_na_ocene`, bo `t1_tak` już nie czeka. Dowód: [regresja-morze.json](../../.maister/tasks/development/2026-10-29-12-tematy-fala-1/verification/regresja-morze.json).

## Zmiana metody R2 (2026-10-29)
Operator przejrzał 9 stron R2, ale ocen nie zaznaczył: większość terminów musiałby sprawdzać
w wyszukiwarce. Decyzja operatora
([scope-clarifications.md](../../.maister/tasks/development/2026-10-29-12-tematy-fala-1/analysis/scope-clarifications.md),
„Zmiana metody R2”):
- trafność T2 i T3 na bramce liczymy z ocen agenta, z tymi samymi progami;
- zgodność operator–agent i kappa: „nie dotyczy”;
- checker się nie zmienia: bez ocen operatora T2, T3 i zgodność mają „czeka”. Wynik bramki liczy
  `analysis/zestawienie_fali.py` tą samą funkcją `verdict` (opis w [jakosc.md](../generator/jakosc.md#próbki-tematy-tematy-quality-v1)).

**Znane obciążenie.** Agent ocenia surowiej niż operator. Morze: operator T2 30/30, T3 27/27;
agent T2 21/50 („nie” 23), T3 9/27 („nie” 14); zgodność 20/57, κ 0. Bramka z ocen agenta może więc
odrzucić temat, który operator by przyjął.

**Wynik bramki z ocen agenta** ([gate-report.md](../../.maister/tasks/development/2026-10-29-12-tematy-fala-1/verification/gate-report.md)):
„dalej” dla kuchni, roślin i zwierząt; „popraw” dla pozostałych 7.

**Decyzje operatora** (2026-10-29, ostateczne): 4 dalej, 6 popraw.
- **dalej:** kuchnia (v2 bez: cytoplazma, sadzeniak, tyrozynaza), rośliny, zwierzęta, morze. Morze mimo
  „popraw” z ocen agenta: trafność z ocen operatora (T2 30/30, T3 27/27).
- **popraw:**
  - grzyby, pogoda, sport: dodatki D z brakujących słów oczywistych; grzyby też wykluczenia;
  - matematyka, muzyka: wykluczenia (oceny agenta „nie”);
  - medycyna: bez T3 (IATE) i bez 18 słów „nie” agenta.
- Bez wydania. Budowy v2 poza #12.

**Otwarte na v2** (przegląd kodu):
- **Wykluczenia a dodatki D.** `_exclude` (`literaki_slownik/tematy.py`) usuwa tylko leksemy T1–T3.
  Checker (`exclusions` w `scripts/check_tematy_package.py`) odrzuca każdy wiersz TSV, także D, z wykluczoną
  klasą. Przed v2 grzybów (dodatki i wykluczenia) trzeba ustalić, co obowiązuje.
- **Checker nie sprawdza tekstów pakietu niezależnie:** resztki `<!--` i `@@SRODLADOWE@@`, atrybucja IATE
  bez `t3`. Nie sprawdza też pól `summary.json`: `t3`, `srodladowe`, `nie_dotyczy`.
- **Odcinki tekstów** walidujemy dopiero przy zapisie pakietu. Mogłoby to być zaraz po `load_topic`.

## Stare pakiety
Pakiety `tematy-v1-*` i `tematy-v2-20261029-*` (metoda `tematy-v1`) sprawdza checker z commitu `a633136`.
Nowy checker zna tylko `tematy-v2` i ich nie przyjmuje. Nie utrzymujemy dwóch metod w jednym checkerze.

## Pochodzenie
Specyfikacja:
[spec.md](../../.maister/tasks/development/2026-10-29-12-tematy-fala-1/implementation/spec.md)
(W1–W15; audyt w
[spec-audit.md](../../.maister/tasks/development/2026-10-29-12-tematy-fala-1/verification/spec-audit.md)).
Powiązane: [#12](https://github.com/robmar-net/literaki-slownik/issues/12), [ADR-010](ADR-010-tematy-v1.md),
[ADR-011](ADR-011-zrodla-slowosiec-iate.md).
