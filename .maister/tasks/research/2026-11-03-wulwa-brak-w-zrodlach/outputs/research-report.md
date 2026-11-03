# Raport: dlaczego „wulwy” nie ma w SGJP, KWJP i Słowosieci

Typ: badanie mieszane · Data: 2026-11-03 · Wykonał: Claude (maister research)

## TL;DR
- „Wulwy” nie ma, bo jest za rzadka. To nowa kalka z ang. *vulva*, a korpusy nie mają jej ani razu: NKJP 0 (nie licząc nazwiska Wulw), KWJP poniżej 5.
- To nie jest luka eksportu. SGJP online, WSJP, SJP PWN i Doroszewski też jej nie mają. Pisownia ani temat tego nie tłumaczą.
- Polskie słowo to „srom”. Słowosieć tłumaczy *vulva* właśnie jako „srom”.
- Rekomendacja: **nie dodawać** do `sgjp-supplement.tab` (wariant A). Ewentualny wpis dałby 10 słów w STANDARD i BROAD. Jego jedynym uzasadnieniem byłoby SJP.pl.

## Kluczowe decyzje
- Do decyzji użytkownika: wariant A (nie dodawać, rekomendowany), B (wyjątek w suplemencie, +10 form) albo C (reguła lub nowe źródło dla luk SGJP, dziś bez wpływu na wulwę).
- Precedens się/siebie nie pasuje. Tamte słowa są w opisie SGJP i mają w KWJP ponad 200 tys. wystąpień. Wulwy nie ma w żadnym z tych dwóch źródeł.

## Otwarte pytania / ryzyka
- Czy wulwodynię (11 form, lemat Słowosieci) traktować tak samo? Rekomendacja: tak, czyli też nie dodawać.
- Słowo może się upowszechnić, bo jest w poradnikach z lat 2020+. Warto wrócić do niego przy nowym wydaniu SGJP albo KWJP.
- Status w bazie SGJP (`cand`) jest niewidoczny. Nie zmienia to wniosku.

## Spis treści
1. Streszczenie · 2. Cel · 3. Metoda · 4. Ustalenia · 5. Hipotezy · 6. Analiza · 7. Odpowiedź · 8. Warianty i rekomendacja · 9. Załączniki

## 1. Streszczenie
Badanie objęło frekwencję w KWJP i NKJP, pokrycie SGJP, pełny zrzut Słowosieci 4.5, IATE, zasady doboru haseł SGJP, słowniki online i poradnie. Mierzyliśmy lokalnie i sprawdziliśmy w źródłach publicznych. Każde zero ma kontrolę dodatnią: „srom”, „wagina” albo „łechtaczka”.

Wynik: wszystkie źródła zgodnie nie mają wulwy, a SGJP ma regułę, która to tłumaczy. Brak nie jest błędem eksportu.

## 2. Cel
- **Pytanie:** dlaczego „wulwa” nie występuje w SGJP, KWJP i jako lemat Słowosieci 4.5, choć SJP.pl ją notuje?
- **Hipotezy:** luka, celowe pominięcie, pisownia, frekwencja.
- **Zakres:** cache projektu, `config/generator`, lexicony serwera, publiczne słowniki i korpusy.
- **Poza zakresem:** kontakt z autorami, Wikisłownik, zmiany w listach.

## 3. Metoda
- 6 plików ustaleń (local ×2, docs ×2, external ×2).
- Lokalnie: 13 list KWJP, NKJP 1grams, eksport SGJP 20260823, zrzut Słowosieci 4.5 (2,63 GB, odczytany w całości strumieniowo), IATE 2019 (1,86 GB).
- Dokumenty: *Podstawy teoretyczne SGJP* (wyd. 4), kod eksportu Kuźni, artykuły o KWJP i NKJP, ADR-011, decyzja rundy 4, benchmarki v25–v29.
- Zewnętrznie: sgjp.pl, PELCRA NKJP, WSJP, SJP PWN, Doroszewski, Słowosieć 5.0, poradnie PWN i RJP, SJP.pl. Odczyt 2026-11-03.
- Rama: cztery hipotezy, każda z dowodami za i przeciw oraz pewnością.

## 4. Ustalenia

### U1. Frekwencja jest zerowa (pewność wysoka)
| Źródło | wulwa | vulva | wulwodynia | kontrola: srom |
|---|---|---|---|---|
| KWJP (lematy, all) | 0 (<5) | 0 (<5) | 0 (<5) | 92 |
| NKJP 1grams (lokalnie, ok. 246 mln) | 6 tokenów = nazwisko | 4 | 0 | 110 |
| PELCRA, zrównoważony (240 mln) | 2 (+ wulw 4), nazwisko | 2 | – | 44 (lemat 103) |
| PELCRA, cały (1,52 mld) | 5, wszystkie nazwisko; inne formy 0 | 10 | 1 (Wikipedia) | 204 (lemat 478) |

**Uzgodnienie NKJP.** Lokalne 1grams pochodzą ze zrównoważonego podkorpusu, nie mają kontekstu i są zapisane małymi literami. Dają wulwa 2 i wulw 4. PELCRA dla tego samego podkorpusu daje dokładnie 2 i 4, a konkordancje to „Jana Wulwa”, „Jan Wulw”. Lokalne 6 to więc nazwisko, a rzeczownik ma 0 wystąpień. Lemat „wulwa” jest PELCRA nieznany.

Źródła: `analysis/findings/local-frekwencje-sgjp-suplement.md` §1–2, `external-korpusy-uzycie.md`.

### U2. SGJP ma temat, nie ma słowa (pewność wysoka)
- Jest: srom (`anat.`), wagina, pochwa, łechtaczka (`anat.`), penis, prącie, moszna, hymen, sromowy, waginalny.
- Nie ma: wulwa, vulva, vagina, klitoris, wulwodynia, wulwektomia, cerwiks, uterus, labioplastyka.
- SGJP ma 69 lematów `anat.` i 195 `med.`.
- W eksporcie „Wulw” to tylko nazwisko. Pochodzi ze słownika Rymuta, który obejmuje nazwiska z co najmniej 50 nosicielami.
- SGJP online: `rows: []` dla wulwa i jej form.

Źródła: `local-frekwencje-sgjp-suplement.md` §3, `docs-sgjp-zasady-doboru.md` §6–7, `external-slowniki.md`.

### U3. Zasada doboru SGJP tłumaczy brak (pewność wysoka)
*Podstawy SGJP*, s. 13: zapożyczenia wchodzą, „jeśli spełniają warunek dostatecznie częstej powtarzalności … w tekstach ostatnich lat”.

Hasła SGJP pochodzą z Doroszewskiego, ze słowników PWN i z korpusów prasowych. W żadnym z nich wulwy nie ma. Nie ma reguły, która wykluczałaby słownictwo anatomiczne. Jedyna reguła „pomijamy specjalistyczne” dotyczy skrótów.

Źródło: `docs-sgjp-zasady-doboru.md` §1–5.

### U4. Słowosieć mówi „srom” (pewność wysoka)
- Zrzut 4.5 nie ma formy „wulwa” w żadnej tabeli. Polskie trafienia to tylko nazwisko Wulw (9) i wulwodynia (20).
- Angielskie *vulva* (LU 487932) ma relację `Syn_plWN-PWN` z {srom}.
- Wulwodynia ma kwalifikator `specj.`, a jej glosa mówi „sromu lub pochwy”.
- Słowosieć 5.0 online też nie ma wulwy.
- IATE nie ma polskiego „wulw*”.

Źródła: `local-slowosiec-iate.md`, `external-slowniki.md`.

### U5. Jedynym źródłem jest SJP.pl (pewność wysoka)
SJP.pl oznacza hasło „w medycynie: srom kobiecy”. W polu „występowanie” podaje listę turniejową innej gry, a nie słownik ogólny. Tak samo jest przy wulwodynii.

W sieci „wulwy/wulwę” pojawia się w poradnikach z lat 2020+, np. leki.pl 2025. Lekarze (mp.pl) piszą „srom”.

Źródło: `external-slowniki.md`, `external-korpusy-uzycie.md`.

### U6. Reguły projektu i precedens (pewność wysoka)
- Suplement ma dziś 4 wiersze: się i siebie (sobie, sobą). Uzasadnienie: „brak w eksporcie TSV, obecne w opisie SGJP i w KWJP”.
- Prompt v3 §3.2 dopuszcza poprawkę tylko wtedy, gdy uzasadnienie jest „niezależne od samej obecności słowa w SJP.pl”.
- Wariant A (`source-extension-decision.md`) mówi: „nie rozszerzać zasobu leksemów”.
- Runda 4 odłożyła słowa nieobecne w samym SGJP (`antydumpingowy`) jako „lukę źródła”.

Źródło: `docs-korpusy-slowosiec-precedensy.md` §5.

| # | Ustalenie | Kategoria | Pewność | Źródła |
|---|---|---|---|---|
| U1 | Frekwencja zerowa | pomiar | wysoka | 4 |
| U2 | SGJP ma temat, nie ma słowa | pokrycie | wysoka | 3 |
| U3 | Zasada powtarzalności | zasady | wysoka | 2 |
| U4 | Słowosieć: vulva → srom | pokrycie | wysoka | 3 |
| U5 | Tylko SJP.pl (lista turniejowa) | zewnętrzne | wysoka | 2 |
| U6 | Precedens nie pasuje | reguły projektu | wysoka | 3 |

## 5. Hipotezy
| Hipoteza | Za | Przeciw | Werdykt |
|---|---|---|---|
| **H1. Luka eksportu** (jak się/siebie) | eksport pomija `cand`, `litt` i `antyMorfeusz` | SGJP online pusty; brak w słownikach źródłowych; brak w KWJP | odrzucona, **wysoka** |
| **H2. Celowe pominięcie** (termin, rejestr) | SGJP bierze terminy „w pewnym zakresie”; wulwodynia ma `specj.` | brak takiej reguły; srom, wagina i łechtaczka są w SGJP | odrzucona, **średnia** (decyzji redakcji nie znamy) |
| **H3. Pisownia** (vulva/wulwa) | — | „vulva” też nigdzie nie jest hasłem; vulva → srom; poradnie milczą | odrzucona, **wysoka** |
| **H4. Frekwencja** | NKJP 0, KWJP <5, brak w słownikach ogólnych, zasada SGJP | — | **przyjęta, wysoka** |

## 6. Analiza
**Wzorce:**
- Granica w SGJP biegnie po frekwencji, nie po temacie. Ugruntowana „wagina” jest (KWJP 194), nowe vagina, klitoris i wulwa nie.
- Wulwodynia przyszła jako nazwa choroby, a rdzeń „wulwa” za nią nie poszedł.

**SWOT dla wariantu „dodać”:**
| Mocne | Słabe |
|---|---|
| słowo jest w poradnikach i ma regularną odmianę (wzór `wagina`) | zero poświadczeń w dopuszczonych źródłach; jedynym dowodem jest SJP.pl |
| **Szanse** | **Zagrożenia** |
| możliwe upowszechnienie w kolejnych wydaniach SGJP i KWJP | łamie §3.2 i wariant A; staje się precedensem dla każdego słowa z różnic SJP |

## 7. Odpowiedź
„Wulwy” nie ma w SGJP, KWJP i Słowosieci, bo nie jest poświadczona w tekstach, na których te źródła stoją. Korpusy jej nie mają, a słowniki ogólne też jej nie notują. SGJP przyjmuje zapożyczenie dopiero przy „dostatecznie częstej powtarzalności”. Polskim terminem jest „srom”.

SJP.pl ma to hasło z listy turniejowej innej gry, a nie ze słownika ogólnego. Dla `sgjp-supplement.tab` znaczy to tyle, że wulwa nie spełnia kryterium precedensu.

## 8. Warianty i rekomendacja

| Wariant | Co robimy | STANDARD | BROAD | Zgodność z regułami | Wysiłek |
|---|---|---|---|---|---|
| **A. Nie dodawać (rekomendowany)** | wpis w decyzjach: „luka źródła, frekwencja”; wracamy przy nowym SGJP lub KWJP | 0 | 0 | pełna | minimalny |
| B. Wyjątek w suplemencie | 11 wierszy wzorem `wagina` | +10 | +10 | łamie §3.2 i wariant A; pierwszy leksem spoza SGJP | mały |
| C. Reguła lub nowe źródło dla luk SGJP | wspólne podejście z `antydumpingowy` | 0 dziś (żadne dopuszczone źródło nie ma wulwy) | 0 dziś | wymaga nowej decyzji o źródłach | duży |

**Dlaczego A.** Wulwa nie spełnia żadnego z dwóch warunków precedensu: obecności w opisie SGJP i w KWJP. Jedynym dowodem jest SJP.pl, a prompt v3 tego zabrania. Tracimy niewiele, bo w Literakach chodzi o 10 rzadkich form, a „srom” jest w listach.

**Formy, których dotyczy wariant B (10):** wulwa, wulwy, wulwie, wulwę, wulwą, wulwo, wulw, wulwom, wulwami, wulwach. W tagsecie SGJP to 11 wierszy, bo „wulwy” ma dwa tagi: sg:gen i pl:nom.acc.voc. Dziś żadnej z tych form nie ma w `standard.txt` ani `broad.txt` (v31). Żaden filtr by ich nie zatrzymał, bo nie ma progu frekwencji wejścia. Kontrola: srom i wagina są w obu listach.

**Co wymagałby wiersz w suplemencie (B):**
1. Decyzja użytkownika o rozszerzeniu zasobu leksemów poza SGJP. Uchyla ona wariant A, więc trzeba nowego pliku decyzji z dowodami. Dowody z dopuszczonych źródeł dziś nie istnieją, a SJP.pl nie może nim być.
2. 11 wierszy w `config/generator/sgjp-supplement.tab`. Wzór to `wagina`: `subst:…:f`, `nazwa_pospolita`, opcjonalnie `anat.` jak przy `srom`. Do tego zmiana nagłówka, bo obecne uzasadnienie („obecne w opisie SGJP i w KWJP”) przestałoby być prawdziwe.
3. `config/generator/sources.json` (`sgjp-supplement-v1`):
   - nowy `sha256` pliku;
   - `expected_counts`: records 4 → 15, lexemes 2 → 3, pozostałe liczniki do przeliczenia;
   - `evidence` z sha256 nowego pliku decyzji;
   - poprawka `dependencies`, bo „KWJP jako dowód istnienia lematów” nie dotyczyłoby wulwy.
4. Nowy build i benchmark. Wycofanie to usunięcie wierszy i ponowny build.

## 9. Załączniki

### Źródła (pliki ustaleń)
- `analysis/findings/local-frekwencje-sgjp-suplement.md`
- `analysis/findings/local-slowosiec-iate.md`
- `analysis/findings/docs-sgjp-zasady-doboru.md`
- `analysis/findings/docs-korpusy-slowosiec-precedensy.md`
- `analysis/findings/external-slowniki.md`
- `analysis/findings/external-korpusy-uzycie.md`
- Synteza: `analysis/synthesis.md`

### Luki
- Brak liczbowego progu SGJP dla wyrazów pospolitych.
- Status w Kuźni jest niewidoczny.
- Historia hasła w SJP.pl jest nieznana.
- Frekwencji w internecie nie zmierzono.
- Nie sprawdzono, czy listy v31 to ten sam build co dawg 20261014.

### Uwagi metodyczne
Skrypty pomocnicze leżą w scratchpadzie sesji (`…/scratchpad/wulwa/`). Dane w `cache/` czytano tylko do odczytu.
