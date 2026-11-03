# Plan badania: źródła słów potocznych i świadomych zmian językowych

## TL;DR
- Badanie mieszane: przegląd licencji i źródeł (literatura) plus pomiar kontroli na lokalnych próbkach.
- Cztery zbieracze: (1) korpusy mowy i internetu, (2) Common Crawl i prawo TDM z większym pomiarem, (3) źródła świadomej zmiany (Dobry Słownik, RJP, poradnie), (4) metoda i kalibracja w procesie z #16.
- Każde źródło dostaje wiersz tabeli: licencja (cytat, URL, data odczytu), okres, rozmiar, pobieranie, daty, ryzyko SJP.pl, ocena.
- Kontrole liczymy wszędzie, gdzie się da. Każde „brak” ma obok wynik kontroli dodatniej.

## Kluczowe decyzje
- **Nie powtarzamy #16.** OJ UW, WSJP, PWN, Słowosieć, MSR, Miejski, NeoN, ParlaMint, Leipzig, PPC, MADLAD, OSCAR, CulturaX, CC-100, MoncoPL są już ocenione. Wracamy do nich tylko z nowym faktem (np. licencja Spokes).
- **FineWeb-2 i HPLT mierzymy jeszcze raz, ale na większej próbce** (do ~10 GB), bo próbki z #16 (56 MB, 150 MB) są za małe dla słów rzadkich.
- **Licencję tekstu oceniamy osobno od licencji opakowania** (wniosek #16). Pytanie prawne: lokalne liczenie (TDM, art. 26³ pr. aut.) vs publikacja liczb, przykładów i list.
- **Wulwa to osobny typ dowodu** (świadoma zmiana językowa), nie potoczność. Szukamy dla niej konkretnej drogi dowodu.
- **Wynik to dowód do karty kandydata i decyzji użytkownika** (D1-A z #16), nie automatyczne źródło leksemów.

## Otwarte pytania i ryzyka
- Polskie prawo TDM: brzmienie art. 26² / 26³ po nowelizacji z 2024 r. i wpływ zastrzeżeń (opt-out) w robots.txt / TDMRep. Ryzyko: to ocena, nie porada prawna; wynik „do decyzji użytkownika”.
- Napisy (OpenSubtitles/OPUS) mają niejasne prawa do tekstu; Reddit ma regulamin zabraniający masowego użycia. Mogą skończyć jako „tylko pomiar lokalny” albo „odpada”.
- Słowa angielskie (`cringe`, `boomer`, `ghosting`) dają fałszywe trafienia z tekstu angielskiego, nazw własnych i marek. Potrzebny filtr: mała litera, polska odmiana, kontekst polski.
- Dobry Słownik i podobne serwisy mogą nie mieć licencji danych. Wtedy tylko dowód ręczny (link + data odczytu).
- Wolne miejsce ok. 34 GB. Limit ~10 GB na kategorię; pobrania kasujemy po pomiarze.

## 1. Przegląd badania

**Pytanie.** Skąd literaki-slownik może brać wiarygodne dowody na słowa potoczne, internetowe i na świadome zmiany językowe, których nie widać w PPC, ParlaMint i Leipzig?

**Podpytania.**
1. Jakie polskie korpusy mowy potocznej i internetu mają czystą licencję i daty? (napisy, fora, Reddit, media społecznościowe, transkrypcje mowy, Wikipedia — strony dyskusji)
2. Czy lokalne liczenie w FineWeb-2/HPLT mieści się w TDM (dyrektywa 2019/790, art. 3–4; pr. aut. art. 26²–26³)? Co wolno opublikować: liczby, decyzję, krótki przykład?
3. Ile trafień mają kontrole w większej próbce FineWeb-2/HPLT, z podziałem na lata i po filtrze szumu?
4. Gdzie jest wulwa i podobne słowa świadomej zmiany? Jaka licencja, jaka wiarygodność, jak to traktować?
5. Jak włączyć te źródła do procesu z #16: warstwy, pola karty, progi, kalibracja?

**Typ.** Mieszany: literatura (licencje, prawo, słowniki) + pomiar techniczny (liczenie form).

**Zakres.** W zakresie: jak w `orchestrator-state.yml` (`research_context.scope.included`). Poza zakresem: SJP.pl, Wikisłownik, kontakt z autorami, zmiany w listach bez decyzji użytkownika.

**Ograniczenia.** Po polsku, zwięźle. Żadnej gry słownej poza Literaki i Kurnik. Bez kont, logowania, formularzy, maili. W HTTP bez danych użytkownika i bez udawania przeglądarki (domyślny User-Agent narzędzia lub uczciwy własny). Zbiory „gated” na HF odpadają. CPU-ciężkie pod `taskpolicy -b`, pobrane dane czytane przez `python -I` ze skryptów poza katalogiem danych. Dane surowe w scratchpadzie, poza Git. Nie commitujemy.

## 2. Metodologia

**Podejście główne.**
- Kategorie 1 i 3: przegląd źródeł (WebSearch, WebFetch, API HF bez tokenu) → cytat licencji dosłownie → wiersz tabeli → pomiar kontroli, jeśli dane da się pobrać bez konta.
- Kategoria 2: odczyt tekstu prawa (ISAP, EUR-Lex) i kart zbiorów → pomiar kontroli na większej próbce.
- Kategoria 4: odczyt projektu #16 i ADR → propozycja warstwy, pól karty i progów → kalibracja na kontrolach i na słowach SGJP.

**Pomiar kontroli (wspólny dla kategorii 1–2).**
- Formy kontroli z `scratchpad/nowe-slowa/kontrole.json` (pełne paradygmaty). Liczymy dokładne dopasowanie tokenu, osobno z małej i wielkiej litery.
- Dla każdego źródła: trafienia, dokumenty, ipm, podział na lata (jeśli są daty), udział hosta `sjp.pl`.
- Filtr szumu dla słów angielskich: tylko mała litera; odmiana polska (`boomerzy`, `ghostingu`) liczona osobno; odrzucenie dokumentów z przewagą angielskiego (wskaźnik: udział słów stop angielskich).
- 3–5 krótkich kontekstów na kontrolę do oceny trafności (tylko lokalnie, nie do repo).
- Każde „0” sprawdzamy kontrolą dodatnią w tym samym źródle (hejt, lockdown, antyszczepionkowiec).

**Strategie zapasowe.**
- Dane nie do pobrania bez konta → tylko opis i licencja, ocena „tylko dowód ręczny” albo „odpada”.
- Brak licencji → „tylko dowód ręczny” (link + data odczytu), jak OJ UW w #16.
- Za mało trafień w próbce → podać przedział ufności i oszacować potrzebną wielkość próbki.

**Ramy analizy.** Dla każdego źródła: (a) licencja tekstu i licencja zbioru, (b) co wolno: liczyć lokalnie / publikować liczby / cytować przykład / redystrybuować, (c) zasięg rejestru (potoczny, internetowy, świadoma zmiana), (d) daty, (e) wynik kontroli, (f) ryzyko SJP.pl, (g) ocena: `ALLOWED` / `do decyzji` / `tylko dowód ręczny` / `odpada`.

## 3. Źródła danych
Pełna lista w [`sources.md`](sources.md). Skrót:
- Lokalne: próbki i skrypty z #16 (`scratchpad/nowe-slowa/`), dokumenty projektu (`AGENTS.md`, `docs/adr/`, `.maister/docs/INDEX.md`), wyniki #16.
- Zewnętrzne: OPUS (OpenSubtitles, inne), HF (FineWeb-2, HPLT, SpeakLeash, zbiory PL z Twittera/forów), CLARIN-PL / PELCRA, BIGOS, ISAP, EUR-Lex, Dobry Słownik, RJP, poradnie językowe, zaimki.pl, publikacje naukowe.

## 4. Fazy badania

**Faza 1: szeroki przegląd (wszyscy zbieracze).** Lista kandydatów-źródeł w swojej kategorii, po 1 zdaniu i URL. Odrzucić od razu: wymaga konta, gated, SJP.pl, Wikisłownik.

**Faza 2: odczyt licencji i metadanych.** Cytat licencji dosłownie, URL, data odczytu. Okres, rozmiar, format, daty przy dokumentach.

**Faza 3: pomiar i dowód.** Pobranie (≤ ~10 GB na kategorię), liczenie kontroli, konteksty, kontrola dodatnia. Dla wulwy: gdzie jest, w jakiej formie, od kiedy, kto redaguje.

**Faza 4: weryfikacja.** Krzyżowo: czy kontrola widoczna w jednym źródle jest w drugim; czy licencja z karty zgadza się z licencją na stronie projektu; czy trafienia nie są szumem (angielski, marki, nazwy). Kasowanie pobrań po pomiarze (zapisać sumy kontrolne i rozmiary).

## 5. Gathering Strategy

### Instances: 4

| # | Category ID | Focus Area | Tools | Output Prefix |
|---|------------|------------|-------|---------------|
| 1 | potoczne-korpusy | Korpusy mowy potocznej i internetu PL z licencją i datami: OPUS/OpenSubtitles, Reddit, fora, media społecznościowe (PolEval, zbiory z Twittera/X), SpeakLeash, transkrypcje mowy (BIGOS, PELCRA, Spokes — tylko nowy fakt o licencji), strony dyskusji Wikipedii. Licencje + pomiar kontroli tam, gdzie da się pobrać bez konta. | WebSearch, WebFetch, Bash (curl, python -I), Read | potoczne |
| 2 | commoncrawl-tdm | FineWeb-2 i HPLT: licencja tekstu vs TDM (dyrektywa 2019/790 art. 3–4, pr. aut. art. 26²–26³ po noweli 2024), opt-out (robots.txt, TDMRep) i co wolno opublikować. Pomiar kontroli na większej próbce (do ~10 GB łącznie), podział na lata, filtr szumu angielskiego, udział `sjp.pl`. | WebSearch, WebFetch, Bash (curl, python -I, taskpolicy -b), Read | ccrawl |
| 3 | zmiana-swiadoma | Źródła świadomej zmiany językowej: Dobry Słownik (wulwa), zaimki.pl i podobne słowniki języka inkluzywnego, stanowiska RJP (feminatywy 2019 i nowsze), poradnie PWN/UW/UŚ, publikacje naukowe o feminatywach i języku inkluzywnym. Licencja, redakcja, daty, czy jest wulwa, jak traktować (dowód ręczny / sygnał / osobna kategoria). Plebiscyty „słowo roku” jako sygnał. | WebSearch, WebFetch, Read | swiadoma |
| 4 | metoda | Metoda w procesie z #16: nowa warstwa „potoczne / internet” i typ „zmiana świadoma”, nowe pola karty, progi dla źródeł nieformalnych, kalibracja (kontrole + odsetek słów SGJP, które przechodzą), ryzyko SJP.pl. Bazuje na `outputs/high-level-design.md`, `decision-log.md`, ADR projektu i wynikach #16; liczby z kategorii 1–2 wstawia jako zależność (placeholder, gdy brak). | Read, Grep, Bash (python -I na lokalnych danych) | metoda |

### Rationale
Trzy pierwsze kategorie to trzy różne rodzaje dowodu (korpus nieformalny, sieć ogólna, redagowane źródło świadomej zmiany) z różnymi problemami licencyjnymi. Common Crawl dostaje osobnego zbieracza, bo wymaga analizy prawa i ciężkiego pomiaru. Kategoria 4 przekłada wyniki na proces z #16; pracuje głównie na dokumentach lokalnych, więc nie dubluje 1–3. Brak osobnego zbieracza „konfiguracja” — w tym badaniu nie ma kodu do zmiany.

### Zasady wspólne dla zbieraczy
- Pliki: `analysis/findings/<prefix>-NN-<temat>.md`, każdy zaczyna się od TL;DR / Kluczowe decyzje / Otwarte pytania.
- Dane surowe i skrypty: `scratchpad/potoczne/<prefix>/` (dane w `dl-*`, skrypty w `scripts/`, osobno).
- Pobrania ≤ ~10 GB na kategorię; przed pobraniem `df -h`; po pomiarze kasować duże pliki.
- HTTP: bez danych użytkownika, bez udawania przeglądarki, bez kont i tokenów.
- Żadnej nazwy gry słownej poza Literaki i Kurnik. SJP.pl nie jest źródłem (wolno tylko mierzyć jego udział, by go wykluczyć).

## 6. Kryteria sukcesu
- Tabela źródeł z kompletem kolumn: licencja (cytat + URL + data odczytu), okres, rozmiar, pobieranie, daty, ryzyko SJP.pl, ocena. Minimum 8 nowych źródeł ocenionych w kat. 1 i 3 łącznie.
- Kontrole policzone w każdym mierzalnym źródle; każde „brak” z wynikiem kontroli dodatniej w tym samym źródle.
- FineWeb-2/HPLT: liczby kontroli na próbce ≥ 10× większej niż w #16, z latami i po filtrze szumu.
- Ocena prawna TDM z cytatami przepisów: co wolno lokalnie, co wolno opublikować, oznaczona jako „do decyzji użytkownika”.
- Wulwa: konkretna droga dowodu (źródło, URL, data odczytu, licencja) i jej ocena.
- Rekomendacja włączenia do procesu z #16: warstwa, pola karty, progi, kalibracja, wpływ na kolejkę.

## 7. Oczekiwane wyniki
- `outputs/research-report.md` — raport z tabelą źródeł, pomiarami i rekomendacją.
- `outputs/podsumowanie.md` — krótkie podsumowanie dla użytkownika z decyzjami do podjęcia.
- Ewentualnie szkice ADR (nowa warstwa, typ „zmiana świadoma”, polityka TDM) w `outputs/decision-log.md`.
