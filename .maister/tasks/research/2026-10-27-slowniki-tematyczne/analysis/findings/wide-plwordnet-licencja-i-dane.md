# Słowosieć (plWordNet): licencja i dane o dziedzinie

## TL;DR
Licencja jest jasna i liberalna: wzorowana na licencji Princeton WordNet, pozwala na każde użycie i rozpowszechnianie, także zmienionych danych. Warunek: przy każdej kopii trzeba podać notę copyright i zastrzeżenie.
Publicznie do pobrania są wydania 4.2 (2022, dane z 2020) i 4.5 (2021). Wydanie 5.0 udostępniają tylko po zgłoszeniu przez formularz, więc dla nas jest niedostępne.
Słowosieć nie ma dziedzin tematycznych przy słowach. Są tylko „domeny leksykograficzne” (np. `zw`, `czy`, `wytw`), czyli klasy ogólne, oraz kwalifikatory rejestru (`og.`, `specj.`).
Do tematu dochodzimy przez drzewo hiponimii (np. pod `statek 1`) albo przez domeny tematyczne Princeton WordNet po mapowaniu. Pomiar: `wide-plwordnet-pomiar.md`.

## Key Decisions
- Pobrałem dwa wydania: 4.2 i 4.5. Licencja jest jasna i oba pliki mają mniej niż 500 MB. Główne wyniki liczę na 4.5, bo to najnowsze publiczne wydanie.
- Wydania 5.0 nie zamawiam. Formularz oznacza kontakt z autorami, a AGENTS.md go zabrania.
- Rozpakowane zrzuty SQL (4,9 GB) usunąłem. Zostały zipy i bazy SQLite z wybranymi tabelami. Wszystko leży w `data/work/plwordnet/` (gitignore, sprawdzone przez `git check-ignore`).

## Open Questions / Risks
- Strona licencji wskazana w repozytorium (`http://clarin-pl.eu/en/licenses/plwordnet-2/`) zwraca 404. Tekst licencji wziąłem ze strony projektu (https://slowosiec.pl/pl/about#license). Tam jest nota „plWordNet 4.2 © 2020”, nie dla 4.5. Zipy nie mają pliku LICENSE, choć licencja mówi, że „is available as the file LICENSE in any downloaded version”.
- Stopka strony ma „CC BY-SA 4.0”. Według mnie dotyczy treści serwisu, nie bazy. Dla bazy repozytorium podaje licencję „plWordNet”. To moja interpretacja.
- Czy lista słów wybranych z bazy to „modyfikacja bazy”? Najbezpieczniej przyjąć, że tak, i dołączyć notę copyright i zastrzeżenie do `ATTRIBUTIONS.md` pakietu. Nazwy Politechniki Wrocławskiej nie wolno używać w reklamie.
- Zrzut 4.5 to cała robocza baza edytorska. Ma pola `owner` z imionami i nazwiskami redaktorów i tabelę `iplog`. Surowego zrzutu nie publikujemy. Publikować możemy tylko listy lematów.

## Licencja (dostęp 2026-10-27)
- Repozytorium CLARIN-PL, rekord 4.2: https://clarin-pl.eu/dspace/handle/11321/891 — licencja „plWordNet”, status „Publicznie dostępny”, plik `plwordnet_4_2_CLARIN_BIZ_START_with_PWN3.1.zip`, 407,23 MB, MD5 `7defd283…759844`.
- Rekord 4.5: https://clarin-pl.eu/dspace/handle/11321/834 — ta sama licencja, plik `wordnet_work_4_5.zip`, 444 MB, MD5 `08ed723f…ba6f`.
- Lista rekordów (`/server/api/discover/search/objects?query=plWordNet`): najnowsze dane to 4.5 (2021-07-23). Dla 5.0 są tylko artykuły, bez danych.
- Tekst licencji (https://slowosiec.pl/pl/about, sekcja „Licencja”), cytat:
  > „Decyzją władz uczelni Słowosieć jest dostępna bezpłatnie do powszechnego (również komercyjnego) użytku w oparciu o licencję wzorowaną na licencji Princeton WordNet.”
  > „permission to use, copy, modify, distribute, and public expose this software and database (including data getting) and its documentation for any purpose and without fee or royalty is hereby granted, provided that you agree to comply with the following copyright notice and statements, including the disclaimer, and that the same appear on ALL copies of the software, database and documentation, including modifications which you make for internal use or for wider distribution. plWordNet 4.2 © 2020 by Wrocław University of Technology. All rights reserved.”
  > „The name of Wrocław University of Technology may not be used in advertising or publicity pertaining to distribution of the software, the database or both.”
- Strona „Dla badaczy” (https://slowosiec.pl/pl/experts): „Aktualna wersja 5.0”. „Pełne zrzuty bazy, dodatkowe listy i korpus przykładów udostępniamy po weryfikacji zgłoszenia.”
- Wniosek: dla publicznego projektu listy pochodne są dozwolone. Warunek to nota i zastrzeżenie przy każdej kopii. Pod tym względem licencja jest podobna do BSD-2 dla SGJP. **Pewność: wysoka** co do treści, **średnia** co do wersji (nota mówi o 4.2).

## Pobranie
```
curl -o plwordnet_4_2_CLARIN_BIZ_START_with_PWN3.1.zip https://clarin-pl.eu/server/api/core/bitstreams/5995f687-4fa7-43d6-bc49-9e96aabbc85e/content
curl -o wordnet_work_4_5.zip https://clarin-pl.eu/server/api/core/bitstreams/3197cd0f-bb4e-41ba-93e0-eec99ab8d519/content
```
- Link `…/bitstreams/<id>/download` zwraca stronę HTML. Działa tylko link `/server/api/core/bitstreams/<id>/content`.
- Sumy MD5 zgadzają się z rekordami. SHA-256: 4.2 `9f23489a…6312`, 4.5 `30edc5f8…dcbc`.
- Każdy zip zawiera jeden zrzut MySQL: 4.2 ma 2,30 GB, 4.5 ma 2,63 GB. Nie ma w nich pliku LICENSE.
- Skrypt `to_sqlite.py` przenosi do SQLite 7 tabel. Trwa to około 14 s na wydanie. Wynik: `plwn42.sqlite` (238 MB) i `plwn45.sqlite` (226 MB).
- Liczba jednostek w 4.5: 514 016, w tym 295 419 polskich (`pos` 1–4) i 194 787 polskich lematów. Synsetów jest 354 316, relacji między synsetami 1 491 277. Baza zawiera też Princeton WordNet 3.1 (`pos` 5–8) i mapowanie na niego.

## Jaka informacja o dziedzinie jest w bazie
| Pole | Co to jest | Czy daje temat? |
|---|---|---|
| `lexicalunit.domain` (54 wartości, `tmp_domains`) | domeny leksykograficzne: `activity`, `artefact`, `plant`, `animal`, `quantity`, `shape`… (skróty w `unitsstr`: `czy`, `wytw`, `rsl`, `zw`, `il`, `ksz`, `umy`) | nie: to klasy ogólne, bez pól „morze”, „rolnictwo”, „matematyka” |
| `##K:` w `lexicalunit.comment` | rejestr: `og.` 92 284, `specj.` 70 212, `książk.`, `pot.`, `daw.`… (26 wartości, plWN 4.2) | nie: `specj.` mówi tylko, że słowo jest fachowe, nie z jakiej dziedziny |
| `##D:` definicja | tekst, np. „w geometrii…”, „maszyna używana w rolnictwie” | słabo: „w matematyce” 117 LU, „w rolnictwie” 49, „w żeglarstwie” 35 (4.2) |
| hiponimia (rel. 11, PARENT = hiperonim) | drzewo pojęć, np. `jacht 1` < `łódź 2` | tak, przez wybór korzeni |
| część / miejsce (rel. 25, 27), fuzzynimia (108), określnik (146) | np. `statek 1` → `kotwica 2`, `ster 2`, `kambuz`, `cumować` | tak, poszerzają drzewo o części i czynności |
| domeny PWN (rel. 183 `Domain_of_synset_-_TOPIC`, 6752 relacji) | np. `seafaring`, `ship`, `farming`, `mathematics`, `geometry` | tak, ale tylko przez mapowanie plWN↔PWN (rel. 208/209, 3005/3006, 228/229, 210) |

- Skrót `mat.` ani `żegl.` nie pojawia się na początku definicji (0 i 1 LU w 4.2). Słowosieć nie przejęła kwalifikatorów dziedzin w stylu SGJP. **Pewność: wysoka.**
- Domeny PWN są skąpe: `seafaring` ma 36 członków, `farming` 18, `mathematics` 157, `geometry` 19.

## Źródła
- https://clarin-pl.eu/dspace/handle/11321/891, https://clarin-pl.eu/dspace/handle/11321/834, https://clarin-pl.eu/server/api/discover/search/objects?query=plWordNet&dsoType=ITEM
- https://slowosiec.pl/pl/about (sekcja „Licencja”), https://slowosiec.pl/pl/experts
- http://clarin-pl.eu/en/licenses/plwordnet-2/ (404; kopia z 2021 w https://web.archive.org/web/20210120010247/https://clarin-pl.eu/en/licenses/plwordnet-2/, nie czytałem jej w całości)
- Skrypty: `/private/tmp/claude-501/-Users-robmar-Projects-Literaki/7eed58b5-7e1f-4a3f-8359-d9bc24330c2b/scratchpad/plwn/to_sqlite.py`, `lib.py`
