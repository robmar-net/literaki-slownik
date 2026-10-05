# Norma 2026 i mobilne końcówki — przegląd przyrostu

## TL;DR
Wdrożono A dla normy 2026: dokładne analizy comp jeśliby/jeżeliby i ich składniki konstrukcyjne mają odrzucenie STANDARD; BROAD nie wyklucza przez samą dawną pisownię. Nie usunięto wpisów i nie zmieniono reguł gry. Dodano kandydatów mobilnych końcówek dla trzech pozostałych zamkniętych klas, z kontrolą lematu, POS, wokaliczności, źródła i śladów. Rozbieżność ośmiu odmiennych analiz wyjaśniono regułą wokaliczności SGJP §6.4.1; ślad wskazuje wariant klasy oraz rzeczywistej formy. Pełna macierz i kwalifikacja nadal otwarte.

## Key Decisions
- Nowy warunek pisowni działa na dokładnym pełnym lemacie, POS i oryginale; nie bada końcowych liter dowolnego słowa.
- Konstrukcja dziedziczy ocenę źródłowych składników. Historyczny warunek nie oznacza pełnego accept w BROAD.
- Trzy klasy z_aglt/z_aglt_nwok/z_aglt_nwok2 są zamkniętą mapą źródłowych definicji; z_aglt_by zachowuje wcześniejszy odrębny konstruktor.
- Zamknięta klasa określa uprawnienie hosta; przy odmiennych hostach subst:% właściwa końcówka zależy od rzeczywistego zakończenia (SGJP §6.4.1). Kim+em ma jawny ślad tej różnicy, kim+ś nie jest generowane. Niby+m nadal nie ma uprawnionego hosta.
- Ślady mają pełne source_interpretation i FK; bez permissive, nowych leksemów oraz swobodnego dołączania by.

## Open Questions / Risks
- Łączenie host + by + końcówka, pozostała macierz gry i historyczna pisownia wymagają odrębnego źródłowego rozliczenia.
- Zamknięta macierz mobilnych końcówek nie zastępuje kontroli sekwencji host+by ani wszystkich warunków growych.
- Source_presence i lista wynikowa są nadal różnymi stanami; pełne decyzje pozostają nieukończone.

## Dowody i test-first

Podstawy teoretyczne SGJP §6.4.1 (s. 92) opisują mobilną końcówkę i jej wokaliczność; przykłady cóżeś/skądem/byleśmy. Przypięty segmenty.dat wiersze 143–155 i 743–815 definiuje zamknięte klasy. [Inwentaryzacja](mobile-host-inventory.json) wiąże definicje i wszystkie źródłowe interpretacje z hashem.

Dwa testy normy miały red: brak orthography_checks oraz explain unresolved zamiast reject STANDARD. Dwa testy mobilnych klas miały red: brak konstruktora oraz explain bez śladu. Green: 73/73 ukierunkowane policy/constructions/build/explain. Nie twierdzimy, że sama pozytywna ocena częściowa domknęła grupy.

Uzupełniający przegląd kodu segmenty.dat: etn. jest użyte przez klasę etnonimy (wiersz 672), nie dowodzi etnologicznej terminologii. Nie wprowadzono takiego aliasu. Szerokie wyszukiwanie objęło nazwę wyłączonego przykładowego pliku PoliMorfSmall; wyniku nie użyto do dowodów ani budowy. Dalsze wyszukiwania źródeł ograniczamy do jawnych dozwolonych plików.

## Kontrola na pełnych źródłowych wejściach

[Połączony runtime](norm-mobile-runtime.json) dla commit 606b371 obejmuje 93 158 interpretacji źródłowych, 93 871 kandydatów i 187 742 składniki; zero nowych kandydatów przy powtórzeniu i identyczny digest, FK/integrity OK, 134,666 s. To stan przed doprecyzowaniem odmiennych hostów.

[Pełny runtime nowych klas po doprecyzowaniu](mobile-variant-runtime.json) obejmuje 144 interpretacje (wszystkie analizy leksemów mapy oraz osiem aglt), 312 kandydatów i 624 składniki. Powtórzenie daje zero nowych kandydatów oraz identyczny digest, FK/integrity OK, 38,613 s. Kod z tego pomiaru był dirty i jest związany SHA256; diagnostyka nie uzyskuje VERIFIED. Pozostałych klas nie mierzono ponownie po poprawce ograniczonej do nowego konstruktora; nie deklarujemy tego jako drugiego pełnego build G8.

[Osiem różnic klasy i formy](mobile-variant-conflicts.json) zachowuje wszystkie przypadki. Reguła SGJP §6.4.1 określa e po końcowej spółgłosce. Test miał rzeczywisty red brak kandydata kimem; po doprecyzowaniu konstruktora green, z odrębnym host_variant_evidence. To nie swobodne tworzenie dowolnego hosta: lemma/POS nadal muszą należeć do zamkniętej mapy źródłowej.

[Explain na rzeczywistym G2](norm-mobile-explain-runtime.json): 12 zapytań readonly, nowa norma widoczna w JSON/tekście, poprawne ślady i zachowanie bezpośrednich analiz. Ocena pełnego członkostwa pozostaje nierozstrzygnięta. Po doprecyzowaniu wariantu sprawdzono dodatkowo rzeczywiste kimem/czymem; kandydaci mają jawny ślad wokaliczności, a kimś zachowuje niezależne wpisy źródłowe bez takiej rekonstrukcji.

Cała suita generatora 122/122; baseline audytu 5/5, preflight 14 wejść i 10 konfiguracji OK. Wcześniejsze artefakty pozostają historycznymi wynikami odpowiadającego im kodu.
