# R1: lista wyjątków nie-mieszkańców (zaakceptowana 2026-10-08)

Przesiew `-anin/-anka` obejmuje 2 103 lematy m1. Lematy dopasowano do nazw geograficznych SGJP (wspólny rdzeń; skrypt `scripts/probe_resident_toponyms.py`). Słabo dopasowanych było 233, silnie 1 870. Obie grupy przejrzano ręcznie pod kątem znaczeń innych niż „mieszkaniec miejscowości lub regionu”.

Wyjątek obejmuje lemat męski oraz odpowiadający mu lemat żeński `-anka` (np. chrześcijanin → chrześcijanka), o ile jest w przesiewie. Pozostałe lematy przesiewu traktujemy jako nazwy mieszkańców: wielka litera według RJP 2026, więc odmowa w grze; STANDARD odrzuca zapis małą literą, BROAD go zachowuje.

## Proponowane wyjątki (dopuszczone jak zwykłe rzeczowniki)

| Kategoria | Lematy |
|---|---|
| wyznania i ruchy religijne | arianin, arminianin, anglikanin, bisurmanin, chrześcijanin, judeochrześcijanin, niechrześcijanin, gallikanin, luteranin, staroluteranin, mahometanin, muzułmanin, nestorianin, paulicjanin, pelagianin, poganin, pohanin, prezbiterianin, purytanin, rastafarianin, sabatarianin, socynianin, unitarianin, zaratusztrianin, ultramontanin |
| zakony | augustianin, bazylianin, dominikanin, franciszkanin, marianin, norbertanin, oratorianin, oliwetanin, salezjanin, salwatorianin, wallombrozjanin |
| diety i poglądy | wegetarianin, weganin, laktowegetarianin, laktoowowegetarianin, owowegetarianin, semiwegetarianin, fleksitarianin, frutarianin, witarianin, komunitarianin, libertarianin, republikanin, fabianin, fenianin, wolterianin, horacjanin |
| stany i role społeczne | mieszczanin, drobnomieszczanin, małomieszczanin, ziemianin, współziemianin, dworzanin, parafianin, parochianin, diecezjanin, plebejanin, włościanin, publikanin, pretorianin, grubianin, niebianin, przedszkolanin, banianin |
| miejsce ogólne, nie miejscowość | okoliczanin, współwojewodzianin, nadbrzeżanin, wieśnianin, przedmieszczanin |
| przenośne obok mieszkańca (wielka litera osobno w SGJP) | spartanin, samarytanin |

Razem: 76 lematów.

## Niepewne (domyślnie NIE są wyjątkami, czyli traktowane jak mieszkańcy)

nowomieszczanin, staromieszczanin, kartuzianin, górzanin, kortezanin, markietanin, nocleżanin, pokojanin, zwrotniczanin, urszulinianin, augustorianin, młynarzanin

Każdy z nich może być nazwą mieszkańca konkretnej miejscowości (np. Nowe Miasto, Kartuzy, Góra) albo słowem o innym znaczeniu. Eksport tego nie rozstrzyga.
