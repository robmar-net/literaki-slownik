# Utrwalanie potwierdzonych konstrukcji

## TL;DR
Nowe build zapisują kandydatów dwóch potwierdzonych konstrukcji wraz ze składnikami.
Explain wskazuje zapisany ślad, zachowując zgodność ze starymi bazami.
Pełny przegląd obu klas dał 93 446 kandydatów i 186 892 składniki, powtarzalnie.
Kandydat nie oznacza dopuszczenia; pełny etap konstrukcji nadal nieukończony.

## Key Decisions
- Dwie addytywne tabele w dotychczasowym, niewydanym schemacie generatora tworzą się wyłącznie w nowych bazach. Nie migrujemy wcześniejszych przebiegów.
- SHA256 kanonicznego śladu odróżnia homonimy, źródła i rozwinięte tagi; techniczne ID SQLite nie tworzy klucza.
- Każdy składnik źródłowy ma FK do surowego rekordu SGJP; partykuła gramatyczna nie udaje takiego rekordu.
- Ponowne materializowanie tej samej treści nie dubluje kandydatów. Istniejące interpretation nie są usuwane lub zastępowane.
- Brak pełnej macierzy pozostawia constructions pending i INCOMPLETE; błąd potwierdzonej klasy zapisuje failed.

## Open Questions / Risks
- Pozostałe konstrukcje, pełne decyzje, powiązania kandydatów z KWJP oraz pełny indeks/odbiór nadal wymagają wykonania.
- Runtime jest projekcją wszystkich wejść dwóch potwierdzonych klas z pełnego G2, a nie pełnym nowym build czy wydaniem.
- Ślad nie ma końcowej kwalifikacji; lookup identyfikatora nie zastępuje przyszłych hashów/verdict.

## Pełny runtime klas

[Raport](persisted-constructions-runtime.json) wiąże kod hashami, rozlicza pełną projekcję oraz powtórzenie. Oryginalny pełny G2 był dołączony readonly; zapis wykonywano wyłącznie w nowym lokalnym katalogu diagnostycznym data/work. Nie modyfikowano źródeł ani historycznej bazy. Projekcja obejmuje 92 628 interpretacji; każda została zachowana po konstrukcjach.

| Jednostka | Liczba |
|---|---:|
| Źródłowe interpretacje impt | 92 622 |
| Źródłowe by | 2 |
| Źródłowe nwok aglt | 4 |
| Kandydaci impt + partykuła, po rozwinięciu tagów | 93 438 |
| Kandydaci by + aglt, z oddzielnymi analizami by | 8 |
| Razem kandydaci | 93 446 |
| Składniki | 186 892 |
| Nowi kandydaci przy powtórzeniu | 0 |

Trzy różne wynikowe oryginały mają już bezpośredni wpis w całym źródle. Nie są dublowane w interpretation ani automatycznie kwalifikowane. Kontrola foreign_key_check nie zwróciła naruszeń, integrity_check=ok; powtórzony digest uporządkowanych kluczy identyczny. Cały diagnostyczny przebieg projekcji, dwukrotnej materializacji i kontroli trwał 129.014 s; nie jest to koszt pełnego build G8.

## Explain i regresje

Rzeczywiste czytajże/dajcież wskazują po jednym zapisanym śladzie, bym/byśmy po dwa ślady różnych analiz by. Czytajżeż i nibym nie otrzymują kandydatów. Zapisany ślad nadal ma candidate_not_qualified, oceny członkostwa pozostają unresolved. JSON/tekst pokazują ID; bazy bez nowych tabel zachowują odtwarzanie na żądanie, z null persisted_candidate_key.

Trzy testy persistence miały red brak funkcji; dwa build miały red brak kandydatów/brak odmowy błędnej klasy; dwa explain miały red brak persisted_candidate_key. Green obejmuje wszystkie siedem oraz powiązane testy. Test istniejących alternatywnych analiz wykrył kolizję lokalnej nazwy klucza, która ucinała kolejnych kandydatów; poprawiono nazwę i uruchomiono całą suitę. Runtime zapytań odświeżono w nowym interpreterze po poprawce, readonly total_changes=0; wcześniejsze liczniki i powtórzenie materializacji nie zależały od tej poprawki.

## Granica dowodów semantycznych

Wznowione wyszukiwanie w sprawdzonych fragmentach eksportera i kompilatora źródłowego potwierdziło przekazywanie kwalifikatorów, ale nie dostarczyło definicji starszych etykiet. lexeme_export-61daf78.py:206–231 wybiera kwal; serializer.py:123–125 serializuje ich dosłowne zestawy. Nie czytano wyłączonych danych leksykalnych PoliMorf. Luki definicji i odroczenie źródeł społecznościowych pozostają bez zmian.

2026-10-05T01:08:36Z — Generator104/104; baseline/preflight i artefakty sprawdzane przed commitem. G3–G6 częściowe, plan8/36.
