# Diagnostyczny indeks kanoniczny I2

## TL;DR
Nowe build zapisują reports/canonical-index.json z hashami i rozmiarami treści.
Dwa niezależne małe build mają identyczny indeks; zmiana raportu zmienia indeks.
Indeks pozostaje INCOMPLETE, wskazuje brak list i raportu pełnego pokrycia.

## Key Decisions
- Zamknięty zestaw raportów i przyszłych list, źródła/dowody/konfiguracje związane SHA.
- Czasy, RSS, lokalne ścieżki, manifest runtime, review/verify/logi i fizyczne bajty SQLite poza porównaniem. Hash logical-content jest raportem w indeksie.
- Dowiązanie i plik poza przebiegiem odrzucane; brakujące części nie zastępowane pustymi plikami.

## Open Questions / Risks
- To diagnostyczny fragment G6.4, nie kompletny pakiet ani weryfikacja kodu/review/peer-run z G7.
- Pełna macierz, listy i późniejszy verify/export pozostają do wykonania.

## Test-first
Dwa testy red ImportError→green: identyczność po zmianie czasu/performance, różnica po zmianie inventory, jawne missing i odmowa symlink. Integracja w build; focused reports/build27/27 OK. Żadne readiness ani etapy nie zostały podniesione.
