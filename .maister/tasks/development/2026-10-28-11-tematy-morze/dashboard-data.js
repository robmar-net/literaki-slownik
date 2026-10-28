window.MAISTER_DATA = {
  generated: "2026-10-28T22:37:25Z",
  task: {title: "TEMATY: pilotaż słownika „morze” (#11)", type: "development", status: "in_progress",
    description: "Pilotaż TEMATY morze: warstwy T1/T2/T3, raport przecięć, bramka R2.", path: ".maister/tasks/development/2026-10-28-11-tematy-morze",
    current_activity: "Gathering requirements & creating specification"},
  characteristics: {has_reproducible_defect:false,modifies_existing_code:true,creates_new_entities:true,involves_data_operations:true,ui_heavy:false},
  phases: [
    {id:"phase-1",name:"Analiza kodu i doprecyzowanie",icon_hint:"analysis",status:"completed",started:"2026-10-28T22:06:28Z",completed:"2026-10-28T22:12:26Z",skip_reason:null,summary:"Wzór POP00. Słowosieć 4.5 już na dysku; IATE do pobrania. T1 to nowy skan etykiet mors./żegl./ryb.",decisions:[],risks:["Błąd f33fe05: confirm_unchanged ma hashować też pliki w pakietach wejściowych.","IATE: URL i licencja do potwierdzenia przy pobraniu."],artifacts:[{path:"analysis/codebase-analysis.md",label:"Analiza kodu",html:null},{path:"analysis/clarifications.md",label:"Doprecyzowania",html:null}],gate:null},
    {id:"phase-2",name:"Analiza luk",icon_hint:"analysis",status:"completed",started:"2026-10-28T22:12:26Z",completed:"2026-10-28T22:37:25Z",skip_reason:null,summary:"Nic z TEMATY nie istnieje; zmiana addytywna wg POP00. Do decyzji: rozmiar R2, progi bramki, żegluga śródlądowa w T3.",decisions:[],risks:["plwn45.sqlite zawiera nazwiska redaktorów (kolumny owner)","Lista 37 słów testu bramki istnieje tylko w scratchpadzie starej sesji","POP00 ma stan BUILT, nie wydany; nowa budowa zmieni liczby przecięć"],artifacts:[{path:"analysis/gap-analysis.md",label:"Analiza luk",html:null},{path:"analysis/scope-clarifications.md",label:"Decyzje zakresu",html:null}],gate:{question:"Przejść do fazy 5?",answer:"Tak. R2 90 słów; progi jak w projekcie; IATE 4821 zostaje; bez dodatków; 6 korzeni T2; lista 37 przypięta"}},
    {id:"phase-5",name:"Specyfikacja",icon_hint:"spec",status:"in_progress",started:"2026-10-28T22:37:25Z",completed:null,skip_reason:null,summary:null,decisions:[],risks:[],artifacts:[],gate:null},
    {id:"phase-6",name:"Audyt specyfikacji",icon_hint:"verify",status:"pending",started:null,completed:null,skip_reason:null,summary:null,decisions:[],risks:[],artifacts:[],gate:null},
    {id:"phase-7",name:"Plan",icon_hint:"plan",status:"pending",started:null,completed:null,skip_reason:null,summary:null,decisions:[],risks:[],artifacts:[],gate:null},
    {id:"phase-8",name:"Implementacja",icon_hint:"code",status:"pending",started:null,completed:null,skip_reason:null,summary:null,decisions:[],risks:[],artifacts:[],gate:null},
    {id:"phase-10",name:"Opcje weryfikacji",icon_hint:"verify",status:"pending",started:null,completed:null,skip_reason:null,summary:null,decisions:[],risks:[],artifacts:[],gate:null},
    {id:"phase-11",name:"Weryfikacja",icon_hint:"verify",status:"pending",started:null,completed:null,skip_reason:null,summary:null,decisions:[],risks:[],artifacts:[],gate:null},
    {id:"phase-14",name:"Finalizacja",icon_hint:"done",status:"pending",started:null,completed:null,skip_reason:null,summary:null,decisions:[],risks:[],artifacts:[],gate:null}
  ],
  verification: {status:null,issues:[],fixes:[],reverify_count:0}
};
