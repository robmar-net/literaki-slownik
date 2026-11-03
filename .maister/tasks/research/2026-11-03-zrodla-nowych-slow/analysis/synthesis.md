# Synteza: źródła nowych, popularnych słów

## TL;DR
- Nie ma naukowego źródła nowych słów, które wolno wciągnąć do generatora. Jedynym źródłem leksemów zostaje SGJP (+ `sgjp-supplement.tab`). SGJP rośnie wolno: eksport 20261018 dodaje 2 lematy.
- Najlepsze naukowe rejestry (OJ UW, WSJP PAN) nie mają licencji danych. Nadają się tylko na ręczny dowód w decyzji użytkownika.
- Dowód użycia po 2020 roku mogą dać ParlaMint-PL 5.0 i Leipzig news (CC BY 4.0, z datami). Korpusy sieciowe (FineWeb-2, HPLT) mają najlepsze pokrycie, ale nieustaloną licencję tekstu.
- Metoda progowa działa dziś na parze NKJP → KWJP (lata 2011–2020): 374 kandydatów, około 65% trafnych. Łapie hejt, lockdown, covidowy, influencerkę i antyszczepionkowca. Nie łapie wulwy, ghostingu, cringe ani boomera.
- Wulwy nie ma w żadnym dopuszczonym źródle. Jest tylko w kilku dokumentach sieciowych. Dziś da się ją dodać jedynie przez suplement v2, i to wyłącznie decyzją użytkownika.

## Kluczowe decyzje
- Rozdzielam trzy role i trzymam się ich w całym tekście: **(a) źródło leksemów** (SGJP, suplement), **(b) dowód użycia** (`corpus_evidence`, liczby z korpusu), **(c) dowód ręczny** (link i data odczytu w karcie kandydata).
- Poprawiam błąd planu. W `sources.json` jest **13 artefaktów KWJP**, nie 15. Liczba 15 obejmuje też SGJP i suplement (sprawdzone: 4 + 4 + 4 + 1 KWJP, 1 `sgjp_tab`, 1 `lexical_supplement`).
- Zmiany składu list zostawiam jako otwarte decyzje użytkownika. Nic tu ich nie przesądza.

## Otwarte pytania i ryzyka
- Użycie NKJP w metodzie wykracza poza ADR-006 (POP, POP0). Bez decyzji metoda nie ma podstawy formalnej.
- Licencja tekstu w FineWeb-2 i HPLT jest nieustalona. Bez decyzji to źródło jest zablokowane.
- Trafność 65% oceniał jeden agent, bez konkordancji. Pewność średnia.
- Leipzig: strona i API mają CC BY-NC, korpusy do pobrania CC BY 4.0. Trzeba trzymać się wyłącznie plików do pobrania.

---

## 1. Pytanie
Czy istnieją dobre, naukowe i wiarygodne źródła słów, które są w polszczyźnie od niedawna, ale są popularne (np. „wulwa”)? Jak literaki-slownik może takie słowa systematycznie wychwytywać?

## 2. Analiza krzyżowa

### Potwierdzone przez kilka źródeł (pewność wysoka)
| Ustalenie | Źródła |
|---|---|
| SGJP nie ma antyszczepionkowca ani boomera (jest tylko `bumer`) | SGJP 20260823 i 20261018 (`neolog-slowniki`, `projekt-kontrole-lokalne`) |
| Antyszczepionkowiec to prawdziwa luka SGJP | OJ UW (2022-03-25), WSJP, PWN, Słowosieć 4.5, KWJP F=34, ParlaMint 93 |
| KWJP obejmuje lata 2011–2020, a NKJP teksty do 2010 | `cache/kwjp/article.pdf`, `overview.html`, artykuł NeoN |
| Wulwy nie ma w żadnym słowniku ani rejestrze | OJ UW (nowa, stara, negver), WSJP, PWN, SGJP, Miejski, Słowosieć 4.5 |
| Wulwy nie ma w korpusach z czystą licencją | KWJP <5, ParlaMint 0, LCC news 2024 0 |
| Ghosting jest rzadki i ma szum („Anti-ghosting”) | FineWeb-2, Wikipedia, LCC (3) |
| ParlaMint pokazuje datę wejścia słowa | lockdown i covidowy: 0 do 2019, od 2020 setki; antyszczepionkowiec: 78 w 2021 |

### Sprzeczności i ich wyjaśnienie
- **Hejt: „nowy” czy „stary”?** OJ UW odrzuca go (negatywna weryfikacja, poświadczenia sprzed 2003). Dla nas jest nowy, bo NKJP ma 2 wystąpienia, a KWJP 366. Wyjaśnienie: inne kryteria. OJ UW pyta „po 2003 i poza 8 słownikami”, my pytamy „poza SGJP”. **Brak w OJ UW nie znaczy, że słowo nie jest nowe.**
- **Influencerka, covidowy w OJ UW.** Są na starej witrynie (do 2021), nie ma ich na nowej. To luka migracji, nie decyzja redakcji (pewność średnia).
- **Boomer.** W WSJP i PWN WSO jest, w KWJP F=5, w HPLT 79 trafień, w ParlaMint 0. HPLT to prawdopodobnie nazwy i marki, a NKJP (10) to angielskie *baby boomer*. Liczby korpusowe dla boomera są niewiarygodne bez filtra wielkiej litery i kontekstu.
- **Wulwa w Wikipedii (64 strony, „wulwy” 153).** To głównie termin zoologiczny (anatomia pajęczaków), nie nowe znaczenie. Liczba stron nie jest więc dowodem popularności.
- **Liczba artefaktów KWJP.** Plan i `sources.md` mówią 15, kod i `sources.json` mają 13. Poprawne: 13 KWJP, 15 razem z SGJP i suplementem.
- **MADLAD-400.** Karta podaje naraz `odc-by` i „CC-BY-4.0”. Sprzeczności nie da się rozstrzygnąć bez kontaktu, więc źródło jest BLOCKED.

### Pewność ustaleń
- **Wysoka:** licencje (cytaty dosłowne z URL i datą), stan SGJP, kontrole w SGJP, KWJP, NKJP, ParlaMint, okresy KWJP i NKJP, wymagania kodu (`inputs.py`).
- **Średnia:** trafność metody (65%), wyniki w próbkach sieciowych (<0,03% korpusu), luki migracji OJ UW.
- **Niska:** okres PPC po 2018, licencja Spokes, dostępność MoncoPL.

## 3. Wzorce

| # | Wzorzec | Dowód | Zasięg |
|---|---|---|---|
| W1 | **Licencja jest odwrotnie proporcjonalna do świeżości.** Im szybciej źródło notuje nowe słowa, tym gorsza licencja. | OJ UW, WSJP, MSR, MoncoPL bez licencji; SGJP i KWJP z licencją, ale wolne lub stare | wszystkie 26 źródeł |
| W2 | **Licencja opakowania to nie licencja tekstu.** | FineWeb-2 (ODC-By), HPLT i OSCAR (CC0): „We do not own any of the text” | korpusy z Common Crawl |
| W3 | **Bramka dostępu wyklucza źródło.** Formularz albo konto oznacza BLOCKED. | Słowosieć 5.0, OSCAR, CulturaX | 3 źródła |
| W4 | **Różne kryteria „nowości”.** | OJ UW (po 2003), NeoN (poza NKJP i KWJP), projekt (poza SGJP) | 3 definicje |
| W5 | **Szum z tej samej rodziny:** błędne lematy, nazwy własne, angielskie frazy, terminy specjalistyczne. | `wielkanoca`, `lubiać`; boomer w HPLT; Anti-ghosting; wulwa zoologiczna | każdy korpus |
| W6 | **Rejestr korpusu decyduje o tym, co widać.** | ParlaMint: covid tak, influencerka 1, wulwa 0; LCC news: influencerka 96 | ParlaMint, LCC |

## 4. Kluczowe spostrzeżenia

1. **Problem ma dwie warstwy i trzeba je rozdzielić.** Wykrywanie (czy słowo jest nowe i popularne) da się zrobić na korpusach. Wejście do list zależy od źródła leksemów z fleksją i licencją, a takiego źródła poza SGJP nie ma. — pewność wysoka.
2. **Pierwszym ograniczeniem jest polityka, nie technika.** Wariant A („nie rozszerzać zasobu leksemów”) blokuje każde słowo spoza SGJP, nawet z najlepszym dowodem. Kod przyjmuje najwyżej 1 suplement i dokładnie 13 slotów KWJP. — pewność wysoka.
3. **Najtańszy dobry kandydat to antyszczepionkowiec.** Ma dowód ręczny (OJ UW, WSJP), dowód użycia (KWJP 34, ParlaMint 93) i potwierdzenie w Słowosieci. Jest dobrym wzorcem pierwszej decyzji o suplemencie v2. — pewność wysoka.
4. **Metoda działa, ale tylko na latach 2011–2020.** Para NKJP → KWJP łapie 5 z 5 kontroli celu. Słowa po 2020 roku wymagają nowego korpusu z datami. — pewność średnia-wysoka.
5. **Wulwa nie jest jeszcze „popularna” w żadnym mierzalnym sensie.** Ma 2 dokumenty w próbce FineWeb-2, 3 w próbce HPLT i 0 w korpusach z czystą licencją. Metoda słusznie jej nie łapie. — pewność średnia (próbki są małe).
6. **NeoN (IPI PAN) potwierdza metodę z zewnątrz.** Ma podobne progi (DF > 5, ≥ 5 wystąpień małą literą) i podobny lejek. Nie udostępnia jednak danych. — pewność wysoka.

## 5. Relacje i przepływ

```
 (c) dowód ręczny          (b) dowód użycia                 (a) źródło leksemów
 OJ UW, WSJP, PWN,         KWJP100 [ALLOWED]                SGJP [ALLOWED]
 MSR, Miejski (kontrola)   NKJP 1grams [ADR-006: POP]       sgjp-supplement.tab [v1: 4 formy]
        |                  ParlaMint, LCC [kandydaci]              ^
        |                  FineWeb-2, HPLT [do decyzji]            |
        |                          |                               |
        |                  metoda progowa -> lista kandydatów      |
        |                          |                               |
        +------------> karta kandydata (liczby + przykłady + linki)
                                   |
                         decyzja użytkownika
                     (uchyla wariant A dla słowa)
                                   |
                  suplement v2 (ręczna fleksja z wzoru SGJP) ----+
```

Punkty styku w kodzie: `literaki_slownik/inputs.py` (`KINDS`, reguła `14 + supplements`, `supplements ≤ 1`), `build.py:107`, `config/generator/sources.json`.

## 6. Luki i niepewności
- Brak historii dat dodania haseł do SGJP. Kalibracji „przed wejściem do SGJP” nie da się zrobić. Zastępuje ją kalibracja „przed 2011 / 2011–2020”.
- Miara wzrostu g jest zgrubna: porównuje lemat KWJP z formą NKJP. Przy tych samych progach przechodzi 2 313 lematów, które już są w SGJP.
- ParlaMint liczono wzorcem na formach w `.txt`. Nie sprawdzono, czy wersja z anotacją ma lematy z tym samym tagerem co w innych korpusach.
- Próbki sieciowe: FineWeb-2 15,1 mln słów, HPLT 67,4 mln słów. „Brak” w próbce nie znaczy brak w korpusie.
- Leipzig ma zdania przetasowane i tylko formy (bez lematów). Brakuje roczników 2019–2020 i 2025.
- Licencja wpisów OJ UW i WSJP: do ustalenia tylko kontaktem, a kontakt jest zabroniony. Zostaje BLOCKED jako wejście.

## 7. Synteza według ramy

### Stan obecny (literatura i źródła)
- **Rejestry neologizmów:** jedynym naukowym słownikiem online jest OJ UW (2756 haseł, ostatnie z 2026-10-30, 280 haseł w 2026). Nie znaleziono podobnych słowników UJ, UŁ ani UG. Słowniki drukowane IJP PAN dotyczą lat 2001–2005.
- **Słowniki ogólne:** WSJP PAN (100 tys. haseł, ma leksykę XXI w.), SGJP (BSD-2, wolny), PWN (tylko użytek osobisty), Słowosieć 5.0 (formularz).
- **Plebiscyty:** MSR (PWN) i Słowo Roku (UW, FJP) dają sygnał popularności, ale bez danych i bez licencji.
- **Korpusy z datami:** ParlaMint-PL 5.0, Leipzig news, FineWeb-2, HPLT, MoncoPL (tylko wyszukiwarka), PPC (okres do ustalenia).
- **Metody:** NeoN (2025), frekwencja w okresach, porównanie list.

### Kompromisy (dowód użycia po 2020)
| Opcja | Plus | Minus | Kiedy |
|---|---|---|---|
| ParlaMint-PL 5.0 | CC BY 4.0, daty dzienne, 37 mln słów | jeden rejestr (polityka), kończy się w 06.2022, za mały na F ≥ 20 przy rzadkich słowach | słowa polityczne i społeczne |
| Leipzig news | CC BY 4.0, roczniki do 2024, gotowe liczby | ~15,7 mln tokenów na rocznik, tylko formy, brak 2019–2020 | potwierdzenie w prasie |
| FineWeb-2 / HPLT | ogromne, daty i URL, da się wykluczyć sjp.pl | licencja tekstu nieustalona, dużo szumu, pobranie ≫ 2 GB | po decyzji prawnej użytkownika |
| tylko KWJP + NKJP | już w repo, skalibrowane | tylko 2011–2020; NKJP poza zakresem ADR-006 | dziś, dla starszych luk |

### Zastosowanie w projekcie
- Pasuje dziś: SGJP 20261018 (droga A), metoda NKJP → KWJP jako lista kandydatów (po rozszerzeniu ADR-006), OJ UW i WSJP jako dowód ręczny.
- Pasuje po decyzji: ParlaMint i Leipzig jako narzędzie do szukania kandydatów. Jako `corpus_evidence` w buildzie wymagają zmiany kodu.
- Nie pasuje: SJP.pl, PoliMorf, OSCAR, CulturaX, MADLAD-400, CC-100, Słowosieć 5.0. Wikisłownik jest odroczony decyzją użytkownika z 2026-10-04.

## 8. Wnioski
**Główne:**
1. Wiarygodne naukowe źródła nowych słów istnieją (OJ UW, WSJP PAN, NeoN jako metoda), ale żadne nie ma licencji danych. Nie mogą być źródłem leksemów. Mogą być dowodem ręcznym. — pewność wysoka.
2. Systematyczne wychwytywanie jest możliwe: korpus z datami, progi, lista kandydatów, decyzja użytkownika, suplement v2. Dla lat 2011–2020 jest gotowe. Dla lat po 2020 potrzeba nowego korpusu (ParlaMint, Leipzig, ewentualnie FineWeb-2 lub HPLT). — pewność średnia-wysoka.
3. Wulwy nie da się dziś dodać z żadnego źródła. Jedyna droga to suplement v2 z ręczną fleksją (wzór `wagina`), z wyraźną decyzją użytkownika, przy słabym dowodzie. — pewność wysoka.

**Dodatkowe:**
- SGJP 20261018 to bezpieczne, ale małe podbicie (`muralista`, `muralistka`).
- Metoda ujawnia też starsze luki: neoliberalny, prorosyjski, postsowiecki, performans, superbohater, kryptowaluta. Formacje z `anty-` i `post-` wymagają osobnych decyzji (§2.4).
- Reforma pisowni RJP od 2026 może zmienić formy w listach. To osobny temat.
