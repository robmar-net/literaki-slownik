# neolog — przegląd źródeł i kontroli

## TL;DR
- Sprawdziłem 11 źródeł (odczyt 2026-11-03). Żadne źródło nowych słów nie ma licencji danych, która pozwala wciągnąć je do generatora.
- Jedyne `ALLOWED` to SGJP. Ma nowszy eksport 20261018, który dodaje 2 lematy względem 20260823. SGJP nie nadąża za nowymi słowami.
- Najlepsze dowody ręczne: OJ UW (2756 haseł, żywy, kryterium „po 2003”) i WSJP PAN (ma antyszczepionkowca i boomera, których SGJP nie ma).
- Wulwy nie ma w żadnym sprawdzonym źródle, a ghostingu w żadnym słowniku. Wniosek: nowe słowa trzeba wykrywać w korpusach (zbieracz `korpusy`) i decydować ręcznie z dowodem z OJ UW lub WSJP.

## Kluczowe decyzje
- Słowniki i obserwatoria są tylko krokiem „dowód do decyzji użytkownika”. Wejście do list idzie dalej przez `sgjp-supplement.tab`.
- Hejt pokazuje różnicę kryteriów: OJ UW odrzuca go jako „za stary” (sprzed 2003), choć dla nas to nowe słowo. Brak w OJ UW nie znaczy „nie jest nowy”.

## Otwarte pytania
- Czy podbić SGJP do 20261018? Zysk: `muralista`, `muralistka`. To decyzja dla `projekt` i użytkownika.
- Licencja wpisów OJ UW i WSJP jest nieustalona. Ustalić ją można tylko kontaktem, a ten jest zabroniony. Zostaje `BLOCKED`.

## Tabela źródeł

| # | Źródło | Prowadzący | Licencja danych | Aktualność | Pokrycie | Pobieranie | Ocena |
|---|---|---|---|---|---|---|---|
| 1 | Słownik neologizmów OJ UW | UW, IJP UW | brak; regulamin § 7: „przedmiotem praw autorskich” | ostatnie hasło 2026-10-30; 2026: 280 haseł | 2756 haseł + 97 odrzuceń; jednostki po 2003 | brak eksportu; REST WP publiczne (slugi, daty) | tylko dowód ręczny / `BLOCKED` jako wejście |
| 2 | Stara witryna OJ UW (nowewyrazy.uw.edu.pl) | UW | brak; „Copyright © Uniwersytet Warszawski” | zamrożona 31.10.2021 | ~3547 haseł | HTML | tylko dowód ręczny (archiwum) |
| 3 | SGJP eksport 20261018 | zespół SGJP | BSD-2-Clause | 18.10.2026; 18 eksportów w 2026 | 348 420 lematów (+2) | tak, 41 MB | **`ALLOWED`** (`lexical`) |
| 4 | WSJP PAN | IJP PAN | brak tekstu; „Copyright© IJP PAN” | ciągła; 100 tys. haseł 01.2026 | ogólny, z leksyką XXI w. | brak oficjalnego | tylko dowód ręczny |
| 5 | SJP PWN + WSO | PWN | „jedynie w zakresie własnego użytku osobistego” | ciągła | ogólny | nie | `BLOCKED`; cytat ręczny |
| 6 | Słowosieć 5.0 | PWr / CLARIN-PL | plWordNet License (Princeton-like) | 5.0 (2025) | 196 348 lematów | pełne zrzuty po formularzu | `BLOCKED` (wymaga kontaktu); 4.5 wg ADR-011 |
| 7 | Młodzieżowe Słowo Roku | PWN | brak | rocznie od 2016 | 15–20 słów/rok | nie | tylko dowód ręczny (sygnał popularności) |
| 8 | Słowo Roku UW i FJP | FJP, UW | brak | rocznie (15. edycja 2025) | ~21 słów/rok | nie | tylko dowód ręczny, mała przydatność |
| 9 | Rada Języka Polskiego | RJP PAN | brak | reforma pisowni 2026 | normy, nie lista | nie | nie jest źródłem nowych słów |
| 10 | Miejski Słownik Slangu | społeczność | nie znaleziono | ciągła | slang | nie | tylko kontrola |
| 11 | NeoN (IPI PAN) | IPI PAN | artykuł CC BY 4.0; dane niedostępne | 2025 | ~1056 kandydatów (RSS, 2 mies.) | nie | metoda, nie dane |

Szczegóły i cytaty: `neolog-ojuw.md`, `neolog-slowniki.md`, `neolog-inne.md`.

## Kontrole (odczyt 2026-11-03)
Oznaczenia: + jest, − brak, n nie da się sprawdzić, NW = negatywna weryfikacja OJ UW.

| Słowo | OJ UW nowa | OJ UW stara | SGJP 20261018 | WSJP | PWN | Miejski | MSR |
|---|---|---|---|---|---|---|---|
| hejt | − (NW) | + | + | + | + | + | n |
| lockdown | + | + | + | + | + (WSO) | + | n |
| covidowy | − | + | + | + | + (WSO) | − | n |
| influencerka | − (`influencer` +) | + | + | − | n | − | n |
| antyszczepionkowiec | + | − | − | + | + | − | n |
| boomer | − | „ok boomer” | − (`bumer`) | + | + (WSO) | + | n |
| ghosting | − | − | − | − | − | − | n |
| cringe | `cringe-owy` | − | − | − | − (ciekawostka) | + | + (finał 2024) |
| wulwa | − | − | − | − | − | − | n |

Kontrola dodatnia przy każdym „−”: w OJ UW lockdown i antyszczepionkowiec, w SGJP hejt, w WSJP hejt i lockdown, w PWN hejt, w Miejskim hejt i lockdown.
Słowosieć 5.0 i NeoN: kontroli nie da się sprawdzić (SPA bez publicznego API; brak danych).

## Co z tego wynika dla metody
- Luki SGJP, które słowniki naukowe już mają: **antyszczepionkowiec** (OJ UW, WSJP, PWN) i **boomer** (WSJP, PWN WSO). To kandydaci, dla których dowód ręczny istnieje dziś.
- **ghosting** i **wulwa** nie ma w żadnym słowniku. Tu jedynym dowodem będzie korpus.
- **cringe** jest tylko w źródłach popularnych (Miejski, MSR) i jako `cringe-owy` w OJ UW.
- Progi NeoN (DF > 5, ≥ 5 wystąpień małą literą i nie jako nazwa własna) są zgodne z progiem 5 dla KWJP w `sources.json`.

## Zgodność z zasadami badania
- Bez kontaktu: nie wysłałem formularzy (OJ UW „Zgłoś hasło”, Słowosieć „Zgłoszenie dostępu”), nie zakładałem kont.
- SJP.pl, PoliMorf, Wikisłownik: nie otwierane, nie pobierane (`polimorf-20261018.tab.gz` celowo pominięty).
- WSJP: `curl` dostał 403; nie obchodziłem blokady, odczyt przez WebFetch.
- Pobrania tylko w scratchpadzie `nowe-slowa/neolog/`: 2 eksporty SGJP (~41 MB każdy), JSON-y slugów OJ UW, strony HTML. Nic > 2 GB.
