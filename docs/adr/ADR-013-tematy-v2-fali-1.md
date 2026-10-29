# ADR-013: TEMATY v2 pierwszej fali

## TL;DR
Siedem tematów dostało wersję v2 według bramki #12: grzyby, pogoda, sport (dodatki D), matematyka, muzyka,
kuchnia (wykluczenia) i medycyna (bez IATE, wykluczenia). Metoda zostaje `tematy-v2`
([ADR-012](ADR-012-tematy-fala-1.md)). Wykluczenie jest teraz bezwzględne i obejmuje też dodatki D.
Bramka v2 (operator, 2026-10-29): **dalej** wszystkie 10 tematów. Grzyby, matematyka i medycyna przechodzą
mimo jednego progu poniżej granicy. Bez wydania.

## Kluczowe decyzje
- **Wykluczenie jest bezwzględne.** Lemat i klasa z `wykluczenia` nie mogą być w temacie w żadnej warstwie.
  Generator odrzuca dodatek D z lematem i klasą wykluczenia (kod 4), także homonim spoza T1–T3. Checker
  już tak działał (`exclusions`). Wcześniej generator usuwał tylko T1–T3. Jedno znaczenie w kodzie, checkerze
  i dokumentach.
- **Skład v2** (pliki `config/generator/tematy/<id>.json`, wersje `<id>-v2`):
  - dodatki D z brakujących słów oczywistych, tylko słowa z tematu, nie z jego otoczenia:
    grzyby 9 (np. grzybobranie, trzon, trujący), pogoda 7 (np. pochmurny, susza), sport 14 (np. boisko, kibic);
  - pominięte: słowa z otoczenia (las, koszyk, jesień, lato, niebo, karta) i `sędzia` (2 leksemy subst w SGJP);
  - wykluczenia ocen agenta „nie”: grzyby 5, matematyka 6, muzyka 3, kuchnia 3;
  - medycyna bez `t3`. 11 z 18 słów „nie” było tylko w T3 i znika z nim; 7 pozostałych to wykluczenia.
- **R2 jak w #12** (oceny agenta). Próba to ranking hashem klucza, więc ocenę z #12 przenosimy, gdy klucz
  i `selected_unit` są identyczne. Agent ocenił tylko 33 nowe pozycje.
- **Checker sprawdza teksty i pola `summary`.** Brak resztek odcinków i znacznika; IATE w tekstach tylko
  przy `t3`; `t3`, `srodladowe`, `nie_dotyczy` zgodne z tematem. Generator waliduje odcinki tekstów przy
  wczytaniu wejść.
- **Bramka v2: dalej mimo progu** dla grzybów (T2 tak 24/50), matematyki (T2 tak 32/50) i medycyny
  (T1 tak 43/50). Braki to oceny „niepewne”, nie „nie”; T2 „nie” jest w normie wszędzie. Agent jest surowszy
  od operatora (morze: agent T2 21/50, operator 30/30).

## Otwarte pytania / ryzyka
- **Test słów oczywistych w grzybach, pogodzie i sporcie** przestał mierzyć pokrycie generatora: dodatki D
  pochodzą z tej listy. Wynik 30/34, 30/36, 34/36 mówi tylko, że braki uzupełniono ręcznie.
- **Matematyka:** dwa słowa „nie” (pryzma, reeksport) zostają. Wykluczymy je przy następnej wersji,
  najpóźniej przed wydaniem.
- **Medycyna T1:** atomy `psych.` i `med.` dają słowa „niepewne” (afekt, cyklotymik). Przy wydaniu do
  rozważenia węższe atomy.
- Checker zgłasza KeyError zamiast kodu wyjścia przy brakującym polu. Cytat licencji Słowosieci nie ma
  końcowej kropki. Nie robiliśmy tego w #13.
- Pakiety „dalej” zbudowano różnym kodem: rośliny, zwierzęta i morze w #12, reszta w #13. Wydanie
  przebuduje wszystkie jednym commitem.

## Wyniki
Pakiety `data/work/tematy-<id>-v2-20261029-{a,b}`: 14 budów, a = b bajtowo, checker pass.
Szczegóły: [gate-report.md](../../.maister/tasks/development/2026-10-29-13-tematy-v2/verification/gate-report.md).

| Temat | Wpisy | D | Wykluczenia | Słowa oczywiste | T1 tak | T2 tak |
|---|---|---|---|---|---|---|
| grzyby | 211 | 9 | 5 | 30/34 | 1 | 24/50 |
| pogoda | 239 | 7 | 0 | 30/36 | 24/25 | 41/50 |
| matematyka | 469 | 0 | 6 | 28/35 | 49/50 | 32/50 |
| muzyka | 1060 | 0 | 3 | 28/37 | 47/50 | 17/25 |
| sport | 808 | 14 | 0 | 34/36 | 24/25 | 22/25 |
| kuchnia | 1815 | 0 | 3 | 31/37 | 1 | 9/10 |
| medycyna | 2896 | 0 | 7 | 31/39 | 43/50 | 41/50 |

## Pochodzenie
Plan: [plan.md](../../.maister/tasks/development/2026-10-29-13-tematy-v2/plan.md),
zgłoszenie [#13](https://github.com/robmar-net/literaki-slownik/issues/13). Decyzje bramki #12:
[decision-log.md](../../.maister/tasks/development/2026-10-29-12-tematy-fala-1/decision-log.md).
