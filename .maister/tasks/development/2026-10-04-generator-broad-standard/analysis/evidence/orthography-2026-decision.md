# Norma z 2026 r. a nieoznaczone dawne zapisy SGJP

## TL;DR
Przypięty SGJP zawiera jeśliby oraz jeżeliby jako spójniki bez kwalifikatora dawności.
Norma obowiązująca od 2026 r. wymaga dla tych połączeń pisowni rozdzielnej.
Przed aktywacją kwalifikacji potrzebny jest wybór sposobu traktowania takiej rozbieżności.
Nie zmieniono reguł gry ani zapisów źródłowych; kandydaci pozostają niezakwalifikowani.

## Key Decisions
- Wpis w SGJP i pisownia wymagana przez współczesną normę są odrębnymi dowodami.
- Nie wolno odrzucać wszystkiego zakończonego na by: odrębne wyrazy aby/gdyby oraz nierozdzielne partykuły mają inne zachowanie.
- Nie usuwamy źródłowych analiz. BROAD/STANDARD, filtr gry i profil pozostają oddzielnymi ocenami.
- Brak etykiety dawności nie wyklucza udokumentowanej zmiany pisowni.

## Open Questions / Risks
- Użytkownik zatwierdził A; konkretne klasy aktywujemy po dowodzie i testach.
- Potrzebna jest pełna macierz zmian pisowni, nie tylko dwa wyjątki albo ogólna reguła sufiksu.
- Rozstrzygnięcie nie dowodzi kompletności kategorii i pozostałych kwalifikatorów.

## Dowody

[RJP, Zasady pisowni i interpunkcji polskiej, wersja jednolita 11-2025](https://rjp.pan.pl/app/uploads/2025/11/2-zalacznik-do-komunikatu-11-25-wersja-jednolita.pdf), §4.5.1c–d oraz §4.5.2c, rozdziela odrębne wyrazy i połączenia spójników z cząstką warunkową.
[Komunikat RJP](https://rjp.pan.pl/komunikat-rady-jezyka-polskiego-przy-prezydium-pan-z-dnia-7-listopada-2025-r/) określa wejście zmian w życie 1 stycznia 2026 r.
[Poradnia Uniwersytetu Łódzkiego](https://www.poradnia-jezykowa.uni.lodz.pl/szczegoly/pisownia-spojnikow-jesli-jezeli-z-czastka-by) rozstrzyga konkretnie zapis jeśli/jeżeli + by jako rozdzielny od 2026 r.
Dokumenty są dowodem normy, nie nowym źródłem leksemów ani licencją na ich pełną redystrybucję.

Odczyt pełnego G2 w trybie readonly:

| Oryginał | Pełne ID lematu | Tag | Kwalifikatory | Wiersz SGJP |
|---|---|---|---|---:|
| jeśliby | jeśliby | comp | brak | 2037336 |
| jeżeliby | jeżeliby | comp | brak | 2037791 |

Wdrożony konstruktor mobilnego by daje ponadto osiem kandydatów: jeślibym/jeślibyś/jeślibyśmy/jeślibyście oraz analogiczne cztery formy jeżeliby. Razem są to dwa bezpośrednie wpisy i osiem śladów konstrukcyjnych wymagających oceny. To ekspozycja problemu, nie końcowa delta list: inne warunki i homonimy nadal oceniane osobno.
Czyby występuje wyłącznie w czterech interpretacjach nazwisk z wielką literą; nie dowodzi spójnika czyby. Toby nie ma bezpośredniej analizy. Aby i gdyby mają odrębne analizy comp/part, które trzeba zachować.

[Inwentaryzacja mobilnych hostów](mobile-host-inventory.json) sprawdza wszystkie 70 różnych definicji z czterech zamkniętych klas źródłowych. Żadna definicja nie jest nieobecna w przypiętym SGJP. Definicje wskazują 95 interpretacji (liczone per klasa, nie jako unikalna populacja wszystkich rekordów) i osiem źródłowych aglutynantów. Powtórne czyż w z_aglt jest jedną definicją z dwoma numerami wierszy. To pokrycie źródłowe, nie akceptacja dowolnych sklejeń.

## Wybór przed wdrożeniem

A — rekomendowane: STANDARD stosuje normę z 2026 r.; BROAD może zachować udokumentowane dawne zapisy. Każda analiza nadal przechodzi oddzielne, niezmienione reguły gry. Zmiany dotyczą również nieoznaczonych w SGJP starych zapisów i wymagają dowodu konkretnej klasy, bez zgadywania po sufiksie.

B — oba warianty na tym etapie opierają ocenę pisowni na przypiętym SGJP; rozbieżności z normą 2026 są jawnie opisane, a odmienna baza normy wymaga aktualizacji specyfikacji przed dalszym wydaniem.

Pytanie wynika z AGENTS.md: decyzje zmieniające skład słownika lub kryteria dopuszczalności omawiamy przed wdrożeniem, oraz G3/3.4 zatwierdzonego planu. Użytkownik odpowiedział A; odpowiedź zarejestrowano w stanie zadania.
