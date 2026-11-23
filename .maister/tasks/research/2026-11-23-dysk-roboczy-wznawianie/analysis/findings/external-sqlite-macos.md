# Zewnętrzne: SQLite i macOS przy znikającym dysku USB

## TL;DR
- Zniknięcie dysku w trakcie transakcji SQLite daje `SQLITE_IOERR_*`; transakcja jest stracona, ale baza w trybie domyślnym (rollback journal `DELETE`, `synchronous=FULL`) zwykle zostaje spójna: przy ponownym otwarciu *hot journal* cofa przerwaną transakcję. Warunek: `-journal` leży obok bazy pod tą samą nazwą i nikt go nie usunął ani nie przeniósł.
- Nośnik USB może kłamać o `fsync`, a SQLite tego nie wykryje. Na macOS `fsync` nie opróżnia cache dysku; robi to `F_FULLFSYNC` (`PRAGMA fullfsync`, domyślnie wyłączone, także w Pythonie 3.15 z SQLite 3.54.1 na tym Macu).
- Wznawianie nie powinno opierać się na naprawie jednej 21-GB bazy. Lepiej: wyjście per etap lub część, zapis do pliku tymczasowego, `fsync`, potem `os.replace` w tym samym systemie plików, na końcu znacznik „gotowe” z hashem.
- Na tym Macu `/Volumes` ma właściciela `root:wheel` i prawa 755, więc proces użytkownika nie utworzy „sobowtóra” `/Volumes/Data` na dysku systemowym. Przed startem i przed każdym etapem i tak trzeba sprawdzić `ismount` i UUID wolumenu.
- W ciągu ostatnich 7 dni dysk zniknął raz: 2026-11-20 o 02:32:18 na 3 s, bez snu systemu. Dysk to Samsung PSSD T7 Shield 4 TB (USB 10 Gb/s, zasilany z portu, 4,48 W). Ten sam kontener APFS (`disk10`) mieści wolumen Time Machine `<wolumen Time Machine>`. W `/Volumes/Data` jest ślad `.DocumentRevisions-V100-bad-1`, a Spotlight indeksuje wolumen.

## Key Decisions
- **Zostaje rollback journal (`DELETE`) z `synchronous=FULL`; WAL nie jest potrzebny.** Build ma jednego pisarza i duże transakcje, a w WAL `ATTACH` traci atomowość między plikami (lang_attach). Rozważ `PRAGMA fullfsync=ON` tylko przy commitach etapów (koszt: każdy sync opróżnia cache dysku).
- **Jednostką wznowienia jest plik, nie transakcja.** Każdy etap lub część zapisuje osobny plik `.sqlite` przez `tmp` → `fsync` → `os.replace` → `fsync` katalogu, a potem znacznik z sha256. Po wznowieniu pomija się części, których znacznik i hash się zgadzają.
- **Etapy łączy `ATTACH` (tylko odczyt) albo końcowe scalenie.** Migawki robi `VACUUM INTO` lub backup API, nie `cp` otwartej bazy.
- **Ochrona przed zniknięciem dysku:** sprawdzić `os.path.ismount('/Volumes/Data')` i odczytać plik-znacznik z oczekiwanym `Volume UUID` (`<UUID wolumenu>…`) przed startem, przed każdym etapem i przed `os.replace`. Nie uruchamiać buildu przez `sudo`, nie robić `mkdir -p` od `/Volumes`, długi przebieg owinąć w `caffeinate -dimsu`.

## Open Questions / Risks
- **Przyczyna zniknięć jest nieznana.** W logu z 7 dni jest jedno zdarzenie: 2026-11-20 02:32:18 dysk `disk6` zniknął, a o 02:32:21 wrócił. Przerwa trwała 3 s, w `pmset -g log` nie ma wtedy snu ani wybudzenia, a kernel niczego nie zapisał. Pasuje to do resetu USB albo chwilowego spadku zasilania, nie do uśpienia (wniosek). Źródła podają też kabel, hub i firmware T7.
- **Nie wiadomo, czy mostek USB T7 przekazuje do NVMe polecenie opróżnienia cache z `F_FULLFSYNC`.** Apple tego nie gwarantuje dla USB. Bez tego nawet `fullfsync` nie chroni przed utratą zasilania dysku.
- **Uszkodzenie po odłączeniu jest możliwe mimo journala**, jeśli dysk przestawia kolejność zapisów (howtocorrupt §3.1). Każdą bazę po wznowieniu trzeba sprawdzić (`PRAGMA quick_check` lub hash zamrożonego pliku).
- **Time Machine pisze na ten sam fizyczny dysk.** To I/O w tle, a przy złym zasilaniu dodatkowe obciążenie (wniosek, niezmierzone).
- **Ślad `.DocumentRevisions-V100-bad-1`** z 2026-09-30 wskazuje na wcześniejszy problem wolumenu. Warto rozważyć `diskutil verifyVolume` (tylko na prośbę operatora).
- **Czas kopiowania 21 GB nie został zmierzony.** Teoretycznie przy ~1 GB/s (T7, 10 Gb/s) to około 20–60 s; przy spadku zapisu po wyczerpaniu cache SLC lub przy błędzie firmware FXI72P2Q (raporty: zapis spada do ~2 MB/s) może trwać kilka minut albo dłużej.

---

## 1. SQLite przy utracie urządzenia

| Temat | Ustalenie | Źródło |
|---|---|---|
| Błąd na otwartym połączeniu | `SQLITE_IOERR_WRITE`/`_READ` „might result from … a filesystem became unmounted while the file was open”; `_FSYNC` to błąd przy opróżnianiu buforów | https://www.sqlite.org/rescode.html |
| Co z transakcją | `SQLITE_IOERR`/`SQLITE_FULL` „may or may not” cofnąć całą transakcję; zalecenie: jawny `ROLLBACK` (porażka nieszkodliwa). Połączenie zamknąć; nowe otworzyć dopiero na zamontowanym dysku | https://www.sqlite.org/lang_transaction.html |
| Hot journal | Przy następnym otwarciu proces z blokadą EXCLUSIVE przepisuje strony z `-journal`, obcina plik i baza jest jak przed transakcją (§4.2–4.6). Szukany „in the same directory … name derived from the name of the file” (§9.5) | https://www.sqlite.org/atomiccommit.html |
| Czego nie robić | usuwać/przenosić/zmieniać nazwy `-journal`/`-wal` po awarii; kopiować bazę bez journala; zmieniać nazwę otwartej bazy; otwierać przez inną ścieżkę/symlink niż w chwili awarii (howtocorrupt §1.3–1.4, §2.5–2.6; atomiccommit §9.5) | https://www.sqlite.org/howtocorrupt.html |
| Kłamiące nośniki | „USB flash memory sticks seem to be especially pernicious liars regarding sync requests”; „SQLite must believe whatever the operating system and hardware tell it” (§3.1) | howtocorrupt |
| `synchronous` | FULL = domyślne dla rollback; NORMAL w rollback „very small (though non-zero) chance … corrupt”; w WAL NORMAL jest spójne, ale nietrwałe; OFF może uszkodzić przy awarii OS/zasilania | https://www.sqlite.org/pragma.html#pragma_synchronous |
| WAL | `-wal` „is part of the persistent state” – rozdzielenie z bazą = utrata/korupcja; sync tylko przy checkpoincie przy NORMAL; „sync failure during a COMMIT might result in loss of durability but not in a corrupt database” (poza checkpointem); długa transakcja = duży WAL | https://www.sqlite.org/wal.html, howtocorrupt §3.1 |
| `journal_mode=OFF/MEMORY` | przy awarii w trakcie transakcji „very likely go corrupt” – wykluczyć | pragma.html#pragma_journal_mode |
| `ATTACH` | atomowość między plikami tylko gdy nie WAL i nie `:memory:` | https://www.sqlite.org/lang_attach.html |

**macOS: fsync a F_FULLFSYNC**
- `man 2 fsync` (Apple) mówi, że po `fsync` „the drive itself may not physically write the data … for quite some time and it may be written in an out-of-order sequence”. `F_FULLFSYNC` „asks the drive to flush all buffered data”. Bazy danych, którym zależy na kolejności zapisów, powinny go używać. https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man2/fsync.2.html
- `PRAGMA fullfsync` (domyślnie off) włącza `F_FULLFSYNC` dla każdego sync. `checkpoint_fullfsync` (domyślnie off) robi to tylko przy checkpoincie WAL; przy `fullfsync=ON` przestaje mieć znaczenie. https://www.sqlite.org/pragma.html#pragma_fullfsync
- Pomiar na tym Macu (Homebrew Python 3.15, SQLite 3.54.1): `fullfsync=0`, `checkpoint_fullfsync=0`, `synchronous=2`; opcje kompilacji `DEFAULT_SYNCHRONOUS=2`, `DEFAULT_WAL_SYNCHRONOUS=2`, `TEMP_STORE=1`.
- W Pythonie `os.fsync` woła zwykłe `fsync()`, a `os.fdatasync` nie istnieje na macOS. Pełny flush daje `fcntl.fcntl(fd, fcntl.F_FULLFSYNC)`. https://docs.python.org/3/library/os.html#os.fsync

**Wniosek dla 21-GB bazy na USB:** transakcja przerwana zniknięciem dysku zostanie przy ponownym otwarciu cofnięta, o ile dysk nie kłamał o kolejności zapisów. Dysk kłamiący o fsync może zostawić bazę uszkodzoną, a SQLite tego nie zauważy. Dlatego potrzebny jest pomiar po wznowieniu (`quick_check`, hash) i niezmienne pliki ukończonych etapów (średnia pewność: źródła ogólne, bez testu na T7).

## 2. Wzorce checkpoint/resume

- **Atomowa podmiana:** `os.replace(src, dst)` jest atomowa na POSIX, ale może zawieść, gdy `src` i `dst` leżą w różnych systemach plików. Plik tymczasowy musi więc być w tym samym katalogu albo wolumenie. Kolejność: zapis → `flush` → `fsync`/`F_FULLFSYNC` pliku → `os.replace` → `fsync` deskryptora katalogu. https://docs.python.org/3/library/os.html#os.replace
- **Migawka bazy:** `VACUUM INTO 'plik'` daje „consistent snapshot”; cel nie może istnieć albo musi być pusty. Przy NORMAL/FULL wynik dostaje `fsync`, ale przerwany w trakcie „might be incomplete and corrupt”, więc też trzeba go podmieniać przez `tmp` + rename. Cel może leżeć na innym dysku (strona tego nie zabrania). https://www.sqlite.org/lang_vacuum.html
- **Backup API** (`sqlite3.Connection.backup` w Pythonie) kopiuje przyrostowo (`pages=`) i spójnie. Zapis do źródła z innego połączenia restartuje kopię. https://www.sqlite.org/backup.html, https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.backup
- **Plik per etap i `ATTACH`:** etap N czyta etapy <N przez `ATTACH … AS sN` (najlepiej w trybie `?mode=ro`/`immutable=1` przez URI) i pisze tylko swój plik. Liczbę dołączonych baz ogranicza `SQLITE_LIMIT_ATTACHED` (domyślnie 10 według dokumentacji limitów: https://www.sqlite.org/limits.html). Etapów jest 7, więc się mieści.
- **Wyjścia adresowane treścią i znacznik „done”:** to wzorzec Make, Snakemake i DVC. DVC trzyma w `dvc.lock` hash wejść i wyjść, a etap uruchamia ponownie tylko przy zmianie hasha. Snakemake usuwa niekompletne wyjścia przerwanego joba. https://dvc.org/doc/user-guide/project-structure/dvcyaml-files, https://snakemake.readthedocs.io/en/stable/project_info/faq.html. Dla tego projektu wystarczy prosty wariant: `stage.done.json` z `{inputs_sha256, output_sha256, code_identity}`, zapisany atomowo po `os.replace` wyjścia. Brak znacznika albo niezgodny hash oznacza, że etap trzeba wykonać ponownie (wniosek, nie cytat).
- **Koszt kopiowania 21 GB:** zob. Open Questions. Hash sha256 21 GB to dodatkowe odczytanie całego pliku (rzędu 1–2 min przy ~1 GB/s; niezmierzone).

## 3. macOS: dyski zewnętrzne

**Pomiar lokalny (tylko odczyt, 2026-11-23):**
- `mount`: `/dev/disk10s2 on /Volumes/Data (apfs, local, nodev, nosuid, journaled, noowners)`.
- `diskutil info`: Protocol USB, External, SSD, Removable Media: Fixed, Owners: Disabled, SMART Verified, `Volume UUID: <UUID wolumenu>`.
- `diskutil list disk10`: kontener na `disk6s2` (PSSD T7 Shield, 4,0 TB) zawiera `Data` (1,2 TB) i `<wolumen Time Machine>` (1,7 TB, cel Time Machine według `tmutil destinationinfo`).
- `system_profiler`: T7 Shield, Link Speed 10 Gb/s, Power Allocated 4,48 W (896 mA), bez huba (osobna magistrala).
- `pmset -g`: `disksleep 0`, `sleep 0` (sen blokują powerd i caffeinate), `standby 1`, `powernap 1`, `hibernatemode 3`.
- `mdutil -s /Volumes/Data`: Indexing enabled.
- `ls -la /Volumes`: `root wheel drwxr-xr-x`. W `/Volumes/Data` są `.Spotlight-V100`, `.fseventsd` i `.DocumentRevisions-V100-bad-1` (z 2026-09-30).
- `log show --last 7d`: zapytanie o diskarbitrationd dało 0 wierszy. Szersze zapytanie (`disk6`/`disk10` + unmount/eject/terminat/disappear) trafiło `storagekitd`: `Operation = Disappear` dla `disk6`, `disk6s1` i `disk6s2` 2026-11-20 o 02:32:18.283, potem `Operation = Appear` dla `disk6` o 02:32:21.500. Wcześniej, o 02:32:17.521, powerd zwolnił asercję `ExternalMedia … externalmediamounted` (age 276:29:45, czyli dysk był zamontowany ~11,5 doby). W `pmset -g log` w oknie 02:2x–02:3x nie ma sleep/wake, a kernel w 02:32:10–19 nie zapisał nic. Uwaga: jeden przebieg tego zapytania nie dowodzi, że innych zniknięć nie było; filtr mógł je ominąć.

**Co się dzieje z `/Volumes/<nazwa>`:**
- Przy poprawnym odmontowaniu macOS usuwa punkt montowania. Przy nagłym zniknięciu programy, które dalej piszą pod tę ścieżkę, mogą utworzyć zwykły folder `/Volumes/<nazwa>` na dysku systemowym („doppelganger”). Prawdziwy dysk montuje się wtedy jako `<nazwa> 1`, a programy dalej piszą do folderu na dysku systemowym. https://tidbits.com/2008/05/15/dealing-with-doppelganger-folders-in-volumes/, https://community.adobe.com/questions-675/false-mounts-993698
- Na tym Macu `/Volumes` ma prawa 755 i właściciela root, więc proces użytkownika dostanie `EACCES`/`ENOENT` i nie stworzy sobowtóra (pomiar uprawnień; wniosek o skutku, średnia pewność). Ryzyko zostaje dla procesów z `sudo` lub root i dla przypadku, gdy wolumen wróci jako `Data 1`, bo coś innego zajęło `Data`.
- **Wykrywanie:** `os.path.ismount(p)` porównuje `st_dev` ścieżki `p` i `p/..` (albo inode). Zwykły katalog na dysku systemowym da `False`. https://docs.python.org/3/library/os.path.html#os.path.ismount. Dodatkowo plik-znacznik na wolumenie z oczekiwanym UUID (`diskutil info -plist` → `VolumeUUID`) chroni przed podmianą wolumenu. Można też zapamiętać `os.stat(run_dir).st_dev` na starcie i porównywać przed każdym etapem.

**Przyczyny odłączeń (raporty użytkowników i producenta, niska do średniej pewność):**
- Za mało prądu z portu albo hub bez zasilania. Pomaga zasilany hub lub inny port. Pomaga też kabel. https://discussions.apple.com/thread/252346675?page=2, https://www.seagate.com/gb/en/support/kb/disk-not-ejected-properly-on-mac/
- Usypianie dysku lub komputera, wybudzanie (Power Nap, standby). Pomaga `pmset -a disksleep 0`; tutaj jest już 0. Seagate zaleca blokować sen komputera i dysku. https://discussions.apple.com/thread/254133497
- T7: zgłoszenia „Disk Not Ejected Properly” po wybudzeniu i na hubach. T7 Shield 4 TB z firmware FXI72P2Q: zapis spada do ~2 MB/s lub się zawiesza (mostek ASM2364). https://discussions.apple.com/thread/255179257, https://us.community.samsung.com/t5/Monitors-and-Memory/T7-Shield-4TB-Firmware-FXI72P2Q-Severe-Write-Speed-Regression/td-p/3386826
- Spotlight i Time Machine dają tylko dodatkowe I/O; nie znalazłem źródła, które wiąże je z odłączeniem.

**Łagodzenie (do decyzji, bez zmian w tym badaniu):**
- `caffeinate -dimsu <build>` na czas przebiegu. https://ss64.com/mac/caffeinate.html
- `mdutil -i off /Volumes/Data` (wymaga sudo) albo dodanie wolumenu do Spotlight → Prywatność. Wyłącza indeksowanie 21-GB baz. https://ss64.com/mac/mdutil.html
- Nie uruchamiać buildu w czasie backupu Time Machine na ten sam fizyczny dysk; można też `tmutil` wykluczyć/przesunąć harmonogram (do decyzji operatora).
- `noowners` jest już włączone; `nodev,nosuid` nie przeszkadzają.
- Bezpośredni port, krótki kabel 10 Gb/s, ewentualnie zasilany hub. Sprawdzić wersję firmware T7.
