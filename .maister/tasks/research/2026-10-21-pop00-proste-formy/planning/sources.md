# Rejestr źródeł

## TL;DR
Badamy wydane pop-v3 i przypięte lokalne dane KWJP.
Historia decyzji i aktualny kod mają pierwszeństwo przed starszymi opisami README.
Zewnętrzne publikacje są dowodami metodologicznymi, nie zatwierdzonymi wejściami generatora.

## Key Decisions
- Lokalny kod bazowy: `4f74b42fb4b6d3c256e079f30eebc6cac8d782a9`.
- Dostęp: 2026-10-21. Dokładne hashe wejść zapisze pomiar.

## Open Questions / Risks
- Brak badania rozpoznawalności wśród docelowych graczy.
- SUBTLEX-PL: możliwość importu wymaga osobnego ustalenia warunków.

## Kategorie
| Kategoria | Źródła | Stan |
|---|---|---|
| Kod | literaki_slownik/pop.py, schema.sql | zbadane; wyniki agenta zweryfikowane przez koordynatora |
| Dokumenty/historia | ADR-007/008, notatka o prostym języku, wcześniejsze badania POP, issue #6 | zbadane; wydanie i remote main potwierdzone przez GitHub API |
| Konfiguracja i testy | config/generator/pop.json i pop-sources.json; tests/test_pop*.py | zbadane; bez zmian generatora |
| Dane | POP0.txt.gz pop-v3, KWJP orth-all, fikcja, orth_lc-all, units.json i baza morfologii | dwa odtwarzalne skrypty, wyniki w analysis/evidence |
| Literatura | KWJP, Mandera i in. 2015, Jasnopis — prosty język | zbadane; ograniczenia poniżej |

## Źródła zewnętrzne
- Mandera, Keuleers, Wodniecka, Brysbaert (2015), SUBTLEX-PL, DOI 10.3758/s13428-014-0489-4:
  https://biblio.ugent.be/publication/5878584 — częstość pisana i napisy, rozpoznawanie form.
- KWJP: https://kwjp.pl/lists/en — formy, lematy, podkorpusy, IPM i dyspersja.
- Jasnopis: https://jasnopis.pl/prosty-jezyk/ — prosty język jako standard komunikacji.
- https://github.com/robmar-net/literaki-slownik/issues/6 — otwarty dług kalibracji progów.

## Dostęp i ograniczenia
Próba adresu https://kwjp.pl/info/lists zwróciła błąd narzędzia; dalszy odczyt przez
adres oficjalnej dokumentacji z README danych. Nie oznacza to niedostępności całego KWJP.
Odczyt zakończony powodzeniem: https://kwjp.pl/lists/doc/about/.
Strona bazy SUBTLEX-PL zwróciła błąd narzędzia, pełny tekst na UGent wymaga dostępu instytucjonalnego.
Wykorzystano abstrakt i metadane artykułu; nie importowano bazy.
Źródła wcześniej zablokowane (Jasnopis/Logios/minimum/PSONI) nie zostały odblokowane.
W tym badaniu są kierunkami metodologicznymi, nie wejściem ani kalibracją listy.

## Wersje i atrybucje
- KWJP100: snapshot repozytorium `26d82bd8b906dfed1cfcf8f903b1650b56daeabf` przypięty w projekcie;
  źródło IPI PAN, https://github.com/ipipan/kwjp100-varia, CC BY 4.0.
- SGJP/Morfeusz: snapshot 20260823; warunki BSD-2-Clause tekstowego eksportu zachowane przez projekt.
- POP0: pop-v3, publikacja 2026-10-14 00:39:57 UTC, hash gzip zgodny z GitHub Release asset digest.
- Baza SQLite: hash przypięty w konfiguracji; nie przeliczono wielkiego pliku, sprawdzono natomiast
  dokładną równość odtworzonego zbioru form z pakietem POP0. Ograniczenie zapisano w wyniku pomiaru.
- Hashe faktycznie użytych CSV, POP0 i units są w wynikach JSON skryptów.
- Warunki i pełne atrybucje projektu: `ATTRIBUTIONS.md`, `docs/generator/publikacja.md`, ADR-006.
