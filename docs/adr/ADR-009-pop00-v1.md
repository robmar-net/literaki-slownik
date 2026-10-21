# ADR-009: POP00 — ochrona odmiany i próg wybranych form

## TL;DR
Operator zatwierdził politykę pop00-v1 2026-10-21.
POP00 dziedziczy leksemy POP0 i ogranicza konkretne formy, zachowując zwykłą odmianę.
To słownik znajomości. Jego reguły nie zmieniają dopuszczalności przy stole.

## Key Decisions
- Źródło leksemów: zamrożony pakiet POP0 pop-v3; reguła przynależności (i) jak w POP0.
- Każdy wybrany leksem musi zachować formę. Brak formy zatrzymuje budowę, bez sztucznego ratowania.
- POP00 ⊆ POP0 ⊆ STANDARD; istniejące metody pop-v2/pop-v3 pozostają odtwarzalne.
- Osobna komenda, konfiguracja i pakiet POP00. Bez migracji bazy i nowych źródeł.

## Open Questions / Risks
- Nie przeprowadzono badania znajomości wśród graczy ani pomiaru partii.
- Usuwane są również poprawne, zrozumiałe formy, np. czytanymi i najmilszemu.
- Dziedziczymy słabości selekcji leksemów POP0, w tym skutki homonimii i rejestru pisanego.

## Reguły
Po rozwinięciu tagów SGJP oceniamy każdą analizę:
1. Rodzaj n i osoba pri/sec: odrzucenie tej analizy.
2. Zwykła fleksja, w tym osobowe czasowniki, rozkaźnik, tryb warunkowy, pcon i ger aff: zachowanie.
3. Pact/ppas/pant/pacta, ger neg, adja/adjp, stopień com/sup: dokładny zapis w KWJP orth/all musi mieć IPM ≥ 0,1.
4. Konstrukcje by+aglt: zachowanie; nie-prefix-degree-v2 podlega regułom swojego tagu.
   Pozostałe znane konstrukcje wymagają progu całego napisu. Nie dziedziczą częstości składnika.
5. Co najmniej jedna zachowana analiza wybranego leksemu wystarcza do zachowania napisu.

POS, warianty pól i reguły konstrukcji mają zamknięty kontrakt. Nieznana klasa jest błędem danych,
a nie językowym odrzuceniem. Brak wiersza to NO_PUBLISHED_EVIDENCE, nie częstość zero.
Miara jest publikowanym dziesiętnym IPM z dokładnej listy orth/all, bez łączenia wielkich liter.

## Uzasadnienie i alternatywy
Zatwierdzony [plan](../../.maister/tasks/quick-plan/2026-10-21-10-pop00-generator-wiki/plan.md)
opisuje sondaż progów oraz przykłady po obu stronach. Próg każdej formy usuwał zwykłe odmiany
i całe leksemy. Sama blokada nijakiej pierwszej/drugiej osoby redukowała listę tylko o 14 005 form.
Wybrano ochronę zwykłej fleksji z ostrożnym progiem 0,1 dla pozostałych grup.
Sonda na pop-v3: 259 779 form, 13 896 leksemów; to nie potwierdzenie znajomości tych słów przez ludzi.

Zmiana progu, grup lub leksemów wymaga nowej uzgodnionej wersji metody.
Pakiet BUILT wymaga osobnego sprawdzenia, dwóch odtworzeń i przeglądu przed wydaniem.
Próbka wyklucza przykłady diagnostyczne, a przegląd techniczny nie zastępuje badania graczy.

## Pochodzenie
Warunki SGJP, KWJP i odziedziczonego NKJP zachowujemy z POP0; bez redystrybucji surowego NKJP.
Szczegóły w ATTRIBUTIONS.md, ADR-006 i dokumentach pakietu.
Powiązane: [#10](https://github.com/robmar-net/literaki-slownik/issues/10), ADR-007 i ADR-008.
