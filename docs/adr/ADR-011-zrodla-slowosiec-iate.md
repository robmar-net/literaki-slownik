# ADR-011: Źródła TEMATY — Słowosieć 4.5 i IATE 2019

## TL;DR
TEMATY ([ADR-010](ADR-010-tematy-v1.md)) korzysta z dwóch nowych źródeł: Słowosieci 4.5 (T2) i IATE 2019 (T3).
Oba pobiera osobny skrypt z siecią. Budowa działa bez sieci i czyta przypięte pliki.
Ze Słowosieci budujemy własną pochodną SQLite bez danych redaktorów. Publikujemy tylko lematy.
Z IATE bierzemy polskie terminy `fullForm` z kodu dziedziny 4821.

## Kluczowe decyzje
- **Słowosieć 4.5:** relacje 11, 25, 27, kierunek `PARENT_ID → CHILD_ID`; kody części mowy 1–4, kody 5–8 pomijane.
- **Pochodna:** lista dozwolonych tabel i kolumn, tylko relacje `valid=1`, wiersze w stałej kolejności.
- **IATE 2019:** pełny TBX bez logowania; `fullForm`, bez `deprecatedTerm-admn-sts` i `supersededTerm-admn-sts`,
  niezawodność ≥ 3, kod dziedziny porównywany jako cały kod.
- **TBX:** DOCTYPE dozwolone; `<!ENTITY` albo podzbiór wewnętrzny to błąd; zewnętrznego DTD nie ładujemy.
- **Słowosieć pobieramy ponownie** zamiast przenosić starą kopię. Hash musi równać się pinowi.
- **Atrybucje:** nota i zastrzeżenie plWordNet; „Download IATE, European Union, 2019”.

## Otwarte pytania / ryzyka
- **Licencja Słowosieci 4.5.** Nota na slowosiec.pl mówi „plWordNet 4.2 © 2020”. Link licencji w repozytorium
  CLARIN-PL zwraca 404, a zip 4.5 nie ma pliku LICENSE. Przyjmujemy tekst noty jako licencję danych 4.5
  (decyzja operatora w badaniu). `LIMITATIONS.md` pakietu opisuje tę niejasność.
- **Znaczenie `lexicalunit.status` (0–5) jest nieudokumentowane.** Nie filtrujemy po nim.
- **Dziedzina 4821 obejmuje żeglugę śródlądową.** Udział mierzy raport ([ADR-010](ADR-010-tematy-v1.md)).
- **Dane IATE pochodzą z 2019 roku.** Trafność T3 zmierzy przegląd.
- **Determinizm bajtów pochodnej zależy od wersji SQLite.** Zmierzony na 3.51.0. Inna wersja może dać inny hash.

## Mapa numerów
Lokalne ADR-003 (Słowosieć) i ADR-004 (IATE) z
[decision-log](../../.maister/tasks/development/2026-10-28-11-tematy-morze/analysis/research-context/decision-log.md)
badania. Pozostałe lokalne decyzje są w [ADR-010](ADR-010-tematy-v1.md).

## Słowosieć 4.5
Zrzut `wordnet_work_4_5.zip`, 465 563 957 B, SHA-256 `30edc5f85c06408d372a897f1d1ff3d03fa939b8680b176c1f97351f4a72dcbc`.
Pobrany ponownie 2026-10-28T23:25:16Z z
<https://clarin-pl.eu/server/api/core/bitstreams/3197cd0f-bb4e-41ba-93e0-eec99ab8d519/content>; hash zgodny z pinem.

**Odstępstwo od `clarifications.md`.** Tam: przenosimy już pobraną kopię z `data/work/plwordnet/`.
Robimy inaczej: `scripts/fetch_tematy_sources.py` pobiera plik ponownie do `cache/plwordnet/` i zapisuje URL,
datę i hash. Pochodzenie jest wtedy odtwarzalne skryptem. Pin hasha wyklucza inną zawartość.

Wybór: hiponimia (11), części (25) i miejsca (27). Skojarzenia (108, 146) dawały w badaniu połowę szumu,
a domeny Princeton WordNet 0–11% dla morza.

### Pochodna `plwn45-tematy.sqlite`
`scripts/build_plwordnet_db.py` czyta zrzut SQL strumieniowo i kopiuje tylko:

| Tabela | Kolumny |
|---|---|
| `lexicalunit` | `ID`, `lemma`, `pos`, `variant` |
| `synset` | `ID`, `isabstract` |
| `unitandsynset` | `LEX_ID`, `SYN_ID`, `unitindex` |
| `synsetrelation` | `PARENT_ID`, `CHILD_ID`, `REL_ID`; tylko `valid=1` |
| `relationtype` | `ID`, `name` |
| `meta` | `zip_sha256`, `zip_member`, `script_version` |

- Bez `owner`, `comment`, `error_comment`, `iplog`, `iplimit` i `tracker_*`. Zrzut ma nazwiska redaktorów i log IP.
- Parser obsługuje wielowierszowe `INSERT` i ucieczki MySQL (`\'`, `\\`).
- Nazwy relacji muszą brzmieć: 11 `hiperonimia`, 25 `część`, 27 `miejsce`. Inna nazwa to błąd.
- `isabstract`: przez synset sztuczny przechodzimy, ale lematów z niego nie bierzemy.
  W domknięciu „morze” są 2 takie synsety; liczba lematów się nie zmienia (864).
- `status`: bez filtra.
- Budowa nie hashuje zipa. Hashuje pochodną i porównuje jej `meta` z pinem zipa.

Liczności (`verification/plwordnet-derivative.json`):

| Tabela | Nowa pochodna | Stara `data/work/plwordnet/plwn45.sqlite` |
|---|---|---|
| `lexicalunit` | 514 016 | 514 016 |
| `synset` | 354 316 | 354 316 |
| `unitandsynset` | 514 018 | 514 018 |
| `synsetrelation` | 1 491 275 | 1 491 277 |
| `relationtype` | 306 | 306 |

Różnica relacji (2) to dokładnie wiersze `valid=0`. Dwie budowy dały ten sam plik:
122 908 672 B, SHA-256 `aa65ad796ff5331ee6c0b2fddb81fb89786e428a3720cc8e52fbc45502b6c536`, SQLite 3.51.0.
Stara pochodna nie jest wejściem budowy.

### Kierunek relacji
`PARENT_ID` to hiperonim lub całość, `CHILD_ID` to hiponim, część lub miejsce. Sprawdzone na nowej pochodnej:
dla `statek 1` (7354) dzieci po 11 to m.in. `łódź 2` i `okręt 1`; po 25 m.in. `pokład 3`, `kadłub 3`;
po 27 m.in. `kambuz 1`, `ładownia 1`. Rodzice po 11: `jednostka 6`, `pojazd nawodny lub podwodny 1`,
`środek lokomocji 1`.

### Korzenie
Nazwa korzenia to `lemma + ' ' + variant` jednostki o najniższym `unitindex` w synsecie. Niezgodność to błąd.
Wszystkie 6 korzeni „morze” zgadza się na nowej pochodnej.

### Części mowy
Kody `lexicalunit.pos` potwierdzone na danych (`statek`, `morze` → 2; `pływać`, `żeglować` → 1;
`morski`, `szybki` → 4; `szybko`, `daleko` → 3):

| Kod | Klasy SGJP | Jednostek |
|---|---|---|
| 2 | `subst`, `depr` | 180 708 |
| 1 | `inf` | 45 721 |
| 4 | `adj` | 54 752 |
| 3 | `adv` | 14 238 |
| 5–8 | pomijane wszędzie, także w `wieloznaczny` | 218 597 |

Kody 5–8 to jednostki angielskie (np. `breathe`, `geranium`, `able`).

### Domknięcie T2 „morze”
Pełne domknięcie od 6 korzeni: 1 092 synsety, **864** lematy jednowyrazowe (definicja z [ADR-010](ADR-010-tematy-v1.md)).
Ten sam wynik na starej pochodnej. Audyt specyfikacji podał 874, bo liczył też lematy z łącznikiem i kropką
(`U-Boot`, `okręt-baza`, `ro-ro`, `s.y.` i inne).

## IATE 2019
Plik `IATE_download.zip` z <https://iate.europa.eu/em-api/artifacts/full-tbx>, 112 828 998 B,
SHA-256 `ac50c2a701484f3108eec6aea80ee23b5da0c0a2062fd5cc72790ac57ccf5c6f`, pobrany 2026-10-28T23:24:59Z.
Nagłówek `Last-Modified`: Mon, 30 Sep 2019 07:41:10 GMT. Plik w zipie: `IATE_export_26022019.tbx`.
Manifest źródeł zapisuje `last_modified` i `member`. To jedyna droga bez konta EU Login i bez kontaktu z autorami.

### Typ terminu
Projekt mówił o typie „term”. Ten plik go nie zna. Wartości `termType` (PL w nawiasie): `fullForm` 6 714 426
(75 016), `abbreviation` 302 352 (3 512), `phraseologicalUnit` 70 992 (462), `shortForm` 36 364 (1 743),
`formula` 1 219 (6). **„term” z projektu = `fullForm`.** Pozostałe typy pomija filtr; raport podaje ich liczby.

### Status administracyjny
Odrzucamy `deprecatedTerm-admn-sts` oraz `supersededTerm-admn-sts`. Drugi to decyzja techniczna dla spójności:
oba oznaczają termin, którego nie należy już używać. W 4821 polskich terminów deprecated jest 5, superseded 9. Wśród 78 kandydatów
nie ma żadnego superseded, więc dziś wpływ jest zerowy. Kandydaci: 77 bez statusu, 1 `preferredTerm-admn-sts`.

### Dziedzina
`subjectField` to lista kodów po przecinkach (np. `20, 2036, 48`). Dzielimy po `,`, przycinamy spacje
i porównujemy cały kod. Samo `48` nie pasuje do `4821`.
Kod 4821: 3 992 hasła, 577 z polskim terminem. Polskie terminy: `fullForm` 665, `abbreviation` 50, `shortForm` 28.
Po filtrach (`fullForm`, status, niezawodność ≥ 3, jedno słowo bez wielkich liter w źródle): 78, w tym 74 różne.

### Format TBX
- Drugi wiersz pliku: `<!DOCTYPE martif SYSTEM "TBXcoreStructV02.dtd">`, bez podzbioru wewnętrznego. Dozwolone.
- `<!ENTITY` albo podzbiór wewnętrzny to błąd. Zewnętrznego DTD nie pobieramy. W pliku nie ma deklaracji encji.
- Czytamy strumieniowo: `termEntry` → `descripGrp/descrip[subjectField]`, `langSet/tig` z `term`,
  `termNote[termType]`, `termNote[administrativeStatus]`, `descrip[reliabilityCode]`.
- Pomijamy pola, których T3 nie potrzebuje: `descripGrp/note` (226 977 haseł) i terminy `formula`.

Liczby pochodzą z pełnego skanu (`verification/iate-scan.json`): 934 921 haseł, 64 723 z polskim terminem.

## Wejścia budowy
- BROAD i STANDARD wiążemy przez przypięty `data/work/release-LL-PL-v30/release-manifest.json`.
  Jego hash musi równać się `export.release_manifest_sha256` przebiegu. Hashe BROAD i STANDARD muszą zgadzać się
  z wpisami w nim. Manifest przebiegu sam nie ma hasha BROAD.
- Manifest źródeł `config/generator/tematy-sources.json` przypina pochodną Słowosieci, rekord zipa i plik IATE.

## Atrybucje i publikacja
- `ATTRIBUTIONS.md` pakietu: najpierw `ATTRIBUTIONS.md` pakietu POP (z sekcją SGJP, BSD-2), potem nota
  i zastrzeżenie plWordNet, potem „Download IATE, European Union, 2019”.
- Słowosieć: publikujemy tylko lematy. Surowego zrzutu ani pochodnej SQLite nie publikujemy; zrzut zawiera nazwiska
  redaktorów i log IP. Bez nazwy Politechniki Wrocławskiej w reklamie.
- Surowe pliki leżą w `cache/` poza Git.

## Zmiany po audycie
Ten ADR zapisuje: K1 (`fullForm`, statusy), W1 (DOCTYPE), W2 (`subjectField`), W4 (kody części mowy),
W9 (atrybucje), D3 (`valid`, `isabstract`, `status`), D4 (nazwa korzenia), D5 (manifest wydania),
D6 (parser, liczności), D7 (bez hashu zipa), D8 (ponowne pobranie, `last_modified`, `member`),
D16 (kierunek relacji). Pozostałe zapisuje [ADR-010](ADR-010-tematy-v1.md).

## Pochodzenie
Pomiary: `verification/sources.json`, `plwordnet-derivative.json` i `iate-scan.json` w
[folderze zadania](../../.maister/tasks/development/2026-10-28-11-tematy-morze/verification/).
Powiązane: [#11](https://github.com/robmar-net/literaki-slownik/issues/11), [ADR-010](ADR-010-tematy-v1.md).
