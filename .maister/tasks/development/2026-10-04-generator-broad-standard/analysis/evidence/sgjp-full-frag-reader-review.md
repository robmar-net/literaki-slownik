# Pełny przegląd publicznego czytnika dla frag

## TL;DR
Odczytano wyszukiwanie wszystkich147 źródłowych form frag i148 artykułów:144 jednoartykułowe kandydaty, don z dwoma kandydatami oraz koń/mąż opisane przy artykułach rzeczownikowych. Pełne pokrycie odczytu nie dowodzi pełnego mapowania znaczeń ani dopuszczalności. Żadnego nowego wejścia lub filtra nie aktywowano.

## Key Decisions
- Zamknięta populacja pozostaje przypięta do źródła20260823 i niezmienionego rejestru pan-semantic-cases. Każda własna obserwacja zachowuje pełną źródłową tożsamość, niezależne internetowe ID, odsyłacze i hashe odpowiedzi.
- Odczyt punktowy ograniczony do147 zaplanowanych form, nie całego słownika. W tej turze134 nowe wyszukiwania i135 artykułów, pozostałe13 odczytów z poprzedniej tury zachowane. Wszystkie zakończone poprawnie; nie wystąpił limit429. Dwie równoległe niezależne prośby, bez logowania, chronionego eksportu lub kontaktu z autorami.
- Publikujemy własne zwięzłe klasy obserwacji i metryki, bez kopii HTML, glos, definicji i pełnych nagłówków. Surowe odpowiedzi/parser/wyciągi pozostają ignorowane w tmp.
- Wyszukiwanie pisownia+klasa jest kandydatem mapowania, nie potwierdzeniem zgodności całej wersji. Czytnik jako baza maszynowego wejścia nadal BLOCKED. Nie przenosimy kwalifikatorów całego artykułu na źródłowe formy bez właściwego zakresu.

## Open Questions / Risks
- [Konieczna decyzja modelu użyć](semantic-use-alternatives-decision.md): jeden rekord eksportu nie musi mieć jednego artykułu lub jednego znaczenia. Przed zmianą kwalifikacji trzeba ustalić reprezentację udokumentowanych alternatyw.
- Klasa frazeologiczna sama nie dowodzi ani obcojęzyczności, ani samodzielności growej. New ma taką etykietę i przykłady nazw. Sir/ichmość to obserwacje przedimka, nie automatycznie nazwiska. Don ma obserwację wykrzyknikową i przedimkową.
- Dla niemiara, owąd i młodu opis całego artykułu zawiera oznaczenia nieobecne w polu tych rekordów eksportu. Nie ustalono przyczyny różnicy ani zakresu propagacji. Nie uruchomiono odmowy STANDARD z samej tej obserwacji.
- Pełna semantyka, nazwy mieszkańców obu rodzajów, ortografia2026, pozostała macierz i G7–G9 nadal wymagają pracy. Żadna główna grupa nie została ukończona przez sam odczyt.

## Pokrycie

[Własne obserwacje](sgjp-full-frag-reader-observations.json); [odtworzony audyt](sgjp-full-frag-reader-coverage.json).

| Jednostka | Liczba |
|---|---:|
| Źródłowe przypadki frag |147|
| Artykuły obserwowane |148|
| Jednoartykułowe kandydaty pisownia+klasa |144|
| Rekord z wieloma artykułami |1|
| Użycia przy artykule nadrzędnym |2|

Klasy własnych obserwacji, liczone przy artykułach (nie przy słowach):100 frazeologicznych,36 członów nazw,7 członów nazwiska,3 przedimki,2 artykuły rzeczownikowe z opisem użycia frazeologicznego. Nie sumujemy ich jako liczby potwierdzonych znaczeń. Don jest liczony w dwóch różnych klasach artykułu.

SGJP [§7.12 s.138](https://sgjp.pl/static/pdf/Podstawy_teoretyczne_SGJP.pdf#page=138) rozdziela frazeologizmy i człony nazw; [§9.2 s.145–146](https://sgjp.pl/static/pdf/Podstawy_teoretyczne_SGJP.pdf#page=145) omawia subiektywną granicę zapożyczenia/cytatu i zachowanie członów nazw. Wynika z tego potrzeba osobnej oceny leksykalnej i growej, nie automatyczny werdykt dla całej klasy frag.

## Kontrole i odtworzenie

Nowy scripts/audit_sgjp_reader_review.py jest wyłącznie walidatorem własnych adnotacji: nie pobiera serwisu i nie czyta glos. Wymaga pełnego pokrycia przypiętych przypadków, dokładnej tożsamości, poprawnych odsyłaczy/hashy, jawnego rozróżnienia wielu artykułów lub nadrzędnego artykułu, statusu unresolved i braku aktywnych wejść. Odmawia braków, powtórzeń, innego ID/snapshotu, kwalifikacji accept i nieuprawnionego twierdzenia snapshot_confirmed.

Trzy testy red(FileNotFoundError)→green; dodatkowy test dokładnego zakotwiczenia odsyłacza i hasha green. Całość172/172 generator i5/5 audytu. Dwa uruchomienia na kompletnym rzeczywistym rejestrze dały identyczne bajty. Źródłowe bazy, dane i wcześniejsze oceny pozostają bez zmian.

```sh
python3 scripts/audit_sgjp_reader_review.py --cases .maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/pan-semantic-cases.json --review .maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/sgjp-full-frag-reader-observations.json --output tmp/nowy-audyt-czytnika.json
```

Cel musi być nowym plikiem. Weryfikacja dotyczy rejestru własnych obserwacji, nie potwierdza licencji internetowej bazy ani kompletności wszystkich znaczeń.
