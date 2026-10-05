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
- Pełne nazwy „dawne, dziś gwarowe/rzadkie/frazeologiczne” oraz „przestarzałe, dziś książkowe” wskazują współczesne ograniczenie użycia. Ich wpływ na wiek formy rozstrzygnięto w zatwierdzonej regule 160/16 etykiet; pozostałe składniki nadal wymagają oceny. Nie są one alternatywą sensów.
- Nie przyjmujemy automatycznie wyłączeń źródłowych SJP.pl; brak metadanych SJPDor nie jest uzgodnionym powodem odrzucenia. Zob. [sprostowanie polityki źródeł](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/source-policy-clarification.md). `z_D.` oznacza łączenie zaimka z określeniem przymiotnikowym w dopełniaczu, a nie pochodzenie z Doroszewskiego.

## Dowód formatu
[Kod eksportera Kuźni](https://git.nlp.ipipan.waw.pl/SGJP/Kuznia/blob/61daf78fb2378b1f33e707a364c7d912f8edd255/export/lexeme_export.py), wiersze 206–235, pobiera zbiór kwalifikatorów leksemu, odmiany i końcówki; wiersze 244–250 pobierają klasyfikację pospolitości. Model `dictionary/models.py`, wiersze 97–163, przechowuje dosłowną etykietę. Są to dowody sposobu reprezentacji, bez twierdzenia, że bieżący commit był kompilatorem eksportu 20260823. Format zgadza się z parserem przypiętego Morfeusza.

[Instrukcja SGJP](https://sgjp.pl/instrukcja/) opisuje domyślną pospolitość rzeczownika bez oznaczenia nazwy własnej, kwalifikatory leksemu i odmiany oraz osobne oznaczenie pochodzenia SJPDor. Eksport pięciopolowy nie przechowuje całej informacji artykułu hasłowego. [Oznaczenia](https://sgjp.pl/oznaczenia/) objaśniają proste etykiety; nie dowodzą dowolnego rozbicia złożonych etykiet na alternatywne sensy.

## Pełna kontrola
[`label-coverage.json`](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/label-coverage.json) zawiera wszystkie kombinacje, liczniki i 295 interpretacji z mieszaną nazwą pospolitą/własną. Każdy z tych 295 zapisów zawiera wielką literę: znane growe wyłączenie wystarcza do odrzucenia tej konkretnej analizy. Nie jest to dowód poprawności dowolnej konstrukcji korzystającej z niej ani usunięcie wpisu z bazy.

Odtworzenie: `python3 scripts/probe_generator_evidence.py --database PATH --mode labels`. Wynik porównano z pełną inwentaryzacją G2; wszystkie liczniki zgodne. Skrótowce mają osobny [przesiew](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/acronym-probe.json); nie zastępuje on klasyfikacji normatywnej.

## Uzupełniona kontrola semantyczna
[Podstawy teoretyczne SGJP](https://sgjp.pl/static/pdf/Podstawy_teoretyczne_SGJP.pdf), §3.4.1, s.52, wyjaśniają `z D.` jako właściwość składniową zaimków typu CO. Bieżące metadane formularza [SGJP](https://sgjp.pl/leksemy/) potwierdzają istnienie pełnych nazw kwalifikatorów, ale nie są snapshotem przypiętego eksportu. `arch.…ku` zachowuje znaczenie archaiczności pomimo składnika składniowego. Dokładna treść uwagi `akcent` nadal nie została ustalona.

[Raport semantyki](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/qualifier-semantics-audit.json) obejmuje 10 rodzin i niezależnie sprawdzone rozliczenie pól. Liczby 423 kluczy dla rodziny dawne/dziś gwarowe, 1400 dla przestarzałe/dziś książkowe i 2272 dla archaiczne po ku opisują tylko ekspozycję po alfabecie/długości. Nie są deltą końcowej listy: nadal zawierają wielkie litery i inne przyczyny odrzucenia.

## Zatwierdzone niezalecanie

Użytkownik zatwierdził [A](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/disrecommended-decision.md): samo `niezal.` nie odrzuca w BROAD ani STANDARD. `config/generator/policy.json` rejestruje warunek, a `disrecommended_checks` pokazuje go również w explain. Nie jest to pełna ocena złożonej etykiety; historyczność i inne ograniczenia pozostają osobne. Pełny odczyt wszystkich 2 330 rekordów i pięciu dosłownych pól potwierdził pokrycie tej decyzji.

## Zatwierdzony wiek form i pierwszeństwo dawności

Użytkownik zatwierdził [A](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/mixed-history-decision.md): dodatkowe daw./przest. wyklucza konkretną interpretację ze STANDARD mimo dziś. Samo dziś gwarowe/książkowe/rzadkie nie wyklucza. `history_checks` używa zamkniętej mapy 160 etykiet historycznych (w tym potwierdzonego arch. po ku) i 16 wskazujących współczesne użycie. Wybrano je po przeglądzie całej listy dosłownych etykiet i definicji SGJP. Każda ocena dotyczy wyłącznie wieku, nie kompletnej poprawności lub dopuszczalności. Nieznane etykiety nie są interpretowane przez substring.

Pełny przegląd 615 pól potwierdził 180 pól z oceną wieku, 601 247 źródłowych rekordów. Historyczność i współczesne wskazanie mogą się nakładać; nie sumujemy tych liczników jako utraconych słów. Pozostałe składniki złożonych etykiet, np. akcent, nadal wymagają domknięcia semantyki.

## Potoczność, regionalność i rzadkość

Zatwierdzony prompt §2.3 i specyfikacja §5 nie wykluczają form tylko przez potoczność, wulgarność, regionalność, gwarowość ani rzadkość. `usage_checks` stosuje ten zakres do zamkniętej mapy 15 zaobserwowanych dosłownych etykiet; runtime nie dzieli przecinków ani nie zgaduje nowych mieszanek. Pozytywna ocena warunku nie nadaje całej analizie accept. Potwierdzono znaczenie pięciu oznaczeń w [dokumentacji SGJP](https://sgjp.pl/oznaczenia/).

[Runtime](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/usage-incorrect-runtime.json): 288 034 rekordy ekspozycji; wszystkie 15 etykiet obecne, brak zapisów do źródłowej bazy. Pełna polityka pozostaje otwarta; niepopr. rozstrzygnięto osobnym A, którego decyzja o niezal. nie zastępuje.

## Jawna niepoprawność

Zatwierdzone A: jawne niepopr. odrzuca konkretną interpretację w BROAD i STANDARD. Wdrożono 27 sprawdzonych dosłownych etykiet, zachowując wpisy i inne analizy. Niezal. pozostaje odrębne i niewykluczające; nieznane etykiety wymagają oceny. Pełna polityka i członkostwo w listach nadal nieukończone. `incorrect_checks` jest oceną językową, a nie zmianą reguł gry. Pozytywna ocena innego warunku nie znosi odmowy niepoprawności.

[Runtime](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/incorrect-runtime.json) uwzględnia wszystkie importowane analizy objętych napisów. Wynik nie jest członkostwem w pełnym wydaniu.

## Etykiety opisowe — zamknięta mapa

Dodano niewykluczające oznaczenia dziedzin, stylu i wariantów formy: 357 sprawdzonych dosłownych etykiet, 73 oznaczenia dziedzin, 18 stylu/użycia i 2 wariantów. Nowy warunek nie obejmuje mieszanek z nieznanymi ograniczeniami. Explain odtwarza teraz kandydatów potwierdzonych konstrukcji impt + jedna partykuła oraz by + nwok aglt z rzeczywistych składników importu, bez zapisu do bazy i bez końcowego dopuszczenia. Macierz kontekstu i pozostałe konstrukcje pozostają otwarte.

[Przegląd](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/descriptive-label-review.json) wiąże 357 etykiet z dokumentacją SGJP i hashami. `descriptive_checks` nie rozbija przecinków w runtime; nazwy własne, składnia i pozostałe warunki nie są domyślnie uznane. Mapa obejmuje także char./hom. jako opis formy, nie ocenę poprawności. `hist.` nie staje się automatycznie arch./daw.

[Pełna kontrola](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/descriptive-derivation-runtime.json): 139 729 rekordów ekspozycji nowego warunku, wszystkie 357 etykiet obecne. 34 dosłowne etykiety nie mają jeszcze żadnej oceny przez dotychczasowe warunki; nie oznacza to kompletnej kwalifikacji pozostałych 571 etykiet. W części rozpoznanych etykiet oceniono tylko dawność lub niepoprawność.

## Zatwierdzony kontekst

Zatwierdzono A: samo wymaganie kontekstu składniowego lub frazeologicznego nie wyklucza poprawnej formy w BROAD ani STANDARD. Wdrożono zamkniętą mapę 11 dosłownych etykiet; explain zachowuje source_label i required_context. Dawność, niepoprawność, niesamodzielne składniki i pozostałe kryteria oceniane są osobno. Pełny odczyt 7 458 520 rekordów potwierdził 169 rekordów kontekstu; pięć rzeczywistych zapytań bez zapisów do bazy. Pełna kwalifikacja i integracja build nadal nieukończone.

[Decyzja i dowody](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/context-restrictions-decision.md). `context_checks` porównuje całe etykiety, bez dzielenia przecinków. Z D. zachowuje wymaganie określenia przymiotnikowego w dopełniaczu, fraz. użycie frazeologiczne, po_liczebniku użycie po liczebniku. Daw.,z_D. nadal odrzuca tę analizę ze STANDARD. 26 etykiet nadal nie ma żadnej oceny warunku; pozostałe nie są przez to w pełni zakwalifikowane.
