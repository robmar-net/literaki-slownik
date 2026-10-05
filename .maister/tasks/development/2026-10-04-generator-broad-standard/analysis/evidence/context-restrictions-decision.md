# Poprawna forma z wymaganiem kontekstu — decyzja

## TL;DR
Wybrana forma może być poprawna w określonym otoczeniu składniowym; to inna sytuacja niż niesamodzielny morfem.
W przypiętym SGJP trzy rodziny oznaczeń kontekstu obejmują 169 rekordów, 84 napisy i 24 pełne ID leksemów.
Nie włączono reguły domyślnej akceptacji ani odmowy tych etykiet; wybór dotyczy samego wymagania kontekstu.

## Key Decisions
- Oceniamy jedną konkretną analizę i zachowujemy jej wymagania; nie łączymy warunków różnych homonimów.
- `z_D.` opisuje składnię, nie pochodzenie słownikowe; `fraz.` wskazuje użycie frazeologiczne; `po_liczebniku` określa otoczenie.
- Składnik `ń` oznaczony jako pisany łącznie z przyimkiem nie jest samodzielnym słowem; tej klasy nie obejmuje proponowany warunek niewykluczający.
- Nie zmieniamy zasad gry i nie aktywujemy danych Wikisłownika.

## Open Questions / Risks
- Czy poprawność źródłowej formy w określonym kontekście wystarcza, by sam kontekst nie wykluczał jej analizy, czy każdy taki przypadek wymaga indywidualnego przeglądu?
- A nie nadaje całemu słowu accept; dawność, niepoprawność, kategoria, ortografia, gra i profil nadal są osobnymi warunkami.
- Wpływ końcowy zależy od innych analiz i przyszłych konstrukcji; liczby poniżej nie są deltą list wydania.

## Rzeczywiste dane i dowody

[Runtime](descriptive-derivation-runtime.json) rozlicza wszystkie 7 458 520 rekordów. `procenta` leksemu procent ma źródłowy dopełniacz z etykietą po_liczebniku. Nominalna analiza `coś` ma z_D.; opis dotyczy dołączanego określenia przymiotnikowego w dopełniaczu. Stopień wyższy `brzemienniejszy` ma analizę z fraz., czyli zaznaczonym kontekstem frazeologicznym. Nie tworzymy tych form; występują w dopuszczonym eksporcie.

[Teoria SGJP](https://sgjp.pl/static/pdf/Podstawy_teoretyczne_SGJP.pdf), §3.4.1, s.52, objaśnia nietypowe wymagania składniowe mianownika/biernika zaimków typu CO. [Oznaczenia](https://sgjp.pl/oznaczenia/) rozróżniają opis frazeologiczny od oceny niepoprawności. Etykiety po liczebniku i z D. zostały potwierdzone w wcześniejszym audycie metadanych; nie traktujemy strony online jako źródła nowych leksemów ani aktualizacji przypiętego eksportu.

| Rodzina | Rekordy ekspozycji |
|---|---:|
| fraz. | 128 |
| po_liczebniku | 15 |
| z_D. | 26 |
| Razem | 169 |

Oddzielne pisane_łącznie_z_przyimkiem dotyczy tylko dwóch analiz ń. Nie przepisujemy go na samodzielne słowo; poprawność całej kontrakcji nadal wymaga odrębnych warunków.

## Warianty przed wdrożeniem

**A — rekomendowany:** samo wymaganie składniowego lub frazeologicznego kontekstu nie odrzuca udokumentowanej poprawnej formy w BROAD ani STANDARD. Zachowujemy wymaganie w explain. Dotyczy zamkniętej mapy sprawdzonych etykiet, bez zniesienia ograniczeń niesamodzielnych składników.

**B:** nie nadajemy tym oznaczeniom automatycznego efektu niewykluczającego; każda taka analiza wymaga indywidualnego przeglądu i do tego czasu pozostaje unresolved. To dodatkowa kontrola użycia, a nie automatyczne odrzucenie całych leksemów.
