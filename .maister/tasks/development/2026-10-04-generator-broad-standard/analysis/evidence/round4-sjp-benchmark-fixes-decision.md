# Runda 4: poprawki po benchmarku SJP.pl

## TL;DR
[Benchmark SJP.pl list v25](sjp-benchmark-v25.md) ujawnił jedną lukę źródła i cztery błędy kwalifikacji. Właściciel 2026-10-08 zatwierdził wszystkie pięć poprawek, a w punkcie 3 rozszerzył zakres na skrótowce („bmw itp. to rzeczowniki, ale też skrótowce, odrzucamy takie rzeczy”). Szczegóły, takie jak listy i próg, ustalił agent z upoważnienia właściciela. Wszystkie decyzje są odwracalne.

Polityka: `approved-conditions-v26`. SJP.pl nie jest wejściem: poprawki opierają się na SGJP, KWJP i zasadach gry. Z listy SJP nie skopiowano żadnego słowa.

## Key Decisions
1. **Uzupełnienie eksportu SGJP: zaimek zwrotny** (`config/generator/sgjp-supplement.tab`, artefakt `lexical_supplement`).
   - Przypięty eksport `sgjp-20260823.tab.gz` nie zawiera ani jednego wiersza z lematem `się` lub `siebie`. Wszystkie inne słowa funkcyjne są obecne (`nie`, `by`, `że`, `już`, `niech`).
   - KWJP, nasze przypięte źródło, ma lemat `siebie` (klasa `siebie`, 211 982 wystąpienia) i `się` (`part`, 1 733 236).
   - Dodane 4 formy w tagsecie SGJP: `się` (`part`), `siebie` (`siebie:gen.acc`), `sobie` (`siebie:dat.loc`), `sobą` (`siebie:inst`).
   - Dotąd `sobie` i `sobą` przechodziły tylko jako formy rzeczownika `soba` (makaron, `kulin.`).
   - Klasa `siebie` dochodzi do macierzy jako `word`.
   - **Szukanie podobnych przypadków:** porównano lematy KWJP z co najmniej 30 wystąpieniami z lematami SGJP. W klasach zamkniętych (przyimki, spójniki, zaimki, partykuły) nie brakuje innych lematów.
   - Brakuje natomiast przymiotników przedrostkowych, których nie ma w samym SGJP, nie tylko w eksporcie (`antydumpingowy`, `neoliberalny`, `prorosyjski`, `postsowiecki`, `prorodzinny`). To osobna luka źródła; wymagałaby konstruktora lub nowego źródła i nie wchodzi w tę rundę.
   - Reszta braków to wtrącenia obce, literówki korpusu i nazwy własne.
2. **Tematy `agl` nie są słowami** (`game-agl-stem-v1`, reject).
   - Analiza `praet:...:agl` (`mogł`, `niosł`, `dorosł`) to temat pod końcówkę (`mogł-em`). W v25 przeszło tak 189 słów.
   - Formy z końcówką i formy `nagl` (`mógł`) bez zmian.
3. **Skróty i skrótowce zapisane jako rzeczowniki** (`game-abbreviation-noun-v1`, reject; zamknięta lista `ABBREVIATION_NOUN_LEMMAS`, 32 lematy):
   - lematy rzeczownikowe bez samogłoski: `nr`, `dr`, `km`, `pkt`, `płk`, `ppłk`, `mgr`, `mjr`, `kmdr`, `kmdt`, `bp`, `sms`, `bmw`, `bhp`, `tv`, `vw`, `www`, `wc`, `wf`, `ckm`, `rkm`, `lkm`, `kb`, `kbk`, `kbks`, `ftp`, `scs`, `rh`, `m-c`, `r-k`;
   - `abp` (bliźniak formy `brev`) i `ha:S` (hektar; wykrzyknik `ha` zostaje).
   - Spośród lematów zbieżnych z formą `brev` ręcznie zachowano zwykłe słowa: `dom`, `ul`, `por`, `sen`, `para`, `tłum`, `gen`, `kat`, `cal`, `lit`, `rys`, `bryg`, `temp`, `aut`, `woj`, `fot`, `reż`, `sek`, `szer`, `kard`, `in`.
   - Pisanych małą literą skrótowców z samogłoską SGJP nie ma (`VAT` czy `PIT` ma wielką literę i już odpada).
4. **Wyjątki R1 z przeglądu według frekwencji KWJP:**
   - nie-mieszkańcy męscy, wraz z formami żeńskimi: `powodzianin` (ofiara powodzi), `targowiczanin` (członek konfederacji, mała litera);
   - żeńskie (nowa lista `NON_RESIDENT_FEMININE_EXCEPTIONS`): `sielanka`, `przytulanka`, `kijanka`, `markietanka`.
   - Niejasne (`zakopianka`, `wólczanka`, `świetliczanka`) zostają po bezpiecznej stronie, czyli z odmową.
5. **STANDARD: współczesne użycie znosi odmowę za dawność** (`linguistic-contemporary-use-kwjp-v1`):
   - dotyczy form z co najmniej 30 wystąpieniami w tekstach nieliterackich KWJP (`orth_lc`, gatunki fakt + publicystyka);
   - beletrystykę pominięto, bo stylizuje;
   - próg wybrano na pełnym zbiorze BROAD bez STANDARD, a nie na słowach SJP. Od 10 wystąpień pojawiają się stylizacje (`ninie`, `trzykroć`), od 30 dominują słowa żywe (`wraz`, `ponoć`, `ilekroć`, `aukcji`, `hospicjum`, `takowe`);
   - inne odmowy STANDARD (wielka litera, pisownia 2026) zostają.

## Alternatywy i wycofanie
- **1:** usunięcie wiersza z `sgjp-supplement.tab` lub artefaktu z manifestu, potem nowy build.
- **2, 3:** usunięcie gałęzi w `source_game_checks` lub lematu z `ABBREVIATION_NOUN_LEMMAS`.
- **4:** usunięcie lematu z zestawu wyjątków.
- **5:** zmiana `CONTEMPORARY_USE_MIN_NONFICTION`. Bardzo wysoka wartość wyłącza regułę. Alternatywą był próg 10, przy którym przechodzą formy stylizowane.

## Testy
- `tests/test_round4_sjp_fixes.py`: 6 testów, w tym pełny build fikstury z uzupełnieniem i frekwencją publicystyki (styk import → decyzje → listy).
- Po buildzie v26 benchmark zostanie powtórzony tym samym skryptem i progiem.
