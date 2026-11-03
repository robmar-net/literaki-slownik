# ccrawl: zastrzeżenia TDM (opt-out) na hostach próbki FineWeb-2

> Do decyzji użytkownika, nie porada prawna.

## TL;DR
- Stan na **2026-11-03** dla 200 hostów z próbki FineWeb-2 (100 największych i 100 losowych z miejsc 101–2000): **TDMRep nie ma nigdzie** (0/200: brak `/.well-known/tdmrep.json`, nagłówka `tdm-reservation` i znacznika meta).
- robots.txt dziś blokuje `CCBot` na **34/100** największych hostach (37,6% ich dokumentów) i na **11/100** losowych. Jakikolwiek bot AI blokuje 47/100 i 15/100. Nagłówek Cloudflare `Content-Signal: … ai-train=no` mają 12/100 i 7/100 hostów.
- Część hostów zastrzega TDM wprost, po polsku, w komentarzu w robots.txt. Grupa Agora pisze tam: „Wlasciciel niniejszego serwisu nie wyraza zgody na zwielokrotnianie ani inne korzystanie z utworow rozpowszechnionych w tym serwisie, w celu eksploracji tekstow i danych.” Takich hostów jest 8/200 w przebiegu automatycznym, 3 potwierdzone ponownie.
- Wniosek: dane zebrano, gdy robots.txt na to pozwalał, ale **dziś** duża część dużych portali zastrzega TDM. Zgodnie z art. 26³ dokumenty z hostów z zastrzeżeniem trzeba wykluczyć z liczenia (lista blokad), a hosty dowodów kandydata sprawdzić przed wpisem.

## Kluczowe decyzje
- Za zastrzeżenie uznaję (zachowawczo): (a) blokadę `CCBot` lub `*` (`Disallow: /`) w robots.txt, (b) jawny tekst o TDM w robots.txt lub regulaminie, (c) TDMRep, (d) `Content-Signal ai-train=no` (dotyczy treningu AI, nie każdego TDM; oznaczam osobno).
- Nie czytałem regulaminów stron (HTML). Przy hostach dowodów kandydata trzeba to zrobić ręcznie.

## Otwarte pytania i ryzyka
- To stan z dziś, nie z dnia crawla. Nie wiadomo, czy art. 26³ liczy stan w chwili naszego zwielokrotnienia (pobrania shardu). Zakładam, że tak, bo to wariant bezpieczniejszy.
- Komentarz w robots.txt (`#`) nie jest formatem „do odczytu maszynowego” w ścisłym sensie, ale jest wyraźny. Traktuję go jako zastrzeżenie.
- Losowa setka pochodzi z hostów 101–2000. Długi ogon (332 317 hostów w próbce) może mieć mniej blokad. 7–17% hostów nie odpowiedziało albo nie ma robots.txt.

## Metoda
- Lista hostów: `scripts/hosts_fw2.py` na 5 plikach próbki (1 513 000 dok., 332 317 hostów; 100 największych = 11,0% dokumentów).
- Sprawdzenie: `scripts/optout.py`. Dla każdego hosta trzy GET-y: `https://<host>/robots.txt`, `/.well-known/tdmrep.json` i strona główna (nagłówek i meta). UA `literaki-slownik-research`, 8 wątków, timeout 12 s.
- Wynik surowy: `scratchpad/potoczne/ccrawl/out/optout.json`.

## Wyniki

| Próba | robots.txt 200 | blokada CCBot | blokada dowolnego bota AI | `Disallow: /` dla `*` | Content-Signal ai-train=no | tekst o TDM w robots | TDMRep (plik/nagłówek/meta) |
|---|---|---|---|---|---|---|---|
| 100 największych hostów | 90 | 34 (37,6% dok.) | 47 (49,8% dok.) | 2 | 12 (7,5% dok.) | 5 (5,9% dok.) | 0 / 0 / 0 |
| 100 losowych (miejsca 101–2000) | 83 | 11 | 15 | 0 | 7 | 3 | 0 / 0 / 0 |

Przykłady blokady CCBot: rynekzdrowia.pl, pl.tripadvisor.com, sportowefakty.wp.pl, money.pl, polityka.pl, forum.gazeta.pl. Jawny polski tekst zastrzeżenia ponownie potwierdzony na: forum.gazeta.pl, wiadomosci.radiozet.pl, next.gazeta.pl. Wszystkie odsyłają do `agora.pl/zastrzezenie-prawne`.

## Wpływ na proces
- Liczby w [`ccrawl-02-kontrole.md`](ccrawl-02-kontrole.md) i [`ccrawl-03-nowe-slowa.md`](ccrawl-03-nowe-slowa.md) policzono **przed** filtrem opt-out. Przy wdrożeniu: najpierw lista hostów z zastrzeżeniem (robots.txt hostów z próbki, ~10⁵ zapytań, jednorazowo), potem liczenie.
- Lżejsza ścieżka: liczyć tylko dla kandydatów, a przed wpisem do karty sprawdzić hosty ich dokumentów dowodowych i odrzucić dowody z hostów z zastrzeżeniem.
