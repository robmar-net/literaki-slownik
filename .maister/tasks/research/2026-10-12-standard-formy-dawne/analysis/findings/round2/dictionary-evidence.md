# Kontrola znaczeń, odmiany i aktualności — runda 2

## TL;DR
Odczytano 40 celowo wybranych haseł SGJP, obejmujących 47 artykułów.
WSJP i konteksty potwierdzają zarówno żywe słowa z dawną etykietą, jak i rzeczywiście dawne warianty.
Pełny paradygmat w czytniku nie dowodzi używania wszystkich form, ale brak trafienia też nie dowodzi niepoprawności.
Nowsze źródła potwierdzają punktowo użycie po 2020; nie tworzą reprezentatywnego korpusu.

## Key Decisions
- Własne obserwacje służą researchowi. Nie importujemy tabel, definicji ani metadanych do generatora.
- Rozdzielamy leksem, znaczenie, wariant odmiany i formę zachowaną we frazeologizmie.
- Bieżący czytnik nie jest utożsamiany z eksportem SGJP 20260823.

## Open Questions / Risks
- Kwalifikatory źródeł mogą być sprzeczne. Nie ustalono historii redakcyjnej każdej etykiety.
- SGJP, WSJP i anotacja KWJP mają powiązania; zgodność nie oznacza trzech niezależnych ocen.
- Dobór słownikowy jest celowy, a nie losowy. Nie wyznacza odsetka błędnych odmów.

## SGJP: 40 haseł, 47 artykułów

[Pełny manifest](sgjp-review.json) zawiera każde hasło, identyfikatory artykułów, adresy zapytań, SHA256 odpowiedzi i własną obserwację. Dostęp: 2026-10-12. Skrypt [sgjp_review.py](../../sgjp_review.py) odtwarza manifest z lokalnych odpowiedzi.

W czytniku nadal są oznaczone: `desperacja`, `familia`, `industrialny`, `generyczny`, `dinozaur`, `sołtyska`, `preferować`, `wynegocjować` — przest.; `niezbędnik`, `wolontariacki` — daw. Zatem problem nie sprowadza się do błędu naszego parsera. Nie dowodzi to jednak, kiedy ani dlaczego etykiety nadano.

Przypadki rozstrzygające mechanizm:

| Przypadek | Obserwacja w SGJP | Znaczenie dla badania |
|---|---|---|
| [desperacja 27040](https://sgjp.pl/edycja/ajax/inflection-tables/?lexeme_id=27040&variant=0) | przest. w nagłówku; desperacyj osobno char. arch. | Wiek leksemu i wiek wariantu mają różne poziomy |
| [dokument 3202](https://sgjp.pl/edycja/ajax/inflection-tables/?lexeme_id=3202&variant=0) | dokumenta: daw. przy formie | Popularność dokument nie uzasadnia dokumenta |
| [zasłonić 271105](https://sgjp.pl/edycja/ajax/inflection-tables/?lexeme_id=271105&variant=0) | zasłoniono/zasłonienie/zasłonieni: przest. | Zachowanie blokady samego arch. jest niewystarczające |
| [wywrzeć 268872](https://sgjp.pl/edycja/ajax/inflection-tables/?lexeme_id=268872&variant=0), [268873](https://sgjp.pl/edycja/ajax/inflection-tables/?lexeme_id=268873&variant=0) | Wygotowanie: wywre/wywrzał; wpływ: wywrze/wywarł | Ta sama lemma i część mowy mogą oznaczać inne czasowniki |
| [kursor 39051](https://sgjp.pl/edycja/ajax/inflection-tables/?lexeme_id=39051&variant=0), [66898](https://sgjp.pl/edycja/ajax/inflection-tables/?lexeme_id=66898&variant=0) | Posłaniec m1 i wskaźnik ekranowy m3 | Kursorzy nie jest odmianą wskaźnika |
| [metr 66941](https://sgjp.pl/edycja/ajax/inflection-tables/?lexeme_id=66941&variant=0) | Nauczyciel, m1, metrowie | Popularność jednostki długości nie dowodzi tej osoby |
| [rozpuk 54175](https://sgjp.pl/edycja/ajax/inflection-tables/?lexeme_id=54175&variant=0) | Dzisiejsze użycie w do rozpuku, mimo pełnej tabeli | Frazeologizm nie dowodzi rozpukowi |
| [umór 61110](https://sgjp.pl/edycja/ajax/inflection-tables/?lexeme_id=61110&variant=0) | Na umór, mimo pełnej tabeli | Poprawny przykład to na umór; brak podstaw do umorach |
| [ukradek 61025](https://sgjp.pl/edycja/ajax/inflection-tables/?lexeme_id=61025&variant=0), [bakier 73621](https://sgjp.pl/edycja/ajax/inflection-tables/?lexeme_id=73621&variant=0) | Ograniczenia do ukradkiem/z ukradka oraz na bakier | Nota o użyciu jest istotna obok samej odmiany |

[Kod eksportera Kuźni](https://git.nlp.ipipan.waw.pl/SGJP/Kuznia/blob/61daf78fb2378b1f33e707a364c7d912f8edd255/export/lexeme_export.py), wiersze 206–235, łączy kwalifikatory leksemu, odmiany i zakończenia w jedno pole. Wariant zagnieżdżony uwzględnia też rodzica. Z tego pola nie odtworzymy automatycznie źródłowego poziomu każdej etykiety. SHA256 odczytanego pliku: `258d7364ccb443ade53cb2a9db9a72a5d6cf33866ba944123f799937da05e79e`. Dowód formatu, bez twierdzenia, że ten commit zbudował nasz eksport. Zob. też istniejące [etykiety projektu](../../../../../../../docs/generator/etykiety.md).

## WSJP: kontrola znaczeń i kontrprzykładów

Dostęp do poniższych stron: 2026-10-12. To 24 wiersze kontrolne, część z kilkoma znaczeniami/hasłami. Kontrole rundy 1 pozostają w [external-evidence.md](../external-evidence.md).

| Hasło i źródło | Własna obserwacja |
|---|---|
| [sołtyska: pani sołtys](https://wsjp.pl/haslo/podglad/120846/soltyska/5278353/pani-soltys), [żona sołtysa](https://wsjp.pl/haslo/podglad/120846/soltyska/5278354/zona-soltysa) | Pierwsze bez dawności, drugie przest.; nie wolno odrzucić nowego znaczenia przez stare |
| [wolontariacki](https://wsjp.pl/haslo/podglad/120083/wolontariacki) | Bez dawności; przykłady NKJP i KWJP, więc częściowo te same zasoby dowodowe |
| [generyczny: nazwa](https://wsjp.pl/haslo/podglad/80827/generyczny/5217598/nazwa), [przemysł](https://wsjp.pl/haslo/podglad/80827/generyczny/5217646/przemysl) | Współczesne znaczenia ogólne i farmaceutyczne |
| [industrialny: pejzaż](https://wsjp.pl/haslo/podglad/616/industrialny/5168134/pejzaz), [zespół](https://wsjp.pl/haslo/podglad/616/industrialny/5168148/zespol) | Pierwsze książkowe, drugie muzyczne; książkowość nie jest oznaczeniem dawności |
| [dinozaur: zwierzę](https://wsjp.pl/haslo/podglad/31984/dinozaur/3919032/zwierze), [rzecz](https://wsjp.pl/haslo/podglad/31984/dinozaur/3919035/rzecz) | Nazwa zwierzęcia i współczesna metafora, bez etykiety dawności |
| [powijak](https://wsjp.pl/haslo/podglad/87549/powijak), [powijaki](https://wsjp.pl/haslo/podglad/87564/powijaki) | Przedmiot w lp. osobno od figuratywnego początku w lm.; brak trafienia KWJP dla powijak nie kończy oceny |
| [szuwar](https://wsjp.pl/haslo/podglad/72148/szuwar) | Zwykle lm., ale podana lp. i przykład użycia szuwarem |
| [sztaluga](https://wsjp.pl/haslo/podglad/72132/sztaluga), [sztalugi](https://wsjp.pl/haslo/podglad/87502/sztalugi) | Współistnienie lp. i wariantu lm.; nie wolno mechanicznie zakazać lp. |
| [mokradło](https://wsjp.pl/index.php/haslo/podglad/2055/mokradlo) | Zwykle lm. nie oznacza wyłącznie lm.; lp. potwierdzona także w naszych kontekstach |
| [zarośla](https://wsjp.pl/haslo/podglad/11999/zarosla) | Współczesna odmiana tylko w lm.; zarośle pojawia się w etymologii |
| [manowce](https://wsjp.pl/haslo/podglad/85075/manowce) | Opis w lm.; dawnego manowiec nie przyjmujemy na podstawie samej etymologii |
| [cugle](https://wsjp.pl/haslo/podglad/40807/cugle/5153681/konia) | Współczesny opis mnogi; nie dowodzi lp. cugiel |
| [deszcz](https://wsjp.pl/haslo/podglad/11500/deszcz/1079561/duza-ilosc-czegos), [kania dżdżu](https://wsjp.pl/haslo/podglad/11519/ktos-potrzebuje-czegos-jakniczym-kania-dzdzu/4763262) | Zwykła odmiana deszczu obok zachowanej frazeologii; nie jeden pełny wspólny paradygmat |
| [na umór](https://wsjp.pl/haslo/podglad/90324/na-umor/5225373/pic) | Żywy frazeologizm; poprawka przykładu z rundy 1 |
| [książę](https://wsjp.pl/haslo/podglad/26232/ksiaze/4244925/z-bajki) | Współczesne księcia nie dowodzi archaicznych wariantów odmiany |
| [metr: nauczyciel](https://wsjp.pl/haslo/podglad/3440/metr/5165378/nauczyciel) | Opis historycznej profesji; sama dawność desygnatu to osobny problem od dawnej formy języka |
| [kursor](https://wsjp.pl/haslo/podglad/36555/kursor) | Współczesny wskaźnik komputerowy; dawne znaczenia w historii hasła nie dowodzą kursorzy |
| [przytulisko: dla znajomych](https://wsjp.pl/haslo/podglad/72539/przytulisko/5220510/dla-znajomych), [dla zwierząt](https://wsjp.pl/haslo/podglad/72539/przytulisko/5220411/dla-zwierzat) | Żywe znaczenia, mimo braku konkretnego przytuliskom w sondzie KWJP |
| [marnotrawny: system](https://wsjp.pl/haslo/podglad/85292/marnotrawny/5212512/system), [syn](https://wsjp.pl/haslo/podglad/85292/marnotrawny/5212523/syn) | Nie ogranicza się do dosłownego cytowania przypowieści |
| [wywrzeć wpływ](https://wsjp.pl/haslo/podglad/35072/wywrzec/3936730/wplyw) | Współczesny czasownik; nie dowodzi wygotowania się z innego leksemu SGJP |
| [atencja](https://wsjp.pl/haslo/podglad/50012/atencja/5149691/publicznosci) | Książkowe znaczenie; atencyj oznaczone char., bez arch. — jawna różnica wobec SGJP |
| [konfuzja](https://wsjp.pl/haslo/podglad/77145/konfuzja) | Książkowość, a konfuzyj jako char.; nie utożsamiać char. z dawnością |
| [kajet](https://wsjp.pl/haslo/podglad/55419/kajet) | Przest. mimo obecności w tekstach współczesnych |
| [sierociniec](https://wsjp.pl/haslo/podglad/56350/sierociniec) | Przest. mimo przykładów prasowych; samo wystąpienie nie anuluje oceny rejestru |

Nie znaleziono bezpośrednich haseł WSJP dla `przechwałka` i `rozpuk` w wykonanych wyszukiwaniach. To ograniczenie wyniku wyszukiwania, nie twierdzenie o nieistnieniu haseł; wykorzystano SGJP i konteksty. Wyszukiwanie `aliści/jakoż/trzykroć/nazad` dawało też przykłady wewnątrz innych haseł; nie potraktowano ich jako kwalifikatorów tych wyrazów.

## Zasady redakcyjne i zależność źródeł

[Zasady WSJP, wydanie dziewiąte, luty 2026](https://pliki.wsjp.pl/zasady_opracowania_wsjp.pdf), §2.7 i §2.11: kwalifikator dawności dotyczy języka, a nie wieku opisywanego przedmiotu. Książkowość jest osobną osią. Opis fleksji korzysta z SGJP i dopuszcza regularne formy potencjalne, niepoświadczone osobno w tekstach. Dlatego tabela WSJP nie jest niezależnym drugim pomiarem częstości każdej formy. Definicje i rozdział znaczeń dostarczają innego rodzaju kontroli. Dokument ma na okładce 2026, choć zdanie wstępne mówi o stanie na luty 2025; zapisujemy obie informacje.

## Dowody po 2020

| Źródło, data | Obserwacja i granica |
|---|---|
| [ARiMR, Polska wieś w oczach kobiet, 15.10.2025](https://www.gov.pl/web/arimr/polska-wies-w-oczach-kobiet) | Sołtyska użyta w treści o kobiecie pełniącej urząd, nie tylko w tytule konkursu |
| [Senat, komisja gospodarki, 2024](https://www.senat.gov.pl/prace/komisje-senackie/przebieg,10618,1.html) | Wolontariacki w zapisie wypowiedzi o współczesnym programie. Punktowy przykład mowy publicznej, nie reprezentacja polszczyzny mówionej |
| [Repozytorium UJ, praca magisterska, obrona 12.07.2024](https://ruj.uj.edu.pl/entities/publication/1f2a11fc-e0a0-45b4-ae5e-f8f34dea9b7d) | Generyczny w polskich słowach kluczowych; świadectwo użycia fachowego, nie dowód rozpowszechnienia |
| [IPN, prace w Drzewicy, 1–3.09.2025](https://poszukiwania.ipn.gov.pl/bbp/aktualnosci/kalendarium-prac/rok-2025/24918,1-3-wrzesnia-2025-r-Drzewica.html) | Niezbędnikiem jako nazwa znalezionego wyposażenia; dzisiejszy język opisujący dawny przedmiot |

To celowe kontrprzykłady dla tezy o braku współczesnego użycia, bez szacowania częstości. Sejm chwilowo zwracał błąd narzędzia; stronę Służby Więziennej o programie wolontariackim znaleziono w indeksie, ale pełny odczyt zwrócił 403. Nie opieramy wniosków na tych dwóch niedostępnych stronach. Alternatywne źródło senackie odczytano w całości. IPN po błędzie web odczytano przez publiczny HTML; surowa odpowiedź pozostaje lokalna.

## Korekty uproszczeń z pierwszej rundy

- Książkowość, rzadkość i regionalność same w sobie już nie wykluczają w obecnej polityce. Nie wymagają ponownej ogólnej zgody; problemem jest współistniejąca etykieta dawności oraz jej zakres.
- `przechwałka`, `sztaluga`, `szuwar`, `mokradło` nie mogą trafić do jednego worka z automatycznie podejrzaną liczbą pojedynczą. Są konkretne pozytywne dowody; `manowiec/cugiel/zarośle` wymagają odmiennej oceny.
- `aliści`, `jakoż`, `nazad`, `trzykroć` mają też współczesne autorskie użycia nacechowane. Uczciwy opis to problem granicy rejestru i dawności, nie twierdzenie, że każdy ich kontekst jest dawnym cytatem.
- Poprawny przykład ograniczonej frazeologii: **na umór**, nie wcześniejsze do umoru. Stare artefakty pozostają historią; korekta jest jawna.
