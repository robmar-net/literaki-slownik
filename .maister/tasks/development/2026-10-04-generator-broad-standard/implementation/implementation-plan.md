# Plan implementacji generatora BROAD i STANDARD

## TL;DR

Dziewięć grup i 36 kroków obejmuje narzędzie, dowody językowe i pełny odbiór K1–K10.
Wykonanie sekwencyjne: fundament → import → dowody → reguły → KWJP → explain/raporty → wydanie → dwa pełne przebiegi → dokumentacja.
Każda grupa kodowa zaczyna od testów; pilot i INCOMPLETE nie są końcowym wynikiem.
Status: plan zatwierdzony przez użytkownika odpowiedzią A; implementacja rozpoczęta.

## Key Decisions

- Wiążące wejścia: [specyfikacja](spec.md), [wymagania](../analysis/requirements.md), [audyt specyfikacji](../verification/spec-audit.md), G1/N1/C1.
- Wszystkie pliki wspólne edytuje koordynator. Brak równoległych zapisów i nakładającej się odpowiedzialności.
- Odbiór techniczny nie zastępuje źródłowego rozstrzygnięcia macierzy klas i przeglądu jakości.
- Najbliższa praca G3: własny przegląd znaczeń na dostępnych materiałach PAN (PAN-1–PAN-5), bez kontaktu z innymi grupami; aktywacja filtrów wymaga omówienia wpływu.

## Open Questions / Risks

- G3 może ujawnić rzeczywisty wybór polityki językowej; wtedy przedstawiamy przykłady użytkownikowi, bez arbitralnego filtra. Doprecyzowanie użytkownika: reguł gry nie zmieniamy; odróżniamy wpis od dopuszczalności, nie głosujemy nad zniesieniem istniejących wyłączeń.
- Przed K10 trzeba ustalić warunki publikacji własnego kodu/dokumentacji/wyników; zakres nie jest zmniejszany, jeśli wymaga to decyzji.
- G8 mierzy pełny koszt dwóch przebiegów; brak zasobów pozostaje blokadą do rozwiązania.

## 1. Zasady wykonania i kontrakty wspólne

Executor: maister-implementation-plan-executor; pełny kontrakt trzeba wczytać przed G1. Środowisko Python 3.11+, biblioteka standardowa, lokalne SQLite. Nie dodajemy usług ani frameworka. Obowiązuje AGENTS, polski język dokumentacji, zachowanie materiałów obcych z polską metryczką i brak surowych danych w Git. Prompt, skrypty audytu i hashowane wyniki research pozostają niezmienione.

Wszystkie grupy należą do koordynatora. Oczekiwane pliki poniżej są granicami odpowiedzialności, nie pretekstem do utworzenia pustych modułów. Można połączyć drobne funkcje w zadeklarowanym module bez zmiany zachowania; nowa architektura lub odmienny model danych wymaga ponownego rozstrzygnięcia. Plany/stan/dashboard/log aktualizuje wyłącznie koordynator.

Testy w `tests/`, odkrywanie `python3 -m unittest discover -s tests -p 'test_*.py'`. Każda grupa kodowa: właściwe fikstury i testy → potwierdzony red → najmniejsza implementacja → green. Nie zapisujemy fikcyjnego red ani nie piszemy testu powtarzającego algorytm. Dokumentacja nie wymaga osobnych testów; sprawdzamy instrukcje na gotowym CLI. Baseline audytu: `python3 -m unittest discover -s scripts -p 'test_audit_sgjp.py'`.

Doprecyzowania I1–I3 z audytu, jawnie objęte zatwierdzeniem tego planu:

- Verify ocenia przyszły pakiet w roboczym `candidate/`: dwa pliki list, raporty, atrybucje, ograniczenia i deklarację warunków. Ma oznaczenie INCOMPLETE i nie jest samodzielnym wydaniem. Export materializuje dokładnie zweryfikowane bajty w nowym celu, porównuje hashe i dopiero wtedy nadaje FROZEN.
- `canonical-index.json` wiąże listy robocze i kanoniczne raporty: import/counts, inventory, unknowns, coverage, decyzje/analizy, pochodzenie, links, filter-impact i quality-sample. Czas/RSS, log, lokalne ścieżki, wynik verify, review z czasami i fizyczne bajty SQLite nie są porównaniem dwóch build. Review jest osobno związany hashami indeksu i dowodów. Hash logical-content obejmuje wszystkie merytoryczne relacje bazy, nie tylko liczbę słów.
- Dobór próbki: SHA256 UTF-8 kanonicznej tablicy JSON `[seed, warstwa, klucz]`, bez spacji, stabilny klucz rozstrzyga remis. Wersja quality-v1, seed i do 30 jednostek na warstwę pozostają zgodne ze specyfikacją.

## 2. Zależności i punkty kontrolne

`G1 → G2 → G3 → G4 → G5 → G6 → G7 → G8 → G9`. G2 umożliwia pełną inwentaryzację do G3; G3 domyka dowody przed aktywacją reguł G4. Przy rzeczywistej blokadzie dowodowej można wykonać niezależne prace importu/KWJP/explain, jednak nie zaznaczać G3/G4/G8 jako ukończonych i nie kończyć G1 wynikiem częściowym.

Po grupie: ukierunkowane testy, checkboxy i krótki log red/green, dowody/ryzyka; nie powtarzamy całej suity po każdej zmianie dokumentu. Commit po większym spójnym przyroście oraz przed pełnymi przebiegami, aby użyty kod był utrwalony; bez commitów po każdym kroku. Na koniec całość commit/push.

W każdym kroku rollback oznacza zatrzymanie nowego przebiegu i zachowanie poprzednich plików. Nie usuwa się katalogów, nie cofa Git i nie zmienia wcześniejszego wydania bez zgody. Do trzech prób grupy według executora; powtarzająca się awaria lub zmiana założeń zatrzymuje wykonanie do rozstrzygnięcia.

## 3. Grupy i kroki

### G1 — manifest, CLI i bezpieczny katalog przebiegu

Zależności: zatwierdzony plan. Pliki: `literaki_slownik/{__init__,__main__,cli,inputs,run,canonical}.py`, `tests/{__init__,helpers,test_inputs,test_run,test_cli}.py`, `config/generator/{sources,profile,quality}.json`. Kontrola K1/K8; R01/R08/R11.

- [x] 1.1 Test-first: manifest poprawny/błędny, role, BLOCKED/benchmark/wyłączone pochodzenie, hash, ścieżki względne i istniejący katalog; fixtures jawnie testowe.
- [x] 1.2 Wdrożyć jawny schemat wejść i inspect-sources, SHA256 strumieniowo, typy/role/proweniencję, metadane źródeł/dowodów oraz profil 32 liter/2–15.
- [x] 1.3 Wdrożyć szkielet CLI i obsługę kodów wyjścia/JSON/stderr, statusy etapów i atomowy manifest; nowe katalogi bez nadpisywania; brak efektów importu modułu.
- [x] 1.4 Green dla testów G1; `python3 -m literaki_slownik --help` i `inspect-sources --help`; przejrzeć zmapowanie 1 SGJP/13 KWJP względem rejestrów, nie dopuszczać fikstury do produkcyjnego VERIFIED.

### G2 — baza oraz pełne parsery/import

Zależności: G1. Pliki: `literaki_slownik/{database,sgjp,kwjp,build}.py`, `literaki_slownik/schema.sql`, `tests/{test_database,test_sgjp,test_kwjp,test_build}.py`. K2/K8; R02/R08.

- [x] 2.1 Test-first: UTF-8/gzip, pięć pól, brak nagłówka, duplikaty, pełne ID homonimu i rozwinięcia tagów; CSV lemma/orth/orth_lc/bigram, puste nagłówki, decimal/zera, uszkodzenie i błąd po commicie porcji.
- [x] 2.2 Wdrożyć schemat/FK/unikalności i strumieniowe importy z porcjami do 10 000 rekordów, surowe zapisy i odrębne jednostki; failed/running nie oznacza kompletności.
- [x] 2.3 Dodać rozliczenie importu, indeksy wyszukiwania i pełną inwentaryzację tagów/kombinacji; uruchomić pełny import przypiętych źródeł w nowym katalogu diagnostycznym, bez wydania.
- [x] 2.4 Green dla G2 i baseline audytu; zachować raport rzeczywistych metryk versus manifest/rejestry, jawnie wyjaśnić różnice jednostek, nie zmieniać historycznych statystyk.

### G3 — domknięcie dowodów językowych i mapowania

Status częściowy: pełna inwentaryzacja, defektywność próby i mapowanie lemma-all sprawdzone. [Przegląd](../analysis/evidence/g3-review.md) oraz [bramka dodatkowych wejść](../analysis/evidence/source-extension-decision.md); żaden krok nie jest oznaczony complete przez częściowy wynik.

Zależności: G2. Pliki: `docs/generator/{etykiety,konstrukcje,ortografia,mapowanie-kwjp}.md`, `config/generator/{evidence,coverage,qualifiers,categories,pos-map,constructions,orthography}.json`, ewentualnie `scripts/probe_generator_evidence.py`; nowe wyniki w `analysis/evidence/` tego zadania. K4/K5/K6; R04/R05/R06.

- [ ] 3.1 Przeanalizować wszystkie rzeczywiście występujące pola/kombinacje nazw i kwalifikatorów oraz klasy skrótowców; ustalić semantykę na źródłach pierwotnych, policzyć wpływ i zachować przykłady, m.in. PCR/PCV.
- [ ] 3.2 Domknąć pełne paradygmaty/defektywność i osobowe praet/cond/winien; wyjaśnić nadmiarowe trójki kontroli audytu; macierz bym/byśmy, przyimek+-ń, rozkaźnik+-ż/-że/podwojenia i mobilne końcówki.
- [ ] 3.3 Udokumentować dziedziczenie kwalifikacji, ograniczenia składników i ortografię BROAD/STANDARD oraz mapowanie POS/KWJP; wersje/hash/dowody i dodatnie/ujemne przypadki każdej klasy.
- [ ] 3.4 Przejrzeć pełną macierz i nierozstrzygnięcia, zapisać status/dowód/zakres/liczebność; materialny wybór polityki przedstawić z przykładami. Ukończenie wymaga domknięcia, nie etykiety „później”.

Doprecyzowanie zatwierdzone A (2026-10-04T14:40:29Z): audyt oficjalnych metadanych SGJP oraz niezależnych poświadczeń istniejących konstrukcji. Nowe artefakty po pozytywnym audycie warunków wymagają pełnej metryki, mapowania do przypiętego eksportu, hasha i testów odmowy przy BLOCKED/nieznanym pochodzeniu. Bez nowych leksemów i zmiany reguł gry. Dotąd nie aktywowano uzupełniającego artefaktu; brak licencjonowanego snapshotu pozostaje rzeczywistą luką.

G3 to badanie źródłowe, bez z góry obiecanego wyniku. Pobieranie nowych dokumentów tylko w zadeklarowanej roli po sprawdzeniu warunków; bez danych benchmarku lub internetowych list haseł. Dokumentacja językowa nie staje się importerem słów. Ustalenia muszą dać przykłady do niezależnych testów G4/G5; nie dopisujemy intuicyjnych wyjątków.

### G3 — samodzielny przegląd znaczeń na materiałach PAN

Doprecyzowanie G3.1/G3.3/G3.4 na prośbę użytkownika; nie dodaje dziesiątej grupy ani nie zmniejsza zakresu odbioru. Wstępne rozpoznanie źródeł już wykonano w [przeglądzie PAN](../analysis/evidence/pan-data-recheck.md); poniższe działania wymagają pełnego przeglądu przypadków. Nie kontaktujemy się z innymi grupami.

| Etap | Wynik | Praca do wykonania |
|---|---|---|
| PAN-1 | Inwentaryzacja przypadków | Wyprowadzić z pełnego SGJP rekordy wymagające przeglądu, z pełnym ID, tagiem, nazwami, kwalifikatorami i powodem. Zacząć od zamkniętej populacji 147 analiz frag; następnie nazwy mieszkańców obu rodzajów i pozostałe wyjątki znaczeniowe. Sufiksy i statystyki służą tylko do wyszukiwania kandydatów, nie dowodzą kompletności klasy. |
| PAN-2 | Zebranie dowodów PAN | Powiązać przypadki z przyjętymi listami lemma/orth/orth_lc/bigram i sprawdzonymi próbkami KWJP½M. Sprawdzić dostępne glosy/uwagi/odsyłacze SGJP oraz dokumentację. Zarejestrować także rzeczywisty brak dostępu lub brak potrzebnych wartości; nie zakładać gotowego eksportu glos. Zapisać URL, wersję, hash, warunki, bibliografię i ID/numer próbki; surowe materiały poza Git. |
| PAN-3 | Przegląd i mapowanie znaczeń | Przejrzeć dowody dla konkretnego znaczenia i dopasować do pełnego ID SGJP; zachować niezależne homonimy. Odróżnić rozpoznanie znaczenia od oceny normatywnej i growej. Zapisać uzasadnienie, sprzeczności, poziom pewności i status: potwierdzone, nierozstrzygnięte albo dowód niedostępny. Brak wystąpienia w KWJP nie oznacza odrzucenia. |
| PAN-4 | Pomiar pokrycia i wpływu | Rozliczyć wszystkie rekordy wskazanej populacji: przejrzane, rozstrzygnięte, nierozstrzygnięte, bez dowodu i z konfliktem mapowania. Dla mieszkańców osobno udokumentować sposób wyznaczenia populacji i ograniczenia jej kompletności; nie przedstawiać listy kandydatów jako całej klasy. Pokazać wpływ na analizy i całe słowa z uwzględnieniem homonimów, osobno BROAD/STANDARD. Nie zamykać G3 przez częściowe przykłady. |
| PAN-5 | Przekazanie do G4 i decyzji | Przedstawić użytkownikowi rozstrzygnięcia zmieniające skład list lub kryteria wraz z przykładami, alternatywami i wpływem. Po wymaganych decyzjach wdrożyć wyłącznie udokumentowane mapowanie z testami rozdzielenia homonimów, zachowania unresolved i śladów explain. Zebranie dowodów nie aktywuje samo nowych wejść ani filtrów. |

Oczekiwane artefakty w analysis/evidence/: pan-semantic-cases.json (rekordy/pełne ID, dowody, mapowanie i status), pan-semantic-coverage.json (populacje, rozliczenie i wpływ), pan-semantic-review.md (wnioski, ograniczenia i decyzje do omówienia). Ewentualny skrypt odtwarzający ekstrakcję trafia do scripts/; surowe dane, robocze indeksy i cache pozostają ignorowane. Materiały dowodowe zachowują role źródeł; KWJP nie staje się dowodem poprawności konstrukcji, a teksty 2011–2020 nie rozstrzygają normy pisowni 2026.

Najbliższy krok: PAN-1 — przygotowanie rejestru wszystkich 147 analiz frag i ich niezależnych interpretacji SGJP. Następnie PAN-2/PAN-3 dla tej zamkniętej populacji; równolegle nie tworzymy arbitralnych filtrów mieszkańców po końcówkach słów.

### G4 — kwalifikacja, rekonstrukcje i agregacja

Częściowo wykonano mechanikę policy/decisions: odrębne warstwy, zachowanie przyczyn, reject mimo innych niewiadomych, brak domyślnego accept oraz agregacja jednej spójnej analizy. Dodano zatwierdzony warunek niezalecania oraz konstrukcje impt + pojedyncza partykuła i by + nwok aglt. Dodano zatwierdzony priorytet dawności, zamkniętą ocenę wieku 160/16 etykiet i widoczność w explain. Pełna polityka i integracja konstrukcji z build nadal nieukończone; 4.1–4.4 wymagają domknięcia.

Zależności: G2/G3. Pliki: `literaki_slownik/{policy,constructions,decisions}.py`, `tests/{test_policy,test_constructions,test_decisions}.py`, `config/generator/policy.json`. K3/K4/K5; R03/R04/R05.

- [ ] 4.1 Test-first z G3: odrębna kwalifikacja językowa/growa/profil, obowiązkowa wielka litera bez dopuszczenia przez lower, jedna spójna analiza, accept mimo odrzuconego homonimu, unresolved, zależny segment vs pospolita forma, mieszane etykiety, brak korpusu, profil NFC/znaki/limity, STANDARD ⊆ BROAD.
- [ ] 4.2 Wdrożyć wersjonowany, zamknięty zestaw reguł, accept/reject/unresolved i wszystkie przyczyny; zachować oryginały, agregować dopiero po kwalifikacji i osobno pokazać reguły gry oraz profil płytek. Obecność wpisu nie oznacza dopuszczenia growego.
- [ ] 4.3 Test-first i implementacja każdej potwierdzonej konstrukcji z dodatnimi/ujemnymi przykładami, kompletem składników i dziedziczeniem; brak nowych leksemów/nadgeneracji, deduplikacja wyników bez utraty śladów.
- [ ] 4.4 Green i kontrola pełnego pokrycia konfiguracji/macierz/testy; raport wszystkich niewiadomych oraz ich wpływu. Znane luki zmieniające pełny zakres blokują wydanie, nie mają automatycznego override.

### G5 — powiązania KWJP i dostępność dowodów

Fragment wykonany niezależnie podczas blokady dowodowej G3: moduł links, 4 testy red→green i pełny przegląd lemma-all. Pełny niezależny przebieg wszystkich 13 list i raport mianowników wykonano: 5 066 341 jednostek, 2 940 032 krawędzie, FK OK. Test raportu potwierdza jednorazowe F i odmowę niepełnego rozliczenia. Integracja etapu build po konstrukcjach oraz późniejszy przegląd jakości pozostają do wykonania; grupa i kroki nieukończone.

Zależności: G2/G3/G4. Pliki: `literaki_slownik/links.py`, `tests/test_links.py`; dopracowanie `config/generator/pos-map.json`. K6; R06.

- [ ] 5.1 Test-first: lemma/POS/homonimy, dokładna forma i orth_lc, wielka litera, F raz przy jednostce, gatunki 1–4, brak gatunkowy/globalny, segmentacja, bigram, zera miar i brak POS.
- [ ] 5.2 Wdrożyć pełne mapowanie z metodą, kandydatami i niepewnością; miary pozostają przy rekordzie korpusu. Dopasowanie strukturalne nie dowodzi sensu ani dopuszczalności słowa.
- [ ] 5.3 Wdrożyć wszystkie statusy dostępności/null/powody, mianowniki per lista i odrębność gatunków/miar; jawne UNAVAILABLE NKJP; nie imputować ani rekonstruować częstości segmentowanych form.
- [ ] 5.4 Green oraz pełny raport liczebności/metod/niejednoznaczności/niedopasowań; źródłowy przegląd mapowania powiązany z macierzą i późniejszą próbką jakości.

### G6 — explain, raporty i deterministyczne próbki

Niezależny fragment po zleceniu kontynuacji kodu: diagnostyczne explain tekst/JSON, wszystkie source interpretacje i rozwinięcia, wpis versus gra/profil, niepełny import, pełne powiązania bez powielania F. Osiem rzeczywistych zapytań i hashe read-only sprawdzone. Dodano mechanikę quality-v1 i szablon przeglądu: 7 testów, powtarzalna próbka 90 jednostek na rzeczywistych 184 917 rekordach lemma-all. Dodano strumieniowy raport samodzielnych/kolejnych/łącznych efektów filtrów, z kontrolą homonimów, niewiadomych i pominiętych odrzuceń. Przynależność do pełnych warstw, analizy w przeglądzie, integracja raportów i finalne decyzje pozostają do wykonania; kroków nie oznaczono complete.

Zależności: G4/G5. Pliki: `literaki_slownik/{explain,reports,quality}.py`, `tests/{test_explain,test_reports,test_quality}.py`; CLI/build aktualizowane sekwencyjnie. K7/K9 oraz K8; R07/R09/R11.

- [ ] 6.1 Test-first: accept/reject/unresolved/absent, failed build, wszystkie homonimy/składniki, odrzucenie profilu, brak KWJP; wszystkie analizy w JSON, żadnego cichego ucięcia; wpis istniejący lecz niedopuszczalny growo ma osobny powód i pozostaje osiągalny.
- [ ] 6.2 Wdrożyć explain tekst/JSON oraz raporty importu, inwentaryzacji, pokrycia, niewiadomych, powiązań i filtrów (samodzielnie/kolejno/łącznie, analizy versus utracone formy).
- [ ] 6.3 Test-first i implementacja quality-v1/I3, do 30 jednostek na każdą warstwę/metodę/kategorię; stabilny dobór, populacje i nakładanie, szablon review związany hashami; brak pustej warstwy jako dowodu klasy.
- [ ] 6.4 Green, runtime CLI explain na małej fiksturze i rzeczywistym diagnostycznym build; przygotowanie `canonical-index.json` i logical-content według I2, odrębnie performance/log/czasy.

### G7 — verify, plan pakietu i export

Zależności: G1–G6. Pliki: `literaki_slownik/{verify,export}.py`, `tests/{test_verify,test_export,test_lifecycle}.py`, `docs/generator/publikacja.md`, konfiguracja warunków pakietu. K1–K10; R08/R10/R11.

- [ ] 7.1 Test-first: niekompletny etap/macierze/review, niewłaściwe hashe, fikstura produkcyjna, niespójna baza, zmieniony kod/wejścia, peer-run różniący się treścią lub tylko czasem, nieznane nierozstrzygnięcia i każda brakująca pozycja K.
- [ ] 7.2 Wdrożyć verify K1–K10 oraz review/peer-run związane hashami; I1 plan pakietu/candidate przygotowany przed verdict; ustalić jawnie warunki kodu/dokumentacji/list/raportów i ewentualnej dystrybucji bazy, bez narzucania licencji.
- [ ] 7.3 Test-first i export: staging w tym samym systemie plików, nowy cel bez nadpisania/wyścigu, hashe zweryfikowanych bajtów, manifest bez rekursji, atrybucje/ograniczenia, FROZEN i odczyt bez zmiany danych językowych.
- [ ] 7.4 Green i dwa małe przepływy lifecycle; awarie na granicach etapów/transakcji/eksportu, zachowanie wcześniejszych plików, odmowa zmian po verify. Fixture testuje mechanikę wewnętrzną, publiczne CLI nie omija wymogu produkcyjnych źródeł.

### G8 — pełne odtworzenia i odbiór źródłowy

Zależności: G1–G7, utrwalony użyty kod/konfiguracje. Pliki: nowe raporty `verification/full-builds/`, `verification/quality-review.json`, `verification/acceptance-matrix.md`; duże przebiegi `data/work/` ignorowane. K1–K10; R01–R11.

- [ ] 8.1 Commit większego spójnego przyrostu; inspect-sources pełnego manifestu, dwa niezależne pełne build w nowych katalogach. Zapis komend, środowiska, czasów/RSS/rozmiaru bazy i czasu próby explain.
- [ ] 8.2 Porównać wszystkie hashe I2, liczby importu i pokrycie klas; wykonać rzeczywiste explain/przegląd całej wybranej próby quality-v1. Review uzasadnia wyniki źródłami; nie jest deklaracją bez dowodów.
- [ ] 8.3 Naprawić ujawnione błędy ogólnymi regułami z dowodami i testami, uruchomić nowe przebiegi po zmianie; verify wszystkich K, następnie export pełnego pakietu. Przy unresolved zmieniającym listy G8 pozostaje nieukończona.
- [ ] 8.4 Odbiór macierzy K1–K10 i hashy pakietu, ochrona wcześniejszych wyników, jawne ograniczenia i brak wdrożenia do gry; istotne raporty/dowody w repo, surowe źródła i robocze bazy poza Git.

### G9 — dokumentacja i przekazanie do weryfikacji Maister

Zależności: G8. Pliki: `docs/generator/{README,manifest,cli,odbior}.md`, `README.md`, `AGENTS.md`, `.maister/docs/INDEX.md`, log/plan/stan/dashboard. R12; K7/K8/K10.

- [ ] 9.1 Opisać polski quickstart, jawne pozyskanie wejść, manifest, polityki/macierz, komendy/statusy i diagnostykę; przykłady z osiągniętego działania, nie samego planu.
- [ ] 9.2 Opisać review/verify/export, deterministyczne odtworzenie, aktualizacje, atrybucje, warunki i bezpieczny powrót do poprzedniego pakietu; zachować obce materiały z polską metryczką.
- [ ] 9.3 Sprawdzić instrukcje na rzeczywistym CLI, linki oraz ignorowanie cache/tmp/baz; README/AGENTS/INDEX odróżniają zamknięty audyt od gotowego generatora; bez zmiany promptu i historii research.
- [ ] 9.4 Uzupełnić plan/log i przekazać dowody do obowiązkowego wyboru weryfikacji w fazie 10 oraz canonical maister-verify. Nie oznaczać całego zadania completed przed pozostałymi fazami; finalny commit/push po odbiorze.

## 4. Walidacja grup

| Grupa | Ukierunkowana komenda / dowód |
|---|---|
| G1 | `python3 -m unittest tests.test_inputs tests.test_run tests.test_cli` |
| G2 | `python3 -m unittest tests.test_database tests.test_sgjp tests.test_kwjp tests.test_build`; baseline audytu; pełny raport importu |
| G3 | Macierz kompletności, źródła/hash, dodatnie/ujemne przykłady i status wszystkich wymaganych klas |
| G4 | `python3 -m unittest tests.test_policy tests.test_constructions tests.test_decisions` |
| G5 | `python3 -m unittest tests.test_links`; pełny raport powiązań |
| G6 | `python3 -m unittest tests.test_explain tests.test_reports tests.test_quality`; runtime explain |
| G7 | `python3 -m unittest tests.test_verify tests.test_export tests.test_lifecycle` |
| G8 | Dwa pełne build/peer-run, przegląd quality-v1, verify/export i macierz odbioru |
| G9 | Instrukcje CLI, lokalne linki, `git diff --check`, brak danych roboczych w indeksie Git |

Komendy pełnego przebiegu (po powstaniu plików; dziś to plan):

```sh
python3 -m literaki_slownik inspect-sources --manifest config/generator/sources.json --json
python3 -m literaki_slownik build --manifest config/generator/sources.json --run-dir data/work/g1-a --json
python3 -m literaki_slownik build --manifest config/generator/sources.json --run-dir data/work/g1-b --json
python3 -m literaki_slownik explain --run-dir data/work/g1-a --word kot --variant standard --json
python3 -m literaki_slownik verify --run-dir data/work/g1-a --peer-run data/work/g1-b --review .maister/tasks/development/2026-10-04-generator-broad-standard/verification/quality-review.json --json
python3 -m literaki_slownik export --run-dir data/work/g1-a --output-dir data/work/g1-release --json
```

Nazwy katalogów są przykładowe; ponowienie zawsze używa nowego celu. Pełna suita po ukończeniu implementacji: `python3 -m unittest discover -s tests -p 'test_*.py'` oraz baseline audytu, w jednej kanonicznej weryfikacji Maister. Bez E2E przeglądarkowego: CLI ma własny runtime odbiór, brak makiet UI i wymagania visual-fidelity.

## 5. Pokrycie odbioru i granica ukończenia

| Kryterium | Grupy / zasadniczy dowód |
|---|---|
| K1 / R01 | G1/G7/G8 — manifest, testy odmowy, pełny preflight |
| K2 / R02 | G2/G8 — pełne liczniki i oryginalne rekordy |
| K3 / R03 | G4/G8 — spójne analizy i podzbiór |
| K4 / R04 | G3/G4/G8 — macierz wszystkich klas, testy i przegląd |
| K5 / R05 | G3/G4/G7/G8 — wykaz niewiadomych i brak blokad pełnego zakresu |
| K6 / R06 | G3/G5/G8 — jednostki/miary, niepewność, próba linków |
| K7 / R07 | G6/G8/G9 — runtime explain i instrukcja |
| K8 / R08 | G1/G2/G6/G7/G8 — awarie i dwa odtworzenia |
| K9 / R09 | G6/G8 — wpływ filtrów i źródłowy przegląd próbki |
| K10 / R10 | G7/G8/G9 — zweryfikowany pakiet i warunki |
| R11 | G1/G6/G7/G8 — pięć osiągalnych komend i kody/JSON |
| R12 | G9 — dokumentacja sprawdzona na gotowym narzędziu |

Żadna grupa nie usuwa wymaganego discovery ani klasy językowej. Ukończenie implementacji oznacza kod, pełne dowody, dwa listowe kandydaty, odtworzenia, przegląd i dokumentację. Pozostałe fazy Maister potwierdzają całość; ich wymagane bramki nadal obowiązują.

## 6. Bramka planu

A: zatwierdzić dziewięć grup i I1–I3, rozpocząć implementację według executora. B: wskazać korektę przed kodem. Zatwierdzenie planu nie udziela zgody na destrukcyjny rollback ani na arbitralną zmianę polityki językowej.

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

[Adnotacja akcent](../analysis/evidence/accent-gloss-first-release-decision.md): zatwierdzone A, wdrożone; dawność oceniana osobno.

## Adnotacja akcent i klasy źródłowe gry — przyrost

Zatwierdzone A dla adnotacji akcent wdrożono bez zmiany dawności: BROAD nie wyklucza przez brak objaśnienia, STANDARD odrzuca dwie analizy daw.,rzad.,akcent. Pełny raport 7 458 520 analiz zachowuje 26 nieobjaśnionych oznaczeń w 1910 analizach. Dodano diagnostyczne warunki klas źródłowych gry: nazwy, brev, niesamodzielne segmenty oraz odrębną ocenę całości konstrukcji. Nowa zamknięta klasa ja/ty/my/wy/wszyscy zachowuje sześć kandydatów i growe odrzucenie tych analiz, bez usuwania homonimów. Pozostałe mobilne hosty i sekwencje by oceniono zgodnie z zachowanymi wyłączeniami gry; byle ma udokumentowany wyjątek. Pełna kwalifikacja i wydanie nadal nieukończone.

[Przegląd i dowody](../analysis/evidence/accent-and-source-game-review.md).

## Utrwalone oceny — postęp i następna decyzja

Utrwalono diagnostycznie każde rozwinięcie tagu i każdą konstrukcję, dwa warianty i komplet powodów w schema2. Wspólne dokumenty JSON/SHA nie tracą indywidualnego profilu ani homonimów. Explain pokazuje zapisane analizy z wersją; build tworzy decisions.json, logical-content obejmuje nowe relacje. Projekcja615 interpretacji daje1626 analiz/3252 oceny,72 dokumenty powodów, repeat0new i identyczny digest; FK/integrity OK. Generator147/147,audyt5/5. Pełna polityka/listy/verify/export pozostają nieukończone. Przed filtrem wymagającym wielkiej litery dla dawnych zapisów BROAD potrzebne doprecyzowanie normy odniesienia wspólnych reguł gry.

[Przegląd](../analysis/evidence/persisted-assessments-review.md); [decyzja](../analysis/evidence/game-capitalization-norm-decision.md).

## Norma growa i podwojona partykuła — wdrożone A

Wdrożono A: growy obowiązek wielkiej litery według normy2026 w obu wariantach, na udokumentowanym podzbiorze trzech pełnych ID; dawne wpisy i taneczny homonim zachowane. Dodano zamkniętą klasę impt_sg + że + ż z trzema składnikami i odrębną odmową grową. Rzeczywista projekcja wszystkich obecnych wejść konstruktorów oraz przykładów kapitalizacji:93 284 interpretacje,125 360 konstrukcji,219 713 analiz i439 426 ocen; powtórzenie0nowych rekordów/identyczny hash/FK/integrityOK. Generator151/151,audyt5/5,preflight14wejść+10konfiguracjiOK. Pełna macierz semantyki/ortografii i wydanie nadal nieukończone.

[Przegląd](../analysis/evidence/capital-double-review.md). Pozostałą lukę semantyczną opisuje [historyczny projekt niewysłanego zapytania](../analysis/evidence/sgjp-semantic-metadata-request.md); kontakt został wykluczony przez użytkownika. Dalsza praca korzysta z [przeglądu PAN](../analysis/evidence/pan-data-recheck.md) i etapów PAN-1–PAN-5 w G3.

## Przegląd PAN — postęp populacji frag

PAN-1: zamknięta populacja147frag zinwentaryzowana; PAN-2: wszystkie13list i5500próbek powiązane, glosy niedostępne w odczycie; PAN-3: wstępny odczyt62pierwszychkontekstów, pełne mapowanie nierozstrzygnięte; PAN-4: pokrycie frag147/64alternatywy/108listy/62próbki/39beztrafień, bez wpływu na listy. Nazwy mieszkańców i pozostałe wyjątki nadal do inwentaryzacji.

Dwa odtworzenia identyczne; hash bazy źródłowej bez zmian,152/152testów. Tokenizer zachowuje granice zapisów z łącznikiem. Nie aktywowano nowej klasyfikacji ani filtrów; główne checkboxy pozostają8/36. [Przegląd](../analysis/evidence/pan-semantic-review.md).

## Dokumentacyjne mapowanie PAN — postęp i wybór wieku

PAN-3:12 użyć udokumentowanych SGJP+2 obserwacje WSJP, dokładne tożsamości i homonimy zachowane. Pełny ID nie jest gwarancją jednego znaczenia. PAN-4:14/147 z dowodem użycia,133 bez takiego przeglądu,147 kwalifikacji unresolved. Audyt snapshotu/mapowania i dwa identyczne odtworzenia;156/156 testów. Wymagany wybór roli ogólnego opisu wieku przed filtrem STANDARD. Bez aktywacji źródeł i zmian list,8/36 bez zmian.

[Przegląd](../analysis/evidence/pan-document-review.md); [decyzja wieku](../analysis/evidence/general-class-age-decision.md). PAN-1–PAN-5 pozostają częściowe, bez zmiany checkboxów.
