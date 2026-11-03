# Brief: „wulwa” poza SGJP, KWJP i Słowosiecią

## TL;DR
Sprawdzamy, czemu rzeczownik „wulwa” (srom) jest w SJP.pl z pełną odmianą, a nie ma go w SGJP (eksport sgjp-20260823, jest tylko nazwisko „Wulw”), w lematach KWJP i jako lematu w Słowosieci 4.5, gdzie jest tylko „wulwodynia”. Na końcu rekomendacja: dodać do `sgjp-supplement.tab` czy nie.

## Open Questions / Risks
- Odpowiedź „dlaczego” może się opierać tylko na pośrednich dowodach: zasadach doboru haseł i frekwencji. Autorów źródeł nie pytamy.

## Pytanie
Luka w źródłach, celowe pominięcie (termin specjalistyczny, zapożyczenie, rejestr), pisownia (wulwa / vulva) czy niska frekwencja?

## Typ
Mieszany: dane lokalne (cache) i publiczne opisy źródeł.

## Zakres
- **W zakresie:**
  - `cache/sgjp` i `cache/sgjp-docs`, z zasadami doboru haseł SGJP;
  - `cache/kwjp`, `cache/nkjp`, `cache/plwordnet`;
  - `config/generator`, w tym `sgjp-supplement.tab`;
  - lexicony w `server/lexicons`;
  - publiczne opisy SGJP, NKJP, KWJP i Słowosieci;
  - słowniki ogólne, o ile da się ustalić, czy notują „wulwa”.
- **Poza zakresem:**
  - kontakt z autorami;
  - Wikisłownik (odroczony);
  - zmiany w listach.
- **Ograniczenia:**
  - dane surowe tylko do odczytu, Python uruchamiamy jako `python3 -I`;
  - w tekście nie wymieniamy gier słownych poza Literaki i Kurnik.

## Kryteria sukcesu
1. Frekwencja „wulwa”, „vulva” i „wulwodynia” w dostępnych korpusach, z liczbami i źródłem.
2. Czy SGJP ma podobne terminy anatomiczne (np. srom, łechtaczka, wagina, penis, moszna) i jak je traktuje.
3. Udokumentowane zasady doboru haseł SGJP, jeśli są dostępne.
4. Hipotezy z oceną pewności.
5. Rekomendacja dla `sgjp-supplement.tab` oraz list STANDARD i BROAD, zgodna z AGENTS.md: decyzję podejmuje użytkownik po zobaczeniu przykładów i wpływu.
