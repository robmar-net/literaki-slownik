# Odczyt glos w publicznym SGJP

## TL;DR
Poprawne parametry publicznego czytnika umożliwiły odczyt13 artykułów. Wartości glos istnieją i są osiągalne w tym odczycie. Wcześniejszych502 nie traktujemy jako dowodu nieobecności danych. Nie aktywowano metadanych internetowej bazy w generatorze.

## Key Decisions
- Odczyt używa tych samych anonimowych GET co publiczny czytnik, z reader=true i wariantem0. Nie użyto eksportu wymagającego uprawnień ani logowania.
- [Metryki i własne zwięzłe obserwacje](sgjp-public-reader-observations.json) zawierają dokładne źródłowe przypadki i osobne identyfikatory internetowe oraz hashe odpowiedzi. Nie publikujemy kopii HTML ani zbioru glos.
- Dopasowanie pisowni i klasy frag pozostaje kandydatem mapowania. Internetowe ID nie jest pełnym ID lematu w eksporcie Morfeusza i nie dowodzi zgodności całego snapshotu.

## Open Questions / Risks
- Warunki użycia metadanych jako maszynowego wejścia oraz zgodność wersji nadal nieustalone; wcześniejszy BLOCKED nie został zniesiony przez dostępność odczytu.
- Klasa frazeologiczna nie dowodzi sama obcojęzyczności ani growej odmowy. Pro i jam wymagają konkretnych opisów użycia; sir nie otrzymuje automatycznie klasy nazwiska.
- Przejrzano13 artykułów, nie całe147frag ani wszystkie znaczenia. Nie zamykamy G3 na podstawie tej próbki.

## Nowe obserwacje

De, ibn i bin są opisane jako człony nazwisk; pro i jam jako części frazeologizmów. Jednocześnie publiczne wyszukiwanie de pokazuje osobny rzeczownik i prefiks. Dla jam pokazuje także formę rzeczownika jama. Wystąpienie napisu w KWJP nie może więc automatycznie potwierdzić konkretnej analizy frag. [Publiczny SGJP](https://sgjp.pl/leksemy/), punkty odczytu i identyfikatory zapisano w JSON.

Połączenie corpus→spelling→SGJP musi zachować wszystkie alternatywy. Uzupełnienie klasy de:F nie oznacza odrzucenia de:S. Wniosek dokumentacyjny nie aktywuje wejścia ani filtra.
