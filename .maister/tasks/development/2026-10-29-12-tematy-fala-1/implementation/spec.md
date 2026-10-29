# Specyfikacja: TEMATY, pierwsza fala — 9 tematów (#12)

## TL;DR
Dziewięć nowych tematów, każdy w osobnym pakiecie a/b: zwierzęta, rośliny, medycyna i ciało, muzyka, kuchnia, sport, matematyka, pogoda, grzyby. Warstwy liczymy jak dla morza.
Najpierw uogólniamy kod: T3 opcjonalne, `dodatki` na górnym poziomie, działające wykluczenia lematów, teksty zależne od tematu. Operator ocenia tylko T2 (i T3 w medycynie).
Zmiana zasad przeglądu podbija metodę do `tematy-v2`. Po zmianie kodu morze-v2 przebudowane daje bajtowo te same `MORZE.txt.gz` i `MORZE.tsv.gz`.
Listy słów oczywistych powstają i zostają zamrożone przed pierwszą budową nowego tematu. Potem 18 budów, strony R2 (9 stron i strona zbiorcza), a na końcu wspólna ocena 10 tematów. Bez wydania.

## Kluczowe decyzje
- **Jeden pakiet na temat.** Kontrakt pakietu, checker i przegląd zostają jednotematowe. Pakiet wielotematowy zmieniłby wszystkie trzy.
- **Metoda `tematy-v2`.** Reguły warstw się nie zmieniają. Zmienia się przegląd: operator ocenia wybrane warstwy, `t1_tak` liczymy z ocen agenta, a przy temacie bez T3 `t3_tak` dostaje „nie dotyczy”. Te reguły leżą w `tematy.json` (`method.json` w pakiecie). Pakiet zbudowany według innych reguł musi mieć inną nazwę metody. Losowanie zostaje bez zmian (`tematy-quality-v1`, ten sam seed), więc próba agenta dla morza się nie zmienia.
- **`morze.json` zostaje `morze-v2`.** `dodatki` przechodzą z `t3` na górny poziom. Wersja tematu opisuje treść listy, a lista się nie zmienia, co potwierdza regresja bajtowa.
- **T3 tylko w medycynie (IATE 2841).** Bez `t3` budowa nie haszuje i nie parsuje IATE. IATE nie trafia wtedy do `ATTRIBUTIONS.md`, `TERMS.md`, `LIMITATIONS.md` ani do `inputs` manifestu.
- **Znaczniki śródlądowe tylko w morzu.** Pole jest opcjonalne. Dozwolone tylko przy `t3` z kodem `4821`, bo tekst w `LIMITATIONS.md` opisuje tę dziedzinę (D7).
- **Teksty warunkowe przez dwa znaczniki odcinków** (`<!--T3-->…<!--/T3-->`, `<!--SRODLADOWE-->…<!--/SRODLADOWE-->`) we wspólnych plikach `tematy-teksty/`. Nie robimy osobnych plików tekstów dla każdego wariantu.
- **Wykluczenia lematów działają.** Wykluczenie usuwa każdy leksem kandydata o tym `lemma_base` i klasie tagu, w każdej warstwie T1–T3. Wykluczenie bez trafienia daje kod 4. To samo dotyczy wykluczenia poddrzewa nieosiągalnego z korzeni.
- **Zwierzęta: relacje `[11, 27]`.** Cięcie części ciała z relacji 25 robimy przez pominięcie tej relacji. Przejrzałem wszystkie 269 celów krawędzi 25 z domknięcia. To części ciała, wytwory zwierząt (`angora`, `lanolina`, `edredon`) i gwara łowiecka (`farba`, `świece`, `chorągiew`). Odpada 275 lematów.
- **Medycyna: wykluczamy 5 poddrzew roślinnych.** Są to 244560, 38995, 32240, 4722 i 27813. Odpada 414 lematów, m.in. owoce, warzywa i nasiona. Komórki i biochemię ocenia R2.
- **Atomy SGJP z szerokimi granicami.** Dodajemy `ogr.` (rośliny) oraz `psych.`, `wet.` i `farm.` (medycyna). Nie dodajemy `biol.`, `biochem.`, `hydrol.` ani `łow.`. Operator zatwierdził te atomy na bramce specyfikacji (2026-10-29, „Tak, audyt”).
- **Sport bez korzeni T2 dla gier, szachów i kart.** Te dziedziny niesie T1 (`gry`, `szach.`, `karc.`). Zatwierdzone przez operatora razem z atomami (2026-10-29). Relacje zwierząt `[11, 27]` i poddrzewa medycyny wynikają z jego decyzji w `scope-clarifications.md`.
- **Grzybica.** Poddrzewo 24994 jest osiągalne z medycyny (przez `schorzenie 1`), a z grzybów nie. W grzybach nie trzeba więc go wykluczać.
- **Nazwy pakietów:** `data/work/tematy-<wersja tematu>-YYYYMMDD-{a,b}`, np. `tematy-grzyby-v1-20261029-a`. Stary schemat `tematy-v2-…` mylił wersję tematu z wersją metody.

## Otwarte pytania / ryzyka
- **Ograniczenie zakresu metody.** Bump do `tematy-v2` zmienia jedną decyzję techniczną z `scope-clarifications.md` („metoda `tematy-v1`”). Reguły warstw zostają te same co w v1.
- **Małe tematy** (pogoda T2 209 lematów, grzyby 351, matematyka 543) mogą nie przejść progu 0,70 słów oczywistych. W v1 nie ma warstwy D.
- **Zgodność agent–operator.** Dla morza wyszło 47/87. Szeroka instrukcja ma to poprawić, ale tego nie zmierzono.
- **Sport w T2 nie ma korzeni gier, szachów ani kart** (zatwierdzone). Brak pokaże test słów oczywistych.
- **`t1_tak` z ocen agenta to słaba bramka.** Dla morza agent dał T1 46/50, tuż nad progiem, przy zgodności z operatorem 20/57. Decyzja operatora; to ryzyko, nie błąd.
- **Wspólny seed.** Wspólny lemat ma tę samą rangę w każdym temacie, więc próby tematów się korelują. Warto o tym pamiętać przy macierzy nakładania.
- **Czas maszyny.** 20 budów i co najmniej 30 przebiegów checkera: 20 na pakietach i 10 z `--review` (w tym morze). Każdy przebieg dwa razy haszuje 22 GB `build.sqlite`. Szacunek: 2–3 h, tylko po kolei, w tle.
- **Nakład agenta:** ok. 950 ocen R2 (9 × (T1 do 50 + T2 50) + T3 medycyny 50), z powodem przy każdej. Szacunek: 9 sesji po ok. 100 pozycji. Do tego ok. 315 słów oczywistych.
- **Nakład operatora:** ok. 315 słów oczywistych i 300 ocen R2 na 9 stronach.

## Zmiany po audycie
Audyt: `verification/spec-audit.md` (0 krytycznych, 5 ważnych, 9 drobnych). Operator: „Popraw i do planu”. Wszystkie uwagi przyjęte.
- **W1** (przepięcie bez `evidence_sha256`): W9 kopiuje 4 pola z nowego szablonu i hash `SHA256SUMS`.
- **W2** (forma zamiast lematu): W10.2 sprawdza `lemma_base` z klasą i formę w STANDARD.
- **W3** (zgoda na skład list): zapisana w Kluczowych decyzjach. Operator zatwierdził atomy `ogr.`, `psych.`, `wet.`, `farm.` i sport bez korzeni gier w T2 (2026-10-29, „Tak, audyt”). Krok 0 niepotrzebny.
- **W4** (zdejmowanie znaczników): bajtowa reguła w W4; test w W8 przypina stare hashe, a `LIMITATIONS.md` porównuje z podmienionymi punktami T2 i T3.
- **W5** (budżet): ≥ 30 przebiegów checkera, ok. 950 ocen agenta (Ryzyka, Podejście techniczne).
- **D1:** bez commitu w trakcie serii budów (W12).
- **D2:** `srodladowe` = `null` bez znaczników, także w medycynie (W4).
- **D3:** progi z ocen agenta liczymy zawsze (W6).
- **D4:** oczekiwany werdykt morza w W9.
- **D5:** wiki: dochodzą `Slownik-STANDARD` i `_Sidebar`, klon lokalny (W15).
- **D6:** manifest wejść nadal z `iate`; od `t3` zależą tylko piny; temat czytany przed pinami (W7).
- **D7:** punkt T3 w `LIMITATIONS.md` bez „T3 jest mała”; znaczniki tylko przy kodzie `4821` (W1, W4).
- **D8:** stare pakiety sprawdza checker z `a633136` (ADR-012, W15).
- **D9:** przypis o wielkości liter w W11.

## Cel
Zbudować i zmierzyć 9 tematów metodą morza, tak by operator mógł na wspólnej bramce wybrać dla każdego z 10 tematów: dalej, popraw albo stop.

## Historie użytkownika
- Jako operator chcę przejrzeć 9 list słów oczywistych na jednej stronie na iPhonie, zanim powstaną listy tematów, żeby test nie był dopasowany do wyniku.
- Jako operator chcę ocenić tylko T2 (i T3 medycyny), ok. 300 słów, bo T1 jest trafne w trzech pomiarach.
- Jako operator chcę jedną stronę z linkami do 9 stron R2, żeby nie zgubić tematu.
- Jako operator chcę tabelę 10 tematów z przecięciami, testem słów i werdyktem, żeby zdecydować wspólnie.
- Jako operator chcę po ocenie usunąć pojedyncze złe słowa w v2 tematu bez nowego kodu.

## Wymagania

### W1. Schemat pliku tematu (`load_topic`)
- Klucze: `id`, `nazwa`, `wersja`, `t1`, `t2`, `dodatki`, `wykluczenia`, `diagnostyka`, `uwagi` oraz opcjonalnie `t3`. Nieznany klucz to kod 2.
- `t3`, gdy jest, ma dokładnie `{iate}`. Pole `iate` ma ten sam schemat co dziś. `t3.dodatki` to błąd.
- `dodatki` (górny poziom): lista `{lemat, czesc_mowy, powód}`, może być pusta. Reguły jak dziś: unikalna para i powód bez tabulacji.
- `wykluczenia`: lista `{lemat, czesc_mowy, powód}`, może być niepusta. `czesc_mowy` to klasa tagu SGJP. Para jest unikalna, powód bez tabulacji i nowej linii. Ta sama para w `dodatki` i `wykluczenia` daje kod 2.
- `diagnostyka`: `slowa_oczywiste` (wymagane) i opcjonalnie `znaczniki_srodladowe`. Znaczniki bez `t3` albo przy `t3` bez kodu `4821` dają kod 2.
- `t2.wykluczenia_poddrzew` bez zmian w schemacie. Nowa reguła: wykluczony synset nieosiągalny z korzeni po relacjach tematu (liczone bez żadnych wykluczeń) daje kod 4.
- Id `[a-z]+` = nazwa pliku; wersja `<id>-v<n>`. Bez zmian.

### W2. Wejścia zależne od tematu
- `tematy-sources.json` bez zmian: IATE zostaje w manifeście i walidacji źródeł.
- `check_inputs` rejestruje i haszuje `iate` tylko wtedy, gdy temat ma `t3`. `candidates` woła `t3_candidates` tylko wtedy. Inaczej T3 jest puste.
- Manifest pakietu: `inputs` zawiera tylko użyte wejścia. Blok `iate` (`member`, `last_modified`, `bytes`) pojawia się tylko przy `t3`.

### W3. Wykluczenia lematów w budowie
- Stosowane w `build_entries` po zebraniu źródeł T1–T3, a przed dodatkami, formami i diagnostyką. Usuwamy każdy leksem z `lemma_base` = `lemat`, którego klasy zawierają `czesc_mowy`.
- Wykluczenie bez leksemu wśród kandydatów daje kod 4 („wykluczenie bez trafienia”).
- Wykluczone leksemy nie liczą się jako kandydaci. `summary.json` ma nowy klucz `wykluczenia`: lista `{lemat, czesc_mowy, powód, klucze, warstwy}`. `raport.md` dostaje sekcję „Wykluczenia” tylko wtedy, gdy lista jest niepusta.
- Checker: żaden wiersz TSV nie ma lematu i klasy z `wykluczenia` tematu. Usuwamy obecny wymóg „temat bez wykluczeń”.

### W4. Teksty i raport zależne od tematu
- `tematy-teksty/*.md`: odcinek `<!--T3-->…<!--/T3-->` zostaje tylko przy `t3`. Odcinek `<!--SRODLADOWE-->…<!--/SRODLADOWE-->` zostaje tylko przy `znaczniki_srodladowe`.
- Reguła zdejmowania, bajtowo: w zachowanym odcinku usuwamy dokładnie bajty obu znaczników. Usunięty odcinek tracimy w całości, od `<!--X-->` do `<!--/X-->` włącznie. Nic poza tym (spacje i nowe linie zostają).
- Znaczniki stawiamy tak, żeby oba warianty dawały poprawny tekst. Punkt listy: odcinek zaczyna się od `\n- ` poprzedniego końca linii. Zdanie w akapicie `TERMS.md`: spacja przed zdaniem leży wewnątrz odcinka.
- Odcinki się nie zagnieżdżają i każdy jest zamknięty, inaczej kod 2. `@@SRODLADOWE@@` musi wystąpić dokładnie raz, wewnątrz odcinka SRODLADOWE.
- Odcinkami T3 obejmujemy: sekcję IATE w `ATTRIBUTIONS-tematy.md`, zdanie o IATE w `TERMS.md`, punkt o T3 w `LIMITATIONS.md`. Punkt o żegludze śródlądowej obejmujemy odcinkiem SRODLADOWE.
- `LIMITATIONS.md`, dwie zmiany treści:
  - punkt T2 bez przykładów morza: „Daje szum; przykłady w `reports/raport.md` i próbie R2”;
  - punkt T3 bez „T3 jest mała” (medycyna ma ok. 950 terminów IATE, wielkości T3 nie mierzono): „T3 to polskie terminy jednowyrazowe IATE z dziedzin tematu; liczba w `reports/raport.md`. Dane IATE pochodzą z 2019 r.”.
- Pierwsza budowa medycyny mierzy T3; liczba trafia do raportu bramki.
- `raport.md` i komunikaty: bez literału „MORZE” (nazwa listy z `id`). „T1 < T2 < T3” zastępuje lista użytych warstw. Sekcje T3 i „Żegluga śródlądowa (T3)” pojawiają się tylko przy T3 albo przy znacznikach.
- `summary.json`: bez `t3` pole `t3` = `null`. `srodladowe` = `null` zawsze, gdy brak `znaczniki_srodladowe`, także w medycynie (D2). Wiersz TL;DR raportu o śródlądowych tylko przy znacznikach. Nowe pole `werdykt.nie_dotyczy`.

### W5. Metoda `tematy-v2` (`config/generator/tematy.json`)
- `version: tematy-v2`, `adr: docs/adr/ADR-012-tematy-fala-1.md`. Stałe `METHOD` i `ADR` w `tematy.py` i w checkerze.
- Nowe pole `operator_warstwy: ["T2", "T3"]`. To niepusty podzbiór `PROBA` bez powtórzeń, inaczej kod 2. `operator_per_stratum: 30` bez zmian.
- `sampling` bez zmian (`tematy-quality-v1`, seed `literaki-slownik-tematy-v1`, 50). `quality.py` bez zmian.
- `progi` bez zmian (decyzja operatora: jak dla morza). `teksty`: nowe hashe plików ze znacznikami.
- Próba (`sample.json`) nadal losuje T1, T2 i T3 (pusta T3 ma `EMPTY_NOT_COVERAGE`). `operator.strata` zawiera tylko warstwy z `operator_warstwy`.

### W6. Werdykt
- Próg warstwy (`t1_tak`, `t2_tak`, `t2_nie`, `t3_tak`) liczymy z ocen operatora, gdy warstwa jest w `operator_warstwy`. W pozostałych warstwach liczymy go z ocen agenta. Dla tematów fali `t1_tak` pochodzi więc z ocen agenta.
- Progi z ocen agenta liczymy zawsze, także przed oceną operatora. „czeka” dostają tylko progi z warstw operatora i zgodność (D3).
- `t3_tak` = `nie_dotyczy`, gdy temat nie ma `t3`. Temat z `t3` i pustą populacją T3 daje `niespelniony`, bo błąd konfiguracji ma być widoczny.
- Status `nie_dotyczy` nie blokuje „dalej”. Ma go `CZEKA` w `tematy.py` (`summary.werdykt.nie_dotyczy`) i `verdict` w checkerze.
- Zgodność i kappa liczymy jak dotąd, na pozycjach ocenionych przez obu (T2, oraz T3 w medycynie). Próg 0,80.

### W7. Checker i strona R2
- `check_tematy_package.py`:
  - `load_config` zna `operator_warstwy`;
  - walidacja manifestu wejść nadal wymaga `iate` (W2). Od `t3` zależy tylko porównanie pinów: checker czyta temat z pakietu przed porównaniem pinów (dziś czyta go po nim, `check_tematy_package.py:304–316`) i porównuje piny tylko użytych wejść;
  - `addenda` czyta górne `dodatki`;
  - dochodzi kontrola wykluczeń (W3);
  - przy temacie bez `t3` warstwa T3 jest pusta;
  - `check_sample` porównuje `operator.strata` z `operator_warstwy`;
  - `check_review` liczy werdykt według W6.
- Checker nadal nie importuje `literaki_slownik`.
- `tematy_review.py`: `page_items` i `record` iterują po warstwach z `sample.operator.strata`, a nie po stałej `PROBA`. Strona i JSON operatora bez innych zmian.

### W8. Regresja morza
Po zmianach kodu (W1–W7) i migracji `morze.json` budujemy dwa pakiety morza: `tematy-morze-v2-YYYYMMDD-{a,b}`. Porównujemy je z `data/work/tematy-v2-20261029-a`.
- **Bajtowo równe:** `MORZE.txt.gz` (`6e78d1ef…`), `MORZE.tsv.gz` (`83037db1…`), `ATTRIBUTIONS.md` (`a3a221e9…`), `TERMS.md` (`b4250289…`).
- **`LIMITATIONS.md`:** różni się tylko punktami T2 i T3 (W4). Sprawdzamy to przez `diff`.
- **`reports/summary.json`:** równy po usunięciu `method`, `wykluczenia` i `werdykt.nie_dotyczy`.
- **`reports/sample.json`:** równe `strata`, `items`, `unique_selected_units` i `overlaps`. `operator.strata` ma tylko T2 i T3.
- **Mogą się różnić:** `tematy/morze.json`, `method.json`, `reports/raport.md`, `reports/review-template.json`, `release-manifest.json` (`method`, `adr`, `code_identity`, `topic.sha256`, `config_sha256`, `files`) i `SHA256SUMS`.
- a = b (`SHA256SUMS`), checker PASS. Liczby: 970 wpisów, 11 035 form, test 37/37.
- Test jednostkowy tekstów (temat z T3 i znacznikami):
  - `ATTRIBUTIONS-tematy.md` po zdjęciu znaczników ma stary hash `d6673156…`, a `TERMS.md` stary hash `b4250289…`;
  - `LIMITATIONS.md` równa się staremu tekstowi z podmienionymi tylko punktami T2 i T3;
  - temat bez T3: teksty bez „IATE” i bez „śródląd”.

### W9. Przepięcie ocen morza
- Plik `verification/tematy-morze-review.json` (w folderze #12) powstaje z `tematy-morze-v2-review.json` z #11. Oceny agenta przechodzą bez zmian, z tym samym `agent_sha256`. Od operatora bierzemy pozycje T2 (30) i T3 (27). To te same klucze, które ocenił na stronie z #11.
- Wiązanie z nowym pakietem a: z jego `reports/review-template.json` kopiujemy `sample_sha256`, `canonical_index_sha256`, `evidence_sha256` i `version`. `sha256sums_sha256` to hash jego `SHA256SUMS`. `evidence_sha256` się zmienia, bo `summary.json` ma `method: tematy-v2`. `operator.agent_sha256` = `agent_sha256`.
- Skrypt lokalny w zadaniu (`analysis/`). Na końcu woła checker `--review`.
- Wynik oczekiwany (policzony w audycie z ocen #11):
  - `t1_tak` (agent) 23/25, spełniony;
  - `t2_tak` i `t3_tak` (operator) 1, spełnione; `t2_nie` 0;
  - zgodność 20/57, kappa 0, niespełniona;
  - werdykt „popraw”. Inny wynik oznacza błąd przepięcia albo W6.

### W10. Słowa oczywiste (przed każdą budową nowego tematu)
1. Agent dostaje tylko nazwę tematu i granice z `clarifications.md`. Nie widzi kandydatów, list Słowosieci ani pakietów. Pisze ok. 35 słów na temat: lematy małymi literami, jedno słowo.
2. Skrypt sprawdza każde słowo tak, jak liczy test: słowo musi być `lemma_base` leksemu SGJP z klasą z `czesci_mowy` (`inf`, `subst`, `depr`, `adv`, `adj`), a leksem musi mieć formę w STANDARD v31. Wzór: `map_lemmas` (`tematy.py:552`) i `_read_forms`. Sama forma w STANDARD nie wystarcza (np. `psy`, `koty` to formy, nie lematy). Słowo, które nie przejdzie, agent wymienia, zanim lista trafi do operatora.
3. Jedna strona (prywatny artefakt claude.ai, iPhone): 9 list, skreślanie, pole „dopisz”, przycisk „kopiuj JSON”, szkic w `localStorage` w `try/catch`.
4. JSON operatora trafia do `analysis/slowa-oczywiste.json` (szkic agenta i wynik). Commit przed pierwszą budową nowego tematu.
5. Pliki tematów kopiują listy dokładnie. Test porównuje każdy temat z tym plikiem. Po budowie list nie zmieniamy (zmiana = nowa wersja tematu po wspólnej ocenie).

### W11. Pliki 9 tematów (`config/generator/tematy/<id>.json`)
Wszystkie: `t2.tryb: "pelne"`, `dodatki: []`, `wykluczenia: []` i `uwagi` z decyzjami granic (`clarifications.md`, `scope-clarifications.md`). Nazwy korzeni i wykluczeń sprawdzono 2026-10-29 na `plwn45-tematy.sqlite` (`aa65ad79…`): wszystkie są zgodne. Budowa sprawdza je ponownie (`_check_names`). Lematy T2 liczyłem po zmianie na małe litery, tylko jedno słowo, kody 1–4, bez synsetów sztucznych. Budowa nie zmienia wielkości liter (np. kuchnia: 2 432 po zmianie, 2 434 bez niej). Liczby wiążące poda raport budowy (D9).

| id | nazwa | T1 atomy | T2 korzenie (synset nazwa) | relacje | wykluczenia poddrzew | T3 | T2 lematy |
|---|---|---|---|---|---|---|---|
| `zwierzeta` | Zwierzęta | `zool.`, `zootechn.`, `hip.`, `paleont.` | 5621 zwierzę 1; 403786 zwierzę 2 | 11, 27 | 6047 człowiek 1; 78303 hominid 1 | — | 4 452 |
| `rosliny` | Rośliny | `bot.`, `ogr.` | 4603 roślina 1; 4609 drzewo 2 | 11, 25, 27 | — | — | 3 111 |
| `medycyna` | Medycyna i ciało | `med.`, `anat.`, `psych.`, `wet.`, `farm.` | 7729 schorzenie 1; 7227 lekarstwo 1; 2180 organ 3; 441043 część ciała 1; 5999 tkanka 1; 1649 mięsień 1; 6476 kość 1; 15615 gruczoł 1; 10877 medycyna 1; 597 lekarz 2; 30333 zabieg 1; 4113 operacja 1; 259726 uraz 1; 2850 nowotwór 1; 4813 szpital 1; 6377 pielęgniarka 1 | 11, 25, 27 | 244560 organ roślinny 1; 38995 narząd płciowy rośliny 1; 32240 tkanka roślinna 1; 4722 nasiono 1; 27813 zarodnia 1 | IATE `2841` | 4 063 |
| `muzyka` | Muzyka | `muz.`, `chor.` | 1720 muzyka 1; 8272 instrument muzyczny 1; 6994 utwór muzyczny 1; 5860 muzyk 1; 10970 taniec 1; 10972 taniec 2; 2324 piosenka 1; 23802 śpiewak 1; 7139 śpiew 2; 27623 dźwięk muzyczny 1; 19153 muzykant 1; 7767 orkiestra 1 | 11, 25, 27 | — | — | 1 148 |
| `kuchnia` | Kuchnia | `kulin.`, `spoż.` | 11077 potrawa 1; 10738 jedzenie 2; 11041 przyprawa 1; 5268 napój 1; 10933 napój 2; 11038 ciasto 1; 11015 mięso 1; 11150 ser 1; 11099 wędlina 1; 11178 zupa 1; 11211 sos 1; 14646 naczynie kuchenne 1; 13142 kucharz 1; 11010 warzywo 2; 11005 owoc 2 | 11, 25, 27 | — | — | 2 432 |
| `sport` | Sport | `sport.`, `gry`, `szach.`, `karc.` | 12622 sport 1; 5963 sportowiec 1; 6558 zawody 2; 4286 zawodnik 1; 233326 dyscyplina sportowa 1; 14502 gimnastyka 1; 427828 sprzęt sportowy 1 | 11, 25, 27 | — | — | 757 |
| `matematyka` | Matematyka | `mat.` | 8086 pojęcie matematyczne 1; 46351 obiekt matematyczny 1; 48390 figura geometryczna 1; 20685 liczba 2; 885 funkcja 3; 8076 działanie matematyczne 1; 13154 matematyk 1; 8122 matematyka 1; 4984 figura geometryczna 2 | 11, 25, 27 | — | — | 543 |
| `pogoda` | Pogoda | `meteor.` | 2402 pogoda 1; 5353 zjawisko atmosferyczne 1; 5330 burza 1; 5328 wiatr 1; 549 opad 1; 5285 opad 2; 351 chmura 1; 5324 deszcz 1; 42764 śnieg 2; 5749 klimat 2 | 11, 25, 27 | — | — | 209 |
| `grzyby` | Grzyby | `mikol.` | 4617 grzyb 1; 20964 grzyb jadalny 1; 15924 pleśń 1; 27820 plecha 1 | 11, 25, 27 | — | — | 351 |

- Medycyna `t3.iate` ma te same pola co morze: `typ: fullForm`, `jedno_slowo: true`, `niezawodnosc_min: 3`, `odrzuc_status`: `deprecatedTerm-admn-sts`, `supersededTerm-admn-sts`.
- Pomiary uzasadniające wycięcia:
  - zwierzęta: domknięcie po 11, 25, 27 daje 4 727 lematów, po 11, 27 daje 4 452 (relacja 27 nic nie dodaje). Żaden z 269 celów relacji 25 nie leży w domknięciu po 11, 27. Odpadają `dziób`, `kieł`, `jelito`, `guzik`, `poroże`, `wymię`;
  - medycyna: 4 477 → 4 063. Odpadają `batat`, `bazylia`, `cytryna`, `groch`, `kawa`, `sporangium`.
- Wszystkie atomy T1 występują w SGJP jako całe atomy (podział po `|`, potem po `,`).

### W12. Budowy
- Kolejność: grzyby, pogoda, matematyka, muzyka, sport, kuchnia, rośliny, zwierzęta, medycyna. Każdy temat buduje się dwa razy (a, b), po kolei, nigdy równolegle.
- Budujemy z czystego drzewa, po commicie kodu, tematów i list słów (`code_identity.git_dirty: false`).
- Dla każdego tematu: a = b (`SHA256SUMS`), checker PASS. Wynik zapisujemy w `verification/builds.json` (temat, katalog, SHA256SUMS, czas, liczby).
- **Bez commitu od pierwszej do ostatniej budowy serii** (D1). `code_identity.git_commit` = HEAD trafia do manifestu, więc commit między a i b psuje a = b. Dotyczy też regresji morza (W8). `builds.json` i inne zapisy w `.maister` commitujemy dopiero po ostatniej budowie serii.
- Budowy i checker w tle, z czytaniem werdyktu, a nie tylko kodu wyjścia.

### W13. Przegląd R2
1. Instrukcja agenta `analysis/instrukcja-oceny-agenta.md`, commit przed ocenami:
   - „tak”: słowo jest związane z tematem w szerokim sensie (rzeczy, czynności, ludzie, miejsca, żargon);
   - „nie”: brak rozsądnego związku w żadnym znaczeniu;
   - „niepewne”: związek tylko w rzadkim znaczeniu;
   - granice tematów z `clarifications.md`; lemat wspólny z innym tematem zostaje.
2. Agent ocenia całą próbę: T1, T2, T3 po `min(50, N)`. Zapis przez `tematy_review.agent_review` do `verification/tematy-<id>-review.json` i commit z `agent_sha256`, zanim powstanie strona operatora (D12 z #11).
3. 9 stron `tematy_review.py strona` jako prywatne artefakty claude.ai. Operator ocenia 30 słów T2, a w medycynie dodatkowo 30 T3, razem ok. 300.
4. Strona zbiorcza (artefakt): 9 linków z liczbą pozycji i stanem „ocenione / nie”. Agent zmienia stan po otrzymaniu JSON i publikuje stronę ponownie.
5. JSON operatora → `tematy_review.py zapisz` → checker `--review` → `verification/review-check-<id>.json`.

### W14. Zestawienie fali i bramka
- Skrypt lokalny w zadaniu (`analysis/zestawienie_fali.py`) czyta 10 pakietów (9 nowych i morze z W8) oraz pliki `review-check-*`. Wynik: `verification/zestawienie-fali.json` i `verification/gate-report.md`.
- Tabela 10 tematów:
  - wpisy i warstwy, formy;
  - ∩ POP i ∩ POP00 w leksemach i formach;
  - diagnostyka kandydaci → BROAD → STANDARD;
  - test słów (z brakującymi);
  - trafność R2: agent na każdą warstwę, operator na T2 i T3;
  - zgodność i kappa, werdykt automatyczny.
- Nakładanie lematów: macierz par tematów (liczba wspólnych lematów i do 10 przykładów). Lematy zostają w każdym temacie (decyzja operatora); macierz służy tylko do oceny.
- Bramka z operatorem: decyzja dalej / popraw / stop dla każdego tematu, zapisana w `gate-report.md`. Lista lematów do wykluczenia w v2 (bez budowy v2 w tym zadaniu).

### W15. Dokumenty i wiki
- **ADR-012** `docs/adr/ADR-012-tematy-fala-1.md`:
  - metoda `tematy-v2` i powód;
  - T3 opcjonalne, `dodatki` na górnym poziomie, wykluczenia lematów i poddrzew (z regułą „bez trafienia”), teksty z odcinkami;
  - `operator_warstwy` i werdykt `nie_dotyczy`;
  - granice tematów (`clarifications.md`) i zgoda operatora na atomy i sport (2026-10-29), wycięcia z pomiarami (W11), nazwy pakietów, regresja morza (W8);
  - stare pakiety (`tematy-v1-*`, `tematy-v2-20261029-*`, metoda `tematy-v1`) sprawdza checker z commitu `a633136`; nowy checker ich nie przyjmuje (D8).
- **ADR-010** dostaje odsyłacz: „Przegląd i schemat tematu zmienia ADR-012”.
- **Dokumentacja generatora:**
  - `docs/generator/cli.md` (TEMATY): uogólnienie z morza, `<ID>.txt.gz`, opcjonalne T3;
  - `docs/generator/raporty.md`: `counts.<id>`, `wykluczenia`, `srodladowe` tylko przy znacznikach;
  - `docs/generator/jakosc.md`: `operator_warstwy`;
  - `.maister/docs/INDEX.md`: ADR-012 i zadanie #12.
- **`docs/runbook-wiki.md`, sekcja TEMATY:** `counts.<id>`, przykłady sprawdzane w `<ID>.tsv.gz`, tabela tematów na jednej stronie.
- **Wiki** (klon lokalny `/Users/robmar/Projects/Literaki/wiki-literaki-slownik`, gałąź `master`; strony według runbooka, `docs/runbook-wiki.md:79`):
  - `Slownik-TEMATY`: tabela 10 tematów (wersja, wpisy, formy, ∩ POP, ∩ POP00, test słów, stan) i krótki opis metody, nadal „W przygotowaniu”, bez linku pobrania;
  - `Home`: wiersz TEMATY z liczbą tematów;
  - `Slownik-STANDARD`: odsyłacz do TEMATY z liczbą tematów (TEMATY to podzbiory STANDARD);
  - `_Sidebar`: wpis TEMATY bez zmian nazwy, sprawdzamy, czy prowadzi do strony z 10 tematami;
  - `Historia-zmian`: wpis #12.

  Liczby bierzemy z manifestów i sprawdzamy przykłady w TSV.

## Kod do ponownego użycia

### Istniejący kod
| Element | Plik | Użycie |
|---|---|---|
| `load_topic`, `load_method`, `check_inputs`, `candidates`, `build_entries`, `summary`, `raport`, `_write_package`, `build_package` | `literaki_slownik/tematy.py` (101, 67, 223, 523, 633, 837, 873, 997, 1044) | zmiany w miejscu (W1–W6), bez nowego modułu |
| `t2_candidates`, `_check_names` | `literaki_slownik/tematy.py` (348, 341) | wykluczenia poddrzew już działają; dochodzi tylko kontrola osiągalności |
| `map_lemmas`, `_dodatek` | `literaki_slownik/tematy.py` (552, 592) | wzór dopasowania lematu i klasy dla wykluczeń |
| `sample`, `quality.sample_strata`, `review_template` | `literaki_slownik/tematy.py` (970), `literaki_slownik/quality.py` | próba bez zmian; tylko `operator.strata` według `operator_warstwy` |
| checker | `scripts/check_tematy_package.py` (`load_config` 282, `check` 295, `addenda` 219, `check_sample` 239, `verdict` 441, `check_review` 467) | zmiany w miejscu (W7) |
| `agent_review`, `page`, `record` | `scripts/tematy_review.py` (41, 108, 117) | strony R2 i zapis ocen; `page_items` (87) bez stałej `PROBA` |
| strona R2 (HTML z `PAGE`) | `scripts/tematy_review.py` | 9 stron bez zmian wyglądu |
| `record_agent_review.py` | `.maister/tasks/development/2026-10-28-11-tematy-morze/analysis/` | wzór zapisu ocen agenta; kopia w zadaniu #12 z pętlą po tematach |
| fikstury | `tests/tematy_helpers.py` (`config_fixture`, `inputs_fixture`, `package_fixture`) | dochodzi wariant tematu bez T3; `dodatki` na górnym poziomie |
| `morze.json` | `config/generator/tematy/morze.json` | wzór 9 nowych plików |

### Nowe składniki
| Plik | Dlaczego nowy |
|---|---|
| `config/generator/tematy/{zwierzeta,rosliny,medycyna,muzyka,kuchnia,sport,matematyka,pogoda,grzyby}.json` | dane tematów |
| `docs/adr/ADR-012-tematy-fala-1.md` | zmiana metody i schematu wymaga ADR |
| `analysis/slowa-oczywiste.json`, `analysis/instrukcja-oceny-agenta.md` | wejścia zamrożone przed budową i oceną |
| skrypty lokalne w `analysis/`: sprawdzenie słów w STANDARD, zapis ocen agenta, przepięcie ocen morza, zestawienie fali | jednorazowe, dla bramki; nie wchodzą do generatora (tak jak w #11) |
| dwa artefakty: strona słów oczywistych i strona zbiorcza R2 | kanał operatora na iPhonie; strona R2 tematu już istnieje |

Nie robimy: pakietu wielotematowego, nowego modułu, nowej wersji `quality`, warstwy D w v1, `explain --variant tematy`.

## Podejście techniczne
- Kolejność prac:
  1. Słowa oczywiste (W10). Operator przegląda je równolegle z pracą nad kodem.
  2. Kod i testy (W1–W7): ADR-012 przy kodzie, migracja `morze.json`, `tematy.json` v2. Commit.
  3. Regresja i przepięcie morza (W8, W9).
  4. 9 plików tematów i test zgodności list. Commit.
  5. Budowy (W12).
  6. R2 (W13).
  7. Zestawienie i bramka (W14).
  8. Dokumenty i wiki (W15). Pełny zestaw testów raz, na końcu.
- Budowa dla tematu bez T3: brak hasha IATE (113 MB) i brak skanu TBX (40–85 s). Zostają dwa hasze `build.sqlite`. Szacunek: 40–60 s na budowę, medycyna ok. 90 s.
- Budżet razem: 20 budów, co najmniej 30 przebiegów checkera (20 pakietów, 10 `--review`), każdy z dwoma haszami 22 GB; 2–3 h maszyny. Agent: ok. 950 ocen R2 i 315 słów oczywistych.
- Wykluczenia lematów działają na mapie `sources` w `build_entries`, więc diagnostyka i formy już ich nie widzą. Dodatek, który trafiłby w wykluczenie, odrzuca walidacja (kod 2).
- Odcinki tekstów usuwa jedna funkcja w `_write_package`, przed podmianą `@@SRODLADOWE@@`.
- Determinizm i rejestr czytanych plików bez zmian. Temat bez T3 nie rejestruje IATE.
- Commity na `main` (jak #11): `feat(tematy): …`, `docs(tematy): …`, `fix(tematy): … (#12)`. Artefakty `.maister`: `maister: #12 …`. Dane surowe i pakiety zostają poza Git.

## Wskazówki wdrożeniowe

### Testy
- 2–8 testów na grupę kroków. Weryfikacja uruchamia tylko nowe testy grupy. Pełny zestaw (`python3 -m unittest discover -s tests -p 'test_*.py'`) uruchamiamy raz, na końcu.
- Do pokrycia:
  - temat bez `t3`: budowa przechodzi, T3 puste, IATE nie w rejestrze i nie w `inputs`, a teksty bez „IATE” i bez „śródląd”;
  - `t3.dodatki`, znaczniki bez `t3` i znaczniki przy `t3` bez `4821`: kod 2;
  - teksty według W8 (stare hashe `ATTRIBUTIONS-tematy.md` i `TERMS.md`, `LIMITATIONS.md` z podmienionymi punktami T2 i T3); niezamknięty odcinek daje kod 2;
  - medycyna (T3 bez znaczników): `srodladowe` = `null`, raport bez śródlądowych;
  - wykluczenie lematu usuwa leksem z TSV i daje wpis w `summary.wykluczenia`; wykluczenie bez trafienia daje kod 4; para w `dodatki` i `wykluczenia` daje kod 2;
  - wykluczenie poddrzewa nieosiągalne daje kod 4;
  - `operator_warstwy` T2, T3: `operator.strata` bez T1; strona R2 tylko z T2 i T3;
  - werdykt: `t1_tak` z ocen agenta (także bez ocen operatora), `t3_tak` `nie_dotyczy` bez `t3`, `niespelniony` przy `t3` i pustej populacji;
  - przepięcie morza (W9) daje oczekiwany werdykt;
  - skrypt słów oczywistych odrzuca formę, która nie jest lematem;
  - checker: kontrola wykluczeń, piny bez IATE przy temacie bez `t3` (manifest wejść nadal z `iate`), T3 puste bez `t3`;
  - raport bez „MORZE” dla innego `id`;
  - listy słów w 9 plikach tematów równe `analysis/slowa-oczywiste.json`; każdy plik tematu przechodzi `load_topic`.
- Regresja morza (W8) na prawdziwych danych, z wynikiem w `verification/regresja-morze.json`.

### Zgodność ze standardami
- `AGENTS.md`:
  - piszemy po polsku, zwięźle;
  - decyzje o składzie list omawiamy z operatorem: wycięcia w `scope-clarifications.md`, atomy i sport zatwierdzone na bramce specyfikacji;
  - wiki aktualizujemy w tej samej pracy;
  - bez kontaktu z autorami źródeł; dane surowe poza Git.
- ADR-010 i ADR-011: reguły warstw, źródła, atrybucje bez zmian. ADR-012 opisuje różnice.
- `docs/runbook-wiki.md`: stan „W przygotowaniu”, liczby z artefaktów, przykłady z TSV.
- Wnioski z audytu #11:
  - liczby mierzymy na prawdziwych danych, a nie na fiksturze (nazwy korzeni i wycięcia już zmierzone);
  - wszystko przypinamy (listy słów, instrukcja agenta, hash ocen agenta przed stroną);
  - rejestr czytanych plików obejmuje IATE tylko wtedy, gdy temat go czyta.

## Poza zakresem
- Wydanie (tarball, link pobrania), usunięcie „W przygotowaniu”.
- Warstwa D i wersje v2 tematów (po bramce).
- Rolnictwo, Wikisłownik, LLM, kontakt z autorami.
- IATE w tematach innych niż medycyna; korzenie gier w T2 sportu.
- Pakiet wielotematowy, `explain --variant tematy`.
- Zmiany POP, POP0, POP00, BROAD, STANDARD i `quality.py`.

## Kryteria sukcesu
1. Testy grup przechodzą, a na końcu cały zestaw.
2. Regresja morza: zgodna z W8, checker PASS na a i b.
3. `analysis/slowa-oczywiste.json` zacommitowany przed pierwszą budową nowego tematu (kolejność widać w historii Git).
4. 9 tematów: a = b, checker PASS, T3 niepuste tylko w medycynie, IATE tylko w jej manifeście i tekstach.
5. Hash ocen agenta każdego tematu zacommitowany przed jego stroną R2. Operator ocenił ok. 300 pozycji. `review-check-<id>.json` dla 10 tematów.
6. `gate-report.md` ma tabelę 10 tematów, macierz nakładania i decyzję operatora dla każdego tematu.
7. ADR-012, dokumenty generatora, runbook i wiki (Slownik-TEMATY, Home, Slownik-STANDARD, _Sidebar, Historia-zmian) zaktualizowane, stan „W przygotowaniu”.
