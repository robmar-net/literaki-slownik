Pierwsze wydanie **TEMATY**: 10 słowników tematycznych, razem **13 597 słów** (leksemów) i **125 072 formy**.
Każdy temat jest podzbiorem [STANDARD](https://github.com/robmar-net/literaki-slownik/wiki/Slownik-STANDARD).

| temat | wersja | słowa | formy | przykład |
|---|---|---:|---:|---|
| grzyby | v2 | 211 | 1 848 | borowik |
| pogoda | v2 | 239 | 2 191 | mżawka |
| matematyka | v3 | 467 | 4 248 | ułamek |
| muzyka | v2 | 1 060 | 9 158 | skrzypce |
| sport | v2 | 808 | 8 021 | boisko |
| kuchnia | v2 | 1 815 | 16 064 | patelnia |
| rośliny | v1 | 2 371 | 22 244 | paproć |
| zwierzęta | v1 | 2 765 | 23 880 | jeż |
| medycyna | v3 | 2 891 | 26 383 | gorączka |
| morze | v2 | 970 | 11 035 | sztorm |

Metoda `tematy-v2` ([ADR-010](https://github.com/robmar-net/literaki-slownik/blob/tematy-v2/docs/adr/ADR-010-tematy-v1.md), [ADR-012](https://github.com/robmar-net/literaki-slownik/blob/tematy-v2/docs/adr/ADR-012-tematy-fala-1.md), [ADR-013](https://github.com/robmar-net/literaki-slownik/blob/tematy-v2/docs/adr/ADR-013-tematy-v2-fali-1.md)). Słowo trafia do tematu z jednej z warstw:
- T1: etykiety dziedzin SGJP;
- T2: Słowosieć 4.5, słowa podrzędne wobec wybranych pojęć tematu;
- T3: IATE 2019, tylko „morze”;
- D: ręczne dodatki (morze, grzyby, pogoda, sport);
- wykluczenia: słowa ocenione jako spoza tematu.

Kontrola: wszystkie 10 tematów zbudowane z jednego commita (`c563c33`), każdy dwa razy, z identycznymi bajtami.
Niezależny checker przechodzi, także z przeglądem trafności próbki. Ocenę dał agent AI; dla „morza” także właściciel.

Pliki:
- `<TEMAT>.txt.gz` (10 plików): posortowana lista UTF-8, małe litery, jedna forma w wierszu;
- `tematy-v2-pakiety.tar.gz`: pełne pakiety 10 tematów (lista, TSV z warstwą i powodem każdego słowa, raport, próbka, manifest, atrybucje, warunki, ograniczenia) i 10 przeglądów związanych hashami z pakietami;
- `SHA256SUMS`: sumy plików wydania; `SHA256SUMS-rozpakowane`: sumy list po rozpakowaniu.

**Ograniczenia:**
- temat przypisujemy słowu, nie znaczeniu: słowo wieloznaczne wchodzi całe;
- T2 daje szum; w ocenie agenta poniżej progu zostały grzyby (T2), medycyna (T1) i morze (T2, ale właściciel ocenił 30/30); właściciel przyjął je mimo to;
- przegląd próbki nie jest badaniem graczy; słownik nie zmienia gry, włączenie wymaga osobnej pracy.

Formy SGJP: BSD-2-Clause z pełną atrybucją. Wybór słów ze Słowosieci: licencja plWordNet z notą. IATE (tylko „morze”): kopiowanie i utwory pochodne z podaniem źródła. Pełne zawiadomienia w `ATTRIBUTIONS.md`, `TERMS.md` i `LIMITATIONS.md` każdego pakietu.

[Wiki TEMATY](https://github.com/robmar-net/literaki-slownik/wiki/Slownik-TEMATY) · [#11](https://github.com/robmar-net/literaki-slownik/issues/11) · [#12](https://github.com/robmar-net/literaki-slownik/issues/12) · [#13](https://github.com/robmar-net/literaki-slownik/issues/13) · [#14](https://github.com/robmar-net/literaki-slownik/issues/14)
