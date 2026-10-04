# Model danych i odtwarzalny proces — projekt audytu

## TL;DR
Proponujemy relacyjną bazę audytową, z osobnymi formami, interpretacjami i dowodami korpusowymi.
Najprostszy pierwszy generator może używać SQLite oraz strumieniowego importu, bez usługi sieciowej.
Eksporty słów będą wynikami decyzji, nie jedynym miejscem przechowywania informacji.
Jest to projekt; nie utworzono produkcyjnej bazy ani kompletu słowników.

## Key Decisions
- Identyfikatory wszystkich jednostek są związane z wydaniem źródła.
- Częstość należy do jednostki korpusowej; relacja wiele-do-wielu nie powiela wartości.
- Dane porównawcze nie są wejściami procesu budowania; w pierwszym etapie ich nie pobieramy.

## Open Questions / Risks
- Wybór SQLite to rekomendacja na podstawie 7,46 mln rekordów, nie wynik benchmarku bazy. Przed wdrożeniem należy zmierzyć indeksowanie, rozmiar i czas wyjaśniania decyzji.
- Eksport SGJP nie dostarcza jawnego wewnętrznego ID leksemu; przechowujemy niezmieniony identyfikator lematu i ograniczenie mapowania.
- Wersja i warunki NKJP, semantyka złożonych kwalifikatorów oraz polityka części skrótowców wymagają wyjaśnienia.

## Jednostki i ograniczenia

| Encja | Klucz i zawartość | Kontrola |
|---|---|---|
| SourceArtifact | ID, URL, wydanie, retrieved_at, SHA256, rozmiar, licencja, dowód, rola, status | BLOCKED wyklucza użycie konstrukcyjne |
| Lexeme | source_id + oryginalny identyfikator lematu, oddzielnie napis bazowy i sufiks | nigdy nie usuwaj homonimii z klucza |
| SurfaceForm | source_id + oryginalny zapis; NFC, klucz, długość | normalizacja nie usuwa znaków |
| Interpretation | forma, leksem, tag surowy, rozłożone kategorie, nazwa i kwalifikatory surowe | zachowaj alternatywy; nie traktuj przecinków i pionowych kresek jako dowolnie wymiennych |
| Derivation | wynik, identyfikatory składników, source_rule, konfiguracja, generator_version | tylko zatwierdzona rekonstrukcja fleksyjna, bez nowych leksemów |
| CorpusEvidence | source_id + numer rekordu, representation, unit, POS, gatunek, F/IPM/ARF/DP/DP_norm/1-DP/total_freq/Dice, pełny raw_record; osobno derived_rank | liczba i dostępność oddzielne; zapisuj mianownik; ranga wyliczona nie zastępuje miary źródłowej |
| EvidenceLink | evidence_id, cel, metoda, kandydaci, pewność i wersja mapowania | brak kopiowania całego F do każdego kandydata |
| VariantDecision | wersja polityki, interpretation_id, accept/reject/unresolved, wszystkie przyczyny | forma zaakceptowana tylko przy jednej interpretacji przechodzącej całość |
| KnowledgeScore | przypisana baza, lexeme/form, model, miary, braki, wynik | projekt na później; wynik jest podzbiorem bazy |
| TopicScore | leksem, temat, model, konfiguracja, dowód, niepewność | brak generowania leksemów przez klasyfikator |
| BuildManifest | wejścia, hashe kodu/config, środowisko, komendy, seed, hashe wyjść, blokady | jeden przebieg ma niezmienne wejścia |

SQLite może przechowywać relacje i indeksy po formie, identyfikatorze lematu i evidence_id. Surowe wartości tagów pozostają dostępne obok parsowanych. Import w transakcjach porcjowanych; raporty i końcowe zbiory deterministycznie sortowane. Nie wybieramy teraz klastra, API ani formatu binarnego klienta.

## Przepływ

```text
oficjalne źródło → audyt wersji/licencji → manifest artefaktu
  → cache surowy (poza Git) → walidowany import → baza audytowa
  → decyzje interpretacji → agregacja form → zamrożony kandydat
  → raport i eksport wraz z atrybucjami

KWJP → jednostki korpusowe → EvidenceLink → modele znajomości (później)
NKJP → BLOCKED do wyjaśnienia warunków
benchmark → oddzielny proces po zamrożeniu (później)
```

Konstruktor przyjmuje jawny manifest dozwolonych wejść, nie skanuje całego katalogu po plikach. Pliki porównawcze przechowywane w osobnym katalogu bez uprawnień/ścieżki wejściowej konstrukcji. Test kontraktu odrzuca źródło z rolą `benchmark`, niezależnie od nazwy pliku. Sam ten projekt nie stanowi dowodu wdrożenia izolacji.

## Braki, dopasowanie i poziomy

`OBSERVED` oznacza zachowaną wartość opublikowaną. `ABSENT_OR_BELOW_PUBLICATION_THRESHOLD` wolno ustawić dopiero po potwierdzeniu zakresu i porównywalności jednostki. W innym przypadku `NOT_IN_PUBLISHED_LIST` lub `UNMATCHED`. `NOT_APPLICABLE` dotyczy miary nieistniejącej na danym poziomie; `UNAVAILABLE` — źródła niepozyskanego albo BLOCKED. Nigdy `NULL → 0` bez dowodu.

Łączenie zaczyna od formy bez zmiany znaków i od pary napis lematu/POS. Homonimy zachowują odrębne ID. Niejednoznaczna zgodność tworzy grupę kandydatów, nie rozdziela częstości. Osobowe formy przeszłe SGJP i segmenty korpusowe wymagają odrębnego mapowania; nie da się odzyskać częstości ich połączeń z samych unigramów. Nie sumujemy all z gatunkami, ARF, DP ani rang. Modele COMMONNESS, LEXEME/FORM/HYBRID i tematy pozostają następnymi etapami.

Późniejsze losowe poziomy wiedzy: deterministyczny hash z (seed, baza, osobowość, model, jednostka) daje trwałą rangę; monotoniczny próg daje zagnieżdżenie przy tym samym seedzie. Model musi być sprawdzony na próbkach, a nie na intuicji o kompetencji człowieka.

## Manifest wydania

Przykładowy kształt (placeholdery nie są pomiarem):

```json
{
  "schema_version": 1,
  "build_id": "<unikalny-przebieg>",
  "created_at": "<rzeczywisty-UTC>",
  "stage": "audit",
  "source_artifacts": [{"id": "<id>", "sha256": "<hash>", "status": "ALLOWED", "role": "construction"}],
  "code": {"commit": "<commit>", "scripts_sha256": {}},
  "configuration_sha256": "<hash>",
  "environment": {"python": "<wersja>", "unicode": "<wersja>", "sort_locale": "C"},
  "commands": [],
  "seed": null,
  "outputs": [{"path": "<plik>", "sha256": "<hash>", "unit": "<definicja>"}],
  "excluded_sources": [],
  "limitations": [],
  "attribution_files": []
}
```

## Kontrole pierwszego generatora

1. STANDARD ⊆ BROAD; ATTESTED/znajomość/tematy ⊆ wskazanej wersji bazy.
2. Jedna interpretacja spełnia wszystkie warunki; odrzucony homonim nie usuwa przyjętego.
3. Oryginały pozostają niezmienne; brak dopisywania liter lub usuwania interpunkcji.
4. Rekonstrukcja ma ślad reguły i kontrolę defektywności; nie odtwarzamy już obecnej formy bez potrzeby.
5. Miary zachowują jednostkę, źródło i mianownik; brak podwójnego F i imputacji zera.
6. Powtórzony przebieg na tych samych wejściach daje identyczne wyniki i hashe.
7. Osobne licencje kodu projektu, dokumentacji i wyników zostaną ustalone przed wydaniem; publiczność repozytorium sama ich nie nadaje.
