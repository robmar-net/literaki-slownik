# Reguły słowników

<!-- Wygenerowane: python3 scripts/render_rules.py. Nie edytuj ręcznie; zmieniaj config/generator/rule-docs.json. -->

Wszystkie reguły, które oceniają słowa w BROAD i STANDARD: 59. Wersja polityki w kodzie: `approved-conditions-v31`.
Zasada: słowo jest na liście, gdy choć jedna jego analiza przechodzi wszystkie warstwy. Reguła współczesnego użycia i wyjątki #4 znoszą odrzucenie za dawność. Dla konkretnego słowa: `python3 -m literaki_slownik explain --run-dir <przebieg> --word <słowo>`.

**Skutek:** „odrzuca” — reguła może usunąć słowo; „nie wyklucza” — sama etykieta nie usuwa; „dopuszcza” — warunek spełniony, słowo wchodzi, jeśli nic innego go nie odrzuca; „nierozstrzyga” — brak oceny, słowo nie wchodzi; „poprawia źródło” — naprawia błąd w SGJP; „tworzy kandydatów” — reguła składa nowe formy, ocenia je reszta; „—” — nie dotyczy.
**Od:** wersja polityki i data commitu, który wprowadził regułę.

## Konstrukcja (9)

| reguła | BROAD | STANDARD | co robi | przykład | decyzja | od |
|---|---|---|---|---|---|---|
| `documented-spelling-variant-v1` | tworzy kandydatów | tworzy kandydatów | Składa udokumentowany wariant pisowni formy (ZDS §5). | — | — | diagnostic-approved-conditions-v17, 2026-10-05 |
| `impt-double-particle-v1` | tworzy kandydatów | tworzy kandydatów | Składa rozkaźnik z dwiema partykułami -że/-ż (np. idźżeż); gra je odrzuca. | — | — | diagnostic-approved-conditions-v13, 2026-10-05 |
| `impt-single-particle-v1` | tworzy kandydatów | tworzy kandydatów | Składa rozkaźnik z jedną partykułą -że/-ż (np. chodźże). | — | — | diagnostic-approved-conditions-v2, 2026-10-05 |
| `mobile-host-by-sequence-v1` | tworzy kandydatów | tworzy kandydatów | Składa ruchomą końcówkę z „by” na zamkniętej liście hostów (np. albobyś). | — | — | diagnostic-approved-conditions-v9, 2026-10-05 |
| `mobile-inflected-host-vocality-v1` | tworzy kandydatów | tworzy kandydatów | Dobiera wariant końcówki ruchomej do zakończenia formy hosta odmiennego (SGJP §6.4.1). | — | — | diagnostic-approved-conditions-v8, 2026-10-05 |
| `nie-prefix-degree-v2` | tworzy kandydatów | tworzy kandydatów | Składa nie- z przymiotnikiem lub przysłówkiem w każdym stopniu; bez zaimków i nieodmiennych (#5). | — | — | approved-conditions-v29, 2026-10-12 |
| `pred-particle-ze-v1` | tworzy kandydatów | tworzy kandydatów | Składa -że/-ż z „trzeba” i „można” (np. trzebaż), ZDS §5. | — | — | approved-conditions-v27, 2026-10-08 |
| `preposition-n-source-v1` | tworzy kandydatów | tworzy kandydatów | Składa przyimek z zaimkiem -ń (np. nań, doń). | — | — | diagnostic-approved-conditions-v7, 2026-10-05 |
| `sgjp-20260823-winien-person-erratum-v1` | poprawia źródło | poprawia źródło | Poprawia osobę w 7 formach „winien” z -śmy (błędny tag w SGJP). | — | — | diagnostic-approved-conditions-v7, 2026-10-05 |

## Język (21)

| reguła | BROAD | STANDARD | co robi | przykład | decyzja | od |
|---|---|---|---|---|---|---|
| `impt-double-particle-source-proof-v1` | dopuszcza | dopuszcza | Zamknięta źródłowa reguła impt_sg ze z? potwierdza całość; growe wyłączenie oceniane osobno. | — | — | diagnostic-approved-conditions-v13, 2026-10-05 |
| `linguistic-accent-gloss-first-release-v1` | dopuszcza | dopuszcza | Adnotacja akcent zachowana: objaśnienie nieustalone. Sam brak objaśnienia nie wyklucza w pierwszym wydaniu; dawność i inne kryteria osobno. | `dwomakroć` (dopuszczone, BROAD) | [accent-gloss-first-release-decision](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/accent-gloss-first-release-decision.md) | diagnostic-approved-conditions-v12, 2026-10-05 |
| `linguistic-contemporary-use-kwjp-v2` | — | dopuszcza | Forma pisana małymi literami ma współczesne użycie w tekstach nieliterackich KWJP; etykieta dawności nie wyklucza jej ze STANDARD. | `co` (dopuszczone, STANDARD) | [round4-sjp-benchmark-fixes-decision](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/round4-sjp-benchmark-fixes-decision.md) | approved-conditions-v29, 2026-10-10 |
| `linguistic-context-non-excluding-v1` | nie wyklucza | nie wyklucza | Określenie przymiotnikowe w dopełniaczu. Samo wymaganie kontekstu nie wyklucza; inne ograniczenia oceniane osobno. | `co` (dopuszczone, BROAD) | [context-restrictions-decision](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/context-restrictions-decision.md) | diagnostic-approved-conditions-v7, 2026-10-05 |
| `linguistic-current-usage-non-excluding-v1` | nie wyklucza | nie wyklucza | Wskazane współczesne użycie nie wyklucza; dodatkowe ograniczenia oceniane osobno. | `wobec` (dopuszczone, BROAD) | [etykiety](../../docs/generator/etykiety.md) | diagnostic-approved-conditions-v3, 2026-10-05 |
| `linguistic-descriptive-non-excluding-v1` | nie wyklucza | nie wyklucza | Sama dziedzina, stylistyka lub opis wariantu formy nie wyklucza; pozostałe warunki oceniane osobno. | `do` (dopuszczone, BROAD) | [etykiety](../../docs/generator/etykiety.md) | diagnostic-approved-conditions-v6, 2026-10-05 |
| `linguistic-disrecommended-non-excluding-v1` | nie wyklucza | nie wyklucza | Samo niezalecanie nie wyklucza w BROAD ani STANDARD; pozostałe warunki oceniane osobno. | `rzecz` (dopuszczone, BROAD) | [disrecommended-decision](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/disrecommended-decision.md) | diagnostic-approved-conditions-v2, 2026-10-05 |
| `linguistic-documented-use-lexical-proof-v1` | dopuszcza | dopuszcza | Dodatni dowód leksykalny dokładnie udokumentowanego użycia dla BROAD i STANDARD; wiek, pisownia, gra i inne warunki osobno. | `ziem` (dopuszczone, BROAD) | — | diagnostic-approved-conditions-v16, 2026-10-05 |
| `linguistic-fulfilled-component-requirement-v1` | dopuszcza | dopuszcza | Wymaganie składnika spełnione przez potwierdzoną konstrukcję; inne warunki osobno. | `bezeń` (dopuszczone, BROAD) | [konstrukcje](../../docs/generator/konstrukcje.md) | approved-conditions-v25, 2026-10-08 |
| `linguistic-historical-form-v1` | dopuszcza | odrzuca | Oznaczenie dawności wyklucza tę analizę ze STANDARD, także przy dziś. | `jednako` (odrzucone, STANDARD) | [mixed-history-decision](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/mixed-history-decision.md) | diagnostic-approved-conditions-v3, 2026-10-05 |
| `linguistic-incorrect-form-v1` | odrzuca | odrzuca | SGJP oznacza tę interpretację jako niepoprawną; odrzucenie w BROAD i STANDARD. | `aleatoryźmie` (odrzucone, BROAD) | [incorrect-forms-decision](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/incorrect-forms-decision.md) | diagnostic-approved-conditions-v5, 2026-10-05 |
| `linguistic-informal-rare-non-excluding-v1` | nie wyklucza | nie wyklucza | Sama potoczność, wulgarność, regionalność, gwarowość lub rzadkość nie wyklucza; inne warunki oceniane osobno. | `jak` (dopuszczone, BROAD) | [link](https://sgjp.pl/oznaczenia/) | diagnostic-approved-conditions-v4, 2026-10-05 |
| `linguistic-policy-active-v1` | dopuszcza | dopuszcza | Polityka językowa aktywna: zamknięta macierz klas i etykiet; pozostałe warunki osobno. | `się` (dopuszczone, BROAD) | [agent-decisions-round3-decision](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/agent-decisions-round3-decision.md) | approved-conditions-v24, 2026-10-08 |
| `linguistic-standard-age-baseline-v1` | — | nie wyklucza | Brak wykluczającego oznaczenia wieku nie blokuje tego warunku STANDARD. Współczesność nie została niezależnie ustalona; inne warunki i konkretne dowody osobno. | `się` (dopuszczone, STANDARD) | [standard-age-baseline-decision](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/standard-age-baseline-decision.md) | diagnostic-approved-conditions-v20, 2026-10-05 |
| `linguistic-standard-age-exception-v1` | — | dopuszcza | Zatwierdzone współczesne użycie tej analizy (#4); etykieta dawności nie wyklucza jej ze STANDARD. Inne warunki osobno. | `hospicja` (dopuszczone, STANDARD) | [link](https://github.com/robmar-net/literaki-slownik/issues/4) | approved-conditions-v30, 2026-10-12 |
| `linguistic-standard-no-polish-meaning-v1` | — | odrzuca | Wskazana analiza SGJP bez polskiego znaczenia nie wchodzi do STANDARD (config/generator/standard-exclusions.json). Działa od następnego buildu. | — | — | approved-conditions-v31, 2026-11-06 |
| `linguistic-unexplained-label-first-release-v1` | dopuszcza | dopuszcza | Oznaczenie zachowane: objaśnienie nieustalone. Sam brak objaśnienia nie wyklucza w pierwszym wydaniu; inne kryteria osobno. | `go` (dopuszczone, BROAD) | [unexplained-labels-first-release-decision](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/unexplained-labels-first-release-decision.md) | diagnostic-approved-conditions-v10, 2026-10-05 |
| `linguistic-unknown-qualifier-v1` | nierozstrzyga | nierozstrzyga | Etykieta kwalifikatora bez zatwierdzonego warunku wymaga oceny. | — | — | approved-conditions-v24, 2026-10-08 |
| `preposition-n-whole-form-proof-v1` | dopuszcza | dopuszcza | Cała forma dosłownie wskazana w §9.1 SGJP; inne warunki oceniane osobno. | `bezeń` (dopuszczone, BROAD) | [link](https://sgjp.pl/static/pdf/Podstawy_teoretyczne_SGJP.pdf) | diagnostic-approved-conditions-v7, 2026-10-05 |
| `semantic-remainder-exhausted-v1` | odrzuca | odrzuca | Sprawdzone użycia wyczerpują to ID (decyzja właściciela); pozostałość nie daje osobnej analizy. | `ibn` (odrzucone, BROAD) | [owner-decisions-round2-decision](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/owner-decisions-round2-decision.md) | diagnostic-approved-conditions-v23, 2026-10-08 |
| `semantic-use-qualification-closed-v1` | dopuszcza | dopuszcza | Udokumentowane użycie ma domknięte warunki (decyzja właściciela); pozostałe oceny osobno. | `de` (dopuszczone, BROAD) | [owner-decisions-round2-decision](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/owner-decisions-round2-decision.md) | diagnostic-approved-conditions-v23, 2026-10-08 |

## Pisownia (5)

| reguła | BROAD | STANDARD | co robi | przykład | decyzja | od |
|---|---|---|---|---|---|---|
| `orthography-2026-conjunction-by-v1` | dopuszcza | odrzuca | Norma 2026 wymaga pisowni rozdzielnej; ta analiza odpada ze STANDARD. | `jeśliby` (odrzucone, STANDARD) | [orthography-2026-decision](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/orthography-2026-decision.md) | diagnostic-approved-conditions-v8, 2026-10-05 |
| `orthography-2026-host-by-sequence-v1` | dopuszcza | odrzuca | Ta konstrukcja wymaga rozdzielnej pisowni by według normy2026; odrębne źródłowe wyrazy oceniane osobno. | `alboby` (odrzucone, STANDARD) | [link](https://rjp.pan.pl/app/uploads/2025/11/2-zalacznik-do-komunikatu-11-25-wersja-jednolita.pdf) | diagnostic-approved-conditions-v9, 2026-10-05 |
| `orthography-2026-resident-capital-v1` | dopuszcza | odrzuca | Źródłowy dawny zapis małoliterowy nie odpowiada normie2026 wymaganej w STANDARD. | `warszawiaków` (odrzucone, STANDARD) | [capitalization-source-cases.json](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/capitalization-source-cases.json) | diagnostic-approved-conditions-v13, 2026-10-05 |
| `orthography-attested-lowercase-2026-v1` | dopuszcza | dopuszcza | Jawny przykład normy2026 potwierdza mały zapis tego użycia; inne warunki językowe i growe osobno. | `angol` (dopuszczone, BROAD) | [link](https://rjp.pan.pl/app/uploads/2025/11/2-zalacznik-do-komunikatu-11-25-wersja-jednolita.pdf#page=43; §8.1.2 pkt4 uwaga) | diagnostic-approved-conditions-v17, 2026-10-05 |
| `orthography-sgjp-single-word-by-v1` | dopuszcza | dopuszcza | Zapis łączny według SGJP; otwarta lista RJP §4.5 pkt 1c go nie wyklucza (decyzja właściciela). Wiek i gra osobno. | `niechby` (dopuszczone, BROAD) | [owner-decisions-round1-decision](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/owner-decisions-round1-decision.md) | diagnostic-approved-conditions-v22, 2026-10-08 |

## Gra (20)

| reguła | BROAD | STANDARD | co robi | przykład | decyzja | od |
|---|---|---|---|---|---|---|
| `game-abbreviation-noun-v1` | odrzuca | odrzuca | Skrót lub skrótowiec zapisany w SGJP jako rzeczownik; zasady gry wykluczają skróty. | `nr` (odrzucone, BROAD) | [round4-sjp-benchmark-fixes-decision](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/round4-sjp-benchmark-fixes-decision.md) | approved-conditions-v26, 2026-10-08 |
| `game-abbreviation-v1` | odrzuca | odrzuca | Źródłowa analiza jest skrótem; nie utożsamiamy skrótu ze skrótowcem rzeczownikowym. | `zł` (odrzucone, BROAD) | [ortografia](../../docs/generator/ortografia.md) | diagnostic-approved-conditions-v12, 2026-10-05 |
| `game-adjp-graphic-word-v1` | dopuszcza | dopuszcza | Forma przyimkowa (po polsku) jest osobnym wyrazem graficznym według RJP §4.4; dopuszczona warunkowo decyzją właściciela, oznaczona do ewentualnego wycofania. | `prostu` (dopuszczone, BROAD) | [owner-decisions-round1-decision](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/owner-decisions-round1-decision.md) | diagnostic-approved-conditions-v22, 2026-10-08 |
| `game-agl-stem-v1` | odrzuca | odrzuca | Temat czasu przeszłego dla końcówki (mogł-em) nie jest samodzielnym słowem; formy z końcówką osobno. | `mogł` (odrzucone, BROAD) | [round4-sjp-benchmark-fixes-decision](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/round4-sjp-benchmark-fixes-decision.md) | approved-conditions-v26, 2026-10-08 |
| `game-brand-name-v1` | odrzuca | odrzuca | Nazwa marki lub produktu: ZDS §1 jej nie dopuszcza, od 2026 pisze się ją wielką literą. | `audi` (odrzucone, BROAD) | [zds-game-rules-decision](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/zds-game-rules-decision.md) | approved-conditions-v28, 2026-10-09 |
| `game-construction-whole-unit-v1` | dopuszcza | dopuszcza | Potwierdzony konstruktor: oceniamy całość, nie samodzielność końcówki; pozostałe warunki osobno. | `coś` (dopuszczone, BROAD) | — | diagnostic-approved-conditions-v12, 2026-10-05 |
| `game-dependent-segment-v1` | odrzuca | odrzuca | Źródłowa analiza jest niesamodzielnym składnikiem; może uczestniczyć w potwierdzonej pełnej konstrukcji. | `video` (odrzucone, BROAD) | [konstrukcje](../../docs/generator/konstrukcje.md) | diagnostic-approved-conditions-v12, 2026-10-05 |
| `game-documented-conditions-v1` | dopuszcza | dopuszcza | Opublikowane zasady Literaków: słowa słownikowe i ich formy, poza wielką literą, skrótami i łącznikiem; wyłączenia osobno. | `się` (dopuszczone, BROAD) | [agent-decisions-round3-decision](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/agent-decisions-round3-decision.md) | approved-conditions-v24, 2026-10-08 |
| `game-documented-resident-capital-v1` | odrzuca | odrzuca | To udokumentowane użycie nazwy mieszkanki wymaga wielkiej litery według normy2026; obowiązujące wyłączenie growe, inne użycia osobno. | `warszawianki` (odrzucone, BROAD) | — | diagnostic-approved-conditions-v18, 2026-10-05 |
| `game-documented-surname-component-v1` | odrzuca | odrzuca | Dokumentacja autorów SGJP wskazuje tę dokładnie przypisaną analizę jako człon nazwiska; istniejące wyłączenie growe, wpis i inne homonimy zachowane. | `ibn` (odrzucone, BROAD) | [documented-name-class-proof-decision](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/documented-name-class-proof-decision.md) | diagnostic-approved-conditions-v14, 2026-10-05 |
| `game-double-particle-v1` | odrzuca | odrzuca | Ta analiza zawiera dwa dołączenia partykuły że/ż; zachowane reguły gry wykluczają ją, niezależne homonimy osobno. | `abdykujżeż` (odrzucone, BROAD) | [konstrukcje](../../docs/generator/konstrukcje.md) | diagnostic-approved-conditions-v13, 2026-10-05 |
| `game-frag-graphic-word-v1` | dopuszcza | dopuszcza | Fragment frazy (na wznak, za bezcen) jest osobnym wyrazem graficznym; dopuszczony warunkowo decyzją właściciela, oznaczony do ewentualnego wycofania. | `jako` (dopuszczone, BROAD) | [owner-decisions-round2-decision](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/owner-decisions-round2-decision.md) | diagnostic-approved-conditions-v23, 2026-10-08 |
| `game-mandatory-capital-2026-v1` | odrzuca | odrzuca | Ta interpretacja nazwy mieszkańca wymaga wielkiej litery według normy2026, również przy dawnym zapisie w BROAD; inne homonimy osobno. | `warszawiaków` (odrzucone, BROAD) | [capitalization-source-cases.json](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/capitalization-source-cases.json) | diagnostic-approved-conditions-v13, 2026-10-05 |
| `game-mobile-host-composition-v1` | odrzuca | odrzuca | Ta źródłowa konstrukcja mobilnej końcówki lub trybu przypuszczającego z nieczasownikowym hostem jest wyłączona przez zachowane reguły gry; homonimy osobno. | `com` (odrzucone, BROAD) | [konstrukcje](../../docs/generator/konstrukcje.md) | diagnostic-approved-conditions-v12, 2026-10-05 |
| `game-personal-host-aglt-v1` | odrzuca | odrzuca | Końcówka czasownikowa dołączona do zaimka lub przymiotnika: ta konstrukcyjna analiza jest wyłączona przez zachowane reguły gry; homonimy osobno. | — | [konstrukcje](../../docs/generator/konstrukcje.md) | diagnostic-approved-conditions-v12, 2026-10-05 |
| `game-proper-name-class-v1` | odrzuca | odrzuca | Ta analiza jest źródłowo sklasyfikowana jako nazwa własna lub jej człon. | `br` (odrzucone, BROAD) | [link](https://sgjp.pl/instrukcja/) | diagnostic-approved-conditions-v12, 2026-10-05 |
| `game-required-uppercase-v1` | odrzuca | odrzuca | Źródłowy zapis wymaga wielkich liter. | `br` (odrzucone, BROAD) | [ortografia](../../docs/generator/ortografia.md) | diagnostic-mechanics-v1, 2026-10-04 |
| `game-resident-screen-capital-2026-v1` | odrzuca | odrzuca | Przesiew -anin/-anka: nazwa mieszkańca wymaga wielkiej litery według normy 2026 (decyzja klasowa właściciela); wyjątki nie-mieszkańców osobno, inne homonimy osobno. | `szczecinian` (odrzucone, BROAD) | [owner-decisions-round2-decision](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/owner-decisions-round2-decision.md) | diagnostic-approved-conditions-v23, 2026-10-08 |
| `game-source-name-labels-v1` | dopuszcza | dopuszcza | Źródłowe oznaczenia nazw rozpoznane; inne warunki osobno. | `się` (dopuszczone, BROAD) | [link](https://sgjp.pl/instrukcja/) | diagnostic-approved-conditions-v12, 2026-10-05 |
| `game-zds-named-exclusion-v1` | odrzuca | odrzuca | Przykład wyłączenia wymieniony wprost w ZDS (sklep, domena, format pliku albo niedozwolone -ń). | `doc` (odrzucone, BROAD) | [zds-game-rules-decision](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/zds-game-rules-decision.md) | approved-conditions-v27, 2026-10-08 |

## Profil (2)

| reguła | BROAD | STANDARD | co robi | przykład | decyzja | od |
|---|---|---|---|---|---|---|
| `profile-pl-alphabet-v1` | odrzuca | odrzuca | Znaki poza alfabetem płytek. | `von` (odrzucone, BROAD) | — | diagnostic-mechanics-v1, 2026-10-04 |
| `profile-pl-length-v1` | odrzuca | odrzuca | Wymagana długość 2–15 znaków po NFC/lower. | `w` (odrzucone, BROAD) | — | diagnostic-mechanics-v1, 2026-10-04 |

## Zakres (1)

| reguła | BROAD | STANDARD | co robi | przykład | decyzja | od |
|---|---|---|---|---|---|---|
| `first-release-contraction-scope-v1` | odrzuca | odrzuca | Kandydat poza zakresem pierwszego wydania; zachowany diagnostycznie, bez uznania formy za błędną. | `kołoń` (odrzucone, BROAD) | [remaining-contractions-scope-decision](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/remaining-contractions-scope-decision.md) | diagnostic-approved-conditions-v9, 2026-10-05 |

## Ocena (1)

| reguła | BROAD | STANDARD | co robi | przykład | decyzja | od |
|---|---|---|---|---|---|---|
| `assessment-not-evaluated-v1` | nierozstrzyga | nierozstrzyga | Analiza bez oceny wymaganych warunków nie wchodzi na listę. | — | — | diagnostic-mechanics-v1, 2026-10-04 |
