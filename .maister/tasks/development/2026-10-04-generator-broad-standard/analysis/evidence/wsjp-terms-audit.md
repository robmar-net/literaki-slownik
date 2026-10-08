# WSJP PAN: warunki użycia jako źródła (odczyt 2026-10-08)

## TL;DR
WSJP PAN nie publikuje licencji otwartej ani warunków ponownego użycia danych. Serwis podaje tylko „Copyright© Instytut Języka Polskiego PAN”. Nie udostępnia danych do pobrania ani API dla osób trzecich, a `robots.txt` blokuje pobieranie haseł i wyszukiwanie oraz narzuca 5 minut odstępu między żądaniami.

Hurtowe użycie WSJP jako źródła słów nie ma więc podstawy. Specyfikacja v3 (§149) wymaga przed takim użyciem ustalenia uprawnień.

Krążąca informacja, że WSJP jest na licencji CC BY-SA 4.0, jest błędna. To licencja stopek serwisu gov.pl i Wikipedii, a nie WSJP.

## Ustalenia
| co | wynik | źródło |
|---|---|---|
| licencja treści | brak; stopka każdej strony: „Copyright© Instytut Języka Polskiego PAN” | wsjp.pl, `/page/autorzy`, `/page/historia`, `/page/podstawy_naukowe`, `/page/polityka_prywatnosci`, `/jak_korzystac` |
| metadane strony | Dublin Core bez `rights`/`license` (`DC.type`, `DC.title`, `DC.format`, `DC.publisher`) | `https://wsjp.pl/` |
| `robots.txt` | `Disallow: /pobierz_hasla`, `Disallow: /szukaj`, `Disallow: /autocomplete`, `Crawl-delay: 300` | `https://wsjp.pl/robots.txt` |
| zasady opracowania (wersja 2026, 101 s.) | słownik „dostępny bezpłatnie w Internecie”; korzystanie przez wyszukiwanie; brak licencji, eksportu i formatów danych | `https://pliki.wsjp.pl/zasady_opracowania_wsjp.pdf` |
| monografia „Geneza, koncepcja, zasady opracowania” (2018) | „© Copyright by Instytut Języka Polskiego PAN Kraków 2018”; brak warunków ponownego użycia danych | RCIN, `Content/68631` |
| „CC BY-SA 4.0” w wynikach wyszukiwania | stopka serwisu gov.pl („Treści tekstowe publikowane w serwisie…”), nie WSJP | gov.pl, artykuł MNiSW z 2018-11-08 |
| „CC BY-SA” w Wikipedii | licencja samej Wikipedii | pl.wikipedia.org |
| CLARIN-PL, API | nie znaleziono zbioru WSJP ani publicznego API | wyszukiwanie 2026-10-08 |

## Wnioski
- **Bezpłatny dostęp to nie licencja na dane.** WSJP jest chroniony prawem autorskim, a jako baza danych także prawem sui generis (ustawa o ochronie baz danych). Pobranie istotnej części albo systematyczne pobieranie nieistotnych części wymaga zgody producenta.
- **Dopuszczalne bez zgody:** pojedynczy odczyt hasła przez człowieka przy konkretnej decyzji, z cytatem i linkiem. Tak użyto WSJP w PAN-3 (2 obserwacje). Masowe sprawdzanie tysięcy słów, nawet ręczne, zbliża się do systematycznego pobierania.
- **Dla luki „pospolite homonimy nazw własnych”** (do około 8,5 tys. słów, np. `janusz`, `kraków` od `krak`) WSJP byłby właściwym dowodem, ale bez zgody IJP PAN nie może być źródłem hurtowym.

## Opcje (decyzja właściciela)
1. **Zapytać IJP PAN o zgodę albo udostępnienie danych.** To wymaga odstępstwa od zasady „nie kontaktujemy się z innymi grupami”. Taki wyjątek może ustanowić tylko właściciel.
2. **Ręczny, ograniczony przegląd:** najczęstsze w KWJP słowa z tej kategorii, np. pierwsze 100–200, sprawdzone pojedynczo w WSJP. Każda decyzja z cytatem i linkiem, bez zapisywania treści WSJP.
3. **Inne źródło z otwartą licencją,** np. Wikisłownik (CC BY-SA), dziś odłożony. Wymaga audytu jakości i warunków.
4. **Znane ograniczenie pierwszego wydania:** opis w `known_limitations` i na wiki.
