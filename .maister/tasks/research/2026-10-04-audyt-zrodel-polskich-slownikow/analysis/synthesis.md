# Synteza dowodów audytu

## TL;DR
Audyt potwierdza wykonalność pierwszego generatora na konkretnym eksporcie SGJP z pomocniczym KWJP100.
Zbadano całe wejście SGJP, 13 list KWJP i techniczną zawartość unigramów NKJP.
NKJP pozostaje zablokowany do konstrukcji i dopasowań z powodu nieustalonej wersji warunków CC-BY.
Filtry dają policzone scenariusze, nie zatwierdzone słowniki produkcyjne.

## Key Decisions
- SGJP i KWJP mają udokumentowane warunki użycia dla wskazanych plików; zachowujemy atrybucje.
- Preferujemy pełne formy zapisane w SGJP. Nie dopisujemy wyników mechanicznego łączenia segmentów.
- SJP.pl nie pobrano, benchmarku nie uruchomiono, OSPS nie wykorzystano. Dane wyłączonych źródeł nie są wejściami obliczeń.
- Potwierdzenie formy w korpusie pozostaje odrębne od dopuszczalności i tożsamości leksemu.

## Open Questions / Risks
- Warunki NKJP wymagają oficjalnego doprecyzowania; nie oznacza to niedostępności technicznej ani oceny legalności cudzych zastosowań.
- Mieszane kwalifikatory, pisownia części skrótowców i konstrukcje `bym/przezeń/czytajże` wymagają rozstrzygnięcia przed końcowym generatorem.
- Pomiary mają wysoką pewność dla tych bajtów. Kompletność wszystkich klas fleksji, cała historia anotacji i jakość modelu znajomości nie są dowiedzione.

## Zgodność i rozbieżności
Eksport i reguły potwierdzają pełne osobowe formy praet/cond, ale różnią się zapisem dwóch tagów ń. Dokumentacja KWJP i pliki zgadzają się co do progu globalnego; rzeczywiste nagłówki, mianowniki IPM i Dice wymagają odróżnienia od UI. NKJP ma deklarację CC-BY bez wersji i inny porządek kolumn niż opis.

## Wniosek
Rozpoczęcie generatora na SGJP/KWJP jest wykonalne. Nie ma dowodu potrzeby automatycznej rekonstrukcji całej fleksji; jest dowód ryzyka nadgeneracji. NKJP nie jest warunkiem technicznym statystyk SGJP, ale blokuje obecne połączenie trzech źródeł. Potwierdzone wejścia nie są zapewnieniem o całej historii danych zewnętrznych.

## Materiały
- [Raport](../outputs/research-report.md) — pełne10 wymagań i rekomendacje.
- [SGJP i reguły](findings/sgjp-rules.md).
- [KWJP](findings/kwjp-findings.md).
- [NKJP](findings/nkjp-audit.md).
- [Model procesu](findings/model-procesu.md).
