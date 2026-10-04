window.MAISTER_DATA = {
  "generated": "2026-10-04T08:29:35Z",
  "task": {
    "title": "Audyt źródeł polskich słowników — etap 1",
    "description": "Realizacja rozdziału 15 specyfikacji v3: źródła, pomiary, filtry, dopasowania i projekt odtwarzalności.",
    "status": "in_progress",
    "tags": [
      "slowniki",
      "SGJP",
      "KWJP",
      "NKJP"
    ],
    "priority": null,
    "type": "research",
    "path": ".maister/tasks/research/2026-10-04-audyt-zrodel-polskich-slownikow",
    "current_activity": "Audyt zatwierdzony; wybór opcjonalnego porównania wariantów i projektu"
  },
  "characteristics": {
    "scope": "Audyt §15, bez produkcyjnych słowników"
  },
  "phases": [
    {
      "id": "phase_1",
      "name": "Podstawa badania",
      "icon_hint": "analysis",
      "status": "completed",
      "started": "2026-10-04T01:57:27Z",
      "completed": "2026-10-04T08:29:35Z",
      "skip_reason": null,
      "summary": "Audyt zatwierdzony przez użytkownika. Artefakty i wszystkie hashe manifestu zgodne przy wznowieniu; scenariusze filtrów pozostają materiałem do dalszych decyzji.",
      "decisions": [
        "SGJP i KWJP jako udokumentowane wejścia audytu",
        "Preferencja pełnych form eksportu; brak automatycznej nadgeneracji",
        "Publiczne tylko raporty/skrypty/manifesty; cache ignorowany"
      ],
      "risks": [
        "Warunki NKJP nieustalone",
        "Mieszane kwalifikatory i konstrukcje wieloleksemowe do rozstrzygnięcia",
        "Scenariusze filtrów nie są finalną polityką słowników"
      ],
      "artifacts": [
        {
          "path": "outputs/research-report.md",
          "label": "Raport audytu",
          "html": "outputs/research-report.html"
        },
        {
          "path": "analysis/synthesis.md",
          "label": "Synteza"
        },
        {
          "path": "analysis/findings/model-procesu.md",
          "label": "Model i proces"
        },
        {
          "path": "outputs/audit-manifest.json",
          "label": "Manifest"
        },
        {
          "path": "analysis/findings/audit-review.md",
          "label": "Przegląd i testy"
        }
      ],
      "gate": {
        "question": "Czy zatwierdzasz raport audytu etapu1 jako podstawę dalszych decyzji?",
        "options": {
          "A": "Zatwierdź raport i przejdź do wyboru dalszych kroków (rekomendowane). Nie zatwierdza finalnej polityki filtrów.",
          "B": "Pogłęb wskazane punkty audytu przed przejściem dalej."
        },
        "answer": "A",
        "status": "resolved",
        "user_response": "idzmy dalej",
        "answered_at": "2026-10-04T08:29:35Z"
      }
    },
    {
      "id": "phase_2",
      "name": "Decyzja o dalszych fazach",
      "icon_hint": "analysis",
      "status": "in_progress",
      "started": "2026-10-04T08:29:35Z",
      "completed": null,
      "skip_reason": null,
      "summary": "Przygotowano niezależną ocenę porównania wariantów i projektu wysokiego poziomu. Obie fazy rekomendowane, żadna jeszcze niewłączona.",
      "decisions": [],
      "risks": [
        "Otwarte decyzje dotyczące kwalifikowania i konstrukcji z segmentów",
        "NKJP nadal BLOCKED do konstrukcji"
      ],
      "artifacts": [
        {
          "path": "planning/next-phases.md",
          "label": "Zakres dalszych faz"
        }
      ],
      "gate": {
        "status": "pending",
        "question": "Czy włączyć każdą z opcjonalnych faz? Decyzje niezależne.",
        "questions": [
          {
            "id": "brainstorming_enabled",
            "question": "Czy włączyć porównanie wariantów i ich późniejszy wybór?",
            "options": [
              "Tak (rekomendowane)",
              "Nie — pozostaw decyzje do następnego zadania"
            ],
            "answer": null
          },
          {
            "id": "design_enabled",
            "question": "Czy włączyć projekt wysokiego poziomu pierwszego generatora?",
            "options": [
              "Tak (rekomendowane)",
              "Nie — przekaż wyniki bez pełnego projektu"
            ],
            "answer": null
          }
        ],
        "answer": null
      }
    },
    {
      "id": "phase_3",
      "name": "Alternatywy (opcjonalnie)",
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
      "id": "phase_4",
      "name": "Wybór rozwiązania (opcjonalnie)",
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
      "id": "phase_5",
      "name": "Projekt (opcjonalnie)",
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
      "id": "phase_6",
      "name": "Przekazanie wyników",
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
    "status": "passed_with_documented_research_gaps",
    "issues": [
      {
        "severity": "warning",
        "description": "orth_lc/Róża błędnie oznaczone jako brak listy",
        "fixed": true
      },
      {
        "severity": "warning",
        "description": "Niepełna lista miar CorpusEvidence w projekcie",
        "fixed": true
      }
    ],
    "fixes": [
      "UNMATCHED z powodem case-collapsed list; ponowny pilotaż",
      "DP_norm/total_freq/Dice/raw_record/derived_rank w modelu"
    ],
    "reverify_count": 1
  }
};
