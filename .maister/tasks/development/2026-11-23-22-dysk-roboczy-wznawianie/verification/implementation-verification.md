# Weryfikacja wdrożenia #22

## TL;DR
⚠️ **Zaliczone z uwagami.** 0 krytycznych, 13 ostrzeżeń, ~25 uwag info. Plan 95/95, testy 676+5 OK.
Wszystkie przeglądy dają GO na pierwszą parę na T7; żaden nie znalazł utraty danych.
Najważniejsze: krótkie zniknięcie T7 może dać kod 4 zamiast 75 (nadzorca stanie), brak blokady przy `--resume`, `clean_work` może po 24 h skasować kompletną parę czekającą na verify.

## Open Questions / Risks
- Para na T7 nie była uruchomiona ani odłączenie USB nie było testowane na sprzęcie — tylko podstawione `ismount`/`stat`.
- Czas pary na T7 niezmierzony (13 h to dysk wewnętrzny).
- Klasa 6 `clean_work` (kompletna para INCOMPLETE > 24 h) — decyzja właściciela.

## Podsumowanie
Wdrożenie realizuje R1–R13: build na T7, kody 75–78, `build --resume` per etap i raport, nadzorca, promocja po verify z kasowaniem B, `clean_work` z kasowaniem wydań tylko po zgodzie, historia prób. Harness „wznowiony = świeży” przechodzi w 19 punktach przerwania.

## Wyniki kontroli
| Kontrola | Wynik | Raport |
|---|---|---|
| Kompletność | ⚠️ 0/1/5 — plan 95/95, docs R13 kompletne | [completeness-check.md](completeness-check.md) |
| Testy | ✅ 676 + 5 OK (grupa 14; ponowiony w readiness: 676 OK) | work-log |
| Przegląd kodu | ⚠️ 0/4/9 | [code-review-report.md](code-review-report.md) |
| Przegląd pragmatyczny | ⚠️ 0/5/8 | [pragmatic-review.md](pragmatic-review.md) |
| Reality check | ⚠️ 0/3/5, GO | [reality-check.md](reality-check.md) |
| Gotowość | ⚠️ 0/2/6, GO z mitygacjami (88%) | [production-readiness-report.md](production-readiness-report.md) |

## Ostrzeżenia
| # | Źródło | Problem | Miejsce | Do poprawy |
|---|---|---|---|---|
| 1 | reality R1 | T7 wraca zanim pojawi się błąd I/O → strażnik zdrowy → kod 4, nadzorca staje | `build.py` `exit_code` | tak |
| 2 | code | `build --resume` bez blokady; `resume_reports` przyjmuje `reports=running` — może ruszyć bazę żywego buildu | `build.py:508-527`, `resume_reports.py:50` | tak |
| 3 | code | Po 75 nadzorca czyta `marker_id` z niedostępnego manifestu → `None` → przeniesiony wolumen daje 75 po 30 min zamiast 76 | `build_supervised.py:51-61,185` | tak |
| 4 | code | Przerwane `rmtree` B zostawia drzewo bez manifestu (~22 GB), którego nikt nie skasuje | `promote_run.py:231-235`, `clean_work.py:421-428` | tak |
| 5 | code | Klasa 6 kasuje kompletną parę INCOMPLETE (czeka na verify) po 24 h | `clean_work.py:199-209` | decyzja |
| 6 | readiness W1 | SIGHUP po zamknięciu terminala kończy parę (129); runbook bez `& disown`, krok po restarcie bez `caffeinate` | runbook §5, `cli.md` | tak |
| 7 | reality R2 | Nadzorca bez watchdoga na zawieszone I/O | `build_supervised.py` | tak (prosty limit bez postępu) |
| 8 | pragmatic W2 | Kontrola korzenia w 5 miejscach; korzeń na dysku repo: 75 w `probe`, 76 w `check_fresh` | `volume.py`, `build_supervised.py:77`, … | tak |
| 9 | pragmatic W1 | `volume.check_resume` martwy (tylko testy) | `volume.py:106-112` | tak |
| 10 | pragmatic W3 | Tryb 4C w kodzie mimo odrzucenia; `FULLFSYNC_MODE` bez walidacji | `database.py`, `build.py` | tak |
| 11 | pragmatic W4/W5 | Prywatne `canonical._full_sync`/`_sync_directory` poza modułem; zdublowane pomocniki (flock, rmtree ro, rozmiar, `_inside`) | `promote_run.py`, `clean_work.py`, `database.py` | tak |
| 12 | completeness | Pusty „Standards Reading Log” w work-log | `work-log.md` | tak |
| 13 | readiness W2 | Czas pary na T7 niezmierzony | runbook | nie (zmierzyć przy 1. parze) |

Info (wybór): brak sync katalogów stagingu, T7 czytany ~4×22 GB w promocji, sygnał między `Popen` a zapisem dziecka, mieszany stdout w `supervisor.log`, `KeyError` w `resume_reports`, `OSError` z kasowania w `clean_work` → traceback, 5 `ResourceWarning` w starych testach.

## Rekomendacje
1. Poprawić 1–4, 6–12 (techniczne, testowalne).
2. 5: wyłączyć z kasowania przebiegi, których wszystkie etapy są `complete` (rekomendacja) — po decyzji.
3. Przy pierwszej parze: raz odłączyć T7 w krótkim etapie i sprawdzić w logu 75 → wait → `--resume` → 0; zapisać czasy etapów.

## Lista kontrolna
- [x] Plan 95/95 · [x] Testy 676+5 · [x] R1–R13 udokumentowane · [x] Brak UUID/ścieżek domowych · [x] `config/` bez zmian · [x] Brak CI · [ ] Ostrzeżenia 1–12
