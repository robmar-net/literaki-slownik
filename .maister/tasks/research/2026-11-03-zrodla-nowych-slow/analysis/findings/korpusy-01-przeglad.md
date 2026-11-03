# korpusy: przegląd korpusów i list 2015+

## TL;DR
- Dwa źródła mają czystą licencję CC BY 4.0, daty i da się je pobrać: **ParlaMint-PL 5.0** (Sejm i Senat, 2015-11-12–2022-06-30) i **Leipzig Corpora Collection, wiadomości PL** (2018, 2021–2024, gotowe listy frekwencyjne). To kandydaci na `corpus_evidence`.
- Korpusy z Common Crawl (FineWeb-2, HPLT) są ogromne, mają URL i datę przy każdym dokumencie, więc SJP.pl da się wykluczyć po domenie. Licencja obejmuje jednak tylko opakowanie, nie tekst. Status pochodnej listy jest nierozstrzygnięty.
- KWJP100 obejmuje lata 2011–2020. „Przed KWJP” oznacza więc słowa po 2020. W repo nie ma nowszych list niż `26d82bd8`.
- OSCAR i CulturaX wymagają konta HF, więc odpadają. MoncoPL to tylko wyszukiwarka, a 2026-11-03 nie odpowiadała. Google Books Ngram nie ma polskiego.

## Kluczowe decyzje
- „MoNKa” nie znalazłem. Korpusem monitorującym polszczyzny jest **MoncoPL** (Pęzik, UŁ). Opisuję go zamiast MoNKi.
- Licencję opakowania (CC0, ODC-By) traktuję osobno od praw do tekstu. Pochodna lista z FineWeb-2 i HPLT dostaje ocenę „do decyzji”, nie `ALLOWED`.
- Wikipedia i Wikinews mają CC BY-SA 4.0, więc według AGENTS.md (l. 424) trzymamy je osobno, dopóki nie ustalimy obowiązków. Nie są wejściem.

## Otwarte pytania
- Czy pochodna lista frekwencyjna (lemat + liczba) z tekstu na stronach osób trzecich (FineWeb-2, HPLT) może wejść do repo? To decyzja prawna dla `projekt` i użytkownika.
- MADLAD-400 podaje dwie licencje: metadane karty mówią `odc-by`, treść karty „CC-BY-4.0”. Do tego nie ma pola URL.
- Spokes: nie znalazłem licencji danych.
- Okres Korpusu Dyskursu Parlamentarnego (PPC) po 2018 nie jest potwierdzony.

## Tabela źródeł (odczyt 2026-11-03)

| # | Źródło | Prowadzący | Licencja (tekst / pochodna) | Okres | Rozmiar PL | Pobieranie | Podział w czasie | Ryzyko SJP.pl | Ocena |
|---|---|---|---|---|---|---|---|---|---|
| 1 | ParlaMint-PL 5.0 (hdl 11356/2004) | CLARIN ERIC / ParlaMint | CC BY 4.0 dla całości | 2015-11-12 – 2022-06-30 (z nazw plików) | 37,0 mln słów (`wc -w` na .txt), 688 posiedzeń | tak, `ParlaMint-PL.tgz` 202 MB | tak: data posiedzenia, podkorpusy reference/covid/war | brak (stenogramy) | **ALLOWED-kandydat** `corpus_evidence`; tylko jeden rejestr (polityka) |
| 2 | Leipzig Corpora Collection `pol_news_{2018,2021,2022,2023,2024}_1M`, `pol_newscrawl_{2011,2018}_1M` | Uniwersytet w Lipsku (Wortschatz) | korpusy do pobrania: CC BY (link do 4.0) | rocznik w nazwie; 2024: build 2025-02-13 | 1 mln zdań / ~15,7 mln tokenów na rocznik | tak, ~180–220 MB na rocznik; gotowy `-words.txt` z liczbami | tak, rocznikami (bez 2019–2020, brak `pol_news_2025`) | 0 z 179 903 URL-i w 2024 (same portale informacyjne) | **ALLOWED-kandydat** `corpus_evidence`; zdania przetasowane, tylko formy |
| 3 | FineWeb-2 `pol_Latn` | Hugging Face | ODC-By 1.0 na zbiór + CommonCrawl ToU; tekst osób trzecich | 96 zrzutów CC, lato 2013 – IV 2024 | 73,1 mld słów, 152 mln dok., 432 GB | tak, parquet; całość ≫ 2 GB (opis), próbka 56 MB pobrana | tak: pola `date`, `dump` | 1 / 36 574 dok. z hosta `sjp.pl`; da się wykluczyć po `url` | **do decyzji** (licencja tekstu); technicznie najlepszy |
| 4 | HPLT v3.0 (v2.0 cleaned: `pol_Latn`) | HPLT (UFAL i in.) | CC0 tylko na „packaging”; „We do not own any of the text” | IA + CC, 2012–2024 | v2 cleaned: 89,5 mld słów, 175 mln dok. | tak, `jsonl.zst`, shardy 1,2–7,9 GB; ≫ 2 GB (opis), próbka 150 MB | tak: `ts`, `crawl_id` | 0 / 21 656 dok. w próbce; pole `u` pozwala wykluczyć | **do decyzji** (jak FineWeb-2) |
| 5 | MADLAD-400 `pl` | Google / AllenAI | sprzeczność: `odc-by` vs „CC-BY-4.0” | zrzuty CC do 2022-08-01 | 90,9 mln dok. (po audycie) | tak, ≫ 2 GB (nie pobierano) | brak pola daty i URL w karcie | **nie da się wykluczyć** (brak URL) | **BLOCKED**: sprzeczna licencja, brak URL |
| 6 | OSCAR 23.01 | Inria / DFKI / Mannheim | CC0 na opakowanie; HF `gated: manual` | do 2023 | n/d | tylko po zgodzie i z kontem HF | — | — | **BLOCKED**: wymaga konta (zasada zbieraczy) |
| 7 | CulturaX | UONLP | „strictly follows those of mC4 and OSCAR” (cytat wtórny); HF `gated: auto` | mC4 3.1.0 + OSCAR do 23.01 | n/d | tylko z kontem HF | — | — | **BLOCKED**: konto i licencja nieustalona |
| 8 | CC-100 `pl` | statmt / FAIR | licencja „unknown”; CC ToU | tylko 2018 | 12 GB | tak (nie pobierano) | nie | brak URL | **BLOCKED**: brak licencji, tylko 2018 |
| 9 | MoncoPL | P. Pęzik, Uniwersytet Łódzki | brak licencji danych; „jedynym narzędziem […] jest wyszukiwarka” | od 2010, dziennie; 5,6 mld słów w 2019 | — | nie; konkordancje, eksport wyników | tak (daty publikacji) | portale informacyjne, niskie | **tylko dowód ręczny**; `monco.frazeo.pl` nie odpowiadał 2026-11-03 |
| 10 | KWJP100 (listy `kwjp100-varia`) | IPI PAN | CC BY 4.0 (README) | **2011–2020** (`cache/kwjp/article.pdf`) | znane w projekcie | tak, już w `sources.json` | tylko gatunki, bez lat | brak | już `ALLOWED`; HEAD repo `26d82bd8` z 2026-05-28 = commit projektu; nic nowszego |
| 11 | Wikipedia pl, Wikinews pl (zrzuty) | Wikimedia | CC BY-SA 4.0 i GFDL | do bieżącego miesiąca; historia wersji | duży (pl), mały (Wikinews) | tak | tak, przez historię wersji | brak | **trzymać osobno** (BY-SA, AGENTS.md l. 424); możliwy dowód ręczny |
| 12 | Korpus Dyskursu Parlamentarnego (PPC) | IPI PAN | dane: domena publiczna; anotacja: CC BY | 1919– (koniec nieustalony) | >700 mln segmentów | tak, TEI zip | tak | brak | **kandydat po ustaleniu okresu** (rejestr jak ParlaMint) |
| 13 | Spokes / SpokesBiz | PELCRA, UŁ | nie znalazłem licencji danych | n/d | SpokesBiz >650 h | WWW, REST API | ? | brak | **BLOCKED** do czasu ustalenia licencji |
| 14 | Google Books Ngram | Google | „may be freely used for any purpose” | — | **brak polskiego** | — | — | — | nie dotyczy |
| 15 | n-gramy z Common Crawl dla PL | — | — | — | nie znalazłem gotowych | — | — | — | nie dotyczy (trzeba liczyć z 3/4) |

## Uwagi o skażeniu SJP.pl
- FineWeb-2 i HPLT mają URL przy dokumencie, więc filtr hosta `sjp.pl` / `*.sjp.pl` jest prosty. W próbkach udział był bardzo mały: 1/36 574 i 0/21 656. Strony SJP.pl są jednak bardzo podobne (strona słowa), więc cytaty i kopie na innych domenach mogą przejść filtr. W próbce FineWeb-2 tylko 1 dokument miał w tekście ciąg „sjp.pl”.
- MADLAD-400 i CC-100 nie mają URL, więc stron SJP.pl nie da się wykluczyć.
- ParlaMint, LCC news i PPC: ryzyko pomijalne (stenogramy, portale informacyjne).

## Szum zauważony w próbkach
- `ghosting` → „Anti-ghosting” w klawiaturach (FineWeb-2, pcmod.pl, 2020).
- `wulwa` w Wikipedii to głównie termin zoologiczny (anatomia pajęczaków: „Kątnik domowy”, „Tamopsis cooloolensis”), a nie nowe znaczenie.
- `boomer` w HPLT: 79 trafień w 70 dokumentach, w ParlaMint 0. To prawdopodobnie nazwy własne lub marki. Wymaga filtra wielkiej litery.
