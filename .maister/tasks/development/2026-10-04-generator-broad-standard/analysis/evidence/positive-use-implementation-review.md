# Dodatni dowód użycia — wdrożenie

## TL;DR
Zatwierdzone A wdrożono dla dokładnego użycia „na wznak”. Dodatni wynik dotyczy tylko leksykalnego warunku BROAD.
STANDARD, pozostałe warunki językowe i growe oraz nierozpoznana pozostałość pozostają osobne.

## Key Decisions
- Zamknięte mapowanie use_id, pięciu pól, wiersza, SHA eksportu i dokumentu autorów. Nie wystarczy dowolny poprawny hash dokumentu; wymagany dopuszczony własny przegląd i jego identyfikator.
- lexical_proof identyfikuje zatwierdzoną regułę, nie pozwala wstrzyknąć statusu. Walidacja przed zapisem. Nie propaguje się do rekordu, innych użyć lub nieznanych możliwości.
- Nowa wersja polityki v16 wymaga nowych baz; wcześniejsze przebiegi bez zmian. Schema2 pozostaje bez migracji. Aktywne trzy własne przeglądy: de:F, ibn, wznak.
- generic pending zachowuje rzeczywiste luki pełnej macierzy. Dodatni dowód pojedynczego warunku nie daje spójnego accept całej analizy.

## Open Questions / Risks
- Brak pełnej macierzy, kompletnej klasy mieszkańców i odbioru jakości.8/36 głównych kroków; pełne wydanie nadal niegotowe.
- To kontrola przyrostu, nie pełne dwa build ani faza11 weryfikacji Maister. Obowiązkowa bramka fazy10 pozostaje.

## Kontrole
Dwa nowe testy: przed implementacją dodatni przypadek odmawiał rozszerzenia (red), po implementacji green. Sprawdzają wynik BROAD/nieustalony STANDARD, brak przeniesienia na pozostałość i inne warstwy, odmowę zmienionego use_id/reguły/dokumentu przed zapisem oraz idempotencję.
Całość181/181 i5/5 baseline. Preflight14 źródeł+11 konfiguracji poprawny.

[Runtime](positive-use-runtime.json): baseline i dwa nowe niezależne zapisy wszystkich147 kluczy frag wraz z homonimami,295 reprezentatywnych rekordów/540 rozwinięć/543 analiz/1086 ocen. Trzy użycia i trzy pozostałości; powtórzenie0 nowych zapisów, FK/integrity OK. Hashy logicznych i próbek nie różniły ścieżki.12 readonly explain w obu wariantach; wznak zachowuje unknown członkostwa. Źródłowa baza niezmieniona. Finalnej delty list nie da się jeszcze określić.
