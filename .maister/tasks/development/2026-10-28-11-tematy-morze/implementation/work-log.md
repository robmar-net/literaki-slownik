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

## 2026-10-28T23:49:00Z - Group 7 Complete

**Steps**: 7.1–7.6
**Standards Applied**: spec W5, W7, K1, W1, W2, W4, D3, D4; ADR-011
**Tests**: 20 OK (8 nowych + 12 regresji). Mutacje (podział tylko po „,”, wyłączony _check_header) dają czerwone testy.
**Files Modified**: literaki_slownik/tematy.py, tests/tematy_helpers.py, tests/test_tematy_sources.py
**Prawdziwe dane (tylko odczyt)**:
- T1: 254 leksemy (zgodnie z badaniem). Jeden skan trwa 6,7 s.
- T2: 1 092 synsety, 866 surowych lematów, 864 po małych literach. 504 jednostki odpadają jako NIE_JEDNO_SLOWO.
- T3: 78 terminów przyjętych (74 różne). Liczby zgodne z iate-scan.json.
**Kontrakt dla grupy 8**:
- `scan_sgjp(data)` zwraca {t1: {lexeme_id: atomy}, klasy: {lexeme_id: klasy tagów}}.
- `t2_candidates(data)` zwraca {synsets, sztuczne, jednostki, lematy (klucze NFC, bez zmiany wielkości liter), odrzucone}.
- `t3_candidates(data)` zwraca {terminy, hasla (pl, en, przyjete), odrzucone, liczniki}.
- `candidates(data)` uruchamia wszystkie trzy.
- `ger` szukamy indeksami (surface_form → interpretation), bez drugiego pełnego skanu.

## 2026-10-28T23:56:02Z - Group 8 Complete

**Steps**: 8.1–8.6
**Standards Applied**: spec W7, W8, D15, W4/W5; ADR-010 (reguła wieloznaczny z lokalnego ADR-007)
**Tests**: 27 OK. Mutacje (filtr kodów 1–4, tag ger, warstwa najwyższa) dają czerwone testy.
**Files Modified**: literaki_slownik/tematy.py, tests/tematy_helpers.py, tests/test_tematy_layers.py
**Prawdziwe dane (tylko odczyt, bez check_inputs)**: wpisy 964 (T1 246, T2 691, T3 27), MORZE 10 883 formy; wieloznaczny: nie 459, tak 430, brak_danych 75. T3 BRAK_LEKSEMU 20 (ger 9).
**Kontrakt dla grupy 9**: `build_entries(data, cands)` zwraca {kandydaci, wpisy, warstwy, formy, diagnostyka, odrzucone, ger}. Przykłady to pierwsze 10 z pełnych list. T3 jest małe (27), więc w próbie bierzemy całą warstwę.

## 2026-10-29T00:03:12Z - Group 9 Complete

**Steps**: 9.1–9.7
**Standards Applied**: spec W6, W8–W11, W15; ADR-010; wzór pop00._write_package/build_package
**Tests**: 36 OK (nowe 7 i regresja z test_cli). Mutacje (brak confirm_unchanged, operator per+1, brak znaczników EN) dają czerwone testy.
**Files Modified**: literaki_slownik/tematy.py, literaki_slownik/cli.py, tests/tematy_helpers.py, tests/test_tematy_package.py
**Kontrakt dla grup 10, 11 i 14**:
- Pakiet ma 13 plików, wszystkie 0444:
  - MORZE.txt.gz;
  - MORZE.tsv.gz, kolumny w `tematy.TSV_KOLUMNY`: klucz, lemat, czesci_mowy, warstwa, zrodla, znaczenie, wieloznaczny, formy;
  - tematy/morze.json, method.json;
  - reports/{summary.json, raport.md, sample.json, review-template.json};
  - ATTRIBUTIONS.md, LIMITATIONS.md, TERMS.md;
  - release-manifest.json (kind literaki-tematy-manifest, status BUILT);
  - SHA256SUMS.
- summary.json ma klucze:
  - liczby;
  - przeciecia{leksemy,formy}{T1,T2,T3,razem}{temat,pop{liczba,procent},pop00{…}};
  - diagnostyka, odrzucone, t1, t2, t3, wieloznaczny;
  - slowa_oczywiste{razem,T1,T1_T2,spelniony,prog};
  - srodladowe{kandydaci_t3,wpisy_t3};
  - werdykt{automatyczny,niespelnione,czeka_na_ocene}.
- sample.json zawiera wynik sample_strata oraz operator{per_stratum,strata} i items.
- Wywołanie CLI: `python3 -m literaki_slownik tematy --manifest config/generator/tematy-sources.json --config config/generator/tematy.json --topic config/generator/tematy/morze.json --output-dir <nowy> [--json]`. Kody wyjścia: 0, 2, 3, 4, 5.

## 2026-10-29T00:06:26Z - Group 11 Complete

**Steps**: 11.1–11.5
**Standards Applied**: AGENTS.md; wzór c14df5d; spec W13, W14, D13; docs/generator/publikacja.md
**Tests**: test_documented_names OK; 60 OK w powiązanych modułach; linki do repo istnieją
**Files Modified**: docs/generator/{cli,raporty,jakosc}.md, docs/runbook-wiki.md, .maister/docs/INDEX.md, ATTRIBUTIONS.md
**Notes**:
- Flagi skryptów z grupy 10 trzeba dopisać w cli.md po jej zakończeniu.
- Pin ATTRIBUTIONS.md w config/generator/release.json był nieaktualny już przed tym zadaniem (POP00 też go nie odświeżył). Poprawka przy najbliższym wydaniu LL-PL; poza zakresem #11.

## 2026-10-29T00:11:52Z - Group 10 Complete

**Steps**: 10.1–10.6
**Standards Applied**: spec W11, W12, W6, W8, D12, D14; wzór check_pop00_package.py i record_review.py
**Tests**: 14 OK. Mutacja „niepewne = tak” daje czerwone testy. Strona sprawdzona w Playwright 390×844: bez poziomego przewijania.
**Files Modified**: scripts/check_tematy_package.py, scripts/tematy_review.py, tests/test_check_tematy_package.py, tests/test_tematy_review.py, tests/tematy_helpers.py
**Polecenia dla grup 13 i 14**:
- Oceny agenta: `tr.agent_review(PKG, {key: {ocena, powod}}, 'agent (Claude)', ts)` + `tr.write_review(T/verification/tematy-morze-review.json, review)`. Commit i push przed `strona` (D12).
- Kontrola: `python3 scripts/check_tematy_package.py --package-dir <PKG> --manifest config/generator/tematy-sources.json --config config/generator/tematy.json [--review <review.json>]`.
- Strona: `python3 scripts/tematy_review.py strona --package-dir <PKG> --review <review.json> --output $T/verification/tematy-morze-r2.html`.
- Zapis ocen operatora: `python3 scripts/tematy_review.py zapisz --package-dir <PKG> --review <review.json> --oceny <operator.json|->`.

## 2026-10-29T00:15:09Z - Group 12 Complete

**Steps**: 12.1–12.5
**Tests**: pełny zestaw: `Ran 514 tests … OK` (tests) oraz `Ran 5 tests … OK` (scripts/test_audit_sgjp). Brak pominiętych. Dodano 3 testy: dodatki i wykluczenia, leksem w trzech warstwach, błąd SQLite → kod 4 bez pakietu.
**Bug fixed**: `load_topic` przyjmował niepuste `t3.dodatki` i `wykluczenia`, a budowa ich nie czytała, więc wpis był po cichu pomijany. Teraz v1 daje kod 2. ADR-010 dostał o tym zdanie.
**Files Modified**: literaki_slownik/tematy.py, tests/test_tematy_{config,layers,package}.py, docs/generator/cli.md (dokładne flagi skryptów), docs/adr/ADR-010-tematy-v1.md
**Uwaga**: wykluczenia rzecznych terminów po przeglądzie (decyzja operatora) wymagają w v2 obsługi `wykluczenia` w budowie.

## 2026-10-29T00:24:00Z - Group 13 Complete

**Steps**: 13.1–13.7
**Budowy**:
- a: 00:15:47–00:17:10Z (83 s); b: 00:17:10–00:18:29Z (79 s). Obie: status ok, bez diagnostyk.
- 13 plików identycznych bajt w bajt. SHA256SUMS sha256 724f2e81…30a9. Checker PASS na a i na b.
**Wyniki**:
- Wpisy 964 (T1 246, T2 691, T3 27); MORZE ma 10 883 formy.
- Przecięcie leksemów: POP 44,3%, POP00 11,4%. Przecięcie form: POP 36,4%, POP00 9,6%.
- Test 37 słów: 31/37 (83,8%), próg spełniony. Brakuje: sztorm, rybak, cumować, falochron, nabrzeże, trał.
- Żegluga śródlądowa: 0/74 kandydatów T3. Terminy śródlądowe są wielowyrazowe i odpadają wcześniej.
**Ocena agenta (127 pozycji)**:
- T1: 46/50 tak.
- T2: 21/50 tak, 23 nie. To szum pełnego domknięcia: liny, belki, pętle, części maszyn.
- T3: 9/27 tak, 14 nie (ogólne słowa z dziedziny IATE).
- agent_sha256 a423e84c…1e4b.
**Files**: analysis/{verify_real.py,record_agent_review.py,agent-ratings.json}, verification/{real-builds.json,tematy-morze-review.json}

## 2026-10-29T00:24:54Z - Group 14 w toku

- 14.1: check --review PASS (przed oceną operatora).
- 14.2: strona R2 `verification/tematy-morze-r2.html` opublikowana jako prywatny artefakt https://claude.ai/artifact/JA8v14hjvz4skM6MT1PAQB. Ma 87 pozycji: T1 30, T2 30, T3 27. Ocen agenta na stronie nie ma.
- Czekamy na JSON od operatora (14.3–14.4).

## 2026-10-29T00:52:16Z - Group 14 Complete

- Operator: „trudno rozdzielić morze i żeglugę, ja bym wszystkie słowa z listy przyjął”. Zapisano 87 × tak (`tematy_review.py zapisz`, rc 0).
- Checker `--review`: PASS, werdykt „popraw” (tylko zgodność 47/87, kappa 0).
- Wiki f35fa4f: liczby na Slownik-TEMATY, Home i Historia-zmian; nadal „W przygotowaniu”.
- `verification/gate-report.md` zapisany.

## 2026-10-29T01:06:21Z - Groups 15–16 Complete
- 15: decyzja „popraw” (decision-log.md).
- 16: dodatki D (2bd0dab, a633136); 520 + 5 testów OK; v2 a=b, checker PASS, 37/37; oceny przepięte (sample bez zmian).
