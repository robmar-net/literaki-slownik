window.MAISTER_DATA = {
  "generated": "2026-10-12T00:20:23Z",
  "task": {
    "title": "STANDARD: formy dawne i współczesne użycie (#4)",
    "description": "Research przyczyn odmów, niezależnych miar współczesności i skutków wariantów; komentarz do ticketu; decyzje z właścicielem.",
    "status": "awaiting_review",
    "tags": [
      "research",
      "slownik",
      "issue-4"
    ],
    "priority": null,
    "type": "research",
    "path": "/Users/robmar/Projects/Literaki/literaki-slownik/.maister/tasks/research/2026-10-12-standard-formy-dawne",
    "current_activity": "Wyniki gotowe; rozmowa z właścicielem"
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
      "validation.json"
    ],
    "confidence_level": "high_for_mechanism_and_counts_medium_for_semantic_recommendation",
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
      "issue": "https://github.com/robmar-net/literaki-slownik/issues/4",
      "status": "prepared",
      "comment_url": null
    }
  },
  "phases": [
    {
      "summary": "Próg formy 30 potwierdzony. Lemma+POS dodałoby 4559 form; 35/40 grup próbki daje tylko archaiczną odmianę. Potrzebna osobna ocena leksemu i formy.",
      "decisions": [
        "Tylko research, bez brainstormingu, projektu i implementacji — jawna prośba użytkownika."
      ],
      "risks": [
        "Brak pełnego audytu znaczeń w całym przyroście",
        "Korpus KWJP kończy się na 2020"
      ],
      "artifacts": [
        {
          "path": "outputs/research-report.md",
          "label": "Raport researchu",
          "html": "outputs/research-report.html"
        },
        {
          "path": "analysis/findings/measurements.json",
          "label": "Pomiary"
        },
        {
          "path": "analysis/findings/sample-review.md",
          "label": "Przegląd próbek"
        }
      ],
      "gate": {
        "question": "Czy przyjmujesz research jako podstawę rozmowy o kryterium STANDARD, czy najpierw pogłębiamy ocenę próbki?",
        "choices": [
          "Przyjąć research i omówić kryterium",
          "Pogłębić próbkę przed decyzjami"
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
    "status": "research_checked_awaiting_owner",
    "issues": [],
    "fixes": [],
    "reverify_count": 0
  }
};
