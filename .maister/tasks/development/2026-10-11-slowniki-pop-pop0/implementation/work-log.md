# Work Log

## 2026-10-11T12:55:57Z - Implementation Started (etap A)

**Total Steps**: 90 w planie; teraz grupy 1–7 (etap A), stop po 7.6
**Task Groups**: fala 1: G1 + G5; potem G2, G3, G4, G6, G7 po kolei (wspólny pop.py)

## Standards Reading Log

### Loaded Per Group
(Entries added as groups execute)

## 2026-10-11T12:56:41Z - Group 5 Complete
**Steps**: 5.1–5.3. **Tests**: 18 OK (3 nowe + 15 test_quality). **Files**: literaki_slownik/quality.py (mapa SEEDS), tests/test_pop_quality.py.
**Standards**: AGENTS.md; docs/generator/jakosc.md (do uzupełnienia o pop-quality-v1 w grupie dokumentacji).

## 2026-10-11T12:59:34Z - Group 1 Complete
**Steps**: 1.1–1.5. **Tests**: tests.test_pop 7 OK. **Files**: config/generator/pop-sources.json, literaki_slownik/pop.py, tests/pop_helpers.py, tests/test_pop.py.
**Standards**: AGENTS.md, ADR-006 (pola NKJP w manifeście). Prawdziwe dane: check_inputs OK, hash bazy 85b23ca5… w 14,5 s, STANDARD 3 090 194; przebieg niezmieniony.

## 2026-10-11T13:20:29Z - Group 2 Complete
**Steps**: 2.1–2.7. **Tests**: tests.test_pop 14 OK. **Files**: pop.py (load_lexemes, load_kwjp[_lists], kwjp_measures, load_forms, load_forms_accepted, load_constructions), pop_helpers.py, test_pop.py.
**Standards**: AGENTS.md; prompt v3 §8.1/§8.2/§9.4.
**Real DB (ro)**: leksemy 11 s, KWJP 4 listy 6 s, miary 1,5 s (70 771 leksemów, 11 834 grup; masa 81,66 mln: EXACT 76,39, AMBIG 3,47, UNMATCHED 1,81), reguła (i) 12 s (3,28 mln par), konstrukcje 8 s (85 351 form: 83 586 jeden leksem, 1 765 kilka). RSS do 3,1 GB.
**Uwaga**: reguła (ii) ~13 min (14k wierszy/s, przerwana po 240 s) — wynik pomiaru do raportu A9.

## 2026-10-11T13:26:08Z - Group 3 Complete
**Steps**: 3.1–3.6. **Tests**: tests.test_pop 20 OK. **Files**: pop.py (CLEANING_RULES, read_nkjp, nkjp_collisions, form_owners, nkjp_form_status, nkjp_lexeme_ranks), test_pop.py.
**Real data (ro, hash bez zmian)**: form_owners 34 s, 4,93 mln kluczy (360 735 wspólnych). Masa NKJP 246,15 mln; dopasowana do STANDARD: full-nfc 66,7%, strip-edges 80,7%, keep-dot 75,2%. Ścisła jednoznaczność: 54% masy SGJP wspólne (się, nie, w, to) → do G4: opcja grupy homonimów także dla NKJP. Kolizje strip-edges: skróty (r., art., tys., np., ust., ul., proc.).

## 2026-10-11T13:41:10Z - Group 4 Complete
**Steps**: 4.1–4.7 + dodatek D5e. **Tests**: tests.test_pop 29 OK. **Files**: pop.py (opcje D1–D8, units z union-find, measure, rank_units, percentiles, coverage, threshold, tag_classes, load_form_classes, forms_for, spearman, top_overlap; D5e z parametrem eligible), test_pop.py.
**Odkrycie**: D5d łączy łańcuchowo przez nazwy własne (nie+Jedle+Onega; grupa 111). D5e dosłowne (relevant) nie pomaga, bo nazwy własne mają formy w STANDARD; e-common (bez nazw własnych): grupy 10 882, największa 22 (mieć/mój/mama), NKJP przypisane 73%, 0,9 pokrycia przy 10 712 leksemach. Zwykłe homonimy nadal łączą (nie/on/jeść).

## 2026-10-11T13:48:50Z - Group 6 Complete
**Steps**: 6.1–6.7. **Tests**: tests.test_measure_pop 6 OK. **Files**: scripts/measure_pop.py, tests/test_measure_pop.py.
**Bazowe ustawienia raportu**: D1 kwjp-standard; D2 pełna odmiana, konstrukcje tak, reguła (i); D3 KWJP+NKJP z percentyli, waga 0,5; D4 strip-edges-keep-dot; D5 e-common; D6 POP 40k, POP0 5k; D8 available-only. Reguła (ii) za flagą --with-membership-ii.

## 2026-10-11T14:17:54Z - Group 7 Complete
**Pomiar**: data/work/pop-measure-20261011-154857-{a,b,c}; a z regułą (ii) (1149 s, RSS 4,3 GB), b i c bez (261 s, 3,6 GB); b = c bajtowo; hash bazy bez zmian; a różni się tylko polami reguły (ii).
**Raport**: analysis/pop-measure-report.md + dodatek z sondą progów i decyzjami.
**7.6**: właściciel delegował decyzje („podnieść oba limity; POP mocno, POP0 trochę; decyzje podejmij sam”). Decyzje D1–D9 w dodatku raportu.

## 2026-10-11T14:20:40Z - Group 8 Complete
**Steps**: 8.1–8.4. **Files**: docs/adr/ADR-007-metoda-pop-v1.md (nowy, zaakceptowany z upoważnienia), ATTRIBUTIONS.md (NKJP wg D4), release.json i sources.json (piny). **Tests**: 320 OK; inspect-sources ok.
**Uwaga**: warunek D6 „kot w POP0” do sprawdzenia w walidatorze/buildzie (grupa 9/11).

## 2026-10-11T14:23:27Z - Group 9 Complete
**Steps**: 9.1–9.5. **Tests**: test_pop 36 OK, całość 327 OK. **Files**: config/generator/pop.json, pop.py (load_config), test_pop.py.
**Dla grupy 11**: D5 e-common = units('e', eligible=relevant−proper); d6 {pop, pop0} wprost do threshold(); must_include_pop0 ["kot"] do wymuszenia w pop.

## 2026-10-11T14:33:34Z - Group 10 Complete (bramka B5)
**Spec rew. 3** (47 wymagań) i **plan C–E** (grupy 11–17, 102 kroki). 10.4: właściciel zlecił 2026-10-11 „podejmij decyzje i wykonaj kolejne iteracje w ramach workflow maister” — kontynuacja bez osobnego zatrzymania; bramka przeglądu 16.8 zostaje.
**D-6 podstawa**: tree_sha256 81a5f82ae66f9457… (measure b); nowy kod pop pod sekcją konfiguracji.

## 2026-10-11T14:41:45Z - Group 11 Complete
**Tests**: test_pop 44 OK. **Files**: pop.py (pod sekcją konfiguracji: zawężenie ADR-007, build_pop, pop_summary), cli.py (pop), pop_helpers.py, test_pop.py.
**v29 (ro)**: POP 60 000 leks. = 45 229 jedn., 1 328 263 form (46 146 z konstrukcji), kwjp-standard 98,48%, kwjp-all 89,89%; POP0 20 000 = 11 600 jedn., 457 409 form, 94,39% / 86,15%; kot ranga 9 128 w POP0. 122 s, RSS 3,39 GB. Hash bazy bez zmian. D-6: kod rankingu = 7133fbe.
**Decyzja**: C19 częściowe (check_inputs wciąż pinuje plik NKJP) — do LIMITATIONS, bez zmiany zamrożonego kodu.
