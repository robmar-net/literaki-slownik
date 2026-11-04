# Świadoma zmiana 01: Dobry słownik (wulwa)

## TL;DR
- **Wulwa jest w Dobrym słowniku** (DS): https://dobryslownik.pl/slowo/wulwa/226245/ (odczyt 2026-11-03). Hasło dodano w styczniu–lutym 2024 na prośbę abonentów (blog DS). Wniosek z #16, że wulwy „nie ma w żadnym źródle”, był błędny: DS w #16 nie sprawdzano.
- DS to **słownik poprawnościowy z poradnią**, a nie słownik języka inkluzywnego. Prowadzi go firma jednoosobowa Niecowiedzy.pl Łukasz Szałkiewicz (redaktorzy dr Ł. Szałkiewicz, dr A. Czesak, dr hab. S. Żurowski, od 2026 też dr B. Cieśla). Wulwa nie ma żadnego kwalifikatora (definicja odnosi się do kobiet). Świadomą zmianę widać w przykładach: cykl „Niech żyje wulwa!” w wysokieobcasy.pl (6.08.2022) i „Seksuologia Polska” (2015).
- **Licencja haseł: wszystkie prawa zastrzeżone**, a znaczna część treści jest płatna. Ocena hasła: **tylko dowód ręczny** (link + data odczytu).
- **Wyjątek: tezaurus DS jest na wolnej licencji** (GPL-2.0+ / LGPL 2.1), wydawany co kwartał i do pobrania. Ma wulwę (w wersji z 2026-10-01; w 2008 jej nie było). Ocena: **ALLOWED** jako sygnał lokalny „jest w tezaurusie DS vX”, a import listy haseł **do decyzji** (copyleft).
- Kontrole w DS: wulwa, cringe, boomer, hejt, lockdown i antyszczepionkowiec są; ghostingu nie ma (kontrola dodatnia w tym samym źródle: hejt).

## Kluczowe decyzje
- Hasło DS idzie do karty kandydata jako dowód ręczny: URL, data odczytu, krótka parafraza, bez kopiowania definicji ani przykładów.
- Tezaurus DS można sprawdzać lokalnie skryptem (obecność słowa, wersja, SHA256). Do repo trafia tylko fakt obecności i atrybucja, nie lista.
- Plik `pl_PL.dic` z pakietu `.oxt` DS **pomijamy**. To stary korektor z OOo z 2008 r. i może pochodzić z SJP.pl.

## Otwarte pytania i ryzyka
- **Ryzyko SJP.pl: niskie, ale niezerowe.** Według strony `/historia/` Szałkiewicz zaczynał jako hobbystyczny redaktor SJP.pl, a DS opisuje jako słownik zbudowany od nowa na własnej bazie (parafraza wywiadu). Hasła DS są redagowane ręcznie, z przykładami z korpusów; tezaurus pochodzi z OpenThesaurus (synonimy.ux.pl, M. Miłkowski), nie z SJP.pl.
- Licencja tezaurusu jest niespójna: plik txt podaje GPL-2.0+, a README w `.oxt` LGPL 2.1. Obie są wolne, ale do atrybucji trzeba wybrać jedną i podać obie.
- Wayback Machine był 2026-11-03 niedostępny („Temporarily Offline”), więc daty pierwszego wpisu nie sprawdzono w archiwum. Datę opieramy na blogu DS i identyfikatorach haseł.
- Lista haseł z map witryny (sitemap) to baza danych. Prawo sui generis i TDM (art. 26³ pr. aut.) ocenia zbieracz `ccrawl`. Pomiar zrobiłem tylko lokalnie, bez publikowania list.

## Hasło „wulwa” (odczyt 2026-11-03)
- URL: https://dobryslownik.pl/slowo/wulwa/226245/; mapa witryny `lastmod` 2024-03-03.
- Treść (parafraza): zewnętrzna część układu płciowego kobiety (wargi sromowe, wzgórek łonowy, łechtaczka, przedsionek pochwy). Synonim tożsamy: srom. Bliskoznaczne: specjalistycznie wagina, książkowo łono, a także potoczne. Rzeczownik żeński z pełną odmianą (10 form: wulwa, wulwy, wulwie, wulwę, wulwą, wulwo, wulw, wulwom, wulwami, wulwach).
- Przykłady: wysokieobcasy.pl 6.08.2022 (cykl „Niech żyje wulwa!”, oswajanie tabu); P. Flis, „Seksuologia Polska” 2015 nr 2.
- Data i powód dodania: wpis na blogu „Wulwa w popołudniówce, czyli podsumowanie stycznia i lutego 2024” (5.03.2024), https://blog.dobryslownik.pl/wulwa-w-popoludniowce-czyli-podsumowanie-stycznia-i-lutego-2024/. Wulwa jest tam na liście 11 nowych haseł ze stycznia i lutego, opracowanych na prośbę abonentów. Wierszyk we wpisie nawiązuje do sporu o gazetową okładkę.

## Licencja i dostęp (cytaty, odczyt 2026-11-03)
- Regulamin (https://dobryslownik.pl/regulamin/, ostatnia modyfikacja 4.11.2025): „O ile nie zaznaczono inaczej, serwisy oraz ich zawartość objęte są ochroną wynikającą z ustawy prawo autorskie i prawa pokrewne. Kopiowanie i rozpowszechnianie, wykraczające poza własny użytek osobisty, może odbywać się tylko po uzyskaniu uprzedniej, pisemnej zgody NC i jedynie we wskazanym zakresie.” NC to „Niecowiedzy.pl Łukasz Szałkiewicz, właściciel serwisów”.
- „Serwis dostępny jest dla każdego użytkownika Internetu, przy czym dostęp do pewnych części lub informacji może być odpłatny.” Część haseł jest płatna, abonament od 10 zł miesięcznie.
- `robots.txt` nie blokuje `/slowo/`. Nie ma `/.well-known/tdmrep.json` (404) ani meta TDM.
- Nie ma API ani eksportu haseł. Wyszukiwarka działa przez `GET /wyszukiwarka/wyszukaj/?q=`, a mapy witryny w `ds-sitemap-words-*.xml.gz` (27 plików, 68 816 haseł).

## Tezaurus DS (wolna licencja)
- https://dobryslownik.pl/pobierz/: nowe wersje wychodzą co trzy miesiące. Ostatnia wersja jest z 1 października 2026.
- `thesaurus.txt-latest.gz` (982 435 B, SHA256 `77d5e9fb…7437a`), nagłówek: „Copyright (C) 2004-2026dobryslownik.pl … under the terms of the GNU General Public License … version 2 … or (at your option) any later version.”
- `pl-dict-latest.oxt` (SHA256 `b456df80…81b5`), README_pl: „Słownik synonimów … Copyright (C) 2014-2026 Dobry słownik … Copyright (C) 2004-2014 Marcin Miłkowski … Licencja: LGPL 2.1.”
- Wulwa jest w wierszach 31117 i 36853–36854 tezaurusu 2026-10-01. W wersji 1.5 z 2008 r. (sourceforge, SHA256 `7217771e…1445`) nie ma ani wulwy, ani sromu.
- Pomiar: tezaurus ma 30 941 haseł, z tego 27 765 jednowyrazowych małą literą. **1761 nie ma jako lematu w SGJP 20261018, a 1390 nie ma nawet jako formy.** Wśród nich jest 270 feminatywów na `-lożka` (np. kardiolożka, mikrobiolożka, chirurżka) oraz wulwa i ministra. Lista: `scratchpad/potoczne/swiadoma/thes-not-in-sgjp.txt`.

## Kontrole w DS (wyszukiwarka, 2026-11-03; `lastmod` i id z mapy witryny)
| słowo | DS | lastmod | id |
|---|---|---|---|
| wulwa | tak | 2024-03-03 | 226245 |
| cringe (+ cringe'owy, krindż, krindżowy) | tak | 2024-12-07 | 225668 |
| boomer | tak | 2022-04-01 | 225516 |
| ghosting | **nie** | — | — |
| hejt (kontrola +) | tak | 2018-09-11 | 219205 |
| lockdown (kontrola +) | tak | 2020-10-09 | 224893 |
| antyszczepionkowiec (kontrola +) | tak | 2019-06-15 | 223795 |

Identyfikatory rosną z czasem (lockdown 2020 < boomer < wulwa 2024 < ministra < kardiolożka 2025), więc id przybliża datę dodania hasła. `lastmod` oznacza ostatnią zmianę.

## DS a SGJP 20261018 (pomiar lokalny)
- Hasła z map witryny: 68 816, z tego 45 011 jednowyrazowych małą literą. **5448 nie ma w SGJP ani jako lematu, ani jako formy**, w tym 931 z id ≥ 226000 (z grubsza od 2024) i 644 podobne do feminatywów (`-ka`, `-yni`, `-ini`).
- Najnowsze przykłady: ziomalka, zoofilka, zipować, paywall, content, brejk, mansplaining, hipergamia, handpan, whatsappowy, enoturystyka, wiceministerka, bakława.
- Plik: `scratchpad/potoczne/swiadoma/ds-not-in-sgjp-forms.json` (słowo, id, lastmod). Tylko lokalnie.

## Ocena
| zasób | licencja | ocena |
|---|---|---|
| hasła DS (strona) | wszystkie prawa zastrzeżone, część płatna | **tylko dowód ręczny** |
| tezaurus DS (txt/oxt) | GPL-2.0+ / LGPL 2.1 | **ALLOWED** (sygnał lokalny, atrybucja); import listy **do decyzji** |
| `pl_PL.dic` w oxt | GPL/LGPL/MPL/CC-SA, z 2008 r. | **odpada** (ryzyko SJP.pl, poza zakresem) |
| lista haseł z mapy witryny | brak licencji (baza danych) | **do decyzji** (sui generis / TDM; zob. `ccrawl`) |

Dane: `scratchpad/potoczne/swiadoma/dl-ds/`, skrypty: `scratchpad/potoczne/swiadoma/scripts/`.
