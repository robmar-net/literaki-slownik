# Reguła i źródła odmowy

## TL;DR
Publicystyka jest już w wyjątku współczesności.
Próg 30 dotyczy dokładnego napisu małymi literami, nie całej odmiany leksemu.
Benchmark na wiki używa innej miary: orth_lc dla całego KWJP.

## Key Decisions
- Research nie aktywuje żadnej nowej reguły.
- Nowe słowo liczymy dopiero, gdy jedna analiza spełnia wszystkie pozostałe warunki.

## Open Questions / Risks
- Dane form nie identyfikują znaczenia; dotyczy to też istniejącego wyjątku.
- Samo lemma+POS nie rozdziela wszystkich homonimów SGJP ani dawnych form odmiany.

## Ścieżka wykonania
`nonfiction_frequencies` (`literaki_slownik/decisions.py:19`) wybiera source_artifact o kind=kwjp_orth i genre=fakt/publicystyka, sumuje freq po unit_1, tylko gdy unit_1==unit_1.lower().
`assess_diagnostic` stosuje `contemporary_use_override` wyłącznie dla STANDARD. `policy.py:1086` zastępuje tylko odmowy `linguistic-historical-form-v1` przy F≥30. Pozostałe warstwy i odmowy zostają. Build zapisuje ocenę analizy; explain korzysta z tej samej miary. Przynależność słowa wynika z przyjętej spójnej analizy, nie mieszania warunków różnych homonimów.

Reguła obejmuje zamknięty rejestr etykiet, także złożonych i archaicznych; nie jest prostym wyszukiwaniem fragmentu `daw.`. `przest._dziś_książk.` ma osobny status; dodatkowy wykluczający składnik pozostaje.

## Historia decyzji
[Runda 4](../../../../development/2026-10-04-generator-broad-standard/analysis/evidence/round4-sjp-benchmark-fixes-decision.md) uzasadniła próg 30 na całym BROAD−STANDARD, wskazując stylizacje przy 10. [Runda 7](../../../../development/2026-10-04-generator-broad-standard/analysis/evidence/round7-contemporary-use-lowercase-decision.md) zmieniła orth_lc na orth, by imiona i nazwy nie podbijały zwykłych homografów. Dokumentuje też problem `sek`/skrótów z kropką.

## Testy
`python3 -m unittest tests.test_round4_sjp_fixes -q`: 6/6 OK, odczyt 2026-10-12. Sprawdzają 29/30, zachowanie innych odmów i ignorowanie `Niewiasta` w dowodzie dla `niewiasta`. Nie jest to test nowej polityki.

## Benchmark
`scripts/sjp_missing_top.py` bierze `KWJP100-kwjp100-slowa-orth_lc-all`. W pierwszych 2000 braków 615 zawiera dawną analizę; wszystkie te napisy są w BROAD. Kod powodów podaje przecięcie odmów, a jeśli jest puste — ich sumę z różnych analiz. Dlatego „nazwa własna + forma dawna” nie znaczy automatycznie dwóch odmów tej samej analizy. Wynik 615/2000 nie jest odsetkiem błędów STANDARD ani liczbą gotowych do dopisania słów.

Źródła: commit `1b6f4b66803f312bffea3b32593c202faa0eea40`, wskazane pliki; wiki odczytana przez raw.githubusercontent.com po błędzie cache narzędzia web. Surowa strona lokalnie w `tmp/issue4-wiki.md`.
