# ADR-007: Metoda `pop-v1` dla list POP i POP0

**Status:** zaakceptowana 2026-10-11 (decyzje agenta z upoważnienia właściciela, odwracalne). Rewizje 2–4 z 2026-10-11 po przeglądach próbek i weryfikacji (D3, D5, D6, D8); od rew. 4 metoda `pop-v2`.
Właściciel, 2026-10-11: „podnieść oba limity; POP mocno, POP0 trochę; decyzje podejmij sam”.
**Częściowo zastąpiona przez [ADR-008](ADR-008-pop-v3-staly-prog.md)** (2026-10-12, `pop-v3`: D6 i D5 dla POP).
Konfiguracja `pop-v2`: [`config/generator/pop-v2.json`](../../config/generator/pop-v2.json).

## Kontekst
POP i POP0 to listy popularnych słów do gry, wybrane z leksemów SGJP z formą w STANDARD
(236 595 leksemów, 3 090 194 form). Miarę dają KWJP i NKJP ([ADR-006](ADR-006-nkjp-cc-by-bez-wersji.md)).
Liczby: [raport pomiaru](../../.maister/tasks/development/2026-10-11-slowniki-pop-pop0/analysis/pop-measure-report.md)
(tabele D1–D8 i dodatek z 2026-10-11). Konfiguracja metody: [`config/generator/pop.json`](../../config/generator/pop.json).

## Decyzje

**D1. Mianownik pokrycia: `kwjp-standard`.** Raporty pokazują też `kwjp-all`.
Cel „98–99% tekstu” w `kwjp-all` jest nieosiągalny: sufit przy wszystkich leksemach to 91,1%.
Odrzucone: `kwjp-all` (sufit 91,1%); `kwjp-exact` (pomija grupy AMBIGUOUS).

**D2. Formy: pełna odmiana, konstrukcje tak, przynależność reguła (i).**
To zmiana wobec wcześniejszej odpowiedzi właściciela „typowe formy”. Powód: wykluczenia klas
tną formy znane z tekstu (bez czterech klas: 494 764 zamiast 902 062 form, −45%, 4,28% masy NKJP),
a słownik stołu wymaga pełnej odmiany (spec §2.2).
Odrzucone: bez wołacza, rozkaźnika, imiesłowów, os. 1/2 lub czterech klas (j.w.);
bez konstrukcji (−33 495 form); reguła (ii) (907 s na każdy przebieg zamiast 10,5 s, −4 391 form).

**D3. Miara: KWJP+NKJP, log-ipm, waga NKJP 0,5** (rew. 2; pierwotnie percentyle F).
Pokrycie `kwjp-standard` 98,3% przy 40 000 leksemów. Sama KWJP (F) daje 98,6%,
Spearman 0,9705, Jaccard POP 89,6%; zostaje ścieżką wycofania NKJP.
Odrzucone: waga 0,75 i 0,25 (bez zysku, Jaccard ok. 93%); sama KWJP ARF, 1-DP (słabsza zgodność);
gatunki (pokrycie 68,3%); średnia percentyli (rew. 2: percentyle z różnych populacji nie są porównywalne).

**D4. Czyszczenie NKJP: `strip-edges-keep-dot`** (id `nkjp-clean-strip-edges-keep-dot-v1`).
Zdejmuje interpunkcję z brzegów tokenu, zostawia kropkę. Dopasowane 87,1% tokenów,
masa scalona 9,39%. Skróty (`ul.`, `r.`, `art.`) nie sklejają się ze słowami.
Odrzucone: `full-nfc` (77,7% dopasowanych); `strip-edges` (93,7%, ale 16,06% masy scalonej, głównie skróty).

**D5. Homonimy: `e-common`** — grupa homonimów bez nazw własnych.
Przypisuje 72,6% masy NKJP, największa grupa 22 leksemy.
Odrzucone: a i c (NKJP 23,4% i 45,3%); b (kopiuje F, tylko do porównań);
d (łańcuchy, grupa do 112 leksemów); e dosłowne (grupa do 102).

**D6. Progi: POP = 60 000 leksemów, POP0 = 20 000 leksemów** (liczone w leksemach).
Bez nazw własnych w rankingu: 60 000 → 45 229 jednostek, 1 328 263 formy, 98,5% `kwjp-standard`.
Przy 40 000 / 5 000 za granicą były słowa znane (`ryba`, `pensja`, `wada`, `kardamon`, `rowerzystka`).
Warunek: `kot` (ranga jednostki 9 128) musi być w POP0.
Odrzucone: 40 000 / 5 000 (próbki graniczne); 80 000 (+0,1 p.p. pokrycia, za granicą `ruptura`, `dejman`).

**D7. Luka potoczna przyjęta.** W POP 40 000 jest 597 z 2 410 leksemów potocznych.
Opis w LIMITATIONS; dodatki potoczne to osobne zadanie.
Odrzucone: korekta potocznych w `pop-v1` (to osobne zadanie, nie zmiana metody).

**D8. Braki danych: brak pełny → poza listą; brak częściowy → `lower-bound-absent`** (rew. 2; pierwotnie `available-only`).
Odrzucone: `lower-bound` i `exclude` (pokrycie 89,9%, Jaccard 83,5%).

**D9 (nowa). Nazwy własne nie biorą udziału w rankingu.** Ich formy wchodzą na listę tylko
przez zwykłe leksemy o tej samej formie. Powód: `Bednarski`, `Mikołaj`, `Nawarra` zajmowały
miejsca przy granicach.
Odrzucone: ranking z nazwami własnymi (j.w.).

## Rewizja 2 (2026-10-11, po przeglądzie próbek)
Przegląd 420 próbek pakietu z rew. 1: 402 trafne, 13 błędnych, 5 niepewnych; 9 błędów wskazało wady metody.

| wada | przykłady | zmiana |
|---|---|---|
| NKJP ma tylko małe litery; forma wspólna z nazwą własną traci masę, słowo dostaje zaniżoną rangę | `polski` 1 424, `wrocławski` 23 042, `sierota` 40 648 | D5: forma NKJP wspólna z leksemem spoza rankingu → NKJP jednostki `PROPER_SHARED`, miara tylko z KWJP |
| średnia percentyli z różnych populacji ciągnie w dół | `przekopiować` (KWJP 1,5, NKJP 68) | D3: log10 częstości na milion słów każdego źródła, średnia z wagą 0,5 |
| słowo tylko z NKJP przy granicy (brak w KWJP = F < 5) | `melchizedek`, `sazan`, `bomber` | D8: źródło nieobecne dostaje minimum zaobserwowane w tym źródle (flaga `bound:`); źródło niewiarygodne (`PROPER_SHARED`, `UNMATCHED`) jest pomijane |
| granica dzieli słowa o równej mierze alfabetycznie | `przelatek`, `scypuł`, `sekstern` | D6: blok równej miary wchodzi w całości albo wcale; lista może mieć mniej leksemów niż limit |

Wynik (v29): `polski` 72, `wrocławski` 3 101, `sierota` 7 066, `kot` 1 460 (POP0); `przelatek`, `scypuł`, `kieby`, `melchizedek` poza POP.
POP 59 914 leksemów (45 056 jednostek, 1 285 591 form, 98,6% `kwjp-standard`); POP0 19 991 (11 633 jednostki, 444 195 form).
Wycofanie NKJP: D3 = sama KWJP (log-ipm albo F), bez D4.
Zostaje jako ograniczenie: grupa homonimów wciąga rzadki leksem (`targan` z `targać`).

## Rewizja 3 (2026-10-11, po drugim przeglądzie próbek)
Przegląd rew. 2: 404 trafne, 4 błędne, 2 niepewne. Wada: grupa homonimów wciąga rzadki leksem przez jeden wspólny zapis (`kią` z `kia` przez `kto`, `pozytywnieć` przez `pozytywniej`, `targan` przez `targać`).

D5: `prune-weak-members`. Ranga i progi grup bez zmian. Członek grupy zostaje na liście, gdy jego **własne** jednoznaczne dane (KWJP EXACT, NKJP z jednym właścicielem) dają rangę w granicy tej listy. Wyjątki: najsilniejszy członek jednostki zawsze zostaje; członkowie bez własnych danych liczą się razem (jak `zamek`, `rok`, `dzień`). Formy wspólne z zostającym członkiem zostają.

Wynik (v29): POP 51 805 leksemów (45 056 jednostek, 1 219 614 form, 97,35% `kwjp-standard`); POP0 13 181 leksemów (11 633 jednostki, 380 489 form, 92,88%). Usunięci członkowie: 8 109 z POP, 6 810 z POP0 (np. `jadło`, `zeszyć`, `mamić`; znane `niebyt`, `mailowy`, `mem` spadają do POP). `kot` w POP0. Limity D6 (60 000 / 20 000) liczą leksemy jednostek przed przycięciem; nie podnosimy ich.

## Rewizja 4 (2026-10-11, metoda `pop-v2`)
Wydanie `pop-v1` (rew. 3) wycofane: w POP brakowało częstych słów (`pies`, `przypadek`, `padł`; `raz` poza POP0). SGJP dzieli lemat na warianty (`pies:Sm1`/`Sm2`), a przycinanie oceniało je osobno.

| zmiana | powód |
|---|---|
| D5 `prune-weak-members-v2`: warianty jednego lematu (ta sama podstawa przed `:`) mają wspólne własne dane i zostają lub odpadają razem | `pies`, `przypadek`, `metr` |
| straż częstych form (`frequent_guard`): pierwsze 20 000 form KWJP (tylko zapis małymi literami, formy STANDARD ze zwykłym leksemem z danymi w liście lematów) muszą być w POP, pierwsze 5 000 w POP0; brak → kod 4 | błąd z rew. 3 nie może wrócić niezauważony |
| D8 `lower-bound-kwjp-absent`: brak w KWJP → minimum KWJP; brak w NKJP → tylko KWJP (NKJP jest starszy i pomocniczy) | `koronawirus` |
| NKJP przestarzałe: KWJP ≥ 100× częstsze niż NKJP → tylko KWJP | `koronawirus` (śladowe NKJP) |
| NKJP zdominowane: masa wspólna z innym lematem > własna, a jednostka ma KWJP → tylko KWJP | `głównie`, `świetnie` |
| warstwa przeglądu `czeste-poza-lista` | przegląd rew. 3 nie mógł wykryć błędu |
| warunki list jak LL-PL (bez własnego wymogu) | decyzja właściciela 2026-10-11 |

Formy nijakie 1./2. os. (`przeczytałobym`) zostają (decyzja właściciela).
Wynik (v29, w pamięci): POP 53 002 leksemy (1 227 250 form, 98,60% `kwjp-standard`), POP0 13 896 (388 509 form, 94,59%); straż 0 braków.

## Rewizja
Decyzje są odwracalne. Wracamy do nich, gdy:
- ocena próbek właściciela (`pop-quality-v1`) wskaże błędy przy granicach;
- zmieni się wersja SGJP, KWJP lub NKJP;
- pojawi się źródło potoczne (D7).
Każda zmiana to nowa wersja metody w `pop.json` i nowy ADR lub aktualizacja tego.

## Wycofanie NKJP
Jeśli NKJP trzeba wycofać (ADR-006): D3 = sama KWJP (log-ipm albo F), bez D4. Ustawienie w `pop.json`,
potem nowe wydanie POP i POP0 bez NKJP w atrybucjach.
