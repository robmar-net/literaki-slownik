# Zasoby PAN: korpusy i inne listy (NKJP, KWJP, IPI PAN)

## TL;DR
- Żaden korpus PAN nie oznacza dziedziny słowa. Oznacza najwyżej tekst: typ (np. fakt, fikcja, publicystyka) i kanał.
- NKJP ma w nagłówkach tekstów kody UKD i hasła przedmiotowe BN. Według twórców nie są one dostępne dla użytkowników zewnętrznych.
- KWJP½M (CC BY 4.0, 11 108 próbek, archiwum 2,86 MB) ma pole `meta_topic`. To krótki, otwarty opis tematu, tylko dla książek. Tematu słowa z niego nie wyznaczymy.
- Inne zasoby IPI PAN z dziedziną dotyczą ekonomii (SEJFEK) i lotnictwa (glosariusze ELRC). Nic dla marynistyki, rolnictwa ani matematyki.

## Key Decisions
- Korpusów PAN nie używamy do etykiet dziedzinowych. Mogą najwyżej potwierdzić użycie słowa (frekwencja), nie jego temat.
- KWJP½M `meta_topic` warto zbadać tylko tanio: archiwum ma 2,86 MB, ale pobranie wymaga zgody orkiestratora.

## Open Questions / Risks
- Nie wiemy, czy nagłówki podkorpusu milionowego NKJP (CC BY 4.0) zawierają UKD i hasła BN. Książka mówi o „nagłówkach” całego korpusu. Sprawdzenie wymaga pobrania.
- Nie znamy wartości `meta_topic` w KWJP½M ani tego, jak często pole jest wypełnione. Opis wskazuje, że rzadko: tylko książki.
- Nie przeszukałem całego repozytorium CLARIN-PL, a wyszukiwarka nie znalazła tam zasobu PAN z dziedziną słowa.

## NKJP — Narodowy Korpus Języka Polskiego (IPI PAN, IJP PAN, PWN, UŁ)

**Metadane tekstu** (Przepiórkowski i in. 2012, *Narodowy Korpus Języka Polskiego*, rozdz. 2, s. 15–23):
- **Typ (12):** literatura piękna, literatura faktu, publicystyka i krótkie wiadomości prasowe, typ naukowo-dydaktyczny, typ informacyjno-poradnikowy, książka niebeletrystyczna niesklasyfikowana, inne teksty pisane, listy, Internet, teksty mówione konwersacyjne, teksty mówione medialne, teksty quasi-mówione.
- **Kanał:** prasa (dziennik, tygodnik, miesięcznik, inne), książka, Internet, mówiony, ulotka, rękopis.
- **Temat:** „przyjmujemy bez zmian dwie klasyfikacje Biblioteki Narodowej, a mianowicie kod Uniwersalnej Klasyfikacji Dziesiętnej i system haseł tematycznych”. UKD dotyczy tylko książek.
- **Dostępność tematu:** „dane te są zawarte w nagłówkach, ale nie w metadanych wyświetlanych w programach konkordancyjnych, nie są więc dostępne dla zewnętrznego użytkownika korpusu” (s. 17).

Źródło: https://nkjp.pl/settings/papers/NKJP_ksiazka.pdf (dostęp 2026-10-27). Książka ma licencję CC BY 3.0 PL.

**Ile.** Ponad 1,5 mld słów: https://nkjp.pl/index.php?page=0&lang=0 (dostęp 2026-10-27).

**Dostęp i licencja.** Do pobrania jest „Podkorpus milionowy” z dopiskiem „dostępny na licencji CC-BY 4.0”: https://nkjp.pl/index.php?page=14&lang=0 (dostęp 2026-10-27). Unigramy projekt już ma; licencję opisuje ADR-006.

**Status.** Zamknięty. NKJP „nie jest aktualizowany i powiększany” (Gruszczyński 2020): https://publikacje.pan.pl/Content/120189/PDF/2020-01-POLS-20-Gruszczynski.pdf (dostęp 2026-10-27).

**Przydatność.** Typ „naukowo-dydaktyczny” to gatunek, nie dziedzina. Nie odróżni matematyki od rolnictwa.

## KWJP — Korpus Współczesnego Języka Polskiego 2011–2020 (IPI PAN)

**Metadane tekstu.**
- Typ: `typ_fikcja`, `typ_fakt`, `typ_publicystyka`.
- Kanał: `kanal_ksiazka`, `kanal_prasa_dziennik`, `kanal_prasa_tygodnik`, `kanal_prasa_miesiecznik`, `kanal_prasa_inne`, `kanal_internet`.
- `meta_topic` – „tematyka (wartość opisowa; dotyczy tylko książek)”.
  Źródło: `KWJP½M_README.pdf` w https://github.com/ipipan/kwjp100-varia (dostęp 2026-10-27).
- Artykuł o korpusie mówi, że książki mają „bardzo krótki opis” gatunku lub dziedziny (np. „historia, socjologia, pszczelarstwo”). „Wartości z tej klasyfikacji nie są jednak zamkniętym zbiorem, w związku z czym grupowanie na jej podstawie wyników zapytań korpusowych nie ma większego sensu.”
  Źródło: Kieraś i in., *Język Polski* CV(2), s. 9, doi 10.31286/JP.001055; kopia lokalna `cache/kwjp/article.pdf`.
- W interfejsie (https://kwjp.pl) są korpusy „balanced” i „unbalanced” z podziałem na tygodnik, dziennik, inne i dzienniki lokalne. Są też filtry metadanych; strona nie wymienia pola tematu.

**Ile.** Korpus zrównoważony ma ok. 100 mln segmentów. Niezrównoważony ma ponad 1,4 mld segmentów (artykuł, s. 9). KWJP½M ma 11 108 próbek i 513 009 słów (README PDF).

**Dostęp.**
- Listy frekwencyjne (`freqlists/`, 1–4-gramy × lemma/orth/orth_lc × all/fakt/fikcja/publicystyka) i `KWJP½M_samples.tar.gz` (2 860 455 B) są w repozytorium.
  Źródło rozmiaru: `cache/kwjp/tree.json`.
- Wyszukiwarka: https://kwjp.pl.

**Licencja.**
- Repozytorium: „Ze wszystkich zasobów zamieszczonych w tym repozytorium można korzystać na zasadach licencji CC-BY 4.0 (Creative Commons Attribution 4.0)”. Źródło: https://github.com/ipipan/kwjp100-varia (dostęp 2026-10-27).
- Strona list: tylko „Copyright © Instytut Podstaw Informatyki PAN, 2023”. Źródło: https://kwjp.pl/lists/doc/about/ (dostęp 2026-10-27).

**Status.** Aktywny; stopka strony ma rok 2026.

**Przydatność.** Słaba. `meta_topic` dotyczy tylko książek, nie ma stałego zbioru wartości i opisuje tekst, a nie słowo. Mógłby dać tematyczny podkorpus, np. książki „pszczelarstwo”, ale tylko z próbek KWJP½M (0,5 mln słów), czyli bardzo mało.

## Inne zasoby IPI PAN z dziedziną

Lista 88 zasobów Zakładu Modelowania Języka: http://language.ipipan.waw.pl/resources/ (dostęp 2026-10-27).

| Zasób | Dziedzina | Ile | Licencja | Dla 3 tematów? |
|---|---|---|---|---|
| SEJFEK | ekonomia, finanse | 11 212 leksemów wielowyrazowych | CC BY-SA 3.0 | nie |
| NKJP1mEcono, gpwEcono, plWikiEcono, Economic Excerpts | ekonomia | 52 leksemy (NKJP1mEcono) | nie podano | nie |
| ELRC (glosariusze TBX) | lotnictwo (ULC), zamówienia publiczne (UZP) | nie podano | nie podano | nie; rolnictwo tylko jako pamięci tłumaczeń XLIFF |
| WikiTopoPl, SAWA | nazwy geograficzne, transport w Warszawie | 155 tys. nazw / ok. 9 tys. nazw | nie podano | nie (nazwy własne) |
| TermoPL (narzędzie) | ekstrakcja terminów (C-value) | — | plik LICENSE, treści nie czytałem | pośrednio: wydobyłby terminy z tekstów dziedzinowych, gdybyśmy je mieli |

Źródła: http://language.ipipan.waw.pl/resources/2012-06-sejfek/, http://language.ipipan.waw.pl/resources/2017-01-elrc/, http://language.ipipan.waw.pl/resources/2016-05-termopl/ (dostęp 2026-10-27).

**IJP PAN poza WSJP.** Wyszukiwanie nie znalazło elektronicznego słownika terminologicznego IJP PAN dla marynistyki, rolnictwa ani matematyki.

**CLARIN-PL.** Wyszukiwanie nie znalazło zasobu PAN z dziedziną słowa. Rekordy IPI PAN mają różne licencje, np. LCM-PL CC BY-SA 3.0: https://clarin-pl.eu/dspace/handle/11321/585?show=full (dostęp 2026-10-27).

## Kandydaci spoza PAN
- Słowosieć / plWordNet (PWr): domeny synsetów; licencja plWordNet (typu WordNet), do sprawdzenia.
- Glosariusze instytucji publicznych w ELRC-SHARE: terminologia urzędowa; licencje różne, per zasób.
- Lista sjp.pl (słownik do sprawdzania pisowni): brak dziedzin; GPL/LGPL/MPL/CC SA/Apache 2.0 wg README Debiana.
