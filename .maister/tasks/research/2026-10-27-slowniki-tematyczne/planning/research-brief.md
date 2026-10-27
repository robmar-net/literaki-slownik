# Brief: słowniki tematyczne

## TL;DR
Sprawdzamy, czy da się zbudować słowniki tematyczne (np. marynistyczny, rolniczy, matematyczny).
Najpierw szukamy danych, które już mamy (SGJP, KWJP, NKJP, Morfeusz) i w zasobach PAN.
Jeśli ich nie ma, mówimy to wprost; szersze źródła to osobny krok, za zgodą użytkownika.

## Key Decisions
- Zakres: dane lokalne projektu i zasoby PAN (IPI PAN). Źródła spoza PAN tylko notujemy, gdy wyjdą przy okazji.
- Nie kontaktujemy autorów zasobów (AGENTS.md). Wikisłownik pozostaje odroczony decyzją użytkownika.

## Pytanie
Czy w danych projektu albo w zasobach PAN jest informacja o dziedzinie słowa, która pozwala zawęzić listę słów do tematu?

## Typ badania
Mieszane: technika (dane i kod projektu) + literatura (dokumentacja zasobów PAN).

## Zakres
- W zakresie:
  - SGJP (eksport tab, kwalifikatory, etykiety; `docs/generator/etykiety.md`);
  - Morfeusz (tagi, kwalifikatory);
  - KWJP100 (13 list i n-gramy);
  - NKJP (unigramy, metadane podkorpusów i gatunków tekstu);
  - inne zasoby IPI PAN: WSJP (kwalifikatory dziedzinowe), korpusy z metadanymi dziedziny, listy terminologiczne.
- Poza zakresem: wdrożenie, zmiana reguł gry, kontakt z autorami, pobieranie dużych danych bez potrzeby.
- Ograniczenia: warunki licencji muszą być znane (jak w audycie). Dane surowe poza Git.

## Kryteria sukcesu
1. Dla każdego źródła: czy ma informację o dziedzinie, jaką, ile słów ma etykietę, jaka licencja.
2. Dla 3 przykładowych tematów (marynistyka, rolnictwo, matematyka): ile słów da się wskazać i z jaką pewnością, na próbce przykładów.
3. Jasna odpowiedź: „mamy dane” albo „nie mamy, trzeba szerzej” — z listą kandydatów do szerszego szukania.
