# Źródła zewnętrzne list tematycznych (runda 2, `wide-zewnetrzne`)

Data: 2026-10-27. Tylko odczyt: strony, pojedyncze zapytania API, nagłówki HTTP. Bez pobierania całych zbiorów. Bez kontaktu z autorami.

## TL;DR
Najlepsze otwarte źródło to **IATE**: jasna licencja pobrania (wolno kopiować, także komercyjnie i z przeróbkami, z podaniem źródła) i dziedziny EuroVoc przy każdym haśle.
Ale terminy są głównie wielowyrazowe: słowa pojedyncze to ok. 8% (morze), 7% (matematyka), 21% (rolnictwo) w próbie.
**AGROVOC** ma 34 780 polskich etykiet rolniczych, ale licencja polskiej części jest niejasna. **EuroVoc** jest czysty licencyjnie, ale mały (35 pojęć morskich, 3 matematyczne).
Wikisłownik ma kwalifikatory `żegl.`, `roln.`, `mat.` (setki–tysiące stron), lecz jest odroczony. Wikidata Lexemes (CC0) prawie nie ma polskich danych.

## Key Decisions
- Ranking: 1) IATE, 2) AGROVOC (po wyjaśnieniu licencji), 3) EuroVoc jako zalążek, 4) Wikisłownik (tylko opis), dalej reszta.
- IATE i EuroVoc traktujemy jako źródła **terminów urzędowych UE**, nie słownictwa ogólnego. Nadają się na uzupełnienie rdzenia SGJP, nie na pełny temat.
- Nie prosimy IATE o token API (to byłby kontakt). Legalna droga hurtowa to plik pobrania (konto EU Login) albo stary pełny TBX z 2019 r.
- Danych Wikisłownika nie użyliśmy jako wejścia; liczby podajemy tylko jako opis.

## Open Questions / Risks
- Liczby IATE to **dolne granice** z wyszukiwania częściowego (litera „a”), a udział słów pojedynczych pochodzi z próby 86–300 haseł na temat. Pewność: średnia.
- Dziedzina IATE „rolnictwo” (EuroVoc 56) obejmuje też rybołówstwo i leśnictwo; dużo nazw gatunków ryb i środków chemicznych. Słowa pojedyncze to często nazwy łacińsko-polskie lub rzadkie.
- AGROVOC: FAO pisze, że prawa do treści w innych językach niż sześć języków FAO „rests with the institutions that authored it”. Polskiego autora nie ustaliliśmy. Bez tego AGROVOC-PL jest zablokowany.
- Wikidata: WDQS był w trybie awaryjnym (limit 1 zapytanie/min). Liczba 3684 leksemów może być zaniżona.
- Nie znaleźliśmy żadnego polskiego słownika żeglarskiego, rolniczego ani matematycznego z jasną otwartą licencją.

## 1. IATE — baza terminologii UE

**Co daje:** każde hasło ma dziedziny z drzewa EuroVoc (np. `TRANSPORT / maritime and inland waterway transport`, kod 4821; `SCIENCE / … / mathematics`, kod 1835; `AGRICULTURE, FORESTRY AND FISHERIES`, kod 56). Hasło może mieć kilka dziedzin. Terminy mają typ (term, abbreviation, phrase…), ocenę i niezawodność 1–4.

**Licencja (pobranie) — pewność: wysoka.** Warunki strony Download IATE:
> „You are allowed to reproduce the data available for download from this page for your personal needs, to distribute it for non-commercial and commercial purposes, and to make and distribute derivative works, provided the source is acknowledged as follows: Download IATE, European Union, [year].”

Nota prawna: dane z pliku pobrania „is not copyright protected, and can therefore be freely downloaded and reproduced”. UE zachowuje prawo do struktury bazy, ale też pozwala ją powielać.
**Uwaga:** to zezwolenie **nie obejmuje** danych z wyszukiwarki, widżetu i API: „Copying from this website or from the results made available via the search widget or search API is forbidden unless it is explicitly allowed”. Hurtowo wolno więc brać tylko plik pobrania.

**Dostęp:**
- Pobranie z filtrami (język, dziedzina z poddziedzinami, typ terminu, ocena, niezawodność), TBX lub CSV. Wymaga konta EU Login. Plik dostępny 7 dni.
- Stary pełny plik bez logowania: `https://iate.europa.eu/em-api/artifacts/full-tbx` → `IATE_download.zip`, 112 828 998 B, `Last-Modified: 30 Sep 2019` (sprawdzone nagłówkiem, bez pobierania).
- API wyszukiwania: duże ilości zapytań bez tokenu są odrzucane; token wymaga kontaktu z CdT — odpada.

**Liczby PL (zapytania API 2026-10-27, wyszukiwanie częściowe, poddziedziny włączone):**

| Temat | Dziedzina IATE | Hasła PL z literą „a” (dolna granica) | Próba | Słowa pojedyncze w próbie |
|---|---|---:|---|---:|
| Morze | 4821 transport morski i śródlądowy | 1155 | 300 haseł, 771 terminów | 61 (7,9%) |
| Matematyka | 1835 mathematics | 87 | 86 haseł, 121 terminów | 8 (6,6%) |
| Rolnictwo | 56 rolnictwo, leśnictwo, rybołówstwo | 13 784 | 200 haseł, 671 terminów | 139 (20,7%) |

„Słowo pojedyncze” = sam ciąg małych liter polskich (bez spacji, cyfr, wielkich liter).
Przykłady: morze — `cuma`, `forpik`, `kilson`, `szpigat`, `werp`, `żaglowiec`, `wyokrętowanie`; matematyka — `iloraz`, `mianownik`, `odcięta`, `rzędna`, `wielomian`; rolnictwo — `karp`, `indyk`, `brzana`, `czarniak`, ale też `dichlorodifenylotrichloroetan`, `ebola`, `fosfina`.
Typowe wielowyrazowe: „Międzynarodowa konwencja o zapobieganiu zanieczyszczaniu morza przez statki”, „system automatycznej identyfikacji statków”.

**Ocena:** licencja dobra dla publicznego projektu. Słów pojedynczych jest mało, a wiele to terminy prawne UE. Matematyka bardzo uboga (<100 haseł). Morze daje kilkadziesiąt–sto kilkadziesiąt nowych słów, rolnictwo kilka tysięcy kandydatów (dużo gatunków).

Źródła (dostęp 2026-10-27):
- https://iate.europa.eu/assets/i18n/en/static_pages/iate_dl_conditions.html
- https://iate.europa.eu/assets/i18n/en/static_pages/iate_dl_intro.html
- https://iate.europa.eu/assets/i18n/en/static_pages/legal-notice.html
- https://iate.europa.eu/assets/i18n/en/static_pages/apis.html
- https://online-help.iate.europa.eu/technical-info/iate-download/
- https://data.europa.eu/api/hub/search/datasets/iate (licencja: „European Commission reuse notice”, decyzja 2011/833/UE)
- API: `POST https://iate.europa.eu/em-api/entries/_search`, `GET https://iate.europa.eu/em-api/domains/_tree`

## 2. AGROVOC (FAO)

**Co daje:** tezaurus rolnictwa, żywności, rybołówstwa, leśnictwa, gatunków. Polskie etykiety: **34 780 `skos:prefLabel` + 8808 `skos:altLabel`** (API Skosmos `labelStatistics`). Udziału słów pojedynczych nie mierzyliśmy.

**Licencja — pewność: wysoka co do tekstu, niska co do PL.** FAO:
> „Copyright for AGROVOC content in FAO languages - English, French, Spanish, Arabic, Russian and Chinese - is with FAO … while content in other languages rests with the institutions that authored it.”
> Treść w sześciu językach FAO: „Creative Commons Attribution 4.0 International (CC-BY-4.0)”.

Polski nie jest językiem FAO. Rejestry zewnętrzne podają różnie (CC BY 4.0, CC BY-SA, CC BY IGO 3.0). Instytucji autorskiej PL nie znaleźliśmy.

**Dostęp:** pobranie RDF/XML i NT (AGROVOC Core), SPARQL, API Skosmos.
**Ocena:** największe źródło dla rolnictwa, ale bez jasnej licencji PL nie nadaje się do wydania. Status: do wyjaśnienia (bez kontaktu — tylko jeśli warunki znajdą się w dokumentach).

Źródła (2026-10-27): https://www.fao.org/agrovoc/maintenance, https://www.fao.org/agrovoc/releases, https://agrovoc.fao.org/browse/rest/v1/agrovoc/labelStatistics

## 3. EuroVoc (Urząd Publikacji UE)

**Co daje:** tezaurus dziedzinowy UE (21 dziedzin, mikrotezaurusy). Pełne PL. Jest to też drzewo dziedzin IATE.

**Licencja — pewność: wysoka.** data.europa.eu: wszystkie dystrybucje (SKOS, XML, TBX, Excel) pod „European Commission reuse notice” (decyzja 2011/833/UE): ponowne użycie, także komercyjne, z podaniem źródła.

**Liczby PL (SPARQL `publications.europa.eu/webapi/rdf/sparql`):**

| Zakres | Pojęcia (prefLabel PL) | Jednowyrazowe | Przykłady jednowyrazowych |
|---|---:|---:|---|
| 4821 transport morski i śródlądowy | 35 | 8 | `barka`, `port`, `prom`, `lodołamacz`, `zbiornikowiec` |
| 56 rolnictwo (8 mikrotezaurusów) | 374 | 65 | `ugór`, `płodozmian`, `jałówka`, `żniwiarka`, `silos`, `sad` |
| 60 żywność (dodatkowo) | 275 | 93 | `jęczmień`, `pszenżyto`, `gryka`, `chmiel`, `słód` |
| matematyka (1835 z węższymi) | 3 | 1 | `matematyka`, `biometria`, „teoria gier” |

**Ocena:** licencja czysta, ale za mało słów. Przydatne jako zalążek lub test pokrycia, nie jako lista.

Źródła (2026-10-27): https://data.europa.eu/api/hub/search/datasets/eurovoc, https://op.europa.eu/en/web/eu-vocabularies/dataset/-/resource?uri=http://publications.europa.eu/resource/dataset/eurovoc (wersja 4.24)

## 4. Wikisłownik — tylko opis (odroczony przez użytkownika)

**Co daje:** kwalifikatory przy znaczeniach (szablony `{{żegl}}` = „żeglarstwo, żegluga”, `{{mors}}`, `{{ryb}}`, `{{roln}}`, `{{mat}}`) i strony indeksów tematycznych.

| Element | Liczba (API, 2026-10-27) | Uwaga |
|---|---:|---|
| strony z `{{żegl}}` | 1856 | wszystkie języki, nie tylko PL |
| strony z `{{roln}}` | 2333 | j.w. |
| strony z `{{mors}}` / `{{ryb}}` | 271 / 147 | j.w. |
| `Indeks:Polski - Żeglarstwo` | 434 linki | |
| `Indeks:Polski - Matematyka` / `- Indeks terminów matematycznych` | 151 / 792 linki | |
| `Indeks:Polski - Pszczelarstwo` / `- Ryby` / `- Gwara marynarska` | 108 / 56 / 28 | brak indeksu „Rolnictwo” |

Kwalifikator jest **przy znaczeniu**, nie przy leksemie — lepiej niż w SGJP. Licencja: CC BY-SA 4.0 (teksty Wikimedia); wymóg „na tych samych warunkach” może objąć wydaną listę. Liczby `{{mat}}` nie zmierzyliśmy (limit zapytań).

## 5. Wikidata Lexemes i Wikipedia

- **Wikidata Lexemes (CC0):** WDQS: **3684** polskich leksemów, **1** ze znaczeniem z „field of usage” (P9488). Licencja idealna, danych praktycznie brak. Pewność: średnia (WDQS w trybie awaryjnym).
- **Wikipedia PL (CC BY-SA 4.0):** kategorie to drzewa artykułów (`Kategoria:Żeglarstwo` 103 strony + 25 podkategorii; `Rolnictwo` 148 + 24; `Matematyka` 7 + 25). Tytuły to głównie nazwy własne i wyrażenia. Mało przydatne bez dużej obróbki.

## 6. Inne

- **GEMET (EEA):** tezaurus środowiska, wg dziennika zmian licencja CC BY 4.0 od 4.2.3 (2021). Zawiera grupy rolnicze. Polskich liczb nie sprawdzono. Marginalny. https://www.eionet.europa.eu/gemet/
- **GUS „Pojęcia stosowane w statystyce publicznej”:** definicje rolnicze (np. „ziemiopłody”), ale głównie wyrażenia; warunków ponownego użycia nie znaleźliśmy. https://stat.gov.pl/metainformacje/slownik-pojec/pojecia-stosowane-w-statystyce-publicznej/
- **Polskie słowniki żeglarskie:** w sieci tylko wydania komercyjne z copyright (np. Nautica) lub glosariusze sklepów bez licencji. Otwartego nie znaleźliśmy.
- **Akty prawne PL** (np. Kodeks morski) nie są chronione (art. 4 pr. aut.), ale słowniczki ustawowe są krótkie i wielowyrazowe. Niesprawdzone ilościowo.
- **Normy PN** (terminologia) — chronione, PKN; odpadają.

## 7. Ranking

| # | Źródło | Temat | Skala PL | Słowa pojedyncze | Licencja | Dostęp | Ocena |
|---|---|---|---|---|---|---|---|
| 1 | IATE | dziedziny EuroVoc przy haśle | morze ≥1155, mat. ≥87, roln. ≥13 784 haseł | 7–21% | wolne ponowne użycie z atrybucją (plik pobrania) | EU Login lub TBX 2019 | **dobre uzupełnienie** |
| 2 | AGROVOC | rolnictwo szeroko | 34 780 + 8808 etykiet | nie mierzono | PL: prawa przy autorze, niejasne | RDF, SPARQL | **zablokowane do wyjaśnienia** |
| 3 | EuroVoc | mikrotezaurusy | 35 / 374 / 3 | 8 / 65 / 1 | 2011/833/UE, z atrybucją | SKOS | zalążek, za mały |
| 4 | Wikisłownik | kwalifikator przy znaczeniu | setki–tysiące stron | wysoki (hasła słownikowe) | CC BY-SA 4.0 | API, zrzuty | **odroczony** |
| 5 | Wikipedia | kategorie artykułów | setki | niski | CC BY-SA 4.0 | API | słabe |
| 6 | Wikidata Lexemes | P9488 przy znaczeniu | ~0 | — | CC0 | WDQS | dziś bezużyteczne |
| 7 | GEMET, GUS, akty prawne | środowisko / statystyka / prawo | małe | niski | CC BY 4.0 / ? / wolne | WWW | marginalne |
