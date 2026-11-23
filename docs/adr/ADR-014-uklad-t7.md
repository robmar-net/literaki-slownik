# ADR-014: build na T7, symlink per przebieg, promocja po `verify`

**Status:** zaakceptowana 2026-11-23 (właściciel: D1–D3; układ: decyzja agenta). Zadanie #22.

## TL;DR
Nowy przebieg powstaje na dysku roboczym (T7) jako `<korzeń>/<nazwa>`, a `data/work/<nazwa>` to symlink.
`data/work` zostaje katalogiem na dysku wewnętrznym. Po udanym `verify` `scripts/promote_run.py` kopiuje A
na dysk wewnętrzny i kasuje B oraz kopię A na T7. `export` działa tylko na dysku wewnętrznym.
Stare przebiegi i wydania sprząta `scripts/clean_work.py`; wydania kasuje tylko po „tak” właściciela.

## Kontekst
Para A/B trwa ok. 13 h i zajmuje 2 × 22 GB. Dysk wewnętrzny ma mało miejsca, więc build idzie na T7.
Piny w `config/generator/*-sources.json`, `build_pair.sh` i runbooki używają ścieżek `data/work/...`.
K1–K10 porównują hashe, nie ścieżki. T7 może zniknąć (ADR-015, ADR-018), a wydanie ma mieć kopię
w backupie dysku wewnętrznego.

## Decyzje
- **Układ.** `build --work-root W` tworzy `W/<nazwa>` (`mkdir` bez rodziców) i na końcu symlink
  `data/work/<nazwa>`. Piny i ścieżki w repo bez zmian. `.gitignore` łapie symlinki w `data/work/` i `logs/`.
- **Resztka startu.** Gdy `W/<nazwa>` istnieje bez symlinku, nie ma `build.sqlite`, `reports/` jest pusty,
  a manifest ma same etapy `pending` (albo go nie ma), build kasuje katalog i zaczyna od nowa. Inaczej 4.
- **Granica odtwarzalności to `verify` (D1).** Na T7 leży tylko to, co da się odbudować. Zapieczętowana baza
  zamrożonego przebiegu leży na dysku wewnętrznym; `verify` i `export` nie potrzebują T7.
- **Promocja automatyczna (D3).** Jedno polecenie po `verify`: `promote_run.py --run-dir data/work/<A>
  [--peer data/work/<B>]`. Stany S0–S4, każdy wznawialny. Kopia z kontrolą sha256 i trybu każdego pliku,
  zamiana symlinku na katalog jednym `renamex_np(RENAME_SWAP)`, potem kasowanie B (gdy `INCOMPLETE`
  i zgodny `canonical-index`) i kopii A na T7. Manifest A się nie zmienia, więc pieczęć zostaje ważna.
  Ślad: `promotion.json` w katalogu A (poza pieczęcią i `canonical-index`) i `logs/<A>.promote.log`.
- **`export` odmawia przebiegu na T7** (symlink albo wolumen roboczy): kod 5, „najpierw promote_run.py”.
- **Bez migracji dzisiejszego `data/work` (D2).** `clean_work.py` domyślnie tylko wypisuje (klasy 1–8).
  `--apply` kasuje sam nieudane i porzucone przebiegi na T7 (klasy 5–6). Stare wydanie (klasa 8: bez pinu,
  nie bieżące na serwerze według `NOTICE`, nie ostatnie w rodzinie) znika tylko z
  `--apply --delete-releases PLIK`, gdzie plik zawiera nazwy zaakceptowane przez właściciela.

Odrzucone: symlink całego `data/work` na T7 (lokalne 1A). Wszystkie przebiegi, wydania i piny leżałyby
na T7, a wydanie nie miałoby kopii w backupie. Korzeń tylko z env bez symlinku (1B): zmienia ścieżki pinów.

### Poprawki po weryfikacji #22
- Decyzja właściciela: `clean_work.py` nie kasuje przebiegu na T7, którego
  wszystkie etapy są `complete` (`INCOMPLETE` tylko dlatego, że czeka na verify); klasa 3, powód
  „kompletny, czeka na verify”. Kasowane są tylko przebiegi przerwane albo nieukończone i resztki startu ≥ 24 h.
- Kasowanie drzew (B i kopia A w promocji, wpisy `clean_work.py`) jest wznawialne: najpierw zmiana nazwy na
  `.<nazwa>.deleting` w tym samym katalogu, potem `rmtree`. Ponowienie promocji i `clean_work.py --apply`
  dokańczają takie resztki, więc przerwane kasowanie nie zostawia ~22 GB bez manifestu.

## Otwarte pytania / ryzyka
- Po skasowaniu B ponowny `verify` A (np. nowy przegląd K7) wymaga nowej pary.
- Promocja kopiuje ok. 22 GB na dysk wewnętrzny; brak miejsca daje 78.
- „Bieżące na serwerze” zależy od lokalnego `origin/main` repo serwera (bez `fetch`). Chroni też reguła
  „ostatnie w rodzinie” i osobna zgoda właściciela.
