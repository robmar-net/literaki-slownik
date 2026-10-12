window.MAISTER_DATA = {
  "generated": "2026-10-12T01:07:05Z",
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
    "current_activity": "Runda 2 gotowa; omówienie dowodów"
  },
  "characteristics": {
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
      "round2/validation.json"
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
      "round": 2,
      "issue": "https://github.com/robmar-net/literaki-slownik/issues/4",
      "status": "ready_to_publish",
      "comment_url": null,
      "report_commit": null
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
    "round": 2,
    "publication_history": [
      {
        "issue": "https://github.com/robmar-net/literaki-slownik/issues/4",
        "status": "published_and_verified",
        "comment_url": "https://github.com/robmar-net/literaki-slownik/issues/4#issuecomment-6115542830",
        "report_commit": "58396d7a967236de9f479250aff8802dbc078f0b",
        "round": 1
      }
    ]
  },
  "phases": [
    {
      "summary": "Runda 2: pełne 1580 grup (1176 tylko arch.), 155 form i 80 kontroli; 107 fragmentów i 643 konkordancje; 40 haseł SGJP/47 artykułów. Żywe odrzucenia oraz obce dowody w obu kierunkach. Brak podstaw do prostego progu.",
      "decisions": [
        "Tylko research, bez brainstormingu, projektu i implementacji — jawna prośba użytkownika."
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
        }
      ],
      "gate": {
        "question": "Czy przyjmujesz pogłębiony research jako podstawę do omówienia kryterium STANDARD, czy potrzebujesz dalszego badania konkretnej grupy?",
        "choices": [
          "Przyjąć research i omówić kryterium",
          "Pogłębić wskazaną grupę"
        ],
        "answer": null
      },
      "started": "2026-10-12T00:04:14Z",
      "completed": null,
      "id": "research_foundation",
      "name": "Badanie i synteza",
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
    "status": "round2_evidence_validated_awaiting_research_review",
    "issues": [
      "Nie było dostępnej przeglądarki CUA do wizualnego podglądu HTML; kontrola struktury i odsyłaczy wykonana lokalnie."
    ],
    "fixes": [],
    "reverify_count": 0
  }
};
