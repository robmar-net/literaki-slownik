# Kontrola rzeczywistości: pop-v1 wobec #3

**Status: ⚠️ Issues Found.** Mechanika jest gotowa. Treść ma jedną wadę klasy High. Nie zamykać #3 bez rewizji 4.

## TL;DR
- Pakiet jest odtwarzalny, podzbiory się zgadzają, Release i wiki istnieją. Sprawdziłem to sam.
- **Wada High:** przycinanie `prune-weak-members` (rew. 3) usuwa bardzo częste słowa. Poza POP są `pies` (ranga jednostki 521), `przypadek` (161), formy `spaść` i `paść` (`spadł`, `padł`, `upadł`). Poza POP0 jest też `raz` (49) i `świetnie`. To jest dokładnie błąd z pkt 5 #3: gra odrzuca słowo oczywiste.
- Przegląd 420 próbek tego nie wykrył. Żadna warstwa nie losuje słów częstych, które wypadły z listy.
- Rozmiary: POP ma 51 805 leksemów (+30% wobec 40 tys.). POP0 ma 13 181 (2,6 × 5 tys.). „Trochę więcej” to nie jest. POP0 jest mniejszy od POP 3,9 razy, a #3 mówi o rzędzie wielkości.
- 4,2% form POP (51 225) i 4,1% form POP0 (15 587) nie ma w SJP.pl. Są to głównie rzadkie formy z pełnej odmiany: `przeczytałobym`, `oświeciłom`, `remontowałoś`.

## Key Decisions
- Testów nie uruchamiałem (`skip_test_execution`, 372 OK przy a18da79). Zrobiłem kilka szybkich pomiarów:
  - `shasum -c` pakietu;
  - `diff -r` przebiegów `-a` i `-b`;
  - `comm` na listach POP, POP0 i STANDARD;
  - zapytanie `go run -overlay` do DAWG `pl-sjp-20260820` i `pl-standard-20261011` w `server/`;
  - test formami: 20 000 najczęstszych form KWJP (`orth_lc-all`) ze STANDARD porównane z POP i POP0;
  - `explain --variant pop/pop0` dla słów, których brakuje.
- Wadę uznaję za High, a nie Critical. Lista nie jest jeszcze słownikiem gry, bo integracja to osobna praca. Bot z POP przy stole STANDARD gra poprawnie, tylko ubożej.

## Open Questions / Risks
- Czy rozmiar POP0 (13 tys. leksemów, 380 tys. form) zgadza się z intencją właściciela („trochę więcej niż 5 tys.”)?
- Pełna odmiana daje słabemu botowi formy, których nikt nie użyje (`remontowałoś`). Bot z POP0 nie zagra więc „naturalnie słabiej”. #3 pkt 1 proponował inne rozwiązanie: tylko typowe formy, bez rzadkich trybów.
- `LIMITATIONS.md` jest nieaktualny w jednym zdaniu: „serwer gra dziś na SJP.pl”. Od #1836 stół może grać na STANDARD i BROAD. SJP.pl zostaje domyślny.
- Pakiet w tarballu nadal mówi o sobie „BUILT, nie jest wydaniem”. Wykrył to już production-readiness (W1).

## Rzeczywistość wobec deklaracji

| deklaracja z #3 | stan | dowód |
|---|---|---|
| POP0 ⊆ POP ⊆ STANDARD | ✅ | `comm`: 0 form POP poza STANDARD (3 090 194), 0 form POP0 poza POP; DAWG STANDARD: 0 braków |
| źródła KWJP+NKJP | ✅ | manifest: piny `nkjp_sha256` i `database_sha256` |
| odtwarzalność | ✅ | `diff -r …-a …-b` identyczne; `SHA256SUMS` OK; `SHA256SUMS` Release = pakiet (`POP.txt` 504725ab…, `POP0.txt` 6fde7b6a…) |
| `explain` z powodem | ✅ | działa, podaje `PRUNED_WEAK_MEMBER` i rangi członków |
| przegląd próbek | ⚠️ | 414/3/3. Ocenił agent, zatwierdził właściciel. Brak warstwy „częste, a poza listą” |
| liczby zatwierdzone przez właściciela | ✅ | decyzje delegowane, ADR-007 |
| wiki `Slownik-POP`, `Slownik-POP0` | ✅ | HTTP 200 |
| POP jako słownik gry „bez nieznanych słów” i bez odrzucania oczywistych | ❌ | poniżej, G1 |
| POP0 o rząd wielkości mniejszy | ⚠️ | 13 181 / 51 805 leksemów = 1:3,9 |

## Luki

| id | waga | luka | dowód |
|---|---|---|---|
| G1 | **High** | Przycinanie wyrzuca leksem, gdy KWJP rozbija lemat na warianty SGJP (`Sm3~a`/`Sm3~u`, `Vp~dnę`/`Vp~sę`, `Sm1`/`Sm2`). Każdy wariant dostaje wtedy słabą rangę własną albo żadnej. Zostaje członek-satelita (`psi`, `przypadkowy`, `metro`), a rdzeń wypada. | `explain pies`: jednostka ranga 521, `pies:Sm1` własna ranga 69 477, `pies:Sm2` brak. `przypadek`: 161 / 74 841. `raz`: 49 / 23 348. `spaść:Vp~dnę` brak. W 20 000 najczęstszych form KWJP poza POP jest 121 form, w tym `pies`, `psa`, `psy`, `psów`, `psem`, `psu`, `psami`, `przypadek` (6 form), `spadł`, `spadła`, `spadło`, `spadły`, `spadnie`, `padł`, `upadł`, `zapadł`, `metry`, `posłał`, `baran`, `nuda`. Reszta to nazwy własne (D9, zamierzone). W 10 000 najczęstszych form poza POP0 jest 119, w tym `raz`, `razy`, `razie`, `świetnie`, `prawej`, `rzekł`, `samotnie`, `metrów`. W `units.json` są 249 jednostki POP0 i 166 jednostek POP, w których przycięto każdy wariant jednego lematu. |
| G2 | Medium | Przegląd ma ślepy punkt. Losuje jednostki i formy z list oraz z granic progów. Nie losuje częstych słów, które wypadły z listy wewnątrz jednostki. „0 wad metody” w rew. 3 dotyczy więc tylko tego, co próbkowano. | `sample.json`: 14 warstw × 30. W `pop-v1-review.json` przycinanie wspomina jedna pozycja (`przyciszyć`). |
| G3 | Medium | Pełna odmiana wnosi rzadkie formy rodzaju nijakiego w 1. i 2. osobie (`-łom`, `-łoś`, `-łobym`, `-łobyś`): 42 214 form w POP i 13 807 w POP0. Większości nie ma w SJP.pl. Bot przy stole SJP takiego słowa nie zagra legalnie. Bot przy stole STANDARD zagra, ale nienaturalnie. | DAWG SJP: brakuje 51 225 form POP i 15 587 form POP0. Przykłady: `przeczytałobym`, `porozmawiałom`, `znalazłobyś`. |
| G4 | Medium | Rozmiary odbiegają od intencji. POP0 ma 2,6 × 5 tys. leksemów, a miało być „trochę więcej”. POP0 jest 3,9 razy mniejszy od POP, a #3 chce rzędu wielkości. POP ma 51,8 tys. przy limicie 60 tys., bo przycinanie zabrało 8 109 członków, a limitu nie przeliczono. | `thresholds.json`: `pruning.before` 59 914 → 51 805 leksemów |
| G5 | Low | Potoczne słowa (D7) wypadają nieźle. W POP0 są `spoko`, `fajny`, `kurde`, `okej`, `ogarnąć`, `wkurzony`. W POP są `siema`, `ziomek`, `luzik`, `lajk`, `hejt`. Brakuje `nara`, `czipsy` (jest `chipsy`) i `lajkować`. | sonda `grep -x` |
| G6 | Low | `LIMITATIONS.md`: zdanie o SJP.pl jest nieaktualne po #1836, a status `BUILT` jest w wydanym tarballu. | `server/lexicons/lexicons.go` (528db9a87) |

## Plan

| prio | zadanie | kryterium | nakład |
|---|---|---|---|
| High | ADR-007 rew. 4: przy przycinaniu warianty jednego lematu (ten sam rdzeń przed `:`/`~`) łączyć w jeden dowód. Inna droga: nie przycinać członka, którego forma jest wśród 20 000 najczęstszych form KWJP. | `pies`, `przypadek`, `spadł`, `metry` w POP; `raz`, `świetnie` w POP0; `kią`, `przestanek` nadal poza listami | 2–4 h + przebudowa |
| High | Dodać do `pop-quality-v1` warstwę „częste formy KWJP ze STANDARD poza listą” (bez nazw własnych). | próbka pokazuje wykluczenia, przegląd je ocenia | 1–2 h |
| Medium | Właściciel potwierdza rozmiar POP0 albo obniża limit (np. 8–10 tys.). Przeliczyć limit POP po przycinaniu. | decyzja zapisana w ADR | 15 min właściciela |
| Medium | Decyzja o formach `-łom`/`-łoś`/`-łobym` (#3 pkt 1): wyciąć z POP0 albo z obu list, albo zapisać, że zostają. | decyzja i pomiar liczby form | 1 h |
| Low | `LIMITATIONS.md`: zdanie o stołach STANDARD/BROAD; status wydania. | tekst | 15 min |

## Decyzja
- **pop-v1 jako dane do pomiarów i botów przy stole STANDARD: GO.** Jest legalne i odtwarzalne.
- **POP jako słownik gry dla ludzi, zamknięcie #3: NO-GO** do czasu rewizji 4. Gracz, któremu odrzucą `PIES` albo `SPADŁ`, uzna listę za zepsutą.
