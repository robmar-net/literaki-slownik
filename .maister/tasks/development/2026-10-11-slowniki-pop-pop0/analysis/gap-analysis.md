# Analiza luk: słowniki POP i POP0 (#3)

## TL;DR
- Nie ma nic: brak kodu, raportów, wydania, `explain` i stron wiki dla POP. To nowy, addytywny krok tylko do odczytu nad zamrożonym v29.
- Wstępne sondy (2026-10-11) zmieniają obraz celu właściciela: **98–99% wszystkich tokenów KWJP jest nieosiągalne**. Sufit leksemów jednoznacznych to 93,5%. 98% osiągamy tylko przy węższym mianowniku (~23 tys. leksemów).
- Pełna odmiana jest duża: 5 tys. leksemów → 137 tys. form STANDARD, 40 tys. → 878 tys. Decyzja o „formach typowych” mocno zmienia rozmiar.
- Czyszczenie NKJP to nie szczegół: zdjęcie interpunkcji dodaje 14% masy, ale robi z `ul.` (ulica) słowo `ul` (×140), a z `ok.` słowo `ok` (×23).
- Plan: najpierw skrypt pomiarowy (tylko odczyt) z raportem dla właściciela. Decyzje o metodzie i progach dopiero po nim.

## Key Decisions
- Cechy zadania: nowa encja (pakiet POP), drobne zmiany w istniejącym kodzie (`cli.py`, ewentualnie `explain.py`, `ATTRIBUTIONS.md`), operacje na danych tak, UI brak — w tym repo nie ma interfejsu, tylko CLI, wydanie i wiki.
- Zmiana addytywna, zgodność ścisła: LL-PL v29, `sources.json`, `inputs.py`, testy LL-PL i zamrożony przebieg zostają nietknięte.
- Pomiar to osobny skrypt `scripts/measure_pop.py` (wzór `benchmark_sjp.py`, ale kanoniczny JSON, bez czasów w hashowanej treści). Wynik idzie do nowego katalogu `data/work/pop-measure-*`, nigdy do przebiegu. Decyzja techniczna, odwracalna.
- Pomiar raportuje każdą metodę w kilku wariantach (mianownik, czyszczenie, homonimy, formy). Właściciel wybiera na liczbach, nie na opisach.
- Odczyt KWJP: zbiorczo po zakresie `evidence_id`, nie złączeniem. Sonda z `LEFT JOIN evidence_candidate` trwała >10 min (indeksy częściowe nie działają). Ładowanie słownikowe: 0,5 s.

## Open Questions / Risks
- **Rola w grze vs §2.1/§2.2 spec v3.** POP jako słownik gry odrzuca słowa spoza POP. Spec pozwala na to tylko jako osobny słownik przy stole, nie jako zamiennik STANDARD. Wariant „formy typowe” w grze odrzuci formy, które gracz uzna za oczywiste (pytanie 5 z issue).
- **Serwer gra dziś na `pl-sjp-20260820`, nie na LL-PL.** Bot z POP ⊆ STANDARD przy stole SJP może zagrać słowo spoza SJP. Integracja jest poza zadaniem, ale wiki i wydanie muszą to powiedzieć.
- **Listy `familiar/` na serwerze** są z założenia ręczne, „nie z korpusu” (NOTICE). POP ich nie zastąpi bez zmiany tej zasady.
- **Segmentacja KWJP:** `zrobiłem`, `zrobiłam` nie ma w `orth_lc` (KWJP dzieli na `zrobił`+`em`). W NKJP są (2 979, 1 656). Formy 1./2. os. czasu przeszłego mają w KWJP zawsze brak, nie zero.
- **NKJP na poziomie leksemów:** NKJP ma tylko formy. Forma wspólna kilku leksemów (`lata`, `zamku`) nie może dać F żadnemu z nich bez dzielenia lub kopiowania F (zakazane). Udział takiej masy trzeba zmierzyć.
- **12 453 lematów KWJP AMBIGUOUS** (3,47 mln tokenów, 4,2%). Bez reguły dla homonimów `rok`, `zamek` itd. tracą część dowodów.
- **Treść atrybucji NKJP** („oczyszczamy z doklejonej interpunkcji”) może wymagać zmiany po decyzji o czyszczeniu.
- Nieaktualne „NKJP BLOCKED”: `docs/plan-dalszych-prac-runbook.md:51`. Poprawić w ramach zadania.

## Podsumowanie
- **Ryzyko:** średnie (metoda i progi; technicznie niskie).
- **Nakład:** średni (kod umiarkowany; proces: pomiar, dwie bramki właściciela, przegląd próbek, wydanie, wiki).
- **Cechy:** creates_new_entities, involves_data_operations, modifies_existing_code (drobnie).

## Cechy zadania
| Cecha | Wartość | Dowód |
|---|---|---|
| Defekt do odtworzenia | nie | to nowa funkcja |
| Zmienia istniejący kod | tak, drobnie | podkomenda w `cli.py`; `explain` obsługuje tylko `broad`/`standard` (`explain.py:134`) |
| Tworzy nowe encje | tak | brak `pop` w `literaki_slownik/`, brak wydania POP |
| Operacje na danych | tak | budowa, wydanie, wyjaśnianie pakietu |
| Ciężkie UI | nie | brak UI w repo; gra w osobnym repo |

## Wstępne sondy (tylko odczyt, 2026-10-11)
Liczby z jednorazowych skryptów w scratchpadzie. To nie są artefakty wydania. Pomiar je powtórzy i utrwali.

### KWJP lemma-all → leksemy (tylko EXACT, jeden kandydat)
Suma tokenów: 81 664 894. Leksemów z F: 70 771.

| Leksemów (top) | % wszystkich tokenów | Formy STANDARD (pełna odmiana) |
|---|---|---|
| 5 000 | 81,7% | 137 266 |
| 10 000 | 87,3% | 272 084 |
| 20 000 | 91,1% | 513 607 |
| 40 000 | 93,0% | 878 384 |
| 80 000 (wszystkie 70 771) | 93,5% | 1 242 730 |

| Pokrycie | Mianownik: wszystkie tokeny | Mianownik: masa EXACT |
|---|---|---|
| 90% | 15 779 | – |
| 95% | nieosiągalne | 12 780 |
| 98% | nieosiągalne | 23 348 |
| 99% | nieosiągalne | 32 153 |

Gdzie znika masa (status powiązania): EXACT 93,5%, AMBIGUOUS 4,2%, UNMATCHED 2,2%.
Leksemy EXACT bez żadnej formy w STANDARD: 12 142 (5,7% tokenów). Głównie: jednoliterowe (`i`, `a`, `o`, `u`), skróty (`rok` jako brev), nazwy własne (`Rosja`, `Andrzej`), słowa >15 liter (`odpowiedzialność`). To słuszne wyłączenia, ale muszą wyjść z mianownika.

### NKJP 1grams (suma 246 153 378)
| Wariant | Masa w STANDARD | Udział |
|---|---|---|
| Pełny napis NFC (audyt) | 164 245 128 | 66,7% |
| + zdjęta interpunkcja z brzegów | +34,5 mln, 485 tys. form | +14,0% |

| Przykład | bez kropki | z kropką | Skutek zdjęcia |
|---|---|---|---|
| `ul` (ul pszczeli) | 542 | `ul.` 76 737 | ulica liczona jako ul |
| `ok` | 2 028 | `ok.` 45 255 | „około” liczone jako `ok` |

### Potoczność (przykłady)
| Słowo | KWJP orth_lc | NKJP |
|---|---|---|
| fajnie | 1 441 | 2 981 |
| fajny | 557 | 1 481 |
| spoko | 385 | 902 |
| zajebisty | 58 | 95 |
| ziomal | 16 | 43 |

Słowa potoczne są w obu korpusach. Czy mieszczą się w POP, pokaże ranking.

## Stan obecny vs docelowy
| Obszar | Teraz | Cel (issue #3) | Luka |
|---|---|---|---|
| Pomiar | sondy jednorazowe | raport: leksemy/formy vs pokrycie, formy typowe, zgodność KWJP–NKJP, czyszczenie, potoczność, próbki | cały |
| Metoda | brak | COMMONNESS z rang/percentyli (§9.4), braki ≠ 0 (§8.2) | cała, po decyzjach |
| Build | brak | `pop` deterministyczny, ro, POP0 ⊆ POP ⊆ STANDARD | cały |
| Explain | tylko broad/standard | powód dla słowa w POP/POP0 | rozszerzenie |
| Odbiór | wzorzec LL-PL (verify, dwa buildy, przegląd) | to samo dla POP | nowa konfiguracja próbek (`quality.py` zna tylko `quality-v1`) |
| Wydanie | Release `llpl-v29` | Release POP z manifestem, hashami, atrybucją NKJP, bez surowego NKJP | cały |
| Wiki | brak | `Slownik-POP`, `Slownik-POP0` wg runbooka | cały |

## Luki
### Brakujące
- Skrypt pomiarowy i raport dla właściciela.
- Moduł `pop`, manifest POP z pinami bazy (database 85b23ca5…, release-manifest 54705743…, STANDARD a432c7c5…, NKJP 73af4909…).
- Konfiguracja i walidator próbek POP (granice POP/POP0 wewnątrz i na zewnątrz, braki danych, rozbieżności KWJP–NKJP).
- Zamrożenie i wydanie POP; testy (`tests/test_pop.py`).
- `explain` dla POP/POP0.
- Strony wiki.

### Niepełne
- `ATTRIBUTIONS.md`: tekst NKJP jest, ale opis zmian zależy od reguły czyszczenia.
- Runbook: wzmianka „NKJP BLOCKED” nieaktualna.

## Integracja (nowa encja)
| Punkt | Plik | Uwaga |
|---|---|---|
| CLI | `literaki_slownik/cli.py` | podkomenda `pop` (leniwy import, kody 2–5) |
| Explain | `literaki_slownik/explain.py:134` | `VARIANTS` + powód POP; albo `pop explain` |
| Próbki | `literaki_slownik/quality.py:36` `sample_strata` | nowa konfiguracja, nie `quality-v1` |
| Zamrożenie | `literaki_slownik/export.py` | `rename_noreplace`, pliki 0444 |
| JSON | `literaki_slownik/canonical.py` | kanoniczny zapis |
| Wzór pomiaru | `scripts/benchmark_sjp.py`, `scripts/audit_nkjp.py` (parser) | |

## Ścieżka użytkownika
| Kto | Jak dotrze do POP | Ocena |
|---|---|---|
| Właściciel | raport pomiaru → decyzje → przegląd próbek | wymaga raportu czytelnego, z przykładami |
| Twórca botów / serwera | GitHub Release + wiki `Slownik-POP` | jak LL-PL; odkrywalność 7/10 |
| Gracz | brak w tym zadaniu | integracja w `Literaki-server` osobno |

## Cykl życia danych: pakiet POP
| Operacja | Backend | Interfejs | Dostęp | Stan |
|---|---|---|---|---|
| CREATE | brak `pop` | CLI (brak) | – | w zakresie |
| READ | brak | `explain` (tylko broad/standard) | Release, wiki (brak) | w zakresie |
| UPDATE | nowa wersja = nowy build | – | nowy Release | wzorzec LL-PL |
| DELETE | n/d (wycofanie wg ADR-006: wydanie bez NKJP) | – | – | n/d |

Kompletność dziś: 0% (nowa encja). Po zakresie issue: 100% w tym repo. Osierocenie: pakiet bez odbiorcy do czasu prac w serwerze. Issue to przyjmuje.

## Decyzje odłożone do raportu z pomiaru
Nie decydujemy teraz. Pomiar pokaże dla każdej opcje, liczby i przykłady.

| # | Decyzja | Co pokaże pomiar |
|---|---|---|
| D1 | Mianownik pokrycia | krzywe dla: wszystkich tokenów, masy EXACT, masy leksemów z formą w STANDARD |
| D2 | Formy typowe | udział masy form wg klas znaczników (wołacz, tryb rozkazujący, imiesłowy, os. 1/2); liczba form na próg |
| D3 | Miara i wagi KWJP/NKJP | zgodność rang (Spearman, nakładanie top-N), wrażliwość progu na wagi |
| D4 | Czyszczenie NKJP | pełny napis / zdjęcie wszystkich znaków / zdjęcie bez kropki; lista kolizji typu `ul.` |
| D5 | Homonimy (AMBIGUOUS, formy NKJP wielu leksemów) | masa i przykłady: brak F / flaga / dowód tylko z formy jednoznacznej |
| D6 | Progi POP i POP0 | liczba leksemów i form, próbki przy granicach |
| D7 | Luka potoczna | ile przykładów wypada; rozbieżność rang NKJP vs KWJP |
| D8 | Statusy braku w POP0 (§8.2) | ile słów STANDARD nie ma danych w żadnym źródle |

## Decyzje potrzebne teraz
### Ważne (z wartością domyślną)
1. **Jeden POP czy dwa warianty form.** Gra chce pełnej odmiany znanych leksemów; boty mogą chcieć form typowych.
   - Opcje: A) mierzyć oba warianty, wybrać po pomiarze; B) tylko formy typowe; C) tylko pełna odmiana.
   - Domyślnie: A. Koszt pomiaru tylko trochę rośnie; decyzja zostaje otwarta.
2. **Jak mierzyć lukę potoczną bez zewnętrznych list.**
   - Opcje: A) rozbieżność rang NKJP vs KWJP + lista ilustracyjna od właściciela (tylko ilustracja); B) A + kwalifikator „pot.” z SJP.pl jako miara raportowa (nigdy do progów); C) tylko lista ilustracyjna.
   - Domyślnie: A. B jest dozwolone (SJP.pl jako miara), ale kusi strojeniem.
3. **Przegląd próbek: kto i ile.**
   - Opcje: A) 30 słów na warstwę (granice POP/POP0 w środku i na zewnątrz, braki, rozbieżności), agent wstępnie ocenia, właściciel zatwierdza; B) właściciel ocenia wszystko sam; C) większe próbki.
   - Domyślnie: A (zgodnie z `sample_strata`, seed stały).

## Rekomendowany plan
1. **Pomiar (tylko odczyt).** `scripts/measure_pop.py` → `data/work/pop-measure-*/`:
   - pin bazy hashami; hash bazy przed i po bez zmian;
   - krzywe leksemy/formy vs pokrycie (D1), dla KWJP lemma, orth_lc, NKJP;
   - formy typowe (D2); zgodność rang KWJP–NKJP (D3);
   - warianty czyszczenia NKJP z listą kolizji (D4);
   - homonimy (D5); luka potoczna (D7); braki (D8);
   - próbki przy kandydatach na progi (D6), seed stały.
2. **Raport dla właściciela** po polsku, tabele, przykłady. Decyzje D1–D8 → ADR (odwracalne).
3. **Specyfikacja i implementacja**: `pop.py`, manifest POP, CLI, `explain`, testy (POP0 ⊆ POP ⊆ STANDARD, dwa buildy równe bajtowo, brak ≠ 0, baza bez zmian, homonimy bez kopiowania F, kolizje czyszczenia).
4. **Odbiór**: dwa identyczne buildy, przegląd próbek, progi zatwierdzone przez właściciela.
5. **Wydanie**: GitHub Release jak `llpl-v29`, z atrybucją NKJP, bez surowego NKJP.
6. **Wiki**: `Slownik-POP`, `Slownik-POP0`; zaznaczyć, że POP ⊆ LL-PL STANDARD, nie ⊆ SJP.

## Ryzyka
- **Złożoność:** średnia, w metodzie, nie w kodzie.
- **Integracja:** niska w repo; średnia w serwerze (inny słownik bazowy).
- **Regresja:** niska; LL-PL nie zmienia się. `code_identity` zmieni się przez nowy plik `.py` (dotyczy tylko przyszłej weryfikacji LL-PL).
