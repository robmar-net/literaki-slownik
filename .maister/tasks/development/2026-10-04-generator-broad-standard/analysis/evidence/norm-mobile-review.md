# Norma 2026 i mobilne końcówki — przegląd przyrostu

## TL;DR
Wdrożono A dla normy 2026: dokładne analizy comp jeśliby/jeżeliby i ich składniki konstrukcyjne mają odrzucenie STANDARD; BROAD nie wyklucza przez samą dawną pisownię. Nie usunięto wpisów i nie zmieniono reguł gry. Dodano kandydatów mobilnych końcówek dla trzech pozostałych zamkniętych klas, z kontrolą lematu, POS, wokaliczności, źródła i śladów. Odmienne formy niezgodne z wariantem źródłowej klasy wymagają dalszej oceny; pełna macierz i kwalifikacja nadal otwarte.

## Key Decisions
- Nowy warunek pisowni działa na dokładnym pełnym lemacie, POS i oryginale; nie bada końcowych liter dowolnego słowa.
- Konstrukcja dziedziczy ocenę źródłowych składników. Historyczny warunek nie oznacza pełnego accept w BROAD.
- Trzy klasy z_aglt/z_aglt_nwok/z_aglt_nwok2 są zamkniętą mapą źródłowych definicji; z_aglt_by zachowuje wcześniejszy odrębny konstruktor.
- Wokaliczność musi być zgodna zarazem z klasą i zakończeniem rzeczywistej formy. Nie dopuszczamy kim+ś jako nowej mobilnej konstrukcji ani niby+m.
- Ślady mają pełne source_interpretation i FK; bez permissive, nowych leksemów oraz swobodnego dołączania by.

## Open Questions / Risks
- Łączenie host + by + końcówka, pozostała macierz gry i historyczna pisownia wymagają odrębnego źródłowego rozliczenia.
- Odrzucenie niedopasowanej kombinacji nie stanowi dowodu kompletności całej klasy; przypadki niezgodności pozostają w macierzy jako luka.
- Source_presence i lista wynikowa są nadal różnymi stanami; pełne decyzje pozostają nieukończone.

## Dowody i test-first

Podstawy teoretyczne SGJP §6.4.1 (s. 92) opisują mobilną końcówkę i jej wokaliczność; przykłady cóżeś/skądem/byleśmy. Przypięty segmenty.dat wiersze 143–155 i 743–815 definiuje zamknięte klasy. [Inwentaryzacja](mobile-host-inventory.json) wiąże definicje i wszystkie źródłowe interpretacje z hashem.

Dwa testy normy miały red: brak orthography_checks oraz explain unresolved zamiast reject STANDARD. Dwa testy mobilnych klas miały red: brak konstruktora oraz explain bez śladu. Green: 73/73 ukierunkowane policy/constructions/build/explain. Nie twierdzimy, że sama pozytywna ocena częściowa domknęła grupy.

Uzupełniający przegląd kodu segmenty.dat: etn. jest użyte przez klasę etnonimy (wiersz 672), nie dowodzi etnologicznej terminologii. Nie wprowadzono takiego aliasu. Szerokie wyszukiwanie objęło nazwę wyłączonego przykładowego pliku PoliMorfSmall; wyniku nie użyto do dowodów ani budowy. Dalsze wyszukiwania źródeł ograniczamy do jawnych dozwolonych plików.
