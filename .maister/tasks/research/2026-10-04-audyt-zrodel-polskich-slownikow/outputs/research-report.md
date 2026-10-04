# Audyt źródeł polskich słowników — raport etapu 1

## TL;DR
Audyt potwierdza wykonalność pierwszego generatora na konkretnym eksporcie SGJP z pomocniczym KWJP100.
Zbadano całe wejście SGJP, 13 list KWJP i techniczną zawartość unigramów NKJP.
NKJP pozostaje zablokowany do konstrukcji i dopasowań z powodu nieustalonej wersji warunków CC-BY.
Filtry dają policzone scenariusze, nie zatwierdzone słowniki produkcyjne.

## Key Decisions
- SGJP i KWJP mają udokumentowane warunki użycia dla wskazanych plików; zachowujemy atrybucje.
- Preferujemy pełne formy zapisane w SGJP. Nie dopisujemy wyników mechanicznego łączenia segmentów.
- SJP.pl nie pobrano, benchmarku nie uruchomiono, OSPS nie wykorzystano. Dane wyłączonych źródeł nie są wejściami obliczeń.
- Potwierdzenie formy w korpusie pozostaje odrębne od dopuszczalności i tożsamości leksemu.

## Open Questions / Risks
- Warunki NKJP wymagają oficjalnego doprecyzowania; nie oznacza to niedostępności technicznej ani oceny legalności cudzych zastosowań.
- Mieszane kwalifikatory, pisownia części skrótowców i konstrukcje `bym/przezeń/czytajże` wymagają rozstrzygnięcia przed końcowym generatorem.
- Pomiary mają wysoką pewność dla tych bajtów. Kompletność wszystkich klas fleksji, cała historia anotacji i jakość modelu znajomości nie są dowiedzione.

## Pytanie, metoda i pokrycie

Czy da się zbudować odtwarzalny generator według [specyfikacji v3](../../../../../docs/literaki-niezalezne-slowniki-prompt-v3.md), bez wyłączonych wejść konstrukcyjnych? **Tak, warunkowo**: zbadane SGJP i KWJP wystarczają do rozpoczęcia generatora; część polityki kwalifikowania pozostaje otwarta. To rekomendacja z audytu, nie wynik wdrożenia.

Zastosowano audyt dokumentów pierwotnych, pobranie konkretnych artefaktów, pełne skany, kontrolę identyfikatorów/checksum i ograniczony pilotaż połączeń. Sprawdzono wszystkie osiem punktów startowych §16. Pozostałe n-gramy KWJP służą późniejszym badaniom tematycznym; tutaj wszystkie warianty list słownych i jeden kompletny format bigramów zapewniają pokrycie audytu słów. Źródła opcjonalne §4.4 nie są wejściami tego etapu. [Plan](../planning/research-plan.md), [pokrycie](../planning/sources.md).

## Źródła, wersje i statusy

| Źródło | Konkretne wydanie | Warunki | Status/rola |
|---|---|---|---|
| SGJP tekstowy | plik 20260823, DICT-ID `pl.sgjp.sgjp-2026.08.24` | własna nota BSD-2-Clause | ALLOWED, główne wejście |
| Morfeusz — reguły/kod | morfeusz-src-20260823 | BSD-2-Clause programu, pełna nota w const.cpp | ALLOWED, audyt reguł |
| KWJP100 | commit `26d82bd8b906dfed1cfcf8f903b1650b56daeabf` | CC BY 4.0, deklaracja zasobów repo | ALLOWED, 13 plików |
| NKJP unigramy | 1grams.gz, Last-Modified 2014-12-29 | „CC-BY” bez ustalonej wersji/tekstu | BLOCKED do konstrukcji/pilotażu; zbadany technicznie |
| PoliMorf | dokumentacja, bez danych | decyzja metodologiczna §3.1 | BLOCKED jako wejście; dokumentacja odczytana |
| Pełna baza internetowa SGJP/WSJP, OSPS | nie pozyskiwano | nie badano warunków danych | poza zakresem |

Wewnętrzny identyfikator SGJP różni się dniem od ścieżki dystrybucji. Zachowujemy oba, bez „naprawiania” metadanych. Licencję eksportu potwierdza jego własny nagłówek, z pełną listą siedmiu autorów. [Źródło SGJP](https://download.sgjp.pl/morfeusz/20260823/sgjp-20260823.tab.gz), [licencja programu](https://morfeusz.sgjp.pl/doc/license/en), [deklaracja KWJP](https://github.com/ipipan/kwjp100-varia/blob/26d82bd8b906dfed1cfcf8f903b1650b56daeabf/README.md), [dystrybucja NKJP](https://zil.ipipan.waw.pl/NKJPNGrams).

Rejestry dokładnych URL, czasu, SHA256, warunków i zakresu: [SGJP](../analysis/findings/sgjp-source.json), [reguły](../analysis/findings/sgjp-rules-sources.json), [KWJP](../analysis/findings/kwjp-source-registry.json), [NKJP](../analysis/findings/nkjp-sources.json), [PoliMorf](../analysis/findings/polimorf-sources.json), [dodatkowe źródła](../analysis/findings/supplementary-sources.json). Dane surowe pozostają poza Git; manifesty i pomiary są wersjonowane.

## SGJP: format i rzeczywiste statystyki

UTF-8, 5 kolumn rozdzielanych U+0009: forma, identyfikator lematu, tag, nazwa, kwalifikatory. Wszystkie rekordy mają 5 pól. Eksport nie grupuje zawsze identycznych form obok siebie; skrypt wykonuje kontrolowane sortowanie, zanim deduplikuje. Surowy lemat z sufiksem homonimii pozostaje niezmieniony. [Pomiar](../analysis/findings/sgjp-stats.json), [opis źródłowy formatu i ograniczeń](../analysis/findings/sgjp-rules.md).

| Jednostka | Wynik |
|---|---:|
| Rekordy danych po nagłówku | 7 458 520 |
| Unikalne pięciopolowe interpretacje skompresowane | 7 458 520 |
| Suma rozwiniętych alternatyw kategorii tagów | 17 234 910 |
| Identyfikatory lematu wraz z homonimią | 387 398 |
| Oryginalne zapisy form | 5 028 852 |
| Klucze po NFC i lower, przed filtrami | 4 934 967 |
| Zapisy zmienione przez NFC | 0 |

Alternatywy tagu nie oznaczają osobnych znaczeń. Liczba identyfikatorów lematu jest operacyjnym przybliżeniem leksemów, nie odczytem wewnętrznych ID internetowej bazy. Zapis `formy` obejmuje też nazwy, skróty i segmenty; nie oznacza tylu słów dopuszczalnych w grze.

Pełne rozkłady POS, nazw,121 wydzielonych etykiet kwalifikatorowych, surowych kombinacji, długości i znaków są w JSON. Największe klasy: subst 2 570 867, adj 1 614 767, ppas 728 606, praet 598 102, ger 534 042, cond 448 392. Jednostką tych rozkładów jest unikalny rekord interpretacji. Znaki i długości policzono po unikalnych oryginalnych formach, nie ważono częstością korpusu.

## Kwalifikatory i homonimia

| Etykieta | Znaczenie / odczyt | Interpretacje | Klucze | ID lematów |
|---|---|---:|---:|---:|
| daw. | dawne | 405 495 | 308 543 | 13 010 |
| przest. | przestarzałe | 186 666 | 143 109 | 5 746 |
| arch. | archaiczne | 5 186 | 5 123 | 5 186 |
| hist. | historyczne; nie automatycznie archaiczne | 4 226 | 3 478 | 307 |
| rzad. | rzadkie | 189 386 | 149 012 | 5 095 |
| pot. | potoczne | 70 433 | 56 368 | 2 489 |
| wulg. | wulgarne | 14 051 | 11 216 | 224 |
| reg. | regionalne | 7 827 | 6 217 | 203 |
| char. | forma charakterystyczna | 7 380 | 7 212 | 7 378 |
| hom. | forma homonimiczna | 7 377 | 7 209 | 7 376 |
| niepopr. | niepoprawne | 3 156 | 1 714 | 1 398 |

Znaczenia prostych skrótów potwierdza [oficjalny wykaz oznaczeń SGJP](https://sgjp.pl/oznaczenia/). Liczby pochodzą z badanego eksportu. Dla inwentaryzacji dzielimy złożone etykiety po przecinkach i kreskach; nie jest to dowód semantyki ich łączenia. Kategorie nakładają się, zatem nie wolno sumować ich liczebności. `daw._dziś_gwar.` nie jest w scenariuszu tożsame z `daw.`; `hist.` nie jest automatycznie archaizmem. Rzadkość, fachowość, regionalność, potoczność i wulgarność same nie odrzucają wpisu.

Przykłady rzeczywiste: `Róża` jest nazwą, ale klucz `róża` pozostaje dzięki pospolitej interpretacji; `em` ma aglutynant i rzeczownik; `biało` ma interpretację zależną i przysłówkową. Nie łączymy pospolitości jednej interpretacji ze współczesnością innej. Przykłady i surowe rekordy są w polach `pilot_sgjp` i `rescued_examples` pomiaru oraz raporcie reguł.

## Filtry BROAD/STANDARD: policzony scenariusz

Konfiguracja [audit-policy.json](../../../../../config/audit-policy.json): 32 litery PL, NFC/lower, 2–15 znaków, bez kasowania znaków. [Pochodzenie parametrów gry](../analysis/findings/game-policy.md). **Poniższe wyniki to scenariusz przesiewu bez rekonstrukcji, nie zamrożone LL-PL-BROAD/STANDARD.** W szczególności wielkie litery i mieszane oznaczenia kierują do oceny; ich wykluczenie w obliczeniu pokazuje koszt ostrożnego wariantu, nie ostateczną decyzję językową.

| Filtr, kolejność | Odrzucone interpretacje osobno | Utracone klucze osobno | Interpretacje utracone w kroku | Klucze utracone w kroku | Klucze po kroku |
|---|---:|---:|---:|---:|---:|
| znaki | 17 803 | 12 854 | 17 803 | 12 854 | 4 922 113 |
| dlugosc | 1 249 747 | 847 314 | 1 248 007 | 846 273 | 4 075 840 |
| nazwa_wlasna | 1 107 941 | 622 711 | 1 096 762 | 613 218 | 3 462 622 |
| skrot | 449 | 221 | 343 | 211 | 3 462 411 |
| segment_do_oceny | 49 709 | 35 969 | 47 490 | 34 481 | 3 427 930 |
| wielka_litera_do_oceny | 1 119 861 | 630 329 | 8 758 | 5 648 | 3 422 282 |
| mieszane_oznaczenia_do_oceny | 12 891 | 3 161 | 1 070 | 823 | 3 421 459 |
| niepoprawnosc | 3 156 | 1 618 | 2 786 | 1 422 | 3 420 037 |
| historycznosc | 595 972 | 424 518 | 523 835 | 376 930 | 3 043 107 |

Po wszystkich filtrach poza historycznością: **3 420 037 kluczy**. Po dołączeniu scenariusza `daw./przest./arch.`: **3 043 107 kluczy**, różnica 376 930. Sprawdzono relację drugiego zbioru do pierwszego. Nie sumujemy efektów samodzielnych; pełne kombinacje odrzuceń są w `filter_overlaps`.

Uzasadnienia: znaki/długość to ograniczenia eksportu; nazwa własna i brev są kategoriami wyłączonymi specyfikacją; niesamodzielność wynika z POS i konkretnych reguł lemat+tag. `niepopr.` dotyczy poprawności, nie obyczajowej oceny słowa. `niezal.` nie jest automatycznie utożsamione z niepoprawnością. Przypadki z `|` pozostają do oceny bez zgadywania, która etykieta dotyczy którego znaczenia. Bieżący eksport nie ma POS dig/romandig/sym/ign; przyszły import nie może ich milcząco akceptować, gdy pojawią się w nowym wydaniu.

## Pełne słowa, segmenty i plan fleksji

**Preferować pełne formy z eksportu.** Dla osobowych praet/cond sprawdzono 896 798 trójek; kontrolne domknięcie składników objęło wszystkie, lecz utworzyło dodatkowe 120 trójek. Nie dopisano ich. Prawdopodobną przyczyną jest pominięcie ograniczeń paradygmatów; nie ogłaszamy tych różnic brakami źródła.

`czytałem` i `czytałbym` są zapisane wprost; `gniotł` z agl jest częścią zależną. `adjp/frag` nie są automatycznie wykluczane: ograniczenie składniowe nie dowodzi braku samodzielności ortograficznej. Reguła `ń` ma inną kompresję tagu w programie i bieżącym eksporcie; skrypt uwzględnia oba rzeczywiste rekordy. [Dowody, cztery odpowiedzi §5, reguły i próba](../analysis/findings/sgjp-rules.md).

Pozostają konstrukcje kilku leksemów, np. przyimek+ń lub partykuła+końcówka. Rekomendujemy osobną listę zatwierdzonych reguł i decyzję o ich zakresie, bez uruchamiania całej produktywnej segmentacji analizatora. Każda ewentualna rekonstrukcja musi mieć składniki, lematy, regułę i wersję kodu. Pełnej kompletności wszystkich klas nie dowiedziono.

## KWJP: dowód użycia ma własną jednostkę

Zbadano 12 list słownych (lemma/orth/orth_lc × all/fakt/fikcja/publicystyka) oraz 1 listę bigramów lemma. Główne listy: 184 917 par lemma/POS, 419 961 zapisów orth, 360 472 zapisów orth_lc, 1 627 126 bigramów. Progi: F-all≥5, F-gatunek≥1 przy total_freq≥5. Ranga nie jest osobną kolumną; w CSV są puste nagłówki jednostek wymagające jawnego parsera. Wszystkie 13 plików sprawdzono względem blobów przypiętego commitu. [Audyt i pomiary](../analysis/findings/kwjp-findings.md).

**IPM nie ma jednego mianownika 100 mln.** We wszystkich badanych plikach F/suma opublikowanego F×1 mln daje IPM z dokładnością zaokrąglenia. Zachowujemy źródłowe wartości i mianownik reprezentacji. Nie sumujemy IPM, ARF ani dyspersji, nie dodajemy all do gatunków. Dice w CSV bigramów to inna zapisana miara niż logDice widoczne w interfejsie.

Korpus obejmuje redagowane teksty 2011–2020; nie reprezentuje całej codziennej rozmowy. Dokumentacja anotacji wskazuje Hydrę i korektę lematów przez Morfeusz SGJP, a także dalsze zależności modeli. Dokładne wersje i cała historia treningu pozostają nieustalone. Nie nazywamy dowodów KWJP/NKJP niezależnymi statystycznie. [Dokumentacja](https://kwjp.pl/lists/doc/about/), [opis korpusu](https://kwjp.pl/overview), [artykuł autorów](https://jezyk-polski.pl/index.php/jp/article/download/1062/951/3013).

## NKJP: pomiar techniczny i blokada użycia

Zbadano 5 364 398 rekordów, suma F 246 153 378, minimum 1. Plik ma częstość **przed** tokenem, wyrównaną spacjami do 7 znaków, bez nagłówka. Aż 3 892 305 zapisów zawiera interpunkcję; 52 zmienia NFC. Nie usuwamy interpunkcji w celu dopasowania do słowa. Suma F nie pokrywa się z opisywanym korpusem 300M; przyczyna nieustalona.

Nie ustalono wersji CC-BY i tekstu warunków konkretnego pliku po inspekcji oficjalnej strony, załączników i metadanych. Dlatego dane nie weszły do pilotażu łączenia, rankingów ani konstrukcji. Publicznie są nasze agregaty techniczne, nie lista źródłowa. [Audyt, dostępność i wpływ blokady](../analysis/findings/nkjp-audit.md).

## Pilotaż dopasowania i braków

Jawny dobór 13 form i 12 napisów lematów, bez roszczenia reprezentatywności. Połączenie lemma/POS dało 37 zgodnych kandydatów, 2 niejednoznaczne i 25 niedopasowanych jednostek. To liczby wierszy pilotażu, nie estymacja całego korpusu. [Skrypt](../../../../../scripts/pilot_links.py), [pełne wyniki](../analysis/findings/pilot-links.json).

| Przypadek | Wynik | Co zachowujemy |
|---|---|---|
| zamek/subst | dwa ID SGJP: ~a i ~u | jeden dowód KWJP F 5729, lista kandydatów; bez podziału F |
| kot/subst | kot:Sm1 i kot:Sm2 | zgodność napisu+POS nadal niejednoznaczna |
| róża/Róża | osobne orth, jedna scalona orth_lc | brak osobnej wielkiej formy w orth_lc to UNMATCHED, nie brak użycia |
| czytałem/czytałbym | pełne formy SGJP; brak dokładnego wpisu formy KWJP | UNMATCHED wobec segmentacji, nie F0 |
| nietypowe POS przy być/mieć/dwa | część bez zgodnego ID+POS SGJP | UNMATCHED, bez wymuszonego mapowania |
| NKJP przy każdym przykładzie | źródło zablokowane | UNAVAILABLE + powód |

`EXACT_LEMMA_POS_CANDIDATE` nie gwarantuje znaczenia ani bezbłędnej anotacji. Dopiero projektowane EvidenceLink wiąże dowody. Częstość pozostaje przy jednostce korpusowej. Brak z listy można oznaczyć ABSENT_OR_BELOW_PUBLICATION_THRESHOLD dopiero po sprawdzeniu porównywalności; w pilotażu nie wymuszamy tego statusu tam, gdzie pozostaje niepewność.

## Model i odtwarzalność

[Projekt modelu i procesu](../analysis/findings/model-procesu.md) zawiera 11 encji, relacje, obsługę braków, schemat manifestu i kontrole pierwszego generatora. Proponuje prostą bazę SQLite z porcjowanym importem; wydajności bazy jeszcze nie zmierzono. Surowe dane, normalizacja, interpretacja i decyzja pozostają rozdzielone. Izolacja przyszłego benchmarku jest wymaganiem architektury, nie wykonaną integracją.

[Instrukcja odtworzenia](../../../../../docs/odtwarzanie-audytu.md) wskazuje pobieranie przypiętych danych, skrypty i testy. [Manifest audytu](audit-manifest.json) wiąże skrypty, konfigurację i wyniki checksumami. Nota SGJP i atrybucja KWJP są częścią pakietu. Licencja przyszłego kodu/danych projektu nie została wybrana przez sam fakt publicznego repozytorium.

## Ocena pewności, ograniczenia i następny etap

Wysoka pewność: bajty, formaty, liczebności i efekty wskazanego scenariusza. Umiarkowana: projekt filtrów, mapowania i architektury. Nieustalone: pełna semantyka mieszanych kwalifikatorów, wszystkie konstrukcje ortograficzne, pełna historia źródeł/anotacji i NKJP do wykorzystania konstrukcyjnego. Nie przeprowadzono badania ludzkiej znajomości słów, nie wygenerowano końcowych słowników, nie uruchomiono benchmarku ani modeli tematycznych.

Następny etap powinien: (1) rozstrzygnąć konstrukcje z partykułami i politykę skrótowców/mieszanych etykiet; (2) wyjaśnić NKJP albo jawnie wydać pierwszy generator bez niego; (3) zaimplementować import/model/decyzje i wyjaśnienia; (4) zatwierdzić próbki oraz właściwości; (5) zamrozić kandydatów. Dopiero później osobno benchmark SJP.pl. Nie zmienia to słownika działającej gry.

## Pokrycie dziesięciu wymagań §15

| Punkt | Wynik | Dowód / ograniczenie |
|---|---|---|
|1 SGJP/reguły|wykonano|eksport, źródła programu, PDF i licencje; nie kompilowano silnika|
|2 KWJP/NKJP|wykonano audyt|NKJP BLOCKED do użycia; technicznie dostępny|
|3 rejestr/hash|wykonano|rejestry wszystkich użytych plików i dokumentów|
|4 struktura|wykonano|pełne skany danych, różnice względem opisów|
|5 statystyki SGJP|wykonano|definicje jednostek, pełny JSON; ID lematu jako proxy leksemu|
|6 słowa/segmenty/fleksja|wykonano analizę i plan|praet/cond sprawdzone; pełna kompletność innych klas niewykazana|
|7 filtry|wykonano projekt i wpływy|wyniki scenariuszy, przypadki nierozstrzygnięte ujawnione|
|8 pilotaż|wykonano SGJP/KWJP|NKJP niewykonany z powodu nieustalonych warunków; brak zastąpienia zerami|
|9 model/manifest|wykonano projekt|nie produkcyjna baza ani generator|
|10 ograniczenia i zalecenia|wykonano|raport i zakres następnego etapu|

Status: materiał do obowiązkowego przeglądu fazy badawczej Maister. Zatwierdzenie raportu nie oznacza przyjęcia wszystkich scenariuszy filtrów jako finalnej polityki.
