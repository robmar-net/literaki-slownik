# Audyt specyfikacji #22 (build na T7 z wznawianiem)

## TL;DR
Werdykt: **pass-with-concerns**. Spec da się wdrożyć, bez CI i bez USB w testach. Trzeba jednak poprawić 3 sprzeczności.
Liczby: Critical 0, High 3, Medium 8, Low 9.
High: (1) kolejność kontroli `--resume` daje 4 zamiast 75, gdy dysku brak; (2) `NOTICE` serwera nie zawiera sha256 `release-manifest.json`, więc reguła „bieżące na serwerze” nigdy nie trafia; (3) promocja nie opisuje, co się dzieje po przerwie ani przy zniknięciu T7 w trakcie.
Sprawdzone i zgodne z kodem: kolejność DELETE względem FK, pola `new_*` (są tylko w wartościach funkcji, testy ich nie czytają z raportów), pieczęć obejmuje nowe pola, `.done/` jest poza K8 i poza pakietem, build fikstury kończy wszystkie etapy.

## Key Decisions
- Brak Critical: każde kasowanie danych nieodtwarzalnych dalej wymaga listy od właściciela, a T7 kasuje się dopiero po sprawdzeniu kopii sha256. Błędy grożą złym kodem albo stanem, który trzeba poprawić ręcznie, ale nie utratą danych.
- Reguła `NOTICE` dostaje High, nie Medium: wydanie, które naprawdę jest na serwerze (`pop-v2`, tylko lab), zostałoby pokazane właścicielowi jako kandydat do skasowania.
- Ryzyko `rowid` (ADR-016) oceniam jako Low: `logical-content` porównuje trwałe klucze, a po DELETE wszystkich wierszy SQLite znowu numeruje od 1.

## Open Questions / Risks
- Czy limit 50 GB dotyczy każdej strony, czy całego wolumenu? A i B startują razem na jednym T7. Wymagania mówią „na stronę”, tabela strażnika tego nie mówi.
- Co z przebiegiem osieroconym na T7 (bez symlinku), który ma manifest `VERIFIED`? Klasa „osierocony” go kasuje, klasa „VERIFIED na T7” mówi „nigdy”.
- Po stałym katalogu w `/Volumes` macOS może zamontować dysk pod inną nazwą (`<nazwa> 1`). Symlink przebiegu wtedy wisi. Nadzorca czeka 30 min i kończy kodem 75.

## High

**H1. Kolejność kontroli `--resume` jest sprzeczna z kontraktem kodu 75**
- Spec R5: pierwsza kontrola to „manifest przebiegu istnieje (inaczej 4)”, strażnik jest dopiero trzeci. Tabela „Kody wyjścia” mówi: 75 = „brak dysku przy starcie `--resume`”.
- Manifest leży na T7. Gdy dysku brak, jest nieczytelny, więc wynik to 4. Nadzorca przy 4 się zatrzymuje. Zdarzy się to, gdy dysk zniknie między sprawdzeniem G1+G2 a startem procesu potomnego, albo przy ręcznym `--resume` po restarcie.
- Kategoria: Incorrect. Poprawka: najpierw sprawdzić `lexists` symlinku i istnienie jego celu oraz G1 (75), dopiero potem czytać manifest. `marker_id` (G2) sprawdzić po odczycie manifestu.

**H2. Reguła „bieżące na serwerze” opiera się na hashu, którego w `NOTICE` nie ma**
- Spec (Sprzątanie i Key Decisions) zakłada, że sha256 `release-manifest.json` występuje w `origin/main:NOTICE`.
- Sprawdziłem w repo serwera: `NOTICE` podaje sha256 plików list (`LL-PL-STANDARD.txt`, `LL-PL-BROAD.txt`, `POP.txt`, wersje `.gz`) i ścieżki `lexicons/*.dawg`. sha256 `release-manifest.json` dla v29, v30, v31, `pop-v3-…-a` i `pop00-v1-…-r2-a` nie występuje ani razu (0 trafień). Hash listy v29 występuje.
- Skutek: `NOTICE` jest czytelny, więc nie działa bezpieczne „wszystko potrzebne”, a żadne wydanie nie pasuje. Wysłane `pop-v2-…-a/b` nie jest przypięte i nie jest ostatnie w rodzinie, więc trafia na listę kandydatów.
- Kategoria: Incorrect. Poprawka: porównywać sha256 plików z `files` w `release-manifest.json` (listy `.txt` i `.txt.gz`) z hashami w `NOTICE`. Dodać fiksturę z prawdziwym kształtem `NOTICE`.

**H3. Promocja nie opisuje, jak dokończyć pracę po przerwie, ani co zrobić, gdy T7 zniknie**
- Spec (Promocja, krok 2–5, „Ponowne wywołanie…”) nie odpowiada na pytania:
  - Jaki kod zwrócić, gdy T7 zniknie w trakcie kopii? Opisany jest tylko kod 4 przy różnym sha256. Powinno być 75, a staging zostaje.
  - Co zrobić z częściowym stagingiem przy ponownym wywołaniu: kopiować od nowa czy sprawdzić hash każdego pliku?
  - Skąd wziąć ścieżkę kopii A na T7 w stanie „katalog wewnętrzny jest, T7 ma kopię”? Symlinku już nie ma, a manifest ma tylko `marker_id`. Potrzebny jest zapis ścieżki w `logs/<A>.promote.log` albo `--work-root`.
  - Krok 1 wymaga `VERIFIED`. Jeśli ktoś zrobi `export` przed dokończeniem promocji, ponowne wywołanie da 5 i zostawi kopię na T7.
- Krok 3 sprawdza `changes_since_verify` dopiero po podmianie. Jeśli to sprawdzenie nie przejdzie, `data/work/<A>` wskazuje już na kopię, której pieczęć się nie zgadza, a spec nie mówi, jak to cofnąć. `changes_since_verify` liczy wszystko względem `run` (`export.py:59-100`), więc można go uruchomić na stagingu przed podmianą.
- Kategoria: Incomplete. Poprawka: dopisać tabelę stanów (symlink / staging / katalog / kopia T7) z akcją i kodem dla każdego. Kontrolę pieczęci przenieść przed podmianę.

## Medium

- **M1. Podmiana symlinku nie jest atomowa.** Krok 3 to `unlink` symlinku, potem `rename`, więc przez chwilę `data/work/<A>` nie istnieje. `export.py:34-53` już woła `renamex_np` przez ctypes; flaga `RENAME_SWAP` zamienia katalog z symlinkiem jednym wywołaniem.
- **M2. Klasy sprzątania nie mają ustalonego pierwszeństwa.** Klasa „osierocony katalog → kasuje” obejmuje też katalog z manifestem `VERIFIED`/`FROZEN` oraz kopię A w oknie między `unlink` a `rename` z kroku 3 (nie ma wtedy symlinku). Klasa readiness powinna wygrywać, a katalog osierocony powinien mieć próg wieku. Obejmuje to też katalog świeżo utworzony przez `create_run`, który jeszcze nie ma symlinku.
- **M3. SQL resetu `links` jest błędny.** `DROP TABLE IF EXISTS evidence_candidate, evidence_link` to w SQLite błąd składni (sprawdzone). Przy `foreign_keys=ON` (`database.py:14`) usunięcie rodzica przed dzieckiem kończy się „FOREIGN KEY constraint failed” (też sprawdzone). Trzeba dwóch poleceń, najpierw `evidence_candidate`. W wierszach `import_*` DROP tabel links powinien stać przed DELETE (`evidence_candidate` odwołuje się do `lexeme`, `surface_form`, `derivation_candidate`; `evidence_link` do `corpus_evidence`, `links.py:133-144`). Dziś to bezpieczne tylko dlatego, że links nie mogą istnieć, gdy import jest niegotowy.
- **M4. Poprawka 4 zostawia `links` jako `running` przy kodzie 0.** Dziś `links` dostaje `complete` tylko przy `stage_completion.complete` (`build.py:183-184`), w przeciwnym razie nic. Po dodaniu `running` na starcie udany proces kończy z etapem `running`, a `outcome` i `verify` pokażą `running`, nie `pending`. Trzeba dopisać `set_stage(links, 'pending', reason)`.
- **M5. Nadzorca może wznowić przebieg, który jeszcze nie powstał.** „`R` nie istnieje” bez `lexists` traktuje wiszący symlink jak brak przebiegu. Gorzej: gdy pierwszy `build` dostanie 75 jeszcze przed `create_run` (T7 nieobecny na starcie), nadzorca robi potem `build --resume`. Nie ma manifestu, więc wynik to 4 i stop. Po 75 bez manifestu trzeba powtórzyć świeży build.
- **M6. Nie wiadomo, czy próg 50 GB jest na stronę.** A i B sprawdzają miejsce osobno, w tej samej chwili i na tym samym wolumenie (~22 GB każda plus journal).
- **M7. `--work-root` na dysku wewnętrznym bez znacznika przechodzi.** Wiersz „punkt montowania = repo, brak znacznika → przepuszcza” dotyczy też jawnego `--work-root`. Jeśli W istnieje na dysku systemowym (np. ręcznie utworzony katalog w `/Volumes`), build pójdzie na dysk systemowy wbrew R1. Przy jawnym `--work-root` znacznik powinien być wymagany; wyjątek bez znacznika tylko bez `--work-root`.
- **M8. Ponowne zamontowanie pod inną ścieżką.** Symlink wskazuje stałą ścieżkę. Strażnik mógłby znaleźć wolumen po `marker_id` i zgłosić to wprost, zamiast 30 min czekać i kończyć 75. SQLite tego nie potrzebuje: hot journal leży w tym samym katalogu co baza.

## Low

- L1. Niezgodny `inputs.manifest_sha256` przy `--resume` daje 4, a tabela kodów mówi: 3 = błąd wejść (hash). Ujednolicić.
- L2. `.gitignore` ma już `/data/work/`, a `data/work` zostaje katalogiem, więc symlinki w środku są ignorowane i bez zmiany. Test „`check-ignore` dla symlinku `data/work`” przeczy układowi z R1. `/logs` jest potrzebne.
- L3. `constructions.py:515-534` nie porównuje wierszy. Klucz to sha256 treści, więc `insert or ignore` i tak jest bezpieczny. Poprawić opis.
- L4. Ryzyko `rowid` w Open Questions jest przesadzone (zob. Key Decisions; `reports.py:268-292` łączy po kluczach trwałych).
- L5. `tests/test_explain.py:370` nie sprawdza kształtu `stages`. Żaden test nie czyta `stages` z wyniku `explain`. Zmiana jest bezpieczna.
- L6. Wykrywanie wydań: zagnieżdżone pakiety (`tematy-wydanie-20261029/<pakiet>/release-manifest.json`) i wersje typu `v1r2` w regule rodziny nie są opisane. Nieznany wpis powinien mieć klasę „nigdy”.
- L7. Kroki, które da się zautomatyzować: pomiar `fullfsync` można zrobić już w implementacji (T7 jest dziś zamontowany), zamiast zostawiać 4B do „kiedyś”. Restart nadzorcy po restarcie maszyny jest ręczny (można dodać LaunchAgent). Zachowanie przy SIGTERM/SIGHUP nie jest opisane; `running` zostaje, ale `--resume` to obsłuży.
- L8. `resume_reports.py` zmienia kontrakt kodów (dziś 0/2), a `cli.md` tego nie opisuje.
- L9. Testy nadzorcy wymagają podstawienia sztucznego buildu i ułamkowego `--wait-minutes` albo zegara. Spec nie mówi, jak.

## Sprawdzone bez zastrzeżeń (dowody)
- Kolejność DELETE dla `import_sgjp` zgadza się z FK w `schema.sql` (`variant_decision` → `decision_payload`/`analysis` → `derivation_component` → `derivation_candidate` → `interpretation` → `lexeme`/`surface_form` → `sgjp_record`; `corpus_evidence` na końcu). Wiersz `own-semantic-use-review-v1` (`decisions.py:102,356`) nie ma odwołań FK.
- Pola `new_*`: `constructions.py:607`, `decisions.py:432`. Testy (`test_decisions.py:49-50`, `test_constructions.py:279` i inne) czytają je z wartości funkcji, nie z raportów. `verify.py` ich nie czyta.
- Pozostałe poprawki „wznowiony = świeży” są potrzebne i wystarczają: `counts` żyje tylko w pamięci (`build.py:112-128`), `inventory` jest liczone poza etapem (`:129-134`), `links` nie ma `running` (`:170-184`). Metryki `import-counts` da się odtworzyć z bazy.
- Pieczęć: `SEAL_EXCLUDED = ('readiness','verification','export')` (`verify.py:25`), więc `build_attempts`, `resume` i `work_volume` są pod `manifest_core_sha256`, a zmiana po verify daje 5 (`export.py:59-62`). K8 porównuje `canonical-index` (`verify.py:455-462`), w którym nie ma niczego zależnego od przebiegu (`reports.py:119-122`).
- `.done/` nie trafia do pakietu: `_prepare_candidate` kopiuje tylko pliki z indeksu (`verify.py:542-549`).
- `export` po promocji: `changes_since_verify` używa ścieżek względnych od `run` i `inputs.manifest_path`; promocja ich nie zmienia.
- Build fikstury (`tests/release_helpers.py` `fixture_inputs`) kończy wszystkie 7 etapów jako `complete`, więc harness R6 ma realne punkty przerwania.
- Środowisko: Python 3.15, SQLite 3.54, `fcntl.F_FULLFSYNC` jest. W repo nie ma `.github/`, a spec nie wprowadza CI. `data/work` jest objęty Time Machine.
