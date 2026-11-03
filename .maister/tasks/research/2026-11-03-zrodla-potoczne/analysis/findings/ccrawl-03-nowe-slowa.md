# ccrawl: nowe słowa spoza SGJP 20261018 widoczne po 2019

## TL;DR
- Na próbce ok. 500 mln słów (stan pośredni: FW2 ~165 mln, HPLT ~370 mln, dok. `ok`) przy progach **≥10 dok. po 2019, ≥5 hostów, wzrost ipm ≥4×** przechodzi **6 239 form** małą literą spoza SGJP. Po odrzuceniu form bez ogonków i angielskich, przy zgrupowaniu po temacie (≥2 formy, ≥10 hostów) zostaje **314 grup**.
- Szum jest duży. Wśród 150 największych grup ok. **połowa to śmieci**: spam pożyczkowy i kasynowy, porno, zlepki słów z SEO („pozyczkiichwilowkico”), brak ogonków („chwilowki”, „zaswiadczen”), nazwy firm („vivus”, „alior”, „getin”).
- Druga połowa to **prawdziwe nowe słowa, ale prawie same terminy i słowa handlowe, nie potoczne**: kryptowaluta, cashback, cyberbezpieczeństwo, blockchain, webinar, chatbot, smartwatch, glamping, esport, mikroplastik, teleporada, onboarding, dropshipping, phishing, zeroemisyjny, koronawirusowy, freebet, altcoin. Potoczne lub internetowe jest z nich tylko kilka: sneakersy, outfit, streamować, zaopiekowany, casualowy, karcianka.
- Wniosek: Common Crawl dobrze potwierdza słowo już podejrzane (karta kandydata). Jako automatyczne źródło list potocznych się nie nadaje bez mocnego filtra spamu i bez ręcznego przeglądu.

## Kluczowe decyzje
- Kandydat to token zapisany **w całości małą literą**, tylko litery polskie, długość ≥4, którego nie ma w zbiorze form SGJP 20261018 (4 934 988 form po zamianie na małe litery). Liczony tylko w dokumentach `ok` (bez `sjp`, `copy`, `en`).
- Wzrost: ipm w crawlach z lat 2020+ podzielone przez ipm z lat ≤2018 (+0,5 wygładzenia). Rok 2019 pomijam jako przejściowy.
- Flagi: `bez_ogonkow` (po usunięciu diakrytyków równa się formie SGJP), `ang` (jest w `/usr/share/dict/words`). Słowa `ang` nie są odrzucane z definicji, bo zapożyczenia to część celu. W grupowaniu je pominąłem, bo dominuje w nich tekst angielski i spam („casino”, „credit”, „spins”).

## Otwarte pytania i ryzyka
- Liczby pochodzą ze **stanu pośredniego** skanu (`out/neo-test.tsv`, `out/neog-test.tsv`). Ponowne przeliczenie na pełnej próbce (`scripts/neo.py 10 5 4`, `scripts/neogroup.py … 2 10`) nie zdążyło się wykonać. Rząd wielkości się nie zmieni; dokładne liczby tak.
- Liczba hostów jest zaniżona: zbiór hostów na kawałek ma limit 12 i zapisywany jest tylko przy ≥3 hostach.
- Kontrole celowe (`boomer`, `ghosting`, `cringe`, `wulwa`) są celowo wyłączone z listy kandydatów (liczone osobno w [`ccrawl-02`](ccrawl-02-kontrole.md)). Z ich liczb (≤20 dok. po 2019 w FW2) wynika, że próg ≥10 dok. przepuściłby boomer, ghosting i lockdown, ale nie cringe ani wulwę. **Czułość dla słów rzadkich jest niska** przy próbce <1 mld słów.
- Filtr spamu (doc-level) nie istnieje. Kandydat: odrzucać dokumenty z gęstością słów pożyczkowych i kasynowych albo hosty z listy spamu. To zadanie dla kategorii `metoda`.

## Przykłady (grupy, dok. po 2019, przykładowe formy)
Prawdziwe nowe słowa (terminy, handel, technika): kryptowalut- 7 373 · cashback 2 358 · targetowanie 1 524 · cyberbezpieczeństwo 1 325 · jackpot 1 244 · blockchain 1 068 · webinar 975 · loftowy 828 · posprzedażowy 717 · gamingowy 635 · freebet 588 · mikropożyczka 585 · antykryzysowy 550 · ketogeniczny 540 · podolog 538 · kannabinoid 523 · zeroemisyjny 428 · glamping 425 · esport 411 · inwerter 387 · teleporada 262 · chatbot 255 · smartwatch 242 · dropshipping 199 · mikroplastik 165 · phishing 164 · koronawirusowy 151 · onboarding 147 · altcoin 124.

Potoczne i internetowe: sneakersy 677 · stream/streamować 269 · zaopiekowany 220 · outfit 193 · casualowy 179 · karcianka 411.

Szum (odrzucić): pozabankowy 16 595 (spam pożyczkowy, choć to słowo istnieje), chwilówk- 3 587, „pozyczkiichwilowkico” 2 560, poyczki 2 003 (zgubione „ż”), slotowy 2 948 (kasyno), vivus / alior / eurobank (marki), shemale / gangbang / milf (porno), „monitorujpozycje”, „najnowszeprogramypit” (zlepki SEO), rzeszow / czestochowa (bez ogonków).

## Ocena szumu (ręczny przegląd 150 największych grup)
| Klasa | Udział (≈) |
|---|---|
| prawdziwe nowe słowo ogólne lub terminologiczne | 45% |
| prawdziwe słowo potoczne lub internetowe | 4% |
| spam (pożyczki, kasyno, porno) | 25% |
| zlepek, literówka, brak ogonków | 15% |
| marka, nazwa własna, obcy język | 11% |
