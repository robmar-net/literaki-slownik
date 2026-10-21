window.MAISTER_DATA = {
  "generated": "2026-10-21T14:39:24Z",
  "task": {
    "title": "POP00 — proste i znajome formy",
    "description": "Możliwość ograniczenia form leksemów POP0 do języka zwykłego gracza.",
    "status": "completed",
    "tags": [
      "pop00",
      "fleksja"
    ],
    "priority": null,
    "type": "research",
    "path": "/Users/robmar/Projects/Literaki/literaki-slownik/.maister/tasks/research/2026-10-21-pop00-proste-formy",
    "current_activity": "Przekazano do publicznego ticketu #10"
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
      "status": "completed",
      "started": "2026-10-21T14:31:23Z",
      "completed": "2026-10-21T14:39:24Z",
      "summary": "Operator zlecił na razie publiczny ticket z obowiązkowym opisem wiki; dalsze planowanie i implementacja przez maister-quick-plan. Osobne fazy wariantów i projektu w research odłożone do tej pracy.",
      "decisions": [
        "Operator zlecił na razie publiczny ticket z obowiązkowym opisem wiki; dalsze planowanie i implementacja przez maister-quick-plan. Osobne fazy wariantów i projektu w research odłożone do tej pracy."
      ],
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
            "answer": "Odłożone w tym research; operator wybrał przekazanie do ticketu i maister-quick-plan."
          },
          {
            "id": "design",
            "question": "Czy po wyborze wariantu przygotować projekt działania generatora POP00?",
            "choices": [
              "Tak — rekomendowane",
              "Nie, zakończyć na rekomendacji"
            ],
            "answer": "Odłożone w tym research; operator wybrał przekazanie do ticketu i maister-quick-plan."
          }
        ],
        "answer": "Operator zlecił na razie publiczny ticket z obowiązkowym opisem wiki; dalsze planowanie i implementacja przez maister-quick-plan. Osobne fazy wariantów i projektu w research odłożone do tej pracy."
      },
      "skip_reason": null
    },
    {
      "id": "generation",
      "name": "Warianty rozwiązania",
      "status": "skipped",
      "started": null,
      "completed": null,
      "summary": "Operator zlecił na razie publiczny ticket z obowiązkowym opisem wiki; dalsze planowanie i implementacja przez maister-quick-plan. Osobne fazy wariantów i projektu w research odłożone do tej pracy.",
      "decisions": [],
      "risks": [],
      "artifacts": [],
      "gate": null,
      "skip_reason": "Operator zlecił na razie publiczny ticket z obowiązkowym opisem wiki; dalsze planowanie i implementacja przez maister-quick-plan. Osobne fazy wariantów i projektu w research odłożone do tej pracy."
    },
    {
      "id": "convergence",
      "name": "Wybór wariantu",
      "status": "skipped",
      "started": null,
      "completed": null,
      "summary": "Operator zlecił na razie publiczny ticket z obowiązkowym opisem wiki; dalsze planowanie i implementacja przez maister-quick-plan. Osobne fazy wariantów i projektu w research odłożone do tej pracy.",
      "decisions": [],
      "risks": [],
      "artifacts": [],
      "gate": null,
      "skip_reason": "Operator zlecił na razie publiczny ticket z obowiązkowym opisem wiki; dalsze planowanie i implementacja przez maister-quick-plan. Osobne fazy wariantów i projektu w research odłożone do tej pracy."
    },
    {
      "id": "design",
      "name": "Projekt wysokopoziomowy",
      "status": "skipped",
      "started": null,
      "completed": null,
      "summary": "Operator zlecił na razie publiczny ticket z obowiązkowym opisem wiki; dalsze planowanie i implementacja przez maister-quick-plan. Osobne fazy wariantów i projektu w research odłożone do tej pracy.",
      "decisions": [],
      "risks": [],
      "artifacts": [],
      "gate": null,
      "skip_reason": "Operator zlecił na razie publiczny ticket z obowiązkowym opisem wiki; dalsze planowanie i implementacja przez maister-quick-plan. Osobne fazy wariantów i projektu w research odłożone do tej pracy."
    },
    {
      "id": "handoff",
      "name": "Zakończenie",
      "status": "completed",
      "started": "2026-10-21T14:39:24Z",
      "completed": "2026-10-21T14:39:24Z",
      "summary": "Utworzono publiczny ticket #10 z badaniem, zakresem, kryteriami odbioru i wiki.",
      "decisions": [
        "Operator zlecił na razie publiczny ticket z obowiązkowym opisem wiki; dalsze planowanie i implementacja przez maister-quick-plan. Osobne fazy wariantów i projektu w research odłożone do tej pracy."
      ],
      "risks": [
        "Reguły i progi wymagają wyboru podczas planowania."
      ],
      "artifacts": [
        {
          "path": "outputs/research-handoff.md",
          "label": "Przekazanie do #10"
        }
      ],
      "gate": null,
      "skip_reason": null
    }
  ],
  "verification": {
    "status": "Rozpoznanie zaakceptowane; ticket #10 utworzony; research przekazany do planowania.",
    "issues": [],
    "fixes": [],
    "reverify_count": 0
  }
};
