# Runda 7: wyjątek współczesnego użycia liczy tylko zapis małymi literami

## Wniosek
Wyjątek z rundy 4 (forma dawna wraca do STANDARD przy ≥30 wystąpieniach w prasie i literaturze faktu) liczy teraz tylko zapis małymi literami. Decyzja agenta, 2026-10-10, odwracalna.

## Dlaczego
Przegląd próbek jakości (K9) wskazał `ali`. Miara brała listę KWJP `orth_lc`, która skleja wielkość liter. Imię „Ali” podnosiło więc licznik dawnego spójnika `ali`.

Pomiar na v29-a (STANDARD):
- 2 695 słów przyjętych dzięki wyjątkowi;
- 394 z nich mają ≥30 wystąpień tylko z wielką literą, a w zapisie małymi literami mniej niż 30. Odpadają.

Przykłady: `wałęsa`, `nowak`, `amerykanie`, `żyda`, `węgry`, `kielce`, `bogdan`, `ali`. Teksty mówią tu o Wałęsie, Nowaku, Amerykanach, a nie o dawnych formach pospolitych.

Zostają słowa naprawdę współczesne (zapis małymi literami, prasa i literatura faktu): `wraz` 13 088, `ponoć` 1 367, `niewiasta` 57. `toć` ma 23, więc odpada.

## Co zostaje słabe
Miara dotyczy formy, nie znaczenia. Skrót z kropką może ją zawyżyć: `sek` ma 301 wystąpień, głównie jako „sek.” (sekunda). Zapisane w `release.json` jako ograniczenie.

## Zmiana
- `nonfiction_frequencies`: lista `kwjp_orth` (fakt, publicystyka), tylko jednostki równe swojemu zapisowi małymi literami.
- Reguła `linguistic-contemporary-use-kwjp-v2`, polityka `approved-conditions-v29`.
- Testy: `tests/test_round4_sjp_fixes.py` („Niewiasta” 400 razy nie przywraca `niewiasta`).

## Przy okazji: status powiązań z korpusem
Przegląd wskazał też `nienaprawialny` i `nienajlepszy` jako „niejednoznaczne”, choć to jeden leksem. Konstrukcja liczyła się raz na każdy tag, a forma ze źródła raz na formę. Teraz konstrukcja liczy się raz (reguła + forma + lemat). Krawędzie zostają do każdego kandydata. Listy bez zmian. Test: `tests/test_links_structures.py`.

## Wycofanie
Przywrócić `kwjp_orth_lc` w `nonfiction_frequencies` i regułę v1, potem nowy build.
