# Audyt unigramów NKJP

## TL;DR

`1grams.gz` jest technicznie dostępny i został zbadany w całości **wyłącznie audytowo**. Wejście pozostaje **BLOCKED do generowania i pilotażu łączenia źródeł**: deklaracja dystrybucji brzmi „NKJP ngrams are made available on CC-BY licence.”, bez numeru wersji i odnośnika do tekstu warunków. Nie uzupełniamy tych braków samodzielnie. [Źródło i zakres deklaracji](https://zil.ipipan.waw.pl/NKJPNGrams).

## Key Decisions

- Publikujemy własne agregaty techniczne, skrypt oraz metadane. Pobrany plik i kopie dokumentacji pozostają w ignorowanym `cache/nkjp/`; nie publikujemy listy form ani ich częstości.
- Nie dołączamy NKJP do rankingów, zbiorów ATTESTED ani bieżącego pilotażu SGJP/KWJP. Ich pola NKJP mają status `UNAVAILABLE`, z przyczyną blokady licencyjnej.
- `ALLOWED` przy dokumentach w rejestrze oznacza tylko ich wykorzystanie bibliograficzne do opisania ustaleń, nie zgodę na redystrybucję dokumentacji czy danych.

## Open Questions / Risks

- Potrzebne oficjalne wskazanie wersji CC-BY, właściwego tekstu warunków oraz wymaganej atrybucji dla dokładnego artefaktu. Nie przenosimy licencji innych projektów ZIL ani pełnego NKJP na te n-gramy.
- Nie ustalono wersji ekstraktora, jego kodu, dokładnego wydania podkorpusu i zależności anotacyjnych użytych do ekstrakcji. Nie znamy również nakładania z KWJP. Poświadczenia nie są nazywane statystycznie niezależnymi.
- Opis „300M tokens” nie odpowiada sumie częstości napisów w pobranym pliku. Nie rozstrzygnięto, jak definicje jednostek i ekstrakcja tłumaczą różnicę.

## Dokumentacja i dystrybucja

[Strona oficjalna](https://zil.ipipan.waw.pl/NKJPNGrams) opisuje n-gramy 1–5 ze zrównoważonego podkorpusu NKJP, 300 mln tokenów. Jednostką unigramową ma być maksymalny ciąg znaków niebiałych, zapisany małymi literami. Deklarowane są wszystkie unikalne jednostki, lecz brak jawnego progu, wydania i kodu ekstrakcji. Ostatnia edycja strony: 26.01.2021; to nie data wydania danych.

[Metadane załącznika](https://zil.ipipan.waw.pl/NKJPNGrams?action=AttachFile&do=view&target=1grams.gz) wskazują 29.12.2014. Odpowiedź HTTP pliku podaje `Last-Modified: Mon, 29 Dec 2014 13:17:13 GMT`. W nagłówku gzip jest 01.07.2012 07:39:57 UTC; jest to czas zapisany w kontenerze, nie potwierdzona data korpusu. Gzip ma flags=0, bez dodatkowego pola nazwy czy komentarza. Spis załączników zawiera wyłącznie pliki 1–5grams.gz, bez osobnego pliku licencji.

Źródłowy opis sugeruje kolejność napis → liczba. **Pomiar pliku wykazał przeciwną kolejność: liczba → napis.** Każdy rekord ma dziesiętną częstość wyrównaną spacjami do szerokości 7, pojedynczą spację, token i LF. Brak nagłówka. Wszystkie bajty tekstu dekodują się jako UTF-8. Parser nie usuwa interpunkcji ani nie tworzy nowych słów.

## Rzeczywisty pomiar całego pliku

Pole `token` w poniższej tabeli oznacza wpis/wiersz, nie leksem, interpretację ani potwierdzony wyraz języka polskiego. Nie wykonywano osobnej deduplikacji napisów; unikalność jest deklaracją źródła, nie wynikiem tego pomiaru. Kategorie znaków mogą się nakładać.

| Miara | Wynik |
|---|---:|
| Rozmiar gzip | 22 692 778 bajtów |
| Rozmiar po dekompresji | 106 027 837 bajtów |
| Wiersze / poprawnie rozpoznane rekordy | 5 364 398 |
| Suma opublikowanych częstości | 246 153 378 |
| Minimalna / maksymalna częstość | 1 / 7 692 997 |
| Rekordy F=1 | 2 989 804 |
| Rekordy F<5 | 4 219 965 |
| Rekordy ze znakami interpunkcyjnymi Unicode P* | 3 892 305 |
| Rekordy tylko z liter Unicode (`isalpha`) | 1 413 827 |
| Rekordy tylko z liter `aąbcćdeęfghijklłmnńoóprsśtuwyzźż` | 1 368 033 |
| Rekordy z cyfrą (`isdigit`) | 467 701 |
| Rekordy z kropką | 1 333 841 |
| Rekordy z łącznikiem ASCII | 351 637 |
| Rekordy z apostrofem ASCII lub `’` | 50 043 |
| Rekordy dłuższe niż 15 punktów kodowych | 375 363 |
| Rekordy zmieniane przez NFC | 52 |
| Rekordy zmieniane przez `lower()` / zawierające biały znak | 0 / 0 |
| Naruszenia nierosnącej kolejności częstości | 0 |

Próg pięciu wystąpień **nie obowiązuje w tym pliku**: stwierdzono rekordy z F=1. Nie dowodzi to samo w sobie kompletności listy względem wszystkich jednostek korpusu. Duża liczba napisów z interpunkcją jest zgodna z tokenizacją po odstępach; bez kodu ekstrakcji nie odtwarzamy całej procedury. Liczenie tekstowego zapisu nie rozstrzyga nazwy własnej, POS ani leksemu.

## Reprodukcja, granice i próby dostępu

```sh
python3 scripts/audit_nkjp.py cache/nkjp/1grams.gz .maister/tasks/research/2026-10-04-audyt-zrodel-polskich-slownikow/analysis/findings/nkjp-statistics.json
```

SHA256 gzip: `73af49094621b2f86b594beba783c14aee8c8212f1aff3d61f281ab5d99e3dc9`.
SHA256 tekstu: `1476e7c4dc7c41ad9638611a5a723206edb4c579cbf01d6b9f6eec681d0516d4`.
Wersja Unicode w pomiarze: 16.0.0. Rejestr: [nkjp-sources.json](nkjp-sources.json); agregaty: [nkjp-statistics.json](nkjp-statistics.json).

04.10.2026: odczyt strony i metadanych w narzędziu WWW udany. Próba bezpośredniego odczytu gzip tym narzędziem zwróciła `Unsupported content-type: application/octet-stream`; to ograniczenie narzędzia. Pierwszy curl strony wewnątrz sandboxa zwrócił kod 6 (`Could not resolve host`); ponowienie z zatwierdzonym dostępem sieciowym zakończyło się HTTP 200. Pobranie gzip curlem poza sandboxem zakończyło się HTTP 200. Nie ma blokady technicznej źródła.

Sprawdzono stronę dystrybucji, listę załączników, nagłówek i cały zdekompresowany plik. Trzy zapytania wyszukiwarki dotyczące wersji licencji NKJPNGrams/1grams nie ujawniły dokładniejszych oficjalnych warunków; wyniki o innych zasobach nie stanowią podstawy przypisania wersji. Nie twierdzimy, że brak stosownego dokumentu w całym Internecie.

Po wyjaśnieniu warunków połączenie może odbywać się wyłącznie przez zachowany, pełny napis po jawnej normalizacji NFC. Nie wolno usuwać interpunkcji, utożsamiać częstości napisu z częstością leksemu ani mnożyć jej przez liczbę interpretacji SGJP. To projekt późniejszego działania, nie wykonany pilotaż. Brak wpisu wymaga statusu `NOT_IN_PUBLISHED_LIST`, dopóki nie udowodniono porównywalności jednostek i mechanizmu publikacji; nie automatycznego F=0.
