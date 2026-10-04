window.MAISTER_DATA = {
  "generated": "2026-10-04T08:55:44Z",
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
    "current_activity": "Decyzja D3: konstrukcje w głównych słownikach"
  },
  "characteristics": {
    "scope": "Zatwierdzony audyt §15 oraz porównanie i projekt; bez implementacji"
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
      "status": "completed",
      "started": "2026-10-04T08:29:35Z",
      "completed": "2026-10-04T08:38:11Z",
      "skip_reason": null,
      "summary": "Użytkownik włączył niezależnie porównanie wariantów i projekt wysokiego poziomu.",
      "decisions": [
        "brainstorming_enabled=true",
        "design_enabled=true"
      ],
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
        "status": "resolved",
        "question": "Czy włączyć każdą z opcjonalnych faz? Decyzje niezależne.",
        "questions": [
          {
            "id": "brainstorming_enabled",
            "question": "Czy włączyć porównanie wariantów i ich późniejszy wybór?",
            "options": [
              "Tak (rekomendowane)",
              "Nie — pozostaw decyzje do następnego zadania"
            ],
            "answer": "Tak",
            "answered_at": "2026-10-04T08:38:11Z"
          },
          {
            "id": "design_enabled",
            "question": "Czy włączyć projekt wysokiego poziomu pierwszego generatora?",
            "options": [
              "Tak (rekomendowane)",
              "Nie — przekaż wyniki bez pełnego projektu"
            ],
            "answer": "Tak",
            "answered_at": "2026-10-04T08:38:11Z"
          }
        ],
        "answer": "tak i tak",
        "answered_at": "2026-10-04T08:38:11Z"
      }
    },
    {
      "id": "phase_3",
      "name": "Alternatywy (opcjonalnie)",
      "icon_hint": "analysis",
      "status": "completed",
      "started": "2026-10-04T08:38:11Z",
      "completed": "2026-10-04T08:46:48Z",
      "skip_reason": null,
      "summary": "Porównano trzy zakresy pierwszego wyniku oraz niezależne osie konstrukcji, kwalifikatorów, pisowni i harmonogramu NKJP. Dowody pochodzą z zatwierdzonego audytu; rekomendacje pozostają do rozstrzygnięcia.",
      "decisions": [],
      "risks": [
        "Rekomendacje nie są jeszcze decyzjami użytkownika"
      ],
      "artifacts": [
        {
          "path": "outputs/solution-exploration.md",
          "label": "Porównanie wariantów generatora"
        }
      ],
      "gate": {
        "question": null,
        "answer": null
      }
    },
    {
      "id": "phase_4",
      "name": "Wybór rozwiązania (opcjonalnie)",
      "icon_hint": "analysis",
      "status": "in_progress",
      "started": "2026-10-04T08:46:48Z",
      "completed": null,
      "skip_reason": null,
      "summary": "G1 i N1 zatwierdzone. Uzupełniono dowody pisowni i rozdzielono klasy konstrukcji; oczekuje D3 dotycząca ich miejsca w kandydatach.",
      "decisions": [
        "D1=G1: BROAD i STANDARD z pełną dopuszczalną fleksją, wyjaśnieniami i dowodami KWJP; kontrola kompletności przed odbiorem",
        "D2=N1: SGJP/KWJP w pierwszym wyniku; NKJP dołączone później po wyjaśnieniu warunków"
      ],
      "risks": [
        "Pełny wynik wymaga domknięcia dowodów fleksji i istotnych klas",
        "NKJP pozostaje BLOCKED do użycia; pierwszy wynik bez tego źródła zgodnie z N1"
      ],
      "artifacts": [
        {
          "path": "outputs/solution-exploration.md",
          "label": "Porównanie wariantów generatora"
        },
        {
          "path": "analysis/findings/construction-scope.md",
          "label": "Konstrukcje: dowody i zakres D3"
        },
        {
          "path": "analysis/findings/construction-sources.json",
          "label": "Źródła uzupełnienia"
        }
      ],
      "gate": {
        "id": "D3",
        "status": "pending",
        "question": "Czy udokumentowane konstrukcje istniejących leksemów uwzględniamy w głównych kandydatach BROAD/STANDARD?",
        "options": {
          "A": "C1: włączyć po kontroli reguł każdej klasy, np. przezeń i czytajże (rekomendowane).",
          "B": "C2: badać dodatkowe konstrukcje jako osobne rozszerzenie; pełna wymagana fleksja pozostaje w bazie.",
          "C": "C3: odłożyć wybór do pełnej macierzy klas i skutków."
        },
        "answer": null
      }
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
