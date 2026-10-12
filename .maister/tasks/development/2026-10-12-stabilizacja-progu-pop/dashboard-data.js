window.MAISTER_DATA = {
  "generated": "2026-10-12T12:55:27Z",
  "task": {
    "title": "Tymczasowa stabilizacja składu POP (#6)",
    "type": "development",
    "status": "awaiting_scope_decision",
    "description": "Zastąpić limit 60 tys. stałym progiem punktacji dzisiejszego cięcia i zgodnie zmienić przycinanie członków, zachowując POP0. Docelowa granica POP pozostaje otwarta. Zakres pilnych dodatków STANDARD z #4 czeka na odpowiedź właściciela.",
    "path": ".maister/tasks/development/2026-10-12-stabilizacja-progu-pop",
    "current_activity": "Oczekiwanie na decyzję zakresu #4"
  },
  "characteristics": {
    "has_reproducible_defect": false,
    "modifies_existing": true,
    "new_capability": false,
    "data_operations": true,
    "ui_heavy": false,
    "risk_level": "high"
  },
  "phases": [
    {
      "id": "phase-1",
      "name": "Analiza kodu",
      "icon_hint": "analysis",
      "status": "completed",
      "started": "2026-10-12T12:54:52Z",
      "completed": "2026-10-12T12:54:52Z",
      "skip_reason": null,
      "summary": "Wybór jednostek i przycinanie członków to dwa odrębne kroki; D6 i raport są dziś liczbowe; POP0 może zachować własną ścieżkę.",
      "decisions": [
        "Nie zmieniać źródeł ani miary; sprawdzić pełne zbiory i podzbiory przed wydaniem."
      ],
      "risks": [
        "Zaokrąglenie progu; walidacja mieszanej konfiguracji; diagnostyka explain i wiki."
      ],
      "artifacts": [
        {
          "path": "analysis/codebase-analysis.md",
          "label": "Analiza kodu"
        }
      ],
      "gate": null
    },
    {
      "id": "phase-2",
      "name": "Zakres i luki",
      "icon_hint": "analysis",
      "status": "awaiting_approval",
      "started": "2026-10-12T12:54:52Z",
      "completed": null,
      "skip_reason": null,
      "summary": "Stały próg i przycinanie własną punktacją dla POP; POP0 bez zmian. Zakres dodatków STANDARD wymaga decyzji.",
      "decisions": [
        "Docelowa kalibracja i wydanie poza bieżącym krokiem."
      ],
      "risks": [
        "Wynik +2372/0 dotyczy tylko konkretnej symulacji; nie stanowi ogólnej gwarancji."
      ],
      "artifacts": [
        {
          "path": "analysis/gap-analysis.md",
          "label": "Luki i zakres"
        }
      ],
      "gate": {
        "question": "Czy pilne poprawki obejmują teraz także 2382 dodatki do STANDARD z #4, a osiem osobnych cofnięć zostawiamy poza tym krokiem?",
        "choices": [
          "Stabilizacja POP i 2382 dodatki STANDARD; cofnięcia później",
          "Teraz tylko stabilizacja POP",
          "Włączyć także osiem cofnięć po omówieniu"
        ],
        "answer": null
      }
    },
    {
      "id": "phase-3",
      "name": "TDD red",
      "icon_hint": "build",
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
      "id": "phase-4",
      "name": "Makiety",
      "icon_hint": "build",
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
      "id": "phase-5",
      "name": "Wymagania i specyfikacja",
      "icon_hint": "build",
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
      "id": "phase-6",
      "name": "Audyt specyfikacji",
      "icon_hint": "build",
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
      "id": "phase-7",
      "name": "Plan implementacji",
      "icon_hint": "build",
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
      "id": "phase-8",
      "name": "Implementacja",
      "icon_hint": "build",
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
      "id": "phase-9",
      "name": "TDD green",
      "icon_hint": "build",
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
      "id": "phase-10",
      "name": "Wybór kontroli",
      "icon_hint": "build",
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
      "id": "phase-11",
      "name": "Weryfikacja",
      "icon_hint": "build",
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
      "id": "phase-12",
      "name": "E2E",
      "icon_hint": "build",
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
      "id": "phase-13",
      "name": "Dokumentacja użytkownika",
      "icon_hint": "build",
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
      "id": "phase-14",
      "name": "Finalizacja",
      "icon_hint": "build",
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
