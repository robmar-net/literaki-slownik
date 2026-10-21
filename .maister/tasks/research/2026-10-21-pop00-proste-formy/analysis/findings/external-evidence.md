# Co mierzą częstość i prostota

## TL;DR
Częstość formy jest użyteczną wskazówką, ale nie gotowym pomiarem znajomości.
Rejestr źródła ma znaczenie: tekst pisany nie zastępuje codziennej rozmowy.
Prosty język jako standard komunikacji obejmuje znacznie więcej niż listę słów.

## Key Decisions
- KWJP stosujemy jako źródło pomiaru form, a nie test wiedzy graczy.
- SUBTLEX-PL pozostaje tropem do osobnego audytu danych; nie importowano bazy.

## Open Questions / Risks
- Nie mamy ocen zwykłych graczy ani niezależnego testu proponowanych reguł.
- Nie potwierdzono warunków redystrybucji SUBTLEX-PL na potrzeby tego projektu.

## Źródła pierwotne — dostęp 2026-10-21
1. [Dokumentacja KWJP](https://kwjp.pl/lists/doc/about/): listy powstają automatycznie,
   mają próg publikacji co najmniej pięciu wystąpień w całym korpusie i mogą zawierać błędy.
   Dane rozdzielają zapis, lemat i gatunki. ARF oraz 1-DP pomagają ocenić rozproszenie użyć.
   Interpretacja dla POP00: brak wiersza to brak obserwacji w tej liście, a nie dowód nieznajomości.
2. Mandera i in. (2015), [SUBTLEX-PL](https://biblio.ugent.be/publication/5878584),
   DOI 10.3758/s13428-014-0489-4. Dwa eksperymenty rozpoznawania słów wskazały korzyść
   z łącznego użycia częstości napisowych i pisanych; korpus pisany zawyżał częstość formalnego słownictwa.
   To argument za porównaniem rejestrów, nie dowód, że napisy samodzielnie odtworzą gracza Literaki.
   Metadane mówią o dostępności do badań. Bez audytu warunków nie włączamy danych do dystrybuowanej listy.
3. [Jasnopis — prosty język](https://jasnopis.pl/prosty-jezyk/) opisuje standard tworzenia
   zrozumiałych komunikatów dopasowanych do odbiorcy. Wniosek dla projektu: potrzebujemy
   modelu znajomych słów i form; nie należy nazywać go pełnym wdrożeniem standardu prostego języka.

## Ograniczenia dostępu
Pełny PDF artykułu na stronie UGent oznaczono jako dostępny w UGent; wykorzystano metadane i abstrakt.
Adres bazy `https://crr.ugent.be/subtlex-pl/` zwrócił błąd narzędzia. Nie stwierdzamy braku bazy.
Błędny adres `kwjp.pl/info/lists` zastąpiono działającym oficjalnym `kwjp.pl/lists/doc/about/`.

## Zasoby wcześniej zablokowane
`docs/literaki-prosty-jezyk-minimum-leksykalne-kierunki.md` wskazuje listy Jasnopisu, Logios,
słowniki minimum i objaśnienia PSONI. Nie importowano ich ani nie użyto jako wzorca kalibracji.
Nie twierdzimy, że nie mają licencji: wcześniejsza decyzja mówi o nieustalonych warunkach konkretnego użycia.
Ich pełna analiza nie jest wymagana do sprawdzenia hipotezy POP0 + filtr form.
