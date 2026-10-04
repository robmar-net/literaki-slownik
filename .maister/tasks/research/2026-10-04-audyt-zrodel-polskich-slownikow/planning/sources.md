# Źródła zaplanowane do audytu

## TL;DR
Głównym wejściem jest tekstowy eksport SGJP.
KWJP100 i NKJP dostarczają dowodów użycia, nie nowych leksemów.
Wszystkie źródła obowiązkowe zaczynają ze statusem oczekującym sprawdzenia.

## Key Decisions
- Zakres wyznacza rozdział 15 specyfikacji v3.
- Odróżniamy pomiar, interpretację, rekomendację i niewykonane badanie.

## Open Questions / Risks
- Statusy licencyjne i możliwości rekonstrukcji fleksji wymagają sprawdzenia dla konkretnych plików.

| Kategoria | Punkty startowe | Pytania |
|---|---|---|
| SGJP | https://morfeusz.sgjp.pl/download/ ; https://morfeusz.sgjp.pl/doc/license/en ; https://download.sgjp.pl/morfeusz/Morfeusz2.pdf | wydanie, licencja plików, format, segmenty i reguły |
| KWJP100 | https://github.com/ipipan/kwjp100-varia ; https://kwjp.pl/lists/doc/about/ ; https://kwjp.pl/lists/ | commit, CC BY, progi, miary, POS, gatunki, anotacja |
| NKJP | https://zil.ipipan.waw.pl/NKJPNGrams | konkretne unigramy, wersja licencji, tokenizacja |
| Pochodzenie | https://zil.ipipan.waw.pl/PoliMorf | udokumentowana przyczyna wyłączenia z konstrukcji |
| Gra | publiczne źródła Literaki Lounge / lokalna specyfikacja bez list słów | alfabet, blanki, min/max długość |

Status realizacji i dowody zostaną utrwalone w findings oraz rejestrze źródeł. Lokalna nowa baza kodu i testów nie istnieje poza dwoma plikami startowymi, co potwierdzono inwentaryzacją.

## Pokrycie po wykonaniu
Wszystkie osiem punktów startowych §16 odczytano. SGJP: download, licencja, PDF i konkretne źródła programu/eksport. KWJP: repo, dokumentacja, przeglądarka; wszystkie12 list słownych i jeden pełny plik bigramów. NKJP: strona, metadane i unigramy; BLOCKED do konstrukcji z powodu nieustalonych warunków. PoliMorf: dokumentacja pochodzenia, bez użycia danych. Źródła opcjonalne §4.4 są wyłączone z podstawowego pierwszego etapu przez zakres specyfikacji. Brakujące wersje modeli anotacji nie są traktowane jako dowód braku zależności.

[Raport](../outputs/research-report.md) i rejestry findings zawierają szczegóły, hashe i statusy. Publiczną konfigurację gry odczytano; część reguł potwierdzono lokalnie, z jawnym ograniczeniem publicznej weryfikowalności. Nie ma istniejącego generatora w nowym repo do przeglądu: powstały wyłącznie skrypty audytowe. Testy tych skryptów i przegląd połączeń wykonano.
