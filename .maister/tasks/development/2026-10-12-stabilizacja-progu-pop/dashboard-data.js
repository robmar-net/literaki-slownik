window.MAISTER_DATA = {
  "generated": "2026-10-12T13:06:35Z",
  "task": {
    "title": "2382 dodatki STANDARD i tymczasowa stabilizacja POP (#4, #6)",
    "type": "development",
    "status": "awaiting_spec_decision",
    "description": "Trwale dodać dokładnie 2382 zatwierdzone formy do STANDARD, ustabilizować POP stałym progiem dzisiejszego cięcia, zaktualizować wiki. Osiem osobnych cofnięć i docelowa granica POP poza zakresem.",
    "path": ".maister/tasks/development/2026-10-12-stabilizacja-progu-pop",
    "current_activity": "Specyfikacja gotowa do przeglądu"
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
      "status": "completed",
      "started": "2026-10-12T12:54:52Z",
      "completed": "2026-10-12T13:03:39Z",
      "skip_reason": null,
      "summary": "Stały próg i przycinanie własną punktacją dla POP; POP0 bez zmian. Zakres dodatków STANDARD wymaga decyzji.",
      "decisions": [
        "Docelowa kalibracja i wydanie poza bieżącym krokiem.",
        "Zatwierdzono 2382 dodatki STANDARD i aktualizację wiki w tym kroku."
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
      "gate": null
    },
    {
      "id": "phase-3",
      "name": "TDD red",
      "icon_hint": "build",
      "status": "skipped",
      "started": "2026-10-12T13:06:35Z",
      "completed": "2026-10-12T13:06:35Z",
      "skip_reason": "Nie dotyczy; testy przed kodem w planie.",
      "summary": "Pominięto: zmiana metody i danych redakcyjnych, bez pojedynczej reprodukowalnej usterki.",
      "decisions": [],
      "risks": [],
      "artifacts": [],
      "gate": null
    },
    {
      "id": "phase-4",
      "name": "Makiety",
      "icon_hint": "build",
      "status": "skipped",
      "started": "2026-10-12T13:06:35Z",
      "completed": "2026-10-12T13:06:35Z",
      "skip_reason": "Brak zmian UI.",
      "summary": "Pominięto: generator CLI bez nowego interfejsu.",
      "decisions": [],
      "risks": [],
      "artifacts": [],
      "gate": null
    },
    {
      "id": "phase-5",
      "name": "Wymagania i specyfikacja",
      "icon_hint": "build",
      "status": "awaiting_approval",
      "started": "2026-10-12T13:03:39Z",
      "completed": null,
      "skip_reason": null,
      "summary": "Specyfikacja dokładnych wyjątków wieku STANDARD, mieszanego progu POP/POP0, pełnego odbioru i wiki.",
      "decisions": [
        "JSON dokładnych analiz przypięty SHA256; tylko historyczna odmowa ustępuje.",
        "POP score −1,042878629 i własna punktacja członków; POP0 count 20 000."
      ],
      "risks": [
        "Symulowane delty trzeba potwierdzić nowym pełnym buildem.",
        "Docelowa granica popularności pozostaje otwarta."
      ],
      "artifacts": [
        {
          "path": "analysis/requirements.md",
          "label": "Wymagania"
        },
        {
          "path": "implementation/spec.md",
          "label": "Specyfikacja"
        }
      ],
      "gate": {
        "question": "Czy zatwierdzasz tę specyfikację jako podstawę audytu i planu implementacji?",
        "choices": [
          "Zatwierdź specyfikację i przejdź do planu",
          "Wskaż korekty specyfikacji"
        ],
        "answer": null
      }
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
