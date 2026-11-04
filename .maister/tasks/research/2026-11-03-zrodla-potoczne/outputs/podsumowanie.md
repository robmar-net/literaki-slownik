# Podsumowanie: źródła słów potocznych i świadomych zmian (#16)

## TL;DR
- Nie ma jednego źródła. Kandydaci przychodzą z lokalnych detektorów: napisów, Dobrego Słownika (DS), tezaurusa DS, zaimki.pl, plebiscytów i zgłoszeń. Common Crawl (FineWeb-2, HPLT) tylko ich potwierdza liczbami.
- Do publicznego repo idą tylko fakty: liczby, lata, liczba hostów, URL, data i własny opis. Tekstów nie publikujemy.
- Wulwa ma drogę wejścia: hasło DS wystarcza (Z1). Ostatnie słowo i tak należy do użytkownika, przez suplement v2.
- Wszystko działa poza buildem i opiera się na projekcie z #16, który nie jest jeszcze wdrożony.

## Kluczowe decyzje (użytkownik, 2026-11-04)
- **D2:** BAN-PL wycofany, lokalne dane skasowane.
- **D10:** cytaty z tekstów bez licencji zastąpione opisem. Historii Git nie przepisujemy.
- **1A:** do repo tylko fakty. Opt-out sprawdzamy na hostach wszystkich trafień kandydata, w dniu pomiaru i drugi raz przed wpisem. `Content-Signal: ai-train=no` zapisujemy jako flagę hosta, ale go nie wykluczamy.
- **2A (Z1):** przy zmianie świadomej hasło DS wystarcza. Badanie rekomendowało Z2.
- **zaimki.pl:** feminatywy i neutratywy trafiają do kolejki. Słowo, które jest tylko w zaimki.pl, potrzebuje jednego niezależnego dowodu użycia. Danych nie importujemy, bo licencja OQL nie pasuje do CC BY 4.0.
- **3C:** feminatywy w partiach, z osobnym werdyktem dla każdego słowa. Pierwsza partia to 122 słowa (zaimki.pl ∩ tezaurus DS).
- **4A:** CC tylko potwierdza, na próbce 1–2 mld słów, z progami v2 i ręczną oceną znaczeń.
- **5A:** każda pisownia ma osobny dowód i werdykt. `cringe` dostaje dwa tagi.

## Otwarte pytania
- Czy podklasa (b) mieści się w zasadach dopuszczalności Kurnika? Decyzję podejmuje użytkownik przy pierwszej karcie.
- Liczby z sieci są wstępne: policzono je przed filtrem opt-out, a ghosting tylko z 4 form zamiast 9.
- Numery ADR-019–023 zależą od numerów, które dostaną ADR-y z #16.

## Artefakty
- Raport: `outputs/research-report.md` (+ .html)
- Warianty: `outputs/solution-exploration.md` (+ .html)
- Projekt: `outputs/high-level-design.md` (+ .html)
- Szkice ADR-019–023: `outputs/decision-log.md` (+ .html)
- Ustalenia: `analysis/findings/` (17 plików), synteza `analysis/synthesis.md`

## Następne kroki
1. Zadanie rozwojowe dla #16: wdrożenie projektu z badania `2026-11-03-zrodla-nowych-slow`. Najpierw osobny bump SGJP 20261018, potem suplement v2, manifest wykrywania, kolejka i karta.
2. Do kroku 1 dochodzą elementy z tego badania: nowe pola karty, filtr opt-out, tabela progów, ADR-019–023.
3. Przed pierwszą kartą potoczną: przeliczyć ghosting z 9 formami, ujednolicić B4, policzyć próbkę 1–2 mld słów po opt-out.
4. Pierwsza partia zmiany świadomej: wulwa i 122 feminatywy (3C).
5. Wiki: strony z #16 oraz sekcja „Źródła potoczne i świadome zmiany” na stronie `Nowe-slowa`.
6. Sprzątanie: małe pobrania skasowane 2026-11-04. W scratchpadzie zostały skrypty i liczby JSON.
