# Uzupełniający audyt źródeł po zatwierdzeniu A

## TL;DR
Wykonano audyt dostępności i warunków dodatkowych źródeł. Nie aktywowano nowych danych produkcyjnych.
G3 nadal wymaga pełnej semantyki i poświadczeń zgodnych z regułami gry; całe zadanie pozostaje w toku.


> Sprostowanie po rozmowie z użytkownikiem: wymaganie filtra SJPDor i późniejszego niezależnego opracowania nie było uzgodnione. Wyniki audytu pozostają aktualne; wcześniejszy opis ich konieczności nie jest bieżącą polityką generatora. Zob. [wyjaśnienie](source-policy-clarification.md).

## Key Decisions
- Zatwierdzenie A obowiązuje; brak ponownej bramki na tę samą pracę.
- Kod Kuźni potwierdza metadane SJPDor i dokładnych klas. Jego BSD-2-Clause nie licencjonuje automatycznie internetowej bazy SGJP.
- Kontrola poświadczeń objęła wszystkie 26 kandydatów. Otwartość źródła i dopuszczenie przez reguły gry są oddzielnymi warunkami.
- Nie użyto wykluczonych danych, nie zmieniono reguł gry, nie wywołano chronionego eksportu ani nie aktywowano częściowej polityki.

## Open Questions / Risks
- Potrzebny jest audytowalny artefakt pochodzenia/kategorii zgodny z eksportem 20260823 oraz jego warunki użycia. Brak markera SJPDor, status redakcyjny i data nie dowodzą niezależnego opracowania.
- Kontrakcje potrzebują poświadczenia w rodzaju źródła wymaganym przez reguły gry. Wikisłownik tego warunku nie zamyka. WSJP/PWN pozostają bez potwierdzonego artefaktu do planowanego użycia.
- Literalne etykiety przecinkowe i część macierzy hostów pozostają nierozstrzygnięte. Pomiary ekspozycji nie są deltą finalnych list.

## Pokrycie źródeł
[Audyt metadanych SGJP](sgjp-metadata-audit.json): odczytano oficjalną instrukcję, model, eksport, kod kontroli dostępu, COPYING i zawartość katalogu data. Każdy zachowany hash sprawdzono niezależnie. Kod eksportu ma także wyjątki forced-merge i odrębne warunki dla leksemów zagnieżdżonych; sama nazwa antivocabs nie wystarcza do potwierdzenia finalnej polityki.

[Audyt kontrakcji](contraction-attestation-audit.json): 26 punktowych żądań Wikisłownika dało 11 pełnych lokalnych stron, 5 odpowiedzi 404 i 10 odpowiedzi 429. Dodatkowo web odczytał jedną z ograniczonych stron. Nie ponawiano seriami po limitach. To 12 obserwacji językowych oraz 14 kandydatów bez odczytanej strony; zero aktywnych poświadczeń growych. Sprawdzono lokalne hashe, polską sekcję i stopki. Brak jawnego linku do wykluczonego źródła nie zastępuje audytu historii importów.

[Warunki Wikimedia](https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use/pl), §7, opisują warunki użycia treści i atrybucji. Nie stanowią dowodu dopuszczenia źródła przez zasady gry. Historia/dyskusje wpisów nie zostały domknięte, więc nie tworzymy z nich wejścia builda. Definicji i przykładów nie skopiowano do repo.

[WSJP](https://wsjp.pl/) i [zasady opracowania](https://pliki.wsjp.pl/zasady_opracowania_wsjp.pdf) odczytano przez web; curl homepage zwrócił 403. Dokumentacja darmowego wyszukiwania nie potwierdziła warunków włączania danych. Lokalny PDF pobrał się częściowo i nie jest przypiętym pełnym dokumentem. PWN: narzędzie web zgłosiło blokadę robots; obserwacja dostępu nie przesądza o licencji. Nie importowano haseł tych serwisów.

## Dodatkowy wynik techniczny
[Pełny raport KWJP](full-links-report.json): wszystkie 13 list i 5 066 341 jednostek rozliczono niezależnie, 2 940 032 krawędzie kandydatów. FK bez błędów, każdy rekord ma dokładnie jedno powiązanie. [Koszt](full-links-performance.json): 114,10 s samego powiązania, RSS 117 948 416 B. To kontrola techniczna na nowej kopii bazy, bez odbioru G8 i bez końcowej decyzji językowej/growej.

Test-first raportu: brak link_report dał rzeczywisty red, implementacja green. Test potwierdza F raz na jednostkę mimo homonimów, obserwację przy UNMATCHED, UNAVAILABLE NKJP i odmowę niepełnego rozliczenia. 25/25 testów generatora i 5/5 audytu przeszło. Integracja links do pełnego build musi nastąpić po konstrukcjach, aby objąć również nowe formy; nie oznaczono całego G5 complete.
