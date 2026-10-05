window.MAISTER_DATA = {
  "generated": "2026-10-05T19:41:13Z",
  "task": {
    "title": "Pierwszy generator BROAD i STANDARD",
    "description": "Implementacja zatwierdzonego projektu G1/N1/C1: Python/SQLite, SGJP/KWJP, pełna fleksja, kontrolowane konstrukcje, explain, verify i export.",
    "status": "in_progress",
    "tags": [
      "slowniki",
      "generator",
      "SGJP",
      "KWJP"
    ],
    "priority": null,
    "type": "development",
    "path": ".maister/tasks/development/2026-10-04-generator-broad-standard",
    "current_activity": "Wiek wdrożony; decyzja wspólnego progu leksykalnego STANDARD"
  },
  "characteristics": {
    "has_reproducible_defect": false,
    "modifies_existing": true,
    "new_capability": true,
    "data_operations": true,
    "ui_heavy": false,
    "risk_level": "high"
  },
  "phases": [
    {
      "id": "phase_1",
      "name": "Analiza kodu",
      "icon_hint": "analysis",
      "status": "completed",
      "started": "2026-10-04T11:05:21Z",
      "completed": "2026-10-04T11:08:54Z",
      "skip_reason": null,
      "summary": "Zbadano skrypty SGJP/KWJP/pilota i testy; potwierdzono brak generatora, jawne punkty adaptacji i luki językowe. Baseline 5/5 OK, research spójny.",
      "decisions": [
        "Nowy kod generatora z jawnymi ścieżkami; zamrożony audyt pozostaje odtwarzalny"
      ],
      "risks": [
        "Przesiew audytu nie jest finalną polityką",
        "Brak pełnych dowodów semantyki etykiet i macierzy klas"
      ],
      "artifacts": [
        {
          "path": "analysis/codebase-analysis.md",
          "label": "Analiza kodu"
        },
        {
          "path": "analysis/research-context/INDEX.md",
          "label": "Kontekst i źródła research"
        },
        {
          "path": "analysis/research-context/provenance.json",
          "label": "Pochodzenie snapshotów"
        }
      ],
      "gate": {
        "question": null,
        "answer": null
      }
    },
    {
      "id": "phase_2",
      "name": "Luki i zakres",
      "icon_hint": "analysis",
      "status": "completed",
      "started": "2026-10-04T11:08:54Z",
      "completed": "2026-10-04T11:25:24Z",
      "skip_reason": null,
      "summary": "Użytkownik zatwierdził pełny zakres wraz z zadaniami dowodowymi K1–K10 odpowiedzią A.",
      "decisions": [
        "G1/N1/C1 już zatwierdzone; nie są ponownie głosowane"
      ],
      "risks": [
        "Dalsze dowody mogą ujawnić rzeczywisty wybór językowej polityki",
        "Pełnego wyniku nie można odebrać przy nierozstrzygnięciach zmieniających listy"
      ],
      "artifacts": [
        {
          "path": "analysis/gap-analysis.md",
          "label": "Luki i zakres implementacji"
        }
      ],
      "gate": {
        "id": "scope_approval",
        "status": "approved",
        "question": "Czy zatwierdzasz zakres implementacji opisany w analizie luk, obejmujący narzędzie i domknięcie dowodów językowych?",
        "options": {
          "A": "Zatwierdź cały zakres i przejdź do specyfikacji oraz planu (rekomendowane).",
          "B": "Wskaż korektę zakresu przed specyfikacją."
        },
        "answer": "A",
        "answered_at": "2026-10-04T11:25:24Z"
      }
    },
    {
      "id": "phase_3",
      "name": "TDD red",
      "icon_hint": "analysis",
      "status": "skipped",
      "started": "2026-10-04T11:25:24Z",
      "completed": "2026-10-04T11:25:24Z",
      "skip_reason": "Nowa funkcjonalność, bez reprodukowalnego defektu; test-first będzie w grupach implementacji.",
      "summary": "Nowa funkcjonalność, bez reprodukowalnego defektu; test-first będzie w grupach implementacji.",
      "decisions": [],
      "risks": [],
      "artifacts": [],
      "gate": {
        "question": null,
        "answer": null
      }
    },
    {
      "id": "phase_4",
      "name": "Makiety UI",
      "icon_hint": "analysis",
      "status": "skipped",
      "started": "2026-10-04T11:25:24Z",
      "completed": "2026-10-04T11:25:24Z",
      "skip_reason": "Lokalne CLI, brak UI-heavy.",
      "summary": "Lokalne CLI, brak UI-heavy.",
      "decisions": [],
      "risks": [],
      "artifacts": [],
      "gate": {
        "question": null,
        "answer": null
      }
    },
    {
      "id": "phase_5",
      "name": "Specyfikacja",
      "icon_hint": "analysis",
      "status": "completed",
      "started": "2026-10-04T11:25:24Z",
      "completed": "2026-10-04T12:35:13Z",
      "skip_reason": null,
      "summary": "Wymagania R01–R12 i specyfikacja zatwierdzone odpowiedzią A; kolejny krok audyt i plan.",
      "decisions": [
        "Python 3.11+ i biblioteka standardowa; jawne manifesty i oddzielne build/verify/export",
        "Deterministyczne próbkowanie quality-v1 przed pomiarem, po 30 jednostek na warstwę",
        "Dowody językowe obowiązkowe; unresolved zmieniające zakres blokuje wydanie"
      ],
      "risks": [
        "Tabele etykiet i macierz klas do domknięcia w implementacji",
        "Warunki publikacji własnego kodu i danych do ustalenia przed K10",
        "Pełny koszt przebiegu do zmierzenia"
      ],
      "artifacts": [
        {
          "path": "analysis/requirements.md",
          "label": "Wymagania R01–R12"
        },
        {
          "path": "implementation/spec.md",
          "label": "Specyfikacja wykonawcza",
          "html": "implementation/spec.html"
        }
      ],
      "gate": {
        "id": "spec_approval",
        "status": "approved",
        "question": "Czy zatwierdzasz specyfikację wykonawczą generatora BROAD i STANDARD?",
        "options": {
          "A": "Zatwierdź specyfikację; przejdź do audytu i planu (rekomendowane).",
          "B": "Wskaż korektę specyfikacji przed planem."
        },
        "answer": "A",
        "answered_at": "2026-10-04T12:35:13Z"
      }
    },
    {
      "id": "phase_6",
      "name": "Audyt specyfikacji",
      "icon_hint": "analysis",
      "status": "completed",
      "started": "2026-10-04T12:35:13Z",
      "completed": "2026-10-04T12:40:22Z",
      "skip_reason": null,
      "summary": "passed_with_issues: 0 critical, 0 warning, 3 info. I1–I3 uwzględnione w planie do zatwierdzenia; brak blokad planowania.",
      "decisions": [
        "Rozróżnienie przyszłego pakietu verify i zamrożenia export",
        "Jawny indeks kanoniczny i kodowanie danych próbki"
      ],
      "risks": [
        "Macierz językowa i warunki publikacji wymagają wykonania G3/G7/G8"
      ],
      "artifacts": [
        {
          "path": "verification/spec-audit.md",
          "label": "Audyt specyfikacji"
        }
      ],
      "gate": {
        "question": null,
        "answer": null
      }
    },
    {
      "id": "phase_7",
      "name": "Plan implementacji",
      "icon_hint": "analysis",
      "status": "completed",
      "started": "2026-10-04T12:40:22Z",
      "completed": "2026-10-04T12:47:44Z",
      "skip_reason": null,
      "summary": "Plan 9 grup/36 kroków i doprecyzowania I1–I3 zatwierdzone odpowiedzią A.",
      "decisions": [
        "Wykonanie sekwencyjne; koordynator właścicielem wszystkich grup",
        "Test-first grup kodowych; pełny zakres K1–K10 bez pilota zamiast odbioru"
      ],
      "risks": [
        "Nowy wybór językowy lub licencji wymaga konkretnej decyzji w implementacji",
        "Pełne przebiegi i przegląd jakości są obowiązkowe"
      ],
      "artifacts": [
        {
          "path": "implementation/implementation-plan.md",
          "label": "Plan 9 grup i 36 kroków",
          "html": "implementation/implementation-plan.html"
        }
      ],
      "gate": {
        "id": "plan_approval",
        "status": "approved",
        "question": "Czy zatwierdzasz plan dziewięciu grup i doprecyzowania I1–I3, aby rozpocząć implementację?",
        "options": {
          "A": "Zatwierdź plan i rozpocznij implementację (rekomendowane).",
          "B": "Wskaż korektę planu przed implementacją."
        },
        "answer": "A",
        "answered_at": "2026-10-04T12:47:44Z"
      }
    },
    {
      "id": "phase_8",
      "name": "Implementacja",
      "icon_hint": "analysis",
      "status": "in_progress",
      "started": "2026-10-04T12:47:44Z",
      "completed": null,
      "skip_reason": null,
      "summary": "Wdrożone A wieku STANDARD v20 z jawną niepewnością; 208/208+5/5, preflight14+12OK. Dwie projekcje10rekordów/16analiz/32ocen, 24readonly explain, powtarzalność i źródło bez zmian. Raport niewiadomych rozlicza wynik całego słowa; historyczne oceny nie są nowym pełnym build v20. Konieczna decyzja zakresu leksykalnego dowodu STANDARD; pełna macierz i8/36 nadal otwarte.",
      "decisions": [
        "Sekwencyjnie zgodnie z zatwierdzonym planem, brak zainstalowanego task-group-implementer: wykonanie inline",
        "Wpis/kwalifikacja językowa, reguły gry, profil i członkostwo w liście rozdzielone; lower nie omija wyłączeń gry.",
        "Reguły gry niezmienione; częściowych konfiguracji discovery nie aktywowano",
        "Wykonano niezależny fragment KWJP według wyjątku planu; G3/G4/G8 nie oznaczone complete",
        "A supplementary_attestation_inputs approved; audit conditions before supplementary data activation",
        "User authorized code continuation; diagnostic mechanics do not activate incomplete linguistic policy or bypass release",
        "Użytkownik: decyzje zmieniające kryteria i skład słownika omawiamy przed wdrożeniem; bez automatycznego kopiowania polityki źródeł SJP.pl.",
        "A: samo niezal. nie odrzuca interpretacji w BROAD ani STANDARD; pozostałe kryteria nadal obowiązują.",
        "A mixed_history_priority: dodatkowe daw./przest. wyklucza konkretną interpretację ze STANDARD mimo dziś; samo dziś nie wyklucza, BROAD bez wyłączenia przez dawność.",
        "Wikisłownik i podobne źródła społecznościowe odkładamy na później. W bieżącej fazie nie używamy ich do budowy słownika ani rozstrzygania dopuszczalności. Zachowujemy przypięte dane SGJP i KWJP oraz ich odrębne role; KWJP nie jest dowodem poprawności konstrukcji. Brakujące poświadczenia pozostają unresolved — nie oznaczają odrzucenia formy i nie pozwalają deklarować pełnego wydania. Dotychczasowe audyty pozostają materiałem historycznym, bez aktywacji ich danych.",
        "A incorrect_source_label_policy: jawne niepopr. na sprawdzonej dosłownej etykiecie odrzuca konkretną interpretację w BROAD i STANDARD, bez usunięcia wpisu lub innych analiz.",
        "A context_restrictions_policy: samo wymaganie kontekstu niewykluczające; explain zachowuje je, niesamodzielne morfemy osobno.",
        "A contraction_documentation_proof: dosłowne wskazanie całej kontrakcji przez autorów SGJP wystarcza jako dowód językowy dla18 form; pozostałe kryteria osobno,8pozostałych bez automatycznej analogii.",
        "A: własny kod/konfiguracje BSD-2-Clause; własna dokumentacja i raporty CC BY 4.0. Źródła zachowują odrębne warunki.",
        "A: STANDARD stosuje normę 2026 także dla nieoznaczonych dawnych zapisów; BROAD może je zachować z dowodem, reguły gry niezmienione.",
        "A: zakres kontrakcji pierwszego wydania ograniczony do18poświadczonych form;8innych kandydatów zachowane diagnostycznie poza zakresem, nieuznane za błędne. Niezależne homonimy oceniane osobno; rozszerzenie wymaga dowodu i nowego wydania.",
        "A: zamknięte25oznaczeń zachowane z nieustalonym objaśnieniem; brak objaśnienia sam nie wyklucza ani nie blokuje wydania. Pozostałe kryteria i inne unknown nadal obowiązują.",
        "A: brak objaśnienia adnotacji akcent w daw.,rzad.,akcent sam nie wyklucza; zachowujemy adnotację, STANDARD nadal odrzuca za dawność.",
        "A: wspólny growy warunek obowiązkowej wielkiej litery odnosi się do normy2026 także dla dawnych interpretacji BROAD; dawne wpisy zachowane językowo, niezależne homonimy osobno.",
        "Nie kontaktujemy się z innymi grupami w tym projekcie; przygotowane zapytanie do SGJP pozostaje niewysłanym materiałem historycznym. Braki klasyfikacji rozpoznajemy samodzielnie na podstawie dopuszczonych danych i dokumentacji.",
        "Dane PAN częściowo uzupełniają wiedzę o znaczeniach: KWJP bigramy i publiczne próbki kontekstowe, SGJP glosy/relacje poza eksportem. Własny przegląd możliwy bez kontaktu; nie aktywowano danych ani filtrów, kompletność nadal otwarta.",
        "Użytkownik zlecił dopisanie do planu samodzielnego przeglądu PAN: PAN-1–PAN-5 w G3. Najbliżej pełny rejestr147frag, dalej dowody/mapowanie/pokrycie i omówienie wpływu przed G4. Zakres9grup/36kroków i bramka phase10 zachowane.",
        "Zatwierdzone A: ogólny opis wieku całej klasy nie nadaje jej członkom automatycznego odrzucenia STANDARD. Potrzebne oznaczenie lub jednoznaczny dowód konkretnej interpretacji; jawne daw./przest. pozostają wiążące. Bez przeniesienia WSJP do wejść, bez zmiany reguł gry; pełna kwalifikacja nadal otwarta.",
        "Zatwierdzone A: jednoznaczny opis konkretnej formy przez autorów SGJP i ręcznie zweryfikowana tożsamość wystarczają do uzupełnienia klasy członu nazwiska. Wdrożono tylko de:F/frag i ibn/frag, ze strażnikami hasha, źródła, wiersza i pięciu pól. Wpisy i de:S zachowane; reguły gry niezmienione, metadane online nieaktywne.",
        "A: osobne udokumentowane użycia dokładnego rekordu źródłowego; spójne warstwy ocen, niewiadoma pozostałość, bez aktywacji metadanych czytnika.",
        "Model A wdrożony v15: warunki dokumentacyjne przypięte tylko do potwierdzonego użycia; brak propagacji na pozostałość, bez zmiany reguł gry.",
        "A: dokumentacyjny dodatni dowód leksykalny BROAD tylko dokładnie potwierdzonego użycia; STANDARD i pozostałe warunki osobno, nierozpoznana pozostałość zachowana.",
        "Dodatni dowód A wdrożony v16: zamknięte mapowanie wznak, tylko leksykalny warunek BROAD; pełna kwalifikacja nadal otwarta.",
        "A: osobni kandydaci jawnie udokumentowanej pisowni istniejących analiz, tylko angol/jugol; źródłowe rekordy, inne warunki i niewiadome zachowane.",
        "Zatwierdzone A pisowni wdrożone w zamkniętym zakresie; walidacja utrwalonych źródeł/składników przed ocenami i odczytem.",
        "Diagnostyczne próbki i indeks nie aktywują polityki ani odbioru; brakujące pełne części jawne."
      ],
      "risks": [
        "Pełna macierz kwalifikatorów/konstrukcji i udokumentowane warunki gry nadal wymagają domknięcia.",
        "Mechanika próbek nie zastępuje integracji raportów, pełnych analiz w przeglądzie ani odbioru G8.",
        "Brak kompletnej klasy nazw mieszkańców oraz rozdzielenia frag/obcych zwrotów w eksporcie. Nie zakładamy istnienia brakujących metadanych. Kontakt z innymi grupami wykluczony przez użytkownika; brakujące dowody nadal otwarte.",
        "Dokumentacja klasy może różnić się zakresem od opisu konkretnego znaczenia; pełny ID SGJP może łączyć znaczenia. Brak automatycznej propagacji i nowego filtra przed decyzją.",
        "Jedno źródłowe rozpoznanie może odpowiadać kilku publicznym artykułom lub opisowi przy artykule nadrzędnym. Potrzebna decyzja modelu użyć; nie ustalono pełnej zgodności snapshotu."
      ],
      "artifacts": [
        {
          "path": "analysis/evidence/full-import.json",
          "label": "Pełny import i zgodność liczników"
        },
        {
          "path": "analysis/evidence/acronym-decision.md",
          "label": "Wybór polityki skrótowców"
        },
        {
          "path": "analysis/evidence/dictionary-vs-game.md",
          "label": "Wpis słownikowy a dopuszczalność growa"
        },
        {
          "path": "analysis/evidence/g3-review.md",
          "label": "Zweryfikowane dowody G3 i otwarte luki"
        },
        {
          "path": "analysis/evidence/source-extension-decision.md",
          "label": "Decyzja dodatkowych wejść"
        },
        {
          "path": "analysis/evidence/label-coverage.json",
          "label": "Pełne kombinacje i mieszaniny nazw"
        },
        {
          "path": "analysis/evidence/kwjp-mapping.json",
          "label": "Pełne mapowanie lemma-all"
        },
        {
          "path": "../../../../docs/literaki-prosty-jezyk-minimum-leksykalne-kierunki.md",
          "label": "Notatka użytkownika: przyszłe słowniki znajomości"
        },
        {
          "path": "analysis/evidence/supplementary-source-audit.md",
          "label": "Audyt dodatkowych źródeł po A"
        },
        {
          "path": "analysis/evidence/sgjp-metadata-audit.json",
          "label": "Metadane SGJP: istnienie a licencja"
        },
        {
          "path": "analysis/evidence/contraction-attestation-audit.json",
          "label": "Pokrycie 26 kontrakcji"
        },
        {
          "path": "analysis/evidence/qualifier-semantics-audit.json",
          "label": "Semantyka i ekspozycja kwalifikatorów"
        },
        {
          "path": "analysis/evidence/full-links-report.json",
          "label": "Pełny raport 13 list KWJP"
        },
        {
          "path": "analysis/evidence/full-links-performance.json",
          "label": "Koszt pełnego powiązania"
        },
        {
          "path": "analysis/evidence/diagnostic-explain-runtime.json",
          "label": "Rzeczywiste explain i kontrola odczytu bez zmian"
        },
        {
          "path": "analysis/evidence/original-package-audit.md",
          "label": "Oryginalny SGJP: pełne porównanie i granica eksportu"
        },
        {
          "path": "analysis/evidence/source-policy-clarification.md",
          "label": "Sprostowanie polityki źródeł"
        },
        {
          "path": "analysis/evidence/quality-runtime.json",
          "label": "Powtarzalne próbki rzeczywistego lemma-all"
        },
        {
          "path": "analysis/evidence/disrecommended-decision.md",
          "label": "Decyzja przed filtrem form niezalecanych"
        },
        {
          "path": "analysis/evidence/approved-rules-runtime.json",
          "label": "Pełny runtime zatwierdzonych fragmentów"
        },
        {
          "path": "analysis/evidence/mixed-history-decision.md",
          "label": "Pierwszeństwo mieszanych oznaczeń historycznych"
        },
        {
          "path": "analysis/evidence/history-runtime.json",
          "label": "Pełna kontrola warunków wieku"
        },
        {
          "path": "analysis/evidence/filter-report-runtime.json",
          "label": "Raport efektów filtrów rzeczywistych analiz"
        },
        {
          "path": "analysis/evidence/wiktionary-attestation-decision.md",
          "label": "Rodzaj źródła pomocniczych poświadczeń"
        },
        {
          "path": "analysis/evidence/usage-incorrect-runtime.json",
          "label": "Pełna ekspozycja zakresu użycia i niepoprawności"
        },
        {
          "path": "analysis/evidence/incorrect-forms-decision.md",
          "label": "Decyzja dotycząca jawnego niepopr."
        },
        {
          "path": "analysis/evidence/incorrect-runtime.json",
          "label": "Pełny runtime niepoprawności i alternatywnych analiz"
        },
        {
          "path": "analysis/evidence/descriptive-label-review.json",
          "label": "Przegląd 357 etykiet opisowych"
        },
        {
          "path": "analysis/evidence/descriptive-derivation-runtime.json",
          "label": "Pełny runtime etykiet i kandydatów konstrukcji"
        },
        {
          "path": "analysis/evidence/context-restrictions-decision.md",
          "label": "Wybór traktowania wymagań kontekstu"
        },
        {
          "path": "analysis/evidence/context-runtime.json",
          "label": "Pełny runtime zatwierdzonego kontekstu"
        },
        {
          "path": "analysis/evidence/qualifier-coverage-review.md",
          "label": "Pokrycie warunków: pełny przegląd"
        },
        {
          "path": "analysis/evidence/qualifier-condition-coverage.json",
          "label": "Pełny raport615 pól i605 etykiet"
        },
        {
          "path": "analysis/evidence/qualifier-coverage-runtime.json",
          "label": "Powtarzalność raportu i przykłady luk"
        },
        {
          "path": "analysis/evidence/persisted-constructions-review.md",
          "label": "Utrwalanie konstrukcji: przegląd"
        },
        {
          "path": "analysis/evidence/persisted-constructions-runtime.json",
          "label": "Pełny runtime dwóch potwierdzonych klas"
        },
        {
          "path": "analysis/evidence/build-links-integration-review.md",
          "label": "KWJP w build: przegląd"
        },
        {
          "path": "analysis/evidence/build-links-integration-checks.json",
          "label": "Testy i hashe przyrostu"
        },
        {
          "path": "analysis/evidence/contraction-proof-decision.md",
          "label": "Decyzja dowodu kontrakcji"
        },
        {
          "path": "analysis/evidence/constructions-links-review.md",
          "label": "Przegląd kontrakcji, hostów i powiązań"
        },
        {
          "path": "analysis/evidence/preposition-runtime.json",
          "label": "Pełny runtime klasy przyimkowej"
        },
        {
          "path": "analysis/evidence/mobile-by-runtime.json",
          "label": "Pełny runtime hostów by"
        },
        {
          "path": "analysis/evidence/winien-explain-runtime.json",
          "label": "Siedem rzeczywistych errat w explain"
        },
        {
          "path": "analysis/evidence/combined-constructions-runtime.json",
          "label": "Powtarzalność wszystkich wdrożonych klas konstrukcji"
        },
        {
          "path": "../../../../docs/generator/publikacja.md",
          "label": "Zatwierdzone warunki publikacji"
        },
        {
          "path": "analysis/evidence/orthography-2026-decision.md",
          "label": "Wybór normy przy nieoznaczonych dawnych zapisach"
        },
        {
          "path": "analysis/evidence/mobile-host-inventory.json",
          "label": "Pełna inwentaryzacja czterech zamkniętych klas hostów"
        },
        {
          "path": "analysis/evidence/norm-mobile-review.md",
          "label": "Norma 2026 i zamknięte mobilne klasy: przegląd"
        },
        {
          "path": "analysis/evidence/norm-mobile-constructions-runtime.json",
          "label": "Połączony runtime normy i mobilnych klas"
        },
        {
          "path": "analysis/evidence/mobile-variant-runtime.json",
          "label": "Pełny runtime mobilnych wariantów"
        },
        {
          "path": "analysis/evidence/mobile-variant-conflicts.json",
          "label": "Wyjaśnienie ośmiu różnic wariantu"
        },
        {
          "path": "analysis/evidence/norm-mobile-explain-runtime.json",
          "label": "Rzeczywiste explain normy i mobilnych klas"
        },
        {
          "path": "analysis/evidence/remaining-contractions-scope-decision.md",
          "label": "Wybór zakresu niepoświadczonych kontrakcji"
        },
        {
          "path": "analysis/evidence/first-release-scope-review.md",
          "label": "Zakres pierwszego wydania i sekwencje by"
        },
        {
          "path": "analysis/evidence/first-release-scope-runtime.json",
          "label": "Rzeczywista kontrola zakresu kontrakcji"
        },
        {
          "path": "analysis/evidence/conditional-scope-runtime.json",
          "label": "Powtarzalność pięciu klas konstruktorów bez impt"
        },
        {
          "path": "analysis/evidence/unexplained-labels-first-release-decision.md",
          "label": "Wybór wymogu objaśnień 25 oznaczeń SGJP"
        },
        {
          "path": "analysis/evidence/unexplained-and-logical-content-review.md",
          "label": "Przegląd A i logicznej treści"
        },
        {
          "path": "analysis/evidence/unexplained-labels-condition-coverage.json",
          "label": "Pełne pokrycie zatwierdzonego wyjątku25"
        },
        {
          "path": "analysis/evidence/unexplained-labels-runtime.json",
          "label": "Pełny runtime25i sześć explain"
        },
        {
          "path": "analysis/evidence/logical-content-projection-runtime.json",
          "label": "Powtarzalny hash rzeczywistej projekcji"
        },
        {
          "path": "analysis/evidence/accent-gloss-first-release-decision.md",
          "label": "Wymóg objaśnienia akcent: dwa rekordy"
        },
        {
          "path": "analysis/evidence/accent-and-source-game-review.md",
          "label": "Przegląd akcent i klas gry"
        },
        {
          "path": "analysis/evidence/accent-game-runtime.json",
          "label": "Pełny runtime warunków i explain"
        },
        {
          "path": "analysis/evidence/source-game-condition-coverage.json",
          "label": "Pełna ekspozycja klas gry"
        },
        {
          "path": "analysis/evidence/accent-condition-coverage.json",
          "label": "Pokrycie po A adnotacji akcent"
        },
        {
          "path": "analysis/evidence/personal-scope-runtime.json",
          "label": "Powtarzalna projekcja z osobowymi hostami"
        },
        {
          "path": "analysis/evidence/construction-game-runtime.json",
          "label": "Wyłączenia konstrukcji i całe ślady"
        },
        {
          "path": "analysis/evidence/persisted-assessments-review.md",
          "label": "Utrwalone analizy i powody ocen"
        },
        {
          "path": "analysis/evidence/persisted-assessment-runtime.json",
          "label": "Rzeczywista kontrola zapisanych ocen"
        },
        {
          "path": "analysis/evidence/capitalization-source-cases.json",
          "label": "Przykłady wielkiej litery i niezależnego homonimu"
        },
        {
          "path": "analysis/evidence/game-capitalization-norm-decision.md",
          "label": "Norma odniesienia growej wielkiej litery"
        },
        {
          "path": "analysis/evidence/capital-double-review.md",
          "label": "Przegląd normy growej i podwojonej partykuły"
        },
        {
          "path": "analysis/evidence/capital-double-runtime.json",
          "label": "Powtarzalne pełne wejścia obecnych konstruktorów"
        },
        {
          "path": "analysis/evidence/capital-double-conditions.json",
          "label": "Kontrola obu wariantów i homonimów"
        },
        {
          "path": "analysis/evidence/frag-semantic-gap.json",
          "label": "Pełna inwentaryzacja frag i brak klasyfikacji semantycznej"
        },
        {
          "path": "analysis/evidence/sgjp-semantic-metadata-request.md",
          "label": "Przygotowane zapytanie do autorów, niewysłane"
        },
        {
          "path": "analysis/evidence/pan-data-recheck.md",
          "label": "Ponowny przegląd PAN: konteksty i granice dowodów"
        },
        {
          "path": "analysis/evidence/pan-data-recheck.json",
          "label": "Przykłady list, identyfikatory próbek i hashe"
        },
        {
          "path": "analysis/evidence/pan-semantic-review.md",
          "label": "Pełny rejestr frag: przegląd i granice mapowania"
        },
        {
          "path": "analysis/evidence/pan-semantic-cases.json",
          "label": "147 przypadków, alternatywy i ślady dowodów"
        },
        {
          "path": "analysis/evidence/pan-semantic-coverage.json",
          "label": "Pokrycie, odtworzenie i kontrola odczytu"
        },
        {
          "path": "analysis/evidence/pan-document-review.md",
          "label": "Dokumentacyjne mapowanie PAN i granica znaczenia"
        },
        {
          "path": "analysis/evidence/pan-semantic-document-review.json",
          "label": "Dokładne adnotacje14 użyć"
        },
        {
          "path": "analysis/evidence/pan-document-review-coverage.json",
          "label": "Odtworzenie i pokrycie przeglądu"
        },
        {
          "path": "analysis/evidence/general-class-age-decision.md",
          "label": "Wiek klasy a konkretnego znaczenia — pending"
        },
        {
          "path": "analysis/evidence/sgjp-public-reader-review.md",
          "label": "Dostępne glosy: punktowy odczyt i granice"
        },
        {
          "path": "analysis/evidence/sgjp-public-reader-observations.json",
          "label": "Metryki13 publicznych odczytów"
        },
        {
          "path": "analysis/evidence/unresolved-report-review.md",
          "label": "Raport niewiadomych zapisanych analiz"
        },
        {
          "path": "analysis/evidence/unresolved-runtime.json",
          "label": "Readonly raport219713 analiz, dwa odtworzenia"
        },
        {
          "path": "analysis/evidence/documented-name-class-proof-decision.md",
          "label": "Próg dowodu klasy członu nazwiska — pending"
        },
        {
          "path": "analysis/evidence/documented-names-runtime.json",
          "label": "documented-names-runtime.json"
        },
        {
          "path": "analysis/evidence/persisted-filter-impact-runtime.json",
          "label": "persisted-filter-impact-runtime.json"
        },
        {
          "path": "analysis/evidence/documented-names-filter-review.md",
          "label": "documented-names-filter-review.md"
        },
        {
          "path": "analysis/evidence/sgjp-full-frag-reader-review.md",
          "label": "sgjp-full-frag-reader-review.md"
        },
        {
          "path": "analysis/evidence/sgjp-full-frag-reader-observations.json",
          "label": "sgjp-full-frag-reader-observations.json"
        },
        {
          "path": "analysis/evidence/sgjp-full-frag-reader-coverage.json",
          "label": "sgjp-full-frag-reader-coverage.json"
        },
        {
          "path": "analysis/evidence/semantic-use-alternatives-decision.md",
          "label": "semantic-use-alternatives-decision.md"
        },
        {
          "path": "analysis/evidence/semantic-use-implementation-review.md",
          "label": "semantic-use-implementation-review.md"
        },
        {
          "path": "analysis/evidence/semantic-use-runtime.json",
          "label": "semantic-use-runtime.json"
        },
        {
          "path": "analysis/evidence/documented-use-positive-proof-decision.md",
          "label": "documented-use-positive-proof-decision.md"
        },
        {
          "path": "analysis/evidence/positive-use-runtime.json",
          "label": "positive-use-runtime.json"
        },
        {
          "path": "analysis/evidence/positive-use-implementation-review.md",
          "label": "positive-use-implementation-review.md"
        },
        {
          "path": "analysis/evidence/capitalization-coverage.json",
          "label": "capitalization-coverage.json"
        },
        {
          "path": "analysis/evidence/capitalization-coverage-probe.py",
          "label": "capitalization-coverage-probe.py"
        },
        {
          "path": "analysis/evidence/documented-spelling-variants-decision.md",
          "label": "documented-spelling-variants-decision.md"
        },
        {
          "path": "analysis/evidence/spelling-variants-runtime.json",
          "label": "Runtime pisowni"
        },
        {
          "path": "analysis/evidence/spelling-variants-implementation-review.md",
          "label": "Wdrożenie pisowni"
        },
        {
          "path": "analysis/evidence/quality-links-runtime.json",
          "label": "Pełny pomiar próbek linków"
        },
        {
          "path": "analysis/evidence/quality-words-runtime.json",
          "label": "Pomiar próbek słów"
        },
        {
          "path": "analysis/evidence/quality-strata-implementation-review.md",
          "label": "Warstwy quality-v1"
        },
        {
          "path": "analysis/evidence/canonical-index-implementation-review.md",
          "label": "Diagnostyczny I2"
        },
        {
          "path": "analysis/evidence/resident-relations-observation.json",
          "label": "Własna obserwacja jawnych relacji mieszkańca"
        },
        {
          "path": "analysis/evidence/resident-relations-proof-decision.md",
          "label": "Próg dowodu relacyjnego mieszkańca"
        },
        {
          "path": "analysis/evidence/resident-use-implementation-review.md",
          "label": "Użycie mieszkańca — wdrożenie"
        },
        {
          "path": "analysis/evidence/resident-use-runtime.json",
          "label": "Runtime użycia mieszkańca"
        },
        {
          "path": "analysis/evidence/coverage-implementation-review.md",
          "label": "Pokrycie klas"
        },
        {
          "path": "analysis/evidence/coverage-runtime.json",
          "label": "Runtime pokrycia"
        },
        {
          "path": "analysis/evidence/additional-phrase-use-review.md",
          "label": "Dalsze użycia SGJP"
        },
        {
          "path": "analysis/evidence/additional-phrase-runtime.json",
          "label": "Runtime dalszych użyć"
        },
        {
          "path": "analysis/evidence/age-baseline-inventory.json",
          "label": "Pełny pomiar wieku"
        },
        {
          "path": "analysis/evidence/standard-age-baseline-decision.md",
          "label": "Próg wieku STANDARD"
        },
        {
          "path": "analysis/evidence/age-baseline-implementation-review.md",
          "label": "Wdrożenie wieku STANDARD"
        },
        {
          "path": "analysis/evidence/age-baseline-runtime.json",
          "label": "Runtime wieku STANDARD"
        },
        {
          "path": "analysis/evidence/unknown-relevance-implementation-review.md",
          "label": "Niewiadome według wyniku słowa"
        },
        {
          "path": "analysis/evidence/unknown-relevance-runtime.json",
          "label": "Historyczny runtime niewiadomych"
        },
        {
          "path": "analysis/evidence/shared-lexical-proof-decision.md",
          "label": "Zakres leksykalnego dowodu STANDARD"
        },
        {
          "path": "analysis/evidence/shared-lexical-proof-simulation.json",
          "label": "Symulacja readonly sześciu użyć"
        }
      ],
      "gate": {
        "id": "documented_lexical_proof_shared_variants",
        "status": "pending",
        "created_at": "2026-10-05T19:41:13Z",
        "question": "Czy sprawdzony dowód konkretnego polskiego użycia SGJP stosujemy do warunku leksykalnego również w STANDARD, z osobnymi pozostałymi warunkami?",
        "options": {
          "A": "Ten sam dowód leksykalny dla obu wariantów, wiek/pisownia/gra osobno (rekomendowane).",
          "B": "Dowód tylko BROAD; STANDARD wymaga osobnego dowodu leksykalnego."
        },
        "answer": null,
        "artifact": "analysis/evidence/shared-lexical-proof-decision.md"
      }
    },
    {
      "id": "phase_9",
      "name": "TDD green",
      "icon_hint": "analysis",
      "status": "pending",
      "started": null,
      "completed": null,
      "skip_reason": null,
      "summary": null,
      "decisions": [],
      "risks": [],
      "artifacts": [],
      "gate": null
    },
    {
      "id": "phase_10",
      "name": "Wybór weryfikacji",
      "icon_hint": "analysis",
      "status": "pending",
      "started": null,
      "completed": null,
      "skip_reason": null,
      "summary": null,
      "decisions": [],
      "risks": [],
      "artifacts": [],
      "gate": null
    },
    {
      "id": "phase_11",
      "name": "Weryfikacja",
      "icon_hint": "analysis",
      "status": "pending",
      "started": null,
      "completed": null,
      "skip_reason": null,
      "summary": null,
      "decisions": [],
      "risks": [],
      "artifacts": [],
      "gate": null
    },
    {
      "id": "phase_12",
      "name": "E2E",
      "icon_hint": "analysis",
      "status": "pending",
      "started": null,
      "completed": null,
      "skip_reason": null,
      "summary": null,
      "decisions": [],
      "risks": [],
      "artifacts": [],
      "gate": null
    },
    {
      "id": "phase_13",
      "name": "Dokumentacja",
      "icon_hint": "analysis",
      "status": "pending",
      "started": null,
      "completed": null,
      "skip_reason": null,
      "summary": null,
      "decisions": [],
      "risks": [],
      "artifacts": [],
      "gate": null
    },
    {
      "id": "phase_14",
      "name": "Finalizacja",
      "icon_hint": "analysis",
      "status": "pending",
      "started": null,
      "completed": null,
      "skip_reason": null,
      "summary": null,
      "decisions": [],
      "risks": [],
      "artifacts": [],
      "gate": null
    }
  ],
  "verification": {
    "status": null,
    "issues": [],
    "fixes": [],
    "reverify_count": 0
  }
};
