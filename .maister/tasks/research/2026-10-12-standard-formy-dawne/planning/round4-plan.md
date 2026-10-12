# Runda 4: kontrola rodzin i zależności POP

## TL;DR
Użytkownik przyjął wyniki rundy 3 jako podstawę dalszych decyzji i zlecił zalecany audyt.
Badamy mechanizm ubytków POP, wszystkie 110 rodzin propozycji i osobno 12 obecnych przyjęć.
Wyniki zostaną zapisane i opublikowane w komentarzu #4. To nadal research.

## Key Decisions
- Zasada współczesnego znaczenia i odpowiadającej mu współczesnej odmiany pozostaje kierunkiem.
- Paczka 2382 form, cofnięcia, zmiany metody POP i wdrożenie pozostają niezatwierdzone.
- Dwa niezależne przeglądy delegowane zgodnie z orchestrator-patterns §1. Koordynator bada POP i sprawdza pokrycie delegacji.
- Brak zainstalowanych szablonów specjalistów Maister; użyto zwykłych agentów z jawnie opisanymi kontraktami. Osobny kontekst nie oznacza niezależności modeli ani źródeł.

## Open Questions / Risks
- Pełny przegląd rodzin może zawęzić propozycję. Pierwotna runda 3 pozostaje zachowana.
- Zmiana składu ograniczonego rankingu jest naturalna; trzeba rozdzielić ją od transferu dowodu między homonimami.
- Brak dowodu w przeglądzie nie dowodzi nieistnienia słowa. Korpusy i słowniki pozostają częściowo zależne.

## Pytania i tory

| Tor | Pytanie | Źródła | Koniec badania |
|---|---|---|---|
| POP — koordynator | Na jakim etapie wypada każda grupa? Dlaczego cofnięcie dag usuwa dekagram z POP0? | pop.py, ADR-007, konfiguracja/testy, przypięte dane i poprzednie symulacje | Wyjaśnienie przyczyn, pełne przypisanie 2430 ubytków do mechanizmu, izolowane kontrole i konsekwencje dla decyzji |
| Rodziny — family_review | Czy dowód współczesnego znaczenia uzasadnia wskazaną odmianę? | Wszystkie 110 rodzin, źródła pierwotne i lokalne odpowiedzi SGJP/KWJP | 110 jawnych ocen, zakresy zawężeń i niewiadomych, kontrola liczby dotkniętych form |
| Obecne przyjęcia — current_twelve_review | Czy właściwa analiza lub inna legalna interpretacja ratuje każdy zapis? | 12 zapisów i ich analizy, szersze celowane konteksty oraz słowniki | 12 ocen z dowodem i ograniczeniami, bez automatycznego usuwania |

## Walidacja i publikacja

1. Odtworzyć poprzednie liczby z zapisanego wejścia i zbadać ślad jednostek, miary, progu i przycinania.
2. Zachować surowe korpusy w ignorowanym cache. Publikować własne notatki, metryki, identyfikatory i odsyłacze.
3. Zweryfikować pokrycie wszystkich rodzin i 12 zapisów oraz rozliczyć każdą zmianę rekomendacji.
4. Zsyntetyzować raport z pewnością, kontrdowodami i zamkniętym zakresem dalszych decyzji; odświeżyć HTML i dashboard.
5. Commit i push artefaktów w repo słownika, komentarz #4 i odczyt kontrolny komentarza.
6. Bramka użytkownika: przyjęcie wyników i wskazanie kierunku dalszej decyzji. Bez implementacji.

## Własność plików

- Koordynator: stan, plan, rejestr źródeł, synteza, raport/HTML, dashboard, komentarz, round4_pop.py i pomiary POP.
- family_review: round4/family-review.md, round4/family-review.json, round4_family_review.py, ignorowany cache round4-family.
- current_twelve_review: round4/current-twelve.md, round4/current-twelve.json, round4_twelve.py, ignorowany cache round4-twelve.
