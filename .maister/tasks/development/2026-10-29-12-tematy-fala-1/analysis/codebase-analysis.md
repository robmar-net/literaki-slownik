# Analiza kodu i danych — #12 TEMATY, pierwsza fala

**Data**: 2026-10-29
**Zadanie**: #12, 9 tematów obok „morza”: zwierzęta, rośliny, medycyna i ciało, muzyka, kuchnia, sport, matematyka, pogoda, grzyby. Metoda tematy-v1 (#11), repo `literaki-slownik`.
**Opis**: operator chce szerokich granic tematów (morze obejmuje żeglugę). T3 (IATE) tylko tam, gdzie pasuje dziedzina. Temat bez T3 musi działać.
**Analizator**: codebase-analyzer (2 agenty Explore: analiza kodu, odkrywanie danych)

Stan kodu: `a1f2f58`. Grupa 16 z #11 (`2bd0dab`, `a633136`) jest już w drzewie: warstwa D (`t3.dodatki`), `WARSTWY=('T1','T2','T3','D')`, `PROBA=('T1','T2','T3')`, wersja tematu `<id>-v<n>`, pakiet morze-v2 `tematy-v2-20261029-a/b` (970 wpisów, 37/37). Numery linii są przybliżone.

---

## TL;DR

- Generator działa dla jednego tematu na przebieg i jest mocno przywiązany do morza i T3: IATE jest obowiązkowe w schemacie, w źródłach, w budowie, w tekstach i w checkerze.
- **Blokada**: temat bez ocen T3 dostaje zawsze werdykt `popraw`, bo `t3_tak` jest `None` (checker ~485, `CZEKA` w `tematy.py` ~738).
- Dane wystarczą na wszystkie 9 tematów: atomy SGJP dla T1 i korzenie Słowosieci dla T2 są zmierzone. IATE ma sens tylko w medycynie (2841). W kilku innych tematach daje niewiele i wymaga sprawdzenia. W muzyce, sporcie, pogodzie i grzybach nie daje nic.
- Zakres: najpierw uogólnić kod (T3 opcjonalne, bez literału MORZE). To około 10–15 miejsc, złożoność umiarkowana. Potem 9 plików tematów i 9 osobnych pakietów.

## Kluczowe decyzje

- **Jeden pakiet na temat** (9 przebiegów CLI), bez pakietu wielotematowego. Taki pakiet zmieniłby kontrakt: manifest, checker, warstwy próby per temat i przegląd.
- **T3 opcjonalne w schemacie tematu.** Bez `t3.iate` nie parsujemy TBX (oszczędza ~40–85 s), nie haszujemy IATE i nie wpisujemy IATE do ATTRIBUTIONS. Sekcje T3 w podsumowaniu i raporcie pojawiają się tylko wtedy, gdy T3 jest użyte.
- **Warstwa D musi przeżyć bez T3.** Dziś `dodatki` siedzą w `t3`. Trzeba je przenieść poziom wyżej (np. `dodatki` obok `t1`/`t2`) albo dopuścić `t3` bez `iate`. Zalecam przeniesienie i migrację `morze.json` (wersja tematu pozostaje `morze-v2`, chyba że zmieni się zawartość).
- **`t3_tak` = „nie dotyczy”**, gdy populacja T3 jest pusta, i to zarówno w `CZEKA`, jak i w checkerze.
- **Znaczniki śródlądowe tylko dla morza.** `znaczniki_srodladowe`, `PRZYKLADY_SRODLADOWE` i `@@SRODLADOWE@@` stają się opcjonalne. LIMITATIONS i ATTRIBUTIONS mają warianty zależne od tematu.
- **T3 tylko w medycynie (2841).** W pozostałych tematach T3 zostaje pominięte, a ewentualny dodatek z IATE idzie po sprawdzeniu przeciw T2.
- **Zwierzęta: wykluczenie poddrzewa `6047 człowiek 1`** jest konieczne, bo bez niego wychodzi 13 329 lematów pełnych ludzi.

## Otwarte pytania i ryzyka

- **Lemat w kilku tematach.** Wpis niesie temat dla lematu, nie dla znaczenia, więc kilkaset lematów trafi do ≥2 tematów (rośliny–medycyna 539, rośliny–kuchnia 451). Do decyzji: akceptujemy czy wykluczamy?
- **Granice dla operatora.** Czy karty (`karc.`) należą do sportu? Łowiectwo (`łow.`) i paleontologia do zwierząt? Napoje do kuchni? Taniec (`chor.`) do muzyki? Grzybica do medycyny czy do grzybów?
- **Zwierzęta (~5000) mają szum**: dinozaury „-zaur”, a relacja 25 wnosi części ciała (trąba, dziób, guzik). Może trzeba dodatkowych wykluczeń albo węższych korzeni.
- **Medycyna (~4500) jest mocno biochemiczna.** `organ 3` i `tkanka 1` wciągają organy roślin i komórki.
- **Czas.** 9 tematów × 2 budowy (a/b) oznacza 18 razy haszowanie 22 GB `build.sqlite` (dwa razy na budowę). Nie zmierzono, ile z 83 s przypada na każdą część.
- **Teksty i dokumentacja.** Teksty są przypięte raz w `tematy.json`, więc każdy temat dostaje dziś teksty o morzu. ADR-010 opisuje „pilotaż morze, jeden temat”. Trzeba nowego ADR albo poprawki.
- Wersja metody: czy uogólnienie kodu zmienia `tematy-v1` na v2 metody? Do rozstrzygnięcia w specyfikacji.

---

## Podsumowanie

Kod #11 jest gotowy do parametryzacji nazwą tematu: nazwy wyjść biorą się z `id`. Twarde założenia o morzu i o obecności T3 siedzą jednak w ~10 miejscach kodu, tekstów, checkera i testów. Dane źródłowe (SGJP, Słowosieć 4.5, IATE) są w cache, a zakres każdego tematu jest zmierzony.

---

## Pliki

### Główne

**`literaki_slownik/tematy.py`** (1088 linii)
- `load_topic` (~101–149) ma zamknięty zbiór kluczy {id, nazwa, wersja, t1, t2, t3, wykluczenia, diagnostyka, uwagi}. `t3` musi mieć dokładnie {iate, dodatki}. `diagnostyka` musi mieć dokładnie {slowa_oczywiste, znaczniki_srodladowe{pl,en}}.
- `INPUTS` i `load_sources` wymagają IATE. `check_inputs` haszuje zip IATE (113 MB). `candidates()` zawsze woła `t3_candidates` (TBX 1,86 GB).
- Elementy specyficzne dla morza: `PRZYKLADY_SRODLADOWE`, `ZNACZNIK '@@SRODLADOWE@@'`, `srodladowe_hasla`, `_inland`.
- Raport ma na sztywno „formy w MORZE”, „## Żegluga śródlądowa (T3)”, „T1 < T2 < T3” i „T1 ∪ T2 ∪ T3”. Komunikaty błędów mówią o „MORZE.tsv” i „Naruszone MORZE ⊆ STANDARD”.
- `WARSTWY` (530), `PROBA` (531), `CZEKA` (738, zawiera `t3_tak`), sekcja T3 w podsumowaniu (~827).

**`scripts/check_tematy_package.py`** (512 linii)
- Ma na sztywno `WARSTWY`, `PROBA` i `PROGI`, `iate` w INPUTS i warstwy próby dokładnie T1, T2, T3.
- **~485: `t3_tak=part('T3','tak_udzial')` daje `None`, a werdykt traktuje to jako niespełnienie.**
- Nie sprawdza bloku śródlądowego ani LIMITATIONS. Nazwy plików z `topic_id.upper()` działają.

**`config/generator/tematy/morze.json`** (155 linii)
- Wzorzec pliku tematu. Nazwa pliku = `id` (`[a-z]+`). Nowe tematy to nowe pliki obok.

**`config/generator/tematy.json`** (52 linie)
- Wspólna konfiguracja metody: wersja, losowanie, `operator_per_stratum`, `progi` (krotka `PROGI` z `t3_tak`), `czesci_mowy`, `t3_klasy`, przypięte `teksty`.

**`literaki_slownik/cli.py`** (186 linii)
- Jedno `--topic` na przebieg → `build_package` → jeden pakiet.

### Powiązane

- **`config/generator/tematy-sources.json`**: manifest źródeł, zawsze z IATE.
- **Teksty `tematy-teksty`**: LIMITATIONS (punkty T3, IATE i śródlądowe oraz znacznik), ATTRIBUTIONS (zawsze IATE).
- **`tests/tematy_helpers.py`** (363 linie): `config_fixture` (kopia `morze.json`, czyści `dodatki`, LIMITATIONS ze znacznikiem, IATE w manifeście), `inputs_fixture` (małe SGJP, PLWN z korzeniami morza, zip IATE), `package_fixture` (T1 4, T2 4, T3 1).
- **Testy**: `test_tematy_config.py`, `test_tematy_inputs.py`, `test_tematy_layers.py`, `test_tematy_dodatki.py`, `test_tematy_package.py`, `test_check_tematy_package.py`, `test_tematy_review.py`, `test_tematy_sources.py`, `test_fetch_tematy_sources.py`.
- **`tematy_review.py`**: strona ogólna, pusta warstwa działa. `quality.sample_strata` obsługuje pustą warstwę (`EMPTY_NOT_COVERAGE`).
- **Dokumentacja**: ADR-010 („pilotaż morze”, „jeden temat”, IATE 4821, `morze.json`, znaczniki śródlądowe), `cli.md` 131–173, `raporty.md` 88–108 (`MORZE.*`, `counts.morze`, `srodladowe`).
- **Dane**: `cache/sgjp/sgjp-20260823.tab.gz`, `cache/plwordnet/plwn45-tematy.sqlite`, `cache/iate/IATE_download.zip`, `build.sqlite` (22 GB, `interpretation.qualifiers`).
- **Research**: `wide-plwordnet-pomiar.md`, `local-data-sgjp-dziedziny.md`.

---

## Obecne działanie

### Przepływ danych

1. CLI `--topic <id>` → `load_topic` i `load_method` → `load_sources` i `check_inputs` (hasze, w tym IATE).
2. `candidates()` buduje trzy listy: T1 z atomów SGJP, T2 z domknięcia relacji 11/25/27 od korzeni Słowosieci (z `wykluczenia_poddrzew`) i T3 z TBX IATE. Do tego dochodzi D (dodatki).
3. `build_entries`: warstwa = najniższa z `WARSTWY`, `zrodla` = posortowane warstwy. Sprawdza też `<ID> ⊆ STANDARD`.
4. Wynik: `<ID>.txt.gz`, `<ID>.tsv.gz`, `tematy/<id>.json`, podsumowanie (zawsze bloki t3 i srodladowe), raport, LIMITATIONS (dokładnie jeden znacznik `@@SRODLADOWE@@`, inaczej błąd), manifest (zawsze z blokiem iate).
5. Próba do oceny z warstw T1, T2 i T3, oceny operatora, werdykt wg `PROGI`/`CZEKA`, checker.

Katalog pakietu: `data/work/tematy-v<n>-YYYYMMDD-{a,b}`, jeden temat na pakiet (`manifest.topic` to jeden obiekt).

### Czas

Morze: 83 s i 79 s na budowę. Skan interpretacji SGJP ~6,7 s. Pełny skan TBX ~40–85 s (dwa pomiary). Dwa razy haszowanie 22 GB. Nie zmierzono rozbicia. Temat bez T3 powinien być wyraźnie szybszy.

---

## Dane per temat

### Atomy SGJP (T1)

W SGJP jest 113 atomów. Liczby to różne leksemy (pole 5 `sgjp-20260823.tab.gz`, te same atomy w `interpretation.qualifiers`).

| Temat | Atomy (leksemy) | Opcjonalne / do decyzji | T1 ~ |
|---|---|---|---|
| zwierzęta | `zool.` 665, `zootechn.` 16, `hip.` 4 | `łow.` 78 (żargon łowiecki, ryzyko), `paleont.` 28 | ~681 |
| rośliny | `bot.` 407 | `ogr.` 21 | 407–428 |
| medycyna i ciało | `med.` 195, `anat.` 69 | `psych.` 24, `wet.` 5, `farm.` 6; może `biol.` 86, `biochem.` 13 | 264–400 |
| muzyka | `muz.` 172 | `chor.` 76 (tańce) | 172–248 |
| kuchnia | `kulin.` 162, `spoż.` 4 | (napoje w środku) | ~166 |
| sport | `sport.` 123 | `gry` 16, `szach.` 5, `karc.` 44 (karty: decyzja operatora) | 123–188 |
| matematyka | `mat.` 62 | — | 62 |
| pogoda | `meteor.` 56 | `hydrol.` 1 | ~56 |
| grzyby | `mikol.` 54 | — | 54 |

### Korzenie Słowosieci 4.5 (T2)

Rel 11 to hiperonimia, a domknięcie idzie w dół. Synsety abstrakcyjne są przechodzone, ale ich lematy nie trafiają do listy. Lematy pisane małymi polskimi literami, części mowy 1–4. Format: `id nazwa liczba_lematów`. Suma: synsety / lematy.

| Temat | Korzenie | Wykluczenia / pominąć | Suma |
|---|---|---|---|
| zwierzęta | 5621 zwierzę 1; 403786 zwierzę 2 (579, domowe) | **wykluczenie poddrzewa 6047 człowiek 1** (bez niego 13 329 lematów z ludźmi); opcjonalnie 78303 hominid 1 (→4721). Wewnątrz: ptak 5185 (827), ssak 4448, gad 5190 (940, głównie -zaur), ryba 5192 (597), owad 5107 (421), płaz 12912 (69). Rel 25 wnosi części (trąba, dziób, guzik) | 12 103 / 4777 |
| rośliny | 4603 roślina 1 (3111); 4609 drzewo 2 (741, wewnątrz) | pominąć 671 drewno 1. Szum z części (betulina, kłodzina) | 7084 / 3111 |
| medycyna i ciało | 7729 schorzenie 1 (1666); 7227 lekarstwo 1 (676); 2180 organ 3 (1567); 441043 część ciała 1 (abstr., 1661); 5999 tkanka 1 (766); 1649 mięsień 1 (305); 6476 kość 1 (39); 15615 gruczoł 1 (36); 10877 medycyna 1 (151); 597 lekarz 2 (107); 30333 zabieg 1 (144); 4113 operacja 1 (48); 259726 uraz 1 (35); 2850 nowotwór 1 (57); 4813 szpital 1 (41); 6377 pielęgniarka 1 (8) | **nie** 247551 oznaka 1 (3468, szum), **nie** 6408 organ 1 (polityczny). organ 3 i tkanka 1 wciągają organy roślin i komórki, dużo biochemii | 6135 / 4411 |
| muzyka | 1720 muzyka 1 (240); 8272 instrument muzyczny 1 (371); 6994 utwór muzyczny 1 (abstr., 401); 5860 muzyk 1 (205); 10970/10972 taniec 1/2 (93/161); 2324 piosenka 1 (82); 23802 śpiewak 1 (72); 7139 śpiew 2 (48); 27623 dźwięk muzyczny 1 (28); 19153 muzykant 1 (26); 7767 orkiestra 1 (4) | pominąć 7941 odstęp 1, 3495 ton 4, 16943 dominanta 1 | 1378 / 1133 |
| kuchnia | 11077 potrawa 1 (885); 10738 jedzenie 2 (1887); 11041 przyprawa 1 (133); 5268/10933 napój 1/2 (394/118); 11038 ciasto 1 (111); 11015 mięso 1 (131); 11150 ser 1 (43); 11099 wędlina 1 (43); 11178 zupa 1 (185); 11211 sos 1 (37); 14646 naczynie kuchenne 1 (44); 13142 kucharz 1 (15); 11010 warzywo 2 (118); 11005 owoc 2 (215) | pominąć 1451 kuchnia 1 (pomieszczenie), 11029 pieczywo 1 (dziwne). jedzenie 2 jest szerokie (adenina; 378 lematów wspólnych z medycyną) | 2797 / 2407 |
| sport | 12622 sport 1 (339); 5963 sportowiec 1 (275); 6558 zawody 2 (171); 4286 zawodnik 1 (66); 233326 dyscyplina sportowa 1 (36); 14502 gimnastyka 1 (18); 427828 sprzęt sportowy 1 (5) | pominąć 8845 obiekt sportowy 1, 236 boisko 1 (szum map). Szum: matka, egzekutor, partia | 831 / 757 |
| matematyka | 8086, 46351, 48390, 20685, 885, 8076, 13154, 8122 (z researchu); 4984 figura geometryczna 2 | szum: czcionka, prosumpcja, reeksport, poligon, dryf | 1133 / 540 |
| pogoda | 2402 pogoda 1 (111); 5353 zjawisko atmosferyczne 1 (174); 5330 burza 1 (95); 5328 wiatr 1 (57); 549/5285 opad 1/2 (25/15); 351 chmura 1 (19); 5324 deszcz 1 (9); 42764 śnieg 2 (12); 5749 klimat 2 (7) | pominąć 1254 atmosfera 1, 20180 temperatura 1. Szum: chromosfera, mgławica | 224 / 209 |
| grzyby | 4617 grzyb 1 (343); 20964 grzyb jadalny 1 (40); 15924 pleśń 1 (8); 27820 plecha 1 (13) | opcjonalnie 24994 grzybica 1 (46, choroby, raczej do medycyny). Terminy techniczne (sporangium) | 963 / 351 |

### IATE (T3)

TBX z 2019 ma tylko 4-cyfrowe kody EuroVoc (149). Liczby to jednowyrazowe terminy PL po filtrach. W nawiasach: część wspólna z T2 tematu.

| Kod | Dziedzina | Terminy PL | Wspólne z T2 | Ocena |
|---|---|---|---|---|
| 2841 | zdrowie | 950 | medycyna 247 | **użyć w medycynie**; dużo farmakologii i chemii |
| 3606 | nauki przyrodnicze i stosowane | 1297 | zw 250, ro 114, med 126 | za szeroka; najwyżej po sprawdzeniu przeciw T2 |
| 5211 | środowisko naturalne | 287 | zw 133 | tylko po sprawdzeniu |
| 5641 | rybołówstwo | 600 | zw 258 (ryby) | tylko po sprawdzeniu |
| 5631 | działalność rolnicza | 296 | — | nie |
| 6006 | produkty roślinne | 46 | ro 28, kuch 22 | mało |
| 6011/6016/6021/6026/6031/6036 | żywność | 26/18/33/9/19/130 | kuchnia 3/7/13/2/1/6 | prawie nic; 6036 to chemia dodatków |
| 2831 | kultura i religia | 31 | muzyka 2 | nic |
| 2826 | sprawy społeczne | 93 | sport 2 | nic |
| 1631 | analiza ekonomiczna | 99 | mat 10 (statystyka) | mało |
| 36 | nauka | 30 | mat 8 | mało |

Pogoda i grzyby nie mają w IATE nic przydatnego.

### Przybliżona wielkość T1 ∪ T2

| zwierzęta | rośliny | medycyna | muzyka | kuchnia | sport | matematyka | pogoda | grzyby |
|---|---|---|---|---|---|---|---|---|
| ~5000 | ~3200 | ~4500 (+IATE) | ~1200 | ~2500 | ~850 | ~560 | ~230 | ~380 |

### Nakładanie się lematów T2

| Para | Lematy |
|---|---|
| rośliny–medycyna | 539 |
| rośliny–kuchnia | 451 |
| medycyna–kuchnia | 378 |
| zwierzęta–medycyna | 295 |
| zwierzęta–rośliny | 111 (babka, bielik) |
| zwierzęta–kuchnia | 94 |
| medycyna–grzyby | 72 |
| rośliny–grzyby | 53 |
| zwierzęta–grzyby | 22 (kania, koźlak) |

---

## Zależności

- **Wejścia**: SGJP (tab.gz i `build.sqlite`), Słowosieć 4.5 (sqlite), IATE (zip i TBX), STANDARD (warunek podzbioru).
- **Konsumenci**: checker, `tematy_review.py`, testy (9 plików), dokumentacja (ADR-010, `cli.md`, `raporty.md`).
- **Zasięg zmian**: średni, ograniczony do podsystemu tematów. Generator głównego słownika nie jest dotknięty.

---

## Testy

- Mamy 9 plików testów tematów i fikstury z `tematy_helpers.py`. Wszystkie zakładają temat morze z T3.
- **Luki**: brak tematu bez T3, brak drugiego tematu, brak LIMITATIONS bez znacznika, brak werdyktu przy pustej populacji T3.
- **Fikstura drugiego tematu potrzebuje**: JSON tematu (nazwa pliku = id), atomów T1 w kwalifikatorach fikstury SGJP, korzeni T2 o nazwach zgodnych z PLWN (`_check_names` „lemma variant”), schematu bez `t3.iate` i bez znaczników śródlądowych oraz LIMITATIONS bez znacznika.

---

## Wzorce

- Konfiguracja jest deklaratywna w JSON i walidowana zamkniętymi zbiorami kluczy (błąd przy nieznanym kluczu).
- Wynik ma być powtarzalny: hasze wejść, przypięte teksty, budowy a/b muszą dać to samo.
- Nazwy wyjść pochodzą z `id`: `<ID>.txt.gz`, `<ID>.tsv.gz`, `tematy/<id>.json`.
- Kod funkcyjny w stylu modułowym, stałe krotek na poziomie modułu (`WARSTWY`, `PROBA`, `PROGI`, `CZEKA`).

---

## Złożoność

| Czynnik | Wartość | Poziom |
|---|---|---|
| Pliki | ~8 (tematy.py, checker, morze.json, tematy.json, teksty, helpers, docs ×3) + 9 nowych JSON | Średni |
| Rozmiar | `tematy.py` 1088, checker 512 | Średni |
| Konsumenci | checker, review, 9 plików testów | Średni |
| Testy | dobre dla morza, zero dla tematu bez T3 | Średni |

**Ogółem: umiarkowana.** Uogólnienie (T3 opcjonalne) to ~10–15 edycji. Dodanie tematów to głównie dane i decyzje o granicach.

---

## Wnioski

**Mocne strony**: nazwy wyjść już zależą od `id`. Pusta warstwa próby jest obsłużona. Warstwa D istnieje. Dane wszystkich tematów są zmierzone i w cache.

**Słabe strony**: IATE jest twardo wymagane w 6 miejscach. Werdykt bez T3 jest zawsze `popraw`. Literał MORZE występuje w komunikatach i raporcie. Teksty są wspólne dla wszystkich tematów. Dodatki są przywiązane do bloku T3.

**Szanse**: bez T3 budowa jest krótsza. Hasz `build.sqlite` można policzyć raz na serię 9 tematów (do zmierzenia, nie wymagane).

---

## Wpływ

- **Zmiany główne**: `tematy.py` (`load_topic`, `INPUTS`/`load_sources`/`check_inputs`, `candidates`, podsumowanie, raport, `CZEKA`, LIMITATIONS, manifest), `check_tematy_package.py` (INPUTS, warstwy próby, `t3_tak`, zbiór kluczy metody), `morze.json` (jeśli `dodatki` przechodzą wyżej).
- **Zmiany powiązane**: teksty (wariant bez T3, bez śródlądowych), `tematy-sources.json` (IATE potrzebne tylko tematom z T3), ADR (nowy, numer z numeru zgłoszenia, wg zasad repo), `cli.md`, `raporty.md`.
- **Nowe pliki**: `config/generator/tematy/{zwierzeta,rosliny,medycyna,muzyka,kuchnia,sport,matematyka,pogoda,grzyby}.json`. Id musi pasować do `[a-z]+`, czyli bez polskich znaków i bez spacji.
- **Testy**: fikstura tematu bez T3, test werdyktu „nie dotyczy”, test LIMITATIONS bez znacznika. Regresja morza musi dalej dawać 970 wpisów i 37/37.

### Ryzyko: średnie

Zmiany są w kodzie wspólnym z działającym pakietem morza (regresja v2). Granice tematów są subiektywne i bez operatora nie da się ich zamknąć. Duże tematy (zwierzęta, medycyna) mają zmierzony szum.

---

## Rekomendacje

1. **Najpierw kod, potem tematy.** Jedna grupa robi uogólnienie: T3 opcjonalne, dodatki poza T3, „nie dotyczy” dla `t3_tak`, teksty warunkowe, bez literału MORZE. Test regresji: morze-v2 daje identyczny wynik bajt w bajt (albo z udokumentowaną różnicą manifestu).
2. **Tematy po kolei, od małych.** Najpierw grzyby, pogoda i matematyka (małe, bez T3, szybka ocena), potem muzyka, sport i kuchnia, na końcu rośliny, zwierzęta i medycyna (z T3 2841).
3. **Każdy temat to osobny pakiet** `tematy-v<n>-YYYYMMDD-<id>-{a,b}` z własną próbą i oceną operatora.
4. **Bramka nakładania.** Raport pakietu powinien pokazać lematy wspólne z innymi tematami fali, żeby operator mógł je ocenić. Polityka (akceptujemy czy wykluczamy) do ustalenia w specyfikacji.
5. **Granice spisać w JSON tematu** (`uwagi`), razem z decyzjami operatora co do kart, łowiectwa, paleontologii, napojów, tańca i grzybicy.

## Następne kroki

Uruchomić gap-analyzer. Wejścia: lista blokad (T3 obowiązkowe, `t3_tak`, LIMITATIONS, literał MORZE), tabele per temat jako podstawa specyfikacji, otwarte pytania o granice dla operatora.
