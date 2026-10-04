# Morfeusz/SGJP: reguły, segmenty i kompletność form

Data audytu: 2026-10-04. Zakres: dokumentacja, oficjalne źródła programu i kontrolna próbka/obliczenia na tekstowym eksporcie SGJP. To projekt reguł i audyt, nie słownik produkcyjny.

## TL;DR

Bieżący eksport **zawiera już pełne osobowe formy czasu przeszłego i warunkowego**. Nie należy generować ich ponownie przez swobodne doklejanie końcówek. Próba kontrolna wyjaśniła wszystkie 896 798 obecnych trójek `forma/lemat/tag` tych klas, ale mechaniczne łączenie wyprodukowało dodatkowo 120 trójek nieobecnych w eksporcie, m.in. dla czasowników typu `deszczyć`. To sygnał nadgeneracji próby, a nie dowód braków SGJP.

Trzeba filtrować interpretacje niesamodzielne, zachowując homonimiczne pełne słowa: `em` występuje jako aglutynant i jako rzeczownik, `biało` jako `adja` i przysłówek. Nie wolno odrzucić całego napisu z powodu jednej interpretacji.

## Key Decisions — zalecenia do następnego etapu

1. Bazą jest eksport `sgjp-20260823.tab.gz` z wewnętrznym identyfikatorem **`pl.sgjp.sgjp-2026.08.24`**. Zachować obie daty; nie poprawiać identyfikatora na podstawie nazwy katalogu.
2. Domyślnie preferować pełne rekordy fleksyjne zapisane w eksporcie. Reguły segmentacji służą do wykrywania zależnych części i do kontroli pokrycia; nie stanowią automatycznej listy dozwolonych operacji generatora gry.
3. Przed kwalifikacją zapisu zachować pełny lemat z rozróżnieniem homonimów, surowy tag, pola nazw i kwalifikatorów. Rozwijanie kropkowej notacji tagów jest odrębne od liczenia rekordów.
4. Nie aktywować produktywnej derywacji prefiksalnej, złożeń przymiotnikowych/liczebnikowych ani reguł `permissive`. Istniejący w eksporcie leksem o budowie prefiksalnej pozostaje kandydatem.
5. Dla `|` i przecinka w kwalifikatorach zachować surowe wartości oraz niepewność semantyki. Nie budować jeszcze automatycznego rozdziału znaczeń ani krzyżowych kombinacji pól nazw i kwalifikatorów.

## Źródła i licencje

| Artefakt | Ustalenie | Status dla audytu |
|---|---|---|
| [Oficjalna strona pobierania](https://morfeusz.sgjp.pl/download/) i [indeks wydania](https://download.sgjp.pl/morfeusz/20260823/) | Wydanie 20260823, osobne pliki tekstowe SGJP i źródła programu | ALLOWED: identyfikacja dystrybucji |
| [Licencja](https://morfeusz.sgjp.pl/doc/license/en) | Deklaracja BSD 2-Clause dla programu i zawartych danych; program należy do IPI PAN | ALLOWED: audyt programu; zakres eksportu potwierdza jego własny nagłówek |
| [Tekstowy eksport SGJP](https://download.sgjp.pl/morfeusz/20260823/sgjp-20260823.tab.gz) | Własna nota ©2007–2026 i pełne warunki BSD 2-Clause przed rekordami | ALLOWED dla badanego eksportu z zachowaniem zawiadomień |
| [Źródła programu](https://download.sgjp.pl/morfeusz/20260823/morfeusz-src-20260823.tar.gz) | `input/segmenty.dat`, `input/morfeusz-sgjp.tagset`, parser i `morfeusz/const.cpp`; ten ostatni zawiera pełną notę IPI PAN i BSD 2-Clause. `License.txt` jest tylko tekstem zastępczym | ALLOWED do audytu tych komponentów; nie przeniesiono całej paczki do Git |
| [Dokumentacja PDF](https://download.sgjp.pl/morfeusz/Morfeusz2.pdf) | Marcin Woliński, 22 stycznia 2026, 25 stron | Odczyt i cytowanie; brak deklaracji rozszerzającej warunki na redystrybucję całego PDF, pozostaje w cache |

Autorzy eksportu według jego nagłówka: **Marcin Woliński, Zbigniew Bronk, Włodzimierz Gruszczyński, Witold Kieraś, Zygmunt Saloni, Danuta Skowrońska, Robert Wołosz**. Lista różni się od krótszej listy na stronie programu. Dla eksportu zachować listę i lata z pliku, pełne warunki oraz wyłączenie odpowiedzialności. Zbiór wynikowy powinien otrzymać własny identyfikator i opis pochodzenia. Nie wynika stąd uprawnienie do hurtowego pobierania całej internetowej bazy SGJP.

Rejestr URL, czasu pobrania, rozmiaru i SHA256: [sgjp-rules-sources.json](sgjp-rules-sources.json). Dane eksportu i jego hash są także w [sgjp-rules-probe.json](sgjp-rules-probe.json). Archiwum źródeł zawiera również testowe pliki o nazwach odwołujących się do PoliMorfa; nie wczytywano ich do analizy danych ani generatora. Używane wejście fleksyjne to wyłącznie wskazany eksport SGJP.

## Co ustala dokumentacja, a co rzeczywisty kod

PDF, §7.1, s.20–21, nazywa pięć kolumn: wykładnik, lemat, tag, klasyfikacja nazw, kwalifikatory. PDF §6, s.19, opisuje `aggl=strict/isolated/permissive` i `praet=split/composite`. PDF §7.2.2, s.24, zastrzega: „wiążąca jest definicja w pliku segmenty.dat”. Tabele na s.6–7 odróżniają `bedzie`, `aglt`, `praet`, `cond`. PDF §1.1, s.3, ostrzega, że analizator obejmuje również reguły produktywne. PDF nie jest dowodem, że dowolna kolumna form stanowi gotową listę słów do gry. W opisie tabulatora wydrukowano `U+0008`; rzeczywisty separator eksportu to tabulator U+0009, potwierdzony pomiarem.

Dokładniejsze ustalenia z pobranego kodu wydania 20260823:

- `fsabuilder/morfeuszbuilder/fsa/convertinput.py:55–72`: parser obsługuje 3, 4 lub 5 kolumn; pięciokolumnowy rekord przechowuje klasyfikację nazwy jako jeden napis. `parseQualifiers` tworzy zbiór przez podział **wyłącznie po `|`**. Przecinek nie jest tam rozdzielaczem.
- `fsabuilder/morfeuszbuilder/tagset/segtypes.py:95–112,158–174`: ograniczenia `labels=` są traktowane jako zbiory etykiet, `name=` jako wartość. Ten mechanizm nie odtwarza sensów leksemu ani parowania wariantów nazwy i kwalifikatorów.
- `input/segmenty.dat:1–3`: deklaruje `aggl=strict permissive isolated`, `praet=split composite`.
- `input/segmenty.dat:89–130`: gałąź `split` łączy segmenty czasu przeszłego/warunkowego z ograniczeniem liczby i wokaliczności; gałąź `composite` przyjmuje `praetcond` i `praetaglt`.
- `input/segmenty.dat:625–641`: klasy `praetaglt`/`praetcond` są rozpoznawane po obecności osoby w `praet`/`winien` lub POS `cond`. Sama etykieta POS `praet` nie wystarcza do oceny samodzielności.
- `input/segmenty.dat:199`: `adjp:dat` jest samodzielnym segmentem. Zależność składniowa w wyrażeniu takim jak „po polsku” nie przesądza o niesamodzielności ortograficznej `polsku`. `frag` również nie ma ogólnego zakazu samodzielnego zapisu w regułach.

**Wykryta rozbieżność reguł i eksportu:** `segmenty.dat:822` klasyfikuje zależne `ń` przez tag zawierający `gen.acc`, ale eksport ma dwa oddzielne rekordy `on:S` z `gen` i `acc`, oba z kwalifikatorem `pisane_łącznie_z_przyimkiem`. W tym wydaniu dokładne dopasowanie napisu tagu z pliku reguł nie wystarcza. Trzeba porównać zbiory rozwiniętych tagów i zachować dowód z kwalifikatora; nie przenosić mechanicznie niezweryfikowanej reguły.

Oficjalna [lista oznaczeń SGJP](https://sgjp.pl/oznaczenia/) wskazana i odczytana w równoległym audycie głównym pomaga objaśnić pojedyncze kwalifikatory. Nie jest specyfikacją serializacji wariantów w eksporcie Morfeusza.

Techniczny zbiór etykiet nie rozstrzyga, czy `daw.|górn.` oznacza alternatywne zakresy użycia czy współistniejące informacje. Nie znaleziono w przebadanej dokumentacji reguły semantycznej dla przecinków i parowania obu pól. Podział przecinków może służyć pomiarowi jawnie nazwanego scenariusza, ale nie wolno przedstawiać go jako potwierdzonej semantyki eksportu.

## Odpowiedzi na cztery pytania §5

### 1. Które wpisy są pełnymi słowami do dalszej oceny?

Pełne rekordy o samodzielnej postaci ortograficznej, po kwalifikacji **tej samej interpretacji**. Dodatkowo trzeba zastosować politykę nazw, skrótów, znaków, długości i pisowni. Poniższe przykłady są odczytane z aktualnego eksportu, nie zapożyczone z demonstracji analizatora:

| Forma | Lemat i tag | Wniosek |
|---|---|---|
| czytałem | czytać, `praet:sg:m1.m2.m3:pri:imperf` | Pełna forma zapisana wprost |
| czytałbym | czytać, `cond:sg:m1.m2.m3:pri:imperf` | Pełna forma zapisana wprost |
| będę | być, `bedzie:sg:pri:imperf` | Samodzielne słowo; nie sklejać z bezokolicznikiem w jeden napis |
| gniotł | gnieść, `praet:sg:m1.m2.m3:imperf:agl` | Segment zależny; pełne `gniotłem` jest osobnym rekordem |
| em | być, `aglt:sg:pri:imperf:wok` oraz em, `subst:sg.pl:nom.gen.dat.acc.inst.loc.voc:n:ncol` | Odrzucić aglutynant, zachować możliwość kwalifikacji rzeczownika |
| biało | biały:A, `adja` oraz biało, `adv:pos` | Nie usuwać poprawnej interpretacji przysłówkowej |
| nieczytanie | czytać, `ger:sg:nom.acc:n:imperf:neg` | Istniejąca forma odmiany czasownika; nie wymaga dopisania nowego lematu |
| niegrzeczniejszy | niegrzeczny, tagi `adj:…:com` | Istniejący prefiksalny leksem pozostaje kandydatem |

Warunki segmentów niesamodzielnych zapisano w [sgjp-rules-dependent.json](sgjp-rules-dependent.json). Poza POS i `:agl` potrzebne są reguły wskazujące lemat+tag, np. `ż` oraz `ń` z `on:S`. Ich warunki nie mogą usuwać homonimów. Kategorie `brev`, `dig`, `romandig`, `interp`, `sym`, `sp`, `ign` powinny mieć osobne przyczyny wykluczenia.

### 2. Jakie formy trzeba odtworzyć?

Pomiar tego wydania:

| Grupa | Liczba rekordów |
|---|---:|
| praet z osobą | 448 406 |
| praet bez osoby | 149 696 |
| cond z osobą | 448 392 |
| winien z osobą / bez osoby | 105 / 35 |
| aglt / bedzie | 8 / 6 |

W odniesieniu do `praet/cond` audyt nie wykazał potrzeby masowej rekonstrukcji: wszystkie osobowe trójki są zgodne z kontrolnym domknięciem, a próba daje 120 nadmiarowych trójek. Nie należy dopisywać tych 120 pozycji. Hipoteza wyjaśniająca różnicę: mechaniczne reguły nie zachowują ograniczeń paradygmatów czasowników nieosobowych/defektywnych. Potwierdzenie każdej różnicy pozostaje zadaniem przyszłego generatora.

Pozostają konstrukcje ortograficzne składane z oddzielnych leksemów, np. `by+m`, `by+śmy`, przyimek+`ń`, rozkaźnik+`ż(e)` oraz mobilna końcówka przy spójniku lub zaimku. W badanej próbce `bym`, `byśmy`, `przezeń`, `czytajże` nie występują jako pełne rekordy. `doń` ma natomiast homonimiczny rekord od `donia`; nie jest to dowód istnienia rekonstrukcji przyimkowej w eksporcie. Reguły konstrukcji są w `segmenty.dat:134–185,334–354,380–382`. Należy wydzielić je jako osobną klasę kandydującą i rozstrzygnąć, które należą do przyjętej definicji form dopuszczalnych. Nie traktować wszystkich jako automatycznej fleksji jednego leksemu.

### 3. Co jest fleksją, a co rozszerzeniem leksemów?

Gotowe rekordy `praet`, `cond`, `ger`, `pact`, `ppas`, stopni przymiotników/przysłówków przypisane przez eksport do istniejących lematów mieszczą się w badaniu pełnej fleksji; nadal wymagają filtrów interpretacji. Żadne automatyczne `nie+X` nie zastępuje dowodu z eksportu.

Operacje `prefs/prefa + …`, produktywne `adja + …`, `numcomp + …`, konstrukcje z sufiksoidami i swobodne złożenia tworzące nowe identyfikatory nie wchodzą do początkowego generatora. Są w tym samym pliku reguł co fleksja, co nie daje im takiego samego statusu projektowego. `!weak` oznacza mechanizm analizatora, nie certyfikat poprawności słowa do gry. Tryb `permissive` dopuszcza dodatkowe połączenia; komentarz źródłowy przy linii161 ostrzega o nadmiernym dopuszczaniu form przez brak kontroli wokaliczności.

### 4. Jak badać kompletność i chronić interpretacje?

Zalecany kontrakt kontroli:

1. Zachować osobno rekord źródłowy, rozwinięte tagi, lemat, zapisy i flagę samodzielności. Normalizacja nie usuwa znaków.
2. Zamrozić hash eksportu oraz reguł i ustawić jawnie SGJP; przy użyciu silnika zapisać rzeczywisty `dict_id`, parametry aglutynacji, segmentacji i wielkości liter.
3. Kontrolować rodziny osobowych `praet/cond` wobec źródłowych paradygmatów. Próba z tego audytu jest kontrolą krzyżową, nie listą brakujących słów.
4. Dla rekonstrukcji używać wyłącznie zatwierdzonej listy reguł. Zapis: źródłowe rekordy wszystkich składników, lemat główny i pozostałe lematy, identyfikator reguły, hash reguł, wersja kodu oraz przyczyna przyjęcia.
5. Weryfikować przykłady dodatnie i ujemne, szczególnie `gniotł/gniotłem/gniótłbym`, `em`, `biało`, `ń`, `polsku`, defektywne czasowniki i homonimy nazw własnych. Pozytywna analiza nie jest samodzielną przesłanką dopuszczenia.
6. Agregować formę dopiero po ocenie wszystkich warunków dla jednej interpretacji. Nie składać „pospolitości” z jednej interpretacji i „współczesności” z innej.

## Open Questions / Risks

- Semantyka mieszanych nazw i kwalifikatorów: brak potwierdzonego mapowania alternatyw; przechowywać surowe pola. Nie raportować automatycznej dekompozycji jako ustalonego faktu.
- Zgodność starej i nowej pisowni: opisy reguł nie stanowią pełnej polityki ortograficznej gry. Szczególnie konstrukcje z `by` i `nie` wymagają oddzielnej oceny; nie zastosowano zewnętrznych produktywnych reguł.
- Pełna kompletność wszystkich klas fleksji nie została dowiedziona przez jedną próbę `praet/cond`; pomiar nie obejmuje odtwarzania konstrukcji przyimkowych i partykułowych ani `winien`.
- Nie wykonywano pełnej kompilacji słownika ani uruchomienia silnika na wszystkich formach. Tagset `pl.sgjp.morfeusz-0.8.0` z paczki jest artefaktem do osobnej kontroli zgodności przed kompilacją.
- Nie wolno nazwać `adjp/frag` automatycznie niepełnymi słowami tylko dlatego, że mają ograniczoną łączliwość składniową.
- Wszystkie wyniki są z konkretnego wydania. Dowód pochodzenia SGJP w tym procesie nie dowodzi całej historii pośrednich zależności źródła.

## Odtwarzanie

Ze wskazanym eksportem w `cache/sgjp/` uruchomić:

```sh
python3 .maister/tasks/research/2026-10-04-audyt-zrodel-polskich-slownikow/analysis/findings/sgjp-rules-probe.py
```

Skrypt zapisuje `sgjp-rules-probe.json`; nie zapisuje słownika do gry. SHA256 i URL wejść są w rejestrze źródeł. Cache pozostaje poza Git. Próba internetowego renderowania stron PDF 6–7 przez narzędzie screenshot zakończyła się błędem technicznym; odczyt tekstu PDF oraz niezależna inspekcja kodu i eksportu powiodły się. Ustaleń nie oparto na niewidzianych elementach graficznych.
