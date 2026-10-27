# Źródła badania: słowniki tematyczne

## TL;DR
Główne źródło lokalne: `cache/sgjp/sgjp-20260823.tab.gz`, pole 5 ma kwalifikatory, w tym dziedziny.
Lista 73 etykiet dziedzin jest już w `descriptive-label-review.json` (pole `topics`).
KWJP i NKJP lokalnie mają tylko frekwencje i podkorpusy gatunkowe; dziedzin raczej brak.
Zasoby PAN w sieci: SGJP, WSJP, NKJP, KWJP; licencje do sprawdzenia.

## Open Questions / Risks
- Ścieżki w sieci (WSJP, NKJP) nie zostały jeszcze sprawdzone; adresy poniżej są punktem wyjścia.

Ścieżki względem `/Users/robmar/Projects/Literaki/literaki-slownik/`. Istnienie plików lokalnych sprawdzono 2026-10-27.

## Dane lokalne (local-data)

### SGJP
- `cache/sgjp/sgjp-20260823.tab.gz` — eksport form; pola: forma, lemat, tag, nazwa, kwalifikatory. Przykład: `algorytm … nazwa_pospolita mat.`
- `cache/sgjp/oznaczenia.html` — objaśnienia skrótów (zawiera `mat.`, `roln.`, `żegl.`).
- `config/generator/qualifiers.json` — wszystkie 615 dosłownych etykiet z liczbą kompaktowych interpretacji.
- `config/generator/sgjp-supplement.tab` — uzupełnienia projektu.

### Bazy i listy
- `data/work/lists-v31-20261013-060725-b/build.sqlite` (22 GB) — baza budowy v31; tylko do odczytu.
- `data/work/lists-v31-20261012-162111-a/` — para „a” v31.
- `data/work/release-LL-PL-v30/LL-PL-BROAD.txt`, `LL-PL-STANDARD.txt` — wydane listy do przecięcia z tematami.
- `literaki_slownik/schema.sql` — schemat bazy (gdzie są kwalifikatory).

### KWJP100
- `cache/kwjp/kwjp100-slowa-{lemma,orth,orth_lc}-{all,fakt,fikcja,publicystyka}.csv.gz` — 12 list frekwencji.
- `cache/kwjp/kwjp100-2grams-lemma-all.csv.gz` — 2-gramy.
- `cache/kwjp/README.source.md`, `tree.json`, `lists-doc.html`, `overview.html`, `article.pdf` — opis, w tym katalog `KWJP½M` (próbki tekstów; sprawdzić, czy mają metadane źródła).

### NKJP i Morfeusz
- `cache/nkjp/1grams.gz`, `1grams-page.html`, `nkjp-page.html` — unigramy i opis.
- `cache/nkjp/polimorf-page.html` — PoliMorf.
- `cache/nkjp/Morfeusz2.pdf`, `cache/sgjp-docs/Morfeusz/`, `cache/sgjp-docs/morfeusz-src-20260823.tar.gz` — tagi i kwalifikatory Morfeusza.

## Kod, konfiguracja i dokumenty projektu (code-docs)

### Kod
- `literaki_slownik/policy.py` — `descriptive_checks` (w. 797), reguła `linguistic-descriptive-non-excluding-v1`.
- `literaki_slownik/sgjp.py`, `literaki_slownik/inputs.py`, `literaki_slownik/database.py` — import kwalifikatorów.
- `literaki_slownik/kwjp.py`, `literaki_slownik/pop.py`, `literaki_slownik/explain.py`.
- `scripts/probe_generator_evidence.py` (`--mode labels`), `scripts/probe_pan_semantics.py`, `scripts/audit_sgjp.py`, `scripts/audit_kwjp.py`, `scripts/audit_nkjp.py`, `scripts/audit_pan_review.py`.

### Konfiguracja
- `config/generator/qualifiers.json`, `policy.json`, `categories.json`, `semantic-uses.json`, `sources.json`, `evidence.json`.

### Dokumenty
- `AGENTS.md` — zasady (zwięzłość, brak kontaktu z autorami).
- `.maister/docs/INDEX.md` — spis dokumentacji.
- `docs/generator/etykiety.md` — inwentaryzacja etykiet; sekcja „Etykiety opisowe — zamknięta mapa” (73 dziedziny).
- `docs/generator/mapowanie-kwjp.md`, `docs/literaki-niezalezne-slowniki-prompt-v3.md`, `docs/literaki-prosty-jezyk-minimum-leksykalne-kierunki.md`.
- `docs/adr/ADR-006-nkjp-cc-by-bez-wersji.md` — licencja NKJP.
- `.maister/tasks/research/2026-10-04-audyt-zrodel-polskich-slownikow/outputs/research-report.md` — audyt źródeł i licencji.
- `.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/`:
  - `descriptive-label-review.json` — `topics` (73), `styles`, `unmapped_atoms` (m.in. `astron.`, `kolej.`, `flis.`, `fot.`).
  - `descriptive-derivation-runtime.json` — liczniki ekspozycji.
  - `label-coverage.json`, `qualifier-semantics-audit.json`, `qualifier-coverage-review.md`.
  - `wiktionary-attestation-decision.md` — odroczenie Wikisłownika.

## Zasoby PAN w sieci (pan-resources)
- SGJP: https://sgjp.pl/oznaczenia/, https://sgjp.pl/instrukcja/, https://sgjp.pl/leksemy/ (formularz z filtrem kwalifikatorów), licencja: lokalnie `cache/sgjp-docs/license.html`.
- Kuźnia SGJP (kod eksportu): https://git.nlp.ipipan.waw.pl/SGJP/Kuznia
- WSJP (IJP PAN): https://wsjp.pl — kwalifikatory dziedzinowe, licencja i eksport do sprawdzenia.
- NKJP: https://nkjp.pl — metadane tekstów (typ, kanał), podkorpus zrównoważony; licencja wg ADR-006.
- KWJP: https://kwjp.pl, https://kwjp.ipipan.waw.pl/lists/doc/about/, https://github.com/ipipan/kwjp100-varia
- IPI PAN, Zespół Inżynierii Lingwistycznej: http://zil.ipipan.waw.pl — inne korpusy i zasoby (np. korpusy specjalistyczne, listy terminów).
- CLARIN-PL (repozytorium, filtr po instytucji IPI PAN): https://clarin-pl.eu — tylko zasoby PAN.

## Kandydaci spoza PAN
Nie szukamy celowo. Zbieracze notują je przy okazji w sekcji „Kandydaci spoza PAN”.
