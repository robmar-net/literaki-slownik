# local: Słowosieć 4.5 (pełny zrzut) i IATE

## TL;DR
- Pełny zrzut Słowosieci 4.5 (2 627 843 157 B, odczytany strumieniowo w całości) nie zawiera słowa „wulwa” w żadnej formie ani w żadnej tabeli. Polskie trafienia `wulw` to tylko nazwisko „Wulw” (9×, przykłady użycia) i „wulwodynia” (20×).
- Angielskie „vulva” (PWN, LU 487932) jest połączone relacją `Syn_plWN-PWN` z polskim synsetem {srom}. Słowosieć tłumaczy więc vulva jako „srom”, a nie „wulwa”.
- Synset {srom} ma jedną jednostkę. Glosa: „##K: książk. ##D: zewnętrzna część żeńskiego układu płciowego”. Obok są {pochwa, wagina, joni} i {łechtaczka, klitoris, clitoris}.
- Wulwodynia ma kwalifikator „##K: specj.”, a jej glosa używa słów „sromu lub pochwy” i podaje link do pl.wikipedia. Rdzenia „wulwa” nie używa.
- IATE (eksport 2019-02-26) nie ma hasła „vulva” w żadnym języku. Nie ma też polskiego terminu z `wulw`. Polski występuje tylko jako „…zapalenie błony śluzowej sromu i pochwy” (IATE-1245114).

## Kluczowe decyzje
- Zrzut odczytano Pythonem z potoku `unzip -p`, bez rozpakowywania na dysk. Pierwsza próba, `grep -o '.{0,200}…'`, przekroczyła limit złożoności ugrep, a BSD grep był zbyt wolny. Liczba przeczytanych bajtów (2 627 843 157) zgadza się z rozmiarem pliku w `unzip -l`, więc odczyt objął cały zrzut.

## Otwarte pytania
- Brak

## 1. Pełny zrzut Słowosieci
Polecenie:
`unzip -p cache/plwordnet/wordnet_work_4_5.zip | python3 -I /private/tmp/claude-501/-Users-robmar-Projects-Literaki/3ae5c44e-c8df-4ef9-924a-bcb0e5eaf7f8/scratchpad/wulwa/plwn.py`
Skrypt szuka `wulw` i `vulv` bez względu na wielkość liter, z kontekstem 160 B i tabelą z najbliższego `INSERT INTO`. Wynik zapisuje do `…/scratchpad/wulwa/plwn.txt`. Przebieg trwał 17 s.

- Kontrola dodatnia w tym samym przebiegu, `łechtaczk`: lexicalunit 15, synset 5, usage_examples 72, morphology 33, extgraph 30.
- Trafienia `wulw|vulv` według tabel: lexicalunit 14, synset 23, usage_examples 19, tracker_lexicalunit 36, tracker_synset 67.
- Formy polskie, wszystkie: `Wulw` 9 (nazwisko z przykładów użycia, np. „Robert Wulw (81)”, „Maciej Wulw (skrzypce)”), `wulwodynia` 11, `Wulwodynia` 7, `wulwodynii` 2. Formy „wulwa” nie znaleziono.
- Formy angielskie i łacińskie: vulva 104, vulvae 38, vulvovaginitis 28, vulvar 35, vulvitis 24, vulval 20, vulvectomy 12, vulvaria 10, vulvodynia 3. Należą do części PWN (pos 6/8) i do glos, np. kandydoza: „łac. vulvovaginitis candidamycetica”.

Relacje z `cache/plwordnet/plwn45-tematy.sqlite` (sqlite3 -readonly):
- `lexicalunit`, `lemma LIKE '%wulw%' OR '%vulv%'`: wśród polskich lematów (pos 2) jest tylko wulwodynia (7072263). Angielskie to vulva 487932, vulvar, vulval, vulvectomy, vulvitis, vulvovaginitis, pruritus vulvae i rima vulvae.
- Synset 79859 {srom}:
  - `Syn_plWN-PWN` → 315220 {vulva};
  - `część` → {łechtaczka; klitoris; clitoris}, {warga sromowa}, {wzgórek łonowy; wzgórek Wenery}, {przedsionek pochwy};
  - `bliskoznaczność` → {cipka; …};
  - `fuzzynimia` → {pochwa; wagina; joni}.
- Synset 315220 {vulva} → `międzyjęzykowa_synonimia_międzyrejestrowa_PWN-plWN` → {szparka; piczka; pipa}. Polskich odpowiedników jest kilka, ale „wulwy” wśród nich nie ma.
- Synset 7072024 {wulwodynia} → hiponimia {zaburzenie; zakłócenie; aberracja}.
- Glosa LU 42014 `srom`: „##K: książk. ##D: zewnętrzna część żeńskiego układu płciowego. [##W: Srom składa się z wzgórka łonowego, dwóch warg sromowych…]”.
- Glosa LU 7072263 `wulwodynia`: „##K: specj. ##D: zaburzenie polegające na chronicznym bólu lub dyskomforcie … skóry sromu lub pochwy … {##L: https://pl.wikipedia.org/wiki/Wulwodynia}”. Autorka: Justyna.Ławniczak.

## 2. IATE (`cache/iate/IATE_download.zip` → `IATE_export_26022019.tbx`, 1,86 GB)
Polecenie:
`unzip -p cache/iate/IATE_download.zip | python3 -I /private/tmp/claude-501/-Users-robmar-Projects-Literaki/3ae5c44e-c8df-4ef9-924a-bcb0e5eaf7f8/scratchpad/wulwa/iate.py`
Skrypt czyta całe `termEntry` i dopasowuje je do wzorca `vulv|wulw|<term>srom<|<term>łechtaczka<|<term>pochwa<`. Wypisuje terminy en, pl i la. Wynik: 25 haseł, zapisanych w `…/scratchpad/wulwa/iate.txt`.

- Hasła angielskie z `vulv` to same złożenia: vulval (IATE-1684248), vulvovaginitis, pruritus vulvae, vulvo-perineal region, vulvovaginal vascularization i IPV u bydła. Samego „vulva” nie ma.
- Polskich terminów jest mało: IATE-1245114 „otręt bydła | pęcherzykowe zapalenie błony śluzowej sromu i pochwy” oraz IATE-1452300. To jest kontrola dodatnia: polskie „srom” da się tym sposobem znaleźć. Tak samo znaleziono by „wulw”, gdyby IATE je miało.
- Polskiego „wulw*” nie ma. Haseł z samym „srom”, „łechtaczka” czy „pochwa” też nie ma, bo IATE to terminologia UE, a nie słownik anatomii.
