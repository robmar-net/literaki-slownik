# Pokrycie warunków kwalifikatorów — pełny raport

## TL;DR
Nowe build zapisują raport częściowych warunków kwalifikatorów.
Pełne dane mają 615 pól, 605 dosłownych etykiet i 7 458 520 interpretacji.
26 etykiet bez znanego warunku występuje w 1 910 interpretacjach.
Dwa kanoniczne raporty są identyczne; raport nie oznacza pełnej kwalifikacji.

## Key Decisions
- Tylko separator techniczny | tworzy zestaw dosłownych etykiet; przecinka nie rozbijamy.
- Warunek dotyczący jednego aspektu nie dowodzi kompletnej semantyki etykiety lub analizy.
- Liczniki etykiet i kategorii mogą się nakładać; mianownik interpretacji liczymy raz po polu.
- Build nadal ma INCOMPLETE i reports pending; aktywne kryteria językowe niezmienione.

## Open Questions / Risks
- 579 etykiet z przynajmniej jednym warunkiem nie oznacza 579 kompletnie sklasyfikowanych etykiet.
- Brak kwalifikatora w 6 423 658 interpretacjach nie dowodzi poprawności ani dopuszczalności.
- Wymagane są nadal pełne kategorie, ortografia i konstrukcje; ten raport nie zwalnia K4/K5.

## Wyniki

| Licznik | Wartość |
|---|---:|
| Interpretacje kompaktowe po deduplikacji | 7 458 520 |
| Surowe pola kwalifikatorów | 615 |
| Dosłowne etykiety | 605 |
| Interpretacje z przynajmniej jednym znanym warunkiem | 1 032 952 |
| Interpretacje z etykietą bez znanego warunku | 1 910 |
| Interpretacje bez kwalifikatora | 6 423 658 |

Liczniki są ekspozycją warunków, nie deltą końcowych list. Nie tworzymy statystyki pełnego dopuszczenia przez sumowanie tych kolumn.

[Pełny raport](qualifier-condition-coverage.json) zachowuje wszystkie pola i warunki wraz z evidence. [Runtime](qualifier-coverage-runtime.json) wiąże raport i użyty kod hashami; zawiera do trzech źródłowych przykładów każdej nierozpoznanej etykiety z pełnym ID i pierwszym wierszem. Przykłady są celowe i ograniczone, nie stanowią losowej próby jakości G8.

## Pozostałe nierozpoznane etykiety

`astrol.`, `astrol.,ekon.`, `astron.`, `astron.,handl.`, `biblt.`, `char.,fot.`, `char.,gry`, `etn.`, `fot.`, `gry`, `gry,zool.`, `gwar.,etn.`, `hom.,fot.`, `hom.,gry`, `kolej.`, `pisane_łącznie_z_przyimkiem`, `podniosłe`, `pot.,etn.`, `pot.,gry`, `pot.,slang`, `rzad.,etn.`, `rzad.,fot.`, `rzad.,slang`, `slang`, `slang,wulg.`, `spoż.`

## Uzupełniający przegląd źródeł

Sprawdzono przypięte oznaczenia/instrukcję SGJP i zachowane opcje metadanych strony leksemów. Opcje potwierdzają istnienie części etykiet, ale nie podają ich pełnej definicji. W [oznaczeniach SGJP](https://sgjp.pl/oznaczenia/) astr. i fotogr. mają definicje, lecz nie jest to bezpośredni dowód tożsamości starszych astrol./astron./fot. z eksportu. Nie aktywowano intuicyjnych aliasów. Trzy celowane wyszukiwania domeny SGJP nie zwróciły wyników. [Teoria SGJP](https://sgjp.pl/static/pdf/Podstawy_teoretyczne_SGJP.pdf) została sprawdzona pod kątem astrol. oraz akcentu; brak ścisłego wyjaśnienia dosłownej etykiety akcent pozostaje otwarty. Akcent może wystąpić wewnątrz etykiety z potwierdzoną dawnością; znany warunek wieku nie rozstrzyga pozostałych aspektów.

Źródła społecznościowe nadal odroczone; strony dokumentacji nie dodają nowych leksemów ani wejść build.

## Test-first i odtwarzanie

Sześć testów raportu: pięć miało red ImportError przed implementacją, test uruchomienia probe miał red nieznany tryb. Test integracji build miał red brak pliku raportu. Wszystkie siedem green; cała suita 97/97, baseline audytu 5/5. Podczas green skorygowano liczenie znanego warunku: assessment([]) dodaje diagnostyczny unresolved, który nie może być liczony jako rozpoznana reguła. Test mieszanki znanej/nieznanej wykrył tę różnicę.

```sh
python3 scripts/probe_generator_evidence.py --mode qualifier-conditions --database PATH/build.sqlite
python3 -m unittest tests.test_reports tests.test_build
```

Skrypt działa również spoza katalogu repo i otwiera bazę readonly. Nowy build zapisuje ten sam rodzaj raportu w reports/qualifier-conditions.json bez ponownego budowania wcześniejszych przebiegów.

2026-10-05T00:58:02Z — Runtime 3.566 s, total_changes=0. Plan pozostaje 8/36; G3–G6 częściowe.
