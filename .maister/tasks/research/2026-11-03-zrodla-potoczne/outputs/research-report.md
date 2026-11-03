# Raport: skąd brać słowa potoczne i świadome zmiany językowe

Typ: mieszany (literatura + pomiar) · Data: 2026-11-03 · Zadanie: `2026-11-03-zrodla-potoczne` · Kontynuacja #16 (`2026-11-03-zrodla-nowych-slow`)

## TL;DR
- Nie ma jednego źródła. Dowód to **trzy części**: Dobry słownik (DS, dowód ręczny), FineWeb-2/HPLT (tylko liczby, art. 26³ pr. aut.) oraz małe źródła z czystą licencją (BAN-PL, dyskusje plwiki). Napisy OpenSubtitles mają najmocniejszy sygnał (7/7 kontroli), ale nie mają licencji tekstu, więc tylko pomiar lokalny.
- **Wulwa ma drogę dowodu:** DS (od I–II 2024), tezaurus DS, 6 hostów w sieci (2018–2024), dyskusje plwiki (2023). Rekomendacja: typ „zmiana świadoma” z progiem **Z2**.
- **Common Crawl potwierdza podejrzane słowo, ale go nie odkrywa:** wśród nowych grup tylko ok. 4% to słowa potoczne, ok. 40% to spam i zlepki.
- Do decyzji użytkownika jest 12 punktów: D1–D10 poniżej, D11–D12 w § 8. Liczby z sieci są wstępne: liczone przed filtrem opt-out, a ghosting jest zaniżony.

## Kluczowe decyzje
Każdy punkt czeka na decyzję użytkownika. Rekomendacja jest pogrubiona.
- **D1. OpenSubtitles (brak licencji tekstu):** **tylko lokalny detektor do kolejki**. W karcie liczba filmów i link do opensubtitles.org, bez cytatów. Powód: brak licencji, duplikaty, tłumaczenia.
- **D2. Hasło do archiwów BAN-PL:** **przyjąć użycie lokalne** (liczby w karcie z atrybucją CC BY 4.0, bez danych w repo). Powód: autorzy chronią dane przed scrapingiem i trenowaniem LLM. Liczenie form tym nie jest. Hasło jest jawne w repo autorów.
- **D3. Common Crawl / FineWeb-2 / HPLT (art. 26³, opt-out):** **publikować tylko liczby, URL i datę z własnym opisem**. Konteksty tylko lokalnie. Najpierw sprawdzić opt-out hostów dowodów kandydata. Powód: liczby to informacja z TDM; kontekst to już cytat (art. 29, 34, 35).
- **D4. Typ dowodu „zmiana świadoma”:** **Z2** (dowód ręczny + minimalny niezależny dowód użycia). Z1 wpuszcza słowa bez użycia. Przy Z3 wulwa odpada.
- **D5. Tezaurus DS (GPL-2.0+/LGPL 2.1):** **tylko sygnał lokalny** „jest w tezaurusie DS vX”, bez importu listy. Powód: copyleft, a wiele form `-lożka` powstało ze wzoru.
- **D6. zaimki.pl (OQL v1.4):** **nie używać w repo**. Najwyżej dowód ręczny przy jednym słowie. Powód: zakazy co do celu i podmiotu przechodzą na odbiorców. Dane są normatywne.
- **D7. Rodzaj gramatyczny cringe:** **oba tagi**, przymiotnik nieodmienny (jak `cool`) i rzeczownik n (jak `selfie`). Dla gry to i tak jedna forma.
- **D8. bumer jako homograf:** **osobny werdykt dla każdej pisowni** we wspólnej karcie. `bumer` m1 dodaje 1 formę (`bumerzy`), `boomer` 11.
- **D9. Bramki B1–B8:** **przyjąć progi v2 jako start**. B7 zostaje tymczasowy (≥20 trafień i ≥0,05 ipm). Kalibrację powtórzyć po filtrze opt-out i na próbce 1–2 mld słów.
- **D10. Cytaty z napisów i forum już w publicznym repo:** **zastąpić opisem** w `potoczne-01` i `potoczne-03`. Pliki są w `origin/main`.
- Dodatkowo do decyzji: feminatywy hurtem czy słowo po słowie (rekomendacja: **słowo po słowie**, S3 w swiadoma-05) i źródła z licencją NC (Spokes, hate_speech_pl): dziś mało przydatne, więc **odłożyć**.

## Otwarte pytania / ryzyka
- Ocena prawna (TDM, cytat, OQL, GPL) to odczyt zbieracza, **nie porada prawna** (ccrawl-01).
- Nie wiadomo, czy art. 26³ liczy stan opt-out w chwili crawla, czy w chwili naszego pobrania. Przyjęto wariant bezpieczniejszy, czyli dzień pobrania (ccrawl-04).
- Liczby z sieci: próbka 8× zamiast 10×, liczone przed opt-out; `ccrawl-03` na danych pośrednich. Ghosting w `ccrawl-02` i `potoczne-03` liczony z 4 form zamiast 9.
- Teksty, które DS cytuje jako użycie wulwy, nie zostały przeczytane bezpośrednio.
- Czy słowa podklasy (b) mieszczą się w zasadach dopuszczalności Kurnika: decyzja użytkownika (swiadoma-05).

---

## Spis treści
1. Podsumowanie
2. Cele badania
3. Metodologia
4. Ustalenia
5. Analiza
6. Proces: jak włączyć źródła
7. Wnioski
8. Decyzje dla użytkownika (szczegóły)
9. Rekomendacje
10. Załączniki

## 1. Podsumowanie
**Co badano.** Skąd brać dowody na słowa potoczne, internetowe i świadome zmiany językowe, których nie widać w PPC, ParlaMint i Leipzig.
**Jak.** Cztery kategorie zbieraczy, 17 plików ustaleń. Każdą licencję zacytowano z URL i datą. Kontrole liczono lokalnie: wulwa, ghosting, cringe, boomer oraz kontrole dodatnie hejt, lockdown, antyszczepionkowiec.
**Wynik.** Źródła potoczne: sygnał jest odwrotnie proporcjonalny do czystości licencji. Świadoma zmiana: DS daje dowód ręczny, sieć daje rzadkie, ale niezależne użycie. Common Crawl nadaje się do karty, nie do wykrywania.

## 2. Cele badania
Pytanie główne jak wyżej. Podpytania (research-plan.md):
1. Korpusy mowy potocznej i internetu z licencją i datami → § 4.1.
2. TDM dla FineWeb-2/HPLT: co wolno lokalnie i co opublikować → § 4.2.
3. Kontrole na większej próbce, z latami i po filtrze szumu → § 4.3.
4. Wulwa i inne słowa świadomej zmiany → § 4.4.
5. Włączenie do procesu z #16 → § 6.

Poza zakresem: SJP.pl, Wikisłownik (odroczony), kontakt z autorami, zmiany w listach.

## 3. Metodologia
- Przegląd źródeł z cytatem licencji (potoczne-02, ccrawl-01, swiadoma-01..02).
- Pomiar dokładnych form z `kontrole.json`, małą i wielką literą osobno, z filtrem tekstu angielskiego. Każde „0” ma obok kontrolę dodatnią.
- Kalibracja bramek na Leipzig news (5 mln zdań, 67,9 mln słów; metoda-05).
- Dane: OpenSubtitles 2022–2023 (62,6 mln słów), kafeteria 13% (415,7 mln), plwiki 54%, FineWeb-2 187,7 mln i HPLT v3 475,0 mln słów (potoczne-03, ccrawl-02). Transfer ok. 4,9 GB (potoczne) i ok. 8,9 GB (ccrawl). Pobrania skasowane, z wyjątkiem ok. 32 MB małych plików w scratchpadzie (potoczne-03).
- Ramy: (a) licencja tekstu i zbioru osobno, (b) co wolno, (c) rejestr, (d) daty, (e) kontrole, (f) SJP.pl, (g) ocena.

## 4. Ustalenia

### 4.1 Źródła potoczne (potoczne-01, -02, -03)
| Źródło | Licencja tekstu | Kontrole celu (wulwa/ghosting/cringe/boomer, małą literą) | Daty | Ocena |
|---|---|---|---|---|
| OpenSubtitles 2022–2023 | brak („add a link”) | 7 / 10 / 7 / 65 | rok filmu | do decyzji (D1) |
| BAN-PL (Wykop) | CC BY 4.0, „strictly for research”, hasło | 0 / 0 / 4 / 3 (hejt 31) | 2019–06.2023 | ALLOWED z zastrzeżeniem (D2) |
| plwiki, dyskusje (54%) | CC BY-SA 4.0 | 5 / 0 / 2 / 22 (głównie okręty) | rok podpisu | ALLOWED, niska przydatność |
| SpeakLeash kafeteria (13%) | „conditional license” | 3 / 3 (technika) / 0 / 8 (guma) | brak | do decyzji, odłożyć |
| PolEval 2019, hate_speech_pl, PolEmo, Common Voice | unknown / NC / CC BY / CC0 | prawie same 0, kontrole dodatnie też 0 lub prawie 0 | brak | mało przydatne |
| Reddit, X | regulamin zabrania | — | — | odpada |
| BIGOS, PELCRA | bramka HF | — | — | odpada |
| Spokes (nowy fakt) | CC BY-NC 3.0 | niezmierzone | 2000–2013 | do decyzji (NC), za stary |

Pewność: wysoka dla licencji, średnia dla liczb (pomiary częściowe, maszyna obciążona).

### 4.2 Prawo TDM (ccrawl-01, ccrawl-04) — do decyzji, nie porada prawna
| Czynność | Podstawa | Ocena zbieracza |
|---|---|---|
| Lokalne liczenie form | art. 26³ ust. 1 (każdy, także komercyjnie), jeśli brak zastrzeżenia | dozwolone; kasować po pomiarze (ust. 3) |
| Publikacja liczb, lat, liczby domen | wynik TDM, nie utwór; ODC-By 4.3, HPLT CC0 | niskie ryzyko |
| URL + data dokumentu dowodowego | fakt | niskie ryzyko, po sprawdzeniu opt-out hosta |
| Krótki kontekst | art. 29 + 34 + 35 | ryzyko średnie, rekomendacja: nie publikować |
| Redystrybucja próbek | brak podstawy | nie |

- Projekt nie jest organizacją badawczą z art. 26², więc stosuje się art. 26³ i art. 4 dyrektywy. Zastrzeżenie umowne wiąże, bo art. 7 ust. 1 nie obejmuje art. 4.
- Opt-out dziś (200 hostów FineWeb-2): TDMRep 0/200; CCBot zablokowany na 34/100 największych (37,6% ich dok.) i 11/100 losowych. Jawny polski tekst zastrzeżenia (np. Agora) ma 8/200 hostów.
- Wniosek syntezy (moja ocena, pewność niska): dyrektywa mówi o utworach „dostępnych zgodnie z prawem” (art. 4 ust. 1). Napisy to amatorskie tłumaczenia filmów, więc ich legalność jest niepewna. To dodatkowy powód, by napisy zostały tylko detektorem lokalnym (D1).

### 4.3 Kontrole w sieci (ccrawl-02)
| Słowo | FW2 małą (dok.) | ipm | HPLT małą (dok.) | ipm | Uwagi |
|---|---|---|---|---|---|
| hejt (+) | 1009 (685) | 5,40 | 1718 (1216) | 3,68 | |
| lockdown (+) | 1019 (697) | 5,52 | 1740 (1155) | 3,74 | 0 przed 2020 |
| antyszczepionkowiec (+) | 124 (96) | 0,67 | 181 (113) | 0,39 | |
| boomer | 30 (17) | 0,19 | 125 (98) | 0,27 | dużo szumu: manicure, nicki |
| ghosting | 32 (25) | 0,18 | 77 (39) | 0,17 | znaczenie relacyjne tylko w 2/27 i 5/45 kontekstów; **4 formy** |
| cringe | 9 (8) | 0,05 | 16 (15) | 0,03 | prawie same potoczne |
| wulwa | 3 (2) | 0,016 | 3 (2) | 0,006 | anatomia człowieka; 6 hostów 2018–2024 z #16 |

- Ekstrapolacja na całe zbiory: wulwa ok. 1 200 (FW2) i ok. 900 (HPLT); cringe ok. 3 500 i 4 600. Do kart wystarczy próbka 1–2 mld słów (ccrawl-02).
- SJP.pl: ≤0,008% dokumentów, 0 trafień kontroli.
- Wykrywanie nowych słów (ccrawl-03, dane pośrednie): 6 239 form → 314 grup. W 150 największych grupach: terminy 45%, potoczne 4%, spam 25%, zlepki 15%, marki 11%.

### 4.4 Świadoma zmiana (swiadoma-01..05, metoda-02)
- **Dobry słownik:** wulwa (id 226245, dodana I–II 2024 „na życzenie abonentów”). Ma też cringe, boomer, hejt, lockdown i antyszczepionkowca, nie ma ghostingu. Wszystkie prawa zastrzeżone → dowód ręczny.
- **Tezaurus DS 2026-10-01:** wolny (GPL-2.0+ wg pliku txt, LGPL 2.1 wg README). Ma wulwę, wersja z 2008 r. jej nie ma. 1761 haseł bez lematu w SGJP.
- **zaimki.pl:** OQL v1.4. Wulwa tylko w 2 radach. 2439 unikalnych feminatywów spoza SGJP; tylko 8 ma podane źródła.
- **RJP:** stanowisko z 2019 r. (model `-ka`, `-ini/-yni`; „ministra” nietypowa) i opinia z 2026 r. o ogłoszeniach. To reguła dla klasy słów, nie dowód dla słowa.
- **Publikacje:** 5 artykułów, w żadnym nie ma wulwy. Plebiscyty: Słowo Roku 2024 „koalicja”, 2025 „dron” → tylko sygnał.
- **Braki w SGJP 20261018:** wulwa, chirurżka, kardiolożka, premierka, transpłciowy, tranzycja, transfobia, ciałopozytywność i inne. SGJP ma już psycholożkę, ministerkę, gościnię, niebinarny, byłom.

**Wulwa we wszystkich źródłach**
| Źródło | Wynik | Plik |
|---|---|---|
| KWJP, PPC, ParlaMint | 0 | metoda-02 (za #16) |
| Leipzig news | 0 (kontrole dodatnie: hejt 778, lockdown 1 211) | metoda-05 |
| NKJP | 4× `wulw`, 2× `wulwa`, w #16 ocenione jako nazwisko | metoda-02 |
| FineWeb-2 / HPLT | 3 + 3 (2 + 2 dok.), razem z #16 6 hostów | ccrawl-02 |
| OpenSubtitles 2022–2023 | 7 zdań, częściowo duplikaty | potoczne-03 |
| plwiki dyskusje / artykuły | 7 (2023) / 158 (głównie zoologia) | potoczne-03 |
| kafeteria | 3 | potoczne-03 |
| BAN-PL | 0 (kontrola dodatnia hejt 43,5 ipm) | potoczne-03 |
| DS / tezaurus DS | tak / tak | swiadoma-01 |
| zaimki.pl / RJP / publikacje | tylko w 2 radach / brak / 0 | swiadoma-02, -03 |
| ankieta 2022 (HelloZdrowie) | 1% deklaruje użycie; metoda nieznana | swiadoma-03 |

### 4.5 Tabela ustaleń
| # | Ustalenie | Kategoria | Pewność | Źródła |
|---|---|---|---|---|
| F1 | Napisy: najmocniejszy sygnał, brak licencji | potoczne | wysoka / prawo niska | potoczne-01..03 |
| F2 | BAN-PL i plwiki: czyste, ale małe lub mało potoczne | potoczne | wysoka | potoczne-01..03 |
| F3 | Liczenie lokalne CC zgodne z art. 26³; publikacja liczb niskie ryzyko | prawo | średnia | ccrawl-01 |
| F4 | Opt-out dziś częsty na dużych hostach | prawo | średnia | ccrawl-04 |
| F5 | Kontrole celu w sieci są rzadkie i zaszumione | pomiar | średnia | ccrawl-02 |
| F6 | CC jako wykrywacz daje ok. 4% potocznych | pomiar | średnia | ccrawl-03 |
| F7 | Wulwa w DS i w tezaurusie DS; #16 się mylił | świadoma | wysoka | swiadoma-01 |
| F8 | zaimki.pl na OQL, dane normatywne | świadoma | wysoka | swiadoma-02 |
| F9 | Progi v2: 37/43 zapożyczeń, 0/20 słów angielskich | metoda | średnia (małe listy) | metoda-05 |
| F10 | „Nowe formy w grze” zmienia wagę decyzji | metoda | wysoka | metoda-03, -04 |

## 5. Analiza

### 5.1 Wzorce
- **Licencja vs sygnał:** im mocniejszy sygnał potoczny, tym słabsza licencja.
- **Opakowanie ≠ tekst:** ODC-By, CC0 i MIT nie obejmują tekstu autorów.
- **Szum znaczeniowy:** ghosting (monitory), boomer (guma, manicure, okręty, nicki).
- **Słownik wyprzedza korpus:** DS ma hasła wcześniej niż korpusy prasowe (lockdown 2020, boomer 2022, wulwa 2024).
- **Wzór ≠ użycie:** angelolożka, neutratywy.
- **Opt-out rośnie po crawlu.**

### 5.2 Sprzeczności między plikami
| Sprzeczność | Wyjaśnienie |
|---|---|
| Wulwa: Leipzig 0 vs sieć 6 hostów | Wiadomości nie piszą o anatomii. Progi kalibrowane na Leipzig nie nadają się dla zmiany świadomej. |
| Ghosting: 4 formy (`kontrole.json`) vs 9 (wzór `ranking`) | ccrawl-02 i potoczne-03 mogą zaniżać ghosting. metoda-05 liczyła 9. |
| ccrawl-03 na danych pośrednich (~535 mln słów) vs próbka końcowa 662,7 mln | Liczby 6 239 i 314 nie są końcowe, hosty zaniżone. |
| Liczby sprzed filtra opt-out | ccrawl-02 i ccrawl-03 spadną po wykluczeniu hostów z zastrzeżeniem. |
| Wulwa #16 HPLT 19 vs teraz 3 | 19 to wzorzec prefiksowy z zoologią. Formy dokładne: 2. |
| Trzy filtry „tekst angielski” | potoczne-03, ccrawl-02 i metoda-01 mają różne definicje. Liczby nie są w pełni porównywalne. |
| Progi hostów: B6 ≥10, Z2(b) ≥5, ccrawl-03 ≥5 | Potrzebna jedna tabela progów. |
| „ministra”: RJP nietypowa, DS ją ma | Karta pokazuje oba dowody. |
| Konteksty „tylko lokalnie” vs cytaty w potoczne-01/03 | Decyzja D10. |

### 5.3 Kluczowe spostrzeżenia
1. **Dwa typy, dwa progi.** Wulwa: 0,006–0,016 ipm wobec szkicu B7 ≥0,05 ipm. Pod Z3 odpada. Pod Z2(b) ma ≥5 hostów (6), ale nie ma ≥10 trafień (6 w próbce). Z2(c) jest prawdopodobnie spełniony przez publikacje cytowane w DS. Trzeba je przeczytać.
2. **Napisy to detektor, nie dowód.** Duplikaty wersji, kalka tłumacza, brak licencji.
3. **CC to potwierdzenie.** Próbka 1–2 mld słów z filtrem znaczenia wystarczy do kart. Do wykrywania potrzebny jest filtr spamu.
4. **Gra zawęża decyzję.** B1 odcina apostrof, myślnik i q/v/x. `bumer` m1 dodaje 1 formę, `ministra` 4.
5. **Feminatywy: duża pula z pułapką wzoru.** DS ∩ zaimki.pl to 122 formy. To najmocniejszy start podklasy (a), ale z kontrolą użycia.

### 5.4 SWOT
| Mocne | Słabe |
|---|---|
| DS daje datowany dowód ręczny; czyste BAN-PL i plwiki; kontrole dodatnie datują się poprawnie; ryzyko SJP.pl małe | Najlepszy sygnał bez licencji; pomiary częściowe; szum znaczeniowy; brak filtra spamu |
| **Szanse** | **Zagrożenia** |
| Próbka 1–2 mld słów da karty dla każdej kontroli; tezaurus DS jest kwartalny jak ADR-018; KP od 24.12.2025 przyspieszy feminatywy w korpusach | Opt-out rośnie; ryzyko prawne cytatów; zarzut stronniczości przy słowach świadomej zmiany; copyleft/OQL przy imporcie |

## 6. Proces: jak włączyć źródła do #16

### 6.1 Miejsce w procesie
Dwa nowe strumienie wpadają do tej samej kolejki: **potoczne/internet** (warstwa liczbowa) i **zmiana świadoma** (typ dowodu). Oba działają poza buildem. Do list słowo wchodzi tylko decyzją użytkownika przez suplement v2 (D1-A, ADR-016). Rytm kwartalny zostaje (ADR-018). Manifest wykrywania (ADR-015) dostaje osobne pola: licencja tekstu, licencja opakowania i zakres „tylko liczenie lokalne” albo „liczby do publikacji” (metoda-01).

### 6.2 Bramki B1–B8 (metoda-01, progi v2 z metoda-05)
| # | Bramka | Próg |
|---|---|---|
| B1 | alfabet gry | twardo |
| B2 | brak w SGJP i suplemencie (lemat i formy) | twardo |
| B3 | mała litera poza początkiem zdania | ≥70% |
| B4 | dokument polski | ≥50% surowych zostaje |
| B5a / B5b | polska odmiana / polski kontekst | ≥10% i ≥2 formy / ≥70% |
| B6 | rozrzut po hostach | ≥10 hostów, największy ≤35% |
| B7 | częstość | tymczasowo ≥20 trafień i ≥0,05 ipm |
| B8 | hosty wykluczone (SJP.pl, kopie, „znaczenie słowa”, słownik świadomej zmiany) | tylko raport |

### 6.3 Typ „zmiana świadoma”
- Podklasy: (a) feminatyw systemowy, (b) świadoma zmiana z użyciem, (c) forma normatywna bez użycia, której nie dodajemy (swiadoma-04, -05).
- Z2: dowód ręczny + jeden z warunków:
  - (a) ≥3 użycia w korpusie z licencją;
  - (b) ≥5 niezależnych hostów i ≥10 trafień po B1–B5;
  - (c) publikacja redagowana (metoda-02).
- Bez kwalifikatora w suplemencie. Typ dowodu zapisujemy w rejestrze decyzji.

### 6.4 Wypełnienie placeholderów z `metoda-*` (na podstawie ccrawl i potoczne)
| Placeholder | Wartość z pomiaru | Plik |
|---|---|---|
| Czy wolno liczyć i publikować liczby z sieci (metoda-01) | liczyć lokalnie tak; liczby niskie ryzyko; konteksty nie | ccrawl-01 |
| B7 na zbiorach nieformalnych | w próbce CC: cringe 0,03–0,05 ipm (9/16 trafień) → na granicy; boomer i ghosting powyżej, ale głównie szum; wulwa poniżej | ccrawl-02 |
| Wulwa pod Z2 (metoda-02) | (a) nie; (b) hosty tak (6), trafienia nie (6 < 10); (c) do sprawdzenia | ccrawl-02, swiadoma-01 |
| Licencja i redakcja źródeł świadomej zmiany | DS: prawa zastrzeżone, redakcja 4 osób z tytułami naukowymi; tezaurus GPL/LGPL; zaimki.pl OQL | swiadoma-01, -02 |
| Kalibracja celu (metoda-05) | niewykonana na sieci; wymaga próbki 1–2 mld słów po opt-out | ccrawl-02, -04 |

### 6.5 Pierwsza kolejka (swiadoma-04, -05)
Kolejka startowa: wulwa, transpłciowy, transpłciowość, tranzycja, transfobia, ciałopozytywność, chirurżka, kardiolożka. Wszystkie są w DS i nie ma ich w SGJP. Do tego kontrole potoczne: boomer/bumer, cringe/krindż, ghosting. Przed kartą każdy kandydat potrzebuje pomiaru w sieci.

## 7. Wnioski
**Odpowiedź na pytanie.**
- Słowa potoczne: FineWeb-2/HPLT (liczby po opt-out) + BAN-PL i dyskusje plwiki (czyste) + napisy jako detektor lokalny.
- Świadome zmiany: Dobry słownik jako dowód ręczny + tezaurus DS jako sygnał + minimalne użycie z sieci lub z publikacji (Z2).

Żadne z tych źródeł nie jest automatycznym źródłem leksemów.

| Wniosek | Pewność |
|---|---|
| Sieć potwierdza, ale nie wykrywa słów potocznych | średnia |
| Wulwa ma drogę dowodu przez Z2 | średnia–wysoka |
| Lokalne liczenie CC zgodne z art. 26³ | średnia (nie porada prawna) |
| Napisy nie mogą być dowodem w repo | wysoka |
| Feminatywy: przegląd słowo po słowie | średnia |

## 8. Decyzje dla użytkownika (szczegóły)
| # | Decyzja | Opcje | Rekomendacja | Ryzyko | Pliki |
|---|---|---|---|---|---|
| D1 | OpenSubtitles bez licencji tekstu | odpada / detektor lokalny / liczby w karcie | detektor lokalny; w karcie najwyżej liczba filmów + link | prawne; duplikaty; kalka | potoczne-02, -03 |
| D2 | Hasło do archiwów BAN-PL | przyjąć lokalnie / odrzucić | przyjąć lokalnie; liczby z CC BY; bez danych w repo | intencja autorów (anty-scraping/LLM) | potoczne-02 |
| D3 | CC / FineWeb-2 / HPLT | tylko liczby / liczby + konteksty / nic | liczby + URL + data + własny opis; filtr opt-out | brak orzecznictwa; moment zastrzeżenia | ccrawl-01, -04 |
| D4 | Typ dowodu Z1 / Z2 / Z3 | Z1 sam słownik; Z2 + użycie; Z3 progi potoczne | Z2 | Z1: słowa bez użycia; Z3: wycina cel | metoda-02 |
| D5 | Tezaurus DS (GPL/LGPL) | sygnał lokalny / import listy | sygnał lokalny | copyleft; formy ze wzoru | swiadoma-01 |
| D6 | zaimki.pl (OQL) | nie używać / dowód ręczny / import | nie używać w repo | warunki OQL na odbiorcach | swiadoma-02 |
| D7 | Rodzaj cringe | adj nieodm. / n / oba | oba | brak; 1 forma w grze | metoda-04 |
| D8 | bumer homograf | wspólny werdykt / osobne | osobne werdykty, karta wspólna | mylące „+1 forma” | metoda-03, -04 |
| D9 | Bramki B1–B8 | v1 / v2 / inne | v2 jako start; B7 tymczasowy | małe listy kalibracyjne | metoda-01, -05 |
| D10 | Cytaty z napisów/forum w publicznym repo | zostawić / zastąpić opisem | zastąpić opisem | już w `origin/main` | potoczne-01, -03 |
| D11 | Feminatywy (a) hurtem czy pojedynczo | hurt wg wzoru / słowo po słowie | słowo po słowie | wzór daje słowa bez użycia | swiadoma-05 |
| D12 | Źródła NC (Spokes, hate_speech_pl, blogi) | użyć / odłożyć | odłożyć (stare, mało trafień) | ocena komercyjności | potoczne-01 |

## 9. Rekomendacje
| Priorytet | Działanie | Nakład | Uzasadnienie |
|---|---|---|---|
| 1 | Decyzje D1–D4 z użytkownikiem | mały | blokują resztę |
| 2 | D10: usunąć cytaty z napisów i forum z `potoczne-01/03` (osobny commit, po decyzji) | mały | spójność z D3 |
| 3 | Przeliczyć ghosting z 9 formami; ujednolicić filtr angielski (B4) | mały | sprzeczności S2, S6 |
| 4 | Lista hostów z opt-out albo sprawdzenie hostów dowodów kandydata | średni | warunek art. 26³ |
| 5 | Próbka CC 1–2 mld słów z filtrem znaczenia i spamu; pomiar 8 kandydatów świadomej zmiany | duży (czas CPU) | kalibracja B7 i Z2 |
| 6 | Przeczytać teksty, które DS cytuje dla wulwy (Z2(c)) | mały | domyka dowód wulwy |
| 7 | Napisy: liczyć filmy (IMDb ID), nie zdania | mały | duplikaty |
| 8 | Szkice ADR: warstwa potoczna, typ „zmiana świadoma”, polityka TDM | średni | utrwalenie decyzji |

## 10. Załączniki

### A. Pliki ustaleń
`analysis/findings/`: potoczne-01-przeglad, potoczne-02-licencje, potoczne-03-pomiar, ccrawl-01-prawo, ccrawl-02-kontrole, ccrawl-03-nowe-slowa, ccrawl-04-optout, swiadoma-01-dobry-slownik, swiadoma-02-zaimki-rjp-poradnie, swiadoma-03-publikacje-plebiscyty, swiadoma-04-kandydaci-sgjp, swiadoma-05-propozycja-procesu, metoda-01-warstwa-potoczne, metoda-02-zmiana-swiadoma, metoda-03-karta, metoda-04-zapozyczenia-gra, metoda-05-kalibracja. Synteza: `analysis/synthesis.md`.

### B. Główne URL (odczyt 2026-11-03; pełne cytaty w plikach ustaleń)
- DS wulwa: https://dobryslownik.pl/slowo/wulwa/226245/ ; tezaurus: https://dobryslownik.pl/pobierz/
- zaimki.pl OQL: https://zaimki.pl/license
- RJP 2019: https://rjp.pan.pl/stanowisko-rady-jezyka-polskiego-przy-prezydium-pan-w-sprawie-zenskich-form-nazw-zawodow-i-tytulow-przyjete-na-posiedzeniu-plenarnym-rady-25-listopada-2019-r/
- Pr. aut. (Dz.U. 2025 poz. 24): https://api.sejm.gov.pl/eli/acts/DU/2025/24/text.pdf
- FineWeb-2: https://huggingface.co/datasets/HuggingFaceFW/fineweb-2 ; HPLT v3: https://hplt-project.org/datasets/v3.0
- OPUS OpenSubtitles: https://opus.nlpl.eu/legacy/OpenSubtitles-v2018.php ; BAN-PL: https://github.com/NASK-NLP/BAN-PL

### C. Luki
- Pomiary częściowe: kafeteria 13%, plwiki 54%, HPLT `7_1` przerwany, próbka CC 8×.
- Brak pomiaru kandydatów świadomej zmiany w sieci.
- Nie sprawdzono regulaminów forów ani hostów dowodów.
- Wayback niedostępny, więc daty w DS wzięto z bloga i z id haseł.
- `metoda-*` mają placeholdery (wypełnione tu, w § 6.4).
- Brak `outputs/podsumowanie.md` i szkiców ADR przewidzianych w planie.

### D. Dane surowe (scratchpad, poza Git)
`scratchpad/potoczne/{potoczne,ccrawl,swiadoma,metoda}/`. Ok. 32 MB małych pobrań czeka na ręczne skasowanie (potoczne-03).
