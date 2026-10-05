# Obowiązkowa wielka litera: norma odniesienia reguł gry

## TL;DR
BROAD może zachowywać udokumentowaną dawną pisownię w warstwie językowej, STANDARD stosuje normę2026. Oba mają wspólne reguły gry. Trzeba doprecyzować, czy obowiązkową wielką literę w warstwie growej oceniamy według normy2026 także wobec dawnej pisowni w BROAD. Nowego filtra jeszcze nie wdrożono.

## Key Decisions
- Nie pytamy ponownie o normę STANDARD ani o rozdzielenie wpisu i gry — to zatwierdzono. Nie zmieniamy źródłowych zapisów ani reguł gry.
- RJP §8.1.2 pkt3 wymaga wielkiej litery dla nazw mieszkańców miast. Przypięty SGJP20260823 ma małoliterowe warszawianin/warszawiak i krakowiak:Sm1, nazwa_pospolita, bez etykiety dawności.
- Sam literalny zapis źródła nie wystarczy do oceny współczesnego obowiązku wielkiej litery. Sam sufiks, POS lub klucz słowa nie dowodzą znaczenia; potrzebne przypięte mapowanie do konkretnego leksemu i jego analiz.
- Krakowiak:Sm1 to osobowy m1; krakowiak:Sm2 jest m2 z chor. Ten drugi ma pozostać osobnym małoliterowym homonimem; nie odrzucamy całego klucza krakowiak.

## Przykłady i wpływ
[Odczyt źródła](capitalization-source-cases.json), readonly, zero zapisów:

| Pełne ID | Kompaktowe interpretacje | Rozwinięcia | Znaczenie istotne dla decyzji |
|---|---:|---:|---|
| warszawianin |12|17|mieszkaniec|
| warszawiak |12|17|mieszkaniec|
| krakowiak:Sm1 |12|17|mieszkaniec|
| krakowiak:Sm2 |11|14|taniec, osobna analiza|

A wpływa na51 analiz trzech pokazanych leksemów mieszkańców.14 analiz tańca nie jest wykluczane tym warunkiem. To ekspozycja przykładów, nie pełna inwentaryzacja klasy ani delta końcowej listy. Nie zakładamy, że wszystkie nazwy mieszkańców mają te same metadane.

## Open Questions / Risks
A — rekomendowane: wspólny warunek growy obowiązkowej wielkiej litery odnosi się do normy2026 w obu wariantach. BROAD może zachować dawny zapis jako materiał językowy, ale ta interpretacja nie daje dopuszczenia do gry. Inne poprawne homonimy oceniane osobno.

B — najpierw doprecyzować, czy norma historyczna ma wpływać również na grową ocenę dawnych interpretacji BROAD. Do rozstrzygnięcia brak nowego filtra, status unresolved i blokada pełnego wydania; bez samodzielnej zmiany zasad gry.

Pytanie wynika z AGENTS.md: „Decyzje zmieniające skład słownika lub kryteria dopuszczalności omawiamy z użytkownikiem przed ich wdrożeniem”, oraz G3/3.4 i spec§6. Dotychczasowe A dotyczyło normy warstwy językowej, a reguły gry wymagało oceniać osobno.

## Źródła i role
[RJP, wersja jednolita11-2025](https://rjp.pan.pl/app/uploads/2025/11/2-zalacznik-do-komunikatu-11-25-wersja-jednolita.pdf), drukowana strona43, §8.1.2 pkt3; wcześniej przypięty dokument normy, bez importu leksemów. [WSJP PAN, krakowiak — taniec](https://wsjp.pl/haslo/podglad/125451/krakowiak/5284965/taniec) potwierdza rozdzielenie przykładu; tylko odczyt referencyjny, bez aktywacji danych WSJP, kopiowania definicji lub tabel fleksyjnych. Źródłem analiz pozostaje przypięty SGJP. SGJP i dokumenty mają osobne warunki opisane w ATTRIBUTIONS/config; nie przypisujemy sobie ich autorstwa.
