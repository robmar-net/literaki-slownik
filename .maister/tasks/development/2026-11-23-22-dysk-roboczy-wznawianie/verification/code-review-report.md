# Przegląd kodu #22 (dysk roboczy, wznawianie)

**Data**: 2026-11-23 · **Zakres**: `git diff aa50eca..HEAD` · **Status**: ⚠️ są uwagi (0 krytycznych, 4 ostrzeżenia, 9 info)

## TL;DR
- Nie ma błędów krytycznych. Kasowanie ma kilka zabezpieczeń: ponowną klasyfikację, `_inside`, porównanie z punktem montowania repo i sprawdzenie znacznika. Zamiana `RENAME_SWAP` i zapis trwały (F_FULLFSYNC, tmp, `os.replace`, sync katalogu) są poprawne. Kody 75–78 są dobrze sklasyfikowane.
- Ostrzeżenie 1: nadzorca po 75 bierze `marker_id` z manifestu, który leży na T7, czyli na dysku, którego właśnie brak. Wykrywanie „wolumen pod inną ścieżką → 76 od razu” w praktyce nie działa. Test tego nie łapie, bo w fiksturze manifest jest czytelny.
- Ostrzeżenie 2: `clean_work --apply` skasuje po 24 h kompletny, jeszcze niezweryfikowany przebieg A albo B (`INCOMPLETE` + symlink). Jest to zgodne ze spec, ale łatwo stracić 13 h pary.
- Ostrzeżenie 3: `build --resume` nie bierze blokady. `resume_reports.py` przyjmuje `reports: running`, czyli stan żywego buildu.
- Ostrzeżenie 4: przerwane kasowanie B w promocji (albo wpisu w `clean_work`) zostawia pół drzewa bez manifestu. Taka resztka dostaje klasę 4 i nikt jej już nie skasuje.
- 66 testów celowanych (supervised, clean_work, promote, volume, exit_codes, durable_write, resume, stage_loop, report_markers, resume_reports) przechodzi.

## Key Decisions
- Reset bez DELETE dla `constructions`/`decisions` uznaję za poprawny. Spec go zakłada, a kod ma `insert or ignore` (`constructions.py:522`, `decisions.py:312-314`).
- Kolejność DELETE w `DERIVED_TABLES`/`SGJP_TABLES` zgadza się z kluczami obcymi w `schema.sql`. `evidence_*` nie ma w schemacie, więc DROP jest bezpieczny.
- Wyrażenie `primary & 0xff in SQLITE_SPACE` w `build.py:153` jest poprawne, bo `&` wiąże silniej niż `in`. Zostaje jako info o czytelności.

## Open Questions / Risks
- Czy klasa 6 (`clean_work`) ma objąć przebiegi z wszystkimi etapami `complete`? Spec mówi „nieukończony”, a kod patrzy tylko na `readiness`.
- Trwałość podkatalogów stagingu na APFS przed skasowaniem kopii T7 nie jest jawnie zsynchronizowana (info 2). Ryzyko jest niskie, ale nikt go nie zmierzył.
- `build_pair.sh` w terminalu: zamknięcie okna wysyła SIGHUP. Nadzorca przekazuje go buildowi i kończy pracę bez wznowienia (zgodnie ze spec). Runbook powinien kazać uruchamiać parę przez `nohup` albo `tmux`.

## Ostrzeżenia

### W1. Nadzorca nie zna `marker_id`, gdy T7 zniknął
- **Miejsce**: `scripts/build_supervised.py:51-61`, wywołanie `:185`
- `_marker_id` czyta manifest przez symlink. Po zniknięciu T7 manifest jest nieczytelny, a `work_root` (na T7) też nie istnieje, więc wynik to `None`. Wtedy `_wait` nie woła `find` (`:125`), a `probe` pomija G2 (`:68`). Wolumen zamontowany jako `T7 1` daje 75 dopiero po 30 min zamiast 76 od razu (R9). Bezpieczeństwo zostaje, bo `--resume` sam sprawdza G2.
- **Naprawa**: zapamiętać `marker_id` przed pierwszym procesem i po każdym udanym starcie (z manifestu albo ze znacznika W), a nie liczyć go po 75. Do testu dodać przypadek z nieczytelnym manifestem.
- fixable: true

### W2. `clean_work --apply` kasuje kompletne, niezweryfikowane przebiegi
- **Miejsce**: `scripts/clean_work.py:199-209`
- Każdy przebieg przed `verify` ma `readiness=INCOMPLETE`. A i B po udanym buildzie, czekające ponad 24 h na przegląd, trafiają do klasy 6 i znikają razem z symlinkiem. Powód na liście („INCOMPLETE z symlinkiem”) nie mówi, że etapy są kompletne.
- **Naprawa**: przebieg z wszystkimi etapami `complete` (albo `reports` complete) oznaczać klasą 3 lub 4, albo przynajmniej podawać stan etapów w powodzie. Wymaga decyzji, bo spec tego nie rozróżnia.
- fixable: false (decyzja zakresu)

### W3. Brak blokady przebiegu w `build --resume`
- **Miejsce**: `literaki_slownik/build.py:508-527`, `scripts/resume_reports.py:50`
- Blokadę `logs/<nazwa>.lock` trzyma tylko nadzorca. Ręczne `build --resume` albo `resume_reports.py` (przyjmuje `reports: running`) przy żywym buildzie może zrobić trzy rzeczy: `begin_resume` zmieni `running` na `failed` i dopisze próbę, `reset_stage` skasuje tabele pod pracującym procesem, a `restart_in_place` usunie `build.sqlite`. Jest też ryzyko utraty zapisów manifestu przy dwóch piszących.
- **Naprawa**: `flock` w samym buildzie, na pliku per przebieg, innym niż blokada nadzorcy, np. `logs/<nazwa>.build.lock`. `build` i `--resume` biorą go przed pierwszą zmianą, a przy zajętej blokadzie kończą kodem 4.
- fixable: true

### W4. Przerwane kasowanie zostawia resztkę, której nikt nie skasuje
- **Miejsce**: `scripts/promote_run.py:231-235` (B), `scripts/clean_work.py:421-428`
- `shutil.rmtree` kasuje w kolejności `scandir`, więc `manifest.json` może zniknąć wcześnie. Po przerwie ponowna promocja widzi B bez manifestu, wpisuje `peer-kept` i ustawia `completed`. `clean_work` daje takiemu B klasę 4 (tylko lista). Zostaje ok. 22 GB do ręcznego usunięcia. Ten sam kształt ma `clean_work`: symlink jest kasowany przed drzewem, a przy przerwie zostaje „nieznana zawartość”. Kopia A pod `t7_path` nie ma tego problemu, bo ponowienie kasuje ją bezwarunkowo.
- **Naprawa**: przed `_remove` zapisać zamiar w `promotion.json` (`peer_deleting: true`) i przy ponowieniu dokończyć kasowanie bez kontroli manifestu. Druga możliwość: najpierw przemianować katalog na `.<nazwa>.deleting` i rozpoznawać to w `clean_work` jako klasę do skasowania.
- fixable: true

## Informacyjne
1. **Prywatne helpery między modułami**: `promote_run.py:75,80,212` (`canonical._full_sync`, `_sync_directory`), `database.py:8` (`_full_sync`). Proponuję upublicznić je (`full_sync`, `sync_directory`). `_copy_file` (`promote_run.py:66-86`) powiela logikę `write_bytes`.
2. **Trwałość katalogów stagingu**: `promote_run.py:150-151`. `mkdir` podkatalogów nie ma sync katalogu nadrzędnego, a `rename_swap` (`export.py:57-70`) nie synchronizuje `data/work`. Sync robi dopiero `_finish:212`, i to przed kasowaniem, więc kolejność jest dobra. Dla podkatalogów warto dodać `_sync_directory` po `mkdir` albo jeden sync całego drzewa przed S3.
3. **Dwie wersje `_remove`**: `promote_run.py:112-118` nie sprawdza symlinku przed `chmod(target)`, a `clean_work.py:111-119` sprawdza. Warto mieć jedną wspólną funkcję.
4. **Wydajność promocji**: `promote_run.py:126,158,167`. T7 jest czytany około 4 razy (pieczęć, kopia, sha256 źródła, ewentualnie pieczęć stagingu), a staging 2 razy. Hash można liczyć w trakcie kopii (`_copy_file`), co oszczędza jeden pełny odczyt 22 GB.
5. **Wyścig sygnału w nadzorcy**: `build_supervised.py:200-202,175`. Sygnał między `Popen` a `state['child']=child` albo tuż po `_wait` nie trafia do nowego procesu, więc build może biec 13 h mimo SIGTERM. Proponuję sprawdzać `state['signal']` przed `Popen` i zaraz po przypisaniu.
6. **`build_pair.sh:38`**: stdout nadzorcy trafia do `logs/<nazwa>.supervisor.log`, do którego nadzorca sam pisze zdarzenia. Końcowa linia nie ma pola `event`, a parser zdarzeń (jak w teście) się na niej wywróci. Lepiej kierować stdout do osobnego pliku, np. `logs/<nazwa>.result.json`. Brak też walidacji `PREFIKS`, np. `/` albo spacji. Cytowanie jest poprawne.
7. **Połykane błędy**: `build.py:408-412`. Błąd `close_attempt` po udanym buildzie, także G3, znika bez śladu, a build kończy się kodem 0. Przynajmniej warto dodać go do `diagnostics`. `clean_work.py:493-498` nie łapie `OSError` z kasowania, więc przy zniknięciu T7 w trakcie `--apply` wychodzi traceback zamiast kodu.
8. **`resume_reports.py:47,53`**: manifest bez `stages` albo `code` daje `KeyError` i traceback zamiast kodu 4.
9. **`measure_fullfsync.py:62-83`**: pomiar commitu na małej, rosnącej tabeli może zaniżać koszt na bazie 22 GB, a mediana ukrywa ogony. `quick_check` z `immutable=1` (`:88`) ignoruje hot journal. Sam wybór 4B jest przy tym bezpieczny (pełna trwałość).

## Metryki
- Najdłuższa funkcja: `clean_work.scan_internal` ok. 48 linii, `build_supervised.supervise` ok. 58 linii.
- Najgłębsze zagnieżdżenie: 4 poziomy (`supervise`).
- Potencjalne podatności: 0 (brak `shell=True`, brak wstrzyknięć; `git` z listą argumentów i oczyszczonym `GIT_*`).
- Ryzyko N+1: brak.

## Priorytety
1. W3: blokada buildu i wznowienia.
2. W1: `marker_id` znany przed zniknięciem dysku, plus test z nieczytelnym manifestem.
3. W4: idempotentne kasowanie B i wpisów `clean_work`.
4. W2: decyzja o klasie 6 dla przebiegów kompletnych.
5. Info 1–3: publiczne helpery, wspólne `_remove`, sync podkatalogów.
