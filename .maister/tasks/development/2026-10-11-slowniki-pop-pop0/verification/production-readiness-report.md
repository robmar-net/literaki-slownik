# Gotowość wydania pop-v1

**Data:** 2026-10-11 · **Cel:** wydanie danych `pop-v1` (GitHub Release) · **Pakiet:** `data/work/pop-v1r3-20261011-175938-a`
**Werdykt:** GO z uwagami · **Ryzyko:** niskie · **Blokery:** 0 · **Uwagi:** 2 · **Drobne:** 5

## TL;DR
Wydanie jest gotowe. Pakiet się odtwarza, sumy się zgadzają, NKJP ma atrybucję zgodną z ADR-006, surowych danych NKJP brak. Dwie uwagi: pakiet sam o sobie mówi „nie jest wydaniem” (status `BUILT`), a `SHA256SUMS` wydania wymienia pliki, których nie ma wśród zasobów.

## Key Decisions
- Status `BUILT` w pakiecie plus osobny `pop-v1-review.json` (`REVIEWED`) uznaję za zgodny z projektem (docs/generator/cli.md:45). Przegląd jest związany z pakietem hashami (`sha256sums_sha256`, `sample_sha256`, `canonical_index_sha256`, `evidence_sha256`).
- Integracja z serwerem gry: poza zakresem.

## Open Questions / Risks
- Odbiorca, który pobierze tylko tarball, przeczyta „pakiet nie jest wydaniem” (W1).
- ADR-006: jeśli IPI PAN poda wersję CC BY, trzeba sprawdzić zgodność (ryzyko opisane w ADR).

## Pomiary

| sprawdzenie | wynik |
|---|---|
| dwa przebiegi | `diff -r …-a …-b` identyczne |
| piny `pop.json` / `pop-sources.json` | SHA256 = `config_sha256` / `sources_sha256` w manifeście |
| pin NKJP | `cache/nkjp/1grams.gz` = `73af4909…3dc9` (manifest, ADR-006, ATTRIBUTIONS) |
| piny LL-PL | `database`, `release_manifest`, `standard` w manifeście = `pop-sources.json` |
| tożsamość kodu | `a2e64f4`, `git_dirty: false`; do HEAD bez zmian w `literaki_slownik/` i `config/` |
| `SHA256SUMS` pakietu | `shasum -c`: 10/10 OK |
| zasoby wydania | `POP.txt.gz`, `POP0.txt.gz`, tarball, review: OK; rozpakowane listy = `504725ab…0139`, `6fde7b6a…d966` |
| tarball = lokalny pakiet | `diff -r` identyczne |
| `check_pop_package.py --review` na pobranym wydaniu | rc=0, „zgodny i przegląd REVIEWED” |
| format | UTF-8, LF, małe litery, sort bajtowy (`LC_ALL=C sort -c`), bez duplikatów; 1 219 614 / 380 489 wierszy = manifest |
| podzbiory | POP0 ⊆ POP: 0 wyjątków; POP ⊆ LL-PL-STANDARD v29: 0 wyjątków |
| surowe NKJP | brak pliku; `units.json` ma tylko `nkjp_rank`, `nkjp_percentile`, `nkjp_status`; bez zliczeń |
| wiki POP / POP0 | liczby, linki, sha256 zgodne; 18/18 przykładów sprawdzonych na liście |

## Atrybucje vs ADR-006 (suma CC BY 1.0–4.0)

| wymaganie | w `ATTRIBUTIONS.md` |
|---|---|
| twórca, tytuł, adres | tak |
| licencja + link 4.0 + zdanie o wszystkich wersjach | tak |
| zmiany | tak (reguła czyszczenia, rangi) |
| prawa i gwarancja nie podane | tak |
| brak poparcia | tak (także w opisie wydania) |
| brak dodatkowych ograniczeń | tak (TERMS: CC BY 4.0 / BSD-2, bez DRM) |

KWJP: CC BY 4.0, commit, autorzy, informacja o zmianach. SGJP: pełne zawiadomienie BSD-2 z wyłączeniem odpowiedzialności.

## Uwagi (warning)

**W1. Pakiet mówi o sobie „nie jest wydaniem”.** `release-manifest.json`: `status: BUILT`; `LIMITATIONS.md` wiersz 1: „pakiet nie jest wydaniem… wymaga przeglądu… `REVIEWED`”. Przegląd jest tylko poza tarballem. LL-PL v29 ma `FROZEN`. Naprawa: w opisie wydania jedno zdanie, że `pop-v1-review.json` (`REVIEWED`) jest przeglądem tego pakietu (`sha256sums_sha256` = SHA256 jego `SHA256SUMS`); w pop-v2 zmienić tekst LIMITATIONS. Naprawialne: tak.

**W2. `SHA256SUMS` wydania wymienia `POP.txt` i `POP0.txt`, których nie ma w zasobach.** `shasum -a 256 -c SHA256SUMS` daje 2× „FAILED open or read” i kod ≠ 0. Ten sam układ ma llpl-v29. Naprawa: w opisie podać `shasum -a 256 -c --ignore-missing SHA256SUMS` albo osobny plik sum dla list rozpakowanych. Naprawialne: tak.

## Drobne (info)
- I1. `ATTRIBUTIONS.md` w pakiecie ma linki względne do plików spoza pakietu: `LICENSE` (w.220), `LICENSE-DOCS.md` (w.223), `config/generator/sources.json` (w.269). Warunki są i tak spełnione (pełny tekst BSD-2, URL CC BY 4.0 w TERMS). Odziedziczone z LL-PL v29.
- I2. Literówki odziedziczone z LL-PL: „sg jp-20260823” (w.227), „BSD-2-Clause 2-Clause” (w.172).
- I3. Katalog w tarballu nazywa się jak przebieg (`pop-v1r3-20261011-175938-a/`), nie `pop-v1/`.
- I4. Strony wiki POP i POP0 nie podają licencji list (CC BY 4.0 / BSD-2); podaje ją strona wydania.
- I5. Tag `pop-v1` wskazuje `44a1d04`, kod pakietu to `a2e64f4`; bez zmian kodu i konfiguracji pomiędzy, więc odtwarzalne z tagu.

## Next Steps
1. Dopisać do opisu wydania pop-v1 zdanie o statusie przeglądu (W1) i polecenie `--ignore-missing` (W2).
2. Przy pop-v2 / następnym LL-PL: poprawić LIMITATIONS, linki i literówki w ATTRIBUTIONS (I1, I2), nazwę katalogu w tarballu (I3).
