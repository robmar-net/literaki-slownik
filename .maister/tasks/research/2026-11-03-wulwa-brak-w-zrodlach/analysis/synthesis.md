# Synteza: „wulwa” poza SGJP, KWJP i Słowosiecią

## TL;DR
- „Wulwy” brakuje z powodu frekwencji. To rzadka, świeża kalka z ang. *vulva*. Korpusy, na których stoją SGJP i KWJP, jej nie poświadczają.
- To nie jest luka eksportu jak przy się/siebie. SGJP online też jej nie ma. Nie ma jej też w WSJP, SJP PWN ani u Doroszewskiego.
- Pisownia ani celowe pominięcie tematu tego nie tłumaczą. SGJP ma srom, waginę i łechtaczkę z `anat.`, a „vulva” też nigdzie nie ma hasła.
- Jedyne źródło leksykograficzne to SJP.pl. To hasło bierze się z listy turniejowej innej gry.
- Wniosek dla suplementu: wpis nie spełnia precedensu. Rekomendacja: nie dodawać (wariant A). Decyzja należy do użytkownika.

## Kluczowe decyzje
- NKJP 1grams i PELCRA się zgadzają. Lokalne 6 wystąpień (wulw 4, wulwa 2) to dokładnie te same liczby co w zrównoważonym podkorpusie PELCRA. Konkordancje pokazują, że to nazwisko Wulw. Rzeczownik ma 0 wystąpień.
- Liczba form: **10** („wulwa” ma 10 różnych form). W SGJP-owym tagsecie to 11 wierszy, bo „wulwy” pojawia się dwa razy (sg:gen i pl:nom.acc.voc). Stąd wcześniejsze „11”. Wulwodynia ma osobno 11 form.

## Otwarte pytania
- Czy „wulwa” leży w Kuźni SGJP jako `cand`? Nie da się tego sprawdzić. Dla decyzji to bez znaczenia, bo eksport i SGJP online jej nie mają.
- Wulwodynia jest lematem Słowosieci 4.5 i 5.0 (`specj.`). Słowosieć nie jest jednak źródłem leksemów (ADR-011). Czy to osobna sprawa do decyzji?

## 1. Pytanie
Czemu „wulwa” jest w SJP.pl, a nie ma jej w SGJP, KWJP i jako lematu Słowosieci 4.5? Co z tego wynika dla `sgjp-supplement.tab` oraz list STANDARD i BROAD?

## 2. Analiza krzyżowa

### Potwierdzone przez wiele źródeł (wysoka pewność)
| Ustalenie | Źródła |
|---|---|
| Rzeczownik „wulwa” ma 0 poświadczeń w NKJP | local 1grams (6 tokenów), PELCRA (te same 2+4 w zrównoważonym, 5 w całym, wszystkie to nazwisko), lematyzator PELCRA nie zna lematu |
| KWJP: mniej niż 5 wystąpień | 13 list, 0 trafień, próg 5 z dokumentacji list |
| Brak w SGJP: w eksporcie i online | eksport 20260823 ma tylko nazwisko Wulw; `search-by-form` online daje `rows: []` |
| Brak w słownikach ogólnych | WSJP, SJP PWN, Doroszewski; wszystkie mają „srom” (kontrola dodatnia) |
| Brak w Słowosieci 4.5 i 5.0 | pełny zrzut 4.5 przeczytany strumieniowo (2,63 GB) i API 5.0; vulva (PWN) → {srom} |
| Polski termin to „srom” | Słowosieć, IATE („sromu i pochwy”), mp.pl, literatura fachowa |

### Sprzeczności rozwiązane
- **NKJP: 6 czy 0?** 1grams to zrównoważony podkorpus (ok. 246 mln tokenów) bez kontekstu i z wielkością liter sprowadzoną do małych. PELCRA dla zrównoważonego (240 mln) daje dokładnie wulwa 2 i wulw 4, a konkordancje to „Jana Wulwa”, „Jan Wulw” itd. Lokalne 6 to więc nazwisko. Rzeczownik: 0. Pewność wysoka.
- **10 czy 11 form?** 10 różnych form, 11 wierszy tagsetu (podwójne „wulwy”).
- **SGJP online nie ma nazwiska Wulw, a eksport ma.** To różnica wersji lub widoczności słownika nazwisk. Nie dotyczy rzeczownika.

## 3. Wzorce
1. **Zapożyczenie łacińsko-angielskie w spolszczonej pisowni bez poświadczeń.** SGJP nie ma też: vagina, klitoris, wulwodynia, wulwektomia, cerwiks, uterus, labioplastyka. Ma za to dawniej ugruntowaną „waginę” (KWJP 194, NKJP 163). Granica biegnie po frekwencji, nie po temacie.
2. **Temat ciała jest w SGJP opisany.** 69 lematów `anat.`, 195 `med.`, w tym srom, łechtaczka, prącie, moszna, hymen. Nie ma reguły wykluczającej.
3. **Wulwodynia przyszła przed wulwą.** Nazwa choroby trafiła do Słowosieci (`specj.`, glosa z Wikipedii) i do poradników. Rdzeń „wulwa” nie poszedł za nią. Glosa samej wulwodynii mówi „sromu”.
4. **SJP.pl jako jedyne źródło.** Hasła „wulwa” i „wulwodynia” mają w SJP.pl to samo pole „występowanie”: listę turniejową innej gry. To nie jest słownik ogólny.

## 4. Kluczowe wnioski
| # | Wniosek | Pewność |
|---|---|---|
| 1 | Brak w SGJP wynika z zasady „dostatecznie częstej powtarzalności w tekstach ostatnich lat” (*Podstawy SGJP*, s. 13). Wulwa jej nie spełnia. | wysoka |
| 2 | Słowo jest nowsze niż korpusy: NKJP kończy się na 2010, KWJP to lata 2011–2020 bez internetu. Poświadczenia sieciowe są z lat 2020+ (leki.pl 2025). | średnia (dane sieciowe to zliczenia na stronach, nie frekwencja) |
| 3 | Precedens suplementu (się/siebie: opis SGJP + KWJP ponad 200 tys.) tu nie pasuje. Wulwa jest w klasie „luka źródła” jak `antydumpingowy`. | wysoka |
| 4 | Jedynym uzasadnieniem byłaby obecność w SJP.pl, a prompt v3 §3.2 to wyklucza. | wysoka |
| 5 | Wpis w suplemencie dałby 10 nowych słów w BROAD i STANDARD. Nie ma filtra, który by je zatrzymał (brak progu frekwencji wejścia). | wysoka |

## 5. Relacje
```
SJP.pl ──(lista turniejowa innej gry)── wulwa, wulwodynia
SGJP  ← Doroszewski, PWN, korpusy prasowe, NKJP      → brak wulwy (frekwencja)
KWJP  ← książki + prasa 2011–2020, próg 5, lematy z SGJP → brak (<5)
Słowosieć ── vulva(PWN) ⇄ {srom}; wulwodynia (specj.) → brak wulwy
Generator: SGJP-eksport + sgjp-supplement.tab → BROAD → STANDARD
```

## 6. Ocena hipotez
| Hipoteza | Za | Przeciw | Werdykt |
|---|---|---|---|
| H1 luka eksportu (jak się/siebie) | eksport pomija `cand`/`litt`/`antyMorfeusz` | SGJP online pusty; brak w słownikach źródłowych SGJP; brak w KWJP | odrzucona, **wysoka** |
| H2 celowe pominięcie (termin, rejestr) | SGJP bierze terminy „w pewnym zakresie”; wulwodynia ma `specj.` | brak takiej reguły; srom, wagina, łechtaczka są; jedyna reguła „specjalistyczne” dotyczy skrótów | odrzucona jako przyczyna, **średnia** (nie znamy decyzji redakcji) |
| H3 pisownia (vulva) | — | „vulva” też nie ma hasła; Słowosieć mapuje vulva → srom; poradnie milczą | odrzucona, **wysoka** |
| H4 frekwencja / brak poświadczeń | NKJP 0, KWJP <5, brak w słownikach ogólnych, zasada SGJP o powtarzalności | — | przyjęta, **wysoka** |

## 7. Luki
- Brak liczbowego progu SGJP dla wyrazów pospolitych.
- Status w Kuźni (`cand`) jest niewidoczny.
- Historia hasła w SJP.pl jest nieznana (pierwszy komentarz 2020-07-29).
- Frekwencji w internecie nie zmierzono; to tylko zliczenia na wybranych stronach.

## 8. Wnioski
- **Główny:** wulwa nie jest ugruntowanym leksemem w źródłach projektu. Brak wynika z frekwencji, a nie z błędu eksportu, tematu czy pisowni.
- **Drugorzędny:** wulwodynia to ten sam przypadek po stronie SGJP i KWJP. Różni się tylko lematem w Słowosieci, która nie jest źródłem leksemów.
- **Rekomendacja:** nie dodawać. Warianty są w raporcie.
