# STANDARD — próg oceny wieku przy braku wykluczającej etykiety

## TL;DR
Pełny przegląd wieku obejmuje7 458 520 interpretacji SGJP. 598 244 mają zatwierdzony wykluczający warunek wieku;6 860 276 go nie mają. To liczby interpretacji, nie liczby słów ani delty list. Przed aktywacją pełnej kwalifikacji STANDARD trzeba rozstrzygnąć, czy brak dodatniego dowodu wieku jest ograniczeniem raportowanym, czy blokującą niewiadomą każdej takiej analizy.

## Key Decisions
- Reguły gry, wyłączenia niepopr., znane historyczne zapisy i jawne daw./przest./arch. pozostają odrębne i wiążące.
- Wcześniejsze A dotyczą mieszanych kwalifikatorów, opisów całych klas i dowodu konkretnego użycia BROAD. Nie ustalają ogólnego progu dodatniego dowodu współczesności przy nieoznaczonej interpretacji.
- §2.3 promptu: brak kwalifikatora nie stanowi dowodu współczesności; zachowujemy informację o ograniczeniach. A nie zamienia tego braku w fakt o wieku. Wybiera operacyjną politykę listy opartą na dostępnej klasyfikacji źródłowej.
- Nie dodano nowego warunku w kodzie. Ta bramka dotyczy wieku; nie zamyka innych luk, macierzy, kwalifikacji nazw mieszkańców lub pozostałości semantycznej i nie pozwala omijać verify.

## Open Questions / Risks
Decyzja A/B pending. A może zachować nieoznaczone archaizmy; B wymaga dodatnich dowodów dotyczących konkretnych interpretacji nawet dla zwykłych słów. KWJP nie dowodzi samo wieku ani poprawności, więc B nie da się zamknąć licznikiem częstości. Nośnik wieku i status pewności trzeba zachować niezależnie od decyzji członkostwa. Nie wymagamy od użytkownika dostarczenia tych danych i nie kontaktujemy się z innymi grupami.

## Konkretny zakres i przykłady

[Pełne liczniki i rekordy](age-baseline-inventory.json):34klasy źródła,98 rozłącznych grup według POS, pustego pola kwalifikatorów, pola nazwy i istniejącego warunku wieku. Puste kwalifikatory:6 423 658 interpretacji/14 772 617 rozwinięć. Bez wykluczającego warunku wieku w pustej lub wyłącznie pospolitej klasie nazwy:5 754 712 interpretacji/13 928 163 rozwinięć. Obejmuje również klasy zależne, niesamodzielne i frazeologiczne: te liczniki nie są propozycją automatycznego dopuszczenia.

Przykład dom/dom, subst:sg:nom.acc:m3, nazwa_pospolita, kwalifikatory puste, wiersz1546221. Istnieje odrębny skrót domowy/brev, który nie przejmuje oceny rzeczownika. Kot ma niezależne nazwiska/geografię i rzeczownik pospolity; zachowujemy pełne źródłowe ID. Dwójnasób/trójnasób pozostają ilustracją wcześniejszego A: nie przenosimy ogólnego opisu wieku na wszystkie znaczenia.

## Wybór

**A — rekomendowane:** STANDARD kwalifikuje warunek wieku na podstawie przyjętej klasyfikacji SGJP i sprawdzonych konkretnych dowodów wykluczających. Brak wykluczającego oznaczenia sam nie blokuje tego warunku; zapisujemy age_basis=source_classification, age_certainty=not_independently_established, a nie potwierdzoną współczesność. Nie kasujemy rzeczywistych sprzeczności, nierozstrzygniętych znaczeń ani braków pozostałych warstw. Np. rzeczownik dom może przejść warunek wieku; pełna kwalifikacja nadal wymaga wszystkich innych warunków.

**B:** każda nieoznaczona interpretacja wymaga dodatniego, konkretnego dowodu współczesności przed akceptacją tego warunku w STANDARD. Bez dowodu pozostaje unresolved, również dom/kot; pełne wydanie blokowane. BROAD i reguły gry niezmienione.

A to świadomy próg wnioskowania generatora, nie stwierdzenie, że wszystkie nieoznaczone rekordy SGJP są współczesne. B zachowuje rygor dodatniego dowodu i znacznie rozszerza pracę dowodową. Przyszłe porównanie po zamrożeniu może ujawnić potrzebne poprawki, lecz nie służy do ustalenia tego progu.

## Kontrola danych

Skrypt age-baseline-inventory-probe.py czyta G2 readonly i grupuje wszystkie kompaktowe interpretacje; rozwija liczniki według tag_size, nie mnoży źródła przez użycia. Hash bazy przed/po identyczny, total_changes=0. To klasyfikacja istniejących warunków, bez nowych filtrów. Duże dane i surowe dokumenty poza Git.

## Przyczyna bramki

[AGENTS.md](../../../../../../AGENTS.md): „Decyzje zmieniające skład słownika lub kryteria dopuszczalności omawiamy z użytkownikiem przed ich wdrożeniem”. [maister-implementation-plan-executor](/Users/robmar/.codex/plugins/cache/maister-plugins/maister-codex/2.2.3/skills/maister-implementation-plan-executor/SKILL.md) wymaga: „At a material deviation or recovery decision […] ask […] and pause”. Bramka dotyczy konkretnego progu akceptacji wieku, nie ponownej zgody na źródło SGJP ani porzucenia obowiązkowego discovery.
