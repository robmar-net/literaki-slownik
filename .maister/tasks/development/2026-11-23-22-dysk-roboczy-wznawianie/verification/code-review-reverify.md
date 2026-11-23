# Ponowny przegląd poprawek (commit 7aed1ea)

## TL;DR
✅ Ostrzeżenia 1–9 i 11–12 są rozwiązane. Ostrzeżenie 10 rozwiązano częściowo: tryb 4C zostaje z uzasadnieniem, dodano walidację. Krytycznych błędów brak.
Poprawki wprowadziły 1 nowe ostrzeżenie: błąd ENOENT/CANTOPEN na T7 daje 75 także przy błędzie w kodzie (wtedy 3 wznowienia i mylący kod końcowy). Doszło też 7 uwag info.
Testy celowane (6 modułów, 61 testów) przechodzą. Nie uruchamiano buildu słownika i nie dotykano `/Volumes`.

## Open Questions / Risks
- **Klasa 3 „kompletny, czeka na verify” nie wygasa.** Przebieg, który oblał verify (verify ustawia tylko VERIFIED, `verify.py:598-634`), zostaje na T7 na zawsze. Tak samo B, którego promocja zachowała (`peer-kept`). Każdy zajmuje ~22 GB i trzeba go skasować ręcznie. Zgodne z decyzją właściciela, ale warto, żeby raport o tym mówił.
- Watchdog nie był sprawdzony na prawdziwym zawieszeniu USB ani na pełnym etapie `reports`. Testy podstawiają `progress`.
- Odłączenie T7 w trakcie kasowania `.deleting` nie było sprawdzone na sprzęcie.

## Ostrzeżenia 1–12
| # | Stan | Dowód |
|---|---|---|
| 1 | rozwiązane | `build.py:135-137,165-168`: błąd urządzenia na wolumenie roboczym daje 75. Test `test_exit_codes` sprawdza 75 na T7 i 4 na dysku wewnętrznym. |
| 2 | rozwiązane | `build.py:454,459-464,536`: blokada `.<nazwa>.build.lock` na cały build i `--resume`, przed pierwszą zmianą. `resume_reports.py:44` odmawia przy trzymanej blokadzie. `clean_work.py:147-148` traktuje ją jako klasę 3. |
| 3 | rozwiązane | `build_supervised.py:217,219,230`: `marker_id` jest zapamiętany przed pierwszym procesem i odświeżany `or marker_id`. Test w `test_build_supervised.py:172`. |
| 4 | rozwiązane | `workfs.py:426-460`: kasowanie przez rename na `.deleting` i `finish_deleting`. Wywołania w `promote_run.py:188-191` i `clean_work.py:130,386,395-401`. Test w `test_promote_run.py:156`. |
| 5 | rozwiązane (wariant rekomendowany) | `clean_work.py:150-153`. Skutek uboczny opisano w Open Questions. |
| 6 | rozwiązane | runbook §5 (`:183-200`, `nohup … & disown`, `caffeinate` po restarcie), `cli.md:79-82,108-109`. `build_supervised.py:279` zostawia SIGHUP ignorowany pod nohup. |
| 7 | rozwiązane | `build_supervised.py:100-150` (`progress`, `stop_child`, `watch`), `:178` (`_stalled` daje 75, 76 albo 4). Domyślnie 120 min, wartość 0 wyłącza watchdog. |
| 8 | rozwiązane | `volume.py:66-81` (`check_work_root`), używane w `volume.py:87`, `build_supervised.py:82`, `build_pair.sh:23`, `clean_work.py:90` i `init_work_volume.py:43`. Korzeń na dysku repo daje wszędzie 76. |
| 9 | rozwiązane | `volume.check_resume` jest używane w `build.py:543`. |
| 10 | częściowo (zaakceptowane) | Walidacja w `database.py:30-32`. Tryb 4C zostaje jako zapasowy z uzasadnieniem w `database.py:12`. |
| 11 | rozwiązane | `workfs.py` zbiera blokady, `remove_tree`, `tree_size` i `is_within`. W `canonical` są publiczne `full_sync`, `sync_directory` i `copy_durable`. Zostaje drobiazg: nadzorca ma własny `flock` (`build_supervised.py:202`). |
| 12 | rozwiązane | `work-log.md:8-16`. |

## Nowe problemy
### Ostrzeżenie
**N1. ENOENT/CANTOPEN/EROFS na T7 daje 75 bez względu na ścieżkę** (`build.py:137,165-168`).
- Na dysku wewnętrznym nic się nie zmieniło: bez `work_volume` jest 4.
- Na T7 deterministyczny `FileNotFoundError` przechodzi przez strażnika i daje 75. Może to być błąd w kodzie, brak pliku na dysku wewnętrznym albo `SQLITE_CANTOPEN` katalogu temp.
- Nadzorca wtedy sondę zalicza od razu i wznawia. Po `max-resumes` (3) kończy kodem 75, który wskazuje na dysk, a nie na kod. Każde wznowienie powtarza etap, a etap może trwać godziny.
- Poprawka: dla ENOENT i CANTOPEN wymagać, by `error.filename` leżał w realpath przebiegu. Albo w nadzorcy: dwa kolejne 75 w tym samym etapie przy zdrowej sondzie zamieniać na 4.

### Info
- **N2. Fałszywy stall, gdy nie da się odczytać czasu CPU.** Jeśli `ps` zwraca pusto albo zawodzi (`build_supervised.py:113-118`), postęp liczy się tylko z mtime. Etap `reports` czyta bazę godzinami i wtedy po 120 min zostaje zabity, choć jest zdrowy. Kończy się kodem 4: para staje, danych nie traci się. Nadzorca nie loguje, że CPU jest nieznane. Warto dodać zdarzenie w logu.
- **N3. Proces w nieprzerywalnym I/O przeżywa SIGKILL** (`stop_child`) i dalej trzyma blokadę buildu. Po 75 → wait → `--resume` wznowienie dostaje 4 (blokada), a nadzorca kończy kodem 4. Wynik jest bezpieczny, ale warto opisać go w runbooku.
- **N4. Blokada zależy od ścieżki w postaci podanej** (`workfs.py:335-338`, `absolute()` bez realpath). `build --resume` uruchomiony ręcznie przez ścieżkę T7 zamiast symlinku `data/work` bierze inną blokadę i nie wyklucza się z nadzorcą. `clean_work` sprawdza tylko blokady w `data/work`.
- **N5. `.X.deleting` wydania wygląda jak wydanie.** Jeśli przerwane kasowanie zostawiło w kontenerze `release-manifest.json`, `_find_releases` (`clean_work.py:224-236`) bierze takie drzewo za wydanie. Lista robi się zaszumiona (klasa 7), ale `--apply` dokańcza je najpierw (`finish_internal`).
- **N6. Pliki `.<nazwa>.build.lock` nigdy nie znikają.** Zostają w `data/work` także po skasowaniu przebiegu. Są puste i skany je pomijają.
- **N7. Błąd w `clean --apply` gubi listę.** Przerwanie w połowie (`clean_work.py:440-447`) zwraca tylko błąd, bez listy tego, co już skasowano. Ponowne `--apply` jest bezpieczne.
- **N8. Szerokie `SQLITE_IOERR`.** Kod główny IOERR obejmuje też rozszerzenia niezwiązane z odłączeniem, np. `IOERR_NOMEM`. Na T7 dają 75, czyli ten sam efekt co w N1, tylko rzadszy.

## Sprawdzone bez uwag
- **Rename `.deleting`.** Cel leży w tym samym katalogu, więc na tym samym wolumenie. Przed rmtree jest sync katalogu. Resztka pod tą samą nazwą jest kasowana. Równoległe dokańczanie toleruje `FileNotFoundError` (`workfs.py:405-418`, Python 3.15, `onexc`). Nazwę `.*.deleting` tworzy tylko `delete_tree`, a nazwy przebiegów nie zaczynają się od kropki. Potrzebny przebieg nie dostanie więc tej nazwy.
- **Blokada buildu a promocja i export.** Blokada leży obok symlinku, więc ani `rename_swap`, ani `restart_in_place` jej nie ruszają. `scan_t7` i `scan_internal` ją pomijają. Promocja dotyczy tylko VERIFIED, a `--resume` takiego przebiegu odmawia (5) po wzięciu blokady.
- **Korzeń na dysku repo daje teraz 76.** Wcześniej `probe` dawał 75. Regresji to nie wprowadza: przy odpiętym T7 korzeń `<wolumen>/literaki-slownik/work` nie istnieje i nadal daje 75.
- **Watchdog.** Proces zdrowy zużywa czas CPU (user+sys), więc nie zostanie zabity. `ps` ma limit 30 s, sygnał przed `Popen` jest obsłużony, `watch` przy kodzie ujemnym zwraca 128+N.
