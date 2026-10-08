# ZDS jako zasady gry

## TL;DR
Kurnik odsyła do [ZDS](https://sjp.pl/sl/dp.phtml) jako do „szczegółowych zasad”. Od 2026-10-08 (decyzja właściciela) ZDS jest naszą specyfikacją gry, ale tylko w części o grze.

| część ZDS | przyjmujemy? | dlaczego |
|---|---|---|
| §1 wyjątki (wielka litera, skróty, łącznik, sklepy, domeny, `-li` …) | **tak** | to zasady gry |
| §4 dopuszczalne formy (`pany`, `chłopcze`, `kowalsku` …) | **tak** | to zasady gry |
| §5 pisownia łączna (`nie-`, `-że`, `-by`, `-ś`, `-ń`) | **tak** | to zasady gry |
| §2 dozwolone słowniki, Dodatek A | **nie** | to wybór źródeł SJP.pl; nasze źródła to SGJP i KWJP |
| §3 warunek źródła (frekwencja w korpusach) | **nie** | j.w. |

Przykłady wymienione w ZDS traktujemy jako wiążące.

## Wersja
- ZDS „01/2026”, odczyt 2026-10-08, sha256 strony `b6e698e3be36261d67b175e380d7ae4d716f7c5e0837dda3ff7c0588a252f2bf`.
- Kopia: `tmp/zds/dp-2026-10-08.html` (poza Git). Wpis: `config/generator/evidence.json`, id `zds`.
- Nowa wersja ZDS nie zmienia reguł sama. Porównujemy ją z przypiętą i decydujemy osobno.

## Różnice znalezione 2026-10-08, wdrożone w rundzie 5 (v27)
- `abc`: skrót wg ZDS §1, a u nas był.
- `desa`: nazwa sieci sklepów wg ZDS §1, a u nas była.
- `spodeń`: ZDS §5 wymienia jako niedozwolone, a u nas było.
- `bodaj`, `bogdaj` + `-em`/`-śmy` (`bodajem`): ZDS §5 dopuszcza, a u nas nie.
- `trzeba`, `można` + `-że`/`-ż` (`trzebaż`): ZDS §5 dopuszcza, a u nas nie.
- `nie-` z przymiotnikami i przysłówkami w stopniu wyższym i najwyższym (`niedroższy`, `nienajdrożej`): ZDS §5 i pisownia 2026 dopuszczają, a u nas brak (około 10,5 tys. słów).

Reguły: `game-zds-named-exclusion-v1` (desa, spodeń i inne przykłady ZDS), `abc` w `ABBREVIATION_NOUN_LEMMAS`, hosty `bodaj`/`bogdaj`, konstruktory `pred-particle-ze-v1` i `nie-prefix-degree-v1`. Przy `nie-` lematy zaczynające się od „nie” pomijamy, bo mogą być już zaprzeczone, np. `nieniebieski` nie powstaje. Testy: `tests/test_round5_zds.py`.

Przy okazji poprawiono błąd z rundy 4: `explain` liczył ocenę bez frekwencji KWJP, więc dla `wraz` pokazywał w STANDARD odmowę.

## Wycofanie
Zmiana tego dokumentu i wpisu `zds` w `evidence.json`, potem nowy build.
