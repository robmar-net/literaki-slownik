# Brief: źródła słów potocznych i świadomych zmian językowych

## TL;DR
- Poprzednie badanie (#16) dało proces wykrywania nowych słów w PPC, ParlaMint i Leipzig. Te korpusy nie widzą słów potocznych i internetowych ani świadomych zmian językowych.
- Szukamy wiarygodnych dowodów dla takich słów, z licencją, która pozwala ich użyć, i bez kontaktu z autorami.
- Kontrole: wulwa, ghosting, cringe, boomer (cel) oraz hejt, lockdown, antyszczepionkowiec (kontrole dodatnie).

## Kluczowe decyzje
- Wynik to dowód do decyzji użytkownika (karta kandydata, suplement v2 — D1-A z #16), nie automatyczne źródło leksemów.
- „Wulwa” jest osobnym typem: świadoma zmiana językowa (słownik języka nierozróżniającego, np. Dobry Słownik), nie potoczność ani rejestr poselski.

## Otwarte pytania
- Czy korzystanie lokalne z FineWeb-2/HPLT (bez publikowania tekstu, tylko liczby lub decyzja) mieści się w licencji i w TDM UE 2019/790?
- Czy istnieją polskie korpusy mowy potocznej lub internetu z czystą licencją i datami (np. napisy, fora, Reddit, transkrypcje)?
- Jak traktować słowniki świadomej zmiany (Dobry Słownik): dowód ręczny, sygnał, czy osobna kategoria?

## Pytanie badawcze
Skąd literaki-slownik może brać wiarygodne dowody na słowa potoczne, internetowe i na świadome zmiany językowe, których nie widać w korpusach parlamentarnych i prasowych (PPC, ParlaMint, Leipzig)?

## Typ: mieszany (literatura + pomiar techniczny)

## Zakres
- W zakresie: korpusy mowy i internetu; Common Crawl (FineWeb-2, HPLT) i licencja tekstu; słowniki i poradniki świadomej zmiany; plebiscyty i obserwatoria jako sygnał; metody wykrywania; kalibracja na kontrolach.
- Poza zakresem: SJP.pl; Wikisłownik (odroczony); kontakt z autorami (formularze, konta, maile); zmiany w listach bez decyzji użytkownika.
- Ograniczenia: po polsku, zwięźle; żadnej gry słownej poza Literaki i Kurnik; CPU-ciężkie pod `taskpolicy -b`; `python -I`; dane surowe poza Git; w nagłówkach HTTP bez danych użytkownika i bez podszywania się pod przeglądarkę.

## Kryteria sukcesu
- Tabela źródeł: licencja (cytat + URL + data odczytu), okres, rozmiar, pobieranie, podział w czasie, ryzyko SJP.pl, ocena.
- Kontrole policzone w każdym mierzalnym źródle, każde „brak” z kontrolą dodatnią.
- Dla wulwy: konkretna droga dowodu i jej ocena.
- Rekomendacja, jak włączyć źródła do procesu z #16 (warstwy, karta, decyzja).
