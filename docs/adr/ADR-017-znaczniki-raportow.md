# ADR-017: znaczniki per raport w `reports/.done/`

**Status:** zaakceptowana 2026-11-23 (decyzja agenta). Zadanie #22.

## TL;DR
Po atomowym zapisie raportu powstaje `reports/.done/<raport>.json`. Wznowiony `reports` pomija raporty
ze zgodnym znacznikiem. `unresolved` przy wznowieniu wczytuje się z pliku. Najgorsza strata w `reports`
spada z ok. 8,5 h do ok. 4,1 h.

## Kontekst
`reports` to ok. 65% czasu buildu, sam `unresolved` ok. 4,1 h. Jego wynik w pamięci zasilał `filter_impact`,
`quality_*` i `coverage`. `canonical_index` ma jawną listę plików, więc `.done/` nie wchodzi do K8.

## Decyzje
- Znacznik ma `sha256`, `bytes`, `tree_sha256` i `manifest_sha256`. Brak albo niezgodność: raport od nowa.
- `unresolved` przy wznowieniu: `reports/unresolved.json`. Test sprawdza, że raporty zależne mają te same bajty.
- Świeży build też pisze znaczniki, więc A i B mają ten sam układ plików.
- Gdy etap przed `reports` liczył się od nowa, `.done/` znika (znaczniki wiązały się ze starą bazą).

Odrzucone: całe `reports` od nowa; cięcie `unresolved` na części.

## Otwarte pytania / ryzyka
- Dwie ścieżki danych `unresolved` (plik i pamięć). Różnice typów i kolejności łapie test.
- Wczytanie dużego JSON zwiększa szczyt pamięci przy wznowieniu.
