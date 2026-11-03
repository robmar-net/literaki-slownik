# Świadoma zmiana 04: kandydaci tej kategorii a SGJP 20261018

## TL;DR
- Sprawdziłem 33 paradygmaty w `sgjp-20261018.tab.gz`, osobno na poziomie lematu i formy. **Brak w SGJP:** wulwa, chirurżka, kardiolożka, premierka, sędzini, cispłciowy, transpłciowy, transpłciowość, interpłciowy, tranzycja, transfobia, misgenderować, osobatyw, ciałopozytywność, dukaizm, agender, cisnormatywność.
- **Już są w SGJP:** psycholożka, ministerka, członkini, marszałkini, gościni, polityczka, żołnierka, filozofka, niebinarny, niebinarność, queerowy, heteronormatywność, menstruować, byłom i zrobiłom. Z wydaniem 20261018 doszła też muralistka.
- Szczególny przypadek: „ministra”. 6 z 10 form to formy z odmiany „minister”, a nowe są tylko ministrę, ministrą, ministro i ministr. **W Literakach zysk z lematu bywa mniejszy niż z samych nowych form.** Karta musi pokazać te nowe formy.
- Największa pula to **feminatywy systemowe**. W tezaurusie DS jest 270 form na `-lożka` spoza SGJP, a w DS 644 hasła feminatywopodobne spoza SGJP. RJP 2019 uznaje ten model za poprawny.

## Kluczowe decyzje
- Proponuję podział na trzy podklasy, bo każda wymaga innego dowodu:
  - **(a) feminatywy systemowe** (`-ka`, `-ini/-yni` od nazw zawodów): uzasadnia je reguła RJP;
  - **(b) słowa świadomej zmiany z użyciem** (wulwa, transpłciowy, tranzycja): potrzebny dowód z redagowanego słownika (DS) i z korpusu;
  - **(c) formy normatywne bez użycia** (neutratywy, osobatywy, „onu”, `-um`): nie dodajemy.
- Kandydaci do pierwszej karty: wulwa, transpłciowy, transpłciowość, tranzycja, transfobia, ciałopozytywność, chirurżka, kardiolożka. Wszystkie są w DS i nie ma ich w SGJP. Premierka nie ma DS, więc wymaga korpusu.

## Otwarte pytania i ryzyka
- Liczby użyć w korpusach (FineWeb-2, HPLT, PPC) są w kategoriach `ccrawl` i `potoczne`. Tu ich nie ma. Każdy kandydat potrzebuje tego pomiaru, zanim dostanie kartę.
- Feminatywy na `-lożka` w tezaurusie DS wyglądają na **wygenerowane według wzoru** (np. angelolożka, chiropterolożka). Ich obecność nie dowodzi użycia.
- Czy podklasę (a) przyjąć hurtem według wzoru, tak jak SGJP przyjmuje psycholożkę, czy słowo po słowie (D1-A)? To decyzja użytkownika (zob. 05).
- „Sędzini” (od sędzia) nie ma w SGJP ani w DS. Jest za to „sędzina” (SGJP), ale ma inne, potoczne nacechowanie.

## Wyniki (skrypt `scratchpad/potoczne/swiadoma/scripts/sgjp_check.py`, wynik `sgjp-check.tsv`)
| kandydat | lemat w SGJP | formy w SGJP | DS | uwagi |
|---|---|---|---|---|
| wulwa | nie | 0/10 | tak (2024) | podklasa (b) |
| chirurżka | nie | 0/10 | tak | (a); RJP 2019 podaje ją jako przykład |
| kardiolożka | nie | 0/6 | tak (2025) | (a) |
| premierka | nie | 0/6 | nie | (a) |
| sędzini | nie | 0/4 | nie | (a), rzadkie |
| ministra | nie | 6/10 (formy od minister) | tak (2024) | nowe: ministrę, ministrą, ministro, ministr |
| transpłciowy | nie | 0/4 | tak (2024) | (b) |
| transpłciowość | nie | 0/2 | tak | (b) |
| cispłciowy, interpłciowy | nie | 0 | nie | (b), słabszy dowód |
| tranzycja | nie | 0/3 | tak (2024) | (b) |
| transfobia | nie | 0/2 | tak | (b); homofobia jest |
| misgenderować | nie | 0/3 | nie | (b), słaby dowód |
| ciałopozytywność | nie | 0/2 | tak | (b) |
| osobatyw, dukaizm | nie | 0/3 | nie | termin metajęzykowy |
| agender, cisnormatywność | nie | 0 | nie | (b), słaby dowód |
| onu, jenu (neozaimki) | nie | 0 | — | (c), nie dodajemy |
| zrobiłum, byłum, zrobiłxm | — | 0 | — | (c), nie dodajemy |
| psycholożka, ministerka, członkini, marszałkini, gościni, polityczka, żołnierka, filozofka, muralistka | tak | wszystkie | — | kontrola dodatnia: SGJP przyjmuje feminatywy |
| niebinarny, niebinarność, queerowy, heteronormatywność | tak | wszystkie | niebinarny: tak | kontrola dodatnia (b) |
| byłom, zrobiłom | tak (być, zrobić) | 2/2 | — | SGJP ma formy neutralne czasu przeszłego |

DS sprawdzony wyszukiwarką 2026-11-03. Liczba form to tylko te wpisane do testu, nie pełny paradygmat.

## Pule do przeglądu (pliki lokalne, nie do repo)
- `thes-not-in-sgjp.txt`: 1761 haseł tezaurusu DS bez lematu w SGJP (1390 bez formy). Lista jest wolna (GPL/LGPL).
- `ds-not-in-sgjp-forms.json`: 5448 haseł DS bez formy w SGJP, z id i `lastmod`. Lista z mapy witryny, tylko lokalnie.
- `zaimki-not-in-sgjp.json`: formy żeńskie, męskie i neutralne zaimki.pl spoza SGJP. OQL, tylko lokalnie.
- Część wspólna: 122 feminatywy są i w zaimki.pl, i w tezaurusie DS, a nie ma ich w SGJP. To najmocniejsza pula podklasy (a), bo potwierdzają ją dwa niezależne źródła.
