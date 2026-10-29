# Plan #13 — TEMATY v2 pierwszej fali

## Kontekst
Bramka #12 (2026-10-29): 6 tematów „popraw”, kuchnia „dalej” z 3 wykluczeniami. #13 robi wersje v2 tych 7 tematów. Nic nie wydajemy. Przed budową trzeba rozstrzygnąć rozjazd: generator (`_exclude`) usuwa wykluczony lemat tylko z T1–T3, a checker (`exclusions`) odrzuca każdy wiersz z wykluczonym lematem, także D.

PR-y dependabota: brak otwartych w `Literaki-server` i w `literaki-slownik` (sprawdzone).

## Decyzja: wykluczenie jest bezwzględne (obejmuje D)
Wykluczony lemat i klasa nie mogą być w temacie wcale. Checker zostaje bez zmian. Generator odrzuca dodatek D, którego `lemma_base` i klasa trafiają w wykluczenie (kod 4, dziś łapie tylko ten sam leksem). Dziś to samo blokuje `load_topic` dla identycznej pary; nowa reguła łapie też homonim spoza T1–T3. Uzasadnienie: jedno znaczenie „wykluczenia” w kodzie, checkerze i dokumentach. Zapis w nowym ADR-013.

## Skład v2 (do akceptacji z planem, AGENTS.md: zmiana składu słownika)
Sprawdzone w bazie SGJP (tylko odczyt): każdy dodatek ma 1 leksem dla lematu i klasy.

| Temat | Zmiana | Słowa oczywiste (próg 0,70) |
|---|---|---|
| grzyby | D (9): blaszka, drożdże, grzybiarz, grzybobranie, jadalny (adj), nóżka, trujący (adj), trzon, zielonka. Wykluczenia (5): flagowiec, megaspora, monada, promiennik, zrywka | 21/34 → 30/34 |
| pogoda | D (7): chłód, deszczowy, pochmurny, słoneczny, susza, temperatura, wilgoć | 23/36 → 30/36 |
| sport | D (14): biegać (inf), boisko, bramka, drużyna, gol, kibic, medal, mistrz, narta, rakieta, rower, stadion, trener, zwycięstwo | 20/36 → 34/36 |
| matematyka | wykluczenia (6): deniwelacja, eksport, hasło, kolur, oszczędności, wwóz | bez zmian |
| muzyka | wykluczenia (3): pokrywa, różaniec, zakrętka | bez zmian |
| kuchnia | wykluczenia (3): cytoplazma, sadzeniak, tyrozynaza | bez zmian |
| medycyna | bez `t3`; 11 z 18 słów „nie” było tylko w T3 i znika z nim. Wykluczenia (7): gladius, indywiduacja, macka, mizogin, numulit, pantofelek (oba homonimy), skrzele | bez zmian |

Pomijam jako D:
- słowa z otoczenia, nie z tematu: las, koszyk, mech, zbierać (grzyby); jesień, lato, wiosna, zima, lód, niebo (pogoda); karta (sport);
- `sędzia` w sporcie, bo ma 2 leksemy subst (kod 4).

Słowa D pochodzą z listy słów oczywistych, więc dla tych 3 tematów test słów oczywistych przestaje mierzyć pokrycie generatora. Zapisuję to w ADR-013.

Rośliny, zwierzęta i morze zostają bez zmian.

## Kroki
Zadanie: `.maister/tasks/development/2026-10-29-13-tematy-v2/` (krótkie `plan.md`, `work-log.md`, wyniki). Po każdym zapisie w `.maister/tasks` robię commit i push. Commity wprost na `main`, `feat/fix/docs/test(tematy): … (#13)`.

1. **Kod: wykluczenie a D (TDD).**
   - Test w `tests/test_tematy_wykluczenia.py` (red): dodatek D z homonimem wykluczonego lematu i klasy daje kod 4.
   - Zmiana w `literaki_slownik/tematy.py` `build_entries`: przed `_dodatek` sprawdzić `(lemat, czesc_mowy)` dodatku wobec par z `wykluczenia`. Ewentualnie po `_dodatek`: `lemma_base` i klasy leksemu wobec wykluczeń.
   - Docstringi `_exclude` i `build_entries` mają mówić „bezwzględne”.
2. **Checker, opcjonalne (b) i (c) z ADR-012, w osobnym commicie.**
   - (b) `scripts/check_tematy_package.py`:
     - teksty pakietu bez `<!--` i `@@SRODLADOWE@@`;
     - atrybucja IATE tylko przy `t3`;
     - `summary.json`: `t3` zgodne z tematem, `srodladowe` = null bez znaczników, `nie_dotyczy` zgodne z `t3`.
   - (c) `load_topic` / `check_inputs`: walidacja odcinków tekstów (`teksty_pakietu`) zaraz po wczytaniu tematu.
   - Każde z nich dostaje test red, potem green w `tests/test_check_tematy_package.py`.
   - (d) KeyError i (e) kropka w cytacie licencji: poza zakresem, zostają w ADR.
3. **Pliki tematów** `config/generator/tematy/{grzyby,pogoda,sport,matematyka,muzyka,kuchnia,medycyna}.json`:
   - `wersja` `<id>-v2`;
   - `dodatki` i `wykluczenia` z tabeli, z krótkim `powód` (np. „bramka #12: słowo oczywiste” / „bramka #12: ocena agenta «nie»”);
   - medycyna bez `t3`;
   - `uwagi` dopisane o v2.
   - `tests/test_tematy_fala.py`: oczekiwane wersje i liczby z plików.
4. **Budowy.** Skrypt `buduj_v2.sh`, kopia `buduj_fale.sh` z #12 dla 7 tematów, a potem b. Weryfikacja `verify_real.py --fala` (kopia #12): a = b i checker pass. Bez commitów w trakcie serii (`code_identity` = HEAD). Pakiety trafiają do `data/work/tematy-<id>-v2-<data>-{a,b}`, poza Git.
5. **R2 z ocen agenta** (metoda #12):
   - Próba to ranking hashem klucza, więc oceny agenta z #12 dla tych samych kluczy przenoszę bez zmian (payload ten sam, sprawdzam).
   - Agent ocenia tylko nowe pozycje próby, według `instrukcja-oceny-agenta.md`; jeden subagent na temat, równolegle.
   - Zapis i checker `--review` robi `record_agent_review.py` (kopia z `WERSJA` v2).
6. **Zestawienie i raport bramki.**
   - `zestawienie_fali.py` (kopia) daje `zestawienie-v2.json`.
   - `gate-report.md` podaje dla każdego tematu progi przed i po oraz werdykt „dalej/popraw”.
   - Decyzja „dalej” należy do operatora (AskUserQuestion po raporcie).
7. **Dokumenty i wiki.**
   - ADR-013: decyzja o wykluczeniach i składzie v2, uwaga o teście słów oczywistych, wynik bramki.
   - Zmiany w `ADR-012`: „Otwarte na v2” → odsyłacz; `.maister/docs/INDEX.md`; `docs/generator/jakosc.md` (fala v2); `docs/generator/cli.md` (nowy kod 4 dodatku); `docs/runbook-wiki.md`, jeśli trzeba.
   - Wiki `Slownik-TEMATY`: wersje v2 i liczby, nadal „W przygotowaniu”; wpis w `Historia-zmian`.
8. **Zamknięcie.** Pełny zestaw testów, komentarz w #13 z wynikiem, zamknięcie albo nowe zgłoszenie, jeśli coś zostaje „popraw”.

## Ryzyka
- Grzyby mogą dalej nie przejść `t2_tak` (23/50 w #12; agent dawał dużo „niepewne”). Dodatki tego nie zmienią. Wtedy temat zostaje „popraw” i wraca do operatora.
- Wykluczenie bez trafienia daje kod 4. W medycynie wykluczam więc tylko 7 słów spoza T3; zostało to sprawdzone na TSV v1.

## Weryfikacja
- `python3 -m pytest -q` w całości (dziś 555 + 5); nowe testy red przed zmianą.
- 14 budów: a = b bajtowo, checker exit 0, `--review` exit 0.
- Słowa oczywiste ≥ 0,70 w grzybach, pogodzie i sporcie; brak wykluczonych lematów w TSV (`gzip -dc … | grep`).
- Morze, rośliny i zwierzęta nie są przebudowywane. Regresja morza (`regresja_morze.py`) przechodzi na nowym kodzie.

## Standards Compliance Checklist
Brak katalogu `standards/`. Obowiązują zasady i dokumenty projektu z `.maister/docs/INDEX.md`:
- [ ] Teksty po polsku, zwięźle, z blokiem TL;DR / Kluczowe decyzje / Otwarte pytania (from AGENTS.md, zasady operatora)
- [ ] Zmiana składu słownika pokazana operatorowi z przykładami przed wdrożeniem (from AGENTS.md „Decyzje zmieniające skład”)
- [ ] Bez nazw gier słownych poza Literaki i Kurnik (from AGENTS.md / zasada operatora)
- [ ] Dane surowe i pakiety poza Git; piny SHA-256 bez zmian (from AGENTS.md „Pliki tymczasowe…”, ADR-011)
- [ ] Decyzja techniczna zapisana w ADR (ADR-013) i w INDEX.md (from .maister/docs/INDEX.md, wzór ADR-010–012)
- [ ] Wiki zaktualizowana według runbooka; „W przygotowaniu” bez wydania (from docs/runbook-wiki.md §TEMATY, AGENTS.md)
- [ ] Próba R2 według `tematy-quality-v1`, D poza próbą, progi bez zmian (from docs/generator/jakosc.md)
- [ ] Kody wyjścia zgodne z cli.md (2 konfiguracja, 4 dane) (from docs/generator/cli.md)
- [ ] Commit i push po każdym zapisie w `.maister/tasks` (from zasada operatora / AGENTS.md workspace)
- [ ] Bez kontaktu z autorami zasobów; Wikisłownik odroczony (from AGENTS.md, decyzja operatora)
- [ ] Bez CI na runnerach GitHuba (from workspace CLAUDE.md, żelazna zasada)
