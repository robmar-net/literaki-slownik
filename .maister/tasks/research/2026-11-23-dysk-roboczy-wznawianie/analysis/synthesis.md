# Synteza: dysk roboczy na /Volumes/Data i wznawianie buildu

## TL;DR
- Zniknięcie T7 nawet na 3 s zabija trwający build: otwarte deskryptory po ponownym montowaniu są martwe, SQLite zwraca `SQLITE_IOERR`. Ratuje nas tylko to, co już leży trwale na dysku, i to, czy da się od tego zacząć.
- Dziś nie da się: `create_run` odmawia ponownego użycia katalogu, a wznawia się tylko całe `reports`. Każda awaria przed `reports` to praca od zera (do ~13 h).
- Najtańsza ochrona przed USB to nie budować na USB: build na dysku wewnętrznym (193 GB wolne, para ~44 GB), gotowe przebiegi archiwizować na `/Volumes/Data`.
- Wznawianie per etap w tej samej bazie (+ znaczniki per raport) jest potrzebne niezależnie od dysku, bo v32 przerwał restart maszyny.

## Key Decisions
- Lokalizacja: hybryda (build wewnątrz, archiwum na T7) wygrywa z symlinkiem i ze zmienną środowiskową pod względem ryzyka; symlink zostaje jako wariant, gdy zabraknie miejsca wewnątrz.
- Wznawianie: wariant (a) „etapy w jednej bazie” jako podstawa; (b) migawka tylko przy budowie na USB; (c) ATTACH odrzucony na teraz (łamie trzy kontrakty).
- Poprawka `.gitignore` (R1) i strażnik montowania obowiązują w każdym wariancie, który dotyka `/Volumes`.

## Open Questions / Risks
- Normalny czas `decisions` nieznany (v32: 61 h, anomalia). Od niego zależy, ile traci (a) przy awarii w tym etapie.
- Czy wznowiony build daje ten sam `logical_content` co świeży (rowid po `DELETE` + ponownym imporcie). Trzeba testu, zanim (a) wejdzie do pary A/B.
- Czy `data/work` na dysku wewnętrznym trafia do Time Machine, który pisze na ten sam T7 (44 GB kopii co godzinę). Niesprawdzone.
- Piny POP/POP00/TEMATY wskazują usunięty `lists-v31-20261012-162111-a`: decyzja właściciela.

## 1. Pytanie badawcze
Jak trzymać duże pliki generatora (build.sqlite ~21 GB na przebieg, para A/B, build ~13 h) na `/Volumes/Data` (Samsung T7 Shield USB, znika na sekundy, ostatnio 2026-11-20 02:32:18, 3 s) i jak wznowić przerwany build bez pracy od zera, zachowując K1–K10 i parę A/B.

## 2. Analiza krzyżowa

### Potwierdzone przez kilka źródeł (wysoka pewność)
| Ustalenie | Źródła |
|---|---|
| Kod nie ma na sztywno `data/work`; wszystko idzie przez `--run-dir`, `build_pair.sh` składa `data/work/$1-$stamp-$side` | paths (cli.py:25–47, build_pair.sh:12–15), build |
| K1–K10 i K8 porównują hashe i treść, nie ścieżkę przebiegu; przeniesienie katalogu przebiegu jest bezpieczne, przeniesienie repo nie | paths (verify.py:140–157, 416–462; export.py:58–100) |
| Baza: journal `delete`, `synchronous=FULL`, bez `fullfsync`; to domyślne zachowanie, a hot journal cofa przerwaną transakcję przy ponownym otwarciu tą samą ścieżką | build (PRAGMA na v32-a), external (atomiccommit §4, §9.5; pomiar SQLite 3.54.1) |
| `constructions` i `decisions` są idempotentne (`insert or ignore`), `import_*` i `links` nie | build (constructions.py:504, decisions.py:281–315, build.py:21–49, links.py:130–165) |
| `reports` to ~65% czasu (8–8,5 h), nie pisze do bazy; `unresolved` sam 4,1 h | build (performance.json v32-a, work-log v30) |
| ATTACH per etap łamie FK między plikami, `logical_content_report` (tylko `main`), `database_sha256` jednego pliku | build (schema.sql:51–58, reports.py:295–307, verify.py:619, export.py:82), external (lang_attach) |

### Sprzeczności rozwiązane
- **Cichy zapis na dysk systemowy (R2).** Paths: `mkdir(parents=True)` przy pustym `/Volumes/Data` zapisze 21 GB na dysk wewnętrzny. External: `/Volumes` to `root:wheel 755`, więc proces użytkownika nie utworzy sobowtóra. Rozstrzygnięcie: ryzyko jest niskie dla zwykłego procesu, ale realne przy `sudo`, przy wolumenie zamontowanym jako `Data 1` i przy resztce katalogu po innym programie. Strażnik (ismount + znacznik z UUID) zamyka wszystkie trzy przypadki za kilka linii; nie opierać się na prawach `/Volumes`.
- **Czas buildu: 12,5–13,8 h vs ~14 h w briefie.** Pomiary `/usr/bin/time` v27–v31: 9,7–13,8 h. Przyjmujemy ~13 h.
- **Wolne miejsce.** Brief: 1 TB wolne na T7; zlecenie: ~193 GB na dysku wewnętrznym. To dwa różne dyski; oba wystarczą na parę (~44 GB), wewnętrzny tylko na jedną parę z zapasem.

### Ocena pewności
- Wysoka: mapa etapów, idempotentność, ścieżki, kontrakty K, zachowanie hot journal (dokumentacja).
- Średnia: że journal uratuje bazę po zniknięciu T7 (zależy, czy mostek ASM2364 nie przestawia zapisów); że `F_FULLFSYNC` dociera przez USB do NVMe.
- Niska: przyczyna zniknięć (zasilanie/kabel/firmware), czas kopiowania 21 GB na T7, normalny czas `decisions`.

## 3. Wzorce i tematy

| Wzorzec | Opis | Gdzie | Ocena |
|---|---|---|---|
| Jedna baza, jeden proces | 7 etapów, `build.sqlite` jako cały stan danych | build.py:92–248 | proste, ale granulacja awarii = cały build |
| Manifest jako dziennik etapów | `pending/running/complete/failed` + `updated`, zapis atomowy (mkstemp+fsync+replace) | run.py:47–63, canonical.py:33–44 | dobra podstawa wznawiania; brak fsync katalogu i `F_FULLFSYNC` |
| Idempotencja przez `insert or ignore` | klucz = sha payloadu | constructions, decisions | dojrzałe, gotowe do wznawiania |
| Wznawianie ad hoc | `resume_reports.py` z warunkami `tree_sha256`/`manifest_sha256` | scripts/resume_reports.py:46–54 | działa, ale tylko całe `reports`; otwiera bazę `rw` |
| Ścieżki względne w konfiguracji, bezwzględne w manifeście | `../../cache`, `../../data/work`; `resolved_path` bezwzględnie | inputs.py:33–42, config/generator/*.json | symlink przezroczysty, env/flaga nie przekieruje pinów |
| Pieczęć hashem pliku | `database_sha256` całej bazy | verify.py:619, export.py:82 | wiąże z „jedną bazą”; wyklucza ATTACH |
| Logi obok przebiegu | `.out.json`/`.err` w `data/work` | build_pair.sh:12–15 | giną razem z dyskiem (R4) |

## 4. Kluczowe wnioski

1. **3 s to tyle samo co 3 h.** Po zniknięciu urządzenia macOS montuje wolumen na nowo, a deskryptory procesu są martwe. Build pada z `SQLITE_IOERR_*`. Czas przerwy nie ma znaczenia; liczy się, ile pracy leży trwale i czy da się od niej ruszyć. (wysoka)
2. **Dziś każda awaria przed `reports` kosztuje cały build.** `create_run` odmawia istniejącego katalogu (run.py:42–45), status zostaje `running`, a błąd zapisu `failed` jest połykany (build.py:249–253). (wysoka)
3. **Budowa na wewnętrznym dysku usuwa problem USB w całości, przy zerowej zmianie kodu.** Przeniesienie gotowego przebiegu nie łamie K1–K10 (porównania po hashach). Kopię można ponowić, bo źródło zostaje. (wysoka)
4. **Wznawianie per etap jest tanie, bo połowa pracy jest już idempotentna.** Do zrobienia: zgoda na istniejący katalog, `running`→`failed` przy starcie, obcięcie i ponowienie `import_*`, `DROP … IF EXISTS` dla `links`, znaczniki per raport. (wysoka co do kształtu, średnia co do identyczności wyniku)
5. **Największy zysk to znaczniki per raport.** `reports` to 65% czasu; dziś wznowienie powtarza wszystkie 7–9 raportów. Z znacznikami najgorsza strata to `unresolved` (4,1 h). (wysoka)
6. **Migawka po etapie chroni przed korupcją, nie tylko przed przerwą.** Na USB, który może kłamać o kolejności zapisów, niezmienna kopia z hashem jest jedyną pewną granicą. Koszt: +21 GB i czas kopii. Backup API zachowuje strony 1:1; `VACUUM INTO` może zmienić rowid w tabelach bez `INTEGER PRIMARY KEY` (lang_vacuum). (średnia)
7. **Symlink `data/work` bez poprawki `.gitignore` wycieknie do publicznego repo.** `/data/work/` (z ukośnikiem) nie pasuje do symlinku. Poprawka: `/data/work` i `/cache` bez ukośnika. (wysoka, z dokumentacji gitignore)
8. **Hot journal musi zostać obok bazy, pod tą samą ścieżką.** Nie kopiować, nie przenosić ani nie otwierać przez inną ścieżkę/symlink niż w chwili awarii, dopóki SQLite nie cofnie transakcji. (wysoka)

## 5. Relacje i zależności

```
config/generator/sources.json ──(../../cache)──> cache/ (870 MB, zostaje wewnątrz)
            │ hash wejść
            ▼
build_pair.sh ─> build --run-dir data/work/<p>-<stamp>-<a|b>
   preflight → import_sgjp → import_kwjp → constructions → decisions → links → reports
   └──────────── build.sqlite (21–22 GB) ─────────────────────────────┘     └─ reports/*.json
   manifest.json (stany etapów, code_identity K8, inputs z resolved_path)
            ▼
verify (K1–K10, --peer-run B) ─> export (sha256 bazy, FROZEN) ─> explain (ro)
            ▲
pop/pop00/tematy-sources.json ──(../../data/work/<przebieg>)── piny na przebiegi
```

Punkty styku z dyskiem: `create_run` (mkdir), `connect` (ścieżka absolutna, `-journal` obok), `write_json` (rename), `build_pair.sh` (logi), piny `../../data/work`.

## 6. Luki i niepewności
- Brak normalnego czasu `decisions` i czasów etapów v27–v31 (usunięte `performance.json`).
- Niezmierzone: czas `quick_check` 21 GB, kopii 21 GB na T7, backup API 21 GB.
- Niezweryfikowane: czy `mkdir` przez wiszący symlink daje komunikat R3 (wniosek z CPythona).
- Nieznana przyczyna zniknięć T7; jedno zdarzenie w 7 dniach z jednego zapytania do logu.
- Czy `data/work` jest wykluczone z Time Machine.
- Prywatność: findings zawierają UUID wolumenu i ścieżki `~/...`; brief mówi, że repo `literaki-slownik` jest publiczne. Nie przenosić UUID do kodu ani konfiguracji w repo.

## 7. Synteza według ramy technicznej

### Lokalizacja (warianty)
| Wariant | Zmiana | Koszt | Ryzyko | K1–K10 |
|---|---|---|---|---|
| L1 symlink `data/work` → `/Volumes/Data/literaki-slownik/work` | `ln -s`, `.gitignore` bez ukośnika | ~0 kodu | build na USB; wiszący symlink daje mylący błąd (R3); wyciek przy złym `.gitignore` (R1) | bez zmian; piny `../../data/work` działają |
| L2 korzeń roboczy z env/flagi (`LITERAKI_WORK_ROOT` w `build_pair.sh`) | skrypty + runbooki (~20 miejsc w docs) | mały kod, sporo dokumentacji | piny w 4 konfiguracjach nie podążą; cichy zapis przy pustym punkcie montowania (R2) | bez zmian, ale piny trzeba zmienić → nowy `manifest_sha256` |
| L3 hybryda: build wewnątrz, archiwum na T7 | skrypt `archive_run` (kopiuj → sha256 → usuń źródło) | mały | 193 GB wewnątrz: jedna para naraz; TM może kopiować `data/work` na T7 | bez zmian (przeniesienie katalogu przebiegu jest bezpieczne) |

Wspólne: strażnik montowania (ismount + znacznik `.literaki-work-volume` z UUID odczytanym z `diskutil info -plist`, porównany przy starcie, przed każdym etapem i przed `os.replace`); fail-fast, nigdy `mkdir -p` od `/Volumes`; sprawdzenie wolnego miejsca ≥ 2×22 GB na stronę.

### Wznawianie (warianty)
| Wariant | Przetrwa 3 s USB | Strata na awarię | Zmiana kodu | K1–K10 / A-B | Miejsce |
|---|---|---|---|---|---|
| dziś | nie | do ~13 h (w `reports` do 8,5 h) | — | — | 22 GB |
| (a) etapy w jednej bazie + znaczniki raportów | tak, jeśli journal cofnie (średnia) | bieżący etap: ≤2,4 h import, ~25 min konstrukcje/links, `decisions` nieznane, raport ≤4,1 h | średnia (~200–400 linii + testy) | K8: nowa tożsamość kodu (raz); potrzebny test „wznowiony = świeży” | 22 GB |
| (b) migawka po długim etapie (backup API do `checkpoint.sqlite`) | tak, także przy korupcji | jak (a) + czas migawki | (a) bez idempotencji importów + kopia | baza po przywróceniu identyczna stronami | +22 GB/stronę |
| (c) plik per etap + ATTACH | tak, pliki niezmienne | jak (a) | duża; ADR, zmiana FK, `logical_content`, pieczęci, explain/verify | zmienia kontrakt pieczęci | ~22 GB + narzut |
| (d) build wewnątrz, potem przenieś | tak, USB nie bierze udziału | 0 od USB; inne awarie jak dziś (lub jak a) | ~0 | bez zmian | 44 GB/parę wewnątrz |

## 8. Wnioski
- **Główne:** (d)+L3 rozwiązuje USB od razu; (a) rozwiązuje restart/kill i jest potrzebne zawsze. Razem dają: zniknięcie T7 nie dotyka buildu, a restart maszyny kosztuje najwyżej bieżący etap.
- **Poboczne:** poprawić `.gitignore` teraz; przenieść logi `.out.json`/`.err` tak, by nie ginęły z dyskiem; trwale zapisywać czasy etapów w manifeście; `resume_reports.py` otwierać `ro`.
- **Rekomendacja:** patrz `outputs/research-report.md` §9.
