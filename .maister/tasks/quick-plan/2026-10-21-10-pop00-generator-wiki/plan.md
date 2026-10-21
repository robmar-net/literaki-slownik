# Plan #10 — generator POP00 i wiki

## TL;DR
Proponuję osobny wariant POP00 na zamrożonym POP0 pop-v3, z ochroną zwykłej odmiany.
Sonda proponowanych reguł daje 259 779 form: o 128 984 mniej (33,18%), bez utraty leksemów.
Próg 0,1 IPM dotyczy tylko wybranych grup, a nie wszystkich form.
To propozycja do zatwierdzenia, nie wydanie ani potwierdzony model znajomości graczy.
Zapowiedź POP00 jest już publiczna na wiki; kod generatora czeka na zatwierdzenie planu.

## Key Decisions
- Plan do zatwierdzenia przez operatora. Akceptacja wcześniejszego research nie zatwierdza tych reguł.
- Zachowujemy wszystkie 13 896 wybranych leksemów i przynajmniej jedną formę każdego z nich.
- Wybór leksemów oraz działanie metod pop-v2 i pop-v3 pozostają odtwarzalne.
- Nowy wariant jest słownikiem znajomości. Integracja z aplikacją i walidacja stołu są poza #10.

## Open Questions / Risks
- Próg i podział fleksji nie zostały zbadane na graczach; ich zatwierdzenie oznacza przyjęcie pierwszej polityki kandydata.
- Proponowany filtr usuwa także poprawne i zrozumiałe formy: np. `czytanymi`, `najmilszemu`.
- Zasób POP0 obejmuje również leksemy wciągnięte przez współdzielone formy. Nie poprawiamy tu ich wyboru.
- W razie odrzucenia reguł przez operatora zmieniamy plan; nie dopasowujemy ich po cichu w trakcie wdrożenia.

## Zakres i założenia
Ticket: [#10](https://github.com/robmar-net/literaki-slownik/issues/10).
Wejście: POP0 i `reports/units.json` z pakietu pop-v3, zamrożona baza LL-PL v30,
przypięta lista KWJP orth/all. Odczyt SQLite tylko przez `mode=ro`.
Bez zmiany schematu, nowych źródeł, ponownego rankingu leksemów lub przejmowania danych zablokowanych w audycie.
Wszystkie ścieżki poniżej odnoszą się do repozytorium literaki-slownik.

Każdy napis POP00 musi być w POP0 i STANDARD. Przypisanie leksemu i analiz odpowiada regule (i)
odziedziczonej z POP0; nie przełączamy go na inną regułę kwalifikacji.
Słowo wchodzi, jeśli uzasadnia je co najmniej jedna zachowana analiza wybranego leksemu.
Skompresowane tagi rozwijamy przez istniejące `sgjp.expand_tag`; sonda wykonuje równoważny iloczyn pól.
Reguła odrzucająca jedną analizę nie może usunąć innego homonimu.
Nie dopisujemy kilku form na leksem, aby sztucznie spełnić warunek zachowania leksemów:
brak form zatrzymuje budowę i wymaga diagnozy.

## Proponowana polityka pop00-v1
Reguły stosujemy w poniższej kolejności do analiz, a wynik łączymy do napisów.

| Grupa analizy | Proponowane działanie |
|---|---|
| Rodzaj nijaki `n` i osoba `pri` lub `sec` | poza POP00, także gdy wystąpi w korpusie; inna zachowana analiza może uratować napis |
| Zwykła odmiana rzeczowników, zaimków, liczebników i przymiotników w stopniu równym; podstawowe przysłówki | zachować bez progu formy |
| Formy osobowe czasowników, bezokolicznik, rozkaźnik, czas przeszły i tryb warunkowy, z wyjątkiem powyższego `n` | zachować bez progu formy |
| Imiesłów na `-ąc` (`pcon`), rzeczownik odczasownikowy twierdzący (`ger:…:aff`) | zachować bez progu formy |
| `pact`, `ppas`, `pant`, `pacta`, `ger:…:neg`, `adja`, `adjp`, stopień wyższy/najwyższy przymiotnika lub przysłówka | wymagać dokładnego małoliterowego wiersza KWJP orth/all z opublikowanym IPM ≥ 0,1 |
| Konstrukcja `by-aglt-nwok-v1`: `bym`, `byś`, `byśmy`, `byście` | zachować bez progu; segmentacja korpusu nie może ich usuwać |
| Konstrukcja `nie-prefix-degree-v2` | stosować powyższe reguły do jej `expanded_tag`, bez pomijania filtra |
| Pozostałe konstrukcje obecne w POP0 | wymagać IPM ≥ 0,1 całego napisu; nie dziedziczyć częstości składnika |

Pełna lista pozostałych POS z bieżącego wejścia będzie jawnie zamknięta w metodzie: m.in. `adjc`,
`aglt`, `bedzie`, `brev`, `comp`, `conj`, `depr`, `fin`, `frag`, `imps`, `impt`, `inf`, `interj`,
`num`, `numcomp`, `part`, `ppron12`, `ppron3`, `praet`, `pred`, `prep`, `siebie`, `subst`, `winien`.
Zachowanie domyślne w sondzie służyło pomiarowi; kod produkcyjny odmawia nieznanego POS,
nieobsługiwanego wariantu tagu, nieznanej reguły konstrukcji albo niepełnego pokrycia napisów.
Taki błąd nie jest językowym odrzuceniem słowa.

Brak wiersza KWJP ma status `NO_PUBLISHED_EVIDENCE`, nie częstość zero.
W grupie chronionej nie usuwa formy; w grupie wymagającej dowodu oznacza brak spełnienia warunku POP00.
Próg porównujemy dziesiętnie z opublikowanym IPM; nie wyliczamy go ponownie z F ani nie łączymy wielkich liter.
Proponowane 0,1 to ostrożny pierwszy próg z sondy czułości, nie potwierdzona granica znajomości.

### Sprawdzone konsekwencje
| Zostaje | Odpada w proponowanym wariancie |
|---|---|
| `kotach`, `miłemu`, `czytajcie`, `czytając` | `remontowałoś`, `przeczytałobym` |
| `zrobiłem`, `zrobiłam`, `byłam`, `zrobiliśmy`, `zrobiłbym` | `czytanymi` (IPM 0,09) |
| `bym`, `byś`, `byśmy`, `byście` | `najmilszemu` (brak wiersza) |
| `czytany`, `najmilszy`, `lepszemu`, `nieczytanie` | `nieczytaniami`, `czytajże` (brak wiersza) |

To świadoma redukcja także rzadkich realizacji poprawnej fleksji.
Jeśli operator chce pełną ochronę tych paradygmatów, potrzebna jest korekta tej propozycji.

## Dowody i alternatywy
Kod planu bazuje na `bcb699a`; [research](../../research/2026-10-21-pop00-proste-formy/outputs/research-report.md)
pozostaje źródłem wcześniejszych ustaleń.
Nowa [sonda](analysis/probe_policy.py) oraz [wynik z hashami](analysis/policy-probe.json)
odtwarzają wszystkie napisy i właścicieli POP0, uwzględniając konstrukcje i alternatywne analizy.
Hash całej bazy w sondzie pochodzi z pinu; nie był ponownie liczony. Produkcyjny preflight przeliczy go.

| Wariant pomiaru | Formy | Leksemy tracące wszystkie formy |
|---|---:|---:|
| POP0 | 388 763 | 0 |
| Tylko usunięcie nijakiej 1./2. osoby | 374 758 | 0 |
| Proponowany podział, próg 0,1 | 259 779 | 0 |
| Ten sam podział, próg 0,5 | 244 774 | 0 |
| Ten sam podział, próg 1 | 240 903 | 0 |
| Twardy próg 1 dla każdej formy | 53 443 | 661 |

0,1 ogranicza usuwanie zwykłych, mniej częstych form wewnątrz grup wymagających dowodu:
np. `najmilszy` ma 0,36, a `nieczytanie` 0,15. Wyższe progi usuwają je.
Liczba 259 779 jest wynikiem tej konkretnej sondy; nie celem ani liczbą wydanej listy.
Sonda nie mierzy rozpoznawalności, wyników partii ani niezależnej jakości.

Ważne ścieżki i symbole:
- `literaki_slownik/pop.py:287–342`: `load_forms`, `load_constructions` — dotychczasowe właścicielstwo;
  `forms_for` nie filtruje konstrukcji, więc nie może być użyte jako gotowy filtr POP00.
- `literaki_slownik/pop.py:1599–1738`: `build_pop` — istniejąca budowa pozostaje odrębną metodą.
- `literaki_slownik/pop.py:1747–2064`: wzorce pakietu, gzip, manifestu i zapisu do nowego katalogu.
- `literaki_slownik/cli.py:13–136`, `explain.py:346–503`: dodanie nowej komendy i diagnostyki.
- `literaki_slownik/schema.sql:11–55`: istniejące powiązania i tagi; bez migracji.
- `quality.py`: `sample_strata`, `review_template`; `export.py`: `rename_noreplace`.
- `scripts/check_pop_package.py`: wzorzec niezależnej kontroli bez importu buildera.

## Pliki i zakres zmian
| Plik | Zakres |
|---|---|
| `literaki_slownik/pop00.py` — nowy | `load_config`, `check_inputs`, `classify_analysis`, `select_forms`, `build_package`, `explain_pop00`, formatter |
| `config/generator/pop00.json`, `pop00-sources.json` — nowe | zamknięta metoda, reguły, próg, sampling i przypięte wejścia |
| `literaki_slownik/cli.py` | komenda `pop00`; `explain --variant pop00 --pop00-dir`; osobny formatter wyniku |
| `literaki_slownik/quality.py` | rejestr wersji `pop00-quality-v1`, seed `literaki-slownik-pop00-v1`; algorytm bez zmiany |
| `scripts/check_pop00_package.py` — nowy | niezależna kontrola plików, reguł, relacji zbiorów i przeglądu |
| `tests/test_pop00.py`, `test_pop00_package.py`, `test_explain_pop00.py`, `test_check_pop00_package.py` — nowe | testy reguł, pakietu, CLI/diagnostyki i odmów niezależnego kontrolera |
| `tests/pop_helpers.py` lub nowy helper obok | małe fikstury bazowe wraz z konstrukcjami; nie modyfikować historycznych oczekiwań POP |
| `docs/adr/ADR-009-pop00-v1.md` — numer sprawdzić przed zapisem | zaakceptowana polityka, warianty odrzucone i ograniczenia |
| `docs/generator/{cli,jakosc,raporty}.md`, `.maister/docs/INDEX.md` | komendy, wyniki, interpretacja odmowy, aktualne odnośniki |
| `docs/runbook-wiki.md` | dodać POP00 do listy stron i źródeł aktualnych wyników |
| repo wiki, pięć stron | zapowiedź już opublikowana; po buildzie rzeczywiste liczby, filtry i stan |

Nie wymaga zmiany globalnego `LISTS` ani formatu pakietu POP. Nowy pakiet ma osobne `package_id: POP00`
i listę `POP00.txt.gz`; istniejący checker i wyjaśnienia POP nie muszą rozpoznawać tego formatu.
Nie dodajemy zależności spoza biblioteki standardowej.

## Kolejność wdrożenia po zatwierdzeniu
1. **Utrwalić politykę.** Sprawdzić aktualny main i wolny ADR. Zapisać wersjonowane reguły,
   zamknięty zakres POS/konstrukcji, próg 0,1 i osobny manifest wejść. Brak doboru progu podczas kodowania.
2. **Dodać selekcję analiz.** Wczytać wybrane leksemy z `members_in.POP0` oraz napisy pakietu.
   Zweryfikować manifest, hashe list/units/KWJP/konfiguracji, FROZEN i hash bazy.
   Dopasować wszystkie analizy i konstrukcje istniejących form. Odtworzona unia musi być dokładnie POP0.
   Zastosować reguły, złączyć wynik i sprawdzić `POP00 ⊆ POP0 ⊆ STANDARD` oraz brak utraty leksemów.
   Brak danych lub nieznana klasa nie mogą dać cichego pominięcia.
3. **Zapisać pakiet.** Nowy cel poza wejściami; staging i `rename_noreplace` jak w POP.
   Pliki 0444, gzip bez nazwy i z mtime=0, sortowanie i unikalność, kanoniczny JSON.
   Pakiet zawiera `POP00.txt.gz`, `reports/decisions.json` dla wszystkich form POP0,
   `reports/summary.json`, `sample.json`, `review-template.json`, manifest, sumy i dokumenty warunków.
   Każdy napis ma wynik, powody oraz stabilne identyfikatory analiz/leksemów, bez technicznych ID SQLite.
   Nieznane słowo poza POP0 nie uzyskuje członkostwa z samej częstości.
4. **Dodać diagnostykę i kontroler.** CLI buduje pakiet i wyjaśnia wynik z przypiętych raportów;
   sprawdza hashe zanim użyje decyzji. Kontroler nie importuje `pop00.py`, odtwarza relacje zbiorów,
   zachowanie leksemów i semantykę reguł na wejściach oraz wykrywa fałszywy powód także po przeliczeniu sum.
   Zmiana bazy podczas operacji daje odmowę. Kody jak POP: 2 argumenty, 3 piny/braki wejść,
   4 naruszone dane lub cel, 5 niezamrożona albo zmieniona baza.
5. **Sprawdzić wynik.** Wykonać testy i dwa niezależne uruchomienia tego samego commitu.
   Na wejściach sondy oczekiwane 259 779 form i zero utraconych leksemów; różnica wymaga wyjaśnienia,
   nie aktualizacji liczby oczekiwanej bez diagnozy. Porównać pełne listy i raporty kanoniczne.
6. **Przegląd i dokumentacja.** Wylosować po 30 pozycji na warstwę przyczyn zachowania/odrzucenia,
   przy progu, bez KWJP, konstrukcji, krótkich/długich form i alternatywnych analiz.
   Wyłączyć przykłady diagnostyczne z niezależnej próby. Zapisać oceny, uzasadnienia i hashe.
   Każde nierozstrzygnięcie wpływające na skład blokuje gotowość wydania.
   Zaktualizować ADR, CLI, indeks i wiki; jawnie opisać ograniczenia oraz wynik przeglądu.

Pakiet kandydata ma status BUILT. Publiczne pliki do pobrania i oznaczenie wydania dodajemy po odbiorze,
bez przedstawiania automatycznej próbki lub samego pokrycia jako badania graczy.
Dotychczasowe listy nie są nadpisywane.

## Testy i weryfikacja
**Skupione:** `python3 -m unittest tests.test_pop00 tests.test_pop00_package tests.test_explain_pop00 tests.test_check_pop00_package`.
- granica 0,1: poniżej/równo/powyżej, zero, NaN, brak wiersza, zapis wielką literą;
- nijaka 1./2. osoba versus męska/żeńska i trzecia; poprawne segmentowane formy zachowane;
- pozytywne/negatywne gerundia, stopnie, wszystkie wymienione POS;
- konstrukcje by+aglt, nie-prefix-degree oraz pozostałe; żadna nie omija filtra;
- dwie analizy/homonimy: odmowa jednej nie usuwa zachowanej drugiej; tylko wybrane leksemy;
- nieznany POS/tag/konstruktor, luka pokrycia, utrata leksemu, niezgodna baza/pin;
- cel istniejący, wewnątrz wejścia i powstały podczas zapisu; brak nadpisania;
- deterministyczne bajty, pełny diff, skażony raport i przeliczony manifest, pełne powiązanie przeglądu.

**Regresje:** `python3 -m unittest tests.test_pop tests.test_pop_v2 tests.test_pop_v3 tests.test_pop_quality tests.test_quality tests.test_explain_pop tests.test_check_pop_package`.
**Cały projekt:** `python3 -m unittest discover -s tests`.
**Rzeczywiste wejścia:** dwa czyste uruchomienia, niezależny checker, dokładny diff wobec sondy,
hashe wejść przed/po, raport utraconych form i leksemów, długości, próba jakości i wiki.
Pokrycie raportować z jawnym mianownikiem: opublikowane małoliterowe tokeny KWJP lub ich część należąca do POP0.
Nie utożsamiać tego z rozpoznawalnością czy grywalnością.

## Zależności, ryzyka i wycofanie
- Potrzebne przypięte lokalne dane i prawo zapisu nowego katalogu; repo nie ma workflow GitHub Actions.
  Nie uruchamiamy jobów na runnerach GitHuba.
- Standardowa biblioteka Pythona, bez migracji i nowych usług. Wielka baza wpływa na czas kontroli hasha;
  nie pomijamy kontroli przez sam fakt odczytu read-only.
- W `LIMITATIONS.md` wskazać dziedziczenie wyboru leksemów, rejestr pisany,
  sztuczną granicę grup oraz brak empirycznej kalibracji znajomości.
- Rollback: poprzednie listy i komendy pozostają dostępne; nowe pakiety są oddzielne.
  Ewentualny revert kodu, zmiana opublikowanej wersji lub usuwanie plików wymaga jawnej decyzji operatora.
  Wiki wtedy opisuje rzeczywisty stan; nie kasujemy historycznych dowodów.

## Standards Compliance Checklist
- [ ] `AGENTS.md`: polski i prosty opis, uzgodnione kryteria przed kodem, jawność i brak sekretów.
- [ ] `.maister/docs/INDEX.md`: aktualne publiczne odnośniki do nowych dokumentów.
- [ ] `docs/adr/ADR-007-metoda-pop-v1.md`, `ADR-008-pop-v3-staly-prog.md`: POP/POP0 pozostają odtwarzalne; osobna wersja POP00.
- [ ] `docs/generator/konstrukcje.md`: składniki, expanded_tag i alternatywne interpretacje; bez tworzenia nowych leksemów.
- [ ] `docs/generator/ortografia.md`: odziedziczona dopuszczalność i normalizacja, bez zmiany zasad gry.
- [ ] `docs/generator/raporty.md`: efekt analizy oddzielony od efektu napisu, jawne mianowniki i niepewność.
- [ ] `docs/generator/jakosc.md`: deterministyczna próbka, jawnie puste warstwy i UNREVIEWED; nowa jawna wersja konfiguracji.
- [ ] `docs/generator/cli.md`: kody błędów, odczyt FROZEN, bez nadpisywania i bez fałszywego VERIFIED.
- [ ] `docs/generator/publikacja.md`, `docs/adr/ADR-006-nkjp-cc-by-bez-wersji.md`: pełne atrybucje SGJP/KWJP i odziedziczonego NKJP; bez surowych cache i liczników NKJP.
- [ ] `docs/runbook-wiki.md`: publiczny opis od początku, rzeczywiste liczby i przykłady, stan wydania i aktualne linki.

## Stan i decyzja wymagana
Przygotowano plan i sondę, nie zmieniono kodu generatora.
Wiki: [Slownik-POP00](https://github.com/robmar-net/literaki-slownik/wiki/Slownik-POP00),
commit `beb09c0`; powiązano Home, _Sidebar, POP0 i historię.

Do wyboru: zatwierdzić wdrożenie proponowanej polityki; skorygować reguły (np. chronić pełne
paradygmaty imiesłowów i stopniowania); albo zachować sam plan.
Po akceptacji wdrożenia użyć maister-quick-dev i zweryfikować każdy punkt checklisty.
