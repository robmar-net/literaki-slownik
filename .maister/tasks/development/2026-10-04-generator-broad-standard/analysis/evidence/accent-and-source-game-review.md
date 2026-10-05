# Adnotacja akcent i klasy jednostek w regułach gry

## TL;DR
Zatwierdzone A dla adnotacji akcent wdrożono bez zmiany dawności: BROAD nie wyklucza przez brak objaśnienia, STANDARD odrzuca dwie analizy daw.,rzad.,akcent. Pełny raport 7 458 520 analiz zachowuje 26 nieobjaśnionych oznaczeń w 1910 analizach. Dodano diagnostyczne warunki klas źródłowych gry: nazwy, brev, niesamodzielne segmenty oraz odrębną ocenę całości konstrukcji. Nowa zamknięta klasa ja/ty/my/wy/wszyscy zachowuje sześć kandydatów i growe odrzucenie tych analiz, bez usuwania homonimów. Pozostałe mobilne hosty i sekwencje by oceniono zgodnie z zachowanymi wyłączeniami gry; byle ma udokumentowany wyjątek. Pełna kwalifikacja i wydanie nadal nieukończone.

## Key Decisions

- Warunek rozpoznania oznaczeń nie oznacza pełnej akceptacji słowa. Globalne nierozstrzygnięcia języka i gry pozostają jawne.
- Cztery klasy adja/pacta/numcomp/aglt to składniki; brev to skrót. Frag i adjp nie są automatycznie wyłączane z powodu kontekstu. Rzeczownikowy skrótowiec nie staje się brev.
- 35 dosłownych oznaczeń nazw rozpoznano w 79 zaobserwowanych polach. Mieszana klasyfikacja pospolita/własna nie tworzy wymyślonych sensów. Wszystkie 295 mieszanych analiz są pisane z wielką literą; niezależne homonimy zostają.
- Kompletny konstruktor ocenia całość, zachowując składniki. Sam aglt jest niedopuszczalny, ale nie przenosimy tego odrzucenia na całą formę bym. Osobne wyłączenia mobilnych końcówek nadal obowiązują.
- Formalna definicja klasy wszyscy w segmenty.dat wskazuje lemat wszystek i adj:%, mimo komentarza o rzeczowniku PT. Użyto definicji; nominalnego hosta nie dopisano.

## Open Questions / Risks

- Nie zakończono pełnej macierzy semantyki, ortografii i warunków gry. Nazwy domen/plików, niesamodzielne składniki obce i inne warunki nie są dowodzone samym POS. G3–G6 pozostają częściowe.
- Wynik warunku klas źródłowych nie jest deltą list: dodatni warunek nie usuwa innych niewiadomych lub wyłączeń.
- Źródła leksykalne nie zmienione; brak SJP/OSPS/PoliMorf/Wikisłownika jako wejść. ZDS służy rozdzieleniu już udokumentowanych wyłączeń, bez przejęcia jego redakcyjnych ograniczeń źródeł.

## Dowody i kontrola

- [Pokrycie kwalifikatorów po A](accent-condition-coverage.json): 615 pól, 605 oznaczeń, 26 nieobjaśnionych oznaczeń w 1910 analizach, etykieta zależnego ń pozostaje osobno.
- [Pokrycie źródłowych klas gry](source-game-condition-coverage.json): wszystkie 7 458 520 analiz; sam warunek daje 6 300 332 accept, 1 157 893 reject i 295 unresolved. To wyłącznie agregacja tego warunku.
- [Readonly explain i powtarzalność](accent-game-runtime.json): 11 rzeczywistych zapytań, zero zapisów, dwa identyczne raporty kwalifikatorów, manifest niezmieniony.
- [Projekcja konstruktorów](personal-scope-runtime.json): 615 źródłowych interpretacji, 776 kandydatów i 1796 składników; powtórzenie bez nowych kandydatów, identyczny digest, FK/integrity OK. Projekcja obejmuje wszystkie wejścia obecnych klas poza impt; nie jest pełnym build wydania.
- [Growe warunki konstrukcji](construction-game-runtime.json): sześć całych śladów osobowych i rozliczenie każdej klasy. Odrzucenie jam jako ja+m nie odrzuca jam od jama.
- Test-first: accent 1, źródłowe warunki gry 4, osobowy konstruktor i explain 2, mobilne wyłączenia 1; rzeczywiste red→green. Wcześniejszy test czyżeś oczekiwał unresolved przed wdrożeniem reguły; teraz sprawdza potwierdzone growe reject.
- Generator 142/142 i regresja audytu 5/5 przeszły. Kontrola wejść/config po finalnym uporządkowaniu hashy zapisana oddzielnie.

## Źródła

[Instrukcja SGJP](https://sgjp.pl/instrukcja/) wyjaśnia klasy jednostek i informacje o pospolitości. Przypięty tagset Morfeusza: adja 275–276, aglt 436–444, numcomp 736–737, frag/brev 769–773. Segmenty.dat: złożenia pacta 187–191, osobowe hosty 174–183 oraz definicje 1927–1930 i 1947. Metryki i hashe w config/generator/evidence.json; źródłowe pliki pozostają w cache.

[ZDS §1 i §5](https://sjp.pl/sl/dp.phtml) rozróżnia własne nazwy, skróty i ograniczenia dołączania końcówek. Użyto wyłącznie tych potwierdzonych reguł, z odrębnym udokumentowanym byle i hostami kończącymi się na by; nie przejęto zasad źródłowego pochodzenia haseł ani list słów.
