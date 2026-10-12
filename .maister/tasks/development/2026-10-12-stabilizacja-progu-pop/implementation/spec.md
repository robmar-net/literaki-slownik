# Specyfikacja: 2382 formy STANDARD i tymczasowa stabilizacja POP

## TL;DR

Zatwierdzone formy #4 wejdą do STANDARD przez przypięty SHA256, wersjonowany JSON dokładnych analiz i ślad każdej decyzji w bazie przebiegu.
Nowa metoda POP zastąpi konkurencję o 60 tys. miejsc stałym wynikiem dzisiejszego cięcia; POP0 zachowa limit 20 tys.
Odbiór wymaga odtworzenia pełnych zbiorów, dwóch nowych buildów, sprawdzenia straży i aktualizacji wiki.
Docelowa definicja popularności zostaje otwartym zadaniem #6; osiem cofnięć i wydanie nie wchodzą do tego kroku.

## Key Decisions

- Własne użycie współczesne uchyla tylko `linguistic-historical-form-v1` dla jawnie wskazanej analizy. Nie podnosi automatycznie całego lematu ani wszystkich form.
- Dane redakcyjne mają być niezależnym wejściem pipeline, edytowanym i pinowanym jak inne konfiguracje `sources.json`; nowy build nigdy nie zmienia historycznego przebiegu.
- `score ≥ −1,042878629` jest tymczasową stałą pochodzącą z dzisiejszego 60k, a nie merytorycznym progiem znajomości słów.
- POP0 i dotychczasowe wyjątki przycinania grup zostają zachowane. Wydanie wymaga osobnego odbioru po porównaniu wyników.

## Open Questions / Risks

- Badanie pełnego diffu wykonano na zamrożonym przebiegu z 3 090 194 formami. Nowy build musi potwierdzić zgodność wejść oraz przyczyn ewentualnych rozbieżności.
- Stała punktacja może przestać stabilizować skład przy zmianie danych źródłowych, mapowania lub grup. Nie ma gwarancji monotoniczności poza zbadanym scenariuszem.
- Ocena znaczeń 125 rodzin to redakcyjny zapis z badania, z ograniczoną pewnością; produkt nie powinien przedstawiać progu POP jako zweryfikowanej granicy popularności.

## Problem i użytkownicy

Właściciel potrzebuje poprawić konkretne współczesne formy niesłusznie wyłączone ze STANDARD za dawność, zachowując kontrolę nad znaczeniem i odmianą. Operator generatora potrzebuje edytowalnego wejścia, którego wynik można odtworzyć. Gracz oraz użytkownik wiki mają otrzymać prawdziwy opis kryteriów i statusu list. Twórca bota ma móc pobrać dopiero zweryfikowane wydanie z właściwymi hashami.

Obecny próg POP liczy do 60 000 leksemów przed przycięciem. Gdy dodamy proponowane formy STANDARD, badanie przewiduje wypchnięcie 2430 dotychczasowych form POP mimo niezmienionych dowodów ich użycia. Stały próg dzisiejszej punktacji w symulacji odtwarza bazowy POP i daje +2372/0.

## Zawartość konfiguracji STANDARD

1. Nowy plik w `config/generator/`, np. `standard-age-exceptions.json`, ma własny `schema_version`, wersję decyzji, identyfikator źródłowego snapshotu oraz uporządkowane przypadki. Przypadek wiąże formę gry, `source_id`, dokładny `lemma_id`, rozwinięty tag, rodzaj analizy (`source` lub `construction`) i identyfikator dowodu rodziny. Dane powstają z `proposal-proof.json` i `family-decisions.json`, ale nie zawierają znaczników badawczych `research_only` ani `implementation_approved:false`.
2. Powiązanie z badaniem obejmuje hash obu JSON-ów, 2382 różne napisy, 7192 unikatowych analiz, 110 rodzin wnoszących dodatki oraz jawne kontrole negatywne. Każda późniejsza modyfikacja wymaga jawnej rewizji pliku i hasha w `sources.json`.
3. `inputs.inspect_sources()` weryfikuje plik i hash przez istniejący mechanizm `configurations`. W fazie `decisions` walidator odmawia nieznanych kluczy, duplikatów, niewłaściwej normalizacji, niepasującej tożsamości źródła, wejścia bez dowodu i przypadku, który nie odpowiada dokładnie jednej lub jawnie wielu analizom. Licznik dopasowanych i niewykorzystanych wpisów trafia do `reports/decisions.json` lub osobnego kanonicznego raportu.
4. Zatwierdzone przypadki są stosowane do rozwiniętych analiz źródłowych oraz już materializowanych konstrukcji. Zastępują tylko historyczny reject w warstwie językowej STANDARD; wszystkie inne checks są zachowane. Jeżeli żadnej historycznej odmowy nie ma albo istnieje inna odmowa, build odmawia rozjazdu danych zamiast dopuszczać słowo przez obejście.
5. Reguła ma osobne ID, powód, identyfikator decyzji i źródłowy dowód, widoczne w `decision_payload`, `persisted_assessments` i `explain`. Wersja `policy.py` rośnie. `explain` dla nowego przebiegu musi czytać przypiętą konfigurację przebiegu i dawać zgodny wynik; dla starego przebiegu zachowuje historyczny opis i zapisane oceny.
6. BROAD pozostaje zbiorem nadrzędnym. Eksport `lists/standard.txt` nadal wynika z ocen `membership_status='accept'`; żadnego dopisywania 2382 napisów po eksporcie. `verify` ma sprawdzać równoważność listy i ocen oraz piny wejść.

## Metoda POP

1. Nowa wersja `pop-v3` (nazwa robocza) i nowy ADR zachowują D1–D5, D7–D9. W D6 POP ma `by: score`, `value: -1.042878629`, a POP0 ma `by: count`, `value: 20000`. Stara konfiguracja `pop-v2` pozostaje odtwarzalna. Walidacja wymaga tej konkretnej kombinacji w `pop-v3`, skończonej liczby i jawnego sprawdzenia `POP0 ⊆ POP` podczas budowy.
2. `threshold()` dla `score` bierze wszystkie jednostki o zmierzonej punktacji `≥ value`, wraz z remisem na granicy; jednostki bez punktacji zostają poza. Raport podaje rodzaj, wartość progu, ostatnią rangę, liczbę jednostek i leksemów oraz pokrycie. Nie opisuje stałej jako limitu liczby leksemów.
3. D5 dla POP porównuje punktację własnych dowodów członka z tym samym progiem. Zachowuje razem warianty jednego lematu, najmocniejszego członka grupy i grupy bez rozdzielnych dowodów. POP0 nadal porównuje własną rangę do granicy swojej listy. Miarę i źródła obu porównań pozostawia bez zmiany.
4. `explain --variant pop` pokazuje punktację i rzeczywistą granicę; `pop0` pokazuje limit liczby i rangę. Pakiet ma nową metodę, hash konfiguracji i wejść, deterministyczne pliki oraz sprawdzony podzbiór. Teksty `LIMITATIONS.md`, CLI i wiki opisują tymczasowość granicy.

## Kryteria odbioru

| ID | Warunek |
| --- | --- |
| S1 | JSON jest wersjonowany, możliwy do ręcznej edycji, przypięty hashem; każda poprawka wymaga nowego przebiegu. |
| S2 | Na właściwych wejściach dokładnie 7192 zatwierdzone analizy daje 2382 nowe formy STANDARD, bez ubytku; inne odmowy pozostają. |
| S3 | Dodatnie i ujemne przykłady `round3/validation.json` mają oczekiwany wynik; homonimy i konstrukcje są rozliczone osobno. |
| P1 | Bazowy POP v3 jest dokładnie równy wydanemu pop-v2: 1 227 250 form; POP0 również dokładnie równy bazowemu. |
| P2 | Po dodatkach na przypiętych danych POP ma +2372/0 form, a POP0 +481/0; `POP0 ⊆ POP ⊆ STANDARD`. |
| P3 | Remisy, brak punktacji, wyjątki grupowe, raporty, pakiet i `explain` przechodzą testy; straż 20k/5k ma zero braków. |
| R1 | Dwa niezależne buildy LL-PL i POP dają identyczne kanoniczne listy oraz zgodne hashe/piny; niezależne checkery przechodzą. |
| D1 | ADR, dokumentacja generatora, wiki STANDARD/POP/POP0 oraz historia zmian odpowiadają rzeczywiście uzyskanym wynikom; stare wydania nadal opisane jako wydane. |

## Błędy, bezpieczeństwo danych i obserwowalność

Niepoprawny schemat, hash, identyfikator źródła, liczba dopasowań, próg lub naruszenie podzbioru zatrzymuje build przed nową publikacją. Surowe korpusy i baza robocza pozostają w ignorowanym `data/work/`; publiczne repo zawiera tylko własny przegląd, manifesty, dane konfiguracyjne, kody i małe dowody. Raporty pokazują liczbę wpisów, analizy, delty pełnych list, progi, pokrycie, brakujące częste formy i hashe. Żaden test ani workflow nie używa runnera GitHub-hosted.

## Dokumentacja, wdrożenie i wycofanie

Zaktualizować ADR nowej metody POP, `docs/generator/cli.md`, opis wyjątków wieku STANDARD oraz wiki według `docs/runbook-wiki.md`. Wiki pokazuje obecnie wydane liczby i linki do starych pakietów, dopóki nowe wydanie nie nastąpi; przy nowej metodzie zaznacza status roboczy i otwartą kalibrację progu.

Nowy przebieg powstaje w nowym katalogu, a stare FROZEN i wydania pozostają nienaruszone. Jeżeli odbiór nie przejdzie, nowego pakietu się nie publikuje; powrót operacyjny polega na dalszym użyciu poprzednich wydanych manifestów i list. Zmiana po odbiorze wymaga nowej rewizji JSON-a oraz nowych przebiegów. GitHub Release i wdrożenie do gry wymagają oddzielnej decyzji właściciela.
