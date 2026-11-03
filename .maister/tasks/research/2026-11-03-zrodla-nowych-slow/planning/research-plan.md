# Plan badania: źródła nowych, popularnych słów

## TL;DR
- Badanie mieszane: przegląd źródeł w sieci i dopasowanie do zasad projektu.
- Trzech zbieraczy: `neolog` (obserwatoria i słowniki nowych słów), `korpusy` (korpusy i listy frekwencyjne z lat 2015+), `projekt` (zasady, wejście źródła, szkic metody).
- Każde źródło sprawdzamy na tym samym zestawie kontrolnym 9 słów: 4 są w SGJP, 5 nie ma.
- Wynik: tabela ≥10 źródeł z licencją i oceną zgodności, wyniki kontroli, metoda z progami i krokiem decyzji użytkownika.

## Kluczowe decyzje
- **Trzy kategorie, nie cztery.** Konfiguracja i kod projektu to jeden obszar (`projekt`). Źródła zewnętrzne dzielimy na dwa: słowniki i obserwatoria (wynik ręczny, opisowy) oraz korpusy (wynik liczbowy). Każde ma inną licencję i inny sposób użycia.
- **Zestaw kontrolny zmierzony z góry** w lokalnym SGJP 20260823 i KWJP100 (lematy, all). Zbieracze nie wybierają własnych słów. Mogą dodać najwyżej 2 słowa i muszą je oznaczyć.
- **SJP.pl nie jest źródłem ani kontrolą.** Nie sprawdzamy w nim słów kontrolnych. Skażenie SJP.pl mierzymy tylko jako ryzyko w korpusach sieciowych.
- **Ograniczenie §2.4 i §4.4 specyfikacji v3:** korpus nie może sam dodać leksemu spoza SGJP. Metoda daje więc tylko listę kandydatów do decyzji użytkownika. Wejście do listy idzie przez `sgjp-supplement.tab` albo nowe źródło leksykalne, zawsze po decyzji.

## Otwarte pytania / ryzyka
- Większość świeżych korpusów sieciowych ma warunki „research only” albo licencję samego opakowania (np. CC0 na metadane), a nie na tekst. Pochodna lista słów może być dozwolona, a tekst nie. To trzeba ustalić osobno dla każdego.
- Korpusy z Common Crawl mogą zawierać strony SJP.pl. Trzeba sprawdzić, czy da się je wykluczyć po domenie.
- Słowniki nowych słów (Obserwatorium UW, PWN) zwykle nie mają licencji do pobrania hurtowego. Wtedy nadają się tylko jako ręczny dowód w decyzji, nie jako wejście generatora.
- Okres KWJP100 trzeba potwierdzić. Od niego zależy, co znaczy „przed KWJP”.

## 1. Pytanie i zakres
**Pytanie:** jakie wiarygodne, naukowe źródła w sieci notują nowe, szybko popularne słowa polszczyzny i jak ich użyć w literaki-slownik, by wychwytywać je przed SGJP i KWJP?

**Podpytania:**
1. Kto w Polsce rejestruje neologizmy? Jak często, na jakiej licencji, czy da się pobrać dane?
2. Które korpusy i listy frekwencyjne obejmują lata 2015+ i pozwalają na podział w czasie?
3. Czy pochodną listę słów z danego korpusu wolno opublikować w projekcie?
4. Czy kontrole (tabela niżej) są w każdym źródle?
5. Jak wejść ze źródłem do `sources.json` (dowody, sha256, `expected_counts`) i jaki status dostanie?
6. Jak wykrywać kandydatów: jaka miara, jakie progi, jaki krok decyzji?

**W zakresie:** obserwatoria i słowniki nowych słów, nowsze wydania WSJP i SGJP online, korpusy 2015+, n-gramy, metody wykrywania, licencje.
**Poza zakresem:** SJP.pl jako źródło, Wikisłownik, kontakt z autorami i z innymi grupami, zmiany w listach.
**Ograniczenia:** tylko licencje zgodne z AGENTS.md i `sources.json`; w tekstach nie wymieniamy gier słownych poza Literaki i Kurnik.

## 2. Zestaw kontrolny (zmierzony 2026-11-03)
Pomiar: `cache/sgjp/sgjp-20260823.tab.gz` (lemat) i `cache/kwjp/kwjp100-slowa-lemma-all.csv.gz`.

| Słowo | SGJP 20260823 | KWJP100 lemat (F) | Rola |
|---|---|---|---|
| hejt | jest | 366 | kontrola dodatnia: nowe, już w SGJP |
| lockdown | jest | 241 | kontrola dodatnia, słowo z 2020 |
| covidowy | jest | 116 | kontrola dodatnia, słowo z 2020 |
| influencerka | jest | 24 | kontrola dodatnia, rzadsza |
| antyszczepionkowiec | brak | 34 | luka SGJP przy obecności w KWJP |
| boomer (pokolenie) | brak (jest tylko `bumer` m3) | 5 | na progu KWJP |
| ghosting | brak | <5 | zapożyczenie po 2015 |
| cringe | brak | <5 | zapożyczenie, slang |
| wulwa | brak | <5 | przypadek wyjściowy |

Każdy zbieracz podaje dla każdego źródła: jest / brak / nie da się sprawdzić, z liczbą i datą odczytu. Każde „brak” wymaga kontroli dodatniej w tym samym źródle (np. hejt).

## 3. Metoda
- **Główna:** przegląd źródeł w sieci (WebSearch, WebFetch): strony projektów, dokumentacja, licencje, artykuły.
- **Uzupełniająca:** odczyt lokalny (cache, `config/generator`, ADR, specyfikacja v3) i małe pomiary w scratchpadzie.
- **Zapas:** gdy strona źródła nie ma licencji, szukamy jej w repozytorium danych (CLARIN-PL, Hugging Face, Zenodo, GitHub). Brak licencji = `BLOCKED`, nie zgadujemy.
- **Rama oceny (dla każdego źródła):** prowadzący · licencja tekstu i licencja pochodnej · okres · rozmiar · częstość aktualizacji · pobieranie (hurt, API, tylko przeglądarka) · podział w czasie · ryzyko SJP.pl · wynik kontroli · ocena: `ALLOWED-kandydat` / `tylko dowód ręczny` / `BLOCKED` z powodem.

## 4. Fazy
1. **Odkrycie:** lista kandydatów na źródła w każdej kategorii (sources.md jest punktem startu, nie listą zamkniętą).
2. **Odczyt:** strony licencji i dokumentacji; zapis cytatu licencji z URL i datą.
3. **Pomiar:** kontrole w każdym źródle, w którym da się je sprawdzić bez pobierania całego korpusu (wyszukiwarka, API, n-gramy). Pobrania większe niż ok. 2 GB tylko po opisie w ustaleniach, bez wykonywania.
4. **Weryfikacja:** zgodność z §3–4 specyfikacji v3 i `sources.json`; sprzeczności między źródłami zapisane wprost.

## 5. Strategia zbierania

### Instancje: 3

| # | Category ID | Zakres | Narzędzia | Prefiks |
|---|---|---|---|---|
| 1 | neolog | Obserwatoria i słowniki nowych słów: Obserwatorium Językowe UW, projekty „Nowe słowa w polszczyźnie”, nowsze hasła WSJP, zmiany w SGJP online, PWN, Miejski Słownik Slangu (tylko kontrola). Prowadzący, licencja, cadence, pobieranie, kontrole. | WebSearch, WebFetch | `neolog` |
| 2 | korpusy | Korpusy i listy 2015+: MoNKa, ParlaMint-PL, polskie części OSCAR/HPLT/CulturaX/FineWeb-2/MADLAD, Spokes, korpusy monitorujące i prasowe, zrzuty Wikipedii i Wikinews (CC BY-SA), n-gramy Common Crawl, Google Books Ngram. Licencja pochodnej listy, okres, rozmiar, pobieranie, podział w czasie, ryzyko SJP.pl, kontrole. | WebSearch, WebFetch, Bash (małe próbki) | `korpusy` |
| 3 | projekt | Zasady i dopasowanie: licencje dziś w `sources.json`, statusy, ADR-006 i ADR-011, §2–4 specyfikacji v3, wejście źródła (pola rejestru §4.5, `evidence`, `sha256`, `expected_counts`), rola `sgjp-supplement.tab`. Szkic metody: frekwencja w przedziałach czasu, progi, kontrole, krok decyzji. Pomiar kontroli w lokalnym SGJP, KWJP (też podkorpusy), NKJP 1grams, Słowosieci. | Read, Grep, Bash | `projekt` |

Pliki wyjściowe: `analysis/findings/<prefiks>-*.md`. Każdy plik zaczyna się od `## TL;DR` / `## Kluczowe decyzje` / `## Otwarte pytania` (puste pomijamy).

### Uzasadnienie
Źródła słownikowe i korpusowe różnią się wynikiem (hasło a liczba), licencją i sposobem wejścia do projektu. Trzeci zbieracz pracuje tylko lokalnie, więc nie dubluje sieci. Więcej instancji podzieliłoby korpusy sztucznie.

### Zasady dla zbieraczy
- Nie piszemy do autorów źródeł ani do innych grup. Nie zakładamy kont, nie wysyłamy formularzy.
- SJP.pl nie otwieramy. Nie używamy też PoliMorfa ani innych zasobów pochodnych od SJP.pl.
- Wikisłownik pomijamy.
- Licencję cytujemy dosłownie z URL i datą. Licencja witryny to nie licencja danych.
- Nazw gier słownych poza Literaki i Kurnik nie piszemy, także w cytatach (skracamy je „[…]”).
- Pobrania i próbki tylko w scratchpadzie, nie w repo.

## 5a. Szkic metody do sprawdzenia (hipoteza dla `projekt`)
1. Weź korpus z datami i dozwoloną pochodną. Policz lematy w przedziałach (np. 2015–2018, 2019–2022, 2023+).
2. Kandydat: lemat spoza SGJP (i spoza `sgjp-supplement.tab`), z F ≥ próg w ostatnim przedziale, wzrostem względem wcześniejszego i obecnością w ≥ N domenach lub ≥ 2 rodzajach tekstu.
3. Odsiej szum: nazwy własne (wielka litera w większości wystąpień), obce zdania, literówki (bliski znany lemat), kod.
4. Kalibracja: progi mają złapać 4 kontrole „w SGJP” w przedziale sprzed ich wejścia do SGJP i co najmniej antyszczepionkowca. Wynik dla wulwy, ghostingu i cringe podajemy, ale nie stroimy pod nie progów.
5. Krok decyzji: lista kandydatów z liczbami i przykładami idzie do użytkownika. Wpis do suplementu tylko po jego decyzji.
`projekt` ocenia, czy ten szkic da się zrobić na źródłach, które znajdą `neolog` i `korpusy`, i proponuje liczby.

## 6. Kryteria sukcesu
1. Tabela ≥10 źródeł z licencją, okresem, pokryciem, pobieraniem i oceną zgodności.
2. Wynik 9 kontroli w każdym źródle, w którym to możliwe, z kontrolą dodatnią przy każdym „brak”.
3. Metoda wykrywania z miarą, progami (liczbowo), kontrolami i krokiem decyzji użytkownika.
4. Ryzyka: licencja pochodnej, szum (literówki, nazwy własne, kod), skażenie SJP.pl, dryf lematyzacji.
5. Jasna odpowiedź, które źródła mogą wejść do `sources.json` i z jaką rolą (`lexical` czy `corpus_evidence`).

## 7. Wyniki
- `outputs/research-report.md`: tabela źródeł, wyniki kontroli, metoda, ryzyka, warianty do decyzji.
- Bez zmian w listach i w `config/generator`.
