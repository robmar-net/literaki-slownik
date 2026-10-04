# Wymagania pierwszego generatora

## TL;DR

Opiekun słownika potrzebuje odtwarzalnych BROAD i STANDARD z wyjaśnieniem każdej decyzji.
Zakres G1/N1/C1 oraz zakres implementacji zostały zatwierdzone.
Kod i uzupełnienie dowodów językowych stanowią jeden zakres odbioru K1–K10.
Niepełny wynik pozostaje roboczy; nie zastępuje pełnego słownika.

## Key Decisions

- Źródło wymagań: [prompt v3](../../../../../docs/literaki-niezalezne-slowniki-prompt-v3.md), doprecyzowany [zatwierdzonym projektem](../../../research/2026-10-04-audyt-zrodel-polskich-slownikow/outputs/high-level-design.md) i [zakresem](gap-analysis.md).
- Lokalny Python/SQLite; SGJP jest podstawą leksykalną, KWJP dostarcza odrębnych dowodów użycia. Dopuszczalność growa wynika z niezmienionych reguł gry i jest oceniana osobno od obecności wpisu.
- Jedna spójna analiza musi spełniać wszystkie warunki; nie składamy akceptacji z różnych homonimów.

## Open Questions / Risks

- Finalne tabele etykiet, skrótowców, konstrukcji i ortografii wymagają dowodów. Specyfikacja określa obowiązek ich domknięcia, nie udaje rozstrzygnięcia.
- Ustalenie warunków publikacji własnego kodu i danych pozostaje wymaganiem K10.

## Użytkownicy i przebieg

Opiekun przygotowuje manifest lokalnych wejść, uruchamia build w nowym katalogu i przegląda błędy. Recenzent pyta explain o formy, sprawdza źródła i próbki. Opiekun wydania uruchamia verify po dwóch przebiegach i przeglądzie językowym, następnie export. Role te mogą pełnić ta sama osoba; nie dodajemy kont ani mechanizmu uprawnień. Wystarcza dostęp do plików lokalnych.

## Wymagania funkcjonalne i odbiór

| ID | Wymaganie | Odbiór |
|---|---|---|
| R01 | Jawne, wersjonowane wejścia i reguły; kontrola statusów, ról, wersji i hashy | K1 |
| R02 | Pełny import SGJP i 13 przypiętych list KWJP, zachowanie oryginałów i rozliczenie jednostek | K2 |
| R03 | Decyzje accept/reject/unresolved dla spójnych analiz, osobno kwalifikacja językowa i growa; oba warianty stosują niezmienione reguły gry; STANDARD ⊆ BROAD | K3 |
| R04 | Pełna dopuszczalna fleksja i udokumentowane konstrukcje istniejących leksemów, bez nowych leksemów | K4 |
| R05 | Pełna inwentaryzacja niewiadomych i odmowa wydania przy lukach zmieniających zakres list | K5 |
| R06 | Powiązania KWJP zachowują jednostki, niepewność i statusy braków; brak kopiowania częstości | K6 |
| R07 | Explain dla każdej formy; odrębnie obecność/kwalifikacja językowa, reguły gry, profil i członkostwo w liście, także reject/unresolved/absent | K7 |
| R08 | Deterministyczne wyniki, dwa odtworzenia i bezpieczne zachowanie przy awarii | K8 |
| R09 | Wpływ filtrów osobno i kolejno oraz przegląd deterministycznie dobranych prób jakościowych | K9 |
| R10 | Kontrolowany pakiet dwóch list, manifestów, raportów i atrybucji, z warunkami publikacji | K10 |
| R11 | Osiągalne komendy inspect-sources/build/explain/verify/export, czytelny tekst i JSON | K1–K10 |
| R12 | Dokumentacja uruchomienia, wersji, błędów, ograniczeń i aktualizacji | K7, K8, K10 |

Wymagania niefunkcjonalne: Python 3.11+, standardowa biblioteka, SQLite z integralnością relacji, strumieniowy import zamiast przechowywania całych danych w pamięci, brak automatycznych pobrań, kontrolowane katalogi wynikowe. Koszty pełnego przebiegu mierzymy i raportujemy; nie deklarujemy niezmierzonych budżetów jako osiągniętych.

## Poza tym etapem

NKJP pozostaje UNAVAILABLE/BLOCKED do odrębnego odbioru. ATTESTED, znajomość słów, tematy, benchmark, API i integracja gry są poza tym etapem. Wykluczenia nie obejmują żadnej wymaganej klasy fleksji lub konstrukcji: pilot może być krokiem wewnętrznym, lecz nie końcowym wynikiem G1.

## Dokument wiążący po zatwierdzeniu

[Specyfikacja wykonawcza](../implementation/spec.md) rozwija R01–R12 i K1–K10. Plan powinien przypisać każdemu wymaganiu zadania oraz dowody odbioru; sama liczba słów lub działające polecenie nie są wystarczającym kryterium.
