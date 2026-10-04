# Audyt KWJP100 — wydanie przypięte i rzeczywiste pliki

## TL;DR

**ALLOWED dla 13 wybranych list na CC BY 4.0**, na podstawie deklaracji obejmującej zasoby repozytorium. Zbadano wszystkie 12 list pojedynczych jednostek (lemma/orth/orth_lc × cały korpus/3 gatunki) oraz kompletną listę bigramów lemma-all. Pozyskano pliki, obliczono SHA256 i wykonano pełne skanowanie CSV. To audyt, nie końcowy słownik dopuszczalności ani model znajomości. [Deklaracja przypiętego wydania](https://github.com/ipipan/kwjp100-varia/blob/26d82bd8b906dfed1cfcf8f903b1650b56daeabf/README.md).

Dwie pułapki wymagają jawnej obsługi: listy reprezentują segmenty, a **IPM ma mianownik zależny od konkretnej opublikowanej listy**. Ponadto lemat nie jest identyfikatorem leksemu SGJP, a brak wiersza nie jest częstością zero. Dowody i pomiary: [statystyki](kwjp-statistics.json), [rejestr plików](kwjp-source-registry.json).

## Key Decisions

- Utrwalić commit `26d82bd8b906dfed1cfcf8f903b1650b56daeabf` z 2026-05-28T10:34:44Z, wszystkie SHA256 i oryginalne CSV. Data commitu nie jest datą wygenerowania list. [Commit źródłowy](https://github.com/ipipan/kwjp100-varia/commit/26d82bd8b906dfed1cfcf8f903b1650b56daeabf).
- Zachować F, IPM, ARF, DP, DP_norm, 1-DP, total_freq; nie zastępować źródłowych wartości miarami wyliczonymi po imporcie. Przechowywać typ jednostki, gatunek, oryginalną wielkość liter i POS, gdy istnieje.
- KWJP dostarcza dowodów użycia i przyszłych rankingów; nie dostarcza nowych leksemów poza zaakceptowaną bazą SGJP.
- `rank_in_file` jest naszym numerem wiersza przy utrwalonej kolejności. Nie udajemy, że plik zawiera kolumnę R, ani nie traktujemy remisu F jako rozstrzygniętego semantycznego rankingu.
- Surowe dane i pełne kopie dokumentacji pozostają w ignorowanym `cache/kwjp/`; raporty, zawiadomienie licencyjne, metadane i skrypt są istotnymi artefaktami repozytorium.

## Open Questions / Risks

1. Nie ustalono dokładnych wersji Hydry, modelu, słownika SGJP użytego do korekty anotacji ani całej historii treningu modeli. Nie deklarujemy niezależności pełnego pochodzenia narzędzi od wszystkich wyłączonych źródeł. To zależności pośrednie anotacji, nie wczytane wejścia generatora.
2. Nie ma w tych plikach wspólnej tabeli forma→lemat→POS. Częstości form nie wolno kopiować jako osobnego pełnego dowodu do każdego pasującego leksemu SGJP.
3. Automatyczne lematy zawierają jednostki nietypowe, skróty i możliwe błędy. Pisownia oraz tag POS same nie rozstrzygają homonimii znaczeniowej.
4. CSV bigramów zawiera `Dice`, przeglądarka i dokumentacja pokazują `logDice`. Nie wprowadzamy zamiennej nazwy. Przeliczenie wymaga osobnej, wersjonowanej reguły i uwzględnienia zaokrągleń; 15 557 opublikowanych wartości Dice=0 nie pozwala bezpośrednio wziąć logarytmu.
5. Zakres reprezentuje redagowaną polszczyznę pisaną, nie pełny przekrój codziennej rozmowy. Wskaźnik użycia nie jest pomiarem znajomości ludzi.

## Pokrycie źródeł i warunki

Sprawdzono wszystkie trzy wymagane punkty startowe: [repozytorium](https://github.com/ipipan/kwjp100-varia), [dokumentację list](https://kwjp.pl/lists/doc/about/) i [przeglądarkę](https://kwjp.pl/lists/). Dodatkowo oficjalny [opis korpusu](https://kwjp.pl/overview), wskazany przez autorów [artykuł 2025](https://jezyk-polski.pl/index.php/jp/article/download/1062/951/3013), [tekst CC BY 4.0](https://creativecommons.org/licenses/by/4.0/legalcode.pl) oraz publiczny JS przeglądarki. Zestaw URL, czasu pobrania i SHA256 dokumentacji jest w [rejestrze dowodów](kwjp-documentation-evidence.json).

Repozytorium ma 48 plików freqlists. Zakres pomiaru to 13 wybranych artefaktów, pokrywających wszystkie warianty słowne oraz format bigramów. Pozostałych 35 plików n-gramowych nie pobierano: nie są potrzebne do pilotażu dopasowania słów w §15; ich rozmiar i format nie są tutaj podawane jako pomiar. Pełny spis drzewa konkretnego commitu zachowano roboczo w `cache/kwjp/tree.json`. Nie pobrano fragmentów pełnych tekstów KWJP½M ani całego korpusu.

[Zawiadomienie licencyjne i atrybucja](kwjp-license-notice.md) oraz [rejestr per artefakt](kwjp-source-registry.json) zawierają zakres licencji, autora/właściciela, użycie, status i obowiązek oznaczenia zmian. Deklaracji CC BY repozytorium nie rozciągamy na pełne teksty wszystkich książek i czasopism korpusu. Pełnego artykułu ani witryny nie redystrybuujemy w repo.

## Zmierzone jednostki i format

Skrypt `scripts/audit_kwjp.py` czyta całe gzip/CSV jako UTF-8. Separator to przecinek, separator dziesiętny kropka. Nagłówki kolumn jednostek są puste. Użycie naiwnego DictReader zgubiłoby pierwszą kolumnę w plikach z dwoma pustymi nagłówkami. Parser nadaje własne, jawne nazwy na podstawie zweryfikowanego rodzaju listy:

- lemma: `lemma,pos,freq,ipm,ARF,DP,DP_norm,1-DP,total_freq`;
- orth i orth_lc: `form,freq,ipm,ARF,DP,DP_norm,1-DP,total_freq`;
- 2grams-lemma: `unit_1,unit_2,freq,ipm,ARF,DP,DP_norm,1-DP,Dice,total_freq` — brak POS obu członów.

Każdy wiersz lemma oznacza parę napisu lematu i POS, a nie zidentyfikowany leksem SGJP. Dla orth jednostką jest zapis segmentu z zachowaniem wielkości liter, dla orth_lc zapis sprowadzony do małych liter; bigram ma dwa kolejne segmenty. Liczba wierszy wyklucza nagłówek. Pełny skan nie znalazł pustych wartości miar, błędnej liczby pól ani wzrostu F między kolejnymi wierszami. [Pliki wydania](https://github.com/ipipan/kwjp100-varia/tree/26d82bd8b906dfed1cfcf8f903b1650b56daeabf/freqlists), [wyniki skanu](kwjp-statistics.json).

| Lista | Wiersze | min F | min total_freq | Wiersze F<5 |
|---|---:|---:|---:|---:|
| `slowa-lemma-all` | 184,917 | 5 | 5 | 0 |
| `slowa-lemma-fakt` | 164,651 | 1 | 5 | 49,474 |
| `slowa-lemma-fikcja` | 134,453 | 1 | 5 | 48,380 |
| `slowa-lemma-publicystyka` | 157,968 | 1 | 5 | 54,167 |
| `slowa-orth-all` | 419,961 | 5 | 5 | 0 |
| `slowa-orth-fakt` | 384,453 | 1 | 5 | 135,319 |
| `slowa-orth-fikcja` | 331,568 | 1 | 5 | 138,049 |
| `slowa-orth-publicystyka` | 366,287 | 1 | 5 | 143,848 |
| `slowa-orth_lc-all` | 360,472 | 5 | 5 | 0 |
| `slowa-orth_lc-fakt` | 331,932 | 1 | 5 | 109,693 |
| `slowa-orth_lc-fikcja` | 287,133 | 1 | 5 | 114,368 |
| `slowa-orth_lc-publicystyka` | 315,420 | 1 | 5 | 120,254 |
| `2grams-lemma-all` | 1,627,126 | 5 | 5 | 0 |

Próg globalny ≥5 potwierdzono we wszystkich 13 plikach. W gatunkach są wartości 1–4; nie wolno filtrować ich ponownie progiem 5. Nie ma opublikowanego F=0. Są rzeczywiste zera miary 1-DP. Autorzy opisują ograniczenie list do co najmniej pięciu wystąpień w całym korpusie, także przy niższych wartościach gatunkowych. [Dokumentacja list](https://kwjp.pl/lists/doc/about/).

### Miary i mianowniki

Suma F opublikowanych wierszy wynosi 81 664 894 (lemma-all), 81 042 800 (orth-all), 81 318 653 (orth_lc-all), 62 690 472 (2grams-lemma-all). Sprawdzono wszystkie wiersze wszystkich 13 pobranych list: `IPM = 1e6 × F / suma_F_listy` jest zgodne z plikiem do zaokrąglenia 0,005. To wynik obliczenia, nie przypisanie autorom opisu algorytmu. Nie należy więc mnożyć IPM przez 100 i nazywać wyniku odzyskaną częstością korpusu. Także dziewięć list gatunkowych przeszło tę kontrolę; ich własne mianowniki zapisano w statystykach.

ARF i 1-DP przechowujemy jako opublikowane wskaźniki rozłożenia wystąpień. `DP_norm` jest inną kolumną: w danych osiąga 1,00013; nie zastępujemy nią DP przy odtwarzaniu 1-DP. Przykład zmierzony: `spacjalny/adj` ma F=151, ARF=1,17, 1-DP=0,00111; odpowiada przykładowi koncentracji w [dokumentacji](https://kwjp.pl/lists/doc/about/). Źródłowe miary są skorelowane — przyszły COMMONNESS powinien uwzględniać rangi/percentyle w tej samej reprezentacji, a nie sumować różne IPM jako niezależne dowody.

### Weryfikacja granic formatu

W lemma-all znaleziono 128 jednostek wykraczających poza litery łacińskie z dywizem, w tym lematy skrótów `na_przykład` (brev, F=23 304) i `tak_zwany` (brev, F=12 214). Są dwie jednostki z odstępem i dwie niezgodne z NFC. Opis zakresu znaków z dokumentacji nie może zastąpić walidacji lematów. W orth-all wszystkie 419 961 napisów przechodzą sprawdzenie liter łacińskich/dywizu. W orth_lc-all trzy jednostki zawierają łączący znak kropki po i, np. `i̇pekçi` (F=6), co jest zgodne z możliwym skutkiem sprowadzenia İ do małych liter; nie usuwamy znaku, by stworzyć inny napis. [Szczegóły i przykłady](kwjp-statistics.json).

## Gatunki, segmentacja i pochodzenie anotacji

Oficjalny opis obejmuje lata 2011–2020, z docelowymi udziałami fikcja 30%, fakt 35%, publicystyka 35%; brak zwykłych tekstów mówionych i społecznościowych ogranicza model codzienności. Fakt obejmuje także publikacje specjalistyczne. [Opis KWJP](https://kwjp.pl/overview).

Artykuł autorów (§3) potwierdza segmentację `czytał+em`, Hydrę do lematyzacji/znakowania i korektę lematów według Morfeusza SGJP. Opisuje również HerBERT i zasoby składniowe PDB/Składnica oraz PolDeepNer2 wytrenowany na NKJP1M dla nazw. Zachowujemy te zależności pośrednie; nie znamy dokładnych modeli i całej historii ich danych. Nie wynika z tego, że każda lista lematów jest bezbłędna, ani że każda zależność pośrednia wpływa bezpośrednio na listę frekwencyjną. [Artykuł autorów, s. 10–14](https://jezyk-polski.pl/index.php/jp/article/download/1062/951/3013).

W 112 576 parach lemma/POS, 279 641 formach orth oraz 244 736 formach orth_lc obecnych we wszystkich trzech listach gatunkowych suma trzech F jest zgodna z F-all (zero rozbieżności w tej grupie). Pozostałe odpowiednio 72 341, 140 320 i 115 736 jednostek nie mają wiersza co najmniej jednego gatunku. Nie podstawiono za te braki zera w kontroli. Braku w gatunku nie opisujemy automatycznie globalnym progiem 5, ponieważ ten sam napis może być opublikowany w all.

## Materiał do pilotażu i obsługa braków

Przykłady są dobrane ilustracyjnie, nie losowo; źródłowe wiersze i wszystkie miary są w `illustrative_query_matches` w statystykach. Pełne listy do łączenia są w `cache/kwjp/kwjp100-slowa-*-all.csv.gz`.

| Przypadek | Pomiar KWJP | Znaczenie dla połączenia |
|---|---|---|
| `kot/subst`, `kotem` | lemma F=6756; orth kotem F=364; orth_lc kotem F=407 | lemat i forma to różne dowody, nie jedna częstość |
| `zamek/subst` | F=5729 | sam lemma+POS nie rozdziela homonimów SGJP |
| `Róża/subst`, `róża/subst` | F=2108 i F=2218 | zachować wielkość liter przed oceną nazwy własnej |
| `Róża`, `róża` w orth | F=1200 i F=163; orth_lc róża F=1373 | forma mała/duża nie koduje pewnej interpretacji znaczeniowej |
| `mam` | orth F=34158; orth_lc F=47750; osobne lemma mam/xxs F=12 i mam/subst F=9 | nie łączyć formy z lematem przez sam napis |
| `czytał`, `em`, `czytałem` | orth F=2429 i F=266200; brak wiersza czytałem | ostatni brak nie oznacza F=0: jednostka może być segmentowana |

Rekomendowane statusy: obecny wiersz→`OBSERVED`; brak porównywalnej jednostki w globalnej liście z ustalonym progiem→`ABSENT_OR_BELOW_PUBLICATION_THRESHOLD`; niepewna tokenizacja albo brak gatunkowy przy innym mechanizmie selekcji→`NOT_IN_PUBLISHED_LIST`; nieustalone mapowanie SGJP→`UNMATCHED`; POS w orth i bigramach→`NOT_APPLICABLE`. Nieudostępnione/niepobrane warianty→`UNAVAILABLE`. Żadnego z tych stanów nie zamieniamy na zero.

Ścieżka łączenia powinna utrzymywać osobne rekordy dowodów KWJP i relację wiele-do-wielu do interpretacji SGJP. NFC oraz casefold/lower muszą być zapisane jako osobne operacje z zachowaniem oryginału; skróty, nazwy i segmenty nie są dowodami dopuszczalności. Pewność dopasowania nie jest pewnością anotacji korpusu.

## Odtworzenie i napotkane ograniczenia dostępu

`python3 scripts/audit_kwjp.py --fetch` pobiera brakujące 13 plików z przypiętego commitu i skanuje całość. Bez `--fetch` obliczenia są lokalne. Kontrola 13/13 obiektów blob Git z drzewem przypiętego commitu przeszła pomyślnie. Opcjonalne istniejące `cache/kwjp/tree.json` pozwala powtórzyć to sprawdzenie; skrypt zawsze porównuje też pobrane dane z utrwalonym SHA256, gdy rejestr już istnieje. Rejestr SHA256 umożliwia kontrolę tych samych bajtów; czasy pobrania nie są wynikiem naukowym i po ponownym pobraniu będą inne. Skrypt nie czyta wejść porównawczych ani niedopuszczonych źródeł.

Pierwszy curl do GitHub API w sandboxie zwrócił DNS `Could not resolve host`; ponowienie z uprawnioną siecią było udane. Próba alternatywnego, niepodanego przez specyfikację adresu `/doc/about/` w web nie powiodła się; oficjalny `/lists/doc/about/` zadziałał. Przeglądarka zwraca strukturę tabeli i warianty, a dane pobiera przez JS; kompletny pomiar oparto na oficjalnych CSV. Webowy viewer PDF zwrócił cache miss, bezpośredni URL pliku z tego viewera zadziałał. Jednorazowy odczyt gzip jeszcze podczas pobierania zgłosił EOF; po zakończeniu transferu pełne skany i weryfikacja gzip zakończyły się pomyślnie. Nie są to blokady źródła. Nie pominięto żadnego z trzech wymaganych punktów startowych.

Nie znaleziono lokalnego specjalisty `.codex/agents` (ustalenie koordynatora). Zrealizowano kontrakt niezależnego zbierającego: źródła pierwotne, rzeczywiste pliki, pomiary, pochodzenie, jawne ograniczenia. Wynik ścieżki KWJP można przekazać do syntezy audytu i pilotażu SGJP; pełnego generatora ani końcowych list nie przygotowano.
