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
- Pełny zakres stosowania ZDS, łącznie z warunkami pochodzenia haseł, wymaga rozstrzygnięcia opisanego w macierzy. Nie aktualizujemy reguł gry przez odczyt bieżącej witryny.
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
