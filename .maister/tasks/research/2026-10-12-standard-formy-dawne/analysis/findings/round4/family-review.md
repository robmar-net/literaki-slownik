# Niezależny przegląd rodzin — runda 4

## TL;DR

**Przegląd potwierdza 110 rodzin i wszystkie 2382 proponowane formy. Bez nowych dodatków i bez wycofań.** Potwierdzenie dotyczy wskazanych znaczeń i zakresów odmiany, przy wcześniej przyjętej zasadzie dopuszczania rzadkich regularnych form. Pewność oceny językowej pozostaje średnia.

Osobny agent odczytał **324 surowe konkordancje dla 109 rodzin**; `surdut` sprawdził bezpośrednio w WSJP. Dobór: pierwsze trzy różne dokumenty w dostępnych zapytaniach danej rodziny, jeśli tyle było. Osobny parser sprawdził **199 pełnych tabel SGJP**, ich hashe oraz **7192 analizy** propozycji i **15 621 odwołań do form**. Nie wykrył błędnego przeniesienia dodatkowej etykiety dawności. Odmianę potwierdza źródło; nie sprawdzano korpusowego użycia każdej z 2382 form.

[Pełne rozliczenie na rodzinę, formy, identyfikatory i źródła](family-review.json). Skrypt: [round4_family_review.py](../../round4_family_review.py), polecenie `python3 …/round4_family_review.py review`; potrzebny ignorowany cache źródeł. Dane produkcyjne i artefakty rund 1–3 bez zmian.

## Key Decisions

- **`utytułować` (+69): zachować po uzupełnieniu dowodu.** Same przykłady `utytułowane` nie wystarczały do całego czasownika. Siedem dodatkowych zapytań KWJP nie dało trafień. Znaleziono jednak bezpośrednie autorskie użycia czasownika: nadawanie tytułów naukowych w [Gazecie Uniwersyteckiej UŚ, 2005](https://gazeta.us.edu.pl/node/225861) oraz wyróżnienie projektu w [sprawozdaniu szkoły za 2023](https://zss-szamotuly.pl/osiagniecia/). Nie dotyczą dawnych rzeczowników `utytułowany/utytułowana`.
- **`szewron` (+10): zachować z lepszym uzasadnieniem.** Trzy początkowe teksty motoryzacyjne są podobne; nie traktujemy ich jako trzech niezależnych dowodów. [WSJP: naszywka](https://wsjp.pl/haslo/podglad/110989/szewron/5262617/naszywka) potwierdza właściwy rzeczownik i całą odmianę bez potrzeby oparcia się na logo.
- **Granice morfologiczne zachować.** [Dwoić się](https://wsjp.pl/haslo/podglad/82235/dwoic-sie) nie daje tu strony biernej; [naście](https://wsjp.pl/haslo/podglad/112096/nascie) obejmuje także formy zbiorowe. `odstawka` dodaje tylko `odstawce`; `odstawkę` jest już przyjęte. `Rozboi` ma `niezal.`, które zgodnie z obecną polityką samo nie odrzuca.
- **Rzadkość nie zastępuje dawności.** [Szuwar](https://wsjp.pl/haslo/podglad/72148/szuwar) ma także liczbę pojedynczą. [Solenny](https://wsjp.pl/haslo/podglad/86912/solenny/5215913/obietnica) i [zasadny](https://wsjp.pl/haslo/podglad/85607/zasadny) mają potwierdzone stopniowanie. [Surdut](https://wsjp.pl/haslo/podglad/71964/surdut/5193113/marynarka) jest współczesną nazwą dawnego ubioru.

## Open Questions / Risks

- To osobny reviewer-agent, **ten sam model i w znacznej części te same źródła**. Nie jest to recenzja lingwisty ani niezależna próba statystyczna. Nie oszacowano odsetka błędów.
- Dla `szacowny` SGJP podaje nieoznaczony jako dawny stopień wyższy; [odczytane znaczenie WSJP](https://wsjp.pl/haslo/podglad/32129/szacowny/4202582/jubilat) pokazuje tylko równy. Brak tabeli nie jest jawnym zakazem; nie zalecamy z tego powodu usuwania regularnych form.
- Część stron WSJP blokowała bezpośrednie pobranie HTTP (403), ale została odczytana narzędziem web. Strona szkoły nie rozwiązywała DNS przy pobraniu lokalnym; treść odczytano przez web. Błędy powtórzyły się po ponowieniu skryptu poza sandboxem. Manifest rozdziela odczyty web od lokalnych pobrań. UŚ i bieżącą tabelę SGJP pobrano lokalnie.
- Metryki 2021/2022 w korpusie mogą dotyczyć późniejszych wydań; nie uznajemy ich automatycznie za daty powstania tekstów. Pozostałe 2367 kandydatów nie zostało przez ten przegląd zatwierdzone ani odrzucone.
- To nadal research. Zbiór proponowany jest bez zmian, więc nie trzeba przeliczać jego delty POP z powodu tego przeglądu. Wdrożenie wymaga decyzji właściciela.
