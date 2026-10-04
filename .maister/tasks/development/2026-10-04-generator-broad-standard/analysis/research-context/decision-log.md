# Rejestr decyzji pierwszego generatora

## TL;DR

Trzy decyzje zakresu zostały zatwierdzone: G1, N1 i C1.
Lokalny proces, model analiz i kontrola wydania zostały zatwierdzone wraz z projektem.
Rejestr nie nadaje statusu rozstrzygniętego nieznanym regułom językowym.

## Key Decisions

- D1=A: dwa pełne kandydaty, nie pilot jako wynik końcowy.
- D2=A: SGJP/KWJP w pierwszym wyniku, NKJP później.
- D3=A: udokumentowane konstrukcje w głównych kandydatach po kontroli klas.

## Open Questions / Risks

- ADR-003–005 zatwierdzono odpowiedzią „ok” na bramkę projektu; dowody wykonawcze pozostają do zebrania.
- Luki dowodowe i kryteria K1–K10 są w [projekcie](high-level-design.md); ich wymienienie nie oznacza usunięcia.

## ADR-001 — zakres pierwszego wyniku

**Status:** zaakceptowana przez użytkownika (D1 i D3).

**Kontekst:** potrzebna baza dopuszczalności z pełną fleksją; jeden zapis może mieć kilka składników źródłowych.

**Kryteria:** pokrycie, wyjaśnialność, kontrola nadgeneracji i mały pierwszy zakres.

**Rozważone opcje:** G1 — BROAD/STANDARD; G2 — niepełny pilot; G3 — także ATTESTED. Osobno C1 — konstrukcje w bazie; C2 — rozszerzenie; C3 — odroczenie wyboru.

**Decyzja:** G1 i C1, dokładnie według odpowiedzi A na obie niezależne bramki. Konstrukcje wymagają własnych dowodów i zgodności z polityką wariantu.

**Konsekwencje:** pilot może poprzedzać odbiór, lecz go nie zastępuje. Więcej kontroli klas przed wydaniem. ATTESTED, znajomość, tematy i benchmark później. Nie włączamy dowolnych reguł analizatora ani produktywnego słowotwórstwa.

## ADR-002 — harmonogram NKJP

**Status:** zaakceptowana przez użytkownika (D2).

**Kontekst:** dokładny artefakt pozostaje BLOCKED z powodu nieustalonych warunków dla planowanego użycia.

**Kryteria:** postęp niezależnych prac, jawność zakresu i zachowanie wymagań całego projektu.

**Rozważone opcje:** N1 — SGJP/KWJP najpierw; N2 — prace trwają, wydanie czeka; N3 — wyjaśnienie NKJP przed implementacją.

**Decyzja:** N1. NKJP nie znika z docelowego projektu; w pierwszym wyniku jest UNAVAILABLE z przyczyną.

**Konsekwencje:** brak dowodów NKJP w pierwszym wydaniu; późniejsze dołączenie wymaga osobnego odbioru i nowego manifestu.

## ADR-003 — lokalny proces i SQLite

**Status:** zaakceptowana w zatwierdzeniu projektu („ok”).

**Kontekst:** istnieją skrypty audytowe Python, dane mają relacje, potrzebny jest odtwarzalny przebieg i explain. Brak wymagań współbieżnej usługi.

**Kryteria:** prostota uruchomienia, mała liczba zależności, zachowanie surowych rekordów i łatwe odtworzenie.

**Rozważone opcje:** pliki jako jedyny magazyn; lokalny proces Python/SQLite; serwer bazy i API.

**Decyzja:** jedno lokalne narzędzie, moduły i baza na przebieg, strumieniowy import. Bez wdrażania usług.

**Konsekwencje:** łatwy start i izolacja przebiegów; wydajność i pojemność wymagają pomiaru. Jeśli pomiar wykaże problem, decyzję można zrewidować przed finalnym schematem; nie projektujemy klastra na zapas.

## ADR-004 — analizy, rekonstrukcje i niewiadome

**Status:** zaakceptowana w zatwierdzeniu projektu („ok”); nie rozstrzyga nieznanej semantyki językowej.

**Kontekst:** homonimia, konstrukcje kilku leksemów i niejasne etykiety uniemożliwiają kwalifikowanie samych napisów.

**Kryteria:** jedna spójna analiza spełniająca wszystkie warunki, brak nowych leksemów i możliwość wyjaśnienia.

**Rozważone opcje:** mechaniczne filtry napisów; ograniczony silnik Morfeusza; pełny eksport z małą listą zweryfikowanych reguł i macierzą pokrycia (F1). Dla trudnych kategorii: ręczne listy albo udokumentowane reguły z kolejką wyjątków.

**Decyzja:** F1 oraz O2/O3: reguły potwierdzonych klas, badanie źródłowe niewiadomych. VariantDecision odnosi się także do analizy rekonstruowanej. accept/reject/unresolved przed agregacją; istniejący accept zachowuje formę mimo odrzuconego homonimu.

**Konsekwencje:** jednoznaczne ślady, ale konieczna macierz kompletności i dalsze dowody. Dane korpusowe nie zastępują zasad dopuszczalności. Nowa reguła normatywna wymaga oddzielnej decyzji, jeżeli nie wynika z dotychczasowych ustaleń.

## ADR-005 — wydanie po kontroli kompletności

**Status:** wymóg kompletnego G1 i mechanizm zaakceptowane.

**Kontekst:** technicznie działający import lub eksport rozstrzygniętej części nie dowodzi pełności słownika.

**Kryteria:** odtwarzalność, brak cichego pomijania, ochrona wcześniejszych wyników i uczciwe statusy.

**Rozważone opcje:** częściowy eksport jako końcowy wynik; bramka pełnego odbioru (Q2); diagnostyczne warianty graniczne (Q3).

**Decyzja:** Q2; INCOMPLETE pozostaje wynikiem roboczym. Osobne build/verify/export, nowy katalog na przebieg i brak nadpisania istniejącego wydania. Manifesty opisują zakres identyczności wyników.

**Konsekwencje:** pełny wynik może czekać na dowody, choć prace techniczne trwają. Q3 można wykorzystać do oceny wpływu niewiadomych, ale jego górny zakres nie jest słownikiem poprawnych form. Atrybucje i warunki publikacji są częścią odbioru.
