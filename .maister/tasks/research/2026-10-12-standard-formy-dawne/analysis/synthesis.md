# Synteza researchu #4

## TL;DR
Wyjaśniono przyczynę: różna jednostka i różne źródła miary, nie brak publicystyki.
Zmiana na lemma+POS przenosi dowód współczesności na dawne formy.
Użytkownik przyjął kierunek oceny znaczenia i współczesnej odmiany; nie zatwierdzono wdrożenia nowej polityki.
Runda 3 daje propozycję 2382 form i ujawnia ubytki POP mimo wzrostu STANDARD; szczegóły poniżej.

## Key Decisions
- Wykluczone przez użytkownika: implementacja, brainstorming i projekt.
- Liczby oznaczają sondy przy zachowaniu dotychczasowych przyjęć.

## Open Questions / Risks
- Współczesność znaczenia, dawny desygnat, rejestr książkowy i dawna odmiana wymagają odrębnego traktowania.
- Nie da się przeliczyć próbki na liczbę rzeczywistych archaizmów w całym przyroście bez szerszej anotacji.

## Zgodność i kontrdowody
Kod, testy i odczyt bazy zgodnie potwierdzają próg formy 30. Wiki liczy orth_lc/all, więc jej większa frekwencja nie obala zachowania kodu. Korpus i WSJP potwierdzają żywe użycia niektórych odrzuconych leksemów. Jednocześnie jawne arch. w 35/40 grup pierwszej próbki obala bezwarunkowe przeniesienie frekwencji leksemu. Zachowanie arch. redukuje 4559 do 3364 dodatków, lecz ośm i homonimy pokazują pozostałe ryzyko. Kalkulatorzy w WSJP obala przeciwną uproszczoną regułę, że każde m1 przy nazwie urządzenia jest błędem.

## Dalsze zbieranie
Do omówienia kierunku z właścicielem dowody wystarczają. Przed wdrożeniem potrzebny jest skoncentrowany audyt znaczeń i form według wybranego kryterium; nie kolejna arbitralna zmiana progu.

Pełne liczby, cytowania, metodologia i pewność: [raport](../outputs/research-report.md).

## Pogłębiona synteza — runda 2

Pełny spis zastępuje próbkę źródłowych oznaczeń: 1176 z 1580 grup daje wyłącznie dodatki z arch., 404 daje 3364 formy bez arch. Siatka 40 sond potwierdza, że podnoszenie frekwencji i rozproszenia nie rozdziela znaczeń ani końcówek. Nie wybieramy progu produkcyjnego.

155 form, 80 kontroli, 107 publicznych fragmentów oraz 643 konkordancje pokazują zarówno żywe odrzucenia (sołtyska, wolontariacki, aktuariusz), jak i obcy dowód (wywre od innego wywrzeć, żeż jako partykuła zamiast żec). Dawne warianty mogą mieć daw./przest. bez arch.; dokumenta i zasłonionemu obalają wystarczalność pojedynczej blokady.

Kontrole zmieniają ocenę zachowania status quo: 290 napisów zależy od obecnego wyjątku, w tym zwykłe wyrazy oraz sek, którego obejrzane konteksty to skróty i urwane wyrazy. Nie rekomendujemy ani skasowania wyjątku, ani ślepego zachowania jego dowodu. Potrzebne jest rozdzielenie napisu od uprawnionej analizy.

Brak wiersza frekwencyjnego nie jest dowodem nieistnienia: 7/50 form tej warstwy ma trafienia w wyszukiwarce. Odmiana może być regularna i rzadka; nie wolno jednak z na umór wnioskować o swobodnym umorach. Czytnik SGJP i WSJP wspierają rozdział zakresów, lecz nie są niezależnymi źródłami fleksji.

Korekty wcześniejszych uproszczeń: nie wszystkie liczby pojedyncze są dawne; przechwałka/sztaluga/szuwar mają pozytywne dowody. Aliści/jakoż/nazad/trzykroć występują też w nacechowanej narracji współczesnej. Książkowość i regionalność już same w sobie nie wykluczają w obowiązującej polityce. Poprawny frazeologizm: na umór, nie do umoru.

Wysoka pewność dotyczy mechanizmu, policzonego składu i konkretnych kontrprzykładów. Średnia dotyczy oceny rejestru. Nie znamy odsetka błędów całej populacji. Wszystkie obowiązkowe tory wykonano; po przedstawieniu wyników potrzebna jest bramka omówienia, a nie automatyczna implementacja.

## Wynik omówienia

Użytkownik odpowiedział „ok” na rekomendację przyjęcia zasady jako kierunku dalszej rozmowy. Współczesne znaczenie uzasadnia odpowiadającą mu współczesną odmianę, również rzadką; nie przenosimy dowodu na dawne końcówki, inne znaczenia ani cały paradygmat formy zachowanej tylko we frazeologizmie. Książkowość pozostaje dopuszczalna. Frekwencja służy do wyszukiwania i porządkowania kandydatów; trzeba sprawdzić znaczenie, odmianę oraz użycia autorskie w różnych tekstach. Nie przyjęto nowego progu ani paczki 3364 form. Bramka researchu rozstrzygnięta; szczegóły i dalsze pytania w §9 [raportu](../outputs/research-report.md).

## Ocena kandydatów — runda 3

Po „ok, idzmy” oceniono zakres 404 grup oraz wszystkie 290 przyjęć zależnych od wyjątku. Uzupełniono 309 zapytań / 730 konkordancji, 501 wyszukań SGJP i 207 pełnych tabel. Szczegółowe 125 rekordów rodzin daje 2382 nowe formy ze 110 rodzin; 997 pochodzi z poprzednich 3364, a 1385 spoza tej paczki. Pozostałe 2367 nie jest zbiorowo odrzucone. Macierz jest pełnym spisem statusów, nie pełną ekspertyzą wszystkich znaczeń.

Przełożenie zasady na konkretną paczkę jest wykonalne badawczo: znaczenie, właściwa tabela i utrwalona analiza muszą się zgadzać. SQL potwierdził, że wszystkie 7192 wskazane analizy dodatków odpadają wyłącznie przez dawność. Nie rozstrzyga to niezależnie oceny językowej; ta pozostaje oceną jednego badacza o średniej pewności.

Kontrola obecnych przyjęć ujawnia 12 napisów bez właściwego dowodu w pierwszych 10 kontekstach. Nie dowodzi nieistnienia słów. Moko nie uzasadnia wołacza od moka, a ludzko ma poprawne samodzielne użycia mimo części trafień będących członami złożeń. Dlatego cofnięcia wymagają odrębnych decyzji.

Dokładnie odtworzone listy bazowe umożliwiły pełną symulację: STANDARD +2382; POP +2372 i −2430, netto −58; POP0 +481. Zmienia się próg obejmujący całe remisy przy limicie leksemów. Wariant cofnięcia 12 napisów dodatkowo zmienia ranking i dobór leksemów, m.in. usuwa odmianę dekagram z POP0. Wszystkie obowiązujące straże częstych form przechodzą, lecz nie obejmują całego ryzyka ubytków.

Rekomendacja: omówić konkretną paczkę oraz skutki rankingu, a cofanie przyjęć potraktować osobno. Dalsze badanie powinno dotyczyć wskazanej granicy znaczenia lub rejestru. Nowa bramka dotyczy przyjęcia wyników do rozmowy, nie wdrożenia. [Pełny raport rundy 3](../outputs/candidate-assessment.md).
