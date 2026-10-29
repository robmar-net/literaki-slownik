# ADR-010: Metoda `tematy-v1` i pilotaż „morze”

## TL;DR
TEMATY to listy słów jednego tematu, podzbiory STANDARD. Pilotaż ma jeden temat: `morze`.
Lista ma trzy rozłączne warstwy: T1 etykiety SGJP, T2 Słowosieć 4.5, T3 IATE 2019.
Od poprawki 2026-10-29 także D: ręczne dodatki z pliku tematu.
Wpis to leksem SGJP z formami ∩ STANDARD. Pakiet ma tylko stan BUILT; przegląd leży poza nim.
Bramka: automat podaje „dalej” albo „popraw”; „stop” wybiera tylko operator.
To słownik tematyczny. Jego reguły nie zmieniają dopuszczalności przy stole.
Źródła i pochodną Słowosieci opisuje [ADR-011](ADR-011-zrodla-slowosiec-iate.md).

## Kluczowe decyzje
- **Warstwy T1/T2/T3.** Wpis z kilku warstw dostaje najniższą (T1 < T2 < T3) i listę wszystkich źródeł.
- **Jednostka: leksem SGJP** z przebiegu v31 FROZEN. Formy przecinamy ze STANDARD. Lemat bez leksemu
  trafia do `BRAK_LEKSEMU`.
- **T2: pełne domknięcie** po relacjach 11, 25, 27 od 6 korzeni. Decyzja operatora z 2026-10-29,
  przed budową. W pliku tematu: `t2.tryb: "pelne"`.
- **Progi jako udziały**, z mianownikiem równym rzeczywistemu N ocen operatora w warstwie.
- **Przegląd R2: 30 słów na warstwę, razem 90.** Decyzja operatora z 2026-10-28.
- **Bez wykluczeń lematów i wykluczeń poddrzew.** Dodatki ręczne: od poprawki 2026-10-29 (niżej).
- **IATE 4821 zostaje.** Mierzymy udział żeglugi śródlądowej, nic nie wykluczamy.
- **Lista 37 słów oczywistych leży w pliku tematu**, nie w konfiguracji metody.

## Otwarte pytania / ryzyka
- **Szum pełnego domknięcia T2.** Domknięcie ma 1 092 synsety i 864 lematy jednowyrazowe,
  w tym `angora`, `bungee`, `chłodziwo`. Oceni to przegląd R2.
- **Mała T3.** Kod 4821 daje 78 kandydatów (74 różne terminy) przed mapowaniem na leksemy, odjęciem T1 i T2
  i ∩ STANDARD. Warstwa może mieć mniej niż 30 wpisów; wtedy oceniamy całą.
- **Progi pochodzą z pomiaru jednego oceniającego** w badaniu. Mogą wymagać korekty po pilotażu.
- **Temat przypisujemy lematowi przez jedno znaczenie.** Flaga `wieloznaczny` to zapisuje, ale nie usuwa.
- **Nowe wydanie POP, POP00 albo przebiegu zmienia liczby przecięć.** POP00 r2-a ma stan BUILT.

## Mapa numerów
Badanie numerowało decyzje lokalnie
([decision-log](../../.maister/tasks/development/2026-10-28-11-tematy-morze/analysis/research-context/decision-log.md)).
Lokalne numery nie są numerami tego repozytorium. Repozytoryjny ADR-008 to `pop-v3`, nie badanie.

| Badanie | Treść | Tu |
|---|---|---|
| ADR-001 | warstwy T1/T2/T3 | Warstwy |
| ADR-002 | E1 słaba, E2 zablokowana, E3 odroczona; zamiast nich SGJP, Słowosieć, IATE | Metody poza listą |
| ADR-003, 004 | Słowosieć 4.5, IATE 2019 | [ADR-011](ADR-011-zrodla-slowosiec-iate.md) |
| ADR-005 | temat = plik konfiguracji; przegląd R2 | Plik tematu, Przegląd |
| ADR-006 | leksem SGJP; formy ∩ STANDARD | Warstwy |
| ADR-007 | flaga `wieloznaczny` | Warstwy |
| ADR-008 | jeden pakiet TEMATY, jedna strona wiki | Pakiet (z odstępstwem) |
| ADR-009 | przecięcia z POP i POP00; diagnostyka BROAD i STANDARD | Raporty |
| ADR-010 | pilotaż „morze” i bramka | Bramka |

## Metody poza listą
Zadanie E wymienia trzy metody. Statusy: **E1 (n-gramy KWJP): słaba**, pilotaż dał głównie szum.
**E2 (korpus dziedzinowy): zablokowana**, brak korpusu spełniającego warunki.
**E3 (LLM): odroczona**, wymaga dwóch potwierdzeń kosztu. Zamiast nich: etykiety SGJP, drzewa Słowosieci i IATE.

## Warstwy
- **Jedno słowo:** lemat po NFC i zmianie na małe litery ma tylko litery a–z oraz ą ć ę ł ń ó ś ź ż.
  Spacja, łącznik, apostrof, kropka, cyfra: odrzucenie `NIE_JEDNO_SLOWO`.
- **Klasa leksemu:** zbiór klas tagów (pierwszy segment tagu) jego interpretacji SGJP.
- **T1:** interpretacja, której kwalifikatory po podziale `|`, potem `,` zawierają atom tematu jako cały atom.
  Morze: `mors.`, `żegl.`, `ryb.`.
- **T2:** lematy z pełnego domknięcia; lemat → leksemy z równym `lemma_base` i klasą z mapy części mowy
  ([ADR-011](ADR-011-zrodla-slowosiec-iate.md)).
- **T3:** terminy PL z IATE; lemat → leksemy klasy `subst` lub `depr`. IATE nie podaje części mowy.
- **Rzeczowniki odczasownikowe** (np. `żeglowanie`) nie mają własnego leksemu; trafiają do `BRAK_LEKSEMU`
  z osobną liczbą.
- **`wieloznaczny`:** `tak`, gdy lemat ma w Słowosieci jednostkę spoza domknięcia albo lemat z częścią mowy
  wskazuje kilka leksemów SGJP;
  `nie`, gdy wszystkie jego znaczenia leżą w temacie; `brak_danych`, gdy lematu nie ma w Słowosieci.
  Liczymy tylko jednostki z kodami części mowy 1–4.

## Plik tematu
`config/generator/tematy/morze.json` ma zamknięty schemat; nieznane pole to błąd.
- Korzenie T2: 7354 `statek 1`, 2149 `okręt 1`, 4511 `łódź 2`, 6214 `marynarz 1`, 14136 `żegluga 1`,
  14515 `żeglarstwo 1`. Nazwę sprawdza budowa ([ADR-011](ADR-011-zrodla-slowosiec-iate.md)).
- Relacja spoza {11, 25, 27} albo `t2.tryb` inny niż `pelne` to błąd w v1.
- Wersja tematu: `<id>-v<n>` (`morze-v2`). Metoda zostaje `tematy-v1`.
- Dodatek (`t3.dodatki`: `lemat`, `czesc_mowy` jako klasa tagu SGJP, `powód`) to warstwa D (poprawka niżej).
  Wykluczenia lematów muszą być puste; niepuste dają kod 2.
- Znaczniki śródlądowe ustalone przed pierwszą budową. PL: `śródląd`, `rzek`, `rzeczn`, `kanał`, `jezior`,
  `śluz`, `barka`. EN: `inland`, `river`, `canal`, `lake`, `lock`, `barge`. Nie zmieniamy ich po wynikach.
  Główna miara: hasła kandydatów T3; dodatkowo wpisy T3 po ∩ STANDARD.
- Lista 37 słów, bez zmian po wynikach: kotwica, kil, maszt, żagiel, ster, bosman, rufa, burta, pokład,
  statek, okręt, marynarz, jacht, sztorm, kambuz, bandera, reja, bom, fok, szalupa, kuter, rybak, mesa,
  kabestan, sternik, cumować, halsować, falochron, nabrzeże, kuk, bakburta, sterburta, grot, achtersztag,
  knaga, szkuta, trał. Leży w pliku tematu, bo następny temat ma własną listę, a metoda się nie zmienia.

## Raporty
- Przecięcie z POP i POP00: liczba i udział, razem i na warstwę, w leksemach (liczba główna) i formach.
  Leksem w POP = członek POP w `reports/units.json` pop-v3; leksem w POP00 = członek POP0.
- Diagnostyka przed ∩ STANDARD: kandydaci, ∩ BROAD, ∩ STANDARD. Odrzuceni z powodem i do 10 przykładów.
- Bez progu. Lista wydana zostaje ∩ STANDARD.

## Przegląd
- Agent ocenia próbę `min(50, N)` na warstwę (`tematy-quality-v1`). Operator ocenia pierwsze `min(30, N)`
  z niej w kolejności rangi. Klucze `sampling` są takie jak w `quality._config`; `operator_per_stratum`
  leży na górnym poziomie konfiguracji.
- Skala: tak / nie / niepewne. „niepewne” nie liczy się jako „tak” ani „nie”.
- Zgodność: odsetek identycznych ocen (3 kategorie) na pozycjach ocenionych przez obu. Kappa Cohena: te same
  pozycje, 3 kategorie.
- Hash ocen agenta trafia do pliku przeglądu przed wygenerowaniem strony operatora.
- Strona R2 to prywatny artefakt claude.ai, działa na iPhonie, ma przycisk „kopiuj JSON”.
  Przed przeglądem sprawdzamy ją na telefonie operatora.

## Bramka
Progi (porównanie dokładnych ułamków):

| Miara | Próg | W projekcie |
|---|---|---|
| test 37 słów, wynik całości T1 ∪ T2 ∪ T3 | ≥ 0,70 | 70% |
| T1: „tak” / N | ≥ 0,90 | 27/30 |
| T2: „tak” / N i „nie” / N | ≥ 2/3 i ≤ 0,10 | 20/30, najwyżej 3 błędne |
| T3: „tak” / N | ≥ 2/3 | 20/30 |
| zgodność agent–operator | ≥ 0,80 | 80% |

- Wynik T1 oraz T1 ∪ T2 w teście 37 słów to tylko diagnostyka.
- Checker podaje werdykt „dalej” albo „popraw” z listą progów. „stop” wybiera tylko operator.
- Dwie budowy a/b muszą mieć identyczne `SHA256SUMS`.

## Pakiet
Osobna podkomenda `tematy`, konfiguracja `config/generator/tematy.json` i pakiet w nowym katalogu, jak POP00
([ADR-009](ADR-009-pop00-v1.md)). Jeden pakiet TEMATY, plik na temat. Strona wiki `Slownik-TEMATY`
ma stan „W przygotowaniu” do bramki.

**Odstępstwo od lokalnego ADR-008 badania.** Badanie przewidziało stany BUILT i REVIEWED oraz przegląd
w pakiecie. v1 ma tylko stan BUILT. Przegląd żyje poza pakietem, w folderze zadania, i wiąże się
z `SHA256SUMS` pakietu oraz `sample_sha256`. Tak działa POP00. Ocena nie zmienia wtedy bajtów pakietu,
a budowy a/b dają się porównać.

## Poprawka 2026-10-29: dodatki ręczne (warstwa D)
Decyzja operatora po bramce v1 („popraw”): test 37 słów dał 31/37. Brakujące 6 słów dodajemy ręcznie:
`sztorm`, `rybak`, `falochron`, `nabrzeże`, `trał` (subst), `cumować` (inf). Temat `morze-v2`.
- Dodatek wskazuje dokładnie jeden leksem SGJP: równy `lemma_base` i klasa tagu `czesc_mowy`.
  Brak leksemu, kilka leksemów, brak formy w STANDARD albo leksem już w T1–T3: kod 4.
- Wpis D: `zrodla` = D, `znaczenie` = `D: <powód>`, formy ∩ STANDARD, `wieloznaczny` według zwykłych reguł.
- Raporty i przecięcia mają wiersz D; sumy go obejmują. Test 37 słów liczy wszystkie warstwy.
- Próba R2 losuje tylko T1–T3. Próba v2 jest bajtowo równa próbie v1, więc oceny v1 przepinamy na v2.
  Dodatki nie podlegają ocenie R2: wybrał je operator.

## Implementacja
- Każdy plik czytany w budowie, także wewnątrz POP i POP00, trafia do rejestru z hashem. Przed przeniesieniem
  pakietu budowa re-hashuje cały rejestr.
- Formy czytamy tylko dla leksemów kandydatów, porcjami po `lexeme_id`. Bez pełnego skanu dla BROAD.
- `pop._write_gzip` staje się `pop.write_gzip`, bez aliasu; test z `mock.patch.object` dostaje nową nazwę.
- Przykłady na wiki sprawdzamy w `MORZE.tsv.gz`. W v1 nie ma `explain --variant tematy`.
- Wiersz w tabeli źródeł na `Home`: Słowosieć i IATE.

## Zmiany po audycie
Audyt specyfikacji zgłosił 1 krytyczną, 9 ważnych i 16 drobnych uwag. Operator przyjął wszystkie.
Ten ADR zapisuje: W3 (`t2.tryb`), W5 (klasy T3, jedno słowo, `ger`), W6 (mała warstwa, udziały),
W7 (całość do progu), W8 (zgodność, kappa), D1 (`write_gzip`), D2 (`sampling`), D9 (tylko BUILT),
D10 (znaczniki śródlądowe), D11 (lista 37 słów), D12 (hash ocen agenta), D13 (wiki, `MORZE.tsv.gz`),
D14 (strona R2), D15 (formy kandydatów). Pozostałe zapisuje [ADR-011](ADR-011-zrodla-slowosiec-iate.md).
Specyfikacja: [spec.md](../../.maister/tasks/development/2026-10-28-11-tematy-morze/implementation/spec.md).

## Pochodzenie
Decyzje operatora:
[scope-clarifications.md](../../.maister/tasks/development/2026-10-28-11-tematy-morze/analysis/scope-clarifications.md).
Powiązane: [#11](https://github.com/robmar-net/literaki-slownik/issues/11), [ADR-009](ADR-009-pop00-v1.md),
[ADR-011](ADR-011-zrodla-slowosiec-iate.md).
