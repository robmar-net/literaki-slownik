# metoda: warstwa „potoczne / internet” w procesie z #16

## TL;DR
- Nowa warstwa to **osobny strumień wykrywania** obok PPC/ParlaMint/Leipzig. Działa tak samo poza buildem: liczby trafiają tylko do karty, do list wchodzi się decyzją użytkownika przez suplement v2 (D1-A, ADR-016).
- W sieci szum to nie składnik korpusu (jak w PPC), tylko **język i nazwy**: angielskie ciągi, marki, nazwy własne, zapis z myślnikiem lub apostrofem. Dlatego bramki są inne niż w #16: **polska odmiana albo polski kontekst, mała litera w środku zdania, rozrzut po hostach**. Wzrost g jest tylko liczbą w karcie, nie progiem.
- Jednostka to **leksem z paradygmatem według wzoru SGJP**, nie grupa form z ucinania końcówek. Liczymy wszystkie formy wzoru. Dzięki temu „polska odmiana” jest mierzalna.
- Progi liczbowe są szkicem. Kalibracja czeka na liczby z kategorii ccrawl i potoczne: [do uzupełnienia z ccrawl/potoczne].

## Kluczowe decyzje
- **Bez progu nowości.** Słowa potoczne to często stare luki (bumer, ziom), nie słowa po 2020. Kryterium „nowe” (g ≥ 5) z ADR-015 tu nie odcina. Pokazujemy g i pierwszy rok, jeśli źródło ma daty.
- **Bramka polskości** zastępuje filtr „angielskie bez polskiej odmiany” z #16, który tu wyciąłby cel (cringe, selfie są nieodmienne).
- **SJP.pl i słowniki-agregatory nie liczą się jako użycie.** Hosty `sjp.pl` i kopie, strony typu „znaczenie słowa” oraz sam słownik świadomej zmiany wyłączamy z liczenia. Ich udział podajemy w karcie.
- **Z sieci nie cytujemy przykładów** w repo, dopóki ccrawl nie ustali, co wolno opublikować (TDM). Do karty idą tylko liczby. Przykłady zdań dalej pochodzą z korpusów z #16 albo z dowodu ręcznego (link + data odczytu).

## Otwarte pytania i ryzyka
- Czy zbiory sieciowe w ogóle wolno liczyć i publikować z nich liczby: [do uzupełnienia z ccrawl].
- Daty w zbiorach sieciowych to zwykle data zrzutu, nie publikacji. Podział na lata będzie przybliżony.
- Nazwy marek pisane małą literą (zoom, tiktok) przejdą bramkę litery. Potrzebna flaga „marka” z ręczną listą i decyzja użytkownika.
- Progi oparte na ocenie agenta mają tę samą słabość co ADR-017: bez konkordancji. Pierwsza część kart to zweryfikuje.

---

## 1. Miejsce w procesie z #16

```
korpusy #16 (PPC, ParlaMint, Leipzig) ─┐
NKJP → KWJP (374)                      ├─► kolejka ─► karty ─► decyzja ─► suplement vN
NOWE: potoczne/internet (sieć, napisy…) ┤
NOWE: zmiana świadoma (dowód ręczny)   ─┘
```

- Kwartał (ADR-018) zostaje. Zbiory sieciowe zmieniają się rzadko (nowy zrzut raz na kilka miesięcy). Przeliczamy je tylko przy nowej wersji, jak Leipzig.
- Manifest wykrywania (ADR-015) dostaje wpisy dla każdego zbioru: url, wersja, sha256, `retrieved_at`, licencja tekstu i licencja opakowania osobno, zakres „tylko liczenie lokalne” albo „liczby do publikacji”.
- Rejestr decyzji wspólny. Słowo odrzucone w jednej warstwie nie wraca z drugiej bez nowego dowodu (reguła powrotu z ADR-018).

## 2. Bramki (każda zapisana w karcie jako tak/nie z liczbą)

| # | Bramka | Co mierzy | Szkic progu | Co odsiewa |
|---|---|---|---|---|
| B1 | alfabet gry | wszystkie litery lematu w `ALPHABET` z `policy.py` | twardo | `vlog`, `quiz`, `e-mail`, `cringe'owy` |
| B2 | brak w SGJP i suplemencie | lemat i każda forma wzoru | twardo; formy już w SGJP liczymy osobno | `hejt`, `lockdown`, `spoiler` |
| B3 | mała litera | udział małej litery **poza początkiem zdania** | ≥ 90% | marki i nazwy: `Zoom`, `TikTok`, `Netflix` |
| B4 | dokument polski | trafienie w dokumencie z przewagą polskich słów funkcyjnych nad angielskimi | trafienia w dokumentach angielskich wyrzucamy; zostać musi ≥ 50% surowych | `cringe`, `ghosting` w tekście angielskim |
| B5a | polska odmiana (wyrazy odmienne) | udział tokenów w formach innych niż podstawowa | ≥ 10% i ≥ 2 różne formy nie-podstawowe | angielskie ciągi: `adults`, `followers` |
| B5b | polski kontekst (nieodmienne) | w oknie ±3 słowa jest polskie słowo funkcyjne | ≥ 80% trafień | wtrącenia angielskie, tytuły piosenek |
| B6 | rozrzut | liczba hostów i udział największego | ≥ 10 hostów, największy ≤ 25% | jedna strona, spam, kopie |
| B7 | częstość | ipm po bramkach B3–B6 | [do uzupełnienia z ccrawl/potoczne]; szkic ≥ 0,05 ipm i ≥ 20 trafień | rzadkie jednorazówki |
| B8 | host wykluczony | udział `sjp.pl`, kopii, stron „znaczenie słowa”, słownika świadomej zmiany | tylko raport; nie liczy się do B6–B7 | definicje zamiast użyć |

Uwagi:
- B5a/B5b wybiera wzór fleksji (§ 3 w `metoda-04-zapozyczenia-gra.md`). Wzór nieodmienny (selfie, cool) → B5b. Odmienny → B5a.
- Próg B5a 10% to szkic. Dla rzeczownika m3 forma podstawowa (mianownik i biernik) to zwykle ok. 40–60% tokenów. W KWJP `lockdown` ma 115 z 244 (47%) w formie podstawowej, `hejt` 144 z 361 (40%). Słowo z 0–5% form odmienionych to prawie na pewno wtrącenie.
- Bramki B3–B6 liczymy na tych samych trafieniach, w tej kolejności. Karta pokazuje lejek: surowe → po B3 → po B4 → po B6.

## 3. Flagi (nie tną, ustawiają kolejność)

| Flaga | Kiedy | Skutek |
|---|---|---|
| `angielski-wygląd` | litery typowe dla angielskiego (`oo`, `ee`, `sh`, `th`, `ck`, `gh`, końcowe nieme `e`) | tylko informacja; SGJP ma wiele takich słów (zob. metoda-04) |
| `marka` | lemat z ręcznej listy marek/serwisów albo > 50% użyć wielką literą w całym zbiorze | warstwa odłożona; przymiotnik `-owy` od marki nie dostaje flagi (SGJP ma `facebookowy`, `instagramowy`, `tiktokowy`) |
| `wariant-pisowni` | jest para oryginał/spolszczenie (boomer/bumer, cringe/krindż) | karta wspólna dla rodziny pisowni, decyzja osobno dla każdej pisowni |
| `homograf-SGJP` | forma kandydata już jest w SGJP jako inny leksem (`bumer` m3) | karta pokazuje tylko formy nowe w grze |
| `zapis-niegrywalny` | warianty z myślnikiem, apostrofem, q/v/x | liczone jako dowód leksemu, ale nie wchodzą na listę |
| `wulg.` / `obraźliwe` | ręcznie | tylko informacja; `pot.` i `wulg.` nie wykluczają (`usage_checks` w `policy.py`) |

## 4. Kolejka w tej warstwie (analogia do ADR-017)

| Podwarstwa | Warunek | Przegląd |
|---|---|---|
| P1: potwierdzone | B1–B7 + ≥ 1 użycie w korpusie z #16 albo w drugim zbiorze nieformalnym | pełna karta, po grupach ≥ 2 korpusów |
| P2: tylko sieć, mocne | B1–B7, bez flagi `marka` | pełna karta |
| P3: lista skrócona | B1–B6, B7 niespełnione albo tylko jeden zbiór | lista lematów z liczbami, karta tylko dla zaznaczonych |
| P4: odłożone | flaga `marka` albo B4/B5 na granicy | tylko raport kwartału |

Trafność podwarstw: [do uzupełnienia z ccrawl/potoczne] — ocena 50 losowych z P2 i P3, jak w ADR-017.

## 5. Wzrost i daty
- Jeśli zbiór ma daty (rok zrzutu, data dokumentu), liczymy g jak w #16 (+0,5, normalizacja medianą słów SGJP) i pierwszy rok z ≥ 5 trafieniami.
- g jest w karcie i w kolejności wewnątrz podwarstwy. Nie jest bramką.
- Kontrola hejt/hejter z #16 (mają odpaść na g) tu nie działa: w tej warstwie odpadają na B2, bo są w SGJP. Kontrolę „starego słowa” robimy na słowach z SGJP (metoda-05).
