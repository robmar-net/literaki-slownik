window.MAISTER_DATA = {
  "generated": "2026-10-04T11:08:54Z",
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
    "current_activity": "Zatwierdzenie zakresu implementacji przed specyfikacją"
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
      "status": "in_progress",
      "started": "2026-10-04T11:08:54Z",
      "completed": null,
      "skip_reason": null,
      "summary": "Zakres implementacji obejmuje narzędzie oraz domknięcie zadań dowodowych K1–K10; cel G1/N1/C1 zachowany. Oczekuje bramka zakresu przed specyfikacją.",
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
        "status": "pending",
        "question": "Czy zatwierdzasz zakres implementacji opisany w analizie luk, obejmujący narzędzie i domknięcie dowodów językowych?",
        "options": {
          "A": "Zatwierdź cały zakres i przejdź do specyfikacji oraz planu (rekomendowane).",
          "B": "Wskaż korektę zakresu przed specyfikacją."
        },
        "answer": null
      }
    },
    {
      "id": "phase_3",
      "name": "TDD red",
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
      "name": "Makiety UI",
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
      "name": "Specyfikacja",
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
      "name": "Audyt specyfikacji",
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
      "id": "phase_7",
      "name": "Plan implementacji",
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
      "id": "phase_8",
      "name": "Implementacja",
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
