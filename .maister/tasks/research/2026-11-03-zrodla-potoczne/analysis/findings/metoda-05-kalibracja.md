# metoda: kalibracja bramek na kontrolach (Leipzig news PL, pomiar lokalny)

## TL;DR
- Bramki B3–B7 z `metoda-01` sprawdziłem na Leipzig news PL 2018, 2021–2024 (5 mln zdań, 67,9 mln słów, CC BY 4.0). To korpus z licencją i z hostami przy każdym zdaniu, więc dobrze nadaje się do strojenia filtra. Na zbiorach nieformalnych pomiar powtórzą kategorie ccrawl i potoczne.
- **Progi v2** (mała litera ≥ 70%, polski kontekst ≥ 70%, największy host ≤ 35%): przechodzi **37 z 43 zapożyczeń, które są w SGJP** (86%), i **0 z 20 angielskich słów kontrolnych** (the, free, team, love, game…). Progi v1 przepuszczały tylko 26 z 43.
- Kontrole: **antyszczepionkowiec i boomer przechodzą** (boomer tylko przy v2: n = 20, 13 hostów). **Cringe, ghosting, krindż mają w wiadomościach 3–6 trafień, wulwa 0.** Nie przechodzą B7. Kontrole dodatnie hejt i lockdown przechodzą (liczone tak, jakby nie było ich w SGJP).
- Najmocniejsza bramka to **B3 (mała litera poza początkiem zdania)**. Sama odcina wszystkie 20 słów angielskich (maks. 54%). B5b (polski kontekst) prawie nie rozróżnia: angielskie słowa mają 40–85%.

## Kluczowe decyzje
- Przyjmuję **progi v2** jako punkt startowy dla zbiorów nieformalnych. Próg B7 (n ≥ 20) zostaje do sprawdzenia: [do uzupełnienia z ccrawl/potoczne].
- B5b zostaje tylko jako dodatkowy sygnał dla słów nieodmiennych. Wyrazy angielskie odcina B3 + B4, nie B5b.
- „Odsetek słów SGJP, które przechodzą” w tej warstwie mierzy **czułość** (prawdziwe zapożyczenia mają przejść), a nie fałszywe alarmy jak w #16. Fałszywe alarmy mierzy lista angielskich słów kontrolnych (0/20).

## Otwarte pytania i ryzyka
- Leipzig to wiadomości: mało hostów (zwykle 10–150 na słowo), zdania zamiast dokumentów. B4 liczyłem na zdaniu. W sieci B4 będzie liczony na dokumencie i może działać inaczej.
- Cringe, ghosting, krindż i wulwa nie dają się skalibrować na wiadomościach. Kalibracja celu: [do uzupełnienia z ccrawl/potoczne].
- Listy testowe są ręczne i małe (43 + 20 + 6). Przedziały są szerokie: 37/43 to ok. 73–93% (Wilson 95%).
- Wielkie litery w nazwach (`Daily Mail`, `MEM`) zaniżają B3 dla `mail` (0,695) i `mem` (0,706). Próg 70% leży tuż przy nich.

---

## 1. Wyniki dla kontroli (po B3 i B4 liczymy tylko małą literę w zdaniu polskim)

| Słowo | w SGJP | surowe | B3 mała | po B3+B4 | B5a odmienione / form | B5b kontekst | hosty / największy | v1 | v2 |
|---|---|---|---|---|---|---|---|---|---|
| antyszczepionkowiec | nie | 278 | 0,987 | 234 | 94% / 9 | 0,83 | 43 / 0,22 | ✓ | ✓ |
| boomer | nie | 28 | 0,769 | 20 | 20% / 2 | 0,85 | 13 / 0,15 | ✗ (B3) | ✓ |
| cringe | nie | 6 | 1,0 | 6 | — | 0,83 | 6 / 0,17 | ✗ (B6, B7) | ✗ |
| krindż | nie | 4 | 1,0 | 4 | 0% / 0 | 0,50 | 3 / 0,50 | ✗ | ✗ |
| ghosting | nie | 8 | 0,75 | 3 | 67% / 1 | 0,33 | 2 / 0,67 | ✗ | ✗ |
| wulwa | nie | 0 | — | 0 | — | — | 0 | ✗ | ✗ |
| *dodatnia:* hejt | tak | 843 | 0,968 | 778 | 65% / 6 | 0,87 | 71 / 0,09 | ✓ | ✓ |
| *dodatnia:* lockdown | tak | 1 298 | 0,985 | 1 211 | 69% / 9 | 0,81 | 64 / 0,17 | ✓ | ✓ |

- Zapis niegrywalny (dowód leksemu, nie do listy): `cringe'u` 1, `cringe'owy` 1, `cringe’owy` 1; `lockdown’u` 3, `lockdown'owym`, `lockdown’ów`, `lockdown’y`, `lockdown-ie` po 1.
- Każde „0” dla wulwy ma obok kontrolę dodatnią w tym samym korpusie (hejt 778, lockdown 1 211).

## 2. Zapożyczenia z SGJP (czułość)

| Grupa | v1: przechodzi | v2: przechodzi | v2: odpada (powód) |
|---|---|---|---|
| odmienne (36) | 23 | **32** | hacker (n 6), hipster (n 8, 6 hostów), mail (B3 0,695), spojler (9 hostów) |
| nieodmienne (7) | 3 | **5** | cool (B3 0,43), fair (B3 0,69) |
| razem | 26/43 | **37/43** | |

Co zmieniło v1 → v2:
- B3 0,9 → 0,7: wracają coaching, design, mem, stalker, youtuber (B3 0,71–0,88).
- B6 0,25 → 0,35: wracają briefing, fejk, podcast, spoiler (największy host 0,27–0,34).
- B5b 0,8 → 0,7: wracają online, selfie (0,74).
- Udział form odmienionych (B5a) u prawdziwych zapożyczeń: od 23% (weekend) i 32% (lunch) do 97% (mem). Próg 10% ma duży zapas.

## 3. Angielskie słowa kontrolne (fałszywe alarmy)
- 20 słów: beauty, best, black, challenge, fashion, free, friday, game, happy, home, life, love, music, people, shop, story, style, team, the, world. Przy v1 i v2 nie przechodzi żadne (0/20).
- B3 (mała litera poza początkiem zdania): od 0,013 (world) do 0,535 (beauty). Wszystkie poniżej 0,7.
- B5b: od 0,40 (people) do 0,85 (best). Połowa przekracza 0,7, więc B5b sam nie odróżnia angielskiego.
- `challenge`, `shop`, `story`, `team` są w SGJP jako lematy pospolite. Mimo to w wiadomościach zachowują się jak wtrącenia (B3 0,15–0,27). Jeśli takie słowo trafi do kandydatów spoza SGJP, karta pokaże niski B3.

## 4. Co z tego wynika dla kolejki
- Sieć ma być źródłem dla cringe, ghosting, krindż. W wiadomościach mają 3–6 użyć w ~68 mln słów (≈ 0,05–0,09 ipm), więc B7 przy n ≥ 20 wymaga zbioru ≥ ~300 mln słów przy podobnej częstości. W sieci potoczność jest wyższa. Liczby: [do uzupełnienia z ccrawl/potoczne].
- Boomer przechodzi już w Leipzig. W kolejce trafiłby do P1, jeśli ma też trafienia w sieci, albo do P2. Homograf `bumer` (m3 w SGJP) zostaje na karcie.
- Wulwa nie wyjdzie z żadnego korpusu prasowego. Zostaje droga Z2 (`metoda-02`).

## Pliki
`/private/tmp/claude-501/-Users-robmar-Projects-Literaki/3ae5c44e-c8df-4ef9-924a-bcb0e5eaf7f8/scratchpad/potoczne/metoda/`: `scripts/bramki_lcc.py` → `bramki-lcc.json` (wszystkie miary na słowo), `scripts/progi_v2.py` → `progi-v2.txt` (v1 vs v2). Wejście: `nowe-slowa/dl-lcc/pol_news_{2018,2021,2022,2023,2024}_1M/`, SGJP `sgjp-20261018.tab.gz`, formy kontroli `nowe-slowa/kontrole.json` (ghosting rozszerzony do 9 form według wzoru `ranking`).
