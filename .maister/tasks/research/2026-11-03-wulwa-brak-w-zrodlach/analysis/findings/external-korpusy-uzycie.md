# external: NKJP online i użycie medyczne („wulwa”)

## TL;DR
- W pełnym NKJP (PELCRA, 1,52 mld słów) rzeczownika „wulwa” w znaczeniu „srom” jest **0** wystąpień. Wszystkie 5 trafień formy „wulwa” to dopełniacz nazwiska Wulw. Pozostałe formy (wulwy, wulwie, wulwę, wulwą, wulwo, wulwach, wulwami, wulwom) mają po 0 trafień.
- Lematyzator PELCRA nie zna lematu „wulwa”: zapytanie `wulwa**` zwraca pusty wynik, a `srom**` daje 478 akapitów.
- „vulva” ma 10 akapitów (cytaty, hasła, glosa), wulwodynia 1, wulwektomia 1; wszystkie trafienia pochodzą z Wikipedii.
- W sieci „wulwy/wulwę” pojawia się w poradnikach z lat 2020+ (np. leki.pl 2025). Teksty lekarzy (mp.pl) i hasła medyczne używają „srom/sromu”, a z rodziny wulw- tylko „wulwodynia”.

## Kluczowe decyzje
- PELCRA odpytywałem przez `NKJPSpanSearch` z poziomu strony (fetch w przeglądarce, ten sam URL co formularz), bo samo curl dawało HTTP 500 (NPE). Podkorpusy: `balanced` (240 mln) i `---` = cały (1,52 mld). Wielkość liter nie jest rozróżniana.
- Konkordancje czytałem ręcznie, żeby oddzielić nazwisko od rzeczownika.

## Otwarte pytania
- Wyszukiwarka sieciowa nie mierzy częstości. Liczby dla stron internetowych to zliczenia na kilku wybranych stronach, a nie frekwencja.
- Poliqarp (nkjp.pl/poliqarp) nie był potrzebny, bo PELCRA dała spójny wynik. Nie sprawdzałem go.

## NKJP – PELCRA (https://pelcra-nkjp.clarin-pl.eu/, odczyt 2026-11-03)

| Zapytanie | Zrównoważony (240 192 461 sł.) | Cały (1 524 696 745 sł.) | Uwagi |
|---|---|---|---|
| `wulwa` | 2 | 5 | wszystkie 5 trafień to nazwisko: „Jana Wulwa”, „Marcina Wulwa”, „Roberta Wulwa”, „Macieja Wulwa” (Słowo Polskie, Dziennik Polski) |
| `wulwa**` (lemat) | pusto | pusto | brak lematu w analizatorze |
| wulwy / wulwie / wulwę / wulwą / wulwo / wulwach / wulwami / wulwom | 0 | 0 | — |
| `wulw` | 4 | 230 | nazwisko (relacje sportowe, Nafta/Nafciarz Bóbrka; „Jan Wulw”) |
| `vulva` | 2 | 10 | „vulva si!” (GW), cytat z kroniki, symbolika („But występuje jako vulva”), Usenet, Wikipedia (glosa „pizda- vulva, czyli srom”) |
| `vulvy` / `vulvę` | 0 / – | 1 / 1 | Usenet; proza („Znak Anny”) |
| `wulwodynia` / `wulwodynii` | – | 1 / 0 | Wikipedia (lista przyczyn bólu) |
| `wulwodynia**` | pusto | pusto | brak lematu |
| `wulwektomia` | – | 1 | Wikipedia |
| **kontrola** `srom` | 44 | 204 | — |
| **kontrola** `srom**` | 103 | 478 | — |
| `sromu` | – | 231 | — |
| `wagina**` | 124 | 355 | — |
| `łechtaczka**` | 233 | 723 | — |

## Użycie medyczne i poradnikowe (odczyt 2026-11-03; zliczenia słów na stronie)

| Strona | wulwa (wszystkie formy) | srom (formy) | wulwodyni* |
|---|---|---|---|
| leki.pl „Jak opiekować się pacjentką z przewlekłym bólem wulwy” https://leki.pl/?p=565385 (opublikowano 2025-09-15) | 10 (wulwy 7, wulwę 3) | sromu 12 | 37 |
| leki.pl „Kompleksowy przewodnik po wulwodynii” https://leki.pl/?p=565364 | 1 (wulwy) | 27 | 6 |
| mp.pl (Medycyna Praktyczna) „Intymny ból, czyli wulwodynia” https://www.mp.pl/pacjent/ginekologia/aktualnosci/318613,intymny-bol-czyli-wulwodynia | 0 | sromu 26 („choroby sromu”) | 7 |
| gemini.pl „Wulwodynia – cierpi na nią aż 16% kobiet” https://gemini.pl/poradnik/artykul/wulwodynia-cierpi-na-nia-az-16-kobiet/ | 0 (vulva 1) | 8 | 5 |

Wyszukiwanie „rak wulwy” / „choroby wulwy” / „zdrowie wulwy” nie dało żadnego tekstu z tymi frazami w nagłówku. Wyniki prowadziły do tekstów o wulwodynii; literatura fachowa (Ginekologia Praktyczna, Seksuologia Polska, Varia Medica) w tytułach używa „srom” i „wulwodynia”.

## Wnioski cząstkowe (dla syntezy)
- Brak w SGJP, KWJP i Słowosieci zgadza się z frekwencją w NKJP, która wynosi **0** dla rzeczownika (nie licząc nazwiska). Hipoteza „niska frekwencja / brak poświadczeń korpusowych” ma mocne oparcie.
- Polska medycyna mówi „srom”. „Wulwa” to świeża kalka z ang. *vulva* w poradnikach internetowych, a „wulwodynia” przyszła razem z nazwą choroby. Wyjaśnia to, czemu Słowosieć ma „wulwodynia” (SPECJ.), a „wulwa” nie.
