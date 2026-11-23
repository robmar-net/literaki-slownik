# Warianty rozwiązania: build na T7 i wznawianie po zniknięciu dysku

## TL;DR
Właściciel chce buildu na T7, więc zniknięcia dysku nie da się uniknąć. Trzeba je przeżyć.
Rekomendacja: symlink `data/work` na T7 i strażnik montowania w kodzie (`ismount`, znacznik na wolumenie, `st_dev`). Do tego `build --resume` per etap ze znacznikami per raport oraz nadzorca, który czeka na powrót dysku i sam wznawia build.
Na trwałość: `fullfsync=ON` (najpierw zmierzyć koszt) i `quick_check` po każdym wznowieniu. Powtarzalność pilnuje test „wznowiony = świeży” i historia wznowień w manifeście.
Odrzucone: praca lokalna z przenoszeniem etapu (to build na dysku wewnętrznym pod inną nazwą), ATTACH oraz migawki po etapach (na razie).

## Key Decisions
- **Lokalizacja: symlink `data/work` → `/Volumes/Data/literaki-slownik/work` (1A).** Kod, piny i runbooki zostają bez zmian. Trzeba poprawić `.gitignore` (`/data/work` bez ukośnika).
- **Strażnik: trzy warstwy (G1+G2+G3) w kodzie buildu, nie tylko w skrypcie.** UUID trzymamy tylko na wolumenie, nigdy w repo.
- **Granulacja: etap w tej samej bazie + znacznik per raport (2B).** Dalsze cięcie etapów (2C) odkładamy, dopóki nie wiadomo, jak często dysk znika.
- **Odzyskiwanie: nadzorca z automatycznym `--resume` (3B) na bazie ręcznego `--resume` (3A).** Jedyne znane zniknięcie było o 02:32, w nocy. Bez nadzorcy tracimy czas do chwili, gdy ktoś to zauważy.
- **Trwałość: `fullfsync=ON` przez cały build (4B), jeśli pomiar da ≤ ~5% czasu. Inaczej tylko na granicach etapów (4C).** Zawsze `quick_check` po wznowieniu.
- **Powtarzalność: test przerwania i wznowienia na małym zestawie plus historia wznowień w manifeście (5A+5B).** `verify` traktuje wznowiony przebieg jak każdy inny.

## Open Questions / Risks
- **Koszt `fullfsync` na T7 nie jest zmierzony.** Od niego zależy wybór między 4B a 4C.
- **Częstość zniknięć znamy z jednego zdarzenia w 7 dniach.** Przy 13 h buildu to ~7% szans na przerwę w przebiegu (niska pewność). Jeśli przerwy będą częstsze, wraca 2C.
- **Zniknięcie dysku przerywa obie strony A/B naraz, w tym samym etapie.** Para przestaje wtedy łapać błąd wznowienia, który dotyczy obu stron jednakowo. Test 5A musi to pokryć.
- **Mostek USB może przestawiać zapisy.** Wtedy hot journal nie uratuje bazy, a `quick_check` lub `integrity_check` w `verify` wykryje szkodę dopiero po fakcie. Kosztem jest wtedy cały build (rzadko).
- **Po obcięciu tabel importu plik bazy ma inne bajty niż przy świeżym buildzie** (wolne strony). `database_sha256` się różni, ale K8 porównuje `logical_content`, a nie bajty. Trzeba to potwierdzić w 5A.

## Problem Reframing

### Research Question
Jak trzymać duże pliki buildu (`build.sqlite` ~22 GB na przebieg, para A/B ~44 GB, ~13 h) na T7, który czasem znika na kilka sekund, tak żeby zniknięcie nie oznaczało budowy od zera, przy zachowaniu K1–K10 i pary A/B.

### How Might We
1. HMW tak podpiąć T7, żeby kod, piny i runbooki działały bez zmian, a brak dysku dawał jasny błąd zamiast cichego zapisu na dysk wewnętrzny?
2. HMW ograniczyć stratę po przerwie do małej części buildu?
3. HMW wrócić do pracy po zniknięciu dysku bez czekania na człowieka?
4. HMW nie dopuścić, by baza po wznowieniu była cicho uszkodzona?
5. HMW udowodnić, że wznowiony przebieg daje ten sam wynik co świeży?

Fakty z badania, na których stoją warianty (dalej jako F#):
- F1: jedna baza, `journal_mode=delete`, `synchronous=FULL`, bez `fullfsync`.
- F2: `create_run` odmawia istniejącego katalogu, a status po awarii zostaje `running`.
- F3: `reports` zajmuje 8,5 h, z czego `unresolved` 4,1 h; `import_kwjp` 2,4 h.
- F4: idempotentne są `constructions` i `decisions`; nie są `import_*` i `links`.
- F5/F6: kod bierze `--run-dir`, a K1–K10 porównują hashe, nie ścieżki.
- F7: `.gitignore` z ukośnikiem nie łapie symlinku.
- F8: otwarte deskryptory po zniknięciu dysku są martwe; hot journal cofa przerwaną transakcję.
- F9: `fsync` na macOS nie opróżnia cache dysku.
- F10: `/Volumes` należy do roota.
- F11: jedno zniknięcie w 7 dniach.
- F12: ATTACH łamie kontrakty.

## Explored Alternatives

### Obszar 1: gdzie leży korzeń roboczy i jak go podpiąć

**1A. Symlink `data/work` → `/Volumes/Data/literaki-slownik/work`**
- Opis: jeden symlink w repo.
  - `build_pair.sh`, piny `../../data/work/...` w 4 konfiguracjach i ~20 miejsc w runbookach działają bez zmian.
  - Logi `.out.json`/`.err` przenosimy do `logs/` w repo, na dysku wewnętrznym, żeby nie ginęły razem z T7.
- Za:
  - zero zmian w ścieżkach;
  - `connect()` rozwiązuje ścieżkę (`database.py:10`), więc journal leży zawsze w katalogu docelowym;
  - K1–K10 bez zmian (F5, F6).
- Przeciw:
  - bez poprawki `.gitignore` symlink trafi do publicznego repo (F7);
  - wiszący symlink daje mylący błąd „katalog już istnieje” (R3), dopóki strażnik go nie przechwyci;
  - wszystkie przebiegi idą na T7, także małe.
- Najlepszy, gdy: cały `data/work` ma być na T7. Tego chce właściciel.

**1B. Korzeń z env/flagi (`LITERAKI_WORK_ROOT`)**
- Opis: `build_pair.sh` i CLI składają `--run-dir` z `LITERAKI_WORK_ROOT`. Bez zmiennej zostaje `data/work`.
- Za:
  - jawnie widać, gdzie idzie build;
  - nie ma symlinku do pilnowania w git.
- Przeciw:
  - piny w 4 konfiguracjach nie podążą za zmienną, a ich zmiana daje nowy `manifest_sha256` (F5);
  - trzeba przepisać ~20 miejsc w dokumentacji;
  - pusty punkt montowania grozi cichym zapisem na dysk wewnętrzny (R2).
- Najlepszy, gdy: korzeń ma się często zmieniać. Tu się nie zmienia.

**1C. Symlink per przebieg (`data/work/<przebieg>` → T7)**
- Opis: `data/work` zostaje katalogiem na dysku wewnętrznym. `build_pair.sh` tworzy katalog przebiegu na T7 i kładzie w `data/work` symlink do niego.
- Za:
  - małe przebiegi (import, pop) mogą zostać wewnątrz;
  - `.gitignore` już łapie zawartość `data/work/`.
- Przeciw:
  - `canonical_index` odrzuca symlinki plików, a katalogu przebiegu nie (sprawdzić);
  - więcej ruchomych części, a skrypt musi tworzyć dwie rzeczy;
  - każdy przebieg ma swój punkt awarii przy wiszącym symlinku.
- Najlepszy, gdy: tylko część przebiegów ma iść na T7.

**Strażnik montowania (we wszystkich wariantach, warstwy się sumują)**
- **G1 `os.path.ismount` punktu montowania** po rozwiązaniu ścieżki przebiegu.
  - Za: tani, łapie pusty katalog-sobowtór.
  - Przeciw: nie odróżni innego wolumenu zamontowanego jako `Data`.
- **G2 znacznik `.literaki-work-volume` w korzeniu roboczym na T7.**
  - Plik zawiera losowy identyfikator albo `VolumeUUID` z `diskutil`, zapisany raz.
  - Build kopiuje go do manifestu przebiegu, w części poza pieczęcią, i porównuje.
  - Za: łapie `Data 1`, podmianę dysku i resztki katalogów.
  - Przeciw: jeden plik więcej do utrzymania. UUID nie może trafić do repo, które jest publiczne.
- **G3 `st_dev` katalogu przebiegu zapamiętane na starcie.**
  - Porównywane przed każdym etapem, przed każdym `os.replace` i przed otwarciem bazy przy `--resume`.
  - Za: łapie zmianę urządzenia w trakcie.
  - Przeciw: `st_dev` zmienia się po ponownym montowaniu. Przy `--resume` porównujemy więc G2, a nie G3.
- Zawsze:
  - nigdy `mkdir -p` od `/Volumes`; `create_run` tworzy tylko ostatni poziom;
  - przed startem sprawdzamy wolne miejsce (≥ 2×22 GB na stronę);
  - nie uruchamiamy buildu przez `sudo` (F10).

### Obszar 2: granulacja wznawiania

**2A. Etap w tej samej bazie (`build --resume`)**
- Opis:
  - `--resume` przyjmuje istniejący katalog z tym samym `tree_sha256` i `manifest_sha256`;
  - przy starcie zmienia `running` na `failed`;
  - pomija etapy `complete`;
  - `import_*` obcina tabele etapu i powtarza;
  - `links` robi `DROP … IF EXISTS`;
  - `constructions` i `decisions` jadą dalej przez `insert or ignore` (F4);
  - `reports` powtarza wszystkie raporty;
  - czasy etapów zapisuje w manifeście;
  - `write_lists` zapisuje atomowo.
- Za:
  - połowa pracy jest już idempotentna;
  - wzór daje `resume_reports.py`;
  - chroni też przed restartem i kill.
- Przeciw: przerwa w `reports` kosztuje do 8,5 h.
- Najlepszy, gdy: przerwy są rzadkie i trafiają w etapy przed `reports`.

**2B. 2A + znacznik per raport**
- Opis:
  - każdy raport po zapisie (atomowym) dostaje `reports/.done/<raport>.json` z sha256 wyniku i tożsamością kodu;
  - `unresolved`, którego wynik idzie w pamięci do 4 następnych raportów, jest wczytywany z `unresolved.json`;
  - raport bez znacznika albo z niezgodnym hashem liczy się od nowa.
- Za:
  - `reports` to 65% czasu (F3);
  - najgorsza strata w tym etapie spada z 8,5 h do 4,1 h;
  - wzorzec znacznika „done” z hashem jest sprawdzony (Make, DVC).
- Przeciw:
  - trzeba zadbać, by wynik wczytany z pliku był identyczny jak wynik w pamięci (kolejność, typy);
  - to dodatkowa ścieżka kodu.
- Najlepszy, gdy: zawsze. Daje największy zysk za godzinę pracy.

**2C. 2B + cięcie długich etapów od środka**
- Opis:
  - `import_kwjp`: wznowienie od ostatniego zatwierdzonego `row_number` per źródło, bo jest UNIQUE `source_id,row_number`, a commity idą co 10k;
  - `unresolved`: obliczenie w częściach z plikami częściowymi i znacznikami;
  - `decisions`: zapisywanie postępu porcji.
- Za: najgorsza strata spada do minut.
- Przeciw:
  - `unresolved` trzeba rozbić na części, które dają ten sam wynik po złożeniu; to najryzykowniejsza zmiana dla `logical_content`;
  - przy ~7% szans na przerwę zysk oczekiwany to ~0,1–0,2 h na build (szacunek, niska pewność);
  - normalny czas `decisions` jest nieznany.
- Najlepszy, gdy: dysk znika często albo `decisions` okaże się długi.

### Obszar 3: odzyskiwanie po zniknięciu dysku

**3A. Fail fast + ręczne `build --resume`**
- Opis:
  - przy `SQLITE_IOERR` albo `OSError`: `ROLLBACK`, zamknięcie połączenia, wyjście z jasnym kodem i komunikatem;
  - status `failed` jest zapisywany, jeśli się da, a ślad trafia do logu wewnątrz;
  - wznawia operator albo sesja.
- Za:
  - najprostsze;
  - nic nie dzieje się bez człowieka.
- Przeciw: strata obejmuje też czas do zauważenia, a jedyne znane zniknięcie było o 02:32.
- Najlepszy, gdy: build jest pilnowany na żywo.

**3B. Nadzorca: czeka na dysk i sam wznawia**
- Opis: pętla w `build_pair.sh` albo w małym `scripts/build_supervised.py`.
  - Po wyjściu z kodem „utrata dysku” czeka, aż strażnik G1+G2 przejdzie (sprawdzanie co kilka sekund, limit np. 30 min).
  - Potem uruchamia `build --resume` jako nowy proces, więc deskryptory są świeże, a hot journal zostaje cofnięty przy otwarciu.
  - Ma limit prób (np. 3) i loguje do pliku wewnątrz.
  - Inne kody wyjścia (błąd danych, błąd kodu) kończą pracę bez ponawiania.
  - Całość chodzi pod `caffeinate -dimsu`.
- Za:
  - strata = bieżący etap albo raport, bez czasu na reakcję człowieka;
  - nadzorca nie dotyka plików, więc nie łamie zasady „nie ruszać journala” (F8).
- Przeciw:
  - trzeba rozróżnić kody wyjścia, bo ponawianie błędu kodu w kółko nic nie da;
  - przy uszkodzeniu bazy nadzorca musi przestać (wynik `quick_check`, zob. 4).
- Najlepszy, gdy: build chodzi w nocy bez nadzoru. Tak jest tutaj.

**3C. Migawka po długim etapie (backup API)**
- Opis:
  - po `import_kwjp` i `decisions` backup API kopiuje bazę do `checkpoint.sqlite.tmp`, potem `F_FULLFSYNC`, `os.replace` i znacznik z sha256;
  - przy uszkodzeniu bazy wznawiamy z migawki.
  - Wariant: migawka na dysku wewnętrznym (inne urządzenie), usuwana po udanym buildzie.
- Za:
  - chroni przed uszkodzeniem, nie tylko przed przerwą;
  - backup API kopiuje strony 1:1 (F9, lang_vacuum).
- Przeciw:
  - +22 GB na stronę;
  - czas kopii 21 GB na T7 jest niezmierzony (przy błędzie firmware: minuty albo dłużej);
  - migawka wewnątrz zajmuje 44 GB z 193 GB i stoi w napięciu z decyzją właściciela.
- Najlepszy, gdy: `quick_check` po wznowieniu zacznie wykazywać uszkodzenia.

**3D. Etap lokalnie, gotowa baza na T7**
- Opis: każdy etap pracuje na kopii bazy na dysku wewnętrznym, a po etapie kopia wraca na T7.
- Za: zniknięcie T7 w trakcie etapu nie dotyka pracy.
- Przeciw:
  - baza jest jedna i rośnie do 22 GB, więc każdy etap kopiuje ją dwa razy (tam i z powrotem);
  - w praktyce to build wewnątrz, czyli wariant, który właściciel odrzucił;
  - kopia z powrotem i tak może paść.
- Najlepszy, gdy: nigdy w tym projekcie. Opisany, żeby zamknąć temat.

### Obszar 4: trwałość na USB

**4A. Bez zmian (`synchronous=FULL`, `fullfsync=off`)**
- Za: zero kosztu i zero zmian.
- Przeciw:
  - `fsync` nie opróżnia cache dysku (F9);
  - manifest może zapisać `complete`, zanim strony bazy będą na nośniku, a wtedy `--resume` pominie etap z utraconymi danymi.

**4B. `PRAGMA fullfsync=ON` przez cały build, `F_FULLFSYNC` i fsync katalogu w `write_json`**
- Za:
  - najlepsza ochrona kolejności zapisów, o ile mostek T7 przekazuje flush;
  - chroni też strony wcześniejszych etapów przed przestawieniem zapisów w bieżącym.
- Przeciw:
  - każdy commit (co 10k wierszy) opróżnia cache dysku, a kosztu nie zmierzyliśmy;
  - nie ma gwarancji, że USB to honoruje.
- `checkpoint_fullfsync` nic nie daje, bo nie ma WAL. Przy `fullfsync=ON` i tak nie ma znaczenia.

**4C. `fullfsync` tylko na granicach etapów**
- Opis: w trakcie etapu `fullfsync=off`. Przed końcowym commitem etapu `fullfsync=ON`, potem manifest z `F_FULLFSYNC` i fsync katalogu.
- Za:
  - prawie zerowy koszt;
  - zachowuje kolejność „dane etapu trwałe, zanim manifest powie `complete`”.
- Przeciw: przestawione zapisy w środku etapu mogą uszkodzić wspólne strony B-drzewa z wcześniejszych etapów. Hot journal tego nie naprawi.

**Wspólne dla 4A–4C:**
- `PRAGMA quick_check` po każdym `--resume`, przed pierwszym etapem; czas na 21 GB jest niezmierzony;
- przy błędzie nadzorca przestaje, a człowiek decyduje (build od zera);
- `verify` i tak robi `integrity_check`;
- nigdy WAL, `journal_mode=OFF/MEMORY` ani `synchronous<FULL`.

### Obszar 5: strażnik powtarzalności

**5A. Test „wznowiony = świeży” na małym zestawie**
- Opis: hermetyczny test (`tmp_path`, mały zestaw wejść).
  - Przerywa build wstrzykniętym wyjątkiem I/O i zabiciem procesu:
    - na każdej granicy etapu;
    - w środku `import_kwjp`, `constructions`, `links`;
    - między raportami.
  - Potem wznawia i porównuje z jednym świeżym buildem `logical_content_report`, `canonical-index` (lists, reports) oraz `lists/*.txt`.
  - Uruchamiany lokalnie albo na runnerze self-hosted.
- Za:
  - dowodzi dokładnie tego, czego para A/B nie złapie, gdy obie strony wznowiono tak samo;
  - jest tani w czasie.
- Przeciw: mały zestaw nie pokaże efektów skali (np. kolejności przy dużych porcjach).

**5B. 5A + historia wznowień w manifeście**
- Opis:
  - `stages.<etap>.attempts[]` (początek, koniec, powód przerwania) i `resumed: true`;
  - historia leży w części manifestu poza `logical_content`, tak jak czasy;
  - `verify` liczy K1–K10 normalnie i tylko wypisuje historię;
  - `export` przenosi ją do metadanych wydania.
- Za:
  - pełna przejrzystość bez zmiany kontraktu K;
  - zastępuje dzisiejsze ad hoc „dokończony po restarcie” w work-logu.
- Przeciw: trzeba sprawdzić, że nowe pola nie wchodzą do `manifest_core_sha256` w sposób, który zmienia pieczęć między A i B. Czasy też się różnią, więc pewnie są już wyłączone; do sprawdzenia.

**5C. 5B + reguła w `verify`: wznowiony przebieg wymaga świeżego partnera**
- Opis: K8 przechodzi tylko wtedy, gdy co najmniej jedna strona A/B była budowana bez wznowienia albo strony wznowiono w różnych etapach.
- Za: twarda gwarancja na danych w pełnej skali.
- Przeciw:
  - zniknięcie dysku przerywa obie strony naraz, więc reguła wymusza 13 h przebudowy, a tego właśnie chcemy uniknąć;
  - to zmiana kontraktu `verify` i wymaga ADR.

## Trade-Off Analysis

Skala: W = wysoka (dobrze), Ś = średnia, N = niska (źle). Przy „Ryzyku” W oznacza niskie ryzyko.

| Wariant | Wykonalność | Wpływ na operatora | Prostota | Ryzyko | Skalowalność |
|---|---|---|---|---|---|
| 1A symlink `data/work` | W | W (nic się nie zmienia) | W | Ś (`.gitignore`, R3 do strażnika) | Ś (wszystko na T7) |
| 1B env/flaga | Ś | N (piny, ~20 miejsc w docs) | Ś | N (R2, nowy `manifest_sha256`) | W |
| 1C symlink per przebieg | Ś | Ś | N | Ś | W |
| G1+G2+G3 strażnik | W | W (jasny błąd) | Ś | W | W |
| 2A etap w bazie | W | Ś | Ś | Ś (identyczność wyniku) | Ś |
| **2B + znaczniki raportów** | W | W (strata ≤4,1 h) | Ś | Ś | W |
| 2C cięcie od środka | N | W | N | N (`unresolved`) | W |
| 3A ręczne `--resume` | W | N (czas do zauważenia) | W | W | Ś |
| **3B nadzorca** | W | W (bez nocnej straty) | Ś | Ś (kody wyjścia) | W |
| 3C migawka | Ś | Ś | Ś | W (chroni przed korupcją) | N (+22 GB/stronę) |
| 3D lokalnie + przenieś | N | N (kopie 2×22 GB) | N | Ś | N |
| 4A bez zmian | W | W | W | N (kolejność manifest/baza) | W |
| **4B `fullfsync` cały build** | W | Ś (koszt nieznany) | W | W (o ile mostek honoruje) | Ś |
| 4C `fullfsync` na granicach | W | W | Ś | Ś | W |
| 5A test | W | W | W | Ś (mała skala) | W |
| **5B + historia** | W | W | Ś | W | W |
| 5C reguła w `verify` | Ś | N (wymusza przebudowę) | N | W | N |

Kluczowe napięcia:
- prostota 3A przeciw nocnym przerwom (3B);
- ochrona 3C przeciw miejscu i czasowi;
- pewność 4B przeciw niezmierzonemu kosztowi;
- twardość 5C przeciw celowi, którym jest brak przebudowy.

## User Preferences
- Właściciel na bramce: **„Chcę build na T7”**. Duże pliki (`build.sqlite`, para A/B) mają leżeć na T7, a praca ma przetrwać zniknięcie dysku bez zaczynania od zera. To wyklucza L3 i (d) z raportu oraz 3D.
- Najpierw porównanie wariantów, potem projekt.
- Ograniczenia stałe:
  - bez zmian polityki słownika;
  - bez CI na runnerach GitHuba;
  - repo jest publiczne, więc UUID i prywatne ścieżki nie trafiają do kodu ani konfiguracji.

## Recommended Approach

**1A + G1/G2/G3 → 2B → 3B (na 3A) → 4B lub 4C po pomiarze + `quick_check` → 5A+5B.**

Uzasadnienie:
- Symlink nie zmienia ani jednej ścieżki w kodzie, pinach i runbookach.
- Strażnik zamienia każdy przypadek „brak dysku” w jasny błąd z kodem wyjścia, który rozpoznaje nadzorca.
- Wznawianie per etap ze znacznikami raportów ogranicza stratę do bieżącego etapu albo raportu: ≤2,4 h w imporcie, ≤4,1 h w `unresolved`, zwykle mniej.
- Nadzorca usuwa czas oczekiwania na człowieka, który w nocy byłby największą stratą.
- Test i historia wznowień pilnują, że wznowienie nie zmienia wyniku.

Kolejność kroków (do projektu):
1. `.gitignore` (`/data/work`, `/cache` bez ukośnika), symlink, logi do `logs/` wewnątrz, znacznik na T7.
2. Strażnik G1–G3 w `run.py`/`build.py` i w `build_pair.sh`, sprawdzenie miejsca.
3. `build --resume` (2A) z kodem wyjścia „utrata dysku” i obsługą `ROLLBACK`/zamknięcia.
4. Znaczniki per raport (2B), `unresolved` z pliku, `resume_reports.py` w trybie `ro` albo zastąpiony przez `--resume`.
5. Pomiar `fullfsync` na T7 (krótki benchmark commitów co 10k wierszy), potem 4B albo 4C; `F_FULLFSYNC` i fsync katalogu w `write_json`; `quick_check` po wznowieniu.
6. Nadzorca (3B) pod `caffeinate -dimsu`.
7. Test 5A i historia 5B; dopiero potem pierwsza para A/B na T7.

Zaakceptowane koszty:
- przerwa w środku etapu kosztuje cały etap;
- nie mamy migawki na wypadek uszkodzenia, więc kosztem jest wtedy build od zera;
- jedna nowa tożsamość kodu (K8), zmieniona raz.

Założenia (jeśli są fałszywe, rekomendacja się zmienia):
- Zniknięcia są rzadkie (~1 na tydzień). Jeśli są częstsze, wraca 2C dla `import_kwjp` i `unresolved`.
- Hot journal zwykle cofa transakcję na T7. Jeśli `quick_check` pokaże uszkodzenia, wraca 3C.
- Koszt `fullfsync` jest akceptowalny albo wystarcza 4C.
- Obcięcie tabel importu daje ten sam `logical_content`. Jeśli 5A pokaże różnicę, import trzeba wznawiać przez `insert or ignore` albo usuwać plik bazy i zaczynać od `preflight` (strata ~2,7 h).

Pewność: **średnia–wysoka** co do kształtu, **średnia** co do zachowania T7 (fsync, kolejność zapisów).

## Why Not Others
- **1B env/flaga:** nie daje nic ponad symlink, a psuje piny, `manifest_sha256` i ~20 miejsc w dokumentacji.
- **1C symlink per przebieg:** więcej ruchomych części bez potrzeby, bo właściciel chce cały build na T7.
- **2A bez znaczników raportów:** zostawia stratę 8,5 h w etapie, który zajmuje 65% czasu.
- **2C cięcie od środka:** wysokie ryzyko dla `logical_content` (`unresolved`) przy małym oczekiwanym zysku. Wraca, jeśli zniknięcia będą częste.
- **3A samo ręczne wznawianie:** w nocy strata rośnie o godziny oczekiwania. Zostaje jako tryb bazowy pod nadzorcą.
- **3C migawki:** +22 GB na stronę i niezmierzony czas kopii na T7 przeciw ryzyku, którego jeszcze nie zaobserwowano. `verify` i tak wykryje uszkodzenie.
- **3D lokalnie + przenieś:** to build na dysku wewnętrznym, który właściciel odrzucił, plus 2 kopie 22 GB na etap.
- **4A bez zmian:** dopuszcza `complete` w manifeście przed trwałymi danymi, a to wprost psuje wznawianie.
- **5C reguła w `verify`:** zniknięcie dysku przerywa obie strony naraz, więc reguła wymusza przebudowę, której chcemy uniknąć. Zmienia też kontrakt.
- **ATTACH per etap, WAL:** odrzucone w badaniu. ATTACH łamie FK, `logical_content_report` i `database_sha256`, a WAL odbiera ATTACH atomowość i niczego tu nie daje.

## Deferred Ideas
- **Przesunięcie stron A/B w czasie** (start B po zakończeniu importów A), żeby jedno zniknięcie nie trafiało obu stron w tym samym etapie. *Stretch:* wzmacnia parę jako strażnika, ale wydłuża build.
- **Usunięcie przyczyny zniknięć T7:** firmware FXI72P2Q, kabel, port, zasilanie, Spotlight wyłączony dla wolumenu, Time Machine poza oknem buildu. *Poza zakresem kodu*, do decyzji operatora.
- **Migawka (3C) jako opcja `--checkpoint`,** gdy pojawi się pierwsze uszkodzenie. *Stretch.*
- **Piny POP/POP00/TEMATY na usunięty v31:** decyzja właściciela z raportu. *Poza zakresem.*
- **ATTACH / plik per etap:** tylko z osobnym ADR. *Poza zakresem.*
- **`diskutil verifyVolume` dla śladu `.DocumentRevisions-V100-bad-1`:** tylko na prośbę operatora. *Poza zakresem.*
