# Plebiscyty, RJP, Miejski Słownik Slangu, NeoN, źródła drukowane

## TL;DR
- Plebiscyty (Młodzieżowe Słowo Roku PWN, Słowo Roku UW i FJP) dają co roku 15–21 słów. To dobry sygnał „słowo jest popularne”, ale nie ma licencji ani danych. Tylko dowód ręczny.
- RJP nie publikuje listy nowych słów. Ważna jest dla nas jej reforma pisowni od 2026.
- Miejski Słownik Slangu: hejt, lockdown, boomer, cringe są; wulwy i ghostingu nie ma. Tylko kontrola, bez licencji.
- NeoN (IPI PAN, 2025) to gotowa metoda wykrywania neologizmów z progami. Danych nie udostępnia. Przydaje się zbieraczowi `projekt`.

## Kluczowe decyzje
- Żadne z tych źródeł nie wchodzi do `sources.json`.
- Progi NeoN (DF > 5, ≥ 5 wystąpień małą literą, ≥ 5 nie jako nazwa własna, długość 3–20, odległość edycyjna > 0,5) są punktem odniesienia dla metody w §5a planu.

## Otwarte pytania
- Brak oficjalnej strony z regulaminem Młodzieżowego Słowa Roku (`mlodziezowesloworoku.pl` nie istnieje w DNS, 2026-11-03). Listy znane tylko z prasy.

## 1. Młodzieżowe Słowo Roku (PWN)
- Prowadzący: PWN („PWN, czyli organizator konkursu” — https://www.telepolis.pl/wiadomosci/mlodziezowe-slowo-roku-2021-boomer-wyniki-glosowania, odczyt 2026-11-03).
- Cadence: rocznie od 2016. Jury wybiera finał (2024: 20 słów, 2025: 15), głosują internauci, wynik w grudniu. 2026: głosowanie 3–30.11 (prasa).
- Zwycięzcy (prasa, niepełna weryfikacja): 2018 dzban, 2019 alternatywka, 2020 brak (jury odmówiło), 2021 śpiulkolot, 2022 essa, 2023 rel, 2024 sigma, 2025 szpont/szponcić.
- Kontrola: **cringe** w finałowej 20 w 2024 (https://antyweb.pl/bambik-sigma-czy-cringe-oto-20-kandydatow-na-mlodziezowe-slowo-roku, odczyt 2026-11-03). Pozostałych kontroli nie sprawdzałem (brak pełnych list).
- Licencja: brak. Ocena: **tylko dowód ręczny** (sygnał popularności).

## 2. Słowo Roku (UW i Fundacja Języka Polskiego)
- Prowadzący: Fundacja Języka Polskiego i Uniwersytet Warszawski; sekretarz kapituły prof. Marek Łaziński. 15. edycja (2025): kapituła „dron”, internauci „kosmos”; 21 słów na liście (https://www.pap.pl/aktualnosci/wybrano-slowo-roku-2025-internauci-niezgodni-z-kapitula, odczyt 2026-11-03 przez wyszukiwarkę).
- Słowa roku to zwykle stare słowa w nowym użyciu, nie nowe lematy. Licencja: brak. Ocena: **tylko dowód ręczny**, mała przydatność.

## 3. Rada Języka Polskiego PAN
- https://rjp.pan.pl/ (odczyt 2026-11-03): brak listy neologizmów. Stopka: „2026 © Copyright by Rada Języka Polskiego PAN”.
- Ważne: „Mały słownik ortograficzny. Nowe reguły pisowni 2026” (16.12.2025). Zmiana pisowni może zmienić formy w listach; to temat dla `projekt`, nie źródło nowych słów.
- Ocena: **nie jest źródłem nowych słów**.

## 4. Miejski Słownik Slangu (tylko kontrola)
- https://www.miejski.pl — słownik użytkowników. Na stronie hasła nie znalazłem linku do licencji ani regulaminu (są: dodaj, kontakt, logowanie).
- Kontrole (`https://www.miejski.pl/slowo-<słowo>`, odczyt 2026-11-03):

| hejt | lockdown | covidowy | influencerka | antyszczepionkowiec | boomer | ghosting | cringe | wulwa |
|---|---|---|---|---|---|---|---|---|
| jest (200) | jest | 404 | 404 | 404 | jest (3 def.) | 404 (też `ghost`, `ghostowanie`) | jest (3 def.) | 404 |

Kontrola dodatnia: hejt, lockdown. Ocena: **tylko kontrola** (zgodnie z planem); nigdy źródło.

## 5. NeoN (IPI PAN) — metoda, nie dane
- Tomaszewska, Czerski, Żuk, Ogrodniczuk, „NeoN: A Tool for Automated Detection, Linguistic and LLM-Driven Analysis of Neologisms in Polish”, arXiv:2505.15426 (21.05.2025), ICCS 2025. Artykuł CC BY 4.0. https://arxiv.org/abs/2505.15426 (odczyt 2026-11-03).
- Korpusy odniesienia: NKJP (do 2010), KWJP (2011–2020), NEKST (do 2020), Wikipedia. Nowe teksty: 873 kanały RSS, ok. 2 miesiące, 233 538 dokumentów.
- Progi: DF > 5 dokumentów; ≥ 5 wystąpień małą literą; ≥ 5 nie jako nazwa własna; słowa z angielskiego słownika ≥ 5 kontekstów polskich; długość 3–20; min. odległość edycyjna do znanych słów > 0,5; wykluczenie słów ze słowników NKJP i KWJP; filtr LLM.
- Lejek: 200 696 → 1784 (po NKJP) → 1740 (po KWJP) → 1056 (po LLM). Precyzja na zbiorze anotowanym 0,796 → 0,917 po LLM; recall 0,699. Zbiór testowy z OJ UW.
- Dostęp: udostępniono tylko szablony promptów i zrzuty ekranu (Google Drive). Strona `zil.ipipan.waw.pl/NeoN-appendix` zablokowana. Kodu i listy brak.
- Kontrole: żadne z 9 słów nie występuje w tekście artykułu.
- Ocena: **metoda do porównania; brak danych**. Potwierdza, że KWJP to „okres 2011–2020”.

## 6. Źródła drukowane i zamknięte (krótko)
- IJP PAN: T. Smółkowa (red.), „Nowe słownictwo polskie. Materiały z prasy lat 2001–2005”, cz. 1–5, 2010–2014; Smółkowa, „Neologizmy we współczesnej leksyce polskiej”, 2001. Druk, stary okres. **Nie dotyczy**.
- Narodowy Fotokorpus Języka Polskiego: cytaty z lat 1901–2000. **Nie dotyczy** nowych słów.
- Nie znalazłem internetowego słownika neologizmów UJ, UŁ ani UG (wyszukiwanie 2026-11-03). Jedynym takim słownikiem online jest OJ UW.
