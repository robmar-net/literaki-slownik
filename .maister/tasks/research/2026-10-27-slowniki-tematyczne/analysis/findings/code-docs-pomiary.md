# Co już zmierzono o etykietach dziedzin

## TL;DR
Mamy liczniki po etykietach i po słowach, ale nie po leksemach ani po temacie.
83 023 z 7 458 520 kompaktowych interpretacji (1,11 %) ma choć jeden atom z 73 dziedzin.
Warstwa `word:specialist` w v30/v31 liczy 66 590 słów (`game_key`) z dziedziną w którejkolwiek analizie.
Przegląd 30 słów z tej warstwy oceniał decyzję listy, nie trafność tematu.

## Key Decisions
- Jednostka dotychczasowych liczników to kompaktowa interpretacja (forma + zwinięty tag) albo słowo. Nie leksem. Liczby leksemów na temat trzeba policzyć od nowa (zbieracz local-data).
- Liczniki etykiet się nakładają; projekt ich nie sumuje (`qualifier-conditions.json`: `label_counts_overlap: true`).

## Open Questions / Risks
- 9 atomów o charakterze dziedziny jest poza mapą 73 (`unmapped_atoms`): `astron.`, `astrol.`, `kolej.`, `fot.`, `spoż.`, `etn.`, `flis.`, `biblt.`, `gry`. Mają status „objaśnienie nieustalone”. `etn.` to etnonimy, nie dziedzina (`unexplained-labels-first-release-decision.md`, „Przykłady”). `biblt.` celowo nie rozwinięto.
- 110 dosłownych etykiet z atomem dziedziny (2 641 interpretacji) jest poza mapą opisową, bo łączy dziedzinę z wiekiem lub niepoprawnością (np. `daw.,żegl.` 33, `przest.,techn.` 320). Dziedzina jest w nich czytelna, ale STANDARD może je odrzucać.
- `word:specialist` bierze `max` po analizach słowa. Homonimy wpadają przez jedno znaczenie: w próbce są `kręgom`, `markiem`, `stróż` (`quality-review-v31.json`).

## 1. Źródła pomiarów
| plik | co mierzy | jednostka |
|---|---|---|
| `config/generator/qualifiers.json` | 615 pól, licznik na etykietę | kompaktowe interpretacje |
| `.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/descriptive-label-review.json` | 357 etykiet opisowych; `topics` 73, `styles` 18, `form_markers` 2, `unmapped_atoms` 28; hash `oznaczenia` i `instrukcja` | etykiety |
| `…/evidence/descriptive-derivation-runtime.json` | 139 729 rekordów ekspozycji reguły opisowej, wszystkie 357 etykiet obecne (`etykiety.md:60`) | rekordy ekspozycji |
| `…/evidence/label-coverage.json` | wszystkie kombinacje i liczniki (`etykiety.md:23-25`) | interpretacje |
| `data/work/release-LL-PL-v30/reports/qualifier-conditions.json` | warunek na każdą etykietę; `totals`: 7 458 524 interpretacji, 6 423 662 bez kwalifikatorów, 1 034 860 z jakimkolwiek warunkiem | interpretacje |
| `data/work/release-LL-PL-v30/reports/quality-words.json` | `word:specialist`: populacja 66 590, próbka 30 | słowa |
| `.maister/tasks/development/2026-10-12-stabilizacja-progu-pop/verification/quality-review-v31.json` | 30 słów z `word:specialist`: 30 × `correct` | decyzja listy |

Odtworzenie liczników etykiet: `python3 scripts/probe_generator_evidence.py --database PATH --mode labels` (`etykiety.md:25`, `scripts/probe_generator_evidence.py:100-103`).

## 2. Policzone teraz z `qualifiers.json` (bez bazy)
Skrypt: `python3` czytający `config/generator/qualifiers.json` i `topics` z przeglądu. Atom = część etykiety po podziale `,`. Licznik = suma `compact_interpretations` etykiet z tym atomem.

| atom | etykiet | interpretacji | w tym poza mapą opisową |
|---|---:|---:|---:|
| `żegl.` | 13 | 3 741 | 46 |
| `mors.` | 10 | 1 812 | 1 |
| `ryb.` | 3 | 528 | 0 |
| `roln.` | 5 | 2 121 | 10 |
| `ogr.` | 5 | 672 | 0 |
| `leśn.` | 3 | 511 | 11 |
| `zootechn.` | 3 | 296 | 0 |
| `pszcz.` | 2 | 278 | 11 |
| `mat.` | 10 | 929 | 23 |

Największe dziedziny: `techn.` 9 876, `zool.` 7 024, `bot.` 5 355, `hist.` 4 226, `jęz.` 3 784. Najmniejsze: `bank.` 1, `plast.` 11, `genet.` 12, `hydrol.` 12.
Uwaga: to formy (kompaktowe interpretacje), nie leksemy. Liczbę leksemów da dopiero baza.

Atomy poza mapą (interpretacje): `etn.` 967, `astron.` 326, `gry` 189, `fot.` 165, `spoż.` 132, `slang` 129, `astrol.` 22, `biblt.` 11, `flis.` 11, `kolej.` 11.
Tabela oznaczeń SGJP ma dziś inne zapisy (`fotogr.`, `astr.`, `etnon.`); projekt nie utożsamia ich automatycznie (`unexplained-labels-first-release-decision.md`, „Przykłady”).

## 3. Czego nie zmierzono
- Liczby leksemów na dziedzinę i na temat.
- Przecięcia z LL-PL-BROAD / LL-PL-STANDARD na poziomie tematu.
- Trafności tematu na próbce (przegląd `word:specialist` sprawdzał tylko accept/reject listy).
- Pokrycia: ile słów z tematu nie ma etykiety.
- Audyt źródeł 2026-10-04 nie uruchamiał modeli tematycznych (`.maister/tasks/research/2026-10-04-audyt-zrodel-polskich-slownikow/outputs/research-report.md:144`).
