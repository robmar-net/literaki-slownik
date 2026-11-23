# Rejestr decyzji: build na T7 i wznawianie

Projekt: [high-level-design.md](high-level-design.md) · Warianty: [solution-exploration.md](solution-exploration.md) · Data: 2026-11-23

## TL;DR
8 decyzji, wszystkie przyjęte. Wybór 4B/4C w ADR-007 zapadnie po pomiarze.
Najważniejsze: wznawianie per etap w tej samej bazie (ADR-003) i znaczniki per raport (ADR-004). Razem ograniczają stratę do bieżącego etapu albo raportu.
Kod wyjścia 75 (ADR-005) to jedyny sygnał, po którym nadzorca ponawia pracę (ADR-006).
Historia prób jest objęta pieczęcią, ale nie wchodzi do K8 (ADR-008).

## Key Decisions
- ADR-001: symlink `data/work` na T7 (1A).
- ADR-002: strażnik G1+G2+G3; UUID tylko na wolumenie.
- ADR-003: `build --resume` per etap (2A).
- ADR-004: znaczniki per raport (2B).
- ADR-005: kody wyjścia 75–78.
- ADR-006: nadzorca (3B na 3A).
- ADR-007: `fullfsync` według pomiaru (4B/4C), `quick_check`.
- ADR-008: historia prób w manifeście i test „wznowiony = świeży” (5B).

## Open Questions / Risks
- ADR-007: brak pomiaru kosztu `fullfsync` i czasu `quick_check` na T7.
- ADR-003: równość `logical_content` po odbudowie tabel importu potwierdzi dopiero test.
- ADR-008: brzmienie decyzji 5B mówi „poza zapieczętowanym rdzeniem”. Projekt kładzie historię **w** rdzeniu pieczęci, a poza K8. Uzasadnienie jest niżej. Jeśli właściciel miał na myśli co innego, trzeba to potwierdzić.

---

<a id="adr-001"></a>
## ADR-001: Symlink `data/work` na wolumen roboczy T7

### Status
Accepted

### Context
Właściciel chce buildu na T7. Kod bierze `--run-dir`, a `build_pair.sh`, piny w 4 konfiguracjach i ~20 miejsc w runbookach używają `data/work/...`. K1–K10 porównują hashe, nie ścieżki. `.gitignore` z `/data/work/` nie łapie symlinku, więc symlink z prywatną ścieżką trafiłby do publicznego repo. Logi `.out.json`/`.err` leżą obok przebiegu i zginęłyby razem z dyskiem.

### Decision Drivers
- Bez zmian w ścieżkach, pinach i runbookach.
- Bez wycieku prywatnej ścieżki do publicznego repo.
- Logi muszą przetrwać zniknięcie T7.

### Considered Options
1. 1A: symlink `data/work` → wolumen roboczy na T7.
2. 1B: korzeń z env/flagi (`LITERAKI_WORK_ROOT`).
3. 1C: symlink per przebieg.

### Decision Outcome
Wybrana opcja 1A, bo nie zmienia ani jednej ścieżki w kodzie i konfiguracji. Do tego `.gitignore` dostaje wpisy `/data/work`, `/cache` i `/logs` bez ukośnika, a `build_pair.sh` pisze logi do `logs/` na dysku wewnętrznym.

### Consequences

#### Good
- Piny `../../data/work` i runbooki działają bez zmian.
- K1–K10 i `manifest_sha256` bez zmian.
- Logi i log nadzorcy przetrwają zniknięcie dysku.

#### Bad
- Wszystkie przebiegi idą na T7, także małe.
- Wiszący symlink daje mylący błąd, dopóki nie przechwyci go strażnik (ADR-002).
- Absolutne `resolved_path` w manifeście pokażą ścieżkę po `resolve()`. To bez wpływu na K, ale widać ją w metadanych.

---

<a id="adr-002"></a>
## ADR-002: Strażnik wolumenu G1+G2+G3 w kodzie buildu

### Status
Accepted

### Context
Po ponownym montowaniu deskryptory są martwe. Wolumen może wrócić jako `Data 1`, a pod `/Volumes/Data` może pojawić się inny dysk albo pusty katalog (przy `sudo` lub resztce po innym programie). `create_run` robi dziś `mkdir(parents=True)`. Repo jest publiczne, więc UUID wolumenu nie może trafić do kodu ani konfiguracji.

### Decision Drivers
- Każdy brak dysku ma dawać głośny błąd z rozpoznawalnym kodem.
- Nic nie może się zapisać na dysk systemowy zamiast na T7.
- W repo nie może być żadnego identyfikatora sprzętu.
- Strażnik nie może przeszkadzać testom ani buildom na dysku wewnętrznym.

### Considered Options
1. Tylko prawa `/Volumes` (root:wheel 755).
2. Strażnik tylko w `build_pair.sh`.
3. G1+G2+G3 w kodzie buildu.

### Decision Outcome
Wybrana opcja 3, bo tylko kod buildu widzi każdy etap i każde `os.replace`.
- G1: punkt montowania ścieżki po `resolve()` przechodzi `ismount`.
- G2: znacznik `.literaki-work-volume` w korzeniu roboczym (UUID z `diskutil` i losowy `marker_id`) jest zakładany raz, przez `scripts/init_work_volume.py`. Manifest przebiegu zapisuje tylko `marker_id`.
- G3: `st_dev` katalogu przebiegu zapamiętane w procesie i sprawdzane przed etapem i przed `os.replace`. Przy `--resume` liczy się G2, bo `st_dev` zmienia się po ponownym montowaniu.
- Ścieżka na systemie plików `/` bez znacznika: strażnik przepuszcza (testy, buildy wewnątrz). Wolumen zewnętrzny bez znacznika: kod 76.
- `create_run` tworzy tylko ostatni poziom. Wolne miejsce: ≥50 GB na stronę przy starcie. Build nigdy nie działa przez `sudo`.

### Consequences

#### Good
- Strażnik łapie `Data 1`, podmianę dysku, pusty katalog i wiszący symlink.
- UUID zostaje na wolumenie. W manifeście jest tylko losowy `marker_id`.
- Testy hermetyczne działają bez zmian, bo `tmp` leży na `/`.

#### Bad
- Operator musi raz założyć znacznik.
- Znacznik jest jeszcze jednym plikiem, który można przypadkiem usunąć. Wtedy kod 76 i ręczna decyzja.

---

<a id="adr-003"></a>
## ADR-003: `build --resume` per etap w tej samej bazie

### Status
Accepted

### Context
Dziś `create_run` odmawia istniejącego katalogu, a wznawia się tylko całe `reports` (`scripts/resume_reports.py`). `constructions` i `decisions` są idempotentne (`insert or ignore`). `import_*` (zwykły INSERT przy PK) i `links` (`create table`) nie są. Status po awarii zostaje `running`. ATTACH per etap łamie FK, `logical_content_report` i `database_sha256`.

### Decision Drivers
- Strata ograniczona do bieżącego etapu.
- Bez zmiany kontraktu pieczęci i K1–K10.
- Jak najwięcej z istniejącej idempotencji.

### Considered Options
1. 2A: etap w tej samej bazie.
2. 2C: cięcie długich etapów od środka.
3. Plik per etap + ATTACH.
4. Migawka po etapie (3C).

### Decision Outcome
Wybrana opcja 2A, bo połowa etapów jest już idempotentna, a pozostałe da się odbudować prostym `DELETE` albo `DROP IF EXISTS`.
- `--resume` wymaga tego samego `tree_sha256`, czystego kodu i tego samego `manifest_sha256`. Przebieg nie może być `VERIFIED`/`FROZEN`.
- Przy starcie `running` zmienia się w `failed`. Etapy `complete` są pomijane.
- `import_*` czyści tabele etapu i wszystkich późniejszych (w odwrotnej kolejności FK) i importuje od nowa.
- `links`: `DROP TABLE IF EXISTS` i etap od nowa.
- `constructions` i `decisions` jadą dalej.
- `write_lists` zapisuje atomowo.
- Plan awaryjny: jeśli test z ADR-008 pokaże różnicę po odbudowie importu, `--resume` z etapu importu zaczyna w nowym pliku bazy od `preflight`.

### Consequences

#### Good
- Restart, kill i zniknięcie dysku kosztują bieżący etap (≤2,4 h import, ~25 min pozostałe znane).
- Bez zmian w FK, `logical_content_report` i pieczęci.
- `resume_reports.py` staje się zbędny jako osobna logika.

#### Bad
- Przerwa w środku etapu kosztuje cały etap.
- Po `DELETE` plik bazy ma inne bajty niż świeży (`database_sha256` się różni). K8 porównuje treść, więc to akceptowalne.
- Nowa ścieżka kodu w `build.py`. Jednorazowo zmienia się tożsamość kodu (K8).

---

<a id="adr-004"></a>
## ADR-004: Znaczniki per raport, `unresolved` z pliku

### Status
Accepted

### Context
`reports` to ~65% czasu buildu (8–8,5 h). Sam `unresolved` trwa 4,1 h. Jego wynik przechodzi w pamięci do `filter_impact`, `quality_*` i `coverage`. `canonical_index` ma jawną listę plików, więc nowe pliki w `reports/.done/` do niego nie wchodzą.

### Decision Drivers
- Największy zysk za godzinę pracy.
- Raport wczytany z pliku musi dać ten sam wynik co raport z pamięci.

### Considered Options
1. Bez znaczników (całe `reports` od nowa).
2. Znacznik per raport z hashem.
3. Cięcie `unresolved` na części (2C).

### Decision Outcome
Wybrana opcja 2, bo najgorsza strata w `reports` spada z 8,5 h do 4,1 h.
- Po atomowym zapisie raportu powstaje `reports/.done/<raport>.json` z polami `sha256`, `bytes`, `tree_sha256` i `manifest_sha256`.
- Przy wznowieniu raport ze zgodnym znacznikiem jest pomijany. Brak znacznika albo niezgodny hash oznacza, że raport liczy się od nowa.
- `unresolved` wczytuje się z `reports/unresolved.json` (`load_json`). Test sprawdza, że raporty zależne dają te same bajty.
- Świeży build też pisze znaczniki, więc A i B mają ten sam układ plików.

### Consequences

#### Good
- Restart po `unresolved` oszczędza ~4 h albo więcej.
- Wzorzec znany z Make i DVC, prosty do sprawdzenia.

#### Bad
- Druga ścieżka danych dla `unresolved` (plik zamiast pamięci). Ryzyko różnic typów i kolejności łapie test.
- Wczytanie dużego JSON zwiększa szczyt pamięci przy wznowieniu.

---

<a id="adr-005"></a>
## ADR-005: Kontrakt kodów wyjścia 75–78

### Status
Accepted

### Context
Dziś każdy `OSError` i `sqlite3.Error` w buildzie kończy się kodem 4, tak jak błąd danych. Nadzorca musi odróżnić „dysk zniknął, warto czekać” od „błąd, ponawianie nic nie da”. Obecne kody to 0, 2, 3, 4, 5 i 130.

### Decision Drivers
- Jednoznaczny sygnał do ponowienia.
- Bez kolizji z obecnymi kodami i sensem `sysexits`.

### Considered Options
1. Jeden kod błędu i parsowanie stderr w nadzorcy.
2. Nowe kody: 75 utrata dysku, 76 zły wolumen, 77 `quick_check`, 78 brak miejsca.

### Decision Outcome
Wybrana opcja 2, bo kod wyjścia to stabilny kontrakt, a tekst błędu nie.
- Po błędzie I/O klasyfikator robi `ROLLBACK` (porażka pomijana) i zamyka połączenie. Potem sprawdza strażnika ponownie. Strażnik nie przechodzi: kod 75. Przechodzi: kod 4.
- Próba zapisu `failed` może się nie udać i jest wtedy pomijana. `--resume` i tak zamieni `running` w `failed`.
- Kody i ich znaczenie trafiają do `docs/generator/cli.md`.

### Consequences

#### Good
- Nadzorca ma prostą tabelę decyzji.
- Operator od razu widzi przyczynę.

#### Bad
- Błąd I/O z innego powodu w chwili zniknięcia dysku zostanie uznany za utratę dysku. Limit prób (ADR-006) ogranicza skutek.

---

<a id="adr-006"></a>
## ADR-006: Nadzorca wznawia tylko po kodzie 75

### Status
Accepted

### Context
Jedyne znane zniknięcie było o 02:32. Bez nadzorcy strata obejmuje czas do chwili, gdy ktoś to zauważy. Nowy proces ma świeże deskryptory, a SQLite przy otwarciu cofa hot journal. Nadzorca nie może dotykać `-journal`.

### Decision Drivers
- Bez nocnej straty.
- Bez nieskończonego ponawiania błędu kodu.
- Bez uśpienia maszyny w trakcie buildu.

### Considered Options
1. 3A: tylko ręczne `build --resume`.
2. 3B: nadzorca na 3A.
3. Pętla w `build_pair.sh` w sh.

### Decision Outcome
Wybrana opcja 2, w postaci `scripts/build_supervised.py`, bo w Pythonie łatwo przetestować tabelę kodów i ponownie użyć strażnika.
- Jeden nadzorca na stronę. `build_pair.sh` uruchamia dwa pod `caffeinate -dimsu`.
- Po kodzie 75 nadzorca co 5 s sprawdza G1+G2, najdłużej 30 min. Potem uruchamia `build --resume`.
- Limit 3 wznowień. G1 bez G2 kończy się od razu kodem 76.
- Wszystkie inne kody kończą pracę bez ponowienia. Log nadzorcy trafia do `logs/`.
- Ręczne `--resume` (3A) zostaje jako tryb bazowy.

### Consequences

#### Good
- Strata to bieżący etap lub raport, bez reakcji człowieka.
- Nadzorca nie zmienia plików przebiegu.

#### Bad
- Kolejny ruchomy element do utrzymania.
- Przy częstych zniknięciach limit 3 prób może się wyczerpać. Wtedy kod 75 i decyzja człowieka.

---

<a id="adr-007"></a>
## ADR-007: `fullfsync` według pomiaru, `F_FULLFSYNC` w plikach, `quick_check` po wznowieniu

### Status
Accepted (wybór 4B/4C zapada po pomiarze z kroku 2)

### Context
Na macOS `fsync` nie opróżnia cache dysku. `PRAGMA fullfsync` jest domyślnie wyłączone, a `write_json` robi tylko `fsync` pliku, bez fsync katalogu. Bez pełnego flushu manifest może zapisać `complete`, zanim dane etapu będą na nośniku, a `--resume` pominie wtedy etap z utraconymi danymi. Koszt `fullfsync` przy commitach co 10 000 wierszy na T7 nie jest znany.

### Decision Drivers
- Manifest nie może wyprzedzać danych.
- Koszt czasu ≤ ~5% buildu.
- Najpierw pomiar, bez pełnego buildu.

### Considered Options
1. 4A: bez zmian.
2. 4B: `fullfsync=ON` przez cały build.
3. 4C: `fullfsync` tylko na granicach etapów.
4. WAL albo `synchronous<FULL`.

### Decision Outcome
Skrypt `scripts/measure_fullfsync.py` mierzy na T7 commity porcji z `fullfsync` OFF i ON oraz `write_json` z `F_FULLFSYNC`. Opcjonalnie mierzy też `quick_check` istniejącej bazy w trybie `ro`.
- Jeśli narzut przeliczony na liczbę commitów buildu wynosi ≤5%, wybieramy 4B. W przeciwnym razie 4C.
- Zawsze: `F_FULLFSYNC` i fsync katalogu w `write_json` i nowym `write_bytes`. `PRAGMA quick_check` po każdym `--resume`, a wynik inny niż `ok` daje kod 77.
- Nigdy WAL, `journal_mode=OFF/MEMORY` ani `synchronous<FULL`.

### Consequences

#### Good
- Kolejność „dane, potem manifest” jest zachowana, o ile mostek USB przekazuje flush.
- Decyzja oparta na liczbach.

#### Bad
- 4C nie chroni wspólnych stron B-drzewa przed przestawieniem zapisów w środku etapu.
- Brak gwarancji, że T7 honoruje flush. Ostatnią linią obrony są `quick_check` i `integrity_check` w `verify`.
- Czas `quick_check` dla 21 GB może dodać minuty do każdego wznowienia.

---

<a id="adr-008"></a>
## ADR-008: Historia prób w manifeście pod pieczęcią, poza K8; test „wznowiony = świeży”

### Status
Accepted

### Context
Zniknięcie dysku przerywa A i B naraz, w tym samym etapie. Para nie złapie wtedy błędu wznowienia wspólnego dla obu stron. Dziś wznowienie widać tylko w work-logu. `manifest_core_sha256` obejmuje cały manifest poza `readiness`, `verification` i `export`, więc obejmuje też `stages`. K8 porównuje `tree_sha256`, `canonical-index` i `logical_content`, a nie manifest.

### Decision Drivers
- Dowód, że wznowienie nie zmienia wyniku.
- Pełna przejrzystość bez zmiany kontraktu K.
- Historii nie da się zmienić po `verify` bez śladu.

### Considered Options
1. 5A: tylko test.
2. 5B: test i historia w manifeście.
3. 5C: reguła w `verify` wymagająca świeżego partnera.
4. Historia poza rdzeniem pieczęci (nowe pole w `SEAL_EXCLUDED`).

### Decision Outcome
Wybrana opcja 5B, bo daje dowód i przejrzystość bez wymuszania przebudowy.
- Hermetyczny test przerywa build na każdej granicy etapu, w środku `import_kwjp`, `constructions` i `links` oraz między raportami. Potem wznawia i porównuje `logical_content_report`, `canonical-index` i `lists/*.txt` ze świeżym buildem.
- Manifest dostaje `stages.<etap>.attempts[]` (start, koniec, `outcome`, klasa przyczyny) i `resume: {resumed, count}`.
- Pola leżą **w** rdzeniu pieczęci: `SEAL_EXCLUDED` się nie zmienia, więc `verify` liczy `manifest_core_sha256` z historią, a `export` odmówi po każdej zmianie. Do `logical_content` i `canonical-index` historia nie wchodzi, więc K8 jej nie porównuje.
- `verify` wypisuje historię. `export` przenosi do `release-manifest.json` skrót `build_history`: etapy, liczba prób i klasy przyczyn, bez komunikatów i ścieżek.

Odchylenie od brzmienia 5B („poza zapieczętowanym rdzeniem”): wyłączenie historii z pieczęci pozwoliłoby ją zmienić po `verify`. Rdzeń pieczęci nie jest porównywany między A i B, więc objęcie go historią nie psuje pary.

### Consequences

#### Good
- Wznowienie jest widoczne w `verify` i w wydaniu, a historia zamrożona razem z pieczęcią.
- K1–K10 bez zmian.

#### Bad
- Mały zestaw testowy nie pokaże efektów skali.
- Dopóki test nie przechodzi, wznowiona para nie powinna iść do wydania.
