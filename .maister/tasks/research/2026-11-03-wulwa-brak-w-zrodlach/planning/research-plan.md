# Plan badania: „wulwa” poza SGJP, KWJP i Słowosiecią

## TL;DR
Badanie mieszane, dowody pośrednie. Trzy zbieracze: `local` (frekwencje i pokrycie w cache), `docs` (zasady doboru haseł i skład korpusów), `external` (sgjp.pl, NKJP online, słowniki ogólne, poradnie). Wynik: hipotezy z oceną pewności i rekomendacja dla `sgjp-supplement.tab` oraz STANDARD/BROAD do decyzji użytkownika.

## Kluczowe decyzje
- Typ mieszany: same dane lokalne nie wyjaśnią „dlaczego”; same opisy źródeł nie dadzą liczb.
- Trzy kategorie zamiast domyślnych czterech: konfiguracja to tylko `sgjp-supplement.tab` i `policy.py`, mieści się w `local`.
- Słowosieć: tylko strumieniowy grep po `wordnet_work_4_5.zip` (`unzip -p … | grep`), bez rozpakowywania na dysk.
- Pisownię sprawdzamy w obu wariantach: `wulw*` i `vulv*` (też wielkie litery, bo SGJP ma nazwisko „Wulw”).

## Otwarte pytania / ryzyka
- „Dlaczego” to wniosek z poszlak; autorów nie pytamy.
- Strony sgjp.pl i NKJP online mogą być niedostępne lub zmienione; wtedy zapisujemy brak wyniku, nie zgadujemy.
- Pusty grep to twierdzenie o narzędziu: każde „brak” potwierdzić kontrolą dodatnią (np. „srom”, „wulwodynia”).

## Pytanie
Czemu „wulwa” (srom) jest w SJP.pl z pełną odmianą, a nie ma jej w SGJP (sgjp-20260823), w lematach KWJP i jako lematu w Słowosieci 4.5? Luka, celowe pominięcie, pisownia czy frekwencja?

### Pytania szczegółowe
1. Frekwencja: ile razy „wulwa” (wszystkie formy), „vulva”, „wulwodynia” w KWJP (orth/orth_lc/lemma, wszystkie podkorpusy) i NKJP 1grams? Dla porównania: srom, wagina, pochwa, łechtaczka, penis, prącie, moszna, labia/wargi sromowe.
2. Pokrycie SGJP: które podobne terminy (anatomiczne, łacińskie zapożyczenia medyczne: wagina, łechtaczka, moszna, penis, prącie, klitoris, uterus, cerwiks, wulwodynia, wulwektomia) są w eksporcie, a których brak?
3. Słowosieć 4.5 (pełny zrzut): czy jest „wulwa”/„vulva” w jakiejkolwiek tabeli (lemat, wariant, gloss, przykład)? Co jest przy „wulwodynia” (definicja, synonimy)?
4. IATE: czy jest polski termin „wulwa”/„srom” dla „vulva”?
5. Zasady SGJP: jak dobiera hasła (źródła, próg frekwencji, terminologia specjalistyczna, zapożyczenia)? Czy są udokumentowane?
6. Skład KWJP i NKJP: czy brak w korpusie tłumaczy brak lematu?
7. Zewnętrznie: czy sgjp.pl (wersja online, nowsza) ma „wulwa”? Ile trafień w NKJP online? Które słowniki ogólne ją notują? Co mówią poradnie o „wulwa” vs „vulva”?
8. Precedens w repo: jak dodano „się/siebie” do suplementu i jakie kryteria tam przyjęto?

## Metodologia
- **Główna:** pomiar w danych lokalnych + odczyt opisów źródeł + weryfikacja w źródłach publicznych.
- **Rama analizy:** cztery hipotezy (luka / celowe pominięcie / pisownia / frekwencja); każda dostaje dowody za i przeciw i ocenę pewności.
- **Zapasowo:** gdy sgjp.pl lub NKJP online nie odpowiadają, opieramy się na cache i publikacjach w `cache/constructions`, `cache/sgjp-docs`.
- **Zasady wykonania:** dane surowe tylko do odczytu; Python jako `python3 -I`; pliki pomocnicze w scratchpadzie; każde zero z kontrolą dodatnią; liczby z dokładną ścieżką pliku i poleceniem.

## Fazy
1. **Rozpoznanie:** formaty plików (KWJP CSV: `,freq,ipm,ARF,DP,…`; NKJP `1grams.gz`: `liczba forma`; SGJP `.tab.gz`; sqlite Słowosieci); lista form „wulwa” z `pl-sjp-20260820` / SJP.pl (11 form).
2. **Pomiar:** grep/zliczenia form i lematów w KWJP, NKJP, SGJP, Słowosieci, IATE; tabela porównawcza z terminami kontrolnymi.
3. **Opisy:** zasady doboru haseł SGJP, skład korpusów, zakres Słowosieci; precedens suplementu.
4. **Weryfikacja zewnętrzna i krzyżowa:** sgjp.pl, NKJP online, słowniki ogólne, poradnie; zestawienie z wynikami lokalnymi.

## Strategia zbierania

### Instancje: 3

| # | Kategoria | Zakres | Narzędzia | Prefiks |
|---|-----------|--------|-----------|---------|
| 1 | local | Frekwencje (KWJP, NKJP), pokrycie SGJP terminów porównawczych, pełny zrzut Słowosieci (strumieniowo), IATE, lexicony serwera, `sgjp-supplement.tab` i jego decyzja, `policy.py` | Bash (gzcat, unzip -p, grep, sqlite3, `python3 -I`), Read | local |
| 2 | docs | Zasady doboru haseł SGJP (`cache/sgjp-docs`, `cache/constructions/sgjp-theory.pdf`, publikacje tam cytowane), skład KWJP (`cache/kwjp/article.pdf`, `README.source.md`) i NKJP, zakres Słowosieci (ADR-011), wcześniejsze rozstrzygnięcia braków w SGJP w `docs/` i `.maister/tasks` | Read, Grep, Bash | docs |
| 3 | external | sgjp.pl online (czy jest „wulwa”, nowsze wersje), NKJP online (wulwa/wulwie/vulva), słowniki ogólne poza Wikisłownikiem (SJP PWN, WSJP PAN, SJP.pl, Doroszewski), poradnie (PWN, RJP) o pisowni, użycie medyczne | WebSearch, WebFetch | external |

### Uzasadnienie
Podział według rodzaju dowodu: liczby (`local`), deklarowane zasady (`docs`), stan publiczny i norma (`external`). Kategorie się nie nakładają: `docs` nie liczy frekwencji, `local` nie interpretuje zasad.

### Uwagi dla zbieraczy
- Nie wymieniać gier słownych poza Literaki i Kurnik; nie kontaktować autorów; nie używać Wikisłownika.
- Nie rozpakowywać `wordnet_work_4_5.zip` na dysk; nie zmieniać plików w `cache/`, `config/`, lexiconach.
- Wyniki: `analysis/findings/<prefiks>-*.md`, każdy plik zaczyna się od TL;DR / Kluczowe decyzje / Otwarte pytania.

## Kryteria sukcesu
1. Tabela frekwencji: wulwa (formy), vulva, wulwodynia + terminy kontrolne, z liczbą, plikiem i poleceniem.
2. Tabela pokrycia SGJP dla ≥8 terminów porównawczych (jest / brak, lemat, tagi).
3. Wynik pełnego zrzutu Słowosieci dla wulw*/vulv*, z kontrolą dodatnią.
4. Zasady doboru haseł SGJP zacytowane ze źródłem albo jawne stwierdzenie, że ich nie ma.
5. Cztery hipotezy z oceną pewności (wysoka/średnia/niska).
6. Rekomendacja: dodać / nie dodawać do `sgjp-supplement.tab`, wpływ na STANDARD i BROAD (które formy wejdą, przez które filtry), z przykładami; decyzja należy do użytkownika.

## Oczekiwane wyniki
- `analysis/findings/local-*.md`, `docs-*.md`, `external-*.md`.
- Raport końcowy w `outputs/` z odpowiedzią, hipotezami i rekomendacją.
