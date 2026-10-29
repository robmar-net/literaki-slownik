# Plan: TEMATY przed wydaniem (po #13)

## Kontekst
ADR-013 zostawił trzy rzeczy na czas przed wydaniem:
1. matematyka bez „pryzma” i „reeksport”;
2. węższe atomy T1 w medycynie;
3. przebudowa wszystkich 10 tematów z jednego commita.

Dziś pakiety pochodzą z różnych commitów: rośliny, zwierzęta i morze z #12, reszta z #13.

Decyzja operatora o medycynie (2026-10-29): atomy zostają bez zmian, plus 5 wykluczeń z `psych.`: walidować, logizować, apercypować, rozhamować, dezindywiduacja. Psychiatria zostaje w medycynie.

Samo wydanie (Release, link pobrania, zdjęcie „W przygotowaniu”) jest poza zakresem. To osobna decyzja. Dependabot: sprawdzam listę PR-ów na starcie, jak przy każdym nowym zadaniu.

## Kroki
Zgłoszenie: nowe #14 „TEMATY: przygotowanie wydania”. Katalog `.maister/tasks/development/2026-10-29-14-tematy-przed-wydaniem/` (`plan.md`, `work-log.md`, wyniki). Po każdym zapisie w `.maister/tasks` robię commit i push.

1. **Pliki tematów:**
   - `config/generator/tematy/matematyka.json` → `matematyka-v3`, wykluczenia +2: pryzma, reeksport (subst; powód: ocena agenta R2 „nie” w v2).
   - `config/generator/tematy/medycyna.json` → `medycyna-v3`, wykluczenia +5. Klasy biorę z TSV v2: czasowniki mają `inf`, dezindywiduacja `subst`. Powód: słowo z `psych.` bez związku z medycyną (operator).
   - Test najpierw: `tests/test_tematy_fala.py`, słownik `V2` → wersje i wykluczenia dla v3.
   - Commit `feat(tematy): matematyka i medycyna v3 (#14)`.
2. **Jedna seria budów, 10 tematów × a/b, z jednego HEAD:**
   - Skrypt `buduj_wydanie.sh` (kopia `buduj_v2.sh` z #13) z listą 10 tematów, razem z morzem.
   - Pakiety idą do osobnego katalogu `data/work/tematy-wydanie-20261029/tematy-<wersja>-<data>-{a,b}`, bo nazwy z tą samą datą już istnieją; nic starego nie nadpisuję.
   - `verify_real.py --fala` (kopia), `Z_T3 = {}`. Wyjątek: morze ma T3/IATE, więc kontrola fali musi je dopuścić dla morza.
   - Bez commitów w trakcie serii.
3. **R2 na nowych pakietach:**
   - Wiązanie przeglądu zawiera hash `SHA256SUMS`, więc przeglądy trzeba zapisać na nowo.
   - Oceny agenta przenoszę skryptem (kopia `przenies_oceny.py`, źródła: #13 dla 7 tematów, #12 dla roślin i zwierząt).
   - Agent ocenia tylko pozycje nowe w próbie, jeśli takie się pojawią (matematyka, medycyna).
   - Morze: przegląd operatora z #12 przepinam jak w `przepnij_morze.py` z #12.
   - `record_agent_review.py` + checker `--review` (exit 0) dla 10 tematów.
4. **Zestawienie** `zestawienie_fali.py` (kopia) daje `zestawienie-wydanie.json` i krótki `gate-report.md`: liczby, progi, jeden `code_identity` dla wszystkich 20 pakietów.
5. **Dokumenty:**
   - ADR-013: dopisek „Przed wydaniem” (v3 matematyki i medycyny, jedna seria);
   - `.maister/docs/INDEX.md`;
   - wiki `Slownik-TEMATY` (wiersze matematyki i medycyny, wersje v3) i `Historia-zmian`; nadal „W przygotowaniu”.
6. **Zamknięcie:**
   - pełny zestaw testów;
   - komentarz i zamknięcie #14;
   - lista ścieżek 10 pakietów `-a` gotowych do wydania (sha256 `release-manifest.json`).

## Ryzyka
- Wykluczenie bez trafienia albo ze złą klasą daje kod 4. Klasy sprawdzam w TSV przed budową.
- Przepięcie przeglądu morza może wymagać zmiany w kopii `przepnij_morze.py` (inna ścieżka pakietu).

## Weryfikacja
- `python3 -m unittest discover -s tests -t .` bez błędów.
- 20 budów: a = b bajtowo, checker pass, jeden `git_commit` w `code_identity` wszystkich 20.
- W TSV matematyki i medycyny nie ma 7 wykluczonych lematów (`gzip -dc … | cut -f2 | grep -x`).
- 8 tematów bez zmian składu (rośliny, zwierzęta, morze, 5 tematów v2) ma `<ID>.tsv.gz`, `<ID>.txt.gz` i raporty bajtowo jak poprzednie pakiety. Różnice są tylko w `release-manifest.json` i `SHA256SUMS`.

## Standards Compliance Checklist
Brak katalogu `standards/`. Obowiązują dokumenty z `.maister/docs/INDEX.md`:
- [ ] Polski, zwięźle, TL;DR / Kluczowe decyzje / Otwarte pytania (from AGENTS.md, zasady operatora)
- [ ] Zmiana składu zatwierdzona przez operatora przed wdrożeniem (from AGENTS.md „Decyzje zmieniające skład”)
- [ ] Bez nazw gier słownych poza Literaki i Kurnik (from AGENTS.md)
- [ ] Pakiety w `data/work` poza Git; piny wejść bez zmian (from AGENTS.md, ADR-011)
- [ ] Decyzja zapisana w ADR-013 i INDEX.md (from .maister/docs/INDEX.md)
- [ ] Wiki według runbooka, „W przygotowaniu” bez wydania (from docs/runbook-wiki.md §TEMATY)
- [ ] Próba R2 `tematy-quality-v1`, progi bez zmian (from docs/generator/jakosc.md)
- [ ] Nazwy pakietów `tematy-<wersja>-YYYYMMDD-{a,b}` (from docs/generator/cli.md)
- [ ] Commit i push po zapisach w `.maister/tasks` (zasada operatora)
- [ ] Bez CI na runnerach GitHuba (workspace CLAUDE.md)
