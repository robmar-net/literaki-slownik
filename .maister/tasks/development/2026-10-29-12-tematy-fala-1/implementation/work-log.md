# Work Log — #12

## 2026-10-29T02:03:46Z - Implementation Started

**Total Steps**: 127 — 121 zrobione [x], 6 pominięte [~] (stan końcowy `implementation-plan.md`)
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

## 2026-10-29T02:31:32Z - Group 9 Complete
**HEAD przed seriami**: 048d57e (bez commitów do końca porównania). **Budowy**: tematy-morze-v2-20261029-a 86 s, -b 80 s; SHA256SUMS a=b 108077a4…; checker pass na obu (970 wpisów, 11 035 form, 37/37).
**W8**: ZGODNE — MORZE.txt/tsv, ATTRIBUTIONS, TERMS bajtowo jak tematy-v2-20261029-a; LIMITATIONS tylko linie T2/T3; summary równy po korekcie (czeka_na_ocene); sample strata/items równe, operator.strata T2/T3. Kontrola negatywna na starej parze łapie 3 różnice.
**Commit**: 4a7022c (+ verification/verify-morze.json).

## 2026-10-29T02:35:06Z - Group 10 Complete
**Commit**: 08a6adc. **Tests**: 2/2. Przegląd morza przepięty na tematy-morze-v2-20261029-a; checker --review: t1_tak 23/25 (agent), t2_tak 1, t2_nie 0, t3_tak 1, słowa 37/37, zgodność 20/57 (kappa 0) → „popraw” — zgodnie z W9.

## 2026-10-29T02:35:06Z - Pauza: czekamy na operatora (2.4)
Zrobione: grupy 1, 3–10; 2.1–2.3 (strona https://claude.ai/artifact/4XiPDXkEs7dxRE78ohghJ9). Dalej: 2.4–2.6 → 11 → 12 (18 budów) → 13–20.

## 2026-10-29 — Grupa 2 zakończona (2.4–2.6)

Operator: „wszystkie listy wygladaja ok”. Szkic przyjęty bez zmian jako `wynik` (329 słów, 9 tematów). Brak słów dopisanych, więc 2.5 bez sprawdzania (szkic sprawdzony w 2.3). Listy zamrożone.

## 2026-10-29 — Grupa 11 zakończona

9 plików tematów, `tests/test_tematy_fala.py` (3 testy). Commit `047a75b`. Testy TEMATY: 71/71.
`_check_names` i osiągalność 7 wykluczonych poddrzew: OK. Pochodna zgodna z pinem.

| temat | synsety | lematy | małe litery | W11 |
|---|---|---|---|---|
| zwierzeta | 11616 | 4452 | 4452 | OK |
| rosliny | 7084 | 3111 | 3111 | OK |
| medycyna | 5660 | 4063 | 4063 | OK |
| muzyka | 1378 | 1148 | 1148 | OK |
| kuchnia | 2797 | 2434 | 2432 | OK (D9: budowa nie zmienia wielkości liter → 2434) |
| sport | 831 | 757 | 757 | OK |
| matematyka | 1133 | 543 | 543 | OK |
| pogoda | 224 | 209 | 209 | OK |
| grzyby | 963 | 351 | 351 | OK |

`powód` wykluczeń poddrzew dopisany przez agenta (W11 go nie podawał): zwierzęta — człowiek/hominid to nie zwierzęta w tym temacie; medycyna — organy i tkanki roślin.

## 2026-10-29 — Grupa 12 zakończona

18 budów z HEAD `265f1e8`, 09:15–09:40Z (~25 min). 9/9: a = b, checker pass/pass, kontrola fali OK. Commit `420b698`. Zestawienie: `verification/builds.json`.
T3 tylko w medycynie: 342 wpisy. D = 0 wszędzie. `srodladowe` = null wszędzie.
Test słów oczywistych (próg 0,70) nie przeszedł: grzyby 61,8%, pogoda 63,9%, sport 55,6% → werdykt auto „popraw”; reszta „dalej”. Braki to głównie słowa ogólne (las, zima, boisko, drużyna) — do bramki (W14).

## 2026-10-29 — Grupa 13: 13.1–13.2

Instrukcja oceny agenta i `record_agent_review.py` (pętla po tematach), commit `45d36f8`. Kontrola na sztucznych ocenach: brak/obcy klucz, zła ocena, pusty powód — odmowa; poprawny plik przechodzi checker `--review`. 13.3: 9 niezależnych sesji oceniających (każda czyta tylko instrukcję i swój `review-template.json`), razem 950 ocen.
Uwaga: test słów oczywistych nie zależy od ocen, więc grzyby, pogoda i sport dostaną „popraw” niezależnie od R2.

## 2026-10-29 — Grupy 13–14 zakończone

Oceny agenta: 950, commit `913f496` (9 hashy). Strony R2: commit `5f17bcc` (po ocenach). Tak/nie/niepewne w T2: grzyby 23/5/22, pogoda 41/0/9, matematyka 29/6/15, muzyka 32/3/15, sport 44/0/6, kuchnia 42/3/5, rośliny 38/0/12, zwierzęta 43/0/7, medycyna 38/5/7; T3 medycyny 22/11/17.
Opublikowane: strona zbiorcza https://claude.ai/artifact/YbQQhcwinGG7ZistFiMAeG; tematy: grzyby J5EzrRHN3GqDB65YRxfLDw, pogoda 1B1ka5pXotDHv2wLzyb262, matematyka Vx8EAUUMbBQiogmT7F4feN, muzyka AV6sr5j3kAkVuHsv1dfvmW, sport QkoDnx8mh3KCN3LfkzeLjQ, kuchnia WHcJ2cPj11r5EGHszcVCNR, rośliny 6jXHjUmTBUvkurUkJZEToY, zwierzęta L8faHrWkHDSLu6dPGYdB7T, medycyna GmCnntS4ittxg6FzRBwtuu.
Uwaga: `strona` odmawia bez hasha w pliku przeglądu, ale nie sprawdza commita — kolejność pilnowana procedurą.

## Pauza: czekamy na operatora (15.2) — oceny R2, 300 pozycji.

## 2026-10-29 — Grupa 15 zastąpiona

Operator nie ocenia R2 (terminy wymagają wyszukiwarki). Decyzja: trafność T2/T3 z ocen agenta, zgodność nie dotyczy (scope-clarifications.md). Uwaga operatora: cytoplazma ≠ kuchnia (zgodnie z agentem).

## 2026-10-29 — Grupa 16 zakończona

Commit `7d2b714`. Bramka metodą z ocen agenta: dalej — kuchnia, rośliny, zwierzęta; popraw — grzyby (słowa 61,8%, T2 0,46), pogoda (słowa), matematyka (T2 0,58, nie 0,12), muzyka (T2 0,64), sport (słowa), medycyna (T1 0,84, T3 0,44), morze.
Ważne: na morzu agent jest dużo surowszy od operatora (T2 21/50 vs operator 30/30; T3 9/27 vs 27/27; 37 lematów „tak” operatora agent ocenił „nie”). Ocena agenta zaniża trafność → pytanie do bramki 20.2.
Decyzje operatora w gate-report.md puste do 20.2.

## 2026-10-29 — Grupa 17 zakończona

Commit `1f86e2a`: ADR-012 (regresja morza, T3 medycyny 342, zmiana metody R2 i stronniczość agenta), cli/raporty/jakosc, runbook-wiki, INDEX. Przykład nuty/zawody poprawiony w spec W10.2 (psy, koty); w ADR-012 go nie było. test_documented_names 4/4.

## 2026-10-29 — Grupy 18–19 zakończone

- 18: wiki `b0b202f` — Slownik-TEMATY (tabela 10 tematów, „W przygotowaniu”, bez wstępnych werdyktów), Home, Slownik-STANDARD, _Sidebar, Historia-zmian. Publiczna strona sprawdzona.
- 19: +3 testy (`7f30ebd`): dodatek na wykluczonym leksemie → kod 4; temat z t3 i pustą T3 w summary; checker odrzuca obce `summary.wykluczenia`. Pełny zestaw: 555 OK; test_audit_sgjp 5 OK.
- Decyzja techniczna: summary przed oceną pokazuje `t3_tak` jako „czeka” przy pustej T3 (checker po ocenie daje `niespelniony`). Zostawiamy — nie dotyczy fali (medycyna ma T3 = 342), poprawka wymagałaby przebudów. Do rozważenia przy v2.

## 2026-10-29 — Grupa 20: bramka

Decyzje operatora w gate-report.md i decision-log.md. Dalej: kuchnia, rośliny, zwierzęta, morze. Popraw: grzyby, pogoda, sport, matematyka, muzyka, medycyna. Bez wydania. Wszystkie kroki planu zamknięte.
