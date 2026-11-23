# Przegląd pragmatyczny #22 (`git diff aa50eca..HEAD`)

## TL;DR
**Status: złożoność adekwatna, z drobnymi uwagami.** Nic krytycznego. Prawie cała złożoność wynika z decyzji
właściciela i spec: wznawianie, strażnik, nadzorca, promocja, sprzątanie, fullfsync. Przebudowa `build.py`
na pętlę etapów raczej upraszcza kod: jedna ścieżka dla świeżego buildu i wznowienia. Do poprawy jest
5 uwag (warning) i 8 drobnych (info): martwy kod, ta sama kontrola `--work-root` w pięciu miejscach
i pomocniki skopiowane między skryptami.

Skala: kod produkcyjny +2,2 tys. linii (36 plików kodu i testów), testy +2,6 tys., 8 ADR.

## Key Decisions
- Nie zgłaszam jako nadmiarowe: wznowienia per etap i per raport (`.done`), wznawiania przez nadzorcę
  tylko po 75, pomiaru fullfsync, promocji po verify z kasowaniem B, `clean_work` z kasowaniem wydań
  tylko po zgodzie, braku ręcznych kroków.
- Uznaję za uzasadnione przez spec: pole `resume`, `--server-current`, `find_by_marker` (M8), osiem klas
  `clean_work`, wstrzykiwanie zależności w nadzorcy (testy bez czekania 30 min).
- Hak `canonical.set_replace_guard` to stan globalny. Akceptuję go, bo G3 przed każdym `os.replace`
  nie przechodzi inaczej przez wszystkie wywołania `write_json`.

## Open Questions / Risks
- Czy tryb 4C ma zostać w kodzie po pomiarze, który go odrzucił (ADR-020)? Proponuję usunąć (W3).
- `probe` nadzorcy i `check_fresh` dają różne kody dla tej samej sytuacji (W2). Jeśli różnica jest
  celowa, trzeba ją zapisać; jeśli nie, to błąd kontraktu.

## Uwagi

### Warning
| # | Gdzie | Problem | Propozycja |
|---|---|---|---|
| W1 | `literaki_slownik/volume.py:106-112`; `literaki_slownik/build.py:519-522` | `check_resume` wołają tylko testy (`tests/test_volume.py:89-108`). `resume()` powtarza ten sam ciąg G1, G2 i miejsce. | `resume()` woła `volume.check_resume`; inaczej usunąć funkcję. |
| W2 | `volume.py:66-80`, `scripts/build_supervised.py:71-80`, `scripts/build_pair.sh:22-37`, `scripts/clean_work.py:129-147`, `scripts/init_work_volume.py:41-46` | Kontrola „korzeń istnieje, nie leży na dysku repo, ma znacznik” jest napisana pięć razy. Kody się rozjeżdżają: korzeń na dysku repo daje 76 w `check_fresh:73` i `build_pair.sh`, a 75 w `probe:77`. | Jedna funkcja `volume.check_work_root(path, minimum=None)`, która zwraca mount i marker. W `build_pair.sh` wystarczy jedno wywołanie Pythona. Ok. −40 LOC. |
| W3 | `literaki_slownik/database.py:9-21`, `build.py:34-41,371`, `tests/test_durability_modes.py:110-140` | Tryb `stage_boundaries` (4C) zostaje, chociaż ADR-020 go odrzuca (narzut 0,09% przy progu 5%). `FULLFSYNC_MODES` nic nie czyta. | Usunąć 4C, `full_sync` i jego test. `stage_durable` zostaje samym `db.commit()`. Ponowny pomiar robi dalej `measure_fullfsync.py`, a w razie potrzeby wracamy z gita. |
| W4 | `scripts/promote_run.py:66-86`; `literaki_slownik/canonical.py:49-90`; `database.py:7` | `_copy_file` przepisuje `write_bytes` (tmp, F_FULLFSYNC, replace, sync katalogu). Inne moduły wołają prywatne `canonical._full_sync` i `_sync_directory` (`promote_run.py:75,80,212`). | Upublicznić `full_sync` i `sync_directory` albo dodać `canonical.copy_durable(src, dst)`. |
| W5 | `build_supervised.py:93` i `clean_work.py:75`; `clean_work.py:111` i `promote_run.py:112`; `clean_work.py:59` i `promote_run.py:108`; `build_supervised.py:108`, `clean_work.py:122` i `volume.py:164` | Skopiowane pomocniki: sprawdzanie flocka, kasowanie drzewa read-only (dwie różne wersje chmod), rozmiar drzewa, „ścieżka wewnątrz”. Nazwy blokad `logs/<nazwa>.lock` i `.promote.lock` są wpisane literałem w trzech plikach. | Mały moduł, np. `literaki_slownik/workfs.py`, z `lock_held`, `remove_tree`, `tree_size`, `is_within` i nazwami blokad. Ok. −60 LOC, a kasowanie zachowuje się wszędzie tak samo. |

### Info
| # | Gdzie | Uwaga |
|---|---|---|
| I1 | `literaki_slownik/verify.py:34-43`, `literaki_slownik/run.py:147-149` | `build_history` ma też `stages` i `resume_count`, których spec nie wymienia. `resumed_from` da się wyliczyć ze `stages`. `resume.count` powtarza `len(build_attempts)-1`. Spec wymaga pola, więc tylko odnotowuję. |
| I2 | `build.py:471-472` | Walidacja manifestu przez wyrażenia-listy pisane jako instrukcje jest nieczytelna. Lepiej jawna pętla albo `all(...)`. |
| I3 | `scripts/resume_reports.py:42-54` i `run.py:120-128` | Nakładka powtarza kontrolę tożsamości kodu, którą `build --resume` i tak robi. Spec tego wymaga; skrypt można wycofać w kolejnym zadaniu. |
| I4 | `literaki_slownik/export.py:22,64-65`; `canonical.py:9-13` | Gałęzie dla Linuksa i spoza POSIX w narzędziu tylko na Maca. Są zgodne z istniejącym `rename_noreplace`, więc ich nie ruszać. |
| I5 | `scripts/build_pair.sh:50` i `build_supervised.py:155-157` | `build_pair.sh` dopisuje stdout i stderr nadzorcy do tych samych `logs/<nazwa>.supervisor.log` i `.err`, które nadzorca otwiera sam. Końcowy JSON miesza się z logiem zdarzeń. Lepiej osobny `.supervisor.out`. |
| I6 | `build_supervised.py:113,137` | `_wait` ma 11 parametrów, a `supervise` 12. Akceptowalne, bo dzięki temu testy działają bez zegara. Ewentualnie spakować w jeden obiekt `deps`. |
| I7 | `run.py:42-56` i `clean_work.py:204-206` | Wykrywanie resztki nieudanego startu jest zaimplementowane dwa razy, z nieco innymi warunkami. Lepiej jedna funkcja w `run.py`. |
| I8 | `export.py:57` | `rename_swap` woła tylko `promote_run.py`, a leży w `export.py`. To kwestia miejsca, nie zachowania. |

## Ocena złożoności
- **Skala projektu:** jeden operator, jeden Mac, stdlib, build ~13 h. Kosztem jest strata 13 h, więc
  trwały zapis, strażnik i wznawianie są proporcjonalne do ryzyka.
- **Bez zastrzeżeń:** pętla `STAGE_RUNNERS` z resetem tabel (`build.py:358-393`), znaczniki raportów
  (`build.py:304-328`), klasyfikator kodów (`build.py:137-163`), maszyna stanów S0–S4 promocji.
- **DX:** wszystko ma czytelny JSON na stdout, jawne kody i docstringi z użyciem. Ręczne kroki to tylko
  `init_work_volume.py` raz na dysk i plik zgody dla `--delete-releases`, oba z decyzji właściciela.

## Najważniejsze 3 uproszczenia
1. **W1 + W3, martwy kod.** Usunąć `check_resume` albo go użyć, a także tryb 4C. Ok. −30 LOC kodu
   i −40 LOC testów, 20 min.
2. **W2, jedna kontrola `--work-root`.** Przed: pięć wersji z różnymi kodami. Po:
   `volume.check_work_root(root, minimum=MIN_FREE_PAIR)` w `build_pair.sh`, `probe`, `check_fresh`
   i `clean_work`. Ok. −40 LOC i jeden kontrakt kodów, 30–45 min.
3. **W4 + W5, wspólne pomocniki plików.** Moduł `workfs.py` i publiczne `full_sync`. Ok. −60 LOC,
   jedna semantyka kasowania read-only, 30–45 min.

Razem ok. 1,5–2 h, bez zmian zachowania poza ujednoliceniem kodów z W2.
