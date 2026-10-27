# Plan badania: słowniki tematyczne

## TL;DR
Badanie mieszane: najpierw liczymy, potem czytamy dokumentację.
Wstępny odczyt: eksport SGJP 20260823 ma już kwalifikatory dziedzin (73 tematy, m.in. `mors.`, `żegl.`, `roln.`, `mat.`, `ryb.`).
Trzeba zmierzyć, ile leksemów je ma i czy wystarczą na listę tematyczną.
Trzy zbieracze równolegle: dane lokalne, kod i dokumentacja projektu, zasoby PAN w sieci.

## Key Decisions
- Trzy zbieracze, nie cztery. Źródła spoza PAN każdy zbieracz tylko notuje przy okazji, w osobnej sekcji. Osobny zbieracz do ich szukania przeczyłby briefowi.
- Liczymy leksemy (lemat + ID SGJP), nie formy. Eksport tab ma formy, a kwalifikator jest powtarzany przy każdej.
- Etykiety złożone (`anat.,zool.`) liczymy dosłownie i osobno po atomach. Atomy rozbijamy tylko w analizie, nie w kodzie generatora.
- Próba dla 3 tematów: marynistyka (`mors.`, `żegl.`, `ryb.`), rolnictwo (`roln.`, `ogr.`, `zootechn.`, `pszcz.`, `leśn.`), matematyka (`mat.`).
- Używamy plików z `cache/` i istniejącej bazy `build.sqlite`. Nie pobieramy dużych danych.

## Open Questions / Risks
- Pokrycie: większość słów z danej dziedziny może nie mieć etykiety. Trzeba to oszacować na próbce słów spoza etykiet.
- Jeden ID SGJP może łączyć znaczenia. Etykieta dziedziny może dotyczyć tylko jednego znaczenia (np. `mat` szachowy i matematyczny).
- KWJP ma podkorpusy gatunkowe (fakt, fikcja, publicystyka), nie dziedzinowe. Mogą nie pomóc.
- WSJP (IJP PAN) ma kwalifikatory dziedzinowe, ale licencja i sposób dostępu są nieznane. Nie pytamy autorów.

## 1. Pytanie i zakres
**Pytanie:** czy dane projektu albo zasoby PAN mają informację o dziedzinie słowa, która pozwala zawęzić listę do tematu?

**Podpytania:**
1. Które źródła lokalne mają etykietę dziedziny? Jaką i dla ilu leksemów?
2. Ile leksemów wskażemy dla marynistyki, rolnictwa i matematyki? Jak trafne są na próbce?
3. Ile słów z tematu nie ma etykiety (szacunek pokrycia)?
4. Jak kod i dokumenty projektu traktują dziś te etykiety?
5. Jakie zasoby PAN (IPI PAN, IJP PAN) mają dziedzinę? Na jakiej licencji? Czy da się je pobrać bez kontaktu z autorami?
6. Co spoza PAN wyszło przy okazji (lista kandydatów na później)?

**W zakresie:** SGJP (eksport tab, oznaczenia, instrukcja), Morfeusz, KWJP100, NKJP, WSJP, inne zasoby PAN.
**Poza zakresem:** wdrożenie, zmiana reguł gry, kontakt z autorami, Wikisłownik (odroczony), aktywne szukanie poza PAN.

## 2. Metoda
- **Technika (główna):** pomiar na danych lokalnych. Skrypty w scratchpadzie lub `tmp/`, czytające `cache/` i bazę tylko do odczytu.
- **Literatura:** dokumentacja PAN w sieci (WebFetch/WebSearch), cytowana z adresem i datą odczytu.
- **Zapasowo:** gdy baza `build.sqlite` (22 GB) jest za wolna, czytamy strumieniowo `cache/sgjp/sgjp-20260823.tab.gz` (pole 5 = kwalifikatory).

**Rama analizy (dla każdego źródła):**
| Kolumna | Treść |
|---|---|
| Dziedzina? | tak / nie / pośrednio |
| Rodzaj | kwalifikator, gatunek tekstu, podkorpus, metadane |
| Zasięg | liczba leksemów z etykietą |
| Trafność | wynik próbki |
| Licencja | nazwa, link, czy pozwala na publikację listy |
| Dostęp | lokalnie / pobranie / tylko przeglądarka |

## 3. Fazy
1. **Odkrycie.** Lista etykiet dziedzin (`descriptive-label-review.json`, pole `topics`) i ich liczniki z `config/generator/qualifiers.json`. Spis plików KWJP i NKJP z metadanymi.
2. **Pomiar.** Liczba leksemów na etykietę dziedziny (dosłownie i po atomach). Ile z nich jest w LL-PL-BROAD i LL-PL-STANDARD v30/v31.
3. **Próba tematów.** Dla 3 tematów: liczba leksemów, 30 losowych przykładów z oceną (trafne / wątpliwe / błędne). Szacunek pokrycia: 20–30 oczywistych słów z tematu (np. `kotwica`, `kil`, `orka`, `brona`, `całka`, `wektor`) i sprawdzenie, czy mają etykietę.
4. **Weryfikacja.** Zgodność liczników z `label-coverage.json`. Zgodność skrótów z `cache/sgjp/oznaczenia.html`. Krzyżowo: wnioski z danych i z dokumentacji PAN.

## 4. Gathering Strategy

### Instances: 3

| # | Category ID | Focus Area | Tools | Output Prefix |
|---|---|---|---|---|
| 1 | local-data | Pomiar etykiet dziedzin w eksporcie SGJP i bazie; metadane KWJP/NKJP; próba 3 tematów i szacunek pokrycia | Bash (python3, gzip, sqlite3 tylko do odczytu), Read, Grep | local-data |
| 2 | code-docs | Jak kod (`policy.py`, `sgjp.py`, `kwjp.py`), konfiguracja (`qualifiers.json`) i dokumenty (`etykiety.md`, audyt, dowody) obsługują kwalifikatory dziedzin; co już zmierzono | Read, Grep, Glob | code-docs |
| 3 | pan-resources | Dokumentacja PAN w sieci: oznaczenia i instrukcja SGJP, WSJP (kwalifikatory dziedzinowe), NKJP (metadane tekstów), KWJP (podkorpusy, KWJP½M), inne korpusy i listy terminów IPI PAN/IJP PAN; licencje i dostęp | WebFetch, WebSearch, Read | pan-resources |

Wyniki: `analysis/findings/<prefix>-*.md`.

**Uwagi dla zbieraczy:**
- Pisz po polsku, bardzo zwięźle. Na górze pliku blok TL;DR / Key Decisions / Open Questions.
- Każda liczba z poleceniem lub plikiem, z którego pochodzi.
- Źródła spoza PAN tylko w sekcji „Kandydaci spoza PAN (przy okazji)”. Bez szukania ich celowo.
- Nie kontaktuj autorów. Nie pobieraj dużych plików. Nie wymieniaj gier słownych innych niż Literaki i Kurnik.
- Bazę `build.sqlite` otwieraj tylko do odczytu (`file:...?mode=ro`).

### Rationale
Pytanie ma trzy osobne źródła dowodu: dane (ile i jak trafnie), projekt (co już wiadomo i jak to działa), PAN (co jeszcze istnieje i na jakich warunkach). Konfiguracja projektu jest mała i należy do code-docs. Osobny zbieracz „wider-candidates” wyszedłby poza zakres briefu.

## 5. Kryteria sukcesu
1. Tabela z ramy analizy dla każdego źródła: SGJP, Morfeusz, KWJP100, NKJP, WSJP i każde inne znalezione źródło PAN.
2. Dla 3 tematów: liczba leksemów (ogółem i w BROAD/STANDARD), wynik próbki 30 przykładów, szacunek pokrycia.
3. Jasna odpowiedź: „mamy dane” albo „nie mamy, trzeba szerzej”, z listą kandydatów do szerszego szukania.
4. Licencja znana dla każdego źródła, które polecamy.

## 6. Wyniki
- `outputs/research-report.md` z odpowiedzią, tabelą źródeł i próbą tematów.
- Lista kandydatów do szerszego szukania (bez decyzji).
- Bez wdrożenia; ewentualny kolejny krok proponujemy użytkownikowi.
