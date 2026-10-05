# Niewiadome według wyniku całego słowa

## TL;DR
Raport unresolved dodaje word_keys_by_membership: accept/reject/unresolved dla każdej reguły i wariantu. Zachowuje niewiadome także przy odrzuceniu, pokazując wynik całego słowa z uwzględnieniem wszystkich homonimów.

## Key Decisions
To współwystępowanie niewiadomej i wyniku, nie dowód przyczynowy ani symulacja usunięcia reguły. Liczniki sumują się do word_keys; jedna reguła liczy słowo raz. Nie zmieniono ocen ani kryteriów.

## Kontrole
Nowy test: zaakceptowany homonim przy odrzuconej niewiadomej, słowo unresolved oraz słowo wyłącznie odrzucone, powtarzalność i readonly. [Runtime](unknown-relevance-runtime.json) i [skrypt](unknown-relevance-runtime-probe.py): dwa identyczne odczyty każdej z dwóch historycznych baz, hashe baz niezmienione.

W większej historycznej projekcji 219 713 analiz / 213 636 kluczy STANDARD: 59 417 reject, 154 219 unresolved, 0 accept. Reguła dowodu ośmiu kontrakcji poza zatwierdzonym zakresem występuje wyłącznie przy ośmiu odrzuconych słowach. Mniejsza projekcja v19: 14 analiz / 5 kluczy, STANDARD 1 reject i 4 unresolved.

## Open Questions / Risks
To odczyt ocen wcześniej zapisanych polityk, nie ponowna kwalifikacja dużej populacji v20. Nie dowodzi pełnego pokrycia, delta list nadal nieustalona. Nie ukrywamy pozostałych niewiadomych, G3 i odbiór pozostają otwarte.
