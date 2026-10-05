# Kontrola fleksji i konstrukcji

## TL;DR
Nadgeneracja historycznej próby została wyjaśniona, nie dopisujemy 120 form.
Siedem niespójnych tagów winien nie oznacza brakujących napisów.
Macierz rozdziela poprawność językową, dopuszczalność gry i kompletność dowodów.

## Key Decisions
- Pełne rekordy źródłowe są preferowane; surowych tagów nie poprawiamy w importerze.
- Przy konstrukcji zachowujemy wszystkie składniki i ich kwalifikację. Odrzucenie jednej analizy nie usuwa homonimów.
- Nie uruchamiamy trybu permissive ani produktywnego tworzenia nowych leksemów.

## Open Questions / Risks
- Całe kontrakcje przyimkowe potrzebują niezależnego poświadczenia wymaganego dla gry; sama reguła składania go nie daje.
- Warunki konstrukcji odnosimy do udokumentowanych zasad gry, bez automatycznego przejmowania redakcyjnej polityki źródeł SJP.pl. Zob. [sprostowanie](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/source-policy-clarification.md). Nie aktualizujemy reguł gry przez odczyt bieżącej witryny.
- Lista hostów mobilnych zakończeń wymaga dowodu morfemu, nie tylko końcowych liter.

## Fleksja
[Teoria SGJP](https://sgjp.pl/static/pdf/Podstawy_teoretyczne_SGJP.pdf), §6.6.2, opisuje ograniczone paradygmaty czasowników niewłaściwych. Pełny odczyt 30 leksemów wykazał po pięć analiz, bez osobowych form 1./2. osoby. Mechaniczna próba dopisała po cztery nieuprawnione trójki: razem 120. Dane i pełne paradygmaty są w `analysis/evidence/closure-*.json` aktywnego zadania; koordynator porównał wszystkie 150 rekordów z bazą.

W siedmiu leksemach winien źródłowe formy z zakończeniem `-śmy` mają tag `sec`. Tabele SGJP §6.6.1 i §6.4.1 potwierdzają osobę pierwszą. Kontrola daje 105 oczekiwanych i 105 źródłowych osobowych trójek, z siedmioma różnicami tagów po obu stronach. Wpływ na obecność napisów: zero. Przyszły explain ma pokazać surowy tag i osobne, jawne erratum; nie ukrywać poprawki w imporcie.

## Macierz konstrukcji
Warunki techniczne opierają się na przypiętym `segmenty.dat` Morfeusza 20260823; rejestr dowodów zawiera hash.

| Klasa | Kontrola źródłowa | Status |
|---|---|---|
| operator by + aglt | właściwy składnik, osoba/liczba, nwok | potwierdzona klasa, cztery kombinacje |
| rozkaźnik + partykuła | osobowy impt, zakończenie i wokaliczność | 92 622 interpretacje; zero wyjątków zakończeń |
| przyimek + ń | dozwolony wariant, przecięcie gen/acc | 27 analiz / 26 napisów; growe poświadczenia niekompletne |
| podwojona partykuła | oddzielna analiza konstrukcji | językowo możliwa; growo wykluczona |
| mobilne zakończenie | konkretna klasa hosta i morfem | macierz hostów nieukończona; brak automatycznej reguły endswith |
| inne produktywne ścieżki | tworzenie nowych leksemów / permissive | poza zatwierdzonym zakresem |

Przypadki rozdzielające pochodzą z danych SGJP: `jam` ma niezależną analizę od jama i frag; `żeż` jest także rozkaźnikiem od żec; `doń` także formą od donia. Nie odrzucamy całego napisu przez niedopuszczalną analizę konstrukcyjną. Przesiew hostów zwrócił `niby`, choć nie dowodzi on dołączalnego morfemu. Nie generujemy mechanicznie `nibym`.

## Zaimplementowane konstruktory

`literaki_slownik.constructions` tworzy kandydatów dla rozkaźnika z jedną partykułą i źródłowego `by` (comp/part) z czterema końcówkami aglt nwok. Każdy wynik zachowuje pełne składniki, ID homonimów i źródłowe kwalifikatory. Nie tworzymy podwojonej partykuły ani nie zgadujemy hosta po końcowych literach. Nieznana klasa lub niezgodne zakończenie daje błąd pokrycia. Kandydaci nie są jeszcze integrowani z build ani kwalifikowani do list.

Pełny runtime: 92 622 źródłowe rekordy impt → 93 438 rozwiniętych analiz, 91 104 różne napisy; 4 100 napisów odpada już w profilu alfabetu/długości. To nie końcowa delta listy. Dwa źródłowe by × cztery aglt dają osiem analiz czterech napisów. [Raport](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/approved-rules-runtime.json).

## Źródła społecznościowe — bieżąca faza

Wikisłownik i podobne źródła społecznościowe odkładamy na później. W bieżącej fazie nie używamy ich do budowy słownika ani rozstrzygania dopuszczalności. Zachowujemy przypięte dane SGJP i KWJP oraz ich odrębne role; KWJP nie jest dowodem poprawności konstrukcji. Brakujące poświadczenia pozostają unresolved — nie oznaczają odrzucenia formy i nie pozwalają deklarować pełnego wydania. Dotychczasowe audyty pozostają materiałem historycznym, bez aktywacji ich danych.

## Konstrukcje w explain

Explain odtwarza tylko potwierdzone klasy na podstawie pełnych interpretacji w istniejącym imporcie. Sufiks zapytania służy odnalezieniu możliwego źródłowego rozkaźnika; konstruktor musi potwierdzić klasę, zakończenie i dokładny wynik. By + aglt wymaga dokładnego by oraz właściwej nwok końcówki. Nie tworzy nibym ani mechanicznego czytajżeż.

Pole derivations zawiera regułę, rozwinięty tag, pełne składniki i etykiety oraz diagnostyczną ocenę obu wariantów. Source_presence i source_aggregation nadal dotyczą tylko bezpośredniego importu SGJP; brak bezpośredniego wpisu nie zaprzecza istnieniu kandydata. Kandydat pozostaje candidate_not_qualified, list_membership unresolved. Pełna macierz i końcowe decyzje pozostają otwarte; zapis dwóch klas w build dodano w kolejnym kroku.

Warunek kontekstu A nie obejmuje `pisane_łącznie_z_przyimkiem`: źródłowe ń pozostaje niesamodzielnym składnikiem. Nie zezwala na automatyczne tworzenie niepoświadczonych kontrakcji.

## Zapis potwierdzonych kandydatów w bazie

Nowe build utrwalają impt + jedną partykułę oraz źródłowe by + nwok aglt. Tabela `derivation_candidate` przechowuje oryginał, klucz wyszukiwania, pełny lemat, rozwinięty tag, etykiety i kanoniczny JSON śladu. `candidate_key` jest SHA256 tego JSON; nie zależy od technicznego ID wiersza SQLite. Inne analizy, tagi lub składniki zachowują odrębne ślady nawet wtedy, gdy wynikowy napis jest taki sam.

Tabela `derivation_component` wiąże każdy składnik źródłowy kluczem obcym z surowym rekordem SGJP. Partykuła gramatyczna ma jawny kind i nie udaje wpisu słownikowego. Kandydat i jego składniki zapisują się w jednej porcji; po błędzie mogą pozostać wcześniejsze porcje, lecz etap jest failed, a gotowość INCOMPLETE. Ponowne wyliczenie tego samego zestawu nie dubluje śladów. Nie dubluje też ani nie usuwa bezpośrednich wpisów w interpretation.

Kandydaci mają wyłącznie `candidate_not_qualified`. W `reports/construction-candidates.json` znajduje się rozliczenie potwierdzonego podzbioru. Pełny etap constructions pozostaje pending, ponieważ inne klasy i kwalifikacja nadal wymagają wykonania.

Explain nadal odtwarza potwierdzone konstrukcje z rzeczywistych składników, a `persisted_candidate_key` wskazuje odpowiadający im zapis, jeśli istnieje. Dla starych baz bez tych tabel pole jest null; odczyt nie wymaga migracji ani modyfikacji wcześniejszego przebiegu. To odnośnik do śladu, nie finalna ocena dopuszczalności.
