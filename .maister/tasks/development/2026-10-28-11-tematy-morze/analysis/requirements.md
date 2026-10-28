# Wymagania (faza 5)

## TL;DR
Pilotaż „morze”: podkomenda `tematy` według wzoru POP00 buduje lokalny pakiet TEMATY w `data/work/` z warstwami T1/T2/T3. Powstaje też raport przecięć z POP i POP00, diagnostyka BROAD/STANDARD oraz próba R2 (90 słów). Operator ocenia słowa na stronie z przyciskami. Wydanie publiczne następuje dopiero po bramce. Wiki dostaje stronę „W przygotowaniu”.

## Kluczowe decyzje
- Wydanie (tarball w releasie GitHub) i pełna strona wiki dopiero po decyzji operatora na bramce.
- R2: artefakt HTML z przyciskami tak/nie/niepewne. Oceny zapisujemy do review JSON w repo, jak przy POP00.
- Pakiet zawiera `MORZE.txt.gz` (formy ∩ STANDARD) i `MORZE.tsv.gz` (leksem, warstwa, źródła, flaga `wieloznaczny`).
- Architektura: potok wsadowy, deterministyczny, bez sieci w budowie. Wzór POP00 wybrano w badaniu, więc części A nie było.

## Opis wejściowy
Ticket #11 i polecenia operatora z 2026-10-28 (zob. `clarifications.md`, `scope-clarifications.md`).

## Pytania i odpowiedzi (2026-10-28)
1. Odbiorca i wydanie: najpierw lokalny pakiet i raport, wydanie po bramce. Odpowiedź: **tak**.
2. Forma R2: strona z przyciskami, wynik w review JSON. Odpowiedź: **tak**.
3. Format: `MORZE.txt.gz` i `MORZE.tsv.gz`, kod według POP00. Odpowiedź: **tak**.

## Wymagania funkcjonalne
1. Krok pobrania, osobny od budowy:
   - IATE TBX 2019 trafia do `cache/iate/`;
   - Słowosieć 4.5 (zip już jest) trafia do `cache/plwordnet/`;
   - zapisujemy URL, datę UTC, sumę SHA-256 i liczbę bajtów.
2. Pochodna Słowosieci w SQLite, bez kolumn `owner` i `comment` i bez logu IP. Powstaje skryptem w repo, deterministycznie.
3. `config/generator/tematy-sources.json` przypina wejścia:
   - run v31 (manifest, `build.sqlite`, `standard.txt`, `broad.txt`);
   - POP pop-v3 i POP00 r2-a;
   - pochodną Słowosieci i plik IATE.
4. Konfiguracja metody `config/generator/tematy.json`:
   - wersja `tematy-v1`, ADR;
   - próba agenta 50 na warstwę i R2 30 na warstwę;
   - progi bramki;
   - lista 37 słów.
5. `config/generator/tematy/morze.json`:
   - T1: `mors.`, `żegl.`, `ryb.`;
   - T2: 6 korzeni, relacje 11, 25 i 27;
   - T3: 4821, jednowyrazowe, typ „term”, niezawodność ≥ 3;
   - bez dodatków.

   Walidacja: zbiór kluczy i typy; nieznane pola odrzucamy.
6. Podkomenda `python3 -m literaki_slownik tematy --manifest --config --topic --output-dir [--json]`:
   - nigdy nie nadpisuje istniejących plików;
   - przed przeniesieniem wyniku na miejsce sprawdza ponownie hashe wszystkich czytanych plików, także plików w pakietach POP i POP00 (zob. błąd f33fe05).
7. Warstwy i pliki:
   - warstwa leksemu to najniższa z T1 < T2 < T3;
   - TSV wymienia wszystkie źródła;
   - flaga `wieloznaczny`;
   - formy ∩ STANDARD.
8. Raport `reports/summary.json` i czytelny `reports/raport.md`:
   - przecięcie z POP i POP00: % względem tematu i liczby bezwzględne, osobno dla każdej warstwy i razem, w leksemach i w formach;
   - diagnostyka kandydatów przed ∩ STANDARD wobec BROAD i STANDARD;
   - kody powodów `BRAK_LEKSEMU`, `POZA_BROAD`, `POZA_STANDARD`, z przykładami odrzuconych słów.
9. Pomiar pokrycia T2: test 37 słów, osobno dla T1, T1∪T2 i całości.
10. Kontrola żeglugi śródlądowej w T3: udział terminów rzecznych i przykłady, opisane w LIMITATIONS.
11. Próby deterministyczne:
    - agent ocenia 50 na warstwę;
    - operator ocenia 30 na warstwę;
    - werdykt progów dalej / popraw / stop.
12. Niezależny checker `scripts/check_tematy_package.py`, wywoływany z `--review`.
13. Dokumenty:
    - ADR-010 i ADR-011;
    - `ATTRIBUTIONS.md` (plWordNet, IATE: „Download IATE, European Union, 2019”);
    - `docs/generator/cli.md`, `raporty.md`, `jakosc.md`;
    - `docs/runbook-wiki.md`, sekcja TEMATY;
    - `.maister/docs/INDEX.md`.
14. Wiki: strona `Slownik-TEMATY` ze statusem „W przygotowaniu” i liczbami z manifestu, plus Home i `_Sidebar` (runbook wiki).
15. Dowód determinizmu: dwie budowy a/b dają identyczne pliki.

## Kod do ponownego użycia
- `pop00.py`: `load_sources`, `check_inputs`, `package_file`, `read_words`, `_write_package`, `build_package`, `confirm_unchanged`.
- `inputs.checked_file`, `canonical.*`, `pop._write_gzip` (upublicznić), `pop.load_forms` i `pop.load_constructions`, `quality.sample_strata` i `review_template`, `run.code_identity`, `export.rename_noreplace`.
- `scripts/check_pop00_package.py`, `tests/pop00_helpers.py`.

## Zasoby wizualne
Brak. To zadanie nie ma interfejsu. Strona R2 jest narzędziem przeglądu, nie częścią produktu.

## Granice zakresu
Poza zakresem:
- kolejne tematy;
- wydanie publiczne przed bramką;
- Wikisłownik;
- LLM;
- kontakt z autorami;
- integracja z botami Literaki.
