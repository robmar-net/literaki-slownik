# Udokumentowane warianty pisowni — wdrożenie

## TL;DR
Zatwierdzone A wdrożono dla angol/jugol jako dwóch osobnych kandydatów pisowni.
Pięć testów przeszło red→green; dwie rzeczywiste projekcje mają identyczną treść logiczną.
Oryginalne wpisy i homonimy zachowano; pełne członkostwo pozostaje unresolved.

## Key Decisions
- Dokładne rekordy, hash SGJP oraz dokument RJP są warunkami zamkniętej reguły; brak dopasowania nie tworzy kandydata.
- Kandydat ma jeden składnik źródłowy, trace ortograficzny i dowód tylko warunku pisowni. Nie jest sklejeniem ani nowym leksemem.
- Utrwalony zapis jest weryfikowany przez odtworzenie z rzeczywistego źródła i porównanie wszystkich pól/składników; podmiana dokumentu, źródła lub relacji jest odrzucana przed ocenami.
- Pierwszy zakres obejmuje literalne mianowniki; dalszej fleksji nie generujemy.

## Open Questions / Risks
- Pełna klasa mieszkańców, semantyka i macierz normatywna nadal otwarte.
- Dodatni dowód pisowni nie domyka języka, gry ani całego wydania.

## Sprawdzenie

[Runtime](spelling-variants-runtime.json): wszystkie trzy źródłowe homonimy dwóch kluczy, dwa nowe warianty, pięć analiz, dziesięć ocen. Dwie nowe bazy projekcyjne: identyczny logical-content, powtórzenie bez nowych rekordów, FK/integrity OK. Oryginalna baza i źródłowe rekordy bez zmian; osiem readonly explain tekst/JSON zgodnych z zapisem. Nie jest to pełny build G8.

Pliki: constructions/policy/decisions/explain, przypięte orthography/policy/sources i test_spelling_variants. Schema2 bez migracji. Wersja runtime diagnostic-approved-conditions-v17. Decyzja: [zatwierdzone A](documented-spelling-variants-decision.md).
