window.MAISTER_DATA = {
  "generated": "2026-10-21T14:31:23Z",
  "task": {
    "title": "POP00 — proste i znajome formy",
    "description": "Możliwość ograniczenia form leksemów POP0 do języka zwykłego gracza.",
    "status": "awaiting_user",
    "tags": [
      "pop00",
      "fleksja"
    ],
    "priority": null,
    "type": "research",
    "path": "/Users/robmar/Projects/Literaki/literaki-slownik/.maister/tasks/research/2026-10-21-pop00-proste-formy",
    "current_activity": "Decyzje o porównaniu wariantów i projekcie"
  },
  "characteristics": {
    "confidence": "Wysoka: mechanika i pomiary; średnia: kierunek; nieustalona: efekt u graczy."
  },
  "phases": [
    {
      "id": "foundation",
      "name": "Rozpoznanie",
      "icon_hint": "analysis",
      "status": "completed",
      "summary": "POP00 wykonalny. Sam próg IPM≥1 daje 53443 formy, lecz usuwa zwykłe odmiany i 661 leksemów. Rekomendowany kierunek łączy częstość z ochroną zwykłej fleksji.",
      "decisions": [
        "Brak zmiany list i zasad gry; progi pozostają eksperymentem.",
        "Operator zaakceptował rozpoznanie; nie oznacza to wyboru reguł ani progu POP00."
      ],
      "risks": [
        "Nie ma ocen graczy ani pomiaru partii.",
        "Tokenizacja i próg publikacji nie pozwalają traktować braku wiersza jako nieznajomości."
      ],
      "artifacts": [
        {
          "path": "outputs/research-report.md",
          "label": "Raport POP00",
          "html": "outputs/research-report.html"
        },
        {
          "path": "analysis/synthesis.md",
          "label": "Synteza"
        },
        {
          "path": "planning/sources.md",
          "label": "Pokrycie źródeł"
        },
        {
          "path": "analysis/evidence/form-measurement.json",
          "label": "Pomiar form"
        },
        {
          "path": "analysis/evidence/lexeme-measurement.json",
          "label": "Pomiar leksemów"
        }
      ],
      "gate": {
        "question": "Czy przyjmujesz wyniki rozpoznania, czy najpierw pogłębić badanie?",
        "choices": [
          "Przyjąć rozpoznanie",
          "Pogłębić wskazany obszar"
        ],
        "answer": "2026-10-21: użytkownik „ok” — akceptacja wyników rozpoznania."
      },
      "started": "2026-10-21T14:18:57Z",
      "completed": "2026-10-21T14:31:23Z"
    },
    {
      "id": "optional_decision",
      "name": "Opcje dalszych faz",
      "status": "awaiting_user",
      "started": "2026-10-21T14:31:23Z",
      "completed": null,
      "summary": "Rekomendowane porównanie wariantów, a następnie projekt generatora dla wybranego podejścia.",
      "decisions": [],
      "risks": [
        "Projekt przed badaniem graczy pozostanie propozycją, nie dowodem naturalności."
      ],
      "artifacts": [],
      "gate": {
        "question": "Osobno ustalić porównanie wariantów oraz projekt po wyborze.",
        "questions": [
          {
            "id": "brainstorming",
            "question": "Czy włączyć porównanie trzech wariantów POP00?",
            "choices": [
              "Tak — rekomendowane",
              "Nie"
            ],
            "answer": null
          },
          {
            "id": "design",
            "question": "Czy po wyborze wariantu przygotować projekt działania generatora POP00?",
            "choices": [
              "Tak — rekomendowane",
              "Nie, zakończyć na rekomendacji"
            ],
            "answer": null
          }
        ],
        "answer": null
      },
      "skip_reason": null
    },
    {
      "id": "generation",
      "name": "Warianty rozwiązania",
      "status": "pending",
      "started": null,
      "completed": null,
      "summary": null,
      "decisions": [],
      "risks": [],
      "artifacts": [],
      "gate": null,
      "skip_reason": null
    },
    {
      "id": "convergence",
      "name": "Wybór wariantu",
      "status": "pending",
      "started": null,
      "completed": null,
      "summary": null,
      "decisions": [],
      "risks": [],
      "artifacts": [],
      "gate": null,
      "skip_reason": null
    },
    {
      "id": "design",
      "name": "Projekt wysokopoziomowy",
      "status": "pending",
      "started": null,
      "completed": null,
      "summary": null,
      "decisions": [],
      "risks": [],
      "artifacts": [],
      "gate": null,
      "skip_reason": null
    },
    {
      "id": "handoff",
      "name": "Zakończenie",
      "status": "pending",
      "started": null,
      "completed": null,
      "summary": null,
      "decisions": [],
      "risks": [],
      "artifacts": [],
      "gate": null,
      "skip_reason": null
    }
  ],
  "verification": {
    "status": "Rozpoznanie zaakceptowane; opcje dalszych faz oczekują na decyzję.",
    "issues": [],
    "fixes": [],
    "reverify_count": 0
  }
};
