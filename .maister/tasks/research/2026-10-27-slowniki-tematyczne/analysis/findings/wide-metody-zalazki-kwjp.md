# Metoda E1: zalążki i sąsiedzi w n-gramach KWJP100 (pilotaż)

## TL;DR
- Na lokalnych bigramach lematów KWJP100 metoda daje mało i z dużym szumem.
- Precyzja top 50 (ścisła): morze 5–7/50, rolnictwo 8–10/50, matematyka 1–2/50.
- Odzyskane oczywiste słowa spoza zalążków: morze 9/28, rolnictwo 3/35, matematyka 3/27 (w całej liście kandydatów).
- Przyczyna: sąsiad w bigramie to kolokacja („Morze Bałtyckie”, „pole karne”, „liczba zgonów”), nie słowo tematu. Rdzeń SGJP prawie nie występuje w korpusie.
- Wariant „podobieństwo kontekstów” (PPMI + cosinus) jest gorszy: top 50 to praktycznie sam szum.

## Key Decisions
- Dane: tylko pliki lokalne. `cache/kwjp/kwjp100-2grams-lemma-all.csv.gz` (1 627 127 wierszy, próg 5, 62,6 mln wystąpień par) i `kwjp100-slowa-lemma-all.csv.gz` (część mowy). Plików 3- i 4-gramów nie pobierałem.
- Zalążki: rdzeń SGJP z rundy 1 (`theme_*.pkl`) plus 7–8 słów dodanych ręcznie, spoza listy testowej:
  - morze: `morze morski żegluga żeglarz rejs port marynarka`;
  - rolnictwo: `rolnik rolnictwo rolniczy gospodarstwo uprawa pole plon wieś`;
  - matematyka: `matematyka matematyczny liczba geometria algebra wzór obliczać`.
- Wariant główny C: rdzeń bez homonimów (odrzucam leksem, jeśli jego lemat ma w SGJP też leksem bez etykiety tematu) + słowa dodane. Rdzeń po czyszczeniu: 233 / 80 / 59 leksemów (z 254 / 96 / 62).
- Ranking: log-likelihood (G²) dla pary „kandydat × zbiór zalążków”, tylko PMI > 0. Kandydat: lemat małą literą, jest w SGJP, dominująca część mowy to słowo pełne, bez listy zaimków i liczebników.
- Wariant „min2”: kandydat musi sąsiadować z ≥2 różnymi zalążkami.
- Test: oczywiste słowa z `cover.py` rundy 1 (`local-data-sgjp-dziedziny.md`), bez tych, które są zalążkami.
- Ocena precyzji: jeden oceniający (ja). „Ściśle” = słowo samo należy do tematu. „Luźno” = należy tylko w typowej kolokacji (np. `bałtycki`, `fala`).

## Open Questions / Risks
- Jeden oceniający; precyzja to szacunek.
- Pliki 3/4-gramów lematów są w repozytorium `kwjp100-varia` (26,5 MB i 9,4 MB wg `cache/kwjp/tree.json`), ale nie lokalnie. Szersze okno może trochę pomóc; nie sprawdzone.
- Lematy KWJP nie mają numeru homonimu SGJP. Jeden leksem homonimiczny potrafi zdominować wynik (niżej: `dzień:Sf`).

## Polecenia
Skrypty: `/private/tmp/claude-501/-Users-robmar-Projects-Literaki/7eed58b5-7e1f-4a3f-8359-d9bc24330c2b/scratchpad/metody/`
- `seed.py` (A, B), `seed2.py` / `seed3.py` (A–D, czyszczenie homonimów, filtr POS), argument `1` lub `2` = minimalna liczba zalążków.
- `python3 seed3.py 1`, `python3 seed3.py 2` → `seed3-results-min{1,2}.json`, `out3-min{1,2}.txt`. Czas ~6 s.
- `seeds_top.py` — które zalążki mają największą masę w bigramach.
- `dist.py` → `dist-results.json` (wariant kontekstowy).

## Wyniki: odzysk oczywistych słów

Liczba słów testowych odzyskanych w rankingu. Kandydatów jest mniej niż 1000, więc „@1000” = cała lista.

| Temat | Wariant | Zalążki (w KWJP) | Kandydaci | Test | @50 | @200 | wszystkie |
|---|---|---:|---:|---:|---:|---:|---:|
| Morze | A rdzeń | 254 (34) | 80 | 27 | 3 | 3 | 3 |
| Morze | C czysty + dodane | 240 (32) | 479 | 28 | 1 | 4 | 9 |
| Morze | C, min2 | 240 (32) | 87 | 28 | 3 | 3 | 3 |
| Morze | D tylko dodane | 7 (7) | 468 | 37 | 1 | 3 | 7 |
| Rolnictwo | A rdzeń | 96 (9) | 1048 | 35 | 0 | 0 | 0 |
| Rolnictwo | C czysty + dodane | 88 (10) | 590 | 35 | 1 | 3 | 3 |
| Rolnictwo | C, min2 | 88 (10) | 120 | 35 | 1 | 1 | 1 |
| Matematyka | A rdzeń | 62 (17) | 251 | 27 | 0 | 0 | 1 |
| Matematyka | C czysty + dodane | 66 (23) | 977 | 27 | 0 | 1 | 3 |
| Matematyka | C, min2 | 66 (23) | 129 | 27 | 0 | 1 | 1 |

Odzyskane (C, min1): morze `burta jacht nabrzeże okręt pokład statek ster sternik sztorm`; rolnictwo `ciągnik orać zboże`; matematyka `funkcja kąt równanie`.
Nieodzyskane m.in.: `kotwica maszt żagiel`, `pług brona kombajn ul`, `ułamek sinus pierwiastek trójkąt`.

Wkład zalążków: z rdzenia SGJP w bigramach jest tylko 32/240 (morze), 10/88 (rolnictwo), 23/66 (matematyka). Wariant D (same słowa dodane) daje prawie to samo co C. **Rdzeń SGJP prawie nic nie wnosi do tej metody.**

## Wyniki: top 50 i precyzja (wariant C)

**Morze, min1** (ściśle 5/50, luźno 21/50):
`śródziemny lotniczy wojenny śródlądowy bałtycki gospodarka czarny kieszeń latarnia owoc kaspijski brzeg statek północny polski szczeciński centralny mila dno komunikacyjny basen egejski świnka zarząd fala gdyński woda azowski wzburzyć wybrzeże klapa akademia karaibski poziom bryza transport kapitan drzewny czerwony szum farma sól bagażowy tweedowy zewnętrzny gdański jachtowy poła droga urząd`

**Morze, min2** (ściśle 7/50, luźno 16/50): `… brzeg statek … dno … fala woda wybrzeże akademia kapitan … głębina rzeczny … akwen katastrofa … stocznia pokład kontenerowy … wiatr … jacht baza obsługa`.

**Rolnictwo, min1** (ściśle 8/50, luźno 14/50):
`domowy karny widzenie rolny bitwa minister mieszkaniec uprawny okoliczny manewr rozwój agroturystyczny magnetyczny polski mokotowski walka minowy namiotowy krajowy golfowy konopie ciągnik bank rodzinny sąsiedni ministerstwo modernizacja bitewny elizejski kukurydza ekologiczny maszyna szczery pobliski doradztwo wiejski pasieczny skraj kolektywizacja pacyfikacja marsowy martwy mały indywidualny sołtys elektromagnetyczny zaorać prowadzić środek winorośl`
Szum pochodzi głównie z zalążka `pole` (pole karne, widzenia, bitwy, minowe, magnetyczne, golfowe; Pola Elizejskie, Pole Mokotowskie, Pole Marsowe).

**Rolnictwo, min2** (ściśle 10/50, luźno 18/50): `rolny … kukurydza … kolektywizacja … roślina hektar sprzęt kółko … zboże … spółdzielnia … rzepak trzcina leśny … las uprawiać … bawełna … burak …`.

**Matematyka, min1** (ściśle 1/50, luźno 5/50):
`metr duży osoba wzrost mnogi rosnąć zwiększyć zmniejszyć ludność wzrosnąć zakażenie zgon mały spadek ofiara rekordowy ogólny zakazić ogromny ograniczyć odpowiedni zachorować mieszkaniec punkt łączny wystarczający powierzchnia pasażer techniczny wzrastać niewielki niezliczony określony uczeń uczestnik pojedynczy urodzenie głos wzgląd ograniczony fizyka nieskończony znaczny geometryczny maksymalny spory dowolny przyrodniczy dokładny zwiększać`
Szum pochodzi z zalążka `liczba` (liczba osób, zakażeń, zgonów) i z `kwadratowy` (metr kwadratowy).

**Matematyka, min2** (ściśle 2/50: `suma`, `nawias`; luźno 7/50).

## Dlaczego tak słabo
1. **Bigram = sąsiad w tekście.** Przy rzeczowniku stoją przymiotniki i rzeczowniki w dopełniaczu. Dostajemy kolokacje zalążka, nie słownictwo tematu.
2. **Zalążki wieloznaczne dominują.** Jeden częsty zalążek (`pole`, `liczba`, `morze`) daje większość masy.
3. **Homonimy SGJP.** W wariancie A rolnictwa `dzień:Sf` (miara pola) ma w bigramach masę 202 227 i zamienia top 50 w dni i miesiące (`kilka następny dwa … grudzień październik`). Podobnie `kwadratowy` (5 401), `operator:Sm3` (2 973), `aspirant:Sm3` (1 500) (`seeds_top.py`).
4. **Rdzeń jest rzadki.** Terminy fachowe SGJP prawie nie występują w KWJP z progiem 5.

## Wariant kontekstowy (`dist.py`)
Wektor słowa = sąsiedzi z lewej i prawej (PPMI), 43 160 lematów z ≥20 wystąpieniami par. Ranking = cosinus do średniej zalążków.
- Top 50 to szum: morze `meblościanka syfon żużel mansarda …`, rolnictwo same czasowniki (`użalić przebarwiać …`), matematyka `nominał monolit geografia …`.
- Odzysk w top 1000: morze 4/28, rolnictwo 1/35, matematyka 2/27. Wyjątek: `pochodna` na miejscu 47 (matematyka).
- Bigramy mierzą podobieństwo składniowe i frekwencyjne, nie temat.

## Wniosek
Na danych lokalnych metoda E1 nie poszerza tematu w użyteczny sposób. Może najwyżej podsunąć kilkadziesiąt kandydatów do ręcznego przeglądu (morze, rolnictwo). Dla matematyki nie działa. Szansa na poprawę: okno szersze niż 2 słowa (3/4-gramy KWJP, do pobrania) albo zalążki dobrane ręcznie bez słów wieloznacznych.
