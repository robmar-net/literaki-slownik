window.MAISTER_DATA = {
  "generated": "2026-10-12T08:10:44Z",
  "task": {
    "title": "STANDARD: formy dawne i współczesne użycie (#4)",
    "description": "Research przyczyn odmów, niezależnych miar współczesności i skutków wariantów; komentarz do ticketu; decyzje z właścicielem.",
    "status": "awaiting_approval",
    "tags": [
      "research",
      "slownik",
      "issue-4"
    ],
    "priority": null,
    "type": "research",
    "path": "/Users/robmar/Projects/Literaki/literaki-slownik/.maister/tasks/research/2026-10-12-standard-formy-dawne",
    "current_activity": "Wyniki audytu POP, rodzin i obecnych przyjęć do omówienia"
  },
  "characteristics": {
    "runda": 4,
    "tryb": "Tylko research; wdrożenie niezatwierdzone",
    "pytanie": "Dlaczego współczesne słowa odpadają przez dawność i jaka niezależna od SJP.pl miara pozwala zmienić tę regułę z kontrolowanym ryzykiem?",
    "metody": "śledzenie przepływu, triangulacja, symulacja wyłącznie do odczytu, jawna próbka jakości",
    "zakres bieżący": "110 rodzin, 12 zapisów, pełne przyczyny ubytków POP i dag/dekagram",
    "pewność": "Wysoka dla pomiarów; średnia dla ocen językowych"
  },
  "research_context": {
    "research_type": "mixed",
    "research_question": "Dlaczego współczesne słowa odpadają przez dawność i jaka niezależna od SJP.pl miara pozwala zmienić tę regułę z kontrolowanym ryzykiem?",
    "scope": {
      "included": [
        "kod i testy",
        "decyzje i konfiguracje",
        "przypięte dane SGJP/KWJP/NKJP",
        "oficjalna dokumentacja",
        "analiza kontrfaktyczna i próbka",
        "komentarz issue #4"
      ],
      "excluded": [
        "wdrożenie",
        "zmiana reguł lub list",
        "wydanie",
        "wiki",
        "kontakt z zespołami źródeł",
        "brainstorming",
        "projekt architektury"
      ],
      "constraints": [
        "SJP.pl tylko benchmark",
        "licencje według istniejących decyzji",
        "brak redystrybucji surowego NKJP"
      ]
    },
    "methodology": [
      "śledzenie przepływu",
      "triangulacja",
      "symulacja wyłącznie do odczytu",
      "jawna próbka jakości"
    ],
    "sources": [
      "code-and-policy.md",
      "external-evidence.md",
      "measurements.json",
      "sample-review.md",
      "nkjp-examples.json",
      "context-review.json",
      "validation.json",
      "round2/metrics.json",
      "round2/census-1580.json",
      "round2/live-review.json",
      "round2/context-review.json",
      "round2/sgjp-review.json",
      "round2/dictionary-evidence.md",
      "round2/current-override.json",
      "round2/validation.json",
      "round3/family-decisions.json",
      "round3/candidate-matrix.json",
      "round3/current-review.json",
      "round3/context-review.json",
      "round3/sgjp-manifest.json",
      "round3/full-tables-manifest.json",
      "round3/kwjp-manifest.json",
      "round3/proposal.json",
      "round3/pop-baseline.json",
      "round3/pop-impact.json",
      "round3/sensitivity-pop-impact.json",
      "round3/dag-control.json",
      "round3/validation.json",
      "round4/family-review.json",
      "round4/current-twelve.json",
      "round4/pop-losses.json",
      "round4/dag-mechanism.json",
      "round4/pop-validation.json",
      "round4/eight-sensitivity.json",
      "round4/validation.json"
    ],
    "confidence_level": "high_for_counts_and_counterexamples_medium_for_register_unknown_population_error_rate",
    "gathering_strategy": {
      "categories": [
        "codebase",
        "documentation",
        "configuration_tests",
        "official_external",
        "pinned_data"
      ],
      "count": 5,
      "source": "ticket #4 i plan researchu"
    },
    "steps": {
      "brief": "completed",
      "plan": "completed",
      "gather": "completed",
      "synthesize": "completed"
    },
    "publication": {
      "round": 4,
      "issue": "https://github.com/robmar-net/literaki-slownik/issues/4",
      "status": "prepared",
      "report_artifact": "outputs/targeted-audit.md"
    },
    "gate_history": [
      {
        "question": "Czy przyjmujesz research jako podstawę rozmowy o kryterium STANDARD, czy najpierw pogłębiamy ocenę próbki?",
        "choices": [
          "Przyjąć research i omówić kryterium",
          "Pogłębić próbkę przed decyzjami"
        ],
        "answer": "Pogłębić próbkę: użytkownik prosi o znacznie szersze badanie przed decyzją.",
        "answered_at": "2026-10-12T00:27:15Z"
      }
    ],
    "round": 4,
    "publication_history": [
      {
        "issue": "https://github.com/robmar-net/literaki-slownik/issues/4",
        "status": "published_and_verified",
        "comment_url": "https://github.com/robmar-net/literaki-slownik/issues/4#issuecomment-6115542830",
        "report_commit": "58396d7a967236de9f479250aff8802dbc078f0b",
        "round": 1
      },
      {
        "round": 2,
        "issue": "https://github.com/robmar-net/literaki-slownik/issues/4",
        "status": "published_and_verified",
        "comment_url": "https://github.com/robmar-net/literaki-slownik/issues/4#issuecomment-6115957580",
        "report_commit": "7666b28b5e700992c62960c90fdbcd408f71534c",
        "verified_at": "2026-10-12T01:09:42Z"
      },
      {
        "round": 3,
        "issue": "https://github.com/robmar-net/literaki-slownik/issues/4",
        "status": "published_and_verified",
        "report_artifact": "outputs/candidate-assessment.md",
        "comment_url": "https://github.com/robmar-net/literaki-slownik/issues/4#issuecomment-6119310098",
        "report_commit": "67c06ecdef4ef5dac9734fa9d0acbe557c45eaa5",
        "verified_at": "2026-10-12T06:56:59Z"
      }
    ],
    "direction_decision": {
      "status": "accepted_as_direction_only",
      "recorded_at": "2026-10-12T01:18:10Z",
      "user_response": "ok",
      "principle": "Jeśli słowo ma choć jedno współczesne znaczenie, dopuszczamy odpowiadającą mu współczesną odmianę — także rzadkie, regularne formy.",
      "scope": "Ocena dawności przy zachowaniu pozostałych kryteriów STANDARD. Frazeologizm nie uzasadnia pełnej odmiany; dowód nie przechodzi na inne znaczenia i dawne końcówki. Książkowość i rzadkość nadal dopuszczalne.",
      "evidence_direction": "Frekwencja wyłania i porządkuje kandydatów. Sprawdzamy znaczenie, odmianę oraz rzeczywiste użycia autorskie w różnych tekstach.",
      "implementation_approved": false,
      "threshold_selected": false,
      "candidate_batch_approved": false,
      "open_questions": [
        "Dokładne wymagania dowodowe i przypadki graniczne",
        "Wpływ na nowe formy, obecne przyjęcia oraz POP/POP0"
      ],
      "next_recommended_step": "Ocena kandydatów i pomiar wpływu według uzgodnionej zasady; potem osobne uzgodnienie wdrożenia."
    },
    "direction_publication": {
      "status": "published_and_verified",
      "issue": "https://github.com/robmar-net/literaki-slownik/issues/4",
      "artifact": "outputs/issue-comment-direction.md",
      "comment_url": "https://github.com/robmar-net/literaki-slownik/issues/4#issuecomment-6116044652",
      "verified_at": "2026-10-12T01:18:39Z"
    },
    "completion_history": [
      {
        "completed": "2026-10-12T01:18:39Z",
        "round": 2
      }
    ],
    "candidate_assessment": {
      "user_request": "ok, idzmy",
      "steps": {
        "brief": "completed",
        "plan": "completed",
        "gather": "completed",
        "synthesize": "completed"
      },
      "scope": "404 grupy / 3364 formy, 290 zależnych przyjęć, kontrole i pełne rodziny potwierdzonych kandydatów.",
      "result_counts": {
        "new_words": 2382,
        "families_with_additions": 110,
        "previous_candidates_remaining": 2367,
        "current_words_reviewed": 290,
        "unsupported_evidence_words": 12
      },
      "recommendation": "Omówić konkretną paczkę i skutki rankingu; cofanie przyjęć rozpatrzyć osobno. Dalsze badanie celowane na wskazaną granicę."
    },
    "targeted_audit": {
      "user_request": "ok, zrob tak",
      "steps": {
        "brief": "completed",
        "plan": "completed",
        "gather": "completed",
        "synthesize": "completed"
      },
      "lanes": {
        "pop": "coordinator",
        "families": "family_review",
        "current_twelve": "current_twelve_review"
      },
      "scope": "110 rodzin, 12 zapisów, pełne przyczyny ubytków POP i dag/dekagram",
      "lane_status": {
        "pop": "completed",
        "families": "completed",
        "current_twelve": "completed"
      },
      "result_counts": {
        "families": 110,
        "proposed_forms": 2382,
        "explained_pop_losses": 2430,
        "exact_contexts": 771,
        "supplement_contexts": 25,
        "withdrawal_candidates": 8,
        "withdrawal_analyses": 24,
        "holds": 4,
        "held_analyses": 6
      },
      "recommendation": "Przyjąć audyt jako podstawę osobnych decyzji; dodatki przy zachowaniu metody POP, cofnięcia oddzielnie. Bez dalszego ogólnego poszerzania próbki."
    }
  },
  "phases": [
    {
      "summary": "Runda 2: pełne 1580 grup (1176 tylko arch.), 155 form i 80 kontroli; 107 fragmentów i 643 konkordancje; 40 haseł SGJP/47 artykułów. Żywe odrzucenia oraz obce dowody w obu kierunkach. Brak podstaw do prostego progu.",
      "decisions": [
        "Tylko research, bez brainstormingu, projektu i implementacji — jawna prośba użytkownika.",
        "Kierunek przyjęty przez użytkownika: współczesne znaczenie i odpowiadająca mu współczesna odmiana, także rzadka; odrębny zakres dawnych końcówek, homonimów i frazeologizmów. Bez nowego progu i paczki 3364 form."
      ],
      "risks": [
        "Brak pełnego audytu znaczeń 3364 form i niezależnego drugiego anotatora",
        "Pierwsze konkordancje nie są losowe; ocena rejestru ma średnią pewność",
        "KWJP obejmuje 2011–2020; nowsze źródła tylko punktowe",
        "Spłaszczone kwalifikatory i brak mapowania wszystkich znaczeń"
      ],
      "artifacts": [
        {
          "path": "outputs/research-report.md",
          "label": "Pogłębiony raport",
          "html": "outputs/research-report.html"
        },
        {
          "path": "analysis/findings/round2/metrics.json",
          "label": "40 sond i pełne liczby"
        },
        {
          "path": "analysis/findings/round2/live-review.json",
          "label": "257 zapytań i oceny kontekstów"
        },
        {
          "path": "analysis/findings/round2/dictionary-evidence.md",
          "label": "Znaczenia, odmiana i nowe źródła"
        },
        {
          "path": "analysis/findings/round2/validation.json",
          "label": "Walidacja danych i decyzji bazy"
        },
        {
          "path": "outputs/issue-comment-round2.md",
          "label": "Uzupełnienie do ticketu"
        },
        {
          "path": "outputs/research-report-round1.md",
          "label": "Zachowana runda 1"
        },
        {
          "path": "outputs/issue-comment-direction.md",
          "label": "Uzgodnienie kierunku po researchu"
        }
      ],
      "gate": {
        "question": "Czy przyjmujesz pogłębiony research jako podstawę do omówienia kryterium STANDARD, czy potrzebujesz dalszego badania konkretnej grupy?",
        "choices": [
          "Przyjąć research i omówić kryterium",
          "Pogłębić wskazaną grupę"
        ],
        "answer": "Przyjęto research i zasadę oceny współczesnego znaczenia oraz odpowiadającej mu współczesnej odmiany jako kierunek dalszej pracy. Bez zgody na wdrożenie.",
        "answered_at": "2026-10-12T01:18:10Z",
        "followup_question": "Czy przyjmujemy tę zasadę jako kierunek dalszej rozmowy?",
        "user_response": "ok"
      },
      "started": "2026-10-12T00:04:14Z",
      "completed": "2026-10-12T01:18:10Z",
      "id": "research_foundation",
      "name": "Badanie i synteza",
      "icon_hint": "analysis",
      "status": "completed"
    },
    {
      "summary": "Propozycja 2382 form / 110 rodzin: 997 ze starej paczki i 1385 spoza niej. Wszystkie 290 przyjęć sprawdzone; 12 bez zgodnego dowodu w wybranych kontekstach. POP +2372/−2430, POP0 +481. Wyniki gotowe do omówienia.",
      "decisions": [
        "Tylko research; paczka i wdrożenie niezatwierdzone.",
        "Główny scenariusz zachowuje obecne przyjęcia; cofnięcie 12 jest osobną analizą wrażliwości.",
        "Nie dobrano progu frekwencji; dowód dotyczy znaczenia i właściwej odmiany."
      ],
      "risks": [
        "Jeden badacz; średnia pewność oceny znaczeń i rejestru.",
        "2367 dawnych kandydatów poza propozycją nie jest zbiorowo odrzucone.",
        "POP nie rośnie monotonicznie wraz ze STANDARD; ubytki wymagają omówienia.",
        "Brak zatwierdzonego produkcyjnego mapowania czytnika do snapshotu."
      ],
      "artifacts": [
        {
          "path": "planning/candidate-assessment-plan.md",
          "label": "Plan rundy 3"
        },
        {
          "path": "outputs/candidate-assessment.md",
          "html": "outputs/candidate-assessment.html",
          "label": "Ocena kandydatów i wpływ"
        },
        {
          "path": "analysis/findings/round3/proposal.json",
          "label": "2382 formy i zakresy rodzin"
        },
        {
          "path": "analysis/findings/round3/candidate-matrix.json",
          "label": "404 grupy / 3364 formy"
        },
        {
          "path": "analysis/findings/round3/current-review.json",
          "label": "Kontrola 290 przyjęć"
        },
        {
          "path": "analysis/findings/round3/pop-impact.json",
          "label": "Pełna delta POP/POP0"
        },
        {
          "path": "analysis/findings/round3/sensitivity-pop-impact.json",
          "label": "Wrażliwość na cofnięcie 12"
        },
        {
          "path": "analysis/findings/round3/validation.json",
          "label": "Walidacja 7192 analiz"
        },
        {
          "path": "outputs/issue-comment-round3.md",
          "label": "Opublikowany komentarz rundy 3"
        }
      ],
      "gate": {
        "question": "Czy przyjmujesz wyniki rundy 3 jako podstawę rozmowy o paczce i skutkach dla POP, czy najpierw pogłębiamy wskazaną grupę?",
        "choices": [
          "Przyjąć wyniki do omówienia",
          "Pogłębić wskazaną grupę"
        ],
        "answer": "Przyjęto wyniki rundy 3 jako podstawę decyzji; użytkownik zlecił zalecany audyt POP, niezależny przegląd rodzin i osobno 12 obecnych przyjęć. Bez wdrożenia.",
        "implementation_approved": false,
        "user_response": "ok, zrob tak",
        "answered_at": "2026-10-12T07:07:20Z"
      },
      "started": "2026-10-12T01:23:38Z",
      "completed": "2026-10-12T07:07:20Z",
      "id": "candidate_assessment",
      "name": "Ocena kandydatów i wpływu",
      "icon_hint": "analysis",
      "status": "completed"
    },
    {
      "summary": "Potwierdzono 110 rodzin i 2382 formy. Wyjaśniono wszystkie 2430 ubytków POP oraz zależność dag/dekagram. Z 12 zapisów: 8 / 24 analizy do osobnej decyzji o cofnięciu; 4 / 6 analiz wstrzymane. Wyniki zweryfikowane, bez wdrożenia.",
      "decisions": [
        "Tylko research; brak zgody na wdrożenie lub automatyczne cofnięcia.",
        "Rekomendacja: zachować obecną metodę POP i rozpatrzyć paczkę 2382 dodatków w osobnej decyzji wdrożeniowej.",
        "Cofnięcia oddzielnie; sek, um, moko i tem pozostają wstrzymane po nowych dowodach."
      ],
      "risks": [
        "Średnia pewność ocen językowych; osobni agenci używają tego samego modelu i częściowo zależnych źródeł.",
        "Um: granica archaizowania; sek: konflikt kwalifikacji; moko i tem: nowy sens wymaga własnej podstawy leksykalnej i morfologicznej.",
        "POP jest ograniczonym rankingiem; prawidłowe dodatki do STANDARD mogą usuwać inne formy z POP.",
        "Nie oszacowano błędu całej populacji; pomocnicze tropy Khan Academy i szkolnego PDF nie są pełnym zweryfikowanym dowodem."
      ],
      "artifacts": [
        {
          "path": "planning/round4-plan.md",
          "label": "Plan celowanego audytu"
        },
        {
          "path": "outputs/targeted-audit.md",
          "html": "outputs/targeted-audit.html",
          "label": "Wynik audytu i rekomendacja"
        },
        {
          "path": "analysis/findings/round4/family-review.md",
          "label": "Przegląd 110 rodzin"
        },
        {
          "path": "analysis/findings/round4/family-review.json",
          "label": "Macierz 110 rodzin i źródeł"
        },
        {
          "path": "analysis/findings/round4/current-twelve.md",
          "label": "Ocena 12 obecnych przyjęć"
        },
        {
          "path": "analysis/findings/round4/current-twelve.json",
          "label": "30 analiz i 796 adnotacji"
        },
        {
          "path": "analysis/findings/round4/pop-method-review.md",
          "label": "Niezależny przegląd metody POP"
        },
        {
          "path": "analysis/findings/round4/pop-losses.json",
          "label": "Przyczyny wszystkich 2430 ubytków"
        },
        {
          "path": "analysis/findings/round4/dag-mechanism.json",
          "label": "Dag i dekagram: ślady i kontrole"
        },
        {
          "path": "analysis/findings/round4/eight-sensitivity.json",
          "label": "Osobna wrażliwość na 8 cofnięć"
        },
        {
          "path": "analysis/findings/round4/validation.json",
          "label": "Walidacja kompletności i zgodności"
        }
      ],
      "gate": {
        "question": "Czy przyjmujesz wyniki audytu jako podstawę osobnej decyzji o wdrożeniu, czy pogłębiamy konkretny nierozstrzygnięty przypadek?",
        "choices": [
          "Przyjąć wyniki do osobnej decyzji",
          "Pogłębić wskazany przypadek"
        ],
        "answer": null,
        "implementation_approved": false
      },
      "started": "2026-10-12T07:07:20Z",
      "completed": null,
      "id": "targeted_audit",
      "name": "Audyt POP i niezależny przegląd",
      "icon_hint": "analysis",
      "status": "awaiting_approval"
    },
    {
      "id": "solution_generation",
      "name": "Brainstorming",
      "status": "skipped",
      "skip_reason": "Tylko research — prośba użytkownika."
    },
    {
      "id": "high_level_design",
      "name": "Projekt",
      "status": "skipped",
      "skip_reason": "Tylko research — prośba użytkownika."
    }
  ],
  "verification": {
    "status": "round4_passed_awaiting_research_gate",
    "issues": [],
    "fixes": [],
    "reverify_count": 0
  }
};
