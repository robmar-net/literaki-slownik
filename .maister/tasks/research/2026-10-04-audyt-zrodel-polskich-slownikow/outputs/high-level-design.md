# Pierwszy generator BROAD i STANDARD — projekt wysokiego poziomu

## TL;DR

Projekt do zatwierdzenia: lokalny proces wsadowy, SQLite, jawne reguły i deterministyczne eksporty.
Wynikiem mają być LL-PL-BROAD i LL-PL-STANDARD z pełną dopuszczalną fleksją i kontrolowanymi konstrukcjami.
SGJP dostarcza jednostek językowych, KWJP dowodów użycia; NKJP dołączy później po wyjaśnieniu warunków.
Import i raporty można budować wcześniej, ale niepełny wynik nie spełnia kryterium końcowego.
To projekt, nie gotowy generator ani zatwierdzenie wszystkich reguł językowych.

## Key Decisions

- Zatwierdzone przez użytkownika: D1=G1, D2=N1, D3=C1. [Porównanie i historia wyborów](solution-exploration.md).
- Proponowane: lokalne polecenia, jedna baza na przebieg, jawny manifest wejść, eksport dopiero po kontroli kompletności. [Rejestr decyzji](decision-log.md).
- Zachowujemy dane źródłowe, homonimię, niepewność i pełny ślad pochodzenia; scenariusz przesiewu z audytu nie jest finalnym filtrem.
- Nie zmieniamy słownika działającej gry. Implementacja wymaga osobnego zadania Maister.

## Open Questions / Risks

- Niepotwierdzona semantyka mieszanych kwalifikatorów i pól nazw może blokować kompletne wydanie.
- Macierz fleksji, konstrukcji oraz zgodności z pisownią nie jest jeszcze kompletna; C1 nie zatwierdza wszystkich reguł analizatora.
- Reguły dla skrótowców i zleksykalizowanych form wymagają przeglądu źródłowego. Wielka litera nie jest samodzielnym kryterium kategorii.
- Wydajność SQLite, wielkość bazy i czas przebiegu nie zostały zmierzone. Projekt zawiera sposób ich sprawdzenia.
- Warunki publikacji własnego kodu, dokumentacji i wyników trzeba ustalić przed wydaniem. Publiczne repo nie zastępuje licencji.

## 1. Cel, zakres i granice

Odbiorcą jest osoba utrzymująca słowniki: uruchamia odtwarzalny proces, przegląda niewiadome, sprawdza przykłady, a następnie otrzymuje kandydatów oraz uzasadnienia. Projekt realizuje następny krok po [zatwierdzonym audycie](research-report.md), według [specyfikacji v3](../../../../../docs/literaki-niezalezne-slowniki-prompt-v3.md).

| W pierwszym generatorze | W późniejszych etapach |
|---|---|
| Import SGJP/KWJP, baza, reguły, konstrukcje, połączenia dowodów | NKJP po wyjaśnieniu warunków i osobnym odbiorze importu |
| BROAD/STANDARD, raport wpływu filtrów i niewiadomych | ATTESTED, COMMONNESS, poziomy wiedzy i tematy |
| Wyjaśnienie słowa, manifesty, atrybucje, kontrola powtarzalności | Benchmark dopiero po zamrożeniu kandydatów |
| Lokalne polecenia i pliki do przeglądu | Integracja gry, API, harmonogram automatycznych aktualizacji |

Nie ma produktywnego tworzenia nowych leksemów. Dane benchmarku nie są dostępne jako wejścia konstrukcyjne. Każda dodatkowa dokumentacja służy tylko w zadeklarowanej roli: nie staje się ukrytą listą dopisywanych słów.

## 2. Kontekst i komponenty

```text
Opiekun słownika
  | manifest źródeł + polityki + zatwierdzone reguły
  v
[1. Kontrola wejść] -> cache dozwolonych artefaktów
  v
[2. Import SGJP/KWJP] -> baza przebiegu SQLite
  v
[3. Rekonstrukcja i kwalifikacja] -> decyzje + niewiadome
  v
[4. Powiązania KWJP] -> dowody form / kandydatów na leksemy
  v
[5. Kontrola i wydanie] -> BROAD, STANDARD, raporty, manifest

[6. Wyjaśnianie] czyta bazę i manifest wybranego przebiegu
NKJP: UNAVAILABLE z powodem; benchmark: poza tym procesem
```

Są to moduły jednego narzędzia, nie sześć usług. Proponujemy Python, aby wykorzystać wiedzę z istniejących skryptów audytowych, oraz standardową bazę SQLite. Wybór ten jest propozycją do zatwierdzenia; audytowe skrypty wymagają adaptacji i testów przed użyciem jako importerów.

| Moduł | Odpowiedzialność | Granica błędu |
|---|---|---|
| Kontrola wejść | Weryfikuje rolę, status, hash, wersję i wymagane zawiadomienia | BLOCKED, nieznana rola lub niezgodny hash zatrzymują użycie artefaktu |
| Import | Strumieniowo zapisuje rekordy i jednostki z zachowaniem oryginałów | Uszkodzone rekordy nie są cicho pomijane; nieudany etap nie jest oznaczony jako kompletny |
| Reguły | Buduje analizy form i ocenia politykę dla spójnej interpretacji | Nieznana semantyka daje unresolved z przyczyną |
| Powiązania | Łączy jednostki KWJP bez sztucznego podziału częstości | Niejednoznaczność zostaje relacją kandydatów |
| Kontrola i wydanie | Sprawdza kryteria, tworzy posortowane listy i pakiet | Nie publikuje kompletnego kandydata po nieudanej kontroli |
| Wyjaśnianie | Pokazuje źródła, decyzje i dowody dla wskazanego przebiegu | Odróżnia brak słowa, odrzucenie i nierozstrzygnięcie |

## 3. Model danych

Rozwijamy [model audytu](../analysis/findings/model-procesu.md), bez wdrażania encji KnowledgeScore/TopicScore w pierwszym etapie. Dokładny schemat i indeksy należą do specyfikacji implementacyjnej.

| Jednostka | Kontrakt |
|---|---|
| SourceArtifact | Dokładny artefakt, hash, rola, status, wersja i dowody warunków; status dotyczy wskazanego użycia |
| Lexeme | Klucz z wydania i pełnego identyfikatora lematu; sufiks homonimu zostaje. Jest to przybliżenie tożsamości źródłowej, nie rozpoznany sens słowa |
| SurfaceForm / Interpretation | Oryginalny zapis i surowe pola; osobno NFC, tagi rozwinięte i klucz growy |
| Derivation | Ślad konstrukcji: wszystkie rekordy składników, reguła, wersja i ograniczenia. Nie tworzy fikcyjnego nowego leksemu |
| VariantDecision | Odnosi się do spójnej analizy: interpretacji źródłowej albo wyprowadzenia z kompletem składników. accept/reject/unresolved, pełna lista przyczyn i dowodów |
| CorpusEvidence / EvidenceLink | Miara pozostaje przy jednostce korpusu; relacja wskazuje formę, leksem albo nierozstrzygnięty zbiór kandydatów |
| BuildManifest | Wejścia, kod, polityki, środowisko, statusy etapów, wyjścia i ograniczenia |

W stosunku do szkicu audytu VariantDecision musi obsłużyć również analizę rekonstruowaną. Nie wystarczy podstawić jednego leksemu do konstrukcji z dwóch jednostek. Reguła jawnie określa zgodność składników i interpretację kwalifikatorów całego wyniku; bez uzasadnienia nie dziedziczymy ani nie usuwamy etykiet.

## 4. Kwalifikacja i kompletność

1. Najpierw parsujemy bez utraty surowych danych. Nieznane etykiety trafiają do przeglądu.
2. Preferujemy pełne formy z eksportu. Macierz klas wskazuje, gdzie potrzebna jest kontrolowana rekonstrukcja; zawiera przykłady dodatnie i ujemne, ograniczenia paradygmatu oraz źródła.
3. Osobno sprawdzamy samodzielny zapis, kategorię, kwalifikatory wariantu i ortografię. Wszystkie warunki muszą dotyczyć tej samej analizy.
4. Forma należy do wariantu, jeśli istnieje co najmniej jedna analiza z accept. Jeśli nie ma accept, ale istnieje unresolved, wynik jest nierozstrzygnięty. Dopiero same rozstrzygnięte odrzucenia dają reject; brak analiz oznacza brak w bazie.
5. Klucz growy powstaje po kwalifikacji: NFC, jawne sprowadzenie wielkości liter, alfabet i długość. Nie usuwa się spacji, łączników, kropek ani diakrytyków.

STANDARD pozostaje podzbiorem BROAD. Rzadkość, wulgaryzmy, potoczność, regionalność i fachowość nie są samodzielnymi wykluczeniami STANDARD. Konkretna tabela kwalifikatorów wymaga udokumentowania semantyki; nie kopiujemy konfiguracji przesiewu jako normy.

Macierz obejmuje co najmniej: pełne paradygmaty eksportu, defektywność, osobowe praet/cond i winien, formy odrębne typu bym/byśmy, przyimki z -ń, rozkaźnik z partykułą i mobilne końcówki. [Rozdzielenie klas i dowody](../analysis/findings/construction-scope.md). Nie każda ścieżka analizatora stanie się regułą. Wyłączenie klasy wymaga dowodu niezgodności z przyjętym zakresem, a nie samego braku czasu.

Parametry początkowego profilu PL: alfabet i długość 2–15 z [audytu reguł gry](../analysis/findings/game-policy.md). Zachowujemy dane spoza limitu w bazie. Polityka ortograficzna ma własną wersję i macierz zgodności źródła; aktualne zasady STANDARD nie uzasadniają automatycznej zmiany lub usunięcia wszystkich historycznych form BROAD.

## 5. Dowody KWJP i braki danych

Importujemy przypięte listy i zachowujemy wszystkie dostępne miary, reprezentację, gatunek, jednostkę i mianownik. [Audyt KWJP](../analysis/findings/kwjp-findings.md) opisuje progi i niestandardowe nagłówki CSV.

Dokładna zgodność formy i zgodność lematu/POS to dwie odrębne metody. Identyczny napis nie wystarcza do rozstrzygnięcia homonimii. Niejednoznaczne dopasowanie zachowuje kandydatów; nie kopiuje całej częstości do każdego z nich. Segmentowanej formy nie rekonstruujemy liczbowo z unigramów. Dane all i podkorpusów pozostają osobno.

Wartość i status dostępności są oddzielne: OBSERVED, ABSENT_OR_BELOW_PUBLICATION_THRESHOLD, NOT_IN_PUBLISHED_LIST, UNMATCHED, NOT_APPLICABLE, UNAVAILABLE — zgodnie z §8 specyfikacji. Dla NKJP w pierwszym wyniku: UNAVAILABLE z powodem BLOCKED. Brak dowodu KWJP nie odrzuca słowa z BROAD/STANDARD. Kontrola jakości powiązań blokuje przedstawianie błędnych dopasowań jako pewnych, nie wymusza korpusowego poświadczenia każdej formy.

## 6. Interfejs operatora i artefakty

Proponowane operacje CLI (nazwy robocze, nie istniejące polecenia):

| Operacja | Wejście | Wynik |
|---|---|---|
| inspect-sources | Jawny manifest artefaktów | Raport dopuszczenia, braków i zgodności hashy |
| build | Manifest, wersje polityk/reguł, nowy katalog przebiegu | Baza, statusy etapów, raport jakości; brak automatycznego wydania |
| explain | Identyfikator przebiegu + słowo + wariant | Czytelny opis i JSON ze wszystkimi analizami i przyczynami |
| verify | Przebieg + kryteria odbioru | Raport kontroli i lista blokad wydania |
| export | Zweryfikowany przebieg + profil gry | Zamrożony pakiet kandydata albo odmowa z przyczynami |

Podgląd roboczy może zawierać częściową listę, lecz musi nosić oznaczenie INCOMPLETE i nie może zastąpić export. Wyjaśnienie obejmuje: wersję źródeł/polityki, oryginalne rekordy, akceptacje i odrzucenia, niepewność, rekonstrukcję, dowody KWJP oraz ewentualne odrzucenie wyłącznie przez profil growy.

Pakiet wydania: dwa pliki UTF-8 z unikalnymi kluczami, po jednym na wiersz, LF i ustalony porządek; manifest; raport liczebności i filtrów; raport pokrycia klas; atrybucje; informacja o ograniczeniach. Powiązana baza musi umożliwiać wyjaśnienie wydania, ale jej publiczna dystrybucja wymaga osobno zweryfikowanych warunków.

## 7. Przebieg, awarie i powtarzalność

Każdy przebieg ma własny katalog roboczy i niezmienne wejścia. Proponowane statusy etapów: pending/running/complete/failed; gotowość całego wyniku osobno: INCOMPLETE/VERIFIED/FROZEN. Status FROZEN wymaga manifestu wszystkich plików pakietu i ich hashy.

Import używa transakcji porcjowanych, lecz przerwany etap nie udaje kompletnego. Ponowienie domyślnie tworzy nowy przebieg; nie projektujemy teraz skomplikowanego wznawiania w połowie pliku. Poprzednie wyniki są zachowane. Eksport powstaje w katalogu roboczym, po kontroli staje się niezmiennym pakietem; błąd nie nadpisuje poprzedniego wydania.

Manifest identyfikuje dokładne hashe źródeł, kodu, reguł, konfiguracji i wyników; wersję Pythona/Unicode, sortowanie oraz polecenia. Czas uruchomienia jest metadanymi, więc dwa manifesty mogą się nim różnić. Kryterium identyczności dotyczy list i kanonicznych wyników merytorycznych, nie fizycznych bajtów bazy SQLite ani pól czasu. Jawnie wskazujemy zakres hashy porównywanych przy odtworzeniu.

Konstruktor odczytuje wyłącznie wejścia wymienione w manifeście. Nie przeszukuje przypadkowych katalogów. Rola benchmark i źródła wyłączone przez projekt są odrzucane niezależnie od nazwy pliku. Pobranie źródła i import mają osobne statusy; dostępność w cache nie nadaje zgody na użycie. Nie wykonujemy zawartości plików danych.

## 8. Obsługa operacyjna i przyrosty

Opiekun wydania przegląda reguły i przykłady oraz zachowuje konfigurację. Narzędzie raportuje liczbę rekordów, błędy importu, unresolved, czas etapów, szczytowe zużycie pamięci i rozmiar bazy. Pierwszy pełny przebieg mierzy koszt importu, indeksów i zapytania explain; na tej podstawie specyfikacja implementacyjna ustali budżety, bez wymyślania dzisiejszych wyników wydajności.

Aktualizacja źródła oznacza nowy przebieg, kontrolę zmian schematu i liczebności, przykłady nowych etykiet oraz raport różnic decyzji. Nie podmieniamy źródeł pod istniejącym identyfikatorem wydania. Dołączenie NKJP wymaga dowodu warunków, osobnego importera/mapowania, kontroli jednostek i nowego manifestu.

Pierwsze prace implementacyjne można podzielić na import i bazę, reguły z kolejką niewiadomych, dowody KWJP, wyjaśnienia oraz odbiór kompletności i eksport. To kolejność zależności, nie zatwierdzony plan wykonawczy ani obietnica ukończenia reguł bez dalszych badań.

## 9. Kryteria odbioru pierwszego generatora

| ID | Dowód wymagany przy odbiorze |
|---|---|
| K1 | Każde użyte wejście ma dopuszczoną rolę, zgodny hash i udokumentowane warunki; próba użycia BLOCKED lub benchmarku odrzucona |
| K2 | Import rozlicza rekordy i jednostki względem przypiętych danych; bez cichej utraty; nieporównywalne metryki opisane |
| K3 | STANDARD ⊆ BROAD; każda forma ma jedną kompletną zaakceptowaną analizę; homonim odrzucony nie usuwa zaakceptowanego |
| K4 | Macierz wszystkich wymaganych klas, reguły i przykłady dodatnie/ujemne potwierdzają pełny przyjęty zakres; brak niewyjaśnionej nadgeneracji |
| K5 | Znane nierozstrzygnięcia mogące zmienić skład list lub ich wymaganą kompletność blokują pełne wydanie; pozostałe ograniczenia są jawnie opisane |
| K6 | Poprawne statusy korpusowe, brak duplikacji F i imputacji zera; próbki zgodnych/niejednoznacznych/niedopasowanych powiązań |
| K7 | explain rozróżnia brak, reject, unresolved i accept oraz pokazuje spójny ślad źródłowy/rekonstrukcyjny |
| K8 | Dwa przebiegi na tych samych wejściach dają identyczne listy i kanoniczne wyniki; przerwanie etapu nie uszkadza wcześniejszego wydania |
| K9 | Raport wpływu filtrów osobno i w kolejności, utracone interpretacje versus formy; próbki jakościowe z metodą doboru i przeglądem |
| K10 | Pakiet ma manifest, atrybucje i ustalone warunki publikacji; wynik nie jest automatycznie wdrażany do gry |

Próbki obejmują krótkie słowa, homonimy, historyczne formy, fachowe słownictwo, nazwy pokrywające się z pospolitymi i rekonstrukcje. Liczebność i sposób losowania zostaną określone przed pomiarem w specyfikacji implementacyjnej; przykłady ilustracyjne nie zastępują próby jakościowej.

## 10. Warunki przekazania do implementacji

Zatwierdzenie tego dokumentu zamyka projekt architektury i kryteriów odbioru. Kolejne zadanie ma przygotować analizę repo, specyfikację, plan, testy i implementację w maister-development. Nie musi czekać z importerem na wszystkie badania językowe, ale nie może zakończyć odbioru G1 bez K1–K10.

Do specyfikacji trzeba wnieść osobne zadania dowodowe: semantyka kwalifikatorów/nazw, klasy skrótowców, macierz konstrukcji i ortografii. Jeśli ujawnią rzeczywisty wybór polityki, wracamy do użytkownika z przykładami; brak danych nie upoważnia do arbitralnego filtra. Wynik projektu pozostaje użyteczny nawet wtedy, gdy pełne wydanie będzie czekało na rozstrzygnięcie tych kwestii.
