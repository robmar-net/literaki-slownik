# STANDARD: formy dawne i słowa żywe — pogłębiony research #4

## TL;DR
Szersze badanie potwierdza błędne uproszczenie: częstość napisu nie dowodzi współczesności konkretnego znaczenia i odmiany.
Zbadano pełne 1580 grup, próbkę 155 nowych form i 80 kontroli, 107 fragmentów KWJP½M oraz 643 konkordancje pełnej wyszukiwarki.
Żywe słowa bywają oznaczone jako dawne, ale automatyczne przejście na lemat wpuszcza też dawne formy i obce znaczenia.
Materiał wystarcza do rozmowy o kryterium; nie uzasadnia przyjęcia całego przyrostu ani konkretnego nowego progu.

## Key Decisions
- Tylko research: nie zmieniono reguł, list, konfiguracji ani wydania. Nie wybrano nowego kryterium STANDARD.
- Scenariusze dodają wyjątek do obecnej polityki; nie cofają obecnych przyjęć. Nie są pełnym projektem jej zastąpienia.
- SJP.pl pozostaje benchmarkiem, bez wpływu na dobór próbki i kryteriów badania.
- [Pierwsza runda](research-report-round1.md) i [pierwszy komentarz](https://github.com/robmar-net/literaki-slownik/issues/4#issuecomment-6115542830) zostają zachowane; poniżej szersze dowody i jawne korekty.

## Open Questions / Risks
- Jakie dowody mają uchylać dawną etykietę dla konkretnego znaczenia i jego współczesnej odmiany?
- Jak traktować formy żywe wyłącznie we frazeologizmach i archaizujące użycia autorskie?
- Nie ma pełnego audytu znaczeń wszystkich 3364 kandydatów ani niezależnego drugiego anotatora. Nie znamy odsetka błędów przyszłej reguły.

## 1. Co dokładnie zbadano

Pytanie: dlaczego STANDARD odrzuca współczesne słowa przez dawność i co można uznać za wiarygodny kontrdowód? Użytkownik zażądał poszerzenia próby przed decyzją. [Plan rundy 2](../planning/expanded-plan.md) zapisano przed nowymi wynikami.

Baza pozostaje ta sama: lokalny build `lists-v30-20261010-165826-a`, wydanie **LL-PL v29**, polityka `approved-conditions-v29`, STANDARD **3 090 194** form. Numery buildu i wydania nie są zamienne. Dane i hashe: [pomiary bazowe](../analysis/findings/measurements.json), [runda 2](../analysis/findings/round2/metrics.json).

| Tor | Wykonany zakres | Co można z niego wnioskować |
|---|---|---|
| Pełny spis | 1580 identyfikatorów SGJP, 4559 nowych napisów; podzbiór 404/3364 bez arch. | Dokładny skład i źródłowe oznaczenia; nie pełna ekspertyza znaczeń |
| Wrażliwość | 30 par progów oraz 10 wariantów gatunków/rozproszenia | Skala wpływu parametrów, bez wyboru najlepszego progu |
| Próbka form | 155 deterministycznie dobranych form z 4 warstw | Kontrprzykłady i luki dowodowe, bez nieważonego odsetka jakości |
| Kontrole | 40 obecnych przyjęć zależnych od wyjątku i 40 odrzuceń poza scenariuszem lemma≥30 | Ryzyka istniejącej reguły i braki proponowanego zakresu |
| KWJP½M | Skan 5500 plików, 11 108 fragmentów; odczyt wszystkich 107 trafionych fragmentów populacji 4559 | Pełne pokrycie tej publicznej próbki, nie całego korpusu |
| Wyszukiwarka KWJP | 257 zapytań, 643 odczytane konkordancje | Użycia konkretnych form i kontrola kontekstu |
| Słowniki | 40 celowych haseł SGJP, 47 artykułów; 24 wiersze porównań WSJP oraz kontrole rundy 1 | Rozdział znaczeń, odmiany i kwalifikatorów |
| Nowsze teksty | Punktowe źródła urzędowe i akademickie z lat 2024–2025 | Kontrdowód braku dzisiejszego użycia, bez reprezentatywnej frekwencji |

Próbka 155 = 50 + 5 + 50 + 50; warstwa „tylko fikcja” liczy zaledwie 5 form, więc zbadano całą. Seed: `issue4-round2-form-v1:`. W pełnej wyszukiwarce czytano pierwsze 3 konteksty każdego niepustego wyniku; 7 przypadków rozszerzono do 10. Kolejność nie jest losowa i często skupia książki/historyczne teksty. 107 fragmentów i 643 konkordancje mogą się pokrywać — nie sumujemy ich jako niezależnych obserwacji. Jeden badacz, jawne notatki, bez pozorowania zbioru rozstrzygniętych dopuszczeń. [Próbka](../analysis/findings/round2/sample-forms.json), [wszystkie oceny KWJP](../analysis/findings/round2/live-review.json), [fragmenty KWJP½M](../analysis/findings/round2/context-review.json).

## 2. Przyczyna pozostaje potwierdzona

Obecna reguła sumuje **dokładną formę pisaną małymi literami, fakt + publicystykę**. Przy ≥30 uchyla jedynie odmowę dawności. Nie pomija publicystyki. Miara wiki obejmuje też fikcję i zapis wielkimi literami. [Kod i polityka](../analysis/findings/code-and-policy.md).

| Forma | Miara wiki: orth_lc/all | Dokładna forma: fakt + publicystyka | Lemma+POS: fakt + publicystyka |
|---|---:|---:|---:|
| desperacja | 67 | 28 | 233 |
| ekscytacją | 71 | 21 | 219 |
| niezbędnik | 80 | 17 | 88 |
| familia | 95 | 19 | 170 |
| odzienie | 81 | 28 | 63 |
| surdut | 82 | 19 | 58 |
| aliści | 65 | 12 | 31 |
| jakoż | 61 | 7 | 41 |
| iże | 102 | 0 opublikowanych | 1 |

`Desperacji` jest przyjęte, `desperacja` odrzucone; `ekscytacja` przyjęte, `ekscytacją` odrzucone. Kontrola rodzin słów i kontekstów potwierdza, że licznik dokładnej odmiany rozcina żywe paradygmaty. Z kolei **615/2000** z ticketu oznacza napisy z dawną analizą w benchmarku, nie 615 udowodnionych błędów.

## 3. Pełny spis zastępuje pierwsze oszacowanie

W całej populacji 1580 grup **1176 daje wyłącznie dodatki z arch.**; 404 ma choć jeden dodatek bez tej etykiety. To ustalenie strukturalne z pełnych danych, mocniejsze od wcześniejszego 35/40 w próbce. Nie nazywamy go odsetkiem niezależnie potwierdzonych archaizmów. [Spis wszystkich grup](../analysis/findings/round2/census-1580.json).

Wyłączenie dodatków z arch. zmniejsza przyrost z **4559 do 3364**, ale nie rozwiązuje problemu. Dawność bywa oznaczona także przez daw./przest. przy konkretnej końcówce, np. `dokumenta`, `klasztora`, `zasłonionemu`; sama blokada arch. je przepuszcza.

| Dowód dokładnej formy w przypiętych listach KWJP | Formy w populacji 3364 | Zbadane formy |
|---|---:|---:|
| Brak publikowanego wiersza małoliterowego orth/all | 2587 | 50 |
| Publikowana tylko w fikcji | 5 | 5 |
| Fakt + publicystyka 1–4 | 111 | 50 |
| Fakt + publicystyka 5–29 | 661 | 50 |

**Brak wiersza nie oznacza zera użyć.** Spośród 50 form pierwszej warstwy wyszukiwarka znalazła 7, m.in. `niezbędnikiem`, `konsultorzy`, `nieutytułowaną`, ale także stylizowane `onemu`. Pozostałe 43 są niepotwierdzone w tej sondzie, a nie automatycznie błędne. Publikowany próg list dotyczy częstości całego korpusu. Bieżąca wyszukiwarka jest osobnym pomiarem, nie nadpisuje przypiętych CSV.

## 4. Ważne kontrprzykłady po obu stronach

| Rodzaj problemu | Dowód | Wniosek |
|---|---|---|
| Żywe znaczenie pod dawną etykietą | Sołtyska: WSJP rozdziela panią sołtys i dawną żonę sołtysa; KWJP i ARiMR używają pierwszego znaczenia | Odrzucenie całego napisu z powodu starego znaczenia gubi współczesne słowo |
| Żywy język fachowy | Wolontariacką, generyczny, industrialny, jagnięcinę mają zwykłe autorskie użycia | Dawna etykieta nie jest wystarczającym opisem dzisiejszego zakresu |
| Rzadka odmiana współczesnego słowa | Niezbędnikiem ma 3 trafienia wyszukiwarki; przytulisko ma współczesne znaczenia WSJP, choć przytuliskom nie znaleziono | Wymaganie osobnego progu dla każdej regularnej formy tworzy luki |
| Homonim o innej odmianie | SGJP wywrzeć „wygotować się”: wywre/wywrzał; wywrzeć wpływ: wywrze/wywarł | Popularność lemma+POS może ratować obcy leksem |
| Zachowany frazeologizm | Na umór, do rozpuku, jak kania dżdżu | Żywa konkretna forma nie daje dowodu całego swobodnego paradygmatu |
| Nazwa starego przedmiotu | Surdut, powijak; IPN używa niezbędnikiem o dawnym wyposażeniu | Wiek przedmiotu i wiek sposobu mówienia to różne rzeczy |
| Literówka udająca formę | Cześci: 4 z 5 kontekstów wyglądają na błędne części, piąty to dawny tytuł wiersza | Także anotacja lemma+POS może utrwalać błąd |
| Dane z innego zastosowania | Żeż w 10 obejrzanych kontekstach jest partykułą/wykrzyknieniem, kandydat dotyczy żec | Identyczny napis nie jest dowodem analizowanego czasownika |

Adresy źródeł, identyfikatory i ograniczenia: [kontrola słownikowa i nowsze teksty](../analysis/findings/round2/dictionary-evidence.md), [notatki z konkordancji](../analysis/findings/round2/live-review.json).

Skan KWJP½M przyniósł 83 fragmenty z użyciem autorskim, 9 z nazwami własnymi, 9 z cytatem/stylizacją i 6 z innymi problemami. **83 nie oznacza 83 zatwierdzonych słów**: fragment może zawierać kilka kandydatów, temat historyczny lub książkowy rejestr. Oceniono każde trafienie; surowych tekstów nie publikujemy.

## 5. Co ujawniły kontrole obecnej reguły

**290 napisów jest obecnie przyjętych dzięki wyjątkowi częstościowemu i bez innej zaakceptowanej analizy.** Łącznie 2301 napisów ma jakąkolwiek analizę z tym wyjątkiem, ale 2011 przyjęłoby się również inną drogą. Dopiero 290 jest właściwym mianownikiem dla badania skutku zniesienia obecnego wyjątku. [Pomiar](../analysis/findings/round2/current-override.json).

Deterministyczna próbka 40 z tych 290 obejmuje wyraźnie żywe `edukować`, `ubezpieczyciel`, `dostawczym`, `wynegocjować`, `zasadny`, `finalny`. Nie ma podstaw do prostego usunięcia wyjątku.

Jednocześnie **sek** jest przyjęte jako dawny rzeczownik z licznikiem NF=301. W 10 obejrzanych kontekstach wyszukiwarki jest 8 skrótów sekund i 2 urwane wyrazy; żaden nie dowodzi tego rzeczownika. Baza poprawnie odrzuca analizę skrótu, lecz jej częstość przenosi na dawną analizę rzeczownikową. To potwierdzona słabość dowodu, nie ustalenie, że przeczytano wszystkie 303 trafienia. [Walidacja przykładów](../analysis/findings/round2/validation.json).

Próba 40 odrzuceń spoza lemma≥30 wykazała też `aktuariusz`, `moderowana`, `upakowanych`, `pojazdowej`, `harcówki`, `spożytkuje` w żywych kontekstach. Poprawa nie może polegać wyłącznie na akceptacji 3364 kandydatów: taki zakres nadal pomija trafne przypadki. Nie każda z pozostałych odmów jest błędem — w tej samej próbie są dawne cytaty, rejestr książkowy i obce znaczenia.

## 6. Progi zmieniają liczbę, ale nie usuwają przyczyny

Poniżej dodatkowe formy przy zachowaniu obecnych przyjęć, pozostałych odmów oraz blokady arch. **L** to częstość pary lemma+POS w fakt/publicystyka; **F** — dokładnego małoliterowego napisu. POS oznacza kategorię z danych, np. fin i praet są liczone oddzielnie. Ta para nie identyfikuje znaczenia ani pełnego leksemu SGJP.

| Minimalne L | Bez minimum F | F≥1 | F≥5 | F≥10 | F≥20 |
|---|---:|---:|---:|---:|---:|
| 10 | 6988 | 1326 | 1034 | 467 | 127 |
| 20 | 4550 | 1008 | 832 | 400 | 124 |
| 30 | 3364 | 772 | 661 | 346 | 109 |
| 50 | 2336 | 531 | 466 | 256 | 90 |
| 100 | 1368 | 299 | 268 | 156 | 54 |
| 300 | 524 | 67 | 60 | 33 | 14 |

Nawet L≥300 pozostawia **454/524** dodatków bez publikowanego wiersza dokładnej formy. Warunek co najmniej 30 wystąpień lematowych w **każdym** z dwóch gatunków pozostawia 1533 dodatki, w tym 1209 bez takiego wiersza. Dyspersja DP_norm≤0,9 w jednym gatunku z F lematowym≥30 daje 1144 dodatki bez arch., z czego 934 bez publikowanego wiersza formy. To przeniesienie dowodu częstego członu na resztę paradygmatu; rozproszenie leksemu nie rozpoznaje dawnej końcówki. [Wszystkie 40 sond](../analysis/findings/round2/metrics.json).

Sam próg dokładnej formy ≥20/10/5 dodawał odpowiednio 131/487/1193 form w rundzie 1. Cały KWJP≥30 dodawał 150, w tym `iże`. Nie rekomendujemy żadnej liczby jako gotowej odpowiedzi. Wybranie jej przed ustaleniem, które użycia są pożądane, byłoby strojeniem do przykładów.

## 7. Co trzeba rozdzielić w kryterium

Rekomendacja do rozmowy: **oceniać współczesność znaczenia i zakresu odmiany osobno**. Regularna współczesna forma może być rzadka; archaiczna końcówka nie staje się współczesna dzięki popularności innej formy. Ograniczony frazeologizm potrzebuje oceny właściwego zakresu, a nie automatycznego rozszerzenia na cały rzeczownik.

Książkowość, rzadkość, potoczność i regionalność same w sobie **już nie wykluczają** w obecnej polityce. Nie stawiamy ponownie tej ogólnej decyzji. Do uzgodnienia pozostaje sposób podważania dodatkowej etykiety dawności oraz ocena użyć archaizujących. `Aliści`, `jakoż`, `nazad`, `trzykroć` mają także współczesne autorskie użycia nacechowane; nie można wszystkich ich trafień nazwać dawnym cytatem.

[Zasady redakcyjne WSJP](https://pliki.wsjp.pl/zasady_opracowania_wsjp.pdf), §2.7 i §2.11, wspierają rozróżnienie wieku przedmiotu, rejestru i formy. Dopuszczają też regularne formy potencjalne w paradygmatach. To argument przeciw wymaganiu wysokiej frekwencji każdego przypadku, nie automatyczna zgoda na wszystkie tabele SGJP. Fleksja WSJP korzysta z SGJP; źródła te nie są niezależnymi głosami. KWJP również używa powiązanej anotacji.

Pełny eksport spłaszcza kwalifikatory leksemu, odmiany i końcówki. Bieżący czytnik pomaga to badać, ale nie zapewnia automatycznie zgodności ze snapshotem i nowego wejścia do generatora. Wykonalność automatycznego rozdziału poziomów pozostaje osobnym problemem. [Dowody formatu i źródeł](../analysis/findings/round2/dictionary-evidence.md).

## 8. Pewność, luki i następny krok

**Wysoka pewność**: mechanizm obecnej reguły, liczby na przypiętych danych, istnienie obu rodzajów kontrprzykładów, rozdział wskazanych homonimów i wariantów. **Średnia pewność**: ocena rejestru pojedynczych kontekstów i rekomendowany kierunek. **Nieustalone**: dokładny udział błędów w 3364 formach, zachowanie przyszłej reguły na całym słowniku, jej utrzymanie i koszt pełnej kontroli znaczeń.

KWJP opisuje piśmiennictwo 2011–2020; punktowe źródła z lat 2024–2025 częściowo zamykają lukę aktualności. Nie zastępują współczesnego reprezentatywnego korpusu ani mowy. Datę wydania książki 2021 trzeba sprawdzać z datą pierwszej publikacji — np. jeden z odczytanych rekordów ma pierwszą publikację w 2012. NKJP pozostaje starszą kontrolą z rundy 1, bez dodawania pozornej niezależności i bez zmiany zakresu ADR-006.

**Dalsze zwiększanie losowej próbki nie jest teraz najważniejszym krokiem.** Materiał wystarcza do omówienia granic STANDARD. Po ich uzgodnieniu potrzebny będzie przegląd kandydatów według przyjętej definicji i osobna walidacja proponowanej reguły, również na obecnych przyjęciach. W tej rundzie nie wydajemy listy zatwierdzonych dodatków ani nie podajemy pozornego odsetka skuteczności.

Korekty rundy 1: pełne 1176/1580 zastępuje małe 35/40 jako opis źródłowych grup; nie zakładamy, że pojedyncze `przechwałka/sztaluga/szuwar` są z zasady dawne; poprawny frazeologizm to **na umór**, nie do umoru. Szczegóły pozostają jawne w aneksie.

## Pokrycie i odtwarzanie

Wszystkie pięć wymaganych kategorii źródeł sprawdzono i rozszerzono: kod; dokumentację; konfigurację/testy; przypięte dane; zewnętrzne źródła pierwotne. [Rejestr źródeł](../planning/sources.md). Nie pozostał niezbadany obowiązkowy tor; częściowa niedostępność stron i wyszukiwań jest opisana w aneksie. Surowe odpowiedzi oraz pełne konteksty pozostają w ignorowanym `tmp/`.

Z katalogu repo uruchamia się skrypty w katalogu zadania `analysis/`: bazowe `measure.py`, `followup.py`, `evidence_probe.py`; następnie `expanded_probe.py`, `control_probe.py`, `kwjp_live_probe.py`, `annotate_round2.py`, `sgjp_review.py`, `validate_round2.py`. Wymagają przypiętych danych i opisanych cache. Probe KWJP odczytuje publiczną wyszukiwarkę, jeżeli cache nie istnieje; jej wyniki mogą się zmienić. Manifest SGJP korzysta z zachowanych odpowiedzi, a dokładne adresy do ponowienia są w JSON. Baza jest otwierana tylko do odczytu.

Walidacja sprawdza rozłączne warstwy, zgodność spisu i siatki, odtworzenie 4559/3364, kontrolne decyzje bazy, kompletność notatek oraz hashe źródeł. Pierwsza runda zawiera wynik 6 istniejących testów reguły; w rundzie 2 nie zmieniono kodu produkcyjnego. Badanie i publikacja wyników nie zatwierdzają polityki. Faza Maister oczekuje na omówienie i decyzję właściciela.
