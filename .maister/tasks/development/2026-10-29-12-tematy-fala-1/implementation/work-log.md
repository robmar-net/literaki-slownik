# Work Log — #12

## 2026-10-29T02:03:46Z - Implementation Started

**Total Steps**: 107
**Task Groups**: 1–20 (stopy operatora: 2.4, 15.2, 20.2)
**Bramka planu:** zgoda operatora z góry (2026-10-29, „wyrażam zgodę … zacznij na podstawie tej zgody”).

## Standards Reading Log

### Loaded Per Group
(Entries added as groups execute)

## 2026-10-29T02:06:15Z - Group 8 Complete
**Steps**: 8.1–8.4. **Commit**: 5259900. **Files**: docs/adr/ADR-012-tematy-fala-1.md (nowy), ADR-010 (+1 linia). INDEX.md: wpis ADR-012 (orchestrator).
**Standards**: AGENTS.md; format ADR-010/011.

## 2026-10-29T02:07:12Z - Group 3 Complete
**Steps**: 3.1–3.7. **Commit**: 8757039. **Tests**: test_tematy_config 13/13; test_tematy_dodatki 6/7 — 1 błąd i 5 w test_check_tematy_package/test_tematy_review: checker „Zła metoda” (tematy-v1) → grupa 7.
**Files**: tematy.py (METHOD tematy-v2, TOPIC_KEYS, _lemmas, operator_warstwy), tematy.json, morze.json (dodatki na górze), tests/tematy_helpers.py (t3=True|False), test_tematy_config, test_tematy_dodatki.
**Standards**: AGENTS.md; policy.CLASS_MATRIX jako klasy SGJP dla wykluczeń.
**Uwagi dla dalszych grup**: 4 — t3_candidates/check_inputs zakładają t3, osiągalność wykluczeń poddrzew; 5 — raport czyta znaczniki_srodladowe (KeyError), hashe tekstów w tematy.json; hash morze.json zmieniony (W8).

## 2026-10-29T02:09:43Z - Group 1 Complete
**Steps**: 1.1–1.6. **Commit**: 920a89b. **Tests**: 3/3 OK.
**Wynik**: 329 słów (zwierzeta 37, rosliny 38, medycyna 39, muzyka 37, kuchnia 37, sport 36, matematyka 35, pogoda 36, grzyby 34); wszystkie przeszły W10.2 w 1. rundzie. Agent bez dostępu do danych (dowód w slowa-oczywiste-check.json).
**Uwaga**: przykład „nuty/zawody” w W10.2 i ADR-012 błędny (to osobne leksemy SGJP); poprawne przykłady: psy, koty → do poprawy w grupie 17.

## 2026-10-29T02:11:38Z - Group 4 Complete
**Steps**: 4.1–4.6. **Commit**: 1f2ec7b. **Tests**: 12/12 w modułach grupy (6 nowych); szerzej 56/62 — 6 znanych czerwonych dla grupy 7 („Zła metoda”).
**Zmiany**: IATE tylko przy t3 (rejestr, manifest), _no_t3, _exclude (kod 4 bez trafienia), osiągalność wykluczeń poddrzew, summary.wykluczenia, sekcja raportu „Wykluczenia”. Fikstura second_topic (zwierzeta bez t3).
**Morze na fiksturze**: TXT, TSV, raport, LIMITATIONS bajtowo bez zmian; summary +"wykluczenia": [].
**Dla grupy 5**: LIMITATIONS bez T3 ma jeszcze @@SRODLADOWE@@; „MORZE” w TL;DR raportu; linie T3 w „Źródła”. Grupa 6: srodladowe może być None.

## 2026-10-29T02:13:48Z - Group 2 w toku (2.1–2.3)
**Commit**: 78abb49 (strona i generator T/analysis/strona_slowa.py). Kontrola WebKit/Chromium 390 px, jasny/ciemny: PASS.
**Artefakt**: https://claude.ai/artifact/4XiPDXkEs7dxRE78ohghJ9 (prywatny). szkic_sha256 22014ec4…8f5b (kanoniczny JSON pola szkic).
**Czeka**: 2.4 operator (rano).

## 2026-10-29T02:17:55Z - Group 5 Complete
**Commit**: 6a6915e. **Tests**: test_tematy_teksty + test_tematy_package 14/14; 6 znanych czerwonych dla grupy 7.
**Zmiany**: odcinki()/teksty_pakietu() (reguła bajtowa W4), segmenty <!--T3--> / <!--SRODLADOWE--> w tekstach, nowe hashe w tematy.json, summary.t3 null bez t3, raport bez „MORZE”.
**Bajty**: fikstura morze TXT/TSV/ATTRIBUTIONS/TERMS identyczne, LIMITATIONS tylko linie T2 i T3; prawdziwe teksty po stripie = stare hashe (d6673156…, b4250289…).
**Uwaga dla 9**: raport.md morza będzie inny (dozwolone W8).

## 2026-10-29T02:20:33Z - Group 6 Complete
**Commit**: 823332e. **Tests**: test_tematy_package 12/12 (4 nowe); znane czerwone dla grupy 7 + nowy w test_tematy_review (pętla po PROBA zamiast operator.strata).
**Zmiany**: czeka(method,t3), PROG_WARSTWA, operator.strata wg operator_warstwy, werdykt.nie_dotyczy, linia raportu.
**Korekta W8 (decyzja orchestratora)**: porównanie summary.json morza pomija też werdykt.czeka_na_ocene (t1_tak wypada z czekających, bo T1 ocenia tylko agent) — oczekiwane [t2_tak,t2_nie,t3_tak,zgodnosc].

## 2026-10-29T02:25:32Z - Group 7 Complete
**Commit**: 486a991. **Tests**: test_tematy* 68 OK, test_check_tematy* 11 OK — wszystkie moduły TEMATY zielone.
**Zmiany**: checker tematy-v2 (adr, operator_warstwy, temat przed pinami, blok iate tylko z t3, pusty T3 bez t3, exclusions(), werdykt W6); tematy_review.page_items po operator.strata.
**Dla 10**: binding = sample_sha256, canonical_index_sha256, evidence_sha256, version z review-template + sha256sums; operator bez T1 (57 pozycji).
