# Źródła badania

## TL;DR
- Pliki lokalne niżej sprawdzono 2026-11-03: istnieją.
- Adresy w sieci to punkty startu. Zbieracz potwierdza każdy adres, licencję i datę odczytu.
- SJP.pl, Wikisłownik i PoliMorf są wyłączone.

## Kluczowe decyzje
- Miejski Słownik Slangu tylko jako kontrola obecności słowa, nigdy jako źródło.
- Google Books Ngram i Common Crawl traktujemy jako kandydatów do sprawdzenia warunków, nie jako dozwolone.

## 1. `neolog` — obserwatoria i słowniki nowych słów
| Źródło | Punkt startu (do weryfikacji) | Co sprawdzić |
|---|---|---|
| Obserwatorium Językowe UW | https://nowewyrazy.uw.edu.pl | prowadzący, licencja wpisów, cadence, eksport |
| Słowniki i projekty „Nowe słowa w polszczyźnie”, neologizmy (np. IJP PAN, UW, UJ, UŁ) | WebSearch: „neologizmy polszczyzna baza”, „słownik neologizmów” | czy są dane, licencja, lata |
| WSJP PAN, nowsze hasła | https://wsjp.pl | nowe hasła 2020+, licencja (specyfikacja §4.4: nie jest wejściem bez ustalenia praw) |
| SGJP online, zmiany | https://sgjp.pl, https://download.sgjp.pl/morfeusz/ | nowsze eksporty niż 20260823, lista zmian, kontrole |
| PWN, nowe słowa | https://sjp.pwn.pl, poradnia PWN | czy jest dział nowych słów, warunki |
| Rada Języka Polskiego, Młodzieżowe Słowo Roku | https://rjp.pan.pl, https://mlodziezowesloworoku.pl | listy słów, licencja |
| Miejski Słownik Slangu (tylko kontrola) | https://www.miejski.pl | obecność kontroli |
| Słowosieć 5.0 online | https://plwordnet.pwr.wroc.pl | nowe lematy po 4.5 |

## 2. `korpusy` — korpusy i listy 2015+
| Źródło | Punkt startu (do weryfikacji) | Co sprawdzić |
|---|---|---|
| MoNKa (monitorujący korpus) | WebSearch: „MoNKa korpus monitorujący IPI PAN” | okres, dostęp, licencja list |
| KWJP (okres, nowe wydania) | https://kwjp.pl, https://github.com/ipipan/kwjp100-varia | okres korpusu, nowsze listy niż commit `26d82bd8` |
| ParlaMint-PL | https://www.clarin.si/repository (ParlaMint), CLARIN-PL | CC BY 4.0?, lata, podział w czasie |
| OSCAR (pl) | https://oscar-project.org, Hugging Face `oscar-corpus` | licencja tekstu i pochodnej, domeny |
| HPLT (pl) | https://hplt-project.org/datasets | licencja, metadane domen i dat |
| CulturaX (pl) | Hugging Face `uonlp/CulturaX` | warunki, pochodzenie (mC4 + OSCAR) |
| FineWeb-2 (pol_Latn) | Hugging Face `HuggingFaceFW/fineweb-2` | ODC-By, daty zrzutów CC, domeny |
| MADLAD-400 (pl) | Hugging Face `allenai/MADLAD-400` | licencja, dedup, daty |
| Spokes (mowa) | http://spokes.clarin-pl.eu | okres, licencja |
| Korpusy prasowe, monitorujące (np. PELCRA, CLARIN-PL) | https://clarin-pl.eu/dspace, http://nkjp.uni.lodz.pl | daty tekstów, warunki list |
| Wikipedia i Wikinews pl, zrzuty | https://dumps.wikimedia.org/plwiki/, /plwikinews/ | CC BY-SA 4.0, historia wersji jako oś czasu |
| n-gramy z Common Crawl | WebSearch: „Common Crawl n-grams Polish” | licencja, daty |
| Google Books Ngram (brak polskiego?) | https://books.google.com/ngrams | czy jest polski, warunki |

Ryzyko do zmierzenia w każdym korpusie sieciowym: udział stron sjp.pl i jego kopii; czy da się je wykluczyć po URL.

## 3. `projekt` — zasady i dane lokalne
### Dokumenty
- `/Users/robmar/Projects/Literaki/literaki-slownik/AGENTS.md`
- `/Users/robmar/Projects/Literaki/literaki-slownik/docs/literaki-niezalezne-slowniki-prompt-v3.md` (§2.3, §2.4, §3.1, §4.1–4.5, §16)
- `/Users/robmar/Projects/Literaki/literaki-slownik/docs/adr/ADR-006-nkjp-cc-by-bez-wersji.md`
- `/Users/robmar/Projects/Literaki/literaki-slownik/docs/adr/ADR-011-zrodla-slowosiec-iate.md`
- `/Users/robmar/Projects/Literaki/literaki-slownik/docs/plan-dalszych-prac-runbook.md`
- Poprzednie badanie: `/Users/robmar/Projects/Literaki/literaki-slownik/.maister/tasks/research/2026-11-03-wulwa-brak-w-zrodlach/outputs/research-report.md`
- Audyt źródeł: `/Users/robmar/Projects/Literaki/literaki-slownik/.maister/tasks/research/2026-10-04-audyt-zrodel-polskich-slownikow/`

### Konfiguracja
- `config/generator/sources.json`: dziś `ALLOWED` to SGJP 20260823 (BSD-2-Clause), `sgjp-supplement-v1` (BSD-2-Clause, rola `lexical`) i 15 artefaktów KWJP100 (CC BY 4.0, rola `corpus_evidence`, próg 5). `unavailable`: NKJP (`BLOCKED_LICENSE_VERSION_UNRESOLVED`).
- `config/generator/sgjp-supplement.tab`: 4 formy, wzór wejścia leksemu spoza eksportu.
- `config/generator/evidence.json`, `policy.json`, `tematy-sources.json`, `pop-sources.json`: inne wzory wpisu źródła.

### Dane lokalne do pomiaru kontroli
- `cache/sgjp/sgjp-20260823.tab.gz`
- `cache/kwjp/kwjp100-slowa-lemma-{all,fakt,fikcja,publicystyka}.csv.gz`, `kwjp100-slowa-orth_lc-all.csv.gz`, `kwjp100-2grams-lemma-all.csv.gz`, `article.pdf` (okres korpusu)
- `cache/nkjp/1grams.gz`
- `cache/plwordnet/` (Słowosieć 4.5)
