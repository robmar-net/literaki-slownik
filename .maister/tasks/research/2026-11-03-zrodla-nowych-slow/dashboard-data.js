window.MAISTER_DATA = {
  generated: "2026-11-03T09:56:12Z",
  task: { title: "Źródła nowych, popularnych słów polszczyzny", type: "research", status: "in_progress", description: "Otwarte źródła neologizmów i metoda ich wychwytywania w literaki-slownik.", path: ".maister/tasks/research/2026-11-03-zrodla-nowych-slow", current_activity: "Faza 3: alternatywy" },
  characteristics: {},
  phases: [
    { id: "phase-1", name: "Podstawa badania", icon_hint: "analysis", status: "completed", started: "2026-11-03T09:37:17Z", completed: "2026-11-03T10:05:00Z", skip_reason: null, summary: "Rzetelne źródła istnieją (OJ UW, WSJP), ale bez licencji danych — tylko dowód ręczny. Wykrywanie 2011–2020 działa (374 kandydatów, ~65% trafnych); po 2020 dowód z ParlaMint/Leipzig. Wulwa: tylko przez suplement v2 decyzją użytkownika.", decisions: ["D1 suplement v2 dla słów spoza SGJP?","D2 SGJP 20261018 (+2 lematy)?","D3 NKJP w metodzie (poza ADR-006)?","D4 korpus po 2020?","Wulwa: dodać / odłożyć / odrzucić"], risks: ["Licencja tekstu FineWeb-2/HPLT nieustalona","Trafność oceniał jeden agent","Ręczna fleksja w suplemencie"], artifacts: [
      {path:"outputs/research-report.md",label:"Raport",html:"outputs/research-report.html"},
      {path:"analysis/synthesis.md",label:"Synteza",html:null},
      {path:"planning/research-brief.md",label:"Brief",html:null},
      {path:"planning/research-plan.md",label:"Plan",html:null},
      {path:"planning/sources.md",label:"Źródła",html:null},
      {path:"analysis/findings/neolog-00-przeglad.md",label:"Neologizmy: przegląd",html:null},
      {path:"analysis/findings/korpusy-01-przeglad.md",label:"Korpusy: przegląd",html:null},
      {path:"analysis/findings/projekt-zasady-zrodel.md",label:"Projekt: zasady",html:null},
      {path:"analysis/findings/projekt-metoda.md",label:"Projekt: metoda",html:null}
    ], gate: null },
    { id: "phase-2", name: "Ocena burzy mózgów", icon_hint: "plan", status: "completed", started: "2026-11-03T10:05:00Z", completed: null, skip_reason: null, summary: null, decisions: [], risks: [], artifacts: [], gate: null },
    { id: "phase-3", name: "Alternatywy", icon_hint: "spec", status: "in_progress", started: null, completed: null, skip_reason: null, summary: null, decisions: [], risks: [], artifacts: [], gate: null },
    { id: "phase-4", name: "Wybór", icon_hint: "plan", status: "pending", started: null, completed: null, skip_reason: null, summary: null, decisions: [], risks: [], artifacts: [], gate: null },
    { id: "phase-5", name: "Projekt", icon_hint: "spec", status: "pending", started: null, completed: null, skip_reason: null, summary: null, decisions: [], risks: [], artifacts: [], gate: null },
    { id: "phase-6", name: "Podsumowanie", icon_hint: "done", status: "pending", started: null, completed: null, skip_reason: null, summary: null, decisions: [], risks: [], artifacts: [], gate: null }
  ],
  verification: null
};
