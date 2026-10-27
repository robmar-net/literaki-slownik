# Rodziny słowotwórcze w SGJP i Morfeuszu: czy poszerzą rdzeń?

## TL;DR
- SGJP w Kuźni ma odsyłacze słowotwórcze, ale nasz eksport tab ich nie zawiera. Używa ich tylko do doklejenia imiesłowów, odsłowników i stopnia wyższego pod lemat.
- Morfeusz też nie podaje rodzin wyrazów. Prawdziwej rodziny nie da się więc zmierzyć na danych lokalnych.
- Zastępczo: rodzina „po wspólnym początku lematu”. Odzysk oczywistych słów: 0–1 na temat. Precyzja próbki: matematyka ~11/30, morze ~1/30, rolnictwo ~2/30.
- Nawet pełne odsyłacze dałyby głównie przymiotnik → `-ość`/przysłówek i pary aspektowe. Nie dodają słów podstawowych tematu (`kotwica`, `pług`, `ułamek`).

## Key Decisions
- Nie pobierałem bazy Kuźni. Runda 1: pełnej bazy SGJP nie pozyskano, a prompt v3 (w. 149) nie dopuszcza jej bez ustalenia uprawnień.
- Miara zastępcza: lemat SGJP zaczyna się od rdzenia leksemu minus 2 lub 3 ostatnie litery (rdzeń ≥5 liter), najwyżej 6 liter dłuższy. Tylko jako górna granica tego, co da rodzina.

## Open Questions / Risks
- Czy dump Kuźni z tabelą `odsylacze` jest publiczny i na jakiej licencji — nie sprawdzone.
- Precyzja z próbki 30, jeden oceniający.

## Dowody: co jest w danych
- `cache/sgjp-docs/kuznia-models-61daf78.py:960-983` — typy odsyłaczy, m.in. `adjosc` (przymiotnik → `-ość`), `adjadv`, `adjsubst`, `masfem`, `asp`, `verger`, `zdrobod`, `zgrubod`; model `CrossReference` w. 1025-1032.
- `cache/sgjp-docs/lexeme_export.py:110-112` — eksport używa tylko `comadv, comadj, gerver, pactver, ppasver`; w. 315 łączy je przez `odsylacze` jako formy „zagnieżdżone” pod leksemem bazowym. Np. w eksporcie `oranie` ma lemat `orać`; `żeglarstwo` i `morski` to osobne leksemy bez powiązania.
- `cache/sgjp-docs/instrukcja.html` (sekcja „Odsyłacze”): „najregularniejsze derywaty … czasowniki o przeciwnym aspekcie …, imiesłowy … i rzeczowniki odsłowne …; przysłówki i rzeczownikowe nazwy cech na -ość …; przymiotniki w stopniu wyższym”. Też: „Zamieszczanie w słowniku odsyłaczy nie jest poddane ścisłym rygorom”.
- Morfeusz (`cache/sgjp-docs/Morfeusz/`): w kodzie brak słowotwórstwa (`grep -i deriv` trafia tylko w `Font.deriveFont`). Analiza daje formę, lemat, tag i kwalifikatory.

## Pomiar zastępczy (`deriv.py`)
Skrypt: `/private/tmp/claude-501/-Users-robmar-Projects-Literaki/7eed58b5-7e1f-4a3f-8359-d9bc24330c2b/scratchpad/metody/deriv.py` → `deriv-results.json`. Rdzeń bez homonimów (jak w `wide-metody-zalazki-kwjp.md`).

| Temat | Rdzeń | Cięcie | Kandydaci | Odzysk testu | Precyzja próbki 30 |
|---|---:|---:|---:|---|---|
| Morze | 232 | 2 | 223 | 0/28 | ~1/30 (`armatorski`) |
| Morze | 232 | 3 | 336 | 1/28 (`pokład`) | niska |
| Rolnictwo | 80 | 2 | 195 | 0/35 | ~2/30 (`pograbić`, `niedojarkowy`) |
| Rolnictwo | 80 | 3 | 411 | 0/35 | niska |
| Matematyka | 59 | 2 | 118 | 1/27 (`dzielenie`) | ~11/30 (`dwumianowy`, `algorytmizacja`, `mnożnikowy`, `czworościenny`, `iloczynowy` …) |
| Matematyka | 59 | 3 | 168 | 1/27 | podobna (`sinusoidalny`, `trygonometryczność`, `całkowalny`, `kwadratura`) |

Szum: wspólny początek łączy obce słowa (`bandera` → `banderia`, `banderówka`; `dzielna` → `dzielnica`; `węgierka` → `węgierszczyzna`).

## Wniosek
Rodzina słowotwórcza poszerza rdzeń „w dół” (pochodne terminów fachowych), a nie „w bok” (słowa podstawowe tematu). Dla matematyki daje sensowne pochodne przymiotniki i nazwy cech. Dla morza i rolnictwa prawie nic. Na danych lokalnych wiarygodnej rodziny nie ma; byłaby potrzebna tabela odsyłaczy Kuźni.
