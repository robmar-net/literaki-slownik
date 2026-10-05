# Zakres niepoświadczonych kontrakcji pierwszego wydania

## TL;DR
18 całych form ma zatwierdzony dowód z dokumentacji SGJP.
Osiem innych ma zgodne składniki i techniczny ślad, ale nie znaleziono wymaganego poświadczenia całej formy.
Potrzebny jest wybór: jawnie zawęzić zakres pierwszego wydania albo zachować dotychczasowy zakres i blokadę wydania.
Żadnego wyłączenia zakresu nie wdrożono przed odpowiedzią; to nie decyzja o błędności słów.

## Key Decisions
- Dotychczasowe A wystarcza dla dosłownie wymienionych form, nie dla wszystkich możliwych sklejeń.
- Korpusowe wystąpienie i techniczna analiza nie zastępują dowodu językowego całej kontrakcji w obecnym kontrakcie.
- Brak znalezionego poświadczenia nie oznacza, że forma jest błędna lub nie istnieje.
- Niezależne homonimy pozostają oceniane osobno; nie blokujemy całego napisu przez brak dowodu tej konstrukcji.

## Open Questions / Risks
- A/B pending. Brak odpowiedzi nie pozwala wyłączyć wymaganej części macierzy ani zakończyć K4/K5.
- Wikisłownik i podobne źródła użytkownik odroczył. Nie używamy ich jako obejścia.
- To zawężenie tylko zakresu kontrakcji, bez zgody na pomijanie innych klas, testów lub dwóch pełnych przebiegów.

## Pokrycie i poszukiwania

Niepoświadczone w dotychczasowych dopuszczonych dowodach: kołoń, pozań, zzań, ponadeń, popodeń, poprzezeń, sponadeń, spopodeń. Pełny konstruktor daje dla nich 24 analizy rozwinięte; wszystkie mają linguistic_evidence unresolved i pełne źródłowe składniki.

[Audyt poświadczeń](contraction-attestation-audit.json), [zatwierdzony dowód 18 form](contraction-proof-decision.md), [rzeczywiste liczniki](preposition-runtime.json).
Ponowne trzy wyszukiwania domen SGJP/WSJP dla wszystkich ośmiu nazw nie zwróciły wyników. Jest to obserwacja dostępu przez wyszukiwanie, nie dowód nieobecności w całym słowniku ani normatywna odmowa. Nie aktywowano danych źródeł społecznościowych, list SJP ani benchmarku.

## Wybór przed wykonaniem

A — pierwszy pełny pakiet ma jawnie ograniczony zakres przyimek+-ń do 18 całych form wskazanych przez SGJP. Osiem pozostałych zachowujemy jako diagnostycznych kandydatów poza zakresem pierwszego wydania, z osobnym powodem i wpływem w raportach. Nie uznajemy ich za błędne; przyszłe rozszerzenie wymaga poświadczenia i nowego odbioru. Specyfikacja i macierz zostaną zaktualizowane dopiero po zatwierdzeniu tego zawężenia przez użytkownika.

B — zachowujemy wymóg całej macierzy 26 kontrakcji. Brakujące poświadczenia pozostają rzeczywistą blokadą K4/K5 i pełnego wydania. Niezależna implementacja może trwać, ale nie można zadeklarować ukończenia ani zwolnić blokady przez flagę operatora.

Pytanie wynika z zatwierdzonego planu G3/3.4 oraz AGENTS: zmianę zakresu/kryteriów omawiamy przed wdrożeniem. Executor Maister wymaga: „Ask the user before changing scope”. Żadna odpowiedź nie zmienia zasad gry.
