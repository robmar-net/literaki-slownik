# Analiza luk: #11 pilotaż TEMATY „morze”

## TL;DR
- TEMATY nie istnieje: brak modułu, podkomendy, configów, checkera, ADR-010/011, not źródeł i strony wiki. Wzór POP00 pokrywa szkielet.
- Słowosieć 4.5 jest na dysku (SHA-256 zipa potwierdzone), ale `plwn45.sqlite` ma kolumny `owner` (82 redaktorów) i nie ma skryptu, który ją odtwarza. IATE brak.
- Lista 37 słów oczywistych (próg bramki) leży tylko w scratchpadzie starej sesji. Trzeba ją przypiąć w repo.
- Do operatora: rozmiar przeglądu R2 (ticket: 30 słów, projekt: 30 na warstwę), progi bramki, los żeglugi śródlądowej w T3, dodatki i korzenie T2.
- Ryzyko średnie, nakład średni do wysokiego.

## Kluczowe decyzje
- Cechy: nowa funkcja (`creates_new_entities`), z drobnymi zmianami istniejącego kodu (`cli.py`, `quality.SEEDS`, `pop._write_gzip`). Operacje na danych tak, ale to potok wsadowy, nie CRUD. Brak UI i brak defektu.
- Zmiana addytywna: POP, POP0 i POP00 się nie zmieniają. Kompatybilność: ścisła dla istniejących podkomend i pakietów.
- Ustalone wcześniej, nie pytamy: atomy T1 `mors.`, `żegl.`, `ryb.` (całe atomy); relacje T2 11, 25, 27 bez skojarzeń; IATE TBX 2019, terminy jednowyrazowe typu „term”, niezawodność ≥ 3; leksem SGJP i formy ∩ STANDARD; flaga `wieloznaczny`; jeden pakiet TEMATY; ścieżki configów; ADR-010 i ADR-011.
- Sprawy techniczne rozstrzyga agent i zapisuje w ADR, bez pytania operatora. Dotyczy to pochodnej Słowosieci, kierunku relacji 11, parsera TBX, re-hashowania wejść i wspólnych kroków pakowania.

## Otwarte pytania / ryzyka
- `plwn45.sqlite` (sha `b8cc27b8…4eb9`) ma kolumnę `owner` w `synset`, `lexicalunit` i `synsetrelation`: 282 146 jednostek z wpisem, 82 redaktorów. Tabel `owner` ani logu IP w niej nie ma, ale nazwiska są. Nie wiadomo, czym zbudowano ten plik. Potrzebny skrypt w repo: zip → SQLite bez `owner` i `comment`, z przypiętym hashem.
- Relacja 11 w 4.5 to „hiperonimia”. Kierunek `PARENT_ID`/`CHILD_ID` trzeba sprawdzić na `statek 1`, zanim powstanie domknięcie. Odwrócony kierunek wciągnąłby całe ogólne słownictwo.
- POP00 `pop00-v1-20261021-r2-a` ma stan BUILT, nie wydany. Przypinamy hash `3db703ef…2dbbf`. Nowa budowa POP00 zmieni liczby przecięć.
- Pobranie IATE (112,8 MB) jest za darmo i bez logowania. Adres z badania jest sprawdzony tylko nagłówkiem. Rozmiar i SHA-256 zapisujemy po pobraniu.
- Kwalifikator SGJP oznacza termin, a nie temat. T1 może być mało grywalna. Raport przecięć z POP to pokaże.
- `ryb.` obejmuje też rybactwo śródlądowe. Atom jest ustalony; skutek wychodzi w przeglądzie.

## Podsumowanie
- **Ryzyko**: średnie (źródła, licencja, dane osobowe w pochodnej, jakość T2/T3; kod jest izolowany).
- **Nakład**: średni–wysoki (~12–15 plików, trzy nowe parsery źródeł, przegląd z operatorem).
- **Cechy**: creates_new_entities, involves_data_operations, modifies_existing_code (drobno).

## Cechy zadania
- Defekt do odtworzenia: nie
- Zmienia istniejący kod: tak (drobno: rejestracja CLI, `SEEDS`, upublicznienie `_write_gzip`, ewentualnie `explain --variant`)
- Tworzy nowe byty: tak
- Operacje na danych: tak (wsadowy potok, odczyt tylko do odczytu)
- UI: nie (wiki to dokumentacja, nie UI aplikacji)

## Luki

### Brakuje (stan zmierzony 2026-10-28)
| Element | Stan | Dowód |
|---|---|---|
| `literaki_slownik/tematy.py`, podkomenda `tematy` | brak | `cli.py` ma tylko `pop00` (51–55) |
| `config/generator/tematy.json`, `tematy-sources.json`, `tematy/morze.json` | brak | `ls config/generator` |
| `scripts/check_tematy_package.py`, testy `test_tematy*` | brak | — |
| ADR-010, ADR-011 | brak | `docs/adr/` kończy się na ADR-009 |
| Not plWordNet i IATE w `ATTRIBUTIONS.md` | brak | grep: 0 trafień |
| IATE TBX 2019 | brak na dysku | `cache/` bez `iate/` |
| Skrypt pochodnej Słowosieci | brak | pochodzenie `plwn45.sqlite` nieznane |
| Lista 37 słów oczywistych | tylko poza repo | `…/7eed58b5…/scratchpad/td/cover.py` |
| `SEEDS['tematy-quality-v1']` | brak; `_config` wymusza 30 na warstwę | `quality.py:12–26` |
| Strona wiki `Slownik-TEMATY` | brak; `Home` mówi tylko „planowane” | `wiki-literaki-slownik/` |
| Dokumentacja `docs/generator/cli.md`, `raporty.md`, `jakosc.md`, `etykiety.md` | bez TEMATY | — |

### Niepełne
- Słowosieć 4.5: zip przypięty (`30edc5f8…dcbc`, sprawdzone `shasum`), ale leży w `data/work/`, a nie w `cache/plwordnet/`. Data pobrania nie jest zapisana.
- Wejścia do przecięć istnieją i hashe się zgadzają: pop-v3 `4acb7014…1d58`, STANDARD v31 `dab4f3bc…fa7d`, POP00 r2-a `3db703ef…2dbbf`.
- Korzenie T2 z projektu istnieją w 4.5: 7354 `statek 1`, 2149 `okręt 1`, 4511 `łódź 2`, 6214 `marynarz 1`, 14136 `żegluga 1`, 14515 `żeglarstwo 1`.

### Zmiany zachowania
- Brak. Istniejące podkomendy i pakiety bez zmian.

## Nowa funkcja: punkty integracji
- `cli.py`: parser i dispatch `tematy`; opcjonalnie `explain --variant tematy`.
- `quality.py`: nowy wpis w `SEEDS`. Próba 50 na warstwę, a `_config` dopuszcza tylko 30. Potrzebna osobna ścieżka konfiguracji próby.
- Wzory: `pop00.py` (wejścia, staging, `rename_noreplace`, `confirm_unchanged`), `scripts/check_pop00_package.py`, `scripts/audit_kwjp.py --fetch` (pobieranie), `tests/pop00_helpers.py`.
- Wpływ na architekturę: niski. Jeden nowy moduł i wydzielenie wspólnych kroków pakowania.

## Cykl danych (potok wsadowy)
CRUD nie ma tu zastosowania. Sprawdzamy, czy każdy wynik ma odbiorcę i każde wejście ma źródło.

| Krok | Wejście | Wyjście | Odbiorca | Stan |
|---|---|---|---|---|
| Pobranie | URL IATE, zip Słowosieci | `cache/…` + manifest | build | brak (IATE), niepełne (Słowosieć) |
| Build | manifest, config | pakiet TEMATY | checker, wiki, boty (poza zakresem) | brak |
| Diagnostyka | kandydaci przed filtrem | `reports/summary.json` | raport bramki, wiki | brak |
| Przegląd R2 | próba | oceny → stan REVIEWED | bramka operatora | brak |
| Wiki | manifest | `Slownik-TEMATY` | gracze | brak |

Kompletność: 0% (nic nie istnieje). Osieroconych operacji nie ma, bo wszystko powstaje w tym zadaniu. Pakiet nie ma jeszcze konsumenta w botach i tak ma zostać: integracja z botami jest poza zakresem.

## Decyzje do podjęcia

### Krytyczne (przed specyfikacją)
1. **Rozmiar przeglądu R2.** Ticket (D3) mówi, że operator ocenia 30 słów. Projekt i progi zakładają 30 na warstwę, czyli 90.
   - A: 30 razem, po 10 na warstwę; progi przeliczone (T1 ≥ 9/10, T2 i T3 ≥ 7/10). Przy 10 słowach jeden błąd przesuwa wynik o 10 p.p. **Rekomendacja**: zgodne z D3, a agent i tak ocenia 50 na warstwę.
   - B: 30 na warstwę, razem 90; progi jak w projekcie.
   - C: 30 razem, tylko T2 i T3 (po 15). T1 zmierzono w badaniu (29/30).
   - Wpływ: nakład operatora i siła bramki.
2. **Progi bramki.** W projekcie są tylko propozycją: pokrycie 37 słów ≥ 70%, T1 ≥ 27/30, T2 ≥ 20/30 (≤ 3 błędne), T3 ≥ 20/30, zgodność ≥ 80%.
   - A: przyjąć progi, przeliczone na wybrany rozmiar R2. **Rekomendacja.**
   - B: zmienić progi.
   - C: bramka bez progów, tylko ocena operatora.
   - Wpływ: decyduje o „dalej / popraw / stop” i o fali ~10 tematów.
3. **Żegluga śródlądowa w T3 (IATE 4821).** Dziedzina 4821 to „transport morski i śródlądowy”. Pilotaż zmierzy udział terminów śródlądowych. Pytanie: co zrobić z wynikiem. Przykłady: `barka`, `śluza`, `holownik`, `prom`.
   - A: zostawić całe 4821, zmierzyć udział, opisać w `LIMITATIONS.md`, a wyraźnie rzeczne terminy wykluczać w konfiguracji po przeglądzie. **Rekomendacja**: temat to „morze i żegluga”, a te słowa pasują do gry.
   - B: wykluczyć z góry hasła z cechą śródlądową, jeśli TBX ją niesie (do sprawdzenia po pobraniu).
   - C: odłożyć T3, jeśli udział śródlądowych przekroczy ustalony próg.
   - Wpływ: skład T3 i strona wiki.

### Ważne (domyślne, jeśli operator nic nie powie)
1. **Dodatki ręczne w `morze-v1`.** Projekt podaje `sztorm` jako dodatek. `sztorm` należy też do testu 37 słów, więc dodatek zawyżyłby pokrycie.
   - A: v1 bez dodatków; pokrycie mierzone na samych źródłach; dodatki dopiero po przeglądzie, z powodem. **Domyślnie.**
   - B: dodatki od razu, a pokrycie 37 słów podawane z dodatkami i bez nich.
   - Wpływ: uczciwość pomiaru T2/T3.
2. **Korzenie T2.** Projekt ma 6 korzeni z badania (statek, okręt, łódź, marynarz, żegluga, żeglarstwo). Wybrał je jeden oceniający.
   - A: te 6 korzeni, bez wykluczeń poddrzew w v1; wykluczenia po przeglądzie. **Domyślnie.**
   - B: operator zatwierdza listę korzeni przed budową.
   - Wpływ: rozmiar i trafność T2.
3. **Lista 37 słów oczywistych jako zbiór testowy bramki.** Dziś leży tylko w scratchpadzie (`kotwica kil maszt żagiel ster bosman rufa burta pokład statek okręt marynarz jacht sztorm kambuz bandera reja bom fok szalupa kuter rybak mesa kabestan sternik cumować halsować falochron nabrzeże kuk bakburta sterburta grot achtersztag knaga szkuta trał`).
   - A: przypiąć ją bez zmian w configu metody; nie zmieniać jej po zobaczeniu wyników. **Domyślnie.**
   - B: operator poprawia listę przed budową.
   - Wpływ: próg 70%.

## Rekomendacje
- Kolejność: strona wiki „W przygotowaniu” → ADR-010/011 → pobranie IATE i skrypt pochodnej Słowosieci → moduł i testy → dwie budowy a/b → checker → przegląd R2 → raport bramki.
- Pochodna Słowosieci: tylko `synset` (ID, unitsstr), `lexicalunit` (ID, lemma, pos, variant), `unitandsynset`, `synsetrelation` (bez `owner`), `relationtype`. Hash pochodnej przypięty osobno.
- `confirm_unchanged` re-hashuje każde wejście, także pliki w pakietach POP i POP00 (błąd naprawiony w f33fe05).
- Lematy Słowosieci i IATE mapujemy na leksemy przez `lemma_base` i część mowy. Homonimy dostają `wieloznaczny`.
- JSON-ów przeglądu nie commitujemy dwa razy (lekcja z POP00).

## Ocena ryzyka
- **Złożoność**: średnia. Trzy parsery (etykiety SGJP, graf Słowosieci, TBX) i scalanie warstw.
- **Integracja**: niska. Nowa podkomenda, brak konsumentów.
- **Regresja**: niska. Wspólne punkty to `cli.py`, `quality.SEEDS` i `pop._write_gzip`; testy POP i POP00 je pilnują.
- **Dane i licencje**: średnie. Nazwiska redaktorów w pochodnej, nota licencji Słowosieci „4.2 © 2020”, IATE z 2019 r.
