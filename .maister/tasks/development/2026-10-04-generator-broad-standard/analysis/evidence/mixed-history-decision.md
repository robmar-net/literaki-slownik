# Oznaczenia dawności i współczesnego użycia — decyzja

## TL;DR
W eksporcie współistnieją kwalifikatory typu „dawne, dziś gwarowe” i dodatkowe oznaczenia dawności.
Eksporter zbiera etykiety leksemu, odmiany i zakończenia w jednym polu; nie zachowuje ich poziomów.
Nie powinniśmy ignorować dodatkowego ograniczenia ani rozstrzygać pierwszeństwa etykiet bez uzgodnienia polityki.
Poniższy wybór dotyczy STANDARD, nie zasad gry ani BROAD. Nie wdrożono filtra.

## Key Decisions
- Samo „dziś gwarowe/książkowe/rzadkie” wskazuje współczesny zakres użycia i nie jest powodem wykluczenia ze STANDARD.
- Oceniamy konkretną interpretację formy. Odmowa nie usuwa innego homonimu ani całego leksemu.
- Nie dzielimy przecinków na alternatywne sensy; semantykę ustalamy dla konkretnych, dosłownych etykiet.
- Dowód utraty poziomów: przypięty `export/lexeme_export.py`, linie 206–235, unions kwalifikatorów leksemu/odmiany/zakończenia. Nie zakładamy identyczności bieżącej bazy online i eksportu 20260823.

## Open Questions / Risks
- Co zrobić, gdy obok „dziś…” występuje dodatkowe `daw.`/`przest.` w tej samej źródłowej analizie?
- Nie mamy w eksporcie pochodzenia każdego kwalifikatora z konkretnego poziomu opisu.
- Liczby poniżej są ekspozycją wybranych pól, nie końcową deltą listy.

## Przykłady i liczby

`masny` ma pole `daw._dziś_gwar.`. Jego `masniejszy` ma `daw.,daw._dziś_gwar.,rzad.`. Podobnie `uniżnie` ma `daw._dziś_gwar.`, zaś `uniżniej` ma `daw.,daw._dziś_gwar.`. Forma `skonfundowany` ma `przest.,przest._dziś_książk.`. To rzeczywiste rekordy eksportu SGJP 20260823, bez użycia danych SJP.pl.

| Pole | Rekordy | Oryginalne napisy |
|---|---:|---:|
| daw.,daw._dziś_gwar. | 2 | 2 |
| daw.,daw._dziś_gwar.,rzad. | 92 | 44 |
| przest.,przest._dziś_książk. | 32 | 22 |
| przest._dziś_książk.,arch.,char. | 3 | 3 |

Ostatni wiersz dotyczy osobnej, jednoznacznej archaiczności form `rewerencyj`, `deliberacyj`, `plenipotencyj`; nie włączamy go do wyboru pierwszeństwa `daw.`/`przest.`. Pokazuje, dlaczego współczesne użycie leksemu nie musi oznaczać współczesności całej odmiany.

## Wybór przed wdrożeniem

**A — rekomendowany:** dodatkowe samodzielne `daw.`/`przest.` wyklucza tę interpretację ze STANDARD, nawet przy „dziś…”. Sam kwalifikator „dawne, dziś gwarowe” bez dodatkowego oznaczenia pozostaje niewykluczający. To ostrożne podejście do historycznych wariantów form, zgodne z wymogiem, żeby współczesność leksemu nie przywracała jego dawnych form. Może jednak ograniczyć formy, których współczesny status wynika z innego poziomu opisu.

**B:** wskazanie „dziś…” ma pierwszeństwo przed dodatkowym `daw.`/`przest.`; konflikt ten nie wyklucza interpretacji ze STANDARD. Daje szerszy zasób, ale może zachować niektóre dawne warianty odmiany. Niezależne `arch.` i historyczna pisownia nadal są oceniane osobno.

W obu wariantach BROAD nie odrzuca na podstawie samej dawności; pozostałe kryteria językowe, gry i profilu obowiązują bez zmian. Pełne reguły wymagają zamkniętej mapy dosłownych etykiet, bez ogólnego substring `daw` lub `przest`.
