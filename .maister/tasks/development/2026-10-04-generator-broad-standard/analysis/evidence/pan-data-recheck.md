# Ponowny przegląd danych PAN: dowody znaczeń

## TL;DR
Przyjęte dane PAN pozwalają częściowo uzupełniać brakującą wiedzę. Poprzednie wyjaśnienie nadmiernie eksponowało brak gotowej klasyfikacji i pomijało użyteczność dostępnych kontekstów.
Listy KWJP dostarczają połączeń i pisowni; publiczne próbki KWJP½M zawierają pełniejsze konteksty oraz bibliografię. Dokumentacja SGJP potwierdza glosy i odsyłacze w bazie internetowej, poza pięciopolowym eksportem.
Nie dowiedziono kompletnego pokrycia wyjątków; nie zmieniono kryteriów, nie aktywowano nowych danych w generatorze.

## Key Decisions
- Korzystamy z już przyjętych list KWJP do wyszukiwania przypadków i połączeń, nie do automatycznego werdyktu normatywnego.
- KWJP½M sprawdzono wyłącznie jako publiczny materiał dowodowy z tego samego przypiętego repozytorium PAN; nie jako nowe wejście leksykalne lub aktywny filtr.
- Kontakt z innymi grupami pozostaje wykluczony. Dowody mogą być opracowane samodzielnie z publicznych materiałów.
- Każde późniejsze rozstrzygnięcie wymaga dopasowania do pełnego ID SGJP i oddzielenia homonimów. Nie kopiujemy automatycznie znaczenia z pisowni ani statystyk.

## Open Questions / Risks
- Nie ma dotąd pełnej tabeli znaczeń dla nazw mieszkańców i niesamodzielnych członów obcych zwrotów. Kontekst pojedynczego użycia nie zamyka całej klasy ani wszystkich znaczeń.
- Brak wystąpienia w próbce lub liście z progiem pięciu wystąpień nie dowodzi braku samodzielnego polskiego znaczenia.
- KWJP obejmuje teksty 2011–2020, więc pisownia nie rozstrzyga obowiązującej normy 2026. Automatyczna anotacja może zawierać błędy.
- Istnienie glos i relacji w modelu internetowego SGJP nie dowodzi, że każda potrzebna glosa jest wypełniona lub że mamy wersjonowany, dopuszczony eksport całej tej bazy.
- Nie udało się odczytać PDF instrukcji KWJP½M: lokalnie brak czytnika tekstu PDF, web zwrócił cache miss. Strukturę i zawartość próbek sprawdzono bezpośrednio w JSON; README głównego repo opisuje ich cel i warunki.

## Co faktycznie znaleziono
1. Przyjęta lista bigramów: `na oścież` F=357 i `na wznak` F=208. To dowód połączeń, nie samoistny dowód polskości ani poprawności każdej interpretacji.
2. Lista zachowująca wielkość liter zawiera zarówno `krakowiak` F=10, jak i `Krakowiak` F=109. Lista bigramów zawiera także `Dariusz Krakowiak` F=39. Wielka litera nie oznacza automatycznie nazwy mieszkańca, a statystyki nie rozróżniają pełnych ID SGJP.
3. Przeczytano wszystkie 5500 plików JSON archiwum publicznych próbek KWJP½M. Wyszukiwanie kandydatów odbyło się wyłącznie w samples[].text, nie w metadanych, z rozdzieleniem rodzin warszawian-/warszawiank-. Bibliografię, ID i numery próbek zapisano w [raporcie](pan-data-recheck.json), bez kopiowania całych tekstów do repo.
4. Próbka 142495 zawiera opis współczesnych mieszkańców stolicy i formy warszawianek/warszawiaków; 136131 zawiera taniec krakowiaka. Dwie próbki zawierają `na wznak`, dwie `na oścież`. Próbka 181779 zawiera kontekst Desy Unicum; 136576 dotyczy osoby i formy Desa. Ta różnica pokazuje, dlaczego nie można wykluczać po samym zapisie. To własny odczyt kontekstów, jeszcze nie kwalifikacja pełnych ID.
5. Instrukcja SGJP opisuje glosy wyjaśniające homonimy, typowe połączenia i odsyłacze. Przypięty model Kuźni zawiera gloss/note/extended_note, borrowing_source oraz relacje masfem/femmas. Dane te mogłyby ułatwić przegląd; ich rzeczywistych wartości dla całej klasy nie uzyskano. Samo zapożyczenie nie jest growym wyłączeniem członu obcego zwrotu.
6. Eksport SGJP ma użyteczne klasy, m.in. nazwa_firmy/marka/nazwisko oraz kwalifikatory dziedzinowe. Nie brakuje wszelkiej semantyki: brakuje kompletnego rozróżnienia konkretnych wyjątków. Przykładowo warszawianka/desa mają tylko nazwa_pospolita, oścież:F/wznak sam frag. Zachowany eksport nie wystarcza do automatycznego zamknięcia tych wyjątków.

## Pochodzenie i granica wniosku
- Aktywne wejścia sprawdzone w config/generator/sources.json: SGJP oraz 13 list KWJP, w tym bigramy. Cztery lokalne listy przebadano w całości dla jawnie wskazanych przykładów; cały pakiet źródeł nie był ponownie importowany.
- KWJP½M_samples.tar.gz pobrano z commit 26d82bd8b906dfed1cfcf8f903b1650b56daeabf. SHA256 aedad77022508fe10d0d537e6a082884b8e7a97d4836a184ff744a5261db55b1, git blob SHA1 bed4e3e2ca289db6da8a65cab183e007f01e3e35 zgodny z wcześniej zapisanym tree.json. Surowe pliki pozostają w ignorowanym tmp/. Licencja głównego README: CC BY 4.0 dla zasobów repo; materiał tylko do odczytu dowodowego, bez aktywacji build.
- [KWJP: opis i rola kontekstów](https://kwjp.pl/overview), [opis list i ich ograniczeń](https://kwjp.pl/lists/doc/about/), [publiczne repozytorium](https://github.com/ipipan/kwjp100-varia), [instrukcja SGJP: glosy i odsyłacze](https://sgjp.pl/instrukcja/).

Wniosek: najpierw wykorzystać dostępne konteksty do własnego przeglądu konkretnych wyjątków i osobno zmierzyć jego pokrycie. Nie uzależniać postępu od kontaktu z autorami i nie twierdzić, że kompletna klasyfikacja już powstała.
