window.MAISTER_DATA = {
  "generated": "2026-10-21T14:27:51Z",
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
    "current_activity": "Odbiór wyników rozpoznania"
  },
  "characteristics": {
    "confidence": "Wysoka: mechanika i pomiary; średnia: kierunek; nieustalona: efekt u graczy."
  },
  "phases": [
    {
      "id": "foundation",
      "name": "Rozpoznanie",
      "icon_hint": "analysis",
      "status": "awaiting_user",
      "summary": "POP00 wykonalny. Sam próg IPM≥1 daje 53443 formy, lecz usuwa zwykłe odmiany i 661 leksemów. Rekomendowany kierunek łączy częstość z ochroną zwykłej fleksji.",
      "decisions": [
        "Brak zmiany list i zasad gry; progi pozostają eksperymentem."
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
        "answer": null
      },
      "started": "2026-10-21T14:18:57Z",
      "completed": null
    },
    {
      "id": "optional_decision",
      "name": "Opcje dalszych faz",
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
    "status": "Pomiary odtworzone; unia form równa wydanemu POP0; oczekuje na odbiór.",
    "issues": [],
    "fixes": [],
    "reverify_count": 0
  }
};
