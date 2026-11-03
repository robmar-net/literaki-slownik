# Słowniki ogólne: SGJP online, WSJP PAN, PWN, Słowosieć 5.0

## TL;DR
- **SGJP ma nowszy eksport: 20261018** (BSD-2-Clause, jak dotąd). Względem 20260823 dodaje tylko 2 lematy (`muralista`, `muralistka`). Kontrole bez zmian.
- SGJP rośnie powoli i alfabetycznie (06→08.2026: +137 lematów, głównie na C–D). Nie łapie neologizmów szybko.
- WSJP PAN ma 100 tys. haseł (01.2026) i ma `antyszczepionkowiec` i `boomer`, których SGJP nie ma. Licencji nie ma → tylko dowód ręczny.
- PWN: regulamin pozwala tylko na „własny użytek osobisty” → `BLOCKED`, najwyżej dowód ręczny.
- Słowosieć 5.0: licencja jak dotąd (plWordNet License), ale pełne zrzuty dają „po weryfikacji zgłoszenia” (formularz) → poza zasadą „bez kontaktu”.

## Kluczowe decyzje
- SGJP 20261018 to jedyne źródło tu, które może wejść do `sources.json` bez nowej analizy licencji. Podbicie wersji to osobna decyzja (zysk: 2 lematy).
- WSJP to najlepszy *naukowy* dowód ręczny dla luk SGJP (antyszczepionkowiec, boomer), ale nie wejście.

## Otwarte pytania
- WSJP ma link `haslo/json` na stronie głównej. Nie badałem go: bez licencji i tak nie jest wejściem.
- Czy Słowosieć 5.0 da się pobrać bez formularza (np. stary kanał CLARIN-PL)? Nie potwierdzone.
- PWN `influencerka`: strona przekierowuje (307) i nie pokazuje treści hasła. Wynik nieustalony.

## 1. SGJP online i eksporty
- Prowadzący: zespół SGJP (Woliński, Saloni, Wołosz, Gruszczyński, Skowrońska, Bronk, Kieraś); „Wydanie IV online, Warszawa 2020”. https://sgjp.pl/leksemy/ (odczyt 2026-11-03).
- Eksporty: https://download.sgjp.pl/morfeusz/ (odczyt 2026-11-03). Katalogi wg roku: 2019–2024 po 1, 2025: 6, 2026: 18. Ostatni: `20261018/` (18-Oct-2026).
- Plik: `sgjp-20261018.tab.gz`, 42 691 269 B, sha256 `346bd7bc2695cb69c323de16c4c6d93afc514055fab96b458b8ead2523dae5be`, nagłówek `#!DICT-ID pl.sgjp.sgjp-2026.10.19`. Pobrany do scratchpadu `nowe-slowa/neolog/sgjp/`.
- Licencja (cytat z nagłówka pliku): „Copyright © 2007–2026 Marcin Woliński, Zbigniew Bronk, Włodzimierz Gruszczyński, Witold Kieraś, Zygmunt Saloni, Danuta Skowrońska, Robert Wołosz […] Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met: […]” — BSD-2-Clause, bez zmian.
- W tym samym katalogu jest `polimorf-20261018.tab.gz` — wyłączony, nie pobierany.

Pomiar (lemat = pole 2 do pierwszego `:`):

| Eksport | Lematy | Nowe vs poprzedni | Usunięte |
|---|---|---|---|
| 20260615 | 348 281 | — | — |
| 20260823 (lokalny cache) | 348 418 | +137 | 0 |
| 20261018 | 348 420 | +2 (`muralista`, `muralistka`; +23 wiersze) | 0 |

Nowe lematy 06→08 to przegląd alfabetyczny (np. `czterostrunność`, `debeściara`, `dekolonializm`, `dezinstytucjonalizacja`), nie lista neologizmów.

Kontrole w 20261018 = jak w 20260823: hejt, lockdown, covidowy, influencerka **są**; antyszczepionkowiec, boomer, ghosting, cringe, wulwa **brak** (jest `bumer`). Kontrola dodatnia: hejt.

Ocena: **`ALLOWED`** (rola `lexical`, jak dziś). Jako detektor nowych słów słaby: ~2–140 lematów na 2 miesiące.

## 2. WSJP PAN
- Prowadzący: Instytut Języka Polskiego PAN. Stopka: „Copyright© Instytut Języka Polskiego PAN”. https://wsjp.pl/ (odczyt 2026-11-03).
- Rozmiar: „zasób haseł przekroczył 90 tysięcy” (07.2024), „liczba opracowanych haseł osiągnęła 100 tysięcy” (01.2026). https://wsjp.pl/page/historia (odczyt 2026-11-03).
- Cadence: ciągła; sekcja „Ostatnio dodane hasła” bez dat (np. brudota, pojazdka, poraić).
- Licencja: brak tekstu licencji i warunków na stronie głównej i w „Historii”. Jest tylko polityka prywatności.
- Pobieranie: brak oficjalnego eksportu; aplikacje mobilne; link `haslo/json` bez opisu.
- Uwaga techniczna: zwykły `curl` dostaje 403; odczyt przez WebFetch. Nie obchodziłem blokady.
- Żmigrodzki (2025) opisuje WSJP jako źródło leksyki XXI w. z datowaniem haseł: https://krakow.pan.pl/images/2025.03.26_prof._P._Żmigrodzki.pdf (nie czytałem całości).

Kontrole (wyszukiwarka `https://wsjp.pl/szukaj/podstawowe/wyniki?szukaj=<słowo>`, odczyt 2026-11-03):

| hejt | lockdown | covidowy | influencerka | antyszczepionkowiec | boomer | ghosting | cringe | wulwa |
|---|---|---|---|---|---|---|---|---|
| jest | jest | jest | brak (też `influencer` brak) | **jest** (m1, pot.) | **jest** (m1, pogard., pokolenie wyżu) | brak | brak | brak |

Każde „brak” ma kontrolę dodatnią: hejt, lockdown. Ocena: **tylko dowód ręczny** (brak licencji; spec. §4.4: WSJP nie jest wejściem bez ustalenia praw).

## 3. PWN (sjp.pwn.pl)
- Prowadzący: Wydawnictwo Naukowe PWN. Stopka: „(©) 1997 - 2026 PWN”.
- Regulamin, cz. IV (cytat dosłowny): „4. Użytkownik Serwisów uprawniony jest do korzystania z materiałów umieszczonych w nich jedynie w zakresie własnego użytku osobistego. Wykorzystywanie tych materiałów w innym zakresie jest dopuszczalne wyłącznie na podstawie odpowiedniego upoważnienia udzielonego przez uprawnioną osobę lub w zakresie, w jakim powyższe dopuszczalne jest przez obowiązujące przepisy prawa.” https://sjp.pwn.pl/regulamin (odczyt 2026-11-03).
- Brak działu „nowe słowa” z danymi. Jest strona plebiscytu Młodzieżowe Słowo Roku (zob. `neolog-inne.md`).

Kontrole (`https://sjp.pwn.pl/szukaj/<słowo>.html`, odczyt 2026-11-03):

| Słowo | Wynik |
|---|---|
| hejt | jest (SJP PWN) |
| lockdown | jest (Wielki słownik ortograficzny) |
| covidowy | jest (WSO) |
| influencerka | nieustalone (307, brak treści) |
| antyszczepionkowiec | jest (SJP PWN, pot.) |
| boomer | jest (WSO, tylko pisownia) |
| ghosting | brak („Nie znaleziono żadnych wyników…”) |
| cringe | brak hasła; jest tylko „ciekawostka” |
| wulwa | brak („Nie znaleziono…”) |

Kontrola dodatnia: hejt. Ocena: **`BLOCKED`** jako wejście; ręczny dowód tylko w granicach prawa cytatu.

## 4. Słowosieć 5.0
- Prowadzący: Politechnika Wrocławska (CLARIN-PL). Nowa witryna: https://slowosiec.pl/pl (stare plwordnet.pwr.wroc.pl przekierowuje). „5.0 Aktualna wersja”, 196 348 lematów, ~297 tys. jednostek (statystyki z czerwca 2024).
- Licencja (cytat, https://slowosiec.pl/pl/about#license, odczyt 2026-11-03): „Decyzją władz uczelni Słowosieć jest dostępna bezpłatnie do powszechnego (również komercyjnego) użytku w oparciu o licencję wzorowaną na licencji Princeton WordNet. plWordNet License plWordNet® is unencumbered, and may be used in commercial applications in accordance with the following license agreement. […] plWordNet 4.2 © 2020 by Wrocław University of Technology.” Stopka witryny: „CC BY-SA 4.0” (to licencja strony, nie danych).
- Pobieranie: „Pełne zrzuty bazy, dodatkowe listy i korpus przykładów udostępniamy po weryfikacji zgłoszenia.” (https://slowosiec.pl/pl/experts, odczyt 2026-11-03) → wymaga formularza, czyli kontaktu. Zabronione zasadą badania.
- Artykuł 5.0: https://aclanthology.org/2025.gwc-1.19/ (CC BY 4.0).
- Kontrole: nie da się sprawdzić bez JS (aplikacja Nuxt, API niepubliczne w kodzie). Lokalna 4.5 mierzy zbieracz `projekt`.

Ocena: **`BLOCKED` dla 5.0** (dostęp przez formularz); 4.5 zostaje wg ADR-011.
