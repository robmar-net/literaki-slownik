# Wspólny próg leksykalny udokumentowanego użycia

## TL;DR
Wcześniejsze A jawnie zatwierdziło dowód poprawnego polskiego użycia autorów SGJP tylko dla warunku leksykalnego BROAD. A wieku STANDARD nie rozszerza tego zakresu. Potrzebna jedna decyzja wspólnego progu, bez głosowania nad każdym słowem.

## Key Decisions
**A — rekomendowane:** ten sam sprawdzony dowód konkretnego polskiego użycia wystarcza dla warunku leksykalnego BROAD i STANDARD. Wiek, norma 2026, niepoprawność, gra, profil i zakres nadal oceniane osobno. Dokładne tożsamości, hashe i nierozpoznana pozostałość bez zmian; żadnej automatycznej akceptacji całej klasy frag.

**B:** zachować dodatni dowód wyłącznie dla BROAD; STANDARD wymaga osobnego dodatniego dowodu leksykalnego, do tego czasu ten warunek unresolved. Nie przywraca to wymogu dodatniego dowodu wieku odrzuconego w poprzedniej decyzji.

## Przykłady i wpływ
Pierwszy zakres: wznak, dwójnasób, trójnasób, kroćset, roścież, ziem — sześć już dokładnie udokumentowanych użyć. [Symulacja readonly](shared-lexical-proof-simulation.json), [odtwarzanie](shared-lexical-proof-simulation.py) zmieniają w pamięci tylko jeden warunek: STANDARD lexical unresolved → accept dla sześciu użyć. Baza i kod polityki bez zmian.

W tej projekcji v20 członkostwo wszystkich sześciu słów pozostaje takie samo: pięć unresolved, kroćset reject za dawność. Nie jest to twierdzenie o przyszłej finalnej delcie list; inne wymagane warunki nadal otwarte. Dowód dotyczy użycia, nie każdego znaczenia pełnego ID.

## Open Questions / Risks
Decyzja pending. A rozdziela wspólną podstawę leksykalną od ograniczeń STANDARD; nie usuwa żadnego istniejącego wyłączenia. B wymaga dodatkowych danych dla tych samych udokumentowanych jednostek. Nie aktywujemy metadanych czytnika ani nowych źródeł, nie kontaktujemy się z autorami. Pełna macierz i odbiór nadal wymagane.

## Przyczyna bramki
[AGENTS.md](../../../../../../AGENTS.md): „Decyzje zmieniające skład słownika lub kryteria dopuszczalności omawiamy z użytkownikiem przed ich wdrożeniem”. Poprzedni zapis scope=broad_lexical_condition_only jest wyraźnym ograniczeniem zatwierdzenia. [maister-implementation-plan-executor](/Users/robmar/.codex/plugins/cache/maister-plugins/maister-codex/2.2.3/skills/maister-implementation-plan-executor/SKILL.md): „ask the equivalent concise question in the final response and pause”. Rozszerzenie nie zostało wdrożone przed decyzją.
