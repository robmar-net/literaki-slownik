# Etykiety źródłowe

## TL;DR
Pełny eksport ma 79 wartości nazw i 615 wartości kwalifikatorów.
Inwentaryzacja obejmuje wszystkie 7 458 520 kompaktowych interpretacji.
Semantyka techniczna eksportu jest potwierdzona; pełna polityka złożonych etykiet pozostaje otwarta.

## Key Decisions
- Zachowujemy całe pola i pełne identyfikatory. Nie tworzymy iloczynu nazw, kwalifikatorów i znaczeń.
- `|` łączy przypisane etykiety. Przecinek wewnątrz etykiety nie jest technicznym separatorem eksportera.
- Wersjonowany rejestr jest dokumentacją discovery, a nie aktywnym filtrem.

## Open Questions / Risks
- Znaczenie złożonych oznaczeń, zwłaszcza `daw._dziś_gwar.` i `przest._dziś_książk.`, wymaga domknięcia przed STANDARD. Sama obecność fragmentu `daw.` nie rozstrzyga współczesnego użycia.
- Nie ustalono pełnej zgodności danych o pochodzeniu leksemów z wyłączeniami źródłowymi ZDS. `z_D.` nie może być traktowane jako znacznik Doroszewskiego na podstawie podobieństwa napisu.

## Dowód formatu
[Kod eksportera Kuźni](https://git.nlp.ipipan.waw.pl/SGJP/Kuznia/blob/61daf78fb2378b1f33e707a364c7d912f8edd255/export/lexeme_export.py), wiersze 206–235, pobiera zbiór kwalifikatorów leksemu, odmiany i końcówki; wiersze 244–250 pobierają klasyfikację pospolitości. Model `dictionary/models.py`, wiersze 97–163, przechowuje dosłowną etykietę. Są to dowody sposobu reprezentacji, bez twierdzenia, że bieżący commit był kompilatorem eksportu 20260823. Format zgadza się z parserem przypiętego Morfeusza.

[Instrukcja SGJP](https://sgjp.pl/instrukcja/) opisuje domyślną pospolitość rzeczownika bez oznaczenia nazwy własnej, kwalifikatory leksemu i odmiany oraz osobne oznaczenie pochodzenia SJPDor. Eksport pięciopolowy nie przechowuje całej informacji artykułu hasłowego. [Oznaczenia](https://sgjp.pl/oznaczenia/) objaśniają proste etykiety; nie dowodzą dowolnego rozbicia złożonych etykiet na alternatywne sensy.

## Pełna kontrola
[`label-coverage.json`](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/label-coverage.json) zawiera wszystkie kombinacje, liczniki i 295 interpretacji z mieszaną nazwą pospolitą/własną. Każdy z tych 295 zapisów zawiera wielką literę: znane growe wyłączenie wystarcza do odrzucenia tej konkretnej analizy. Nie jest to dowód poprawności dowolnej konstrukcji korzystającej z niej ani usunięcie wpisu z bazy.

Odtworzenie: `python3 scripts/probe_generator_evidence.py --database PATH --mode labels`. Wynik porównano z pełną inwentaryzacją G2; wszystkie liczniki zgodne. Skrótowce mają osobny [przesiew](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/acronym-probe.json); nie zastępuje on klasyfikacji normatywnej.
