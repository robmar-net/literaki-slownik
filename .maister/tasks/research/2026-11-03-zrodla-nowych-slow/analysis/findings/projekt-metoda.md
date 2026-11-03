# projekt: metoda wykrywania kandydatów, progi skalibrowane lokalnie

## TL;DR
- Szkic z §5a da się wykonać już dziś na parze NKJP (do 2010) → KWJP (2011–2020). Progi **F ≥ 20, 1-DP ≥ 0,005, ≥ 2 z 3 gatunków, wzrost g ≥ 10** łapią wszystkie 5 kontroli celu (4 w SGJP + antyszczepionkowiec).
- Wynik: 530 lematów spoza SGJP, po dwóch filtrach szumu 374, z potwierdzeniem w Słowosieci 125.
- Trafność w próbce 60 lematów (ocena ręczna): ok. 65% to prawdziwe leksemy, z potwierdzeniem w Słowosieci 23 z 24, bez niego 16 z 36. Szum to głównie błędne lematy z automatycznej lematyzacji KWJP.
- Wulwa, ghosting, cringe i boomer są poniżej progu (KWJP F ≤ 5). Progów pod nie nie stroiłem. Złapie je dopiero korpus z tekstami po 2020 roku.

## Kluczowe decyzje
- **Miara wzrostu:** g = (F_lemat_KWJP / 81,66 mln) / ((NKJP_forma_podstawowa + 0,5) / 246,15 mln), podzielone przez medianę tej wartości dla lematów SGJP o F ≥ 50 (3,233; n = 43 914). Dla typowego słowa g = 1. Próg 10 odpowiada mniej więcej 95. percentylowi lematów SGJP (p95 surowego = 31,3, czyli 9,7 po normalizacji).
- **Słowosieć porządkuje, nie odcina.** Bez niej odpadłyby kontrole lockdown i covidowy.
- **Wynik to lista do decyzji, nie wpis.** Zgodnie z §4.4 nic nie trafia do list automatycznie.

## Otwarte pytania
- Kalibracji „w przedziale sprzed wejścia do SGJP” z §5a nie da się zrobić lokalnie, bo mamy jeden eksport SGJP (20260823). Zastępuję ją kalibracją „przed 2011 / 2011–2020”. Daty dodania haseł może dać tylko historia wydań SGJP (kategoria `neolog`).
- Miara g jest zgrubna. Porównuje lemat KWJP z formą podstawową NKJP, więc zawyża wynik słów, które rzadko stoją w formie podstawowej (np. `sidło`, `odchrząknąć`). Przy tych samych progach przechodzi 2 313 lematów, które są już w SGJP. Uczciwa miara wymaga zliczeń lematów w obu okresach tym samym tagerem.
- Użycie NKJP w tej metodzie wykracza poza zakres ADR-006 (POP i POP0). Trzeba to dopisać decyzją.
- Próbkę trafności oceniał jeden agent, bez konkordancji. Pewność średnia.

## 1. Metoda (wersja doprecyzowana)
1. **Wejście:** lista lematów z okresu późniejszego (dziś KWJP lemma all + 3 gatunki) i lista z okresu wcześniejszego (dziś NKJP 1grams, formy po obcięciu interpunkcji).
2. **Pula:** lemat spoza SGJP i spoza suplementu, zapisany małą literą, tylko litery, długość ≥ 3, klasa otwarta (`subst, adj, adv, fin, praet, inf, ger, adja, depr`). Dziś to 12 130 lematów.
3. **Próg użycia:** F ≥ 20 (≈ 0,25 ipm), 1-DP ≥ 0,005, F > 0 w ≥ 2 z 3 podkorpusów (fakt, fikcja, publicystyka).
4. **Próg nowości:** g ≥ 10.
5. **Filtry szumu:**
   - (a) lemat jest formą SGJP innego leksemu (np. `nienarodzony` → `narodzić`, `szarawar` → `szarawara`);
   - (b) lemat leży 1 edycję od formy SGJP, która ma w KWJP orth_lc co najmniej 10 razy więcej wystąpień (np. `wszystkio` ~ `wszystko`, `zrozumiać` ~ `zrozumieć`).
   - Kontrole przepuszczone przez filtry, jakby nie było ich w SGJP, przechodzą wszystkie 7 (hejt, lockdown, covidowy, influencerka, hejter, pandemia, antyszczepionkowiec).
6. **Kolejność:** najpierw z potwierdzeniem w Słowosieci 4.5 (polska LU, pos 1–4), potem reszta, malejąco po F.
7. **Krok decyzji użytkownika:** dla każdego kandydata pokazujemy lemat, klasę, F, ipm, gatunki, NKJP, g, Słowosieć i 2–3 przykłady użycia. Przykłady pochodzą z wyszukiwarki KWJP (ręcznie) albo z korpusu z dozwoloną licencją. Werdykt: dodać (suplement v2, wzór fleksji z podobnego leksemu SGJP), odrzucić albo odłożyć do nowego SGJP. Decyzja trafia do pliku dowodów z sha256 (`projekt-zasady-zrodel.md` §4 B).

## 2. Kalibracja na kontrolach
| Kontrola | F | 1-DP | gatunki | NKJP forma podst. | g | Słowosieć | Wynik (F≥20, 1-DP≥0,005, ≥2 gat., g≥10) |
|---|---|---|---|---|---|---|---|
| hejt | 366 | 0,083 | 3 | 2 | 136,5 | tak | łapie |
| lockdown | 241 | 0,029 | 3 | 0 | 449,4 | nie | łapie |
| covidowy | 116 | 0,012 | 3 | 0 | 216,3 | nie | łapie |
| influencerka | 24 | 0,008 | 3 | 0 | 44,7 | tak | łapie |
| antyszczepionkowiec | 34 | 0,015 | 3 | 0 | 63,4 | tak | łapie |
| boomer | 5 | 0,002 | 2 | 8 | 0,5 | nie | nie (próg F i 1-DP) |
| ghosting | <5 | – | – | 1 | – | nie | nie (brak w KWJP) |
| cringe | <5 | – | – | 0 | – | nie | nie (brak w KWJP) |
| wulwa | <5 | – | – | 2 (nazwisko) | – | nie | nie (brak w KWJP) |
| srom (kontrola starego słowa) | 92 | 0,025 | 3 | 46 | 1,8 | tak | odpada na g, poprawnie |

Margines: F ≥ 30 gubi influencerkę (24), więc 20 to najwyższy bezpieczny próg. Najniższe g wśród kontroli to 44,7, więc g ≥ 10 ma ponad 4-krotny zapas. Najniższe 1-DP to 0,008, a próg wynosi 0,005.

## 3. Wielkość listy (lematy spoza SGJP)
| Progi (1-DP ≥ 0,005, ≥ 2 gat.) | przed filtrami | po (a)+(b) | po filtrach + Słowosieć |
|---|---|---|---|
| F ≥ 10, g ≥ 5 | 1 225 | 849 | 294 |
| F ≥ 20, g ≥ 5 | 647 | 462 | 194 |
| **F ≥ 20, g ≥ 10 (propozycja)** | **530** | **374** | **125** |
| F ≥ 30, g ≥ 10 | 337 | 246 | 89 |
| F ≥ 50, g ≥ 10 | 183 | 137 | 58 |

Bez progu wzrostu przy F ≥ 20 jest 1 851 lematów. Kryterium nowości odcina więc ok. 70%: stare luki i błędy lematyzacji (`trzewie`, `gusło`, `obeznany`).

## 4. Co wychodzi (przykłady, F ≥ 20, g ≥ 5, po filtrach)
- **Najczęstsze:** neoliberalny 486, prorosyjski 453, postsowiecki 434, ponadgimnazjalny 422, performans 371, superbohater 351, crossover 327, antysystemowy 183, elektromobilność 159, cyberbezpieczeństwo 123, planszówka 118, kryptowaluta 108, ledowy 106, antysmogowy 104, fanpage 96. Cztery pierwsze to luki znane z rundy 4.
- **Szum, który przechodzi:** `satelit`, `aktywo`, `wielkanoca`, `realium`, `lubiać`, `kwitnieć` (ger), `dzieciakko`, `derok`, `liceł`. To błędne lematy z automatycznej lematyzacji KWJP. Słowosieć usuwa prawie wszystkie.
- **Próbka losowa 60** (seed 1103): 39 prawdziwych leksemów (np. transfobia, mikrobiom, postprawda, karcianka, kalistenika, korpoludek, offshoring, prekaryzacja) i 21 szumu (np. rękoczyna, wnętrznoście, podzieme, bębyć, followers).
- Wiele trafień to formacje z `anty-`, `post-`, `trans-`, `mikro-`. §2.4 zabrania dodawać je z reguły, więc każda wymaga osobnej decyzji.

## 5. Wymagania wobec źródła dla wersji „po 2020”
Wymagania pod te same progi, do sprawdzenia przez kategorie `neolog` i `korpusy`:
- teksty z datą; co najmniej 2 okresy, ostatni od 2021;
- da się pobrać zliczenia lematów albo form, a licencja pozwala opublikować pochodną listę słów (CC BY, CC0 albo ODC-By). Inaczej źródło jest BLOCKED (§4.5);
- przy korpusie sieciowym metadane domen, żeby wykluczyć sjp.pl i jego kopie;
- rozmiar: przy progu 0,25 ipm okres ≥ 80 mln tokenów daje F ≥ 20. Mniejszy korpus wymaga progu ipm, nie F;
- ten sam tager w obu okresach, żeby g nie mierzył różnicy lematyzacji.

Bez takiego źródła metoda działa tylko na latach 2011–2020. Wulwy, ghostingu ani cringe nie złapie.

## Pliki pomiarów
Wszystkie w `/private/tmp/claude-501/-Users-robmar-Projects-Literaki/3ae5c44e-c8df-4ef9-924a-bcb0e5eaf7f8/scratchpad/nowe-slowa/`:
`kalibracja2.py` i `kalibracja2.json` (g, siatka progów, kontrole), `kalibracja3.py` i `kalibracja3.json` (filtry szumu, próbki), `pokrycie.py` i `pokrycie.json` (lematy SGJP o wysokim g). Plik `kalibracja.py` to pierwsza wersja z błędną miarą wzrostu (0/0 → 1). Nie cytuję go.
