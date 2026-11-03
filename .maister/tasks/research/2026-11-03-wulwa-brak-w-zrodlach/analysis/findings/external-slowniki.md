# external: słowniki online i poradnie („wulwa”)

## TL;DR
- „wulwa” ma tylko SJP.pl. Nie ma jej w SGJP online, WSJP PAN, SJP PWN, u Doroszewskiego ani w Słowosieci 5.0 online. Każdy z tych źródeł ma za to „srom” (kontrola dodatnia).
- SJP.pl opiera hasło na słowniku turniejowym innej gry słownej (pole „występowanie”), a nie na słowniku ogólnym. Kwalifikator: „w medycynie: srom kobiecy”.
- Słowosieć 5.0 (nowsza niż nasz zrzut 4.5) dalej nie ma „wulwa”. Ma „wulwodynia” (rejestr SPECJ.) i „srom 2” bez synonimu „wulwa”.
- Poradnie PWN i RJP nie mają porady o „wulwa” ani „vulva”.

## Kluczowe decyzje
- Wszystkie odczyty 2026-11-03. SGJP online i Słowosieć sprawdzałem przez ich własne endpointy wyszukiwania (te same, których używa strona), a nie tylko przez HTML.
- Pole „występowanie” z SJP.pl opisuję bez nazwy gry (zasada projektu).

## Otwarte pytania
- SGJP online nie znajduje też nazwiska „Wulw”, choć lokalny eksport sgjp-20260823 je ma (patrz `local`). Słownik nazwisk w wersji online może być niewidoczny albo starszy. Ma to znaczenie tylko dla porównania wersji, nie dla „wulwa”.
- Kiedy hasło „wulwa” trafiło do SJP.pl, nie wiadomo. Pierwszy komentarz pochodzi z 2020-07-29, ostatnia aktualizacja z 2025-12-17. Historii zmian strona nie pokazuje.

## Wyniki

| Źródło | URL (odczyt 2026-11-03) | „wulwa” | Kontrola dodatnia |
|---|---|---|---|
| SJP.pl | https://sjp.pl/wulwa | **jest**: „dopuszczalne w grach”, pełna odmiana (wulwą, wulwę, wulwie, wulwo, wulwy, wulwach, wulwami, wulwom, wulw), „aktualizacja 2025-12-17, tevex”, znaczenie „w medycynie: srom kobiecy”; „występowanie”: słownik turniejowy innej gry słownej | https://sjp.pl/srom: jest, „występowanie”: *Słownik ortograficzny … Muza SA 2001–2006, T. Karpowicz* |
| SJP.pl | https://sjp.pl/vulva | brak (HTTP 404) | https://sjp.pl/wulwodynia: jest (źródło jak przy „wulwa”) |
| SGJP online (wyd. IV) | `https://sgjp.pl/edycja/ajax/search-by-form/?exponent="wulwa"` | `rows: []`. Puste też dla wulwy, wulwie, wulwę, vulva, wulwodynia, Wulw/wulw (również ze słownikami nazwisk i miejscowości) | srom (m3, id 2438), wagina (f, id 72657), łechtaczka (f, id 7093), moszna (f, id 8456), Kowalski (m1) |
| WSJP PAN | https://wsjp.pl/szukaj/podstawowe/wyniki?szukaj=wulwa | „nie znaleziono”, „Czy chodziło Ci o: bulwa”. Wulwodynia: nie znaleziono | srom: 2 pozycje (srom, sromy). Wagina: pełne hasło z odmianą i chronologizacją 1970 |
| SJP PWN | https://sjp.pwn.pl/szukaj/wulwa.html | „Nie znaleziono … Czy chodziło Ci o? bulwa, ulwa”. Wulwodynia: HTTP 404 | srom: «zewnętrzne narządy płciowe kobiet i samic ssaków», odmiana „-mu, -mie; -mów” |
| SJP PWN „vulva” | https://sjp.pwn.pl/szukaj/vulva.html | strona istnieje, sekcja „znaczenie, definicja” jest **pusta**; jedyny link to porada | — |
| Doroszewski (teraz https://sjp.pwn.pl/doroszewski/…) | lista `…/doroszewski/lista/wul` oraz kolejne ID: 5518882 „wulkanowy” → 5518883 „wundtysta” | brak (w alfabecie nie ma nic między wulkanowy a wundtysta). Stary adres doroszewski.pwn.pl daje 403/404 | srom: `…/doroszewski/srom;5500447` |
| Słowosieć online, ver. 5.0 | `https://slowosiec.pl/api/searchbar?q=wulwa` | `[]`. „wulw” i „wulwo” zwracają tylko „wulwodynia 1”. „vulva” zwraca tylko angielskie „vulva 1” (PWN 3.1) | srom 1 (DAW., „wstyd”), srom 2, sromowy itd. |
| Słowosieć: srom 2 | https://slowosiec.pl/pl/sense/d5908cf0-aac4-11ed-aae5-0242ac130002 | brak „wulwa” w synsecie. Domena BODY PART, rejestr **KSIĄŻK.**, def. „zewnętrzna część żeńskiego układu płciowego”; synonim międzyrejestrowy: tylko wulgaryzm potoczny | — |
| Słowosieć: wulwodynia 1 | https://slowosiec.pl/pl/sense/f301e04d-aac4-11ed-aae5-0242ac130002 | rejestr **SPECJ.**, bez relacji do „srom”. Definicja dosłownie zgodna z komentarzem pod sjp.pl/wulwodynia z 2009-08-13 | — |
| Poradnia PWN | https://sjp.pwn.pl/poradnia/szukaj/wulwa.html | HTTP 404, brak wyników | „srom”: 1 porada (etymologia, 2012) |
| Poradnia PWN „vulva” | https://sjp.pwn.pl/poradnia/szukaj/vulva.html | 1 wynik, nie o pisowni: porada „pitolenie o Szopenie” (2008) cytuje *Etymologiczny słownik* Bańkowskiego: „pitula vulva”. Tu „vulva” to łacińska glosa | — |
| RJP PAN | https://rjp.pan.pl/?s=wulwa (również ?s=vulva, ?s=srom) | „Nie znaleziono postów” | ?s=ortografia: wiele porad (wyszukiwarka działa) |

## Wnioski cząstkowe (dla syntezy)
- Słowniki normatywne i opisowe (PWN, Doroszewski, WSJP) nie notują „wulwa”. SGJP opiera się w dużej mierze na takich źródłach (patrz `docs`), więc brak w SGJP zgadza się z brakiem w ogólnej leksykografii.
- Jedynym źródłem leksykograficznym jest słownik turniejowy innej gry (wg SJP.pl). Tego samego źródła i podobnej daty dotyczą „wulwa” i „wulwodynia”.
- Pisownia: żaden słownik nie notuje „vulva” jako polskiego hasła, a poradnie milczą. Kwestia pisowni nie tłumaczy więc braku. Nie ma też wariantu, pod którym SGJP miałby hasło.
