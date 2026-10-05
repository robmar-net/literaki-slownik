# Specyfikacja wykonawcza generatora BROAD i STANDARD

## TL;DR

Jedno lokalne narzędzie Python/SQLite buduje dwa pełne kandydaty ze wskazanych SGJP/KWJP.
Każdy wynik ma spójne analizy, reguły, powiązania dowodowe i wyjaśnienie.
Build tworzy wynik INCOMPLETE; verify sprawdza K1–K10; export zamraża wyłącznie zweryfikowany pakiet.
Uzupełnienie dowodów językowych jest obowiązkową częścią implementacji.
Status dokumentu: zatwierdzony przez użytkownika odpowiedzią A w fazie 5; audyt i plan w kolejnych fazach.

## Key Decisions

- Zachowujemy G1/N1/C1, lokalny proces i SQLite z [zatwierdzonego projektu](../../../research/2026-10-04-audyt-zrodel-polskich-slownikow/outputs/high-level-design.md).
- Oryginalny audyt pozostaje zamrożony. Nowy pakiet i przebiegi nie zapisują do jego wyników.
- Dane i reguły są jawnymi, hashowanymi wejściami; unknown nie jest domyślną akceptacją ani cichym odrzuceniem.

## Open Questions / Risks

- Semantyka etykiet i macierz klas wymagają domknięcia; rzeczywiste nowe wybory polityki przedstawiamy użytkownikowi z przykładami.
- Licencja własnego kodu, dokumentacji i pakietu wynikowego wymaga osobnego ustalenia przed K10; specyfikacja jej nie narzuca.
- Pełne przebiegi mogą ujawnić ograniczenia czasu lub miejsca; wynik pomiaru zostanie zapisany przed odbiorem, bez obniżania zakresu.

## 1. Problem, użytkownicy i granice

Obecne skrypty dają audyt i pilot, ale nie listy z kontrolowaną kompletnością ani explain dla dowolnej formy. Opiekun i recenzent pracują na lokalnych plikach: manifest → inspect-sources → build → explain/przegląd → verify → export. Nie ma kont, ekranu ani usługi. Dostęp i uprawnienia wynikają z lokalnego systemu plików.

Specyfikacja realizuje [R01–R12](../analysis/requirements.md) i zakres zatwierdzony odpowiedzią A. Powstają LL-PL-BROAD oraz LL-PL-STANDARD, z pełną dopuszczalną fleksją i konstrukcjami C1. NKJP pozostaje niedostępny z podanym powodem. ATTESTED, modele wiedzy/tematów, benchmark, wdrożenie do gry i automatyczne aktualizacje pozostają poza zakresem.

## 2. Uruchomienie i organizacja kodu

Pakiet `literaki_slownik/` w katalogu głównym, uruchomienie `python3 -m literaki_slownik`. Python 3.11+, biblioteka standardowa; SQLite. `--help` oraz pomoc dla podkomend po polsku. Nie wymagamy zależności audytu: sort/curl nie są częścią kontraktu generatora. Moduły: CLI i orkiestracja, wejścia, import/baza, kwalifikacja/konstrukcje, powiązania, weryfikacja/eksport, explain. Dokładne pliki i kolejność prac określi plan.

Konfiguracje źródeł, profilu, polityki, reguł, pokrycia i próbkowania są w `config/generator/`. Kod i konfiguracje nie czytają przypadkowych katalogów ani zmiennych środowiska jako ukrytych wejść. Import modułu nie pobiera danych i nie tworzy wyników. Cache i przebiegi w `data/work/` pozostają ignorowane. Testy używają własnych małych fikstur, nie pełnego pobierania.

## 3. Manifest wejściowy i dopuszczenie

Manifest JSON ma `schema_version=1`, identyfikator projektu, listę artefaktów, polityki/reguły/profil, oczekiwane metryki importu oraz odwołania do dowodów. Każdy artefakt zawiera:

- stabilny `source_id`, nazwę, wersję/commit, URL pochodzenia i czas pozyskania;
- lokalną ścieżkę rozwiązywaną względem manifestu i SHA256 dokładnych bajtów;
- rodzaj: `sgjp_tab`, `kwjp_lemma`, `kwjp_orth`, `kwjp_orth_lc`, `kwjp_bigram` albo dokument reguł/licencji;
- rolę: `lexical`, `corpus_evidence`, `rule_evidence`, `license_evidence`; jawny `ALLOWED/BLOCKED` i zakres dopuszczenia;
- autora/właściciela, warunki/licencję, dowód, zakres, wymagane zawiadomienia i opis zależności pośrednich;
- dla KWJP reprezentację, gatunek, wersję schematu, próg publikacji, jednostkę i mianownik miar.

Niedostępne NKJP deklarujemy oddzielnie jako nieużyte źródło z powodem; nie wskazujemy go w liście aktywnych plików. Próba użycia BLOCKED, benchmark, wyłączonego pochodzenia lub niezgodnej roli/typu zatrzymuje build przed importem. Nieznany typ/rola nie przechodzi jako „inne”. Status ALLOWED nie zastępuje dowodów i właściwego zakresu. Profile startowe identyfikują dokładny SGJP i 13 plików KWJP z istniejących rejestrów audytu; fixtures mają jawny status testowy i nie mogą uzyskać produkcyjnego VERIFIED.

Sprawdzamy istnienie, zwykły plik, wersję, SHA256, format oraz wymagane dowody. Modyfikacja wejścia w trakcie pracy wykrywana jest przez ponowną kontrolę hashy przed ukończeniem. Referencje do konfiguracji/dowodów również są hashowane. Schemat odrzuca nieznane obowiązkowe wartości i sprzeczne deklaracje. Źródła dokumentacji mogą uzasadnić regułę, ale nie są importerem nowych słów. Dopuszczenie nie wynika z nazwy pliku.

## 4. Baza i zachowanie pochodzenia

SQLite: `PRAGMA foreign_keys=ON`, jawna wersja schematu, unikalności i transakcje porcjowane. Nie projektujemy migracji wcześniejszej bazy: nowe wydanie schematu wymaga nowego build. Minimalne encje:

| Encja | Tożsamość i wymagane pola |
|---|---|
| source_artifact | source_id, hash, wersja, rola, status i komplet metadanych wejściowych |
| source_record | artefakt, numer rekordu/wiersza, surowe pola i zapis oryginalny; również duplikaty |
| lexeme | artefakt + pełny ID lematu, osobno napis podstawowy do mapowania; sufiks homonimu zachowany |
| surface_form | oryginał, NFC, lower/NFC do wyszukiwania, długość i wynik profilu; bez usuwania znaków |
| interpretation | rekord, forma, leksem, surowy tag oraz rozwinięta analiza, POS, surowe pola nazw/kwalifikatorów |
| analysis / derivation_component | źródłowa interpretacja albo rekonstrukcja; wynik, reguła/wersja, uporządkowane składniki i spełnione warunki |
| variant_decision | analiza + wariant, accept/reject/unresolved, pełna lista przyczyn oraz odwołania do dowodów |
| corpus_evidence | rekord KWJP, reprezentacja/gatunek/jednostka, oryginalne miary, typowane wartości, mianownik i rank_in_file |
| evidence_link / candidate | dowód, metoda, poziom jednostki, pewność strukturalna, kandydaci i przyczyny niepewności |
| build_stage / review | statusy etapów, liczebności, wersjonowane wyniki kontroli i przeglądu |

Klucze techniczne mogą być liczbami; kanoniczny eksport używa kluczy z treści i pochodzenia, bez zależności od kolejności INSERT. Indeksy obejmują źródło/wiersz, pełny ID lematu, znormalizowany napis formy, analysis/variant oraz klucz jednostki KWJP. Przechowujemy wyłącznie kompletne powiązania przez FK. Duplikaty rekordów nie tworzą nowych leksemów ani podwójnej akceptacji; zachowujemy wszystkie miejsca pochodzenia.

SGJP importujemy strumieniowo: UTF-8 gzip, nagłówek z zawiadomieniami i pięć pól według audytu. Niepoprawny format, uszkodzony gzip lub brak końca nagłówka są błędem. Tagi z alternatywami zachowujemy surowo, rozwijamy deterministycznie; liczba rozwinięć nie jest liczbą znaczeń. Inwentaryzacja nazw i kwalifikatorów zachowuje kombinacje, nie tylko pojedyncze etykiety. Rekordy poza alfabetem/limitem gry pozostają w bazie.

KWJP: wszystkie 13 aktywnych plików, jawny parser dla typu listy, także dwa puste nagłówki bigramów. Każdy rekord i każda źródłowa miara zachowane; liczby całkowite i decimal reprezentowane bez utraty tekstu źródłowego. NaN, nieskończoność, niewłaściwe pola i uszkodzenie wejścia zgłaszają błąd z plikiem/wierszem. `rank_in_file` jest numerem danych w pliku, nie dopisaną miarą źródłową. Rozliczamy rekordy, jednostki, duplikaty i rozszerzone tagi osobno, względem przypiętych statystyk; odmienna jednostka pomiaru ma jawne uzasadnienie.

## 5. Reguły, kwalifikacja i profil gry

Konfiguracja nie jest kodem do wykonania. Rejestr reguł ma ID/wersję, zakres, warunki, efekt dla obu wariantów, źródłowe dowody, przykłady i status `confirmed/unresolved/excluded`. Implementacja obsługuje zamknięty zestaw operacji; nie używa eval/import z konfiguracji. Nie kopiujemy audytowego `audit-policy.json` jako normy.

Każda analiza jest oceniana kolejno pod względem samodzielności, kategorii, nazw, kwalifikatorów i ortografii. Wszystkie decyzje odnoszą się do tej samej analizy albo kompletu składników rekonstrukcji. Przechowujemy wszystkie przyczyny, także przy kilku odrzuceniach. Gdy potwierdzony warunek już wyklucza analizę, może ona być reject pomimo innej niewiadomej; niewiadoma pozostaje w raporcie. Gdy nierozstrzygnięcie może zmienić kwalifikację, wynik unresolved. Brak analiz jest osobnym stanem `absent`, nie reject.

Agregacja per wariant i napis: istnieje accept → accept; bez accept, z unresolved → unresolved; wyłącznie reject → reject. Akceptacja jednej analizy nie usuwa pozostałych wyjaśnień. STANDARD musi być podzbiorem BROAD; niespójna konfiguracja lub decyzja jest błędem weryfikacji, nie cichą korektą.

BROAD nie odrzuca automatycznie archaizmów, rzadkości, stylu lub specjalistyczności. STANDARD ogranicza jednoznaczną przestarzałość/historyczną pisownię według potwierdzonych etykiet. Potoczność, wulgarność, regionalność, terminologia i rzadkość same nie odrzucają. Zatwierdzone A: samo oznaczenie niezalecania nie odrzuca w BROAD ani STANDARD, przy zachowaniu pozostałych warunków. Zatwierdzone A: dodatkowe oznaczenie dawności wyklucza daną interpretację ze STANDARD mimo oznaczenia dziś; samo dziś nie wyklucza i BROAD nie odrzuca przez samą dawność. Brak kwalifikatora nie dowodzi współczesności; ograniczenie to jest opisane. Nazwa własna, skrót, symbol, zapis cyfrowy, element techniczny i niedopuszczalny segment są wykluczane na poziomie interpretacji. Zapisane słownie liczebniki nie są cyframi. Skrótowce/zleksykalizowane formy wymagają rozpoznania klasy językowej; nie zwalnia to z reguł gry. Wielka litera ani lower nie są dowodem klasy. Obowiązkowa wielka litera stanowi odrębną podstawę niedopuszczalności growej, nawet dla rzeczownika pospolitego.

Profil PL: pełny zbiór 32 liter `aąbcćdeęfghijklłmnńoóprsśtuwyzźż`, według [polityki gry](../../../research/2026-10-04-audyt-zrodel-polskich-slownikow/analysis/findings/game-policy.md). Konfigurację sprawdzamy względem kanonicznego rejestru, w tym liczebność i unikalność znaków. Długość 2–15 znaków po NFC/lower, diakrytyki zachowane. Klucz nie zawiera blanków; blank jest reprezentacją płytki, nie znakiem słowa. Forma językowo dopuszczona może być odrzucona wyłącznie przez profil; explain pokazuje oba wyniki. Nigdy nie usuwamy odstępów, dywizów, kropek ani innych znaków, by uzyskać słowo.

## Doprecyzowanie użytkownika: wpis słownikowy a gra

Wpis/analiza zachowane w bazie nie oznaczają dopuszczalności do gry. Reguł gry nie zmieniamy. SGJP jest źródłem leksykalnym, a oddzielna kwalifikacja growa stosuje obowiązujące wyłączenia do konkretnej źródłowej analizy i jej pisowni, przed agregacją do małoliterowego klucza. BROAD i STANDARD różnią się ustalonym zakresem językowym, lecz oba stosują te same niezmienione reguły gry. Listy wydania obejmują wyłącznie formy dopuszczalne do gry; baza i explain zachowują również wpisy niedopuszczalne.

Explain/raporty rozdzielają: obecność i kwalifikację językową, dopuszczalność według reguł gry, wykonalność w profilu płytek/alfabetu/długości i końcowe członkostwo w liście. Każda odmowa ma przyczynę na właściwym poziomie. Rzeczownik pospolity wymagający wielkich liter może istnieć w słowniku, a zarazem mieć odrzuconą analizę grową. Lower służy wyszukiwaniu/agregacji, nigdy dowodzeniu małoliterowej pisowni ani dopuszczeniu. Dodatnia analiza innego leksemu pozostaje niezależna.

Dowody i przypadki odbioru: [rozdzielenie wpisu i dopuszczalności](../analysis/evidence/dictionary-vs-game.md). SJP.pl sprawdzono na wyraźne polecenie użytkownika jako wzorzec rozdzielenia informacji, bez użycia list/werdyktów do budowy lub benchmarku niezależnego słownika. Nie zmieniamy źródeł leksykalnych na SJP.pl ani nie pobieramy stamtąd brakujących form.

## 6. Macierz kompletności i zadania dowodowe

Wersjonowana macierz obejmuje wszystkie zaobserwowane klasy/tagi, kombinacje nazw/kwalifikatorów, kategorie skrótowców oraz wymaganą fleksję/konstrukcje. Każdy wiersz ma zakres/warunek, źródła i ich hashe, status, przykłady dodatnie i ujemne, oczekiwane zachowanie obu wariantów, sposób kontroli pokrycia oraz liczebności pełnego przebiegu. Wyłączenie klasy wymaga dowodu pozostawania poza zatwierdzonym zakresem.

Obowiązkowe domknięcia: semantyka alternatyw i parowania etykiet; pełna tabela kwalifikatorów, w tym mieszanych; skrótowce typu PCR/PCV; pełne paradygmaty i defektywność; praet/cond/winien, wyjaśnienie nadmiarowych trójek kontroli audytu; osobno bym/byśmy; przyimek+-ń z przypadkiem, liczbą i wokalicznością; rozkaźnik+-ż/-że oraz ich podwojenia; mobilne końcówki; współczesna i historyczna ortografia, w tym granice łącznej pisowni by/nie. Każde domknięcie wymaga dowodu źródłowego, a nie samej udanej analizy lub korpusowego wystąpienia.

Preferujemy kompletne formy SGJP; rekonstrukcja wymaga wszystkich składników z tego eksportu, potwierdzonej reguły, ograniczeń i dziedziczenia kwalifikacji. Nie tworzy nowego leksemu. Nie aktywujemy szerokich reguł permissive, produktywnych prefiksów ani swobodnego sklejania. Rekonstrukcja już obecna w eksporcie zachowuje alternatywny ślad, lecz nie dubluje formy w liście. Potwierdzenie negatywnego przykładu jest równie wymagane jak dodatniego.

Inwentaryzacja niewiadomych ma ID, źródłowe przykłady, wpływ na wariant, liczbę analiz/form i wpływ na wymaganą kompletność. Niewiadoma zmieniająca listę lub pokrycie blokuje pełne wydanie. Zwolnienie blokady wymaga wykazania braku wpływu albo rozstrzygnięcia z dowodem; dowolna flaga operatora nie wystarcza. Techniczny build może się zakończyć z unresolved, ale zadanie G1 nie jest wtedy ukończone.

## 7. Powiązania KWJP i braki

Mapowanie POS i normalizacji jest jawne, wersjonowane i poparte przeglądem. Pełny ID leksemu nie jest skracany; usunięcie sufiksu dopuszczalne tylko w kluczu wyszukiwania kandydatów. Metody: dokładna forma/NFC; forma orth_lc według reguły źródłowej; lemma+POS. Bigram zachowuje dwa segmenty i może wskazywać kandydatów, lecz sam nie dowodzi częstości sklejonego słowa. Nie sumujemy częstości segmentów, by wyliczyć pełną formę.

Dowód przechowuje F i inne miary raz, na jednostce i liście. Linki wielu leksemów wskazują ten rekord, nie kopiują F jako potwierdzenia każdego sensu. Zgodny lemma/POS oznacza dopasowanie strukturalne, nie pewną tożsamość znaczenia. All, gatunki, lemma, orth i orth_lc pozostają odrębne; nie sumujemy ich. Zachowujemy IPM i jego mianownik per lista, DP/DP_norm/1-DP odrębnie, Dice bez przemianowania na logDice. Brak korpusowy nie odrzuca BROAD/STANDARD.

| Status | Warunek / wartość |
|---|---|
| OBSERVED | Źródłowy rekord i wartość, także rzeczywiste zero miary |
| ABSENT_OR_BELOW_PUBLICATION_THRESHOLD | Brak porównywalnej jednostki w liście z potwierdzonym dolnym progiem; wartość null |
| NOT_IN_PUBLISHED_LIST | Niepewna tokenizacja albo inny/nieustalony dobór listy; null |
| UNMATCHED | Nie ustalono wiarygodnego mapowania między jednostkami; null |
| NOT_APPLICABLE | Miara nie dotyczy typu jednostki; null |
| UNAVAILABLE | Źródło/lista nieużyta lub niedostępna; null i powód |

W genre wartości F=1–4 zachowujemy. Brak genre nie jest automatycznie globalnym progiem 5. Dla segmentowanych form takich jak czytałem nie twierdzimy, że znamy F=0–4. Explain zawiera niepewność i kandydatów; brak w źródle słów i brak w korpusie to inne stany.

## 8. Kontrakt CLI

Wszystkie komendy: `--json` daje jeden obiekt UTF-8 na stdout, diagnostyka na stderr; bez flagi czytelny polski tekst. Odpowiedź ma `schema_version`, `command`, `status`, wyniki/ścieżki i listę diagnostyk z kodem, opisem, źródłem/wierszem. Argumenty ścieżkowe są jawne. Kody wyjścia: 0 operacja ukończona; 2 argumenty/schemat; 3 wejścia/hash/rola; 4 import lub błąd operacyjny; 5 niespełniona weryfikacja/odmowa wydania; 130 przerwanie. Wynik explain reject/unresolved/absent nie jest błędem komendy.

| Komenda | Kontrakt |
|---|---|
| `inspect-sources --manifest PATH` | Bez zmian źródeł i bazy. Sprawdza aktywne wejścia i konfiguracje; raport per artefakt, nieudana kontrola daje 3. Brak NKJP wskazany jako oczekiwane ograniczenie. |
| `build --manifest PATH --run-dir NEW` | Odmowa istniejącego katalogu; import, konstrukcje, decyzje, powiązania i raporty. Sukces techniczny nadal INCOMPLETE. Bez pobierania i automatycznego export. |
| `explain --run-dir PATH --word WORD --variant broad\|standard` | Domyślnie standard. NFC/lower tylko do wyszukania wszystkich zapisów; pokazuje zapytanie, językową agregację, profil gry, źródła, analizy, przyczyny, konstrukcje i KWJP. |
| `verify --run-dir PATH --peer-run PATH --review PATH` | Kontroluje K1–K10, identyczność kanonicznych wyników z drugim build i związany hashami przegląd; kompletne powodzenie ustawia VERIFIED. W przeciwnym razie raport blokad i 5. |
| `export --run-dir PATH --output-dir NEW` | Powtarza kontrolę spójności VERIFIED i hashy, bez ponownego kosztownego budowania; zapisuje nieistniejący pakiet i ustawia FROZEN po poprawnym zakończeniu. Odmowa dla INCOMPLETE, zmienionych plików lub istniejącego celu. |

Build bez pełnych reguł może dać użyteczną bazę diagnostyczną. Nie istnieje `--force` omijający kryteria ani sposób przemianowania diagnostycznej listy na pełny pakiet. Explain dla failed build zgłasza niekompletność i nie twierdzi, że brak w częściowej bazie oznacza brak w całym źródle. Domyślne wyniki JSON zawierają wszystkie analizy; szczególnie duże zapytanie może zapisywać pełny raport do wskazanego pliku, bez cichego ucięcia.

## 9. Cykl przebiegu, awarie i integralność

Katalog zawiera `build.sqlite`, `manifest.json`, `reports/` i log zdarzeń. Etapy: preflight, import_sgjp, import_kwjp, constructions, decisions, links, reports; status pending/running/complete/failed. Gotowość wydania jest osobna: INCOMPLETE/VERIFIED/FROZEN. Utrwalony running po awarii jest nieukończony. Weryfikacja wymaga wszystkich etapów complete i kontroli bazy (`integrity_check`, FK).

Transakcje domyślnie do 10 000 rekordów; commit porcji nie oznacza ukończenia pliku. Błąd wskazuje etap i rekord; brak miejsca, zły gzip, zmiana źródła, błędny SQL oraz przerwanie nie dają complete. Obsługiwane przerwanie zapisuje failed o ile system plików pozwala; twarda awaria pozostawia running. Ponowienie: nowy katalog, bez skomplikowanego resume wewnątrz pliku. Nie czyścimy ani nie zastępujemy poprzednich wyników.

Manifesty/raporty zapisujemy do pliku tymczasowego i atomowo zastępujemy wyłącznie plik należący do bieżącego przebiegu. Export przygotowuje katalog staging obok docelowego i dopiero po hashach przenosi do nowego celu; istniejący cel nigdy nie jest nadpisywany, także przy wyścigu. Awaria może zostawić oznaczony staging, nie gotowy pakiet. Baza FROZEN jest czytana tylko do odczytu; export pozostaje możliwy do weryfikacji bez modyfikacji danych językowych. Późniejsze zmiany plików unieważniają zapisany verdict.

## 10. Raporty, przegląd i powtarzalność

Manifest identyfikuje SHA256 wejść, konfiguracji, dowodów, kodu i wyników; commit i stan dirty kodu, Python/SQLite/Unicode, porządek sortowania, komendy oraz czasy. Dirty build nie uzyskuje pełnego VERIFIED, dopóki użyty kod nie jest utrwalony i odtwarzalny. Porządek list: rosnący Unicode po NFC/lower, niezależny od locale. Kanoniczny JSON: posortowane klucze, jawna kolejność rekordów, UTF-8 i LF; treść identyfikowana przez źródłowe klucze, bez czasów/ścieżek lokalnych/technicznych ID. Fizyczne bajty SQLite nie są kryterium identyczności.

Raporty: import/counts, inventory, unknowns, coverage, links, filter-impact, quality-sample, performance i verification. Dla filtrów: samodzielny efekt, efekt kolejny przy ustalonej kolejności z §5, łączny efekt, odrzucone analizy oraz faktycznie utracone unikalne formy. Nie sumujemy nakładających się kategorii. KWJP nie jest filtrem dopuszczalności.

Próbkowanie przed pomiarem: wersja `quality-v1`, seed `literaki-slownik-g1-v1`; dla każdej warstwy wybieramy do 30 różnych kluczy o najmniejszym SHA256(seed + identyfikator warstwy + klucz), wszystkie gdy mniej. Warstwy słowne: długość 2–3, homonimia, historia, fachowe, zbieżność nazwy/pospolitego, każda klasa konstrukcji, zmiana decyzji przez filtr, unresolved. Dla linków: do 30 rekordów dla każdej metody i kategorii zgodne/niejednoznaczne/niedopasowane. Raport określa populację, rozmiar, wybrane klucze i nakładanie prób. Zero elementów nie jest dowodem pokrycia wymaganej klasy.

Przegląd zapisuje pełne analizy, ocenę poprawne/błędne/niewiadome, źródłowe uzasadnienie, identyfikator przeglądającego i hash przebiegu. K4 wymaga ponadto kompletnych testów macierzy klas; próba nie zastępuje kontroli kompletności. Każdy wykryty błąd zmieniający skład list/pokrycie lub błędnie przedstawiający link jako pewny blokuje verdict. Poprawka wymaga nowego build i ponownego odbioru; nie edytujemy ręcznie eksportów. Próbka nie jest statystycznym zapewnieniem bezbłędności całego zbioru.

Pomiar pełnego build: czasy etapów, liczba rekordów, peak RSS z opisem platformy/metody, rozmiar bazy, czas explain dla zapisanej próby i dwa odtworzenia. Strumieniowy import i porcjowanie są wymaganiem; konkretne limity czasu/RAM wynikają z pomiaru i ewentualnej decyzji, nie zostają zmyślone. Brak zasobów jest jawną blokadą, nie uzasadnia zastąpienia pełnego wyniku pilotem.

## 11. Weryfikacja i pakiet wydania

| ID | Obowiązkowe dowody / warunek powodzenia |
|---|---|
| K1 | Wszystkie aktywne wejścia dozwolone w roli, hashe/dowody/atrybucje poprawne; testy BLOCKED, benchmark, obce pochodzenie i niezgodny hash odrzucane |
| K2 | Pełne importy rozliczone z przypiętymi metrykami, bez cichej utraty; poprawne surowe dane i jednostki |
| K3 | STANDARD ⊆ BROAD, kompletna zaakceptowana analiza każdej formy, homonimy i brak łączenia warunków między analizami |
| K4 | Kompletna macierz wymaganych klas, dodatnie/ujemne dowody i testy, wyjaśniona nadgeneracja, poprawne składniki rekonstrukcji |
| K5 | Brak nierozstrzygnięć zmieniających listy lub wymaganą kompletność; wszystkie pozostałe ograniczenia opisane z dowodem braku wpływu |
| K6 | F raz przy jednostce, brak imputacji, poprawne statusy/miary, przegląd mapowania i linków |
| K7 | Runtime explain: accept, reject, unresolved, absent, rekonstrukcja, homonimy, odrzucenie przez profil i brak KWJP |
| K8 | Dwa niezależne pełne build dają identyczne listy i kanoniczne raporty merytoryczne; testy przerwania i zachowania poprzednich wyników |
| K9 | Pełny raport filtrów oraz dobrana i przejrzana próba jakościowa; naprawione blokujące błędy |
| K10 | Manifest pakietu, atrybucje, ograniczenia, warunki publikacji kodu/dokumentacji/list/raportów; osobne warunki bazy, jeśli redystrybuowana |

Verify zapisuje wynik per K, dowody i blokady. Nie wystarcza tekst „przegląd zatwierdzony”: plik review musi dotyczyć właściwych hashy, zawierać wymagane próbki, rozstrzygnięcia i dowody. Kontrole automatyczne i przegląd językowy mają różne statusy. Wszystkie K są wymagane dla pierwszego pełnego VERIFIED; brak NKJP jest przewidzianym ograniczeniem N1, nie naruszeniem K6.

Pakiet: `LL-PL-BROAD.txt`, `LL-PL-STANDARD.txt` (UTF-8 bez BOM, LF, ostatni LF, unikalny klucz na wiersz), `release-manifest.json`, kanoniczne raporty, `ATTRIBUTIONS.md`, `LIMITATIONS.md` i warunki udostępnienia. Manifest podaje zakresy hashy; nie hashuje sam siebie rekurencyjnie. Hash manifestu może być zapisany w zewnętrznym indeksie przebiegu. Baza jest powiązana identyfikatorem/hashami logicznej treści i ścieżką archiwum, nie musi być publicznym plikiem pakietu. Atrybucje obejmują faktycznie użyte źródła i opis zmian; nie przypisują własności materiałom zewnętrznym.

## 12. Testy, dokumentacja, aktualizacja i rollback

Test-first w grupach implementacji. Syntetyczne fikstury: poprawne/uszkodzone gzip/CSV, mieszane etykiety, dwa homonimy z przeciwnymi decyzjami, warunki spełniane przez różne analizy, skróty vs liczebniki, konstrukcje dodatnie/ujemne, profile NFC/znaki/limity, KWJP progi i niepewna tokenizacja, wielokrotne linki jednego F, przerwanie, istniejący katalog, naruszone hashe i deterministyczne dwa małe przebiegi. Pełny odbiór używa rzeczywistych źródeł i dwóch pełnych build, nie samych fixtures. Audytowe testy pozostają niezmienione i uruchamiane jako regresja. Szczegółowe komendy, pliki i pokrycie będą w planie.

Dokumentacja polska w `docs/`: szybki start, jawne pozyskanie wejść, manifest/profil/polityki, przykłady CLI i explain, statusy/błędy, przegląd/weryfikacja, pakiet/atrybucje, powtarzalność i aktualizacja. README wskazuje etap i instrukcję; AGENTS wyraźnie rozróżnia historyczny etap audytu od obecnej implementacji. Zachowujemy prompt i stare artefakty bez zmian.

Nowe źródło, reguła lub schemat oznacza nową wersję i nowy katalog; raport różnic decyzji/liczebności i ponowny K1–K10. Nie podmieniamy istniejącego źródła ani pakietu. Nie wdrażamy wyniku do gry. Rollback operatora polega na ponownym wskazaniu wcześniejszego zamrożonego pakietu, bez jego zmiany; usuwanie przebiegów lub cofanie commitów wymaga osobnej zgody. Zmiana architektury/zakresu albo niewynikająca ze źródeł decyzja językowa wraca do użytkownika przed wykonaniem.

## 13. Bramka specyfikacji

Rekomendacja A: zatwierdzić kontrakty i kryteria; następnie wykonać audyt specyfikacji i przygotować plan do osobnego zatwierdzenia. B: wskazać korektę. Zatwierdzenie dokumentu nie oznacza, że finalne reguły językowe lub warunki publikacji zostały już dowiedzione. Ich ustalenie pozostaje obowiązkowym zadaniem implementacji.

## Źródła społecznościowe — decyzja użytkownika

Wikisłownik i podobne źródła społecznościowe odkładamy na później. W bieżącej fazie nie używamy ich do budowy słownika ani rozstrzygania dopuszczalności. Zachowujemy przypięte dane SGJP i KWJP oraz ich odrębne role; KWJP nie jest dowodem poprawności konstrukcji. Brakujące poświadczenia pozostają unresolved — nie oznaczają odrzucenia formy i nie pozwalają deklarować pełnego wydania. Dotychczasowe audyty pozostają materiałem historycznym, bez aktywacji ich danych.

## Zakres użycia — postęp G3/G4

Wdrożono zatwierdzony niewykluczający zakres potoczności, wulgarności, regionalności, gwarowości i rzadkości dla 15 sprawdzonych dosłownych etykiet. Inne składniki oraz pełna polityka nadal wymagają domknięcia. Oznaczenie niepopr. rozstrzygnięto A: odrzuca konkretną interpretację w obu wariantach; nie jest utożsamione z niezal.

## Niepoprawność — zatwierdzone A

Zatwierdzone A: jawne niepopr. odrzuca konkretną interpretację w BROAD i STANDARD. Wdrożono 27 sprawdzonych dosłownych etykiet, zachowując wpisy i inne analizy. Niezal. pozostaje odrębne i niewykluczające; nieznane etykiety wymagają oceny. Pełna polityka i członkostwo w listach nadal nieukończone.

## Etykiety opisowe i diagnostyka konstrukcji — postęp

Dodano niewykluczające oznaczenia dziedzin, stylu i wariantów formy: 357 sprawdzonych dosłownych etykiet, 73 oznaczenia dziedzin, 18 stylu/użycia i 2 wariantów. Nowy warunek nie obejmuje mieszanek z nieznanymi ograniczeniami. Explain odtwarza teraz kandydatów potwierdzonych konstrukcji impt + jedna partykuła oraz by + nwok aglt z rzeczywistych składników importu, bez zapisu do bazy i bez końcowego dopuszczenia. Warunek kontekstu zatwierdzono osobnym A; pozostałe konstrukcje i pełna macierz pozostają otwarte.

## Zatwierdzony warunek kontekstu

Zatwierdzono A: samo wymaganie kontekstu składniowego lub frazeologicznego nie wyklucza poprawnej formy w BROAD ani STANDARD. Wdrożono zamkniętą mapę 11 dosłownych etykiet; explain zachowuje source_label i required_context. Dawność, niepoprawność, niesamodzielne składniki i pozostałe kryteria oceniane są osobno. Pełny odczyt 7 458 520 rekordów potwierdził 169 rekordów kontekstu; pięć rzeczywistych zapytań bez zapisów do bazy. Pełna kwalifikacja i integracja build nadal nieukończone.

## Raport pokrycia warunków — postęp

Dodano deterministyczny raport qualifier-conditions.json do nowych build oraz tryb qualifier-conditions skryptu probe. Raport obejmuje pełne surowe pola i dosłowne etykiety; nie dzieli przecinków. Wskazuje znane warunki obu wariantów oraz etykiety bez żadnego warunku, zachowując pełną kwalifikację jako pending. Nie nadaje VERIFIED i nie kończy etapu reports. Pełne dane: 7 458 520 interpretacji, 615 pól, 605 etykiet; 26 etykiet bez warunku w 1 910 interpretacjach. Dwa kanoniczne odtworzenia identyczne, źródłowa baza tylko odczytywana.

## Utrwalanie potwierdzonych konstrukcji — postęp

Nowe build zapisują potwierdzony podzbiór konstrukcji do derivation_candidate i derivation_component, z kluczem treści SHA256 oraz FK do surowych składników. Nie tracimy homonimów i bezpośrednich wpisów. Explain pokazuje persisted_candidate_key; stare bazy pozostają czytelne bez migracji. Pełna kwalifikacja i inne klasy nadal otwarte, constructions pending, INCOMPLETE. Pełny przegląd potwierdzonych klas: 92 622 źródłowe interpretacje impt, 2 by i 4 nwok aglt, 93 446 kandydatów i 186 892 składniki; powtórzenie bez nowych kandydatów, FK/integrity OK.

## Powiązania KWJP w build — postęp

Komenda build tworzy bezpośrednie powiązania wszystkich zaimportowanych jednostek KWJP i reports/links.json; F pozostaje przy jednostce korpusu. Raport wskazuje osobno listy/gatunki i źródła niedostępne. Pełne powiązania konstrukcji nadal otwarte: links pozostaje pending, a wynik INCOMPLETE. Błąd zapisu powiązań oznacza links failed, zachowując zakończone importy. Testy generatora 106/106 i audytu 5/5 przeszły.

Decyzja o sile dowodu dla kontrakcji została [zatwierdzona A](../analysis/evidence/contraction-proof-decision.md).

## Kontrakcje i powiązania konstrukcji — postęp

Wdrożono zatwierdzone A: 57 rozwiniętych analiz 18 dosłownie wskazanych form SGJP ma dowód językowy; 24 analizy ośmiu pozostałych form pozostają nierozstrzygnięte. Build i explain zapisują pełne składniki i zachowują homonimy. Zamknięta grupa 16 hostów z_aglt_by daje 64 kandydatów zgodnych z klasą źródłową. KWJP orth/orth_lc wiąże całe konstrukcje przez candidate_key, bez dziedziczenia częstości rdzenia. Explain czyta starsze bazy. Siedem errat winien jest adnotacją zależną od hasha źródła. Pełna polityka, pozostałe klasy i wydanie nadal wymagają ukończenia.

## Połączony runtime i warunki publikacji

Połączona kontrola wszystkich wdrożonych konstruktorów: 93 071 źródłowych interpretacji, 93 591 kandydatów i 187 182 składniki. Powtórzenie daje identyczny digest i zero nowych kandydatów, FK/integrity OK. To projekcja klas z pełnego źródła, nie pełny build G8. Warunki własnych materiałów zatwierdzono A i zapisano z oddzielnymi atrybucjami źródeł. Pełna macierz i listy pozostają nieukończone.

## Norma 2026 — wymagany wybór

Sprawdzono wszystkie 70 definicji zamkniętych klas mobilnych hostów. Rozbieżność SGJP z normą 2026 przy nieoznaczonych jeśliby/jeżeliby wymaga [decyzji przed zmianą kwalifikacji](../analysis/evidence/orthography-2026-decision.md). Reguły gry pozostają bez zmian.

## Norma 2026 i dalsze mobilne końcówki — postęp

Wdrożono A dla normy 2026: dokładne analizy comp jeśliby/jeżeliby i ich składniki konstrukcyjne mają odrzucenie STANDARD; BROAD nie wyklucza przez samą dawną pisownię. Nie usunięto wpisów i nie zmieniono reguł gry. Dodano kandydatów mobilnych końcówek dla trzech pozostałych zamkniętych klas, z kontrolą lematu, POS, wokaliczności, źródła i śladów. Odmienne formy niezgodne z wariantem źródłowej klasy wymagają dalszej oceny; pełna macierz i kwalifikacja nadal otwarte.

## Runtime i następna bramka zakresu

Rzeczywista kontrola nowych mobilnych klas: 312 kandydatów i 624 składniki, identyczny digest przy powtórzeniu, FK/integrity OK. Osiem różnic wariantu klasy i odmienionej formy rozstrzygnięto przez SGJP §6.4.1; adnotacja zachowuje oba warianty. Generator 122/122, audyt 5/5. Wymagana decyzja o zakresie ośmiu niepoświadczonych kontrakcji pozostaje pending; brak wyłączenia przed odpowiedzią. [Warianty zakresu](../analysis/evidence/remaining-contractions-scope-decision.md).

## Zatwierdzona korekta zakresu pierwszego wydania

A zatwierdzone i wdrożone: zakres kontrakcji pierwszego wydania obejmuje 18 poświadczonych form (57 analiz), osiem innych (24 analizy) pozostaje diagnostycznie poza zakresem. Ocena językowa niewiadoma nie została zmieniona na błędność. Nowa warstwa release_scope jest oddzielna od języka, gry i profilu; członkostwo jest oceniane dla pojedynczej analizy, więc homonimy nie są tracone. Nie zmieniono kluczy ani treści utrwalonych kandydatów. Dodano zamknięte źródłowe sekwencje host+partykułowe by+(opcjonalna końcówka nwok), z pełnymi 2/3 składnikami i odrębną oceną pisowni normy2026.

## Kontrola zakresu i następna decyzja

Kontrola wszystkich bieżących klas poza impt: 536 interpretacji wejściowych, 770 kandydatów i 1784 składniki; w tym 305 sekwencji host+by+(opcjonalna końcówka). Powtórzenie: zero nowych kandydatów, identyczny digest; FK/integrity OK. Zakres kontrakcji pozostaje 57/24. To projekcja wymaganych wejść konstruktorów z pełnego G2, nie pełny build G8.

[Wymóg objaśnień 25 oznaczeń](../analysis/evidence/unexplained-labels-first-release-decision.md) pozostaje pending. Nie aktywowano odstępstwa; inne wymagania pozostają wiążące.

## Zatwierdzone A: oznaczenia bez objaśnień

Wdrożono A dla25dosłownych oznaczeń bez pełnego objaśnienia: source_label zachowany, gloss_status=unestablished, inne kryteria osobno. Pełny runtime:1908kompaktowych analiz, dwa identyczne raporty, sześć readonly explain; wielka litera Abchaz nadal odrzuca growo. Dodano logical-content bieżącego schematu do build:10zamkniętych relacji, klucze źródłowe zamiast ID, wykrywanie nowych tabel/kolumn i niespójnych FK. Testy potwierdzają identyczność po zmianie ID i zmianę hasha po modyfikacji powiązań/kwalifikatorów. To nie pełny indeks kanoniczny ani odbiór G8.

[Adnotacja akcent](../analysis/evidence/accent-gloss-first-release-decision.md) pozostaje pending, bez rozszerzenia wyjątku przed odpowiedzią.
