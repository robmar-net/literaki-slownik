# ADR-006: NKJP jako źródło na licencji CC BY bez wersji

**Status:** zaakceptowana przez właściciela, 2026-10-11. Zastępuje decyzję N1 z [ADR-002](../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/research-context/decision-log.md) w części o warunkach NKJP.

## Kontekst
[N-gramy NKJP](https://zil.ipipan.waw.pl/NKJPNGrams) mają tylko deklarację: „NKJP ngrams are made available on CC-BY licence.” Brak numeru wersji, tekstu licencji i wzoru atrybucji. ADR-002 wstrzymał NKJP do wyjaśnienia warunków. Nie kontaktujemy się z innymi grupami, więc wyjaśnienia nie będzie.

## Decyzja
Używamy n-gramów NKJP jako CC BY i spełniamy **sumę wymagań wszystkich wersji CC BY (1.0–4.0)**:

| wymaganie | jak spełniamy |
|---|---|
| twórca i licencjodawca | Zespół Inżynierii Lingwistycznej IPI PAN; korpus: Narodowy Korpus Języka Polskiego (NKJP) |
| tytuł | „N-grams from the balanced subcorpus of the National Corpus of Polish” |
| adres źródła | https://zil.ipipan.waw.pl/NKJPNGrams |
| licencja | „CC BY, wersja nieokreślona przez udostępniającego”, z linkiem do https://creativecommons.org/licenses/by/4.0/ i zdaniem, że spełniamy wymagania wszystkich wersji |
| informacja o zmianach | opis, co zrobiliśmy z danymi (niżej) |
| prawa i wyłączenie gwarancji | udostępniający ich nie podał; zaznaczamy to |
| brak sugestii poparcia | zdanie, że autorzy NKJP nie popierają projektu |
| brak dodatkowych ograniczeń | nasze wyniki są na BSD-2-Clause i CC BY 4.0, bez DRM |

Zakres: plik `1grams.gz` (SHA256 `73af4909…3dc9`), do miar popularności (POP, POP0). Nie redystrybuujemy surowego pliku.

## Konsekwencje
- Treść atrybucji jest w [ATTRIBUTIONS.md](../../ATTRIBUTIONS.md). Każdy pakiet, który używa NKJP, ma ją w swoich atrybucjach.
- Pakiet LL-PL v29 NKJP nie używa i się nie zmienia. Wpis `unavailable` w manifeście LL-PL usuniemy przy następnym wydaniu LL-PL.
- Ryzyko: udostępniający może później podać wersję lub warunki. Wtedy sprawdzamy zgodność i w razie potrzeby wydajemy nową wersję.
- Wycofanie: usunąć NKJP z manifestów POP i wydać pakiety bez niego.
