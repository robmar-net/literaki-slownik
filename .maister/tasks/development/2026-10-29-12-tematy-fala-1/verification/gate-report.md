# Bramka fali 1 TEMATY (#12, W14)

## TL;DR

- Zmiana metody (operator, 2026-10-29): trafność T2 i T3 liczymy z ocen agenta. Zgodność operator–agent i kappa: nie dotyczy.
- Werdykt bramki: **dalej** dla 3 tematów (kuchnia, rośliny, zwierzęta), **popraw** dla 7.
- Powody „popraw”: za mało słów oczywistych (grzyby, pogoda, sport), za niskie T2 (grzyby, matematyka, muzyka, morze), T1 i T3 w medycynie.
- Morze ma oceny operatora (T2 30/30, T3 27/27). Agent ocenił je dużo surowiej (T2 21/50, T3 9/27).
- Medycyna ma 342 wpisy T3.

## Kluczowe decyzje

- Progi z `config/generator/tematy.json` (`progi`): słowa oczywiste ≥ 0.70, T1 tak ≥ 0.90, T2 tak ≥ 2/3, T2 nie ≤ 0.10, T3 tak ≥ 2/3. Te same progi checker stosuje do ocen operatora. Dla metody agenta nie ma osobnych progów.
- Dwa werdykty obok siebie:
  - **checker**: wynik `check_tematy_package.py --review` bez zmian. Bez ocen operatora T2, T3 i zgodność mają stan „czeka”.
  - **bramka**: ta sama funkcja `verdict` z checkera, ale T2 i T3 liczone z ocen agenta, a zgodność „nie dotyczy”. Liczy to `analysis/zestawienie_fali.py`.
- Lematy wspólne dla kilku tematów zostają w każdym z nich (decyzja operatora). Macierz nakładania służy tylko do oceny.

## Otwarte pytania

1. Decyzja dla każdego tematu: dalej / popraw / stop (tabela na końcu).
2. Grzyby, pogoda i sport nie przechodzą testu słów oczywistych, bo brakuje im słów ogólnych (lista niżej). Czy dodać je jako `dodatki` (D) w v2?
3. Muzyka: T2 tak = 32/50 = 0.64, tuż pod progiem 2/3. Operator nie był pewien około połowy terminów. Poprawiamy czy przyjmujemy?
4. Morze: agent ocenia T2 i T3 dużo surowiej niż operator (zgodność 20/57, κ 0). Która ocena rozstrzyga? Pod oceną operatora morze miało tylko jedną przeszkodę: zgodność.
5. Lista lematów do wykluczenia w v2. Kandydaci to oceny agenta „nie” (niżej). Operator potwierdza albo skreśla.

## Tabela 10 tematów

Źródła: `reports/summary.json`, `release-manifest.json`, `verification/review-check-<id>.json`. Pełne dane: `verification/zestawienie-fali.json`.

Wpisy: razem (D/T1/T2/T3), „—” oznacza temat bez T3. Przecięcia: leksemy / formy. Diagnostyka: leksemy kandydaci → BROAD → STANDARD. Agent: „tak”/N w warstwach T1 · T2 · T3, w nawiasie liczba ocen „nie”. Operator: T2 / T3.

| Temat | Wpisy | Formy | ∩ POP | ∩ POP00 | Diagnostyka | Słowa oczywiste | Agent T1 · T2 · T3 | Operator | Zgodność / κ | Checker | Bramka |
|---|---|---|---|---|---|---|---|---|---|---|---|
| grzyby | 207 (0/54/153/—) | 1812 | 83 (40.1%) / 709 (39.1%) | 11 (5.3%) / 101 (5.6%) | 216→215→207 | 61.8% (21/34) | 50/50 · 23/50 (nie 5) · — | brak | n/d | popraw (słowa) | **popraw** (słowa, T2 tak) |
| pogoda | 232 (0/54/178/—) | 2105 | 138 (59.5%) / 1254 (59.6%) | 46 (19.8%) / 459 (21.8%) | 237→236→232 | 63.9% (23/36) | 48/50 · 41/50 · — | brak | n/d | popraw (słowa) | **popraw** (słowa) |
| matematyka | 475 (0/60/415/—) | 4320 | 291 (61.3%) / 2769 (64.1%) | 133 (28.0%) / 1347 (31.2%) | 486→480→475 | 80.0% (28/35) | 49/50 · 29/50 (nie 6) · — | brak | n/d | czeka | **popraw** (T2 tak, T2 nie) |
| muzyka | 1063 (0/224/839/—) | 9188 | 625 (58.8%) / 5238 (57.0%) | 180 (16.9%) / 1545 (16.8%) | 1131→1087→1063 | 75.7% (28/37) | 47/50 · 32/50 (nie 3) · — | brak | n/d | czeka | **popraw** (T2 tak) |
| sport | 794 (0/172/622/—) | 7811 | 572 (72.0%) / 5125 (65.6%) | 168 (21.2%) / 1538 (19.7%) | 826→806→794 | 55.6% (20/36) | 48/50 · 44/50 · — | brak | n/d | popraw (słowa) | **popraw** (słowa) |
| kuchnia | 1818 (0/157/1661/—) | 16094 | 1161 (63.9%) / 10390 (64.6%) | 262 (14.4%) / 2531 (15.7%) | 1874→1850→1818 | 83.8% (31/37) | 50/50 · 42/50 (nie 3) · — | brak | n/d | czeka | **dalej** |
| rośliny | 2371 (0/422/1949/—) | 22244 | 978 (41.2%) / 8963 (40.3%) | 203 (8.6%) / 1960 (8.8%) | 2410→2405→2371 | 100.0% (38/38) | 47/50 · 38/50 · — | brak | n/d | czeka | **dalej** |
| zwierzęta | 2765 (0/696/2069/—) | 23880 | 1217 (44.0%) / 10102 (42.3%) | 217 (7.8%) / 1821 (7.6%) | 2831→2814→2765 | 100.0% (37/37) | 50/50 · 43/50 · — | brak | n/d | czeka | **dalej** |
| medycyna | 3246 (0/275/2629/342) | 29775 | 1818 (56.0%) / 16347 (54.9%) | 549 (16.9%) / 5327 (17.9%) | 3335→3272→3246 | 82.1% (32/39) | 42/50 · 38/50 (nie 5) · 22/50 (nie 11) | brak | n/d | popraw (T1) | **popraw** (T1, T3) |
| morze | 970 (6/246/691/27) | 11035 | 432 (44.5%) / 4103 (37.2%) | 113 (11.6%) / 1071 (9.7%) | 996→988→970 | 100.0% (37/37) | 46/50 · 21/50 (nie 23) · 9/27 (nie 14) | 30/30 / 27/27 | 20/57 / κ 0 | popraw (zgodność) | **popraw** (T2 tak, T2 nie, T3) |

Morze to pakiet `tematy-morze-v2-20261029-a` z #11. Ma oceny operatora, więc checker ocenia T2 i T3 z ocen operatora. Kolumna „Bramka” pokazuje dla porównania wynik z ocen agenta.

## Powody werdyktu bramki

- **grzyby**: słowa oczywiste 61.8% < 70%; T2 tak 23/50 = 0.46 < 2/3.
- **pogoda**: słowa oczywiste 63.9% < 70%.
- **matematyka**: T2 tak 29/50 = 0.58 < 2/3; T2 nie 6/50 = 0.12 > 0.10.
- **muzyka**: T2 tak 32/50 = 0.64 < 2/3.
- **sport**: słowa oczywiste 55.6% < 70%.
- **kuchnia, rośliny, zwierzęta**: wszystkie progi spełnione.
- **medycyna**: T1 tak 42/50 = 0.84 < 0.90; T3 tak 22/50 = 0.44 < 2/3. T3 to 342 wpisy.
- **morze** (oceny agenta): T2 tak 21/50 = 0.42, T2 nie 23/50 = 0.46, T3 tak 9/27 = 1/3.

## Brakujące słowa oczywiste

- grzyby: blaszka, drożdże, grzybiarz, grzybobranie, jadalny, koszyk, las, mech, nóżka, trujący, trzon, zbierać, zielonka
- pogoda: chłód, deszczowy, jesień, lato, lód, niebo, pochmurny, susza, słoneczny, temperatura, wilgoć, wiosna, zima
- matematyka: cyfra, kalkulator, równanie, wykres, wzór, zadanie, średnica
- muzyka: akord, dźwięk, gama, nagranie, perkusja, płyta, tańczyć, zespół, śpiewać
- sport: biegać, boisko, bramka, drużyna, gol, karta, kibic, medal, mistrz, narta, rakieta, rower, stadion, sędzia, trener, zwycięstwo
- kuchnia: gotować, nóż, piec, smażyć, widelec, łyżka
- medycyna: badanie, bandaż, ciało, pacjent, plaster, tabletka, zastrzyk

## Kandydaci do wykluczenia w v2 (agent: „nie”)

- grzyby: flagowiec, megaspora, monada, promiennik, zrywka
- matematyka: deniwelacja, eksport, hasło, kolur, oszczędności, wwóz
- muzyka: pokrywa, różaniec, zakrętka
- kuchnia: cytoplazma, sadzeniak, tyrozynaza
- medycyna: absolut, dodatek, dominanta, gladius, indywiduacja, koniugacja, macka, mizogin, numulit, pantofelek:Sm2, podmiot, podtyp, przechowywanie, seria, skrzele, tropizm, walidacja, wytrzymałość
- morze: 37 lematów (lista w `zestawienie-fali.json`, pole `agent_nie`). Operator ocenił je wcześniej jako „tak”.
- pogoda, sport, rośliny, zwierzęta: brak.

## Uwagi operatora (R2)

- „cytoplazma” nie pasuje do kuchni (agent też ocenił „nie”).
- W muzyce operator nie był pewien około połowy terminów. Ocen nie zaznaczał w żadnym temacie: „albo ok, albo nie umiem ocenić”.

## Nakładanie lematów

Liczba wspólnych lematów dla każdej pary tematów. Przykłady (do 10 na parę): `zestawienie-fali.json`, pole `nakladanie`.

| | grz | pog | mat | muz | spo | kuc | roś | zwi | med | mor |
|---|---|---|---|---|---|---|---|---|---|---|
| grz | · | 0 | 0 | 3 | 1 | 8 | 42 | 19 | 42 | 1 |
| pog | 0 | · | 1 | 1 | 1 | 4 | 4 | 1 | 8 | 5 |
| mat | 0 | 1 | · | 9 | 6 | 9 | 6 | 3 | 25 | 8 |
| muz | 3 | 1 | 9 | · | 23 | 13 | 10 | 13 | 33 | 12 |
| spo | 1 | 1 | 6 | 23 | · | 11 | 8 | 20 | 22 | 21 |
| kuc | 8 | 4 | 9 | 13 | 11 | · | 359 | 75 | 170 | 13 |
| roś | 42 | 4 | 6 | 10 | 8 | 359 | · | 98 | 181 | 29 |
| zwi | 19 | 1 | 3 | 13 | 20 | 75 | 98 | · | 66 | 32 |
| med | 42 | 8 | 25 | 33 | 22 | 170 | 181 | 66 | · | 31 |
| mor | 1 | 5 | 8 | 12 | 21 | 13 | 29 | 32 | 31 | · |

Największe nakładania:
- kuchnia ∩ rośliny: 359 (owoce, warzywa, przyprawy);
- rośliny ∩ medycyna: 181;
- kuchnia ∩ medycyna: 170 (biochemia: adenina, albumina, alanina).

## Decyzje operatora

| Temat | Bramka (agent) | Decyzja (dalej / popraw / stop) | Uwagi |
|---|---|---|---|
| grzyby | popraw | | |
| pogoda | popraw | | |
| matematyka | popraw | | |
| muzyka | popraw | | |
| sport | popraw | | |
| kuchnia | dalej | | |
| rośliny | dalej | | |
| zwierzęta | dalej | | |
| medycyna | popraw | | |
| morze | popraw | | |
