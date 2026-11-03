# local: frekwencje, pokrycie SGJP, suplement

## TL;DR
- KWJP: „wulwa”, „vulva” i „wulwodynia” mają 0 trafień we wszystkich 13 listach. Listy „all” zaczynają się od 5 wystąpień, więc każda z tych form ma w KWJP najwyżej 4. Dla porównania „srom” ma 92 wystąpienia (lemat), a „wagina” 194.
- NKJP 1grams (ok. 246 mln tokenów): wulwa razem 6 (wulw 4, wulwa 2), vulva* 4, wulwodynia 0. Dla porównania srom 110, wagina 163, moszna 66.
- SGJP ma wszystkie terminy kontrolne (srom, wagina, pochwa, łechtaczka, penis, prącie, moszna, hymen, sromowy, waginalny). Nie ma wulw*, vulv*, vagina, klitoris ani wulwodynii.
- Suplement przyjmuje dziś tylko lematy z dowodem w KWJP: się ma 1 733 236 wystąpień, siebie 211 982. Wulwa ma w KWJP 0 trafień (mniej niż 5), więc tego precedensu nie spełnia.
- Polityka nie stawia progu frekwencji dla zwykłego rzeczownika. Wiersz w suplemencie wprowadziłby więc 10 form do BROAD i STANDARD. Kontrola: srom, wagina i hymen (anat.) są w obu listach.

## Kluczowe decyzje
- Za formy „wulwa” przyjęto 10 form z listy SJP (`server/lexicons/src/slowa.txt:2859354-2859373`): wulw, wulwa, wulwach, wulwami, wulwą, wulwę, wulwie, wulwo, wulwom, wulwy. Wulwodynia ma osobno 11 form.
- Wartość „pochwa” obejmuje też znaczenie „futerał”, bo listy KWJP nie rozróżniają znaczeń. Liczba jest więc tylko górną granicą.
- Liczby NKJP zsumowano po formach bez interpunkcji i bez rozróżniania wielkości liter, bo 1grams trzyma tokeny takie jak `wulwa,`.

## Otwarte pytania
- Nie wiadomo, czy „wulw” w NKJP (4 wystąpienia, wszystkie pisane małą literą) to dopełniacz l.mn., czy nazwisko. 1grams nie podaje kontekstu.
- Listy v31 z `data/work/lists-v31-20261013-060725-b/lists/` są zapewne tym samym buildem co dawg 20261014, ale tego nie sprawdziłem. SHA dotyczy pliku dawg, a nie txt.

## 1. KWJP (13 list, `cache/kwjp/`)
Polecenie kontrolne, uruchomione dla każdego pliku:
`gzcat $f | grep -a -i -c 'wulw\|vulv'` oraz `gzcat $f | grep -a -i -c '^srom,\|,srom,'`.
Wynik: `wulw|vulv` = 0 w każdym z 13 plików. Kontrola dodatnia `srom` = 1 wiersz w każdej liście słów i 4 wiersze w `2grams-lemma-all`.
Progi: ostatni wiersz `orth_lc-all` i `lemma-all` ma freq 5.0. W podkorpusach są wiersze z freq 1, ale tylko wtedy, gdy `total_freq` ≥ 5. Brak formy oznacza więc łącznie mniej niż 5 wystąpień.

Lematy (`kwjp100-slowa-lemma-*.csv.gz`, skrypt `/private/tmp/claude-501/-Users-robmar-Projects-Literaki/3ae5c44e-c8df-4ef9-924a-bcb0e5eaf7f8/scratchpad/wulwa/freq.py`):

| lemat | all | fakt | fikcja | publ. |
|---|---|---|---|---|
| wulwa / vulva / wulwodynia | 0 (<5) | 0 | 0 | 0 |
| penis | 805 | 393 | 248 | 164 |
| pochwa (oba znaczenia) | 499 | 283 | 156 | 60 |
| łechtaczka | 211 | 115 | 75 | 21 |
| wagina | 194 | 127 | 20 | 47 |
| prącie | 96 | 56 | 34 | 6 |
| sromowy (adj) | 94 | 84 | 4 | 6 |
| srom | 92 | 83 | 4 | 5 |
| moszna | 34 | 17 | 13 | 4 |
| labioplastyka | 7 | 7 | – | – |
| waginoplastyka | 6 | 4 | 1 | 1 |

Bigram `warga,sromowy` = 93 (`kwjp100-2grams-lemma-all.csv.gz`).
Formy (`orth_lc-all`): srom 43, sromu 38, wagina 32, waginy 81, moszna 6, moszny 14.

## 2. NKJP 1grams (`cache/nkjp/1grams.gz`)
Suma liczników: `gzcat 1grams.gz | awk '{s+=$1} END{printf "%d\n", s}'` daje 246 153 378. Plik zawiera też wiersze z freq 1.
Agregacja: `python3 -I /private/tmp/claude-501/-Users-robmar-Projects-Literaki/3ae5c44e-c8df-4ef9-924a-bcb0e5eaf7f8/scratchpad/wulwa/nkjp.py cache/nkjp/1grams.gz`.

| termin | suma | formy |
|---|---|---|
| wulwa | **6** | wulw=4 (`wulw`, `wulw.`), wulwa=2 (`wulwa,`, `wulwa.`) |
| vulva* | **4** | vulva=2, vulvę=1, vulvo=1 (`vulvo!`) |
| wulwodynia* | **0** | – |
| srom | 110 | sromu 49, srom 46, sromów 6 |
| wagina | 163 | waginy 67, wagina 50 |
| vagina* | 57 | vagina 21, vaginy 10 |
| pochwa (oba zn.) | 1268 | pochwy 849 |
| łechtaczka | 292 | łechtaczki 154 |
| penis | 762 | penisa 332 |
| prącie | 205 | prącia 119 |
| moszna | 66 | moszny 22 |
| klitoris/klitor* | 4 | klitorys 1, klitory 2, klitorisem 1 (klitoridektomia osobno: 6) |

Kontrola surowa: `gzcat 1grams.gz | grep -a -i -E '^ *[0-9]+ (wulw|vulv|wulwodyn|klitor)'` zwraca te same tokeny.

## 3. SGJP (`cache/sgjp/sgjp-20260823.tab.gz`, `pl.sgjp.sgjp-2026.08.24`)
Polecenie: `gzcat … | awk -F'\t' '{print $2"\t"$4"\t"$5}' | grep -a -i -E '^(wulw|vulv|vagin|klitor|…)' | sort | uniq -c`.
Kontrola dodatnia w tym samym przebiegu: lemat `Wulw:Sm1` i `Wulw:Sf` (nazwisko, 12+1 wierszy). Wyszukiwanie `wulw` działa, ale znajduje tylko nazwisko.

| termin | SGJP | lemat / kwalifikator |
|---|---|---|
| wulwa, vulva | **brak** | (tylko nazwisko Wulw) |
| wulwodynia, wulwektomia, wulwit* | **brak** | – |
| vagina, klitoris, klitor* | **brak** | – |
| labioplastyka, waginoplastyka, waginizm, cerwiks, uterus | **brak** | – |
| srom | jest, 11 wierszy | `nazwa_pospolita`, `anat.` |
| wagina | jest, 11 | `nazwa_pospolita`, bez etykiety |
| pochwa | jest, 11 | `nazwa_pospolita` |
| łechtaczka | jest, 11 | `anat.` |
| penis | jest, 2×11 (m2, m3) | `anat.` / `rzad.,anat.` |
| prącie | jest, 10 | `anat.` |
| moszna | jest, 11 | `anat.` (+ `Moszna` geogr.) |
| macica, warga, jądro, hymen (`anat.`) | jest | – |
| przymiotniki sromowy, waginalny, pochwowy, łechtaczkowy, mosznowy | jest | – |
| med.: dyspareunia, anorgazmia, endometrioza, histerektomia, mastektomia, pochwica | jest | – |

Lematy z etykietą `anat.`: 69; z `med.`: 195. Oba polecenia mają postać `awk -F'\t' '$5 ~ /anat\./ {print $2}' | sort -u | wc -l`.
SGJP notuje więc polski termin anatomiczny „srom” i przynajmniej jedno zapożyczenie, „wagina”. Brakuje w nim nowszych lub rzadkich zapożyczeń: wulwa, wulwodynia, klitoris i vagina.

Wzór odmiany dla ewentualnego wiersza w suplemencie to `wagina` (11 wierszy, `subst:…:f`, `nazwa_pospolita`, bez etykiety): wagin pl:gen, wagina sg:nom, waginach pl:loc, waginami pl:inst, waginie sg:dat.loc, wagino sg:voc, waginom pl:dat, waginy pl:nom.acc.voc i sg:gen, waginą sg:inst, waginę sg:acc.

## 4. Suplement i polityka
- `config/generator/sgjp-supplement.tab` ma 4 wiersze: się `part` oraz siebie, sobie i sobą w klasie `siebie`. Nagłówek uzasadnia je tak: „brak w eksporcie TSV, obecne w opisie SGJP i w KWJP”.
- `config/generator/sources.json` (`sgjp-supplement-v1`) zawiera `dependencies`: „KWJP jako dowód istnienia lematów”. Są tam też `sha256` pliku, `expected_counts` (records 4, lexemes 2, …) i `evidence` w postaci pliku decyzji z sha256. Dodanie wiersza wymaga więc nowej decyzji oraz aktualizacji sha i liczników.
- `literaki_slownik/inputs.py:16-18,90-92` dopuszcza najwyżej jeden artefakt `lexical_supplement`, pochodzenie `project`, status `ALLOWED` i niepustą listę `evidence`.
- `literaki_slownik/build.py:107` importuje suplement razem z SGJP przez `import_sgjp`, więc dalej jest traktowany jak SGJP.
- `literaki_slownik/policy.py:61-63` dodaje klasę `siebie` do macierzy jako `word`. Nowa klasa nie jest potrzebna, bo `subst` jest już `word`.
- Decyzja-precedens: `.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/round4-sjp-benchmark-fixes-decision.md`, pkt 1.
  - Kryteria: lemat zupełnie nieobecny w eksporcie i istniejący w KWJP. Się ma 1 733 236 wystąpień, siebie 211 982.
  - Szukanie podobnych przypadków: lematy KWJP z co najmniej 30 wystąpieniami porównano z SGJP. W klasach zamkniętych nic więcej nie brakowało.
  - Braki w klasach otwartych, czyli przymiotniki przedrostkowe, zostawiono jako „osobna luka źródła; wymagałaby konstruktora lub nowego źródła i nie wchodzi w tę rundę”.
  - Uwaga z tej decyzji: „SJP.pl nie jest wejściem … Z listy SJP nie skopiowano żadnego słowa”.
- Wpływ ewentualnego wiersza:
  - KWJP podaje frekwencję tylko do zniesienia odmowy za dawność (`CONTEMPORARY_USE_MIN_NONFICTION = 30`, `policy.py:91`, `decisions.py:62`). Nie ma progu wejścia.
  - Kontrola w `data/work/lists-v31-20261013-060725-b/lists/{standard,broad}.txt` (`grep -cx`): srom, sromu, wagina, waginy, moszna, łechtaczka, penis, prącie, hymen i pochwica dają 1/1. Wszystkie 10 form wulwa i wulwodynia dają 0/0.
  - Wiersze wzorowane na `wagina` (bez etykiety) albo na `srom` (`anat.`) dałyby więc 10 nowych słów w BROAD i STANDARD.
