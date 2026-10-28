# Work Log

## 2026-10-28T23:19:14Z - Implementation Started

**Total Steps**: 89
**Task Groups**: 1 wiki, 2 wspólny kod, 3 źródła i pochodna, 4 ADR, 5 konfiguracja, 6 wejścia, 7 kandydaci, 8 leksemy i formy, 9 raporty/pakiet/CLI, 10 checker i przegląd, 11 dokumenty, 12 przegląd testów, 13 budowy a/b, 14 strona R2 i bramka, 15 bramka operatora

**Fale**: W1 = {1, 2, 3}. Każda grupa ma rozłączne pliki. work-log prowadzi agent główny. Commity w repo słownika robi agent główny po fali.

## Standards Reading Log

### Loaded Per Group
(Entries added as groups execute)

## 2026-10-28T23:20:57Z - Group 2 Complete

**Steps**: 2.1–2.5
**Standards Applied**: AGENTS.md (po polsku, zwięźle), spec D1/D2
**Tests**: 95 OK (test_quality, test_pop, test_pop00, test_pop00_package, test_pop_quality)
**Files Modified**: literaki_slownik/{quality,pop,pop00}.py, tests/{pop00_helpers,test_pop,test_quality}.py
**Notes**: `SIZES = {'tematy-quality-v1': 50}`, reszta 30. `_write_gzip` → `write_gzip` bez aliasu. Commit 63e9c29.

## 2026-10-28T23:21:45Z - Group 1 Complete

**Steps**: 1.1–1.6
**Standards Applied**: docs/runbook-wiki.md (start prac nad nowym słownikiem, lista kontrolna kroku 4), spec W14/D13
**Tests**: brak testów jednostkowych; publiczna strona ma „W przygotowaniu” i link do #11
**Files Modified**: wiki: Slownik-TEMATY.md (nowa), Home.md, _Sidebar.md, Slownik-STANDARD.md, Historia-zmian.md
**Notes**: commity wiki 0ffad2e, c67ba8d. Liczby trafią na stronę w grupie 14.

## 2026-10-28T23:33:01Z - Group 3 Complete

**Steps**: 3.1–3.9
**Standards Applied**: AGENTS.md (dane surowe poza Git), spec W1–W2, K1, W1, W2, W4, D3, D6–D8
**Tests**: 6 OK (test_fetch_tematy_sources, test_build_plwordnet_db)
**Files Modified**: scripts/fetch_tematy_sources.py, scripts/build_plwordnet_db.py, tests/test_fetch_tematy_sources.py, tests/test_build_plwordnet_db.py, analysis/verify_plwordnet.py, verification/{sources,plwordnet-derivative,iate-scan}.json
**Notes**:
- IATE: cache/iate/IATE_download.zip, 112 828 998 B, sha256 ac50c2a7…5c6f, last_modified 30.09.2019, member IATE_export_26022019.tbx.
- Słowosieć: hash zgodny z pinem 30edc5f8…dcbc.
- Pochodna plwn45-tematy.sqlite: sha256 aa65ad79…c536. Dwie budowy dają ten sam hash (SQLite 3.51.0), każda trwa ok. 50 s. Pochodna nie ma danych redaktorów.
- Kierunek PARENT_ID → CHILD_ID potwierdzony (statek 1 → łódź 2, okręt 1).
- Domknięcie T2 ma **864** lematy według definicji „jednego słowa” (W7). Audyt podał 874, bo liczył też formy z łącznikiem i kropką.
- TBX: 4821 ma 577 haseł PL. fullForm, bez deprecated, niezawodność ≥ 3, jedno słowo: 78 (74 różne). T3 będzie małe.
- Decyzja techniczna: `supersededTerm-admn-sts` też odrzucamy (spójność z deprecated). Wśród 78 kandydatów nie ma żadnego, więc wpływ jest zerowy. Zapis w ADR-011.

## 2026-10-28T23:36:35Z - Group 4 Complete

**Steps**: 4.1–4.4
**Standards Applied**: wzór ADR-009, AGENTS.md
**Tests**: kontrola linków i grep kodów audytu: K1, W1–W9 i D1–D16 są w ADR
**Files Modified**: docs/adr/ADR-010-tematy-v1.md, docs/adr/ADR-011-zrodla-slowosiec-iate.md
**Notes**: `odrzuc_status` w `morze.json` ma być listą (deprecated i superseded). Moduł z grup 6–7 odrzuca oba statusy. Commit f23e5fa.

## 2026-10-28T23:37:37Z - Group 5 Complete

**Steps**: 5.1–5.7
**Standards Applied**: AGENTS.md; wzór pop00.load_sources; spec W3–W5, W13
**Tests**: 6 OK (test_tematy_config). Prawdziwe pliki ładują się, a piny zgadzają się z dyskiem (bez hashowania build.sqlite).
**Files Modified**: config/generator/{tematy.json,tematy-sources.json,tematy/morze.json,tematy-teksty/*}, literaki_slownik/tematy.py, tests/tematy_helpers.py, tests/test_tematy_config.py
**Notes**:
- `odrzuc_status` to lista: deprecated i superseded.
- `LIMITATIONS.md` ma znacznik `@@SRODLADOWE@@`, który budowa (grupa 9) podmienia na udział śródlądowych.
- Pakietowe ATTRIBUTIONS to plik POP plus ATTRIBUTIONS-tematy.md.
- Grupa 6 sprawdza `meta.zip_sha256` pochodnej z pinem zipa.

## 2026-10-28T23:42:22Z - Group 6 Complete

**Steps**: 6.1–6.6
**Standards Applied**: spec W3, W6, D5, D7; wzór pop00.check_inputs
**Tests**: 12 OK (test_tematy_inputs, test_tematy_config). Mutacja z odczytem spoza rejestru daje czerwony test.
**Files Modified**: literaki_slownik/tematy.py, tests/tematy_helpers.py, tests/test_tematy_inputs.py
**Notes (kontrakt dla grup 7–9)**:
- `register(data, path, expected_sha) -> Path` nie hashuje; wcześniej trzeba wywołać `checked_file`/`package_file`. `_unpinned` obsługuje pliki bez pinu. `confirm_unchanged(data)` hashuje ponownie cały rejestr; woła się go tuż przed `rename_noreplace`.
- `check_inputs(manifest, config, topic)` zwraca dict z kluczami: registry, source, method, topic, texts, paths (9 INPUTS), pins, package, members {POP, POP0}, broad, standard, pop, pop00, attribution, plwordnet_meta.
- Każdy nowy odczyt idzie z `data['paths']` albo `data['package']`. `POP0.txt.gz` nie jest czytany.
- Grupa 9 mapuje OSError i ValueError na kod 4.
- Fikstura `inputs_fixture` ma stałe SGJP, PLWN i TBX do rozbudowy. Audit hook z test_tematy_inputs nadaje się do testu „budowa nie czyta poza rejestrem”.
