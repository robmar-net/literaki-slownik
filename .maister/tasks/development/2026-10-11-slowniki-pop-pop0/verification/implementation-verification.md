# Weryfikacja implementacji POP/POP0

## TL;DR
✅ **Zaliczona po poprawkach** (stan końcowy: wydanie `pop-v2`). Pierwsza weryfikacja (`pop-v1`) nie przeszła: w POP brakowało częstych słów. Po rew. 4 metody: kontrola częstych form 0 braków, testy 390 OK, dwa przebiegi identyczne, przegląd 416/423 trafnych, zatwierdzony przez właściciela.
Pozostałe uwagi: informacyjne (pojedyncze słowa przy granicy, długie funkcje, podwójne zawężanie konfiguracji).

## Open Questions / Risks
- Ponownie sprawdzono: testy, straż częstych form, kontrolę pakietu (D-3, D-5), przegląd próbek, odtwarzalność. Pięciu przeglądów (kod, pragmatyka, gotowość, realność, kompletność) nie uruchamiano drugi raz; ich znaleziska poprawiono punktowo (historia niżej).
- Słowa potoczne bywają za nisko (D7); pojedyncze archaizmy przy granicy POP (`przestanek`, `strzeleński`, `jednonóż`); lemat `krocie` w KWJP inny niż w SGJP.

## Historia poprawek i ponownej weryfikacji

| znalezisko (pierwsza weryfikacja) | poprawka | wynik ponownego sprawdzenia |
|---|---|---|
| G1 krytyczne: brak `pies`, `przypadek`, `padł`; `raz` poza POP0 | warianty lematu razem przy przycinaniu (`prune-weak-members-v2`) | wszystkie w POP0; 27 zwykłych słów sprawdzonych ręcznie: 27/27 |
| G2: przegląd nie widział częstych słów poza listą | straż `frequent_guard` (20 000 / 5 000, zapis małymi literami, leksem z danymi w liście lematów) + warstwa `czeste-poza-lista` | straż 0 braków; warstwa: 3 formy, 1 sporna (`krocie`, pojedyncza) |
| po drodze: `koronawirus`, `głównie`, `świetnie`, `siebie` | D8 `lower-bound-kwjp-absent`, NKJP przestarzałe (≥100×) i zdominowane (przy KWJP) | wszystkie w POP0 |
| licencja: `TERMS.md` „wybór CC BY 4.0” poza decyzją A | warunki jak LL-PL (właściciel) | TERMS bez własnego wymogu |
| W1: `pop` mógł pisać w zamrożonym przebiegu | blokada → kod 2 | test zielony |
| W2: traceback zamiast kodu | `sqlite3.Error`/`KeyError`/`ValueError` → kod 4 | test zielony |
| I4, I8: `must_include` nie jako klucz gry; CRLF w NKJP | walidacja → kod 2; regex → kod 4 | testy zielone |
| LIMITATIONS: „nie jest wydaniem”, zdanie o SJP.pl | tekst poprawiony | w pakiecie pop-v2 |
| `SHA256SUMS` wydania z plikami spoza zasobów | sumy wydania osobno od sum rozpakowanych list | `shasum -c` na pobranym wydaniu: OK |
| spec, plan, INDEX.md nieaktualne | nota w spec i planie (ADR-007 rew. 4), linki w INDEX.md | — |
| G3 rzadkie formy nijakie 1./2. os. | bez zmian (decyzja właściciela) | opisane w LIMITATIONS |

## Wynik
| sprawdzenie | wynik |
|---|---|
| plan | 102/102 kroków + pętla poprawek |
| testy | 390 OK |
| odtwarzalność | dwa przebiegi pop-v2 identyczne; LL-PL v29 bez zmian |
| kontrola pakietu i przeglądu | `check_pop_package.py` = 0, `--review` = 0 |
| przegląd próbek | 416 correct / 4 incorrect / 3 unknown (423) |
| wydanie | [pop-v2](https://github.com/robmar-net/literaki-slownik/releases/tag/pop-v2); pop-v1 oznaczone jako wycofane |

Raporty pierwszej weryfikacji: `completeness-check.md`, `code-review-report.md`, `pragmatic-review.md`, `production-readiness-report.md`, `reality-check.md`. Odbiór: `pop-v2-acceptance.md`.
