# ADR-015: strażnik wolumenu G1+G2+G3, znacznik na wolumenie

**Status:** zaakceptowana 2026-11-23 (decyzja agenta). Zadanie #22.

## TL;DR
Moduł `literaki_slownik/volume.py` pilnuje, żeby build pisał tylko na właściwy dysk roboczy.
G1: punkt montowania, G2: znacznik `.literaki-work-volume`, G3: `st_dev` katalogu przebiegu.
UUID wolumenu jest tylko w znaczniku na wolumenie. Manifest i repo znają jedynie losowy `marker_id`.

## Kontekst
Po ponownym montowaniu deskryptory są martwe. Wolumen może wrócić pod inną nazwą (`<nazwa> 1`), a pod
starą ścieżką może pojawić się pusty katalog na dysku systemowym. Repo jest publiczne, więc identyfikator
sprzętu nie może trafić do kodu, konfiguracji ani manifestu.

## Decyzje
- **G1:** najbliższy przodek ścieżki po `realpath` z `os.path.ismount`. Przebieg-symlink, którego cel
  leży na punkcie montowania repo, oznacza niezamontowany wolumen: 75.
- **G2:** znacznik w korzeniu wolumenu zawiera UUID z `diskutil` i `marker_id`. Zakłada go raz
  `scripts/init_work_volume.py <korzeń>`; stdout ma tylko `marker_id`. Kody skryptu: 4 znacznik już jest,
  76 korzeń na dysku repo, 75 brak korzenia albo błąd `diskutil`.
- **G3:** `st_dev` aktywnego przebiegu zapamiętane w procesie, sprawdzane przed etapem i przed `os.replace`
  w zapisie trwałym. Przy `--resume` liczy się G2, bo `st_dev` zmienia się po montowaniu.
- Ścieżka na dysku repo bez `--work-root` przechodzi (testy, stare przebiegi; `work_volume` = null).
  Jawny `--work-root` zawsze wymaga znacznika. Wolumen zewnętrzny bez znacznika albo inny `marker_id`: 76.
- **Miejsce:** ≥ 50 GB przy starcie buildu i wznowienia, ≥ 100 GB w `build_pair.sh`. Inaczej 78.
- Wolumen o tym `marker_id` pod inną ścieżką: 76 i ścieżka w logu. Symlinków nikt nie przepina sam.

Odrzucone: same prawa `/Volumes` i strażnik tylko w `build_pair.sh` (nie widzą każdego etapu i zapisu).

## Otwarte pytania / ryzyka
- Przypadkowe usunięcie znacznika daje 76 i wymaga ręcznej decyzji.
- Znacznik na T7 założono 2026-11-23. Nowy dysk roboczy wymaga nowego `init_work_volume.py`.
