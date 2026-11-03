# Źródła badania: słowa potoczne i świadoma zmiana

## TL;DR
- Lokalnie: próbki FineWeb-2 (54 MB) i HPLT (1,2 GB), formy kontroli i skrypty liczące z #16, dokumenty projektu i wyniki #16.
- Zewnętrznie: cztery grupy kandydatów do sprawdzenia (korpusy potoczne, Common Crawl + prawo, świadoma zmiana, metoda).
- URL-e zewnętrzne to punkty startu. Zbieracz potwierdza każdy odczytem i datą; nie wszystkie muszą istnieć.

## Kluczowe decyzje
- Źródła ocenione w #16 wymieniamy tylko jako odniesienie, bez ponownej oceny.
- Wykluczone: SJP.pl (poza pomiarem udziału hosta), Wikisłownik, zbiory wymagające konta lub „gated”.

## Otwarte pytania i ryzyka
- Część kandydatów (Reddit, napisy, Twitter/X) może mieć regulamin, który zabrania użycia. Wtedy ocena „odpada” lub „tylko dowód ręczny”.
- Dokładne numery artykułów polskiej ustawy (26², 26³) trzeba potwierdzić w ISAP.

## Źródła lokalne (istnieją, sprawdzone 2026-11-03)

Katalog: `/private/tmp/claude-501/-Users-robmar-Projects-Literaki/3ae5c44e-c8df-4ef9-924a-bcb0e5eaf7f8/scratchpad/nowe-slowa/`
- `kontrole.json`, `kontrole.py` — pełne paradygmaty form kontroli (hejt, lockdown, antyszczepionkowiec, boomer, ghosting, cringe, wulwa i in.) i liczenie.
- `dl-fw2/pol_test_000.parquet` — próbka FineWeb-2 (54 MB).
- `dl-hplt/pol_10_1.head.zst`, `pol_10_1.head.jsonl` — próbka HPLT (1,2 GB).
- `scripts/scan.py`, `scripts/scanjsonl.py`, `scripts/ctx.py` — liczenie form i konteksty (do ponownego użycia).
- `kalibracja*.py/json`, `pokrycie.*`, `zysk/`, `projekt/`, `cards/` — kalibracja progów i karty z #16.
- `dl-ppc`, `dl-parlamint*`, `dl-lcc` — korpusy z #16 (tylko do kontroli dodatnich i porównań; nie pobierać ponownie).
- Wolne miejsce: ok. 34 GB (`df -h /`).

## Dokumentacja projektu

- `/Users/robmar/Projects/Literaki/literaki-slownik/AGENTS.md` — zasady (zwięźle, decyzje z użytkownikiem, bez kontaktu z grupami, SJP.pl nie jest źródłem).
- `/Users/robmar/Projects/Literaki/literaki-slownik/.maister/docs/INDEX.md` — indeks dokumentów i decyzji (m.in. odroczenie Wikisłownika).
- `/Users/robmar/Projects/Literaki/literaki-slownik/docs/adr/` — ADR-006 … ADR-013 (NKJP CC BY, metody POP, TEMATY, Słowosieć/IATE).
- `/Users/robmar/Projects/Literaki/literaki-slownik/ATTRIBUTIONS.md`, `config/generator/evidence.json` — atrybucje i przypięte źródła.

## Wyniki #16 (czytać skrótowo)

Katalog: `/Users/robmar/Projects/Literaki/literaki-slownik/.maister/tasks/research/2026-11-03-zrodla-nowych-slow/`
- `outputs/podsumowanie.md`, `outputs/research-report.md` — wnioski, decyzje D1–D5.
- `outputs/high-level-design.md` — potok, warstwy, karta kandydata, miara wzrostu g (kat. 4).
- `outputs/decision-log.md` — szkice ADR-014–018 (kat. 4).
- `analysis/findings/korpusy-01-przeglad.md`, `korpusy-03-licencje.md` — tabela i cytaty licencji (FineWeb-2 ODC-By, HPLT CC0 na opakowanie).
- `analysis/findings/korpusy-04-zysk.md` — zysk kandydatów.
- `analysis/findings/neolog-00-przeglad.md` — kontrole w słownikach (wulwa i ghosting: brak wszędzie).

## Kategoria 1: korpusy potoczne i internetowe (`potoczne`)

Kandydaci do sprawdzenia:
- OPUS, OpenSubtitles 2018/2024 `pl` — https://opus.nlpl.eu/ (licencja tekstu napisów, daty filmów, rozmiar monolingwalny PL).
- OPUS, inne korpusy z polskim (np. TED2020, QED, Tatoeba) — licencje per korpus.
- SpeakLeash — https://speakleash.org/ i karty na HF (podzbiory forów i portali, metadane licencji per podzbiór).
- Polskie zbiory z mediów społecznościowych: PolEval 2019 (cyberprzemoc, tweety), zbiory mowy nienawiści PL, zbiory sentymentu z Twittera/X na HF bez bramki.
- Reddit: zrzuty (np. Academic Torrents) i regulamin Reddit Data API — https://www.redditinc.com/policies/data-api-terms.
- Mowa: BIGOS (HF `amu-cai/pl-asr-bigos-*`), PELCRA (zbiory na HF/CLARIN), Common Voice PL (CC0; zdania czytane), VoxPopuli (PE), Spokes — tylko nowy fakt o licencji.
- CLARIN-PL repozytorium — https://clarin-pl.eu/dspace/ (korpusy forów, blogów, recenzji; licencje per pozycja).
- Strony dyskusji polskiej Wikipedii — zrzuty https://dumps.wikimedia.org/plwiki/ (CC BY-SA 4.0, daty edycji).
- Zbiory recenzji/opinii PL na HF (np. PolEmo, allegro/klej-*), jeśli licencja jest jawna.

## Kategoria 2: Common Crawl i prawo TDM (`ccrawl`)

- FineWeb-2 `pol_Latn` — https://huggingface.co/datasets/HuggingFaceFW/fineweb-2 (ODC-By + CC ToU; pola `date`, `dump`, `url`). Pobrać kilka shardów parquet z różnych lat.
- HPLT v2.0 cleaned / v3.0 `pol_Latn` — https://hplt-project.org/datasets/v3.0 (CC0 na opakowanie; pola `ts`, `crawl_id`, `u`; shardy 1,2–7,9 GB).
- Common Crawl Terms of Use — https://commoncrawl.org/terms-of-use.
- Dyrektywa (UE) 2019/790, art. 2, 3, 4 — https://eur-lex.europa.eu/eli/dir/2019/790/oj.
- Ustawa o prawie autorskim (tekst jednolity, nowela 2024 wdrażająca DSM) — https://isap.sejm.gov.pl/ (art. 26² i 26³, wyjątek TDM, zastrzeżenie w formie maszynowej).
- Akt o AI (rozporządzenie 2024/1689), art. 53 ust. 1 lit. c — tylko kontekst opt-out.
- TDM Reservation Protocol (W3C CG) — https://www.w3.org/community/reports/tdmrep/CG-FINAL-tdmrep-20240202/.
- Karty: czy FineWeb-2/HPLT respektowały robots.txt przy zbieraniu (README, artykuły zbiorów).

## Kategoria 3: świadoma zmiana językowa (`swiadoma`)

- Dobry Słownik — https://dobryslownik.pl/ (hasło „wulwa”, licencja, redakcja, daty).
- zaimki.pl (Rada Języka Neutralnego) — https://zaimki.pl/ (słowniki: terminologia, feminatywy; licencja).
- Rada Języka Polskiego — https://rjp.pan.pl/ (stanowisko o żeńskich formach nazw zawodów 2019 i nowsze; raporty o stanie języka).
- Poradnia językowa PWN — https://sjp.pwn.pl/poradnia (tylko dowód ręczny; licencja PWN).
- Poradnie uczelniane (UW, UŚ, UWr) — strony poradni.
- Plebiscyty: Słowo Roku (UW/RJP), Młodzieżowe Słowo Roku (już w #16; tylko jako odniesienie).
- Publikacje naukowe o feminatywach, języku inkluzywnym i nazwach anatomicznych (np. Bazhum, CEJSH, repozytoria uczelni, Google Scholar przez WebSearch) — czy dokumentują „wulwa”.
- Kontrola dodatnia w tej kategorii: hasło, które takie źródło na pewno ma (np. feminatyw `ministra` / `psycholożka`).

## Kategoria 4: metoda (`metoda`)

- Wyniki #16: `outputs/high-level-design.md`, `outputs/decision-log.md` (ADR-014–018), `analysis/findings/korpusy-04-zysk.md`.
- Kalibracja z #16: `scratchpad/nowe-slowa/kalibracja*.py/json`, `pokrycie.*`.
- ADR projektu: `docs/adr/ADR-007`, `ADR-008`, `ADR-012` (warstwy, progi jako udziały, przegląd operatora).
- Wyniki kategorii 1–3 tego badania (zależność; placeholder, jeśli jeszcze ich nie ma).

## Źródła już ocenione w #16 (tylko odniesienie)
OJ UW, WSJP PAN, PWN, Słowosieć 5.0, MSR, Miejski Słownik Slangu, NeoN, ParlaMint, Leipzig, PPC, FineWeb-2 i HPLT (próbki), MADLAD-400, OSCAR, CulturaX, CC-100, MoncoPL, Spokes.
