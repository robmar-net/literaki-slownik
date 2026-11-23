# Weryfikacja wdrożenia #22

## TL;DR
✅ **Zaliczone (po poprawkach).** 0 krytycznych, 0 otwartych ostrzeżeń, uwagi info zaakceptowane. Plan 95/95, testy 715 + 5 OK.
Pierwsza weryfikacja: 13 ostrzeżeń. Poprawione 1–12 (commit `7aed1ea`), ponowny przegląd: 11/12 rozwiązane, 10 częściowo (4C zostaje jako zapas, z walidacją), 1 nowe (N1) — poprawione z N2–N8 w drugim commicie.
GO na pierwszą parę na T7.

## Open Questions / Risks
- Nic nie sprawdzono na sprzęcie: odłączenie T7 w trakcie buildu, zawieszenie USB (watchdog), odłączenie w trakcie `.deleting`. Plan: przy pierwszej parze raz odłączyć T7 w krótkim etapie i sprawdzić w logu 75 → wait → `--resume` → 0.
- Czas pary na T7 niezmierzony (nr 13; 13 h dotyczy dysku wewnętrznego). Zmierzyć przy pierwszej parze.
- Przebieg, który oblał verify, i B z `peer-kept` zostają na T7 bez terminu (~22 GB każdy; decyzja właściciela przy nr 5). `clean_work` pokazuje `age_days`; kasuje się je ręcznie.
- Reguła `repeated-75-healthy` nie obejmuje 75 przed powstaniem manifestu z etapami (wtedy tylko limit 3 wznowień).

## Podsumowanie
Wdrożenie realizuje R1–R13: build na T7, kody 75–78, `build --resume` per etap i raport, nadzorca z watchdogiem, promocja po verify z kasowaniem B, `clean_work` z kasowaniem wydań tylko po zgodzie, historia prób. Harness „wznowiony = świeży” przechodzi w 19 punktach przerwania.

## Wyniki kontroli
| Kontrola | Pierwszy przebieg | Po poprawkach | Raport |
|---|---|---|---|
| Kompletność | ⚠️ 0/1/5 | ✅ (log standardów uzupełniony) | [completeness-check.md](completeness-check.md) |
| Testy | ✅ 676 + 5 | ✅ 715 + 5 | work-log |
| Przegląd kodu | ⚠️ 0/4/9 | ✅ 0/0/info | [code-review-report.md](code-review-report.md), [code-review-reverify.md](code-review-reverify.md) |
| Przegląd pragmatyczny | ⚠️ 0/5/8 | ✅ W1–W5 poprawione | [pragmatic-review.md](pragmatic-review.md) |
| Reality check | ⚠️ 0/3/5, GO | ✅ R1, R2 poprawione; R3 = test na sprzęcie | [reality-check.md](reality-check.md) |
| Gotowość | ⚠️ 0/2/6, GO z mitygacjami | ✅ W1 poprawione; W2 = pomiar | [production-readiness-report.md](production-readiness-report.md) |

## Historia poprawek i ponownej weryfikacji
| # | Problem | Poprawka | Wynik ponownej kontroli |
|---|---|---|---|
| 1 | Szybki powrót T7 → kod 4 | I/O (EIO/ENXIO/ENODEV/ENOENT/EROFS, SQLITE IOERR/CANTOPEN) na wolumenie → 75; dysk wewnętrzny nadal 4 | rozwiązane (`build.py:137,165-168`) |
| 2 | `--resume` bez blokady | `.<nazwa>.build.lock` obok symlinku na cały build; `resume_reports` i `clean_work` ją respektują | rozwiązane |
| 3 | `marker_id` gubiony po 75 | zapamiętany przed pierwszym procesem i po każdym odczycie | rozwiązane |
| 4 | Przerwane kasowanie B zostawia 22 GB | `workfs.delete_tree`: rename na `.<nazwa>.deleting`, dokończenie przy ponowieniu | rozwiązane |
| 5 | Klasa 6 kasuje kompletną parę | decyzja właściciela: nie kasować; klasa 3 „kompletny, czeka na verify” + `age_days` | rozwiązane |
| 6 | SIGHUP kończy parę | runbook/cli: `nohup … & disown`; nadzorca zachowuje ignorowanie SIGHUP | rozwiązane |
| 7 | Brak watchdoga | `--stall-minutes` (120), postęp = mtime plików lub czas CPU; `cputime-unknown` w logu | rozwiązane |
| 8 | Kontrola korzenia w 5 miejscach, 75 vs 76 | `volume.check_work_root` wszędzie; dysk repo → 76 | rozwiązane |
| 9 | Martwe `check_resume` | używane w `build.resume` | rozwiązane |
| 10 | Tryb 4C bez walidacji | walidacja `FULLFSYNC_MODE` (kod 4); 4C zostaje jako zapas (ADR-020) | częściowo, zaakceptowane |
| 11 | Prywatne helpery, duplikaty | publiczne `full_sync`/`sync_directory`/`copy_durable`, `literaki_slownik/workfs.py` | rozwiązane |
| 12 | Pusty log standardów | uzupełniony w work-log | rozwiązane |
| N1/N8 | Błąd kodu na T7 wygląda jak zanik dysku | drugie zdrowe 75 w tym samym etapie → 4 (`repeated-75-healthy`), ADR-019 | rozwiązane (test `Healthy75Tests`) |
| N3/N4 | Hung proces / ręczny resume przez ścieżkę T7 | `--resume` przez ścieżkę T7 → 4; runbook opisuje oba przypadki | rozwiązane |
| N5 | `.X.deleting` jako wydanie | pomijane w `_find_releases` | rozwiązane |
| N7 | Brak listy skasowanych przy błędzie | JSON `{error, exit_code, deleted}` | rozwiązane |
| N6 | Puste pliki blokad zostają | — | info, akceptowane |
| 13 | Czas pary na T7 | — | pomiar przy pierwszej parze |

## Rekomendacje
1. Pierwsza para na T7 (za zgodą właściciela): `nohup … & disown`, jedno kontrolowane odłączenie T7, zapis czasów etapów do runbooka.
2. Poza #22: 5 `ResourceWarning` w starszych testach (`test_links_structures`, `test_round5_zds`, `test_sjp_extra`).

## Lista kontrolna
- [x] Plan 95/95 · [x] Testy 715 + 5 · [x] R1–R13 udokumentowane · [x] Brak UUID/ścieżek domowych · [x] `config/` bez zmian · [x] Brak CI · [x] Ostrzeżenia 1–12 i N1–N8
