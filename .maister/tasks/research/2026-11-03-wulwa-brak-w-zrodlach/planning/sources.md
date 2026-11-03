# Źródła: „wulwa”

## TL;DR
Ścieżki względem `/Users/robmar/Projects/Literaki/literaki-slownik` (chyba że podano inaczej). Wszystkie pliki lokalne istnieją (sprawdzone 2026-11-03). Dane surowe tylko do odczytu.

## Otwarte pytania / ryzyka
- Adresy zewnętrzne to punkty startowe; mogły się zmienić.

## 1. local (prefiks `local`)

### Frekwencja
- `cache/kwjp/kwjp100-slowa-orth_lc-all.csv.gz` (kolumny `,freq,ipm,ARF,DP,DP_norm,1-DP,total_freq`); też `-orth-`, `-lemma-` i podkorpusy `fakt`, `fikcja`, `publicystyka`.
- `cache/kwjp/kwjp100-2grams-lemma-all.csv.gz` (np. „wargi sromowe”).
- `cache/nkjp/1grams.gz` (format: `liczba forma`).

### SGJP
- `cache/sgjp/sgjp-20260823.tab.gz` — eksport; terminy porównawcze: srom, wagina, pochwa, łechtaczka, penis, prącie, moszna, klitoris, wulwodynia, wulwektomia, wulw*/vulv*.
- `cache/sgjp/oznaczenia.html`, `cache/sgjp/literaki-pl.json`.

### Słowosieć i IATE
- `cache/plwordnet/plwn45-tematy.sqlite` (tabela `lexicalunit`).
- `cache/plwordnet/wordnet_work_4_5.zip` — tylko `unzip -p … | grep -i -E 'wulw|vulv'`.
- `cache/iate/IATE_download.zip` — strumieniowo, „vulva”/„srom”/„wulw”.

### Lexicony i konfiguracja
- `/Users/robmar/Projects/Literaki/server/lexicons/pl-sjp-20260820.dawg`, `pl-standard-20261014.dawg`, `pl-broad-20261014.dawg` (i wersje 20261011).
- `config/generator/sgjp-supplement.tab` (dziś 4 formy: się/siebie/sobie).
- `literaki_slownik/policy.py` (linia ~62: odczyt suplementu).
- `config/generator/policy.json`, `quality.json`, `evidence.json`, `coverage.json`, `tematy/medycyna.json`.
- Decyzja suplementu: `.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/round4-sjp-benchmark-fixes-decision.md`.

## 2. docs (prefiks `docs`)

### Zasady SGJP
- `cache/sgjp-docs/instrukcja.html`, `release.html`, `license.html`, `download.html`.
- `cache/constructions/sgjp-theory.pdf`, `cache/constructions/rjp-2026.pdf`.
- `cache/sgjp-docs/Morfeusz2.pdf`, `cache/sgjp-docs/lexeme_export*.py`, `kuznia-models-61daf78.py` (co trafia do eksportu).

### Korpusy
- `cache/kwjp/article.pdf`, `README.source.md`, `overview.html`, `lists-doc.html`.
- `cache/nkjp/nkjp-page.html`, `1grams-page.html`, `polimorf-page.html`, `Morfeusz2.pdf`.

### Słowosieć
- `docs/adr/ADR-011-zrodla-slowosiec-iate.md`.

### Repo
- `AGENTS.md`, `docs/generator/LIMITATIONS.md`, `jakosc.md`, `mapowanie-kwjp.md`, `ortografia.md`.
- `.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/`: `supplementary-source-audit.md`, `sjp-benchmark-v25.md`, `-v27.md`, `-v29.md`.
- `.maister/tasks/research/2026-10-04-audyt-zrodel-polskich-slownikow/outputs/research-report.md`, `decision-log.md`.

## 3. external (prefiks `external`)
- SGJP online: https://sgjp.pl (wyszukiwarka; wulwa, vulva, wulwodynia).
- NKJP online: https://nkjp.pl (wyszukiwarki PELCRA/Poliqarp; wulwa, wulwie, wulwy, vulva).
- WSJP PAN: https://wsjp.pl.
- SJP PWN: https://sjp.pwn.pl (też Doroszewski: https://doroszewski.pwn.pl).
- SJP.pl: https://sjp.pl/wulwa (punkt odniesienia; kiedy dodano, źródło).
- Słowosieć online: https://plwordnet.pwr.edu.pl.
- Poradnie: https://sjp.pwn.pl/poradnia, https://rjp.pan.pl.
- Użycie medyczne: wyszukiwanie „wulwa” / „vulva” w polskich tekstach medycznych.
- Nie używać: Wikisłownik.
