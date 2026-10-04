# Decyzja G3: pospolite skrótowce zapisywane wielkimi literami

## TL;DR
Bramka A/B wycofana po doprecyzowaniu użytkownika: reguł gry nie zmieniamy.
Poniższe opcje zachowano jako historię wcześniejszego, błędnie sformułowanego pytania.
Wpis słownikowy i dopuszczalność growa są odrębnymi wynikami.

## Key Decisions
- Wiążące doprecyzowanie: [dictionary-vs-game.md](dictionary-vs-game.md).
- Obowiązkowa wielka litera nie staje się dopuszczalna przez lower.

## Open Questions / Risks
- Pozostałe discovery G3 nadal wymagane; wycofanie bramki nie kończy grupy.

Status: superseded. Nie oczekuje na odpowiedź A/B; opcje poniżej nie obowiązują.

## Dowody

Źródło pierwotne: [Podstawy teoretyczne SGJP, wydanie czwarte](https://sgjp.pl/static/pdf/Podstawy_teoretyczne_SGJP.pdf), wersja 2021.01.11, §§1.3.4 i 3.3.4, strony drukowane 14–15 i 47–49. Lokalny dokument `cache/constructions/sgjp-theory.pdf`, SHA256 `3e3d104b1a210e0097c511b36f1440de539413ec64079fba505c47c3bf7684ca`; używany jako dokumentacja, nie importer haseł. SGJP odróżnia skrótowce od skrótów i opisuje pospolite skrótowce pisane wielkimi literami. Wielka litera sama nie określa klasy językowej.

Przykłady pochodzą z przypiętego SGJP, pełnego importu, nie z internetowej listy słów. Wszystkie poniższe zapisy mają interpretacje `subst` / `nazwa_pospolita`; szczegóły w [acronym-probe.json](acronym-probe.json).

| Zapis SGJP | Klucz gry | Wariant A | Wariant B |
|---|---|---|---|
| PCR | pcr | dopuszczona analiza pospolitego skrótowca | odrzucona analiza zapisu obowiązkowo wielkimi literami |
| PESEL | pesel | jak wyżej | jak wyżej |
| AGD | agd | jak wyżej | jak wyżej |
| RNA | rna | jak wyżej | jak wyżej |
| PCV | pcv | odrzucony profil alfabetu (v) | odrzucony profil alfabetu (v) |
| AIDS / aids | aids | istnieje też małoliterowa analiza | małoliterowa analiza pozostaje |
| DNA / dna | dna | analiza DNA oraz niezależne zwykłe leksemy | pozostają niezależne analizy dna i dno |

## Opcje

**A — rekomendowana:** w BROAD i STANDARD dopuszczamy źródłowo potwierdzone pospolite skrótowce mimo obowiązkowych wielkich liter; neutralizacja wielkości liter następuje dopiero po kwalifikacji. Pozostałe reguły obu wariantów nadal obowiązują.

**B:** w obu wariantach wymagamy źródłowej formy małoliterowej dla tej klasy; same zapisy PCR/PESEL/AGD/RNA nie kwalifikują się. To dodatkowa polityka gry, nie wniosek, że SGJP uznaje je za nazwy własne lub skróty.

Skróty, symbole i nazwy własne nadal wyłączone w obu opcjach. Nie usuwamy dywizów ani niedozwolonych liter z form.

## Zasięg i ograniczenia pomiaru

Przesiew: jednoznaczne `nazwa_pospolita`, tag `subst`, `str.isupper()`. Wynik: 241 interpretacji / 177 kluczy; po profilu 32 liter i długości 2–15: 209 interpretacji / 155 kluczy. To populacja do przeglądu, **nie delta końcowego słownika** ani automatyczna klasyfikacja wszystkich skrótowców. Mieszane nazwy i kwalifikatory wymagają osobnego dowodu. Ostateczny wpływ wyliczy G4.

Odtworzenie: `python3 scripts/probe_generator_evidence.py --database data/work/import-20261004-1302/build.sqlite`. Strumieniowy powtórny przesiew zgodny z zapisanym wynikiem. Brak małoliterowych pcr/pesel/agd/rna dodatkowo sprawdzony w pełnej bazie; dla dna istnieją analizy zwykłych leksemów.

## Pozostałe discovery

G3 nadal nieukończona: semantyka mieszanych pól, kwalifikatory, pełna macierz fleksji/konstrukcji/ortografii oraz mapowanie KWJP. Odkryto pierwotny kod eksportera [Kuznia](https://git.nlp.ipipan.waw.pl/SGJP/Kuznia/blob/6c37a661866ce199dae2ce1558f1b152322f8b3b/export/lexeme_export.py); konieczny dalszy przegląd adekwatności wersji i warunków użycia, bez importu danych leksykalnych. Nie uznano brakujących dowodów za opcjonalne.
