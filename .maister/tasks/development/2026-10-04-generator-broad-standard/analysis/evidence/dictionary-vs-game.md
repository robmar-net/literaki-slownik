# Wpis słownikowy i dopuszczalność do gry

## TL;DR
Wiążące doprecyzowanie użytkownika: słownik może zawierać słowo niedopuszczalne w grze.
Nie zmieniamy istniejących reguł gry; wycofujemy pytanie o zniesienie wyłączenia wielkich liter.
Baza/explain zachowują wpisy, a listy growe eksportują tylko dopuszczone formy.
SJP.pl zbadano jako wzorzec rozdzielenia informacji, bez pozyskiwania słów do generatora.

## Key Decisions
- Rozdzielamy obecność źródłową i kwalifikację językową od dopuszczalności growej, profilu oraz członkostwa w liście.
- Wspólne reguły gry obowiązują BROAD i STANDARD; zakres językowy obu wariantów pozostaje odrębny.
- Lower jest kluczem wyszukiwania/agregacji; nie zmienia normy pisowni źródłowej analizy.
- Zakaz zmiany reguł i konkretna korekta użytkownika rozstrzygają wcześniejszą bramkę, bez kolejnego A/B.

## Open Questions / Risks
- G3 nadal wymaga pełnej macierzy językowej, ortografii i konstrukcji. Utrzymanie reguł nie zwalnia z tych dowodów.
- Źródła niezależnego generatora i SJP mogą różnić się pokryciem; brak formy nie upoważnia do pobrania jej z SJP.
- Aktualnego internetowego ZDS nie przyjmujemy automatycznie jako aktualizacji norm gry. Wszelkie różnice wersji dokumentujemy, nie zmieniamy reguł.

## Obserwacja SJP.pl — wyraźnie zlecona przez użytkownika

[Strona PESEL](https://sjp.pl/PESEL) prezentuje wpis małoliterowy `pesel` jako dopuszczalny oraz wpisy `PESEL` jako niedopuszczalne. To odrębne zapisy/opracowania, nie zgoda na dowolną zamianę wielkich liter. [AGD](https://sjp.pl/AGD) istnieje w słowniku i ma oznaczenie niedopuszczalności. [ZDS](https://sjp.pl/sl/dp.phtml), punkt 1, wymienia wyłączenia m.in. obowiązkowych wielkich liter, skrótów, łączników i apostrofów. Z samego pospolitego charakteru leksemu nie wynika dopuszczalność growa.

Odczyt 2026-10-04 przez web.open; użyto opracowania hasła i oznaczeń serwisu, bez opinii z komentarzy. Strona PCR była niedostępna w tym narzędziu; nie opieramy na niej żadnego twierdzenia. Pozostałe trzy wymagane strony sprawdzono. To opis działania serwisu, nie lista treningowa, importer, oracle testowy ani benchmark. Przypadki generatora pochodzą z przypiętego SGJP i własnych fikstur.

## Zapisane zasady naszej gry

Odczytano lokalny klon wiki, rewizja `b024b73127e261c3c72020024b075d3d4ab34e57`:

- `Zasady.md`, sekcja „Sprawdzanie słów”, i `Rules.md`, „Checking words”: autowalidacja i kwestionowanie korzystają ze słownika gry. To nie jest ogólna baza wszystkich wpisów słownikowych.
- `Licenses.md`, sekcja polskiego słownika: gra używa growej listy SJP w opublikowanej postaci; dokumentuje osobno zasób i sposób użycia. Sekcja modyfikacji list odróżnia też obecność wyrazu i możliwość ułożenia go płytkami.
- Odczytano wcześniejszy dokument zasad z workspace, `analysis/research/literaki-rules.md` zadania product-design `2026-08-21-literaki-online-platform`, sekcję dotyczącą słownika i źródło ZDS. Dokument ma historyczny charakter; nie aktualizujemy nim dzisiejszych zasad.

Nie edytowano wiki, dokumentów aplikacji, list produkcyjnych ani silnika. Weryfikację źródeł dokumentacji zapisuje [game-rules-references.json](game-rules-references.json); publiczny artefakt nie kopiuje prywatnego kodu ani dokumentacji.

## Kontrakt generatora i explain

Dla każdej źródłowej analizy lub kompletnej rekonstrukcji wynik obejmuje oddzielnie:

1. **Obecność i język:** wpis istnieje/nie istnieje; interpretacja i decyzja wariantu z dowodami.
2. **Reguły gry:** accept/reject/unresolved z regułą i przyczyną; ocena oryginalnej, normatywnej pisowni. Zachowujemy wyłączenia growe.
3. **Profil:** alfabet, długość, znaki i możliwość ułożenia płytkami; osobne przyczyny.
4. **Lista:** członkostwo BROAD/STANDARD wymaga jednej spójnej analizy spełniającej wszystkie właściwe warunki. Niewiadome mogą blokować wydanie zgodnie z K5.

Baza nie usuwa wpisu przy growym reject. Explain wyszukuje przez NFC/lower wszystkie zapisy i analizy; nie odpowiada „brak słowa”, gdy istnieje niedopuszczalny wpis. Agregacja nie przenosi zgodności z językiem z jednego homonimu do growej pisowni innego.

## Przypadki odbioru G4/G6

| Analiza z przypiętego SGJP | Obecność/język | Reguły gry | Profil | Oczekiwany wynik |
|---|---|---|---|---|
| PCR / subst / nazwa_pospolita | zachowana analiza pospolita | obowiązkowe wielkie litery: reject | litery/2–15 mieszczą się | analiza nie dopuszcza pcr; explain pokazuje wpis |
| AGD / subst / nazwa_pospolita | zachowana | jak wyżej | mieści się | wpis pozostaje; analiza growa reject |
| PESEL / subst / nazwa_pospolita | zachowana | jak wyżej | mieści się | lower nie tworzy poświadczenia małoliterowego pesel |
| PCV / subst / nazwa_pospolita | zachowana | jak wyżej | v poza alfabetem: reject | obie przyczyny zachowane |
| DNA oraz niezależne dna/dno | wszystkie analizy zachowane | DNA reject nie przenosi się na zwykłe analizy | dna mieści się | dodatnia zwykła analiza może dopuścić klucz dna |
| AIDS i źródłowe aids | zapisy zachowane odrębnie | obowiązkowa wielka litera nie wyklucza niezależnego aids | aids mieści się | dopuszczenie wymaga własnej analizy aids |

Tabela wyznacza wymaganą separację i przypadki regresji; nie deklaruje ukończonego G4 ani pełnego przeglądu klas. Szczegóły w [SGJP probe](acronym-probe.json). SJP ma niezależne opracowanie `pesel`; nie wolno na tej podstawie dodać brakującego zapisu do naszego SGJP. Dalsze dopuszczone źródło może dostarczyć go jawnie w przyszłym zadaniu.
