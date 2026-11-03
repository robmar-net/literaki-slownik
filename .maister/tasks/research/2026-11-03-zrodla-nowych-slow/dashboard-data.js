window.MAISTER_DATA = {
  generated: "2026-11-03T09:56:12Z",
  task: { title: "Źródła nowych, popularnych słów polszczyzny", type: "research", status: "completed", description: "Otwarte źródła neologizmów i metoda ich wychwytywania w literaki-slownik.", path: ".maister/tasks/research/2026-11-03-zrodla-nowych-slow", current_activity: "Zakończone" },
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
      {path:"analysis/findings/korpusy-04-zysk.md",label:"Korpusy: zysk",html:null},
      {path:"outputs/solution-exploration.md",label:"Alternatywy",html:"outputs/solution-exploration.html"},
      {path:"analysis/findings/projekt-zasady-zrodel.md",label:"Projekt: zasady",html:null},
      {path:"analysis/findings/projekt-metoda.md",label:"Projekt: metoda",html:null}
    ], gate: null },
    { id: "phase-2", name: "Ocena burzy mózgów", icon_hint: "plan", status: "completed", started: "2026-11-03T10:05:00Z", completed: null, skip_reason: null, summary: null, decisions: [], risks: [], artifacts: [], gate: null },
    { id: "phase-3", name: "Alternatywy", icon_hint: "spec", status: "completed", started: null, completed: null, skip_reason: null, summary: null, decisions: [], risks: [], artifacts: [], gate: null },
    { id: "phase-4", name: "Wybór", icon_hint: "plan", status: "completed", started: "2026-11-03T10:20:00Z", completed: null, skip_reason: null, summary: "D1 suplement v2; D2 SGJP 20261018; D3 ADR NKJP; D4 PPC+ParlaMint+Leipzig poza buildem; P1 kwartalnie; D5 wulwa do badania języka potocznego.", decisions: ["D1-A","D2-A","D3-A","D4-A","P1-B","D5 odłożone do badania"], risks: [], artifacts: [], gate: null },
    { id: "phase-5", name: "Projekt", icon_hint: "spec", status: "completed", started: "2026-11-03T13:30:00Z", completed: null, skip_reason: null, summary: "Potok kwartalny poza buildem + ręczna brama + istniejący build; suplement v2 w slocie v1 bez zmian kodu; PPC-only w 3 warstwach; ADR-014–018.", decisions: ["v2 zastępuje v1 w tym samym slocie","PPC-only bez wymogu drugiego korpusu: warstwy plenarna/skrócona/odłożona","manifest wykrywania osobny od sources.json"], risks: ["trafności to oceny agenta bez konkordancji","filtr leków jako flaga, do strojenia"], artifacts: [{path:"outputs/high-level-design.md",label:"Projekt",html:"outputs/high-level-design.html"},{path:"outputs/decision-log.md",label:"Decyzje ADR-014–018",html:"outputs/decision-log.html"}], gate: null },
    { id: "phase-6", name: "Podsumowanie", icon_hint: "done", status: "completed", started: "2026-11-03T14:20:00Z", completed: "2026-11-03T14:20:00Z", skip_reason: null, summary: "Badanie zamknięte; dalej: wdrożenie wg projektu i badanie języka potocznego.", decisions: [], risks: [], artifacts: [{path:"outputs/podsumowanie.md",label:"Podsumowanie",html:null}], gate: null }
  ],
  verification: null
};
