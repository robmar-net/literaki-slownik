# potoczne-01: przegląd źródeł potocznych i internetowych

## TL;DR
- Oceniłem 17 nowych źródeł. Najsilniejszy sygnał dają **napisy OpenSubtitles z filmów 2022–2023**: wszystkie 7 kontroli, w tym wulwa 7, ghosting 11, cringe 10. Napisy nie mają jednak licencji tekstu, więc ocena: `do decyzji` (tylko lokalny pomiar, TDM).
- Czystą licencję tekstu i daty mają tylko **strony dyskusji plwiki** (CC BY-SA 4.0), ale potocznych trafień jest w nich mało. BAN-PL wycofany decyzją użytkownika 2026-11-04 (autorzy chronią archiwa hasłem przed automatycznym zbieraniem); liczby usunięte.
- **Fora SpeakLeash** (ogromne, bez konta, bez licencji tekstu, bez dat) dają mało: treść jest stara, a boomer to tam guma do żucia. Ocena `do decyzji`.
- **Wulwa** jako świadoma zmiana: napisy 2022–2023 (zdanie z filmu, w którym bohaterka poprawia potoczną nazwę narządu na „wulwa”), plwiki „Dyskusja:Wargi sromowe” (2023), kafeteria.pl, artykuł plwiki „Srom” („rzadziej wulwa”, przypis glamour.pl). Ma też starsze znaczenie zoologiczne (narząd dwuparców). Plwiki można cytować (CC BY-SA), napisy tylko liczyć.
- Reddit i X odpadają przez regulamin. BIGOS i PELCRA odpadają przez bramkę HF. Common Voice ma czysty tekst, ale nie potoczny (0 trafień, także kontroli).

## Kluczowe decyzje
- Ocena `ALLOWED` tylko przy jawnej licencji tekstu, która pozwala na publikację liczb i krótkich cytatów.
- Źródła z licencją NC (hate_speech_pl, Spokes, blogi CLARIN-PL) dostają `do decyzji`. Literaki to projekt hobbystyczny, ale komercyjność ocenia użytkownik.
- Strony dyskusji plwiki: licencja czysta, ale mało potocznych trafień (to metadyskusja redakcyjna). Ocena `ALLOWED`, przydatność niska.
- Spokes oceniam ponownie, bo jest nowy fakt: CLARIN-PL podaje dla niego CC BY-NC 3.0 (w #16: „nie znalazłem licencji”).

## Otwarte pytania i ryzyka
- Czy lokalne liczenie w forach SpeakLeash i w OpenSubtitles mieści się w TDM (art. 26³ pr. aut.)? Odpowiada na to kategoria 2 (ccrawl). Do tego czasu `do decyzji`.
- Pomiary forów i napisów są częściowe (próbka; szczegóły w `potoczne-03-pomiar.md`). Maszyna była mocno obciążona (load avg 35–73), a liczenie pod `taskpolicy -b` szło wolno.
- Fora SpeakLeash nie mają dat przy dokumentach. Nie da się ich podzielić w czasie.

## Tabela źródeł (odczyt 2026-11-03; cytaty licencji: `potoczne-02-licencje.md`)

| # | Źródło | Licencja tekstu | Okres | Rozmiar PL | Bez konta | Daty | Ryzyko SJP.pl | Ocena |
|---|---|---|---|---|---|---|---|---|
| 1 | OpenSubtitles v2024 (OPUS), mono | brak; prośba o link i cytowanie | filmy do 2023 (11,6% plików z lat 2019+) | 1,76 mld tokenów, 2,44 GB gz | tak | rok filmu w nazwach członów `xml/pl.zip` (15,6 GB; lata wybieralne przez Range); w mono brak | brak | **do decyzji** (tylko lokalny pomiar); najsilniejszy sygnał |
| 2 | SpeakLeash, fora (140 zbiorów, np. kafeteria, wizaz, gazeta.pl) | „conditional license” / „(c) host” | crawl ok. 2022–2023, treść z lat ~2000–2023 | ok. 18 mld słów w kategorii Forum | tak (publiczny bucket, `*.jsonl.zst` + `*.manifest`) | brak dat w `meta` | niskie (brak zbioru z sjp.pl wśród 838 nazw) | **do decyzji** (tylko lokalny pomiar) |
| 3 | SpeakLeash, usenet | „usenet” | lata 90.–2000. | 3,1 mld słów | tak | nie sprawdzałem | niskie | do decyzji; niezmierzone (stare, mało przydatne dla nowych słów) |
| 4 | SpeakLeash, open_subtitles_pl_corpus | podana „PD; CC BY-SA 3.0; FAL 1.3” bez oparcia w źródle | OpenSubtitles 2018 | 226 mln słów | tak | brak | brak | odpada (duplikat nr 1, licencja niewiarygodna) |
| 5 | Strony dyskusji plwiki (ns nieparzyste + `Wikipedia:`) | CC BY-SA 4.0 | 2001–2026, rok z podpisu | 182 mln słów w dyskusjach (54% bajtów zrzutu) | tak (dumps.wikimedia.org) | **tak**: rok każdego komentarza z podpisu | brak | **ALLOWED**; przydatność niska |
| 6 | PolEval 2019 zad. 6 (tweety) | „unknown” | ok. 2018–2019 | 11 tys. tweetów, 0,15 mln słów | tak | brak | brak | tylko dowód ręczny / odpada (brak licencji, mały) |
| 7 | hate_speech_pl (IPI PAN) | CC BY-NC-SA (wersja nieznana) | ok. 2007–2012 (portale) | 0,48 mln słów | tak (HF parquet) | brak | brak | do decyzji (NC); mało przydatne (stare) |
| 8 | PolEmo 2.0 (recenzje) | CC BY 4.0 (CLARIN) / CC BY-SA 4.0 (HF) | do 2019 | 0,9 mln słów | tak | brak | brak | ALLOWED; mało przydatne (recenzje, stare) |
| 9 | Common Voice PL, `sentence-collector.txt` | CC0 | 2017–2026 | 22,7 tys. zdań, 0,16 mln słów | tak (GitHub) | brak | brak | ALLOWED; nieprzydatne (zdania czytane, nie potoczne) |
| 10 | Reddit (API, zrzuty) | regulamin: zakaz scrapingu i treningu ML bez zgody właścicieli | — | — | API wymaga aplikacji/konta; zrzuty to torrenty ze scrapingu | — | — | **odpada**; najwyżej dowód ręczny (link do wątku + data) |
| 11 | X / Twitter | regulamin: zakaz scrapingu; dalej wolno dawać tylko ID | — | — | nie | — | — | **odpada** |
| 12 | BIGOS v2 (amu-cai) | CC BY-SA 4.0 | — | — | **bramka HF** | — | — | odpada |
| 13 | PELCRA for BIGOS | CC BY-NC-ND 4.0 | — | — | **bramka HF** | — | — | odpada |
| 14 | Spokes (PELCRA) — **nowy fakt** | CC BY-NC 3.0 (rekord usługi, hdl 11321/47) | ok. 2000–2013 | >2 mln słów mowy potocznej | WWW i REST, bez konta (nie testowałem API) | z nagrań | brak | do decyzji (NC; korpus za stary dla nowych słów) |
| 15 | Blogi CLARIN-PL (Blogs_2018, Mining blogs, Blogosfera…) | CC BY-NC-SA 3.0 / CC BY-NC-ND 3.0 | do 2018 | małe | tak | brak | brak | do decyzji (NC); niezmierzone, za stare |
| 16 | Korpus forum klientów banku; komentarze YT (CLARIN-PL) | CC BY-NC-ND 3.0 | 2016–2017 | małe | tak | brak | brak | odpada (ND, wąskie, stare) |
| 17 | Mowa Wrocławia lat 80. (CLARIN-PL) | CC BY 4.0 | lata 80. | mały | tak | tak | brak | ALLOWED; nieprzydatne dla nowych słów |

Poza zakresem tej kategorii, ale znalezione: VoxPopuli to przemówienia w PE, nie mowa potoczna. OPUS TED2020 i QED to wykłady. Nie mierzyłem ich.

## Wulwa — ślady w tej kategorii
- kafeteria.pl (SpeakLeash): 3 trafienia w 2 wątkach, m.in. wpis, w którym autorka poprawia „wagina” na „wulwa” jako nazwę właściwą (kafeteria.pl, rok wpisu nieznany). To jest świadoma zmiana, nie potoczność. Daty wpisu brak.
- plwiki, artykuł „Srom”: „'''Srom''', rzadziej '''wulwa'''” z przypisem do glamour.pl („Sekspozytywny alfabet by G'rls ROOM – W jak wulwa”, dostęp 2021-08-22). Link: https://pl.wikipedia.org/wiki/Srom (odczyt 2026-11-03). Licencja CC BY-SA 4.0, więc wolno go cytować z atrybucją.
- plwiki, artykuły zoologiczne (Dwuparce, Kątnik domowy): „wulwa/wulwy” jako narząd samic stawonogów. To starsze znaczenie specjalistyczne. Wynik: słowo ma dwa niezależne źródła użycia.
- OpenSubtitles, filmy 2022–2023: 7 zdań (część to duplikaty wersji napisów), np. zdanie, w którym bohaterka zastępuje wulgarną nazwę narządu słowem „wulwa” (film z lat 2022–2023).
- plwiki, „Dyskusja:Wargi sromowe” (podpis z 2023 r.): „…wyglądu wulwy w encyklopediach i podręcznikach…”.
- PolEval: 0. Kontrola dodatnia w tym samym źródle (hejt) jest >0 (patrz 03).
