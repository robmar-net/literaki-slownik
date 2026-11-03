# Świadoma zmiana 05: jak włączyć kategorię do procesu z #16

## TL;DR
- „Zmiana świadoma” to **typ kandydata, a nie nowa warstwa korpusowa**. Nie ma źródła z czystą licencją, które dawałoby takie słowa z liczbami. Dowodem jest redagowany słownik (DS, ręcznie), wolny tezaurus DS (lokalnie) i korpus (kategorie 1–2).
- Proponuję w karcie kandydata **osobną sekcję „zmiana świadoma”**: podklasa (a/b/c), dowód słownikowy (DS, link + data), reguła (RJP), sygnał społeczny (kampania, przepis) i liczby z korpusów.
- Próg proponuję zróżnicować:
  - (a) feminatyw systemowy: reguła RJP + DS lub tezaurus DS + co najmniej 1 korpus z użyciem;
  - (b) świadoma zmiana: DS + co najmniej 1 korpus z użyciem po filtrze szumu;
  - (c) formy normatywne bez użycia: nie dodajemy.
- Kolejka startowa: 8 słów z podklasy (b) i (a) z pliku 04 oraz część wspólna DS ∩ zaimki.pl (122 feminatywy) do przeglądu w częściach.

## Kluczowe decyzje (do zatwierdzenia przez użytkownika)
- **S1. Typ kandydata, nie warstwa.** Pole karty `typ: zmiana_świadoma`, a w nim `podklasa: feminatyw_systemowy | świadoma_zmiana | normatywna`. Wejście do list idzie jak dotąd przez suplement v2 słowo po słowie (D1-A).
- **S2. Dowody i ich status:**

| dowód | status | co trafia do repo |
|---|---|---|
| hasło DS | tylko dowód ręczny | URL, data odczytu, id hasła |
| tezaurus DS (GPL/LGPL) | ALLOWED, sygnał lokalny | „jest w tezaurusie DS 2026-10-01”, SHA256 pliku |
| RJP 2019 i 2026 | tylko dowód ręczny, reguła | URL stanowiska przy klasie, nie przy słowie |
| zaimki.pl | do decyzji (OQL) | nic, dopóki nie zapadnie decyzja |
| publikacje, plebiscyty | tylko dowód ręczny lub sygnał | DOI lub rok |
| korpusy (kat. 1–2) | wg ich ocen | liczby roczne |

- **S3. Hurt czy słowo po słowie dla podklasy (a).**
  - Wariant A: słowo po słowie, z kontrolą korpusu, zgodnie z D1-A.
  - Wariant B: przyjąć wzór `-log → -lożka` (i podobne) hurtem dla nazw zawodów obecnych w SGJP, z regułą RJP jako uzasadnieniem.
  - Rekomendacja: **A**. SGJP sam dodaje feminatywy pojedynczo (muralistka w 20261018), a wzór daje słowa bez użycia (angelolożka).
- **S4. Formy, nie tylko lematy.** Karta pokazuje formy nowe dla gry, bo dla „ministra” 6 z 10 form już jest w SGJP jako formy „minister”.

## Otwarte pytania i ryzyka
- Kryteria dopuszczalności (Kurnik + ZDS): czy podklasa (b) w ogóle mieści się w zasadach gry? To decyzja użytkownika. Wulwa jako zwykły rzeczownik pospolity raczej tak.
- Bez liczb z kategorii `ccrawl` i `potoczne` progu „≥ 1 korpus” nie da się dziś skalibrować. Placeholder: w FineWeb-2 i HPLT policzyć wulwę, transpłciowy, tranzycję, chirurżkę i kardiolożkę z kontrolą dodatnią (psycholożka).
- Ryzyko SJP.pl w DS jest niskie (zob. 01). Jeśli użytkownik je odrzuci, zostaje tylko korpus.
- Słowa z (b) budzą spory. Karta opisuje tylko użycie i normę, bez oceny postaw.

## Przebieg dla wulwy (przykład)
1. Kandydat z kolejki ręcznej (zgłoszenie użytkownika), `typ: zmiana_świadoma / świadoma_zmiana`.
2. Dowód słownikowy: DS https://dobryslownik.pl/slowo/wulwa/226245/ (odczyt 2026-11-03; dodane I–II 2024) i tezaurus DS 2026-10-01.
3. Sygnał społeczny: kampanie od 2022 (Wysokie Obcasy), edukacja seksualna; 1% deklarowanego użycia (2022).
4. Korpusy: liczby z FineWeb-2 i HPLT (kat. 2) z latami. **Wymagane, zanim karta przejdzie dalej.**
5. Wzór fleksji: wzór leksemu SGJP dla rzeczownika żeńskiego na `-wa` (np. „mewa”), wybierany w karcie. 10 form jak w DS, dopełniacz l.mn. „wulw”.
6. Decyzja użytkownika, potem suplement v2.

## Inne słowa tej kategorii (z 04)
- (b) z DS, bez SGJP: transpłciowy, transpłciowość, tranzycja, transfobia, ciałopozytywność.
- (a) z DS, bez SGJP: chirurżka, kardiolożka, ministra (tylko nowe formy), wiceministerka, ziomalka.
- (a) bez DS: premierka, sędzini. Potrzebny korpus.
- (c) odpadają: onu, jenu, zrobiłum, byłum, osobatywy typu „osoba studencka” (RJP: „jeszcze nie … standard”).
