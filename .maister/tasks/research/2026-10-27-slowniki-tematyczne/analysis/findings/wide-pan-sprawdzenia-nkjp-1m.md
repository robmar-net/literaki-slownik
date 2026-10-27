# NKJP, podkorpus milionowy 1.2: czy nagłówki mają temat

## TL;DR
- Nagłówki 3889 tekstów nie mają kodów UKD ani haseł BN. Mają tylko typ i kanał (`catRef`), tytuł, autora, wydawcę.
- Nagłówek całego podkorpusu deklaruje taksonomie `ukd` i `bn`, ale żaden tekst ich nie używa.
- Po tytułach: morze 11 tekstów (1464 słowa), rolnictwo 14 (1345), matematyka 1 (40). Głównie fragmenty ustaw.
- Rdzeń SGJP w tych tekstach: 0 jednoznacznych trafień w każdym temacie.
- Licencja jest niejednoznaczna: strona nkjp.pl mówi CC BY 4.0, README w archiwum CC BY 3.0 PL.

## Key Decisions
- Pobrałem całe archiwum (170,8 MB, poniżej progu 200 MB). Same nagłówki nie są dostępne osobno; wyciągnąłem z archiwum tylko `header.xml`, `text.xml` i pliki opisu.
- Temat wyznaczyłem ręcznie po tytule źródła (`sourceDesc/bibl/title`), bo innego pola tematu nie ma. Odrzuciłem fałszywe trafienia wzorca („Gazeta Pomorska”, „Przegląd Sportowy”, „O humorze poważnie”) i teksty literackie o niejasnym temacie („Międzymorze”, „Kariera na trzy karpie morskie”).
- Na potrzeby tego pomiaru (bez redystrybucji) rozbieżność licencji nie blokuje. Przy użyciu w pakiecie trzeba ją rozstrzygnąć, np. jak w ADR-006 (spełnić wymagania obu wersji).

## Open Questions / Risks
- Licencja: trzy źródła, trzy zapisy (niżej). Dla użycia w pakiecie potrzebna decyzja właściciela; ADR-006 dotyczy tylko n-gramów NKJP.
- Teksty urzędowe (ustawy) dominują w rolnictwie i morzu. To słownictwo prawne, nie tematyczne.
- Pełny NKJP ma UKD i hasła BN w nagłówkach (książka NKJP, s. 17), ale nie jest do pobrania. Podkorpus milionowy ich nie zachował.

## Licencja i wersja
| Źródło | Zapis |
|---|---|
| https://nkjp.pl/index.php?page=14&lang=0 | „Ręcznie anotowany milionowy podkorpus NJKP, dostępny na licencji CC-BY 4.0.” |
| http://clip.ipipan.waw.pl/NationalCorpusOfPolish (ostatnia edycja 2023-11-20) | „available on CC-BY licence” (bez wersji) |
| `README` w archiwum (data pliku 2021-07-08) | „Podkorpus dostępny jest na licencji CC BY 3.0 PL (Uznanie autorstwa 3.0 Polska)”; część angielska: „CC BY 3.0 PL licence (Attribution 3.0 Unported)” z linkiem do 3.0 |
| `NKJP_1M_header.xml` | „available publicly for free” |
| `header.xml` każdego tekstu | `availability status="free"`: „See the licence agreement.” |

Wszystkie wersje to CC BY (atrybucja, bez ograniczeń niekomercyjnych). Różni się tylko numer wersji.

## Pobranie
- URL: https://clip.ipipan.waw.pl/NationalCorpusOfPolish?action=AttachFile&do=get&target=NKJP-PodkorpusMilionowy-1.2.tar.gz (link ze strony nkjp.pl; `Last-Modified: Thu, 08 Jul 2021 21:15:58 GMT`).
- Wersja 1.2. Rozmiar 170 796 368 B. SHA-256 `1ad87f5a653bf30c986bd791fa64d0b93989f8056887dbc28957596747ef953e`.
- Dostęp 2026-10-27.
- Lokalnie: `data/work/nkjp-1m/dl/`, nagłówki w `data/work/nkjp-1m/hdr/`, teksty w `data/work/nkjp-1m/txt/`, opis w `data/work/nkjp-1m/top/` (gitignore: `/data/work/`).
- Skrypty: `/private/tmp/claude-501/-Users-robmar-Projects-Literaki/7eed58b5-7e1f-4a3f-8359-d9bc24330c2b/scratchpad/pan2/` — `nkjp_hdr.py`, `hits_nkjp.py`; wyniki `nkjp_titles.json`, `hits_nkjp.out`.

## Co jest w nagłówkach
3889 nagłówków (`nkjp_hdr.py`, ElementTree). W każdym: `fileDesc`, `titleStmt`, `extent` (liczba słów), `sourceDesc/bibl` (tytuł, `idno type="nkjp"`, `note type="text_origin"`), `textClass`, `revisionDesc`. Częściowo: `date` 2528, `author` 1601, `publisher` 1380, `pubPlace` 1124, ISBN 266, ISSN 11.

- `catRef` ma tylko dwa schematy: `#taxonomy-NKJP-type` (3889) i `#taxonomy-NKJP-channel` (3889).
- Brak `classCode`, `keywords`, `term` i `catRef` ze schematem `#ukd` lub `#bn`. Sprawdzone dwa razy: parserem i `grep -ri 'ukd|#bn|classCode|keywords|udc'` (jedyne trafienie w nagłówku tekstu to nazwisko „Dudczak”).
- `NKJP_1M_header.xml` (w. 273–289) deklaruje taksonomie `ukd` („UDC-P058”) i `bn` („Słownik języka haseł przedmiotowych BN, wyd. 5, stan na 31.12.2004”), ale bez kategorii.
- Typy (teksty): publ 1986, urzęd 387, lit 376, konwers 283, net_nieinterakt 227, nd 175, net_interakt 161, fakt 127, media 80, inf-por 56, nklas 20, qmow 8, listy 2, lit_poezja 1.
- `statystyki.txt`: 1 003 956 słów.

## Teksty tematu (po tytule)
| Temat | Teksty | Słowa | Co to jest |
|---|---:|---:|---|
| Morze | 11 | 1 464 | 8 ustaw (Kodeks morski, porty, izby morskie, bezpieczeństwo morskie, żegluga śródlądowa, praca na statkach, obszary morskie, urządzenia portowe), czasopismo „Morze” (491), „Szaman morski” (318), „Marynarze w walce o niepodległość Polski” (201) |
| Rolnictwo | 14 | 1 345 | 9 aktów prawnych (ARiMR, izby rolnicze, hodowla zwierząt, produkty rolne i in.), „Działkowiec” (458), strony „Ekoogrodnictwo” (134) i „Pszczelarstwo” (104), 2 prace naukowe o rolnictwie |
| Matematyka | 1 | 40 | „Filozofia matematyki” (typ naukowo-dydaktyczny) |

## Rdzeń SGJP w tekstach tematu
Metoda jak dla KWJP½M (`wide-pan-sprawdzenia-kwjp-half-m.md`): formy leksemów z etykietą, „jednoznaczne” = forma nie należy do leksemu spoza rdzenia.

| Temat | Grupa | Słowa | Trafienia | Jednoznaczne | Leksemy |
|---|---|---:|---:|---:|---|
| Morze | temat | 1 403 | 1 | 0 | — |
| Morze | reszta | 966 060 | 436 | 47 | `prom` 16, `armator` 8, `transatlantyk` 4, `fał` 4, `frachtowiec` 3 i in. (13) |
| Rolnictwo | temat | 1 285 | 0 | 0 | — |
| Rolnictwo | reszta | 966 178 | 568 | 1 | `pojedynkować` 1 (etykieta `ogr.`, w tekście raczej inne znaczenie) |
| Matematyka | temat | 40 | 0 | 0 | — |
| Matematyka | reszta | 967 423 | 158 | 70 | `kwadratowy` 23, `parametr` 23, `współczynnik` 8, `czworościan` 3 i in. (13) |

Liczba słów z tokenizacji (`text.xml`) różni się nieco od `extent` w nagłówku.

Wniosek: tematyczne teksty w podkorpusie są za małe i nie niosą rdzenia SGJP. Podkorpus milionowy nie da podkorpusu tematycznego.
