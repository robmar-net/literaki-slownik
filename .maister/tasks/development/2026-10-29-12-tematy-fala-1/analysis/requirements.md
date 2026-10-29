# Wymagania — #12 TEMATY, pierwsza fala

## TL;DR
9 nowych tematów metodą tematy-v1, każdy w osobnym pakiecie a/b. Kod uogólniony: T3 opcjonalne, wykluczenia lematów, dodatki poza T3. Operator przegląda listy słów oczywistych przed budową (jedna strona), potem R2 tylko T2 (+T3 medycyny) przez stronę zbiorczą i 9 stron. Morze-v2 bajtowo bez zmian. Bez wydania.

## Kluczowe decyzje
Źródła: `clarifications.md`, `scope-clarifications.md`, `codebase-analysis.md`, `gap-analysis.md`.

## Otwarte pytania
- Brak (granice i proces ustalone przez operatora).

## Opis
Temat z issue #12 i decyzji operatora 2026-10-29: „zrób wszystkie 10 i ocenimy je potem wspólnie; metoda się nieźle sprawdziła dla morza”.

## Przebieg operatora (iPhone)
1. Jedna strona z 9 listami ok. 35 słów oczywistych; operator skreśla/dopisuje, wkleja JSON. Listy commitowane przed pierwszą budową; potem bez zmian.
2. Po budowach: strona zbiorcza z linkami do 9 stron R2 (30 słów T2 na temat, medycyna też 30 T3). Operator wkleja JSON z każdej strony, jak przy morzu (prywatne artefakty claude.ai).
3. Wspólna ocena wszystkich 10 tematów (z morzem-v2) na bramce; decyzje per temat: dalej / popraw / stop.

## Wymagania funkcjonalne
- F1 Schemat tematu: `t3` opcjonalne (bez `iate` → brak T3, IATE nieparsowane, brak IATE w ATTRIBUTIONS i manifeście użytych źródeł); `dodatki` na poziomie tematu (migracja morze.json bez zmiany wyniku); `wykluczenia` lematów niepuste dozwolone i stosowane (lemat+część mowy; wykluczenie bez trafienia → błąd); `diagnostyka.znaczniki_srodladowe` opcjonalne.
- F2 Teksty pakietu bez sformułowań o morzu, gdy temat ich nie dotyczy (LIMITATIONS bez znacznika śródlądowego, ATTRIBUTIONS bez IATE).
- F3 Próba R2: operator tylko T2 (+T3 gdy jest), 30 na warstwę; agent ocenia T1, T2, T3 (50 na warstwę jak dotąd). Progi jak morze; `t1_tak` liczone z ocen agenta; `t3_tak` „nie dotyczy” bez T3; zgodność 0,80 na pozycjach ocenionych przez obu.
- F4 Instrukcja dla agenta oceniającego: szerokie granice z clarifications.md, zapisana w zadaniu przed oceną.
- F5 9 plików tematów: zwierzęta, rosliny, medycyna, muzyka, kuchnia, sport, matematyka, pogoda, grzyby (id `[a-z]+`, bez polskich znaków). Atomy, korzenie i wycięcia wg codebase-analysis.md i decyzji operatora (taniec w muzyce; gry, szachy, karty w sporcie; napoje w kuchni; paleont. tak, łow. nie; grzybica w medycynie, wycięta z grzybów; zwierzęta bez 6047 człowiek 1 i 78303 hominid 1; zmierzony szum wycięty).
- F6 Budowy: 9 × (a, b) z czystego drzewa, identyczne SHA256SUMS, checker PASS; morze-v2 przebudowane po zmianie kodu: lista i TSV bajtowo jak `tematy-v2-20261029-a`.
- F7 Raport: przecięcia z POP/POP00 per temat i warstwa; diagnostyka BROAD/STANDARD; test słów oczywistych; tabela zbiorcza 10 tematów i nakładanie lematów między tematami.
- F8 Wiki: jedna strona Slownik-TEMATY z tabelą 10 tematów i opisem metody; Home, Historia-zmian; runbook-wiki uogólniony. Stan „W przygotowaniu”.
- F9 ADR-012 (uogólnienie: T3 opcjonalne, wykluczenia lematów, dodatki, próba R2 tylko T2) i dokumentacja generatora.

## Reużycie
Wzorce #11: `morze.json`, `tematy_review.py` (strona/zapisz), `record_agent_review.py`, checker, `quality.sample_strata`.

## Zasoby wizualne
Brak. Strony R2 jak w #11.

## Poza zakresem
Rolnictwo, Wikisłownik, LLM, kontakt z autorami, wydanie, dodatki D w v1.
