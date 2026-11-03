# Obserwatorium Językowe UW — Słownik neologizmów polskich

## TL;DR
- Najlepsze naukowe źródło nowych słów: 2756 haseł, ostatnie z 30.10.2026. Słownik jest żywy (2026: 280 haseł).
- Licencji danych nie ma. Regulamin mówi tylko o prawie autorskim i o cytowaniu. Dla generatora: `BLOCKED` (brak licencji).
- Dobre jako ręczny dowód w decyzji użytkownika. Lista haseł jest czytelna przez publiczne REST API WordPressa, ale bez licencji nie wolno jej wciągać do list.
- Kontrole: lockdown i antyszczepionkowiec są. Hejt jest w „negatywnej weryfikacji” (za stary). Wulwy, ghostingu i boomera nie ma.

## Kluczowe decyzje
- Ocena: **tylko dowód ręczny**. Hasła OJ UW mogą być linkiem w karcie kandydata, nie wejściem `sources.json`.
- Kryterium OJ UW to „po 2003” i brak w 8 słownikach sprzed 2003. To inne kryterium niż „brak w SGJP”. Dlatego hejt odpada w OJ UW, choć jest nowy dla SGJP.

## Otwarte pytania
- Stara witryna (nowewyrazy.uw.edu.pl, 3547 linków haseł, do 2021) nie jest w pełni przeniesiona. Np. `hejt`, `covidowy`, `influencerka` są tylko w starej. Nie wiadomo, czy to celowe.
- REST API szuka słabo (wyszukiwanie `search=hejt` dało 0). Pełna lista slugów działa; wyszukiwarka witryny działa w JS.

## Prowadzący
- Uniwersytet Warszawski; od 10.2025 pracownia przy Instytucie Języka Polskiego UW, kier. dr Agata Hącia. Powstało w 2014 r. (Bańko, Burzyński, Czeszewski).
  Źródło: https://obserwatoriumjezykowe.uw.edu.pl/historia/ (odczyt 2026-11-03).
- Słownik społecznościowy: hasła zgłaszają użytkownicy, redaguje zespół.

## Kryteria haseł (cytat)
> „jednostka powinna mieć co najmniej 10 poświadczeń w co najmniej 5 powstałych po 2003 r. tekstach […] jednostka nie może występować w żadnym z ośmiu słowników diagnostycznych wydanych przed 2003 rokiem”

Źródło: https://obserwatoriumjezykowe.uw.edu.pl/czym-jest-slownik-neologizmow-polskich/ (odczyt 2026-11-03).

## Licencja i warunki (cytat dosłowny)
Regulamin (na stronie „Jak działamy”, w mocy od 1.06.2021), § 7:
> „1. Treści prezentowane w Serwisie, które stanowią utwory w rozumieniu ustawy z dnia 4 lutego 1994 r. o prawie autorskim i prawach pokrewnych, są przedmiotem praw autorskich.
> 2. Zaleca się cytowanie treści z Serwisu według następującego schematu: […]”

Stopka: „Copyright © 2021 Uniwersytet Warszawski”. Brak licencji CC, brak eksportu, brak zgody na hurtowe użycie. Pole wyszukiwarki „W informacjach o licencji” istnieje, ale w sprawdzonym haśle (`grazynokracja`) nie ma żadnej licencji.
Źródło: https://obserwatoriumjezykowe.uw.edu.pl/jak-dzialamy/ (odczyt 2026-11-03).

## Aktualność i rozmiar (pomiar 2026-11-03)
REST: `https://obserwatoriumjezykowe.uw.edu.pl/wp-json/wp/v2/entry` → `X-WP-Total: 2756`.

| Rok publikacji | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|
| Haseł | 975 | 568 | 477 | 276 | 178 | 280 |

(2021 to głównie migracja ze starej witryny; 1 wpis z 2012 i 1 z 2020.)
Ostatnie hasło: `grazynokracja`, opublikowane 2026-10-30 (zgłoszone 15.10.2026). Ostatnia modyfikacja: 2026-11-02.
„Negatywna weryfikacja” (`/wp-json/wp/v2/negver`): 97 wpisów, ostatni 2026-08-22.

Pobieranie: brak eksportu. Lista slugów i dat przez REST jest publiczna (pobrana do scratchpadu: `nowe-slowa/neolog/slugs.txt`). Hasło ma metadane: data zgłoszenia i opracowania, typ jednostki, rodzimość, nacechowanie.

## Kontrole (odczyt 2026-11-03)
Metoda: pełna lista slugów z REST (nowa witryna) + lista haseł starej witryny `nowewyrazy.uw.edu.pl/lista-hasel/wszystkie/wg-tytulu.html` + lista `negver`.

| Słowo | Nowa witryna | Stara witryna (do 2021) | Uwagi |
|---|---|---|---|
| hejt | brak hasła; **negatywna weryfikacja** | jest (`haslo/hejt.html`) | powód: „dużą liczbę poświadczeń […] sprzed 2003 r.” |
| lockdown | jest (2021-12-30) | jest | kontrola dodatnia |
| covidowy | brak (są `paszportcovidowy`, `antycovidowiec`) | jest | luka migracji |
| influencerka | brak (są `influencer` 2026-04-30, `patoinfluencerka`) | jest | luka migracji |
| antyszczepionkowiec | jest (2022-03-25) | brak | kontrola dodatnia |
| boomer | brak | jest „ok boomer” | — |
| ghosting | brak | brak | kontrola dodatnia: lockdown |
| cringe | jest jako `cringe-owy` (2021-12-17); `/hasla/cringe/` → 301 na `cringe-owy` | brak | tylko przymiotnik |
| wulwa | brak (też w `negver`) | brak | kontrola dodatnia: lockdown, antyszczepionkowiec |

Cytat powodu dla hejtu: https://obserwatoriumjezykowe.uw.edu.pl/negatywna-weryfikacja/hejt/ (odczyt 2026-11-03).

## Ocena zgodności
- **`BLOCKED` jako wejście generatora** — brak licencji danych; regulamin zastrzega prawa autorskie.
- **Dozwolone jako ręczny dowód** (link + data odczytu) w karcie kandydata. Nie kopiujemy definicji ani przykładów.
- Ryzyko SJP.pl: brak (źródło redagowane, własne kryteria).
