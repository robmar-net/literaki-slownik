# Co potwierdzają niezależne źródła

## TL;DR
KWJP jest dobrym dowodem obecności słowa w piśmiennictwie 2011–2020.
Nie rozstrzyga sam, czy użycie jest zwykłe, historyczne, cytowane lub stylizowane.
NKJP jest starszy, traci wielkość liter i nie zastępuje oceny współczesności.

## Key Decisions
- WSJP służy kontroli interpretacji w researchu, bez importu haseł lub reguł do generatora.
- NKJP pozostaje pomocniczą miarą; nie aktywujemy go w STANDARD.

## Open Questions / Risks
- Korpus KWJP kończy się na 2020, więc nie dowodzi aktualnego użycia w latach 2021–2026.
- Licznik całego leksemu może usprawiedliwić dawną formę odmiany lub obce znaczenie homonimu.
- Słowo o dawnym przedmiocie nie musi być dawnym sposobem mówienia.

## Metryki KWJP
[Opis korpusu IPI PAN](https://kwjp.pl/overview), dostęp 2026-10-12: zrównoważone 100 mln słów, 35% publicystyki, 35% faktu, 30% fikcji; teksty 2011–2020, bez reprezentacji mowy i internetu.
[Oficjalny opis list](https://kwjp.pl/lists/doc/about/), dostęp 2026-10-12: automatyczna anotacja może zawierać błędy; próg publikacji F≥5 obowiązuje cały korpus, gatunki mogą mieć 1–4. ARF zmniejsza znaczenie skupisk, a 1-DP rośnie wraz z równomiernością rozkładu. To miary rozproszenia, nie dowód znaczenia ani brak cytatów. W sondzie używamy jawnie DP_norm≤0,9 w co najmniej jednym gatunku z F≥30; próg ten jest eksperymentalny.
[Repozytorium IPI PAN](https://github.com/ipipan/kwjp100-varia) publikuje listy i próbkę KWJP½M na CC BY 4.0. W pomiarach commit 26d82bd8b906dfed1cfcf8f903b1650b56daeabf.

## Etykiety i kontrola znaczeń
[SGJP — oznaczenia](https://sgjp.pl/oznaczenia/): daw., przest., arch., książk. i hist. mają odrębne objaśnienia. Nie są skalą popularności.
[WSJP — desperacja, rozpacz](https://wsjp.pl/haslo/podglad/47650/desperacja/5147287/rozpacz) oraz [determinacja](https://wsjp.pl/haslo/podglad/47650/desperacja/5147288/determinacja): oba znaczenia książkowe, z przykładami prasowymi.
[WSJP — niezbędnik żołnierza](https://wsjp.pl/haslo/podglad/112320/niezbednik/5264791/zolnierza) i [maturzysty](https://wsjp.pl/haslo/podglad/112320/niezbednik/5264798/maturzysty): opisuje współczesne przedmioty i materiały pomocnicze, bez kwalifikatora dawności w tych znaczeniach.
[WSJP — familia wielodzietna](https://wsjp.pl/haslo/podglad/12840/familia/5180478/wielodzietna): książkowe znaczenie rodziny; odrębne znaczenia historyczne.
[WSJP — odzienie](https://wsjp.pl/haslo/podglad/89359/odzienie): przestarzałe mimo współczesnych przykładów prasowych.
[WSJP — surdut](https://wsjp.pl/haslo/podglad/71964/surdut/5193113/marynarka): definicja odnosi przedmiot do dawnego ubioru, bez kwalifikatora przest. To odmienna sytuacja od dawnej formy językowej.
[WSJP — archaizm](https://wsjp.pl/haslo/podglad/86835/archaizm/5225318/jezykowy) podaje cytat z 2009 r., w którym aliści występuje jako przykład archaizmu: sama obecność w nowym tekście jest słabym rozstrzygnięciem.
Wnioski o żywym użyciu to nasza interpretacja powyższych dowodów, nie nowa polityka słownika.

## NKJP
[Strona autorów n-gramów](https://zil.ipipan.waw.pl/NKJPNGrams), dostęp 2026-10-12, ostatnia edycja 2021-01-26: tokeny małoliterowe dzielone białym znakiem, dane ze zrównoważonego NKJP; deklaracja CC-BY bez numeru. Brak znaczeń, dat i gatunków w pojedynczych 1-gramach.
[ADR-006](../../../../../../docs/adr/ADR-006-nkjp-cc-by-bez-wersji.md) dopuszcza te dane do POP/POP0, nie stanowi wcześniejszego zatwierdzenia zmiany STANDARD. Istniejąca metoda czyszczenia `strip-edges-keep-dot` zachowuje kropki skrótów. W naszym pomiarze NKJP ma `jakoż` 413, `aliści` 268, ale `desperacja` 121. Z tego nie wynika większa współczesność pierwszych słów. Wyniki w `nkjp-examples.json`.

## Granice niezależności
Korpusy są niezależne od polityki SJP.pl. Anotacja KWJP korzysta jednak z SGJP/Morfeusza, a przykłady WSJP często pochodzą z NKJP: nie są trzema niezależnymi głosami o identycznym znaczeniu.
