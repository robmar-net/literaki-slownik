# POP00 — odbiór wdrożenia #10

## TL;DR
Wydano pop00-v1: 259 779 form, 13 896 leksemów, zero utraconych leksemów POP0.
461 testów i niezależny kontroler przeszły. Dwa pakiety mają identyczne wszystkie 11 plików.
Przegląd 891 pozycji potwierdza zgodność ze źródłami i zatwierdzonymi regułami.
Sześć publicznych plików ma poprawne hashe, pobieranie listy i końcowa wiki zostały sprawdzone.

## Key Decisions
- Zrealizowano zatwierdzony plan przez maister-quick-dev po maister-quick-plan.
- Źródło wydania: commit f33fe05c53f3ab945f929c81eed25ff736d04202, czyste drzewo kodu.
- Zachowano POP/POP0 oraz pełną podstawę źródłową; POP00 jest osobnym słownikiem znajomości.
- Przegląd jest techniczny, wykonany przez Codex; nie jest badaniem ludzi.

## Open Questions / Risks
- Nie zmierzono rozpoznawalności ani efektu w partiach.
- Próg i grupy są pierwszą polityką. Odpadanie czytanymi i najmilszemu jest zatwierdzonym kompromisem.
- Dziedziczymy ograniczenia wyboru leksemów POP0 i tekstów pisanych.

## Wynik i zachowanie
Zachowane m.in. kotach, czytajcie, zrobiłem, byłam, bym.
Odrzucone m.in. remontowałoś, przeczytałobym, czytanymi i najmilszemu.
Mniej form względem POP0: 128 984 (33,18%). Każdy z 13 896 leksemów zachował formę.
Wszystkie wyniki spełniają POP00 ⊆ POP0 ⊆ STANDARD.

Dodano pop00.py, konfigurację i piny, komendę pop00 i diagnostykę explain,
niezależny kontroler, testy, ADR-009, dokumentację CLI/raportów/jakości i kompletny opis wiki.
Nie zmieniono walidatora ani botów aplikacji.

## Weryfikacja
- python3 -m unittest discover -s tests: 461 testów, OK; w tym 17 nowych.
- Dwa czyste buildy końcowego commitu: [dowód r2](real-builds-r2.json).
- Wszystkie 11 plików identyczne; pełny diff słów z sondą: +0/−0.
- check_pop00_package.py: oba końcowe pakiety PASS, odtworzone źródłowe analizy i powody.
- [Przegląd r2](pop00-v1-r2-review.json): 891 indywidualnie udokumentowanych pozycji.
- [Kontroler z przeglądem](review-check-r2.json): PASS, pełne powiązanie z pakietem.
- [Przykłady](examples.json) sprawdzono na rzeczywistych danych; pliki decyzji obu generacji są identyczne.
- [Publikacja](publication-check.json): rzeczywiste pobranie, liczba form i hash listy; końcowa wiki.
- [Pliki wydania](release-assets.json): hashe wszystkich sześciu załączników zgodne z GitHubem.

W pierwszym przebiegu testów poprawiono złą liczbę kolumn własnej fikstury.
Po pierwszym odbiorze dopisano kontrolę końcowych hashy trzech plików POP0, nawet przy niezmienionym
manifeście. Test potwierdza odmowę po takiej zmianie. Powtórzono pełny suite i oba buildy z poprawki.
Zachowano dowody pierwszej generacji; końcowe mają oznaczenie r2.
W starszych testach projektu występują ResourceWarning o połączeniach SQLite; suite kończy się OK.

Po rozwinięciu skompresowanych tagów 25 522 napisy mają przynajmniej jedną analizę n+pri/sec.
Nie jest to liczba usuwanych słów: inne analizy mogą je zachować. Liczniki grup nakładają się.
Historyczne 14 010 dotyczyło dokładnych pól tagu, przed takim rozwinięciem; nie sumujemy tych wielkości.

## Standards Compliance Checklist
| Źródło | Wynik | Dowód |
|---|---|---|
| AGENTS.md | PASS | język polski, akceptacja kryteriów przed kodem, publiczny ticket i wiki |
| .maister/docs/INDEX.md | PASS | ADR-009 podlinkowany |
| ADR-007 i ADR-008 | PASS | osobny wariant; regresje POP/POP0 w pełnym suite |
| docs/generator/konstrukcje.md | PASS | składniki, źródłowe tagi i alternatywne analizy odtworzone przez niezależny checker |
| docs/generator/ortografia.md | PASS | dziedziczenie dopuszczalności, brak zmian zasad gry i leksemów |
| docs/generator/raporty.md | PASS | każdy napis i jego analizy, nakładające się grupy, jawne mianowniki |
| docs/generator/jakosc.md | PASS | nowy jawny seed, po 30 na warstwę, jawne puste warstwy, niezależna próba i przegląd |
| docs/generator/cli.md | PASS | błędy i odmowy, FROZEN, piny przed/po, brak nadpisywania, testy wyścigu i skażonych danych |
| docs/generator/publikacja.md | PASS | deterministyczny pakiet, pełne dokumenty warunków, bez surowego cache/bazy |
| ADR-006 | PASS | odziedziczone atrybucje NKJP; bez surowego NKJP i liczników w raportach |
| docs/runbook-wiki.md | PASS | pięć stron, rzeczywiste liczby, sprawdzone przykłady, wersja i działające pobieranie |

Repozytorium słownika nie ma workflow GitHub Actions. Testy i odtworzenia wykonano lokalnie.

## Publikacja
[Wydanie pop00-v1](https://github.com/robmar-net/literaki-slownik/releases/tag/pop00-v1)
— tag wskazuje sprawdzony commit źródłowy. [Wiki POP00](https://github.com/robmar-net/literaki-slownik/wiki/Slownik-POP00),
commit 9a7b717, zaktualizowano również Home, POP0, menu i historię.
Wersja metody i wyniki nie są deklaracją empirycznie ustalonej granicy znajomości graczy.
