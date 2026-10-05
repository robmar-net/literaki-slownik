# Dokładne człony nazwiska i wpływ utrwalonych filtrów

## TL;DR
Zatwierdzone A wdrożono dla de:F/frag i ibn/frag. Odrębny rzeczownik de:S zachowany. Nowy raport wpływu obejmuje całą utrwaloną populację analiz; nie jest ukończonym wydaniem.

## Key Decisions
- Runtime v14: dokładny source_id, SHA256 eksportu, wiersz, oryginalny napis, pełny ID lematu, tag, names i qualifiers są strażnikami dokumentacyjnej odmowy. Brak któregokolwiek dowodu nie uruchamia tej reguły.
- Klasa członu nazwiska stanowi osobny powód growy. Surowe pola i wpisy źródłowe nie są zmieniane. Reguła nie przechodzi na konstrukcyjną całość, inny snapshot, homonim ani ogólną klasę frag.
- Explain live i zapisane oceny korzystają z tego samego warunku. Poprzednie bazy pozostają historyczne; nowa wersja wymaga nowego build.
- reports/filter-impact.json podaje efekty samodzielne, kolejne i łączne w obu wariantach. Porządek ID jest jawnie leksykograficzny, diagnostyczny. Nie nadaje pierwszeństwa regułom językowym.

## Open Questions / Risks
- Dokumentacyjnie rozpoznano dwie konkretne analizy nazwiska; pozostałe145frag nadal wymagają przeglądu. Nie znaczy to, że każda z nich ma ten sam brak ani że trzeba każdą odrzucić.
- Nazwy mieszkańców obu rodzajów, pełna macierz kategorii/ortografii i konstrukcji oraz odbiór pełnych przebiegów nadal otwarte. G3/G4/G6 częściowe, 8/36 kroków, phase10 approval gate zachowana.
- Publiczne metadane SGJP osiągalne w odczycie; nie aktywowano ich jako wejścia maszynowego ani nie publikujemy kopii glos. Dokumentacyjny dowód bieżących dwóch przypadków jest oparty na wcześniej audytowanym PDF §7.12 s.138.

## Sprawdzenie

168/168 testów generatora i 5/5 audytu. Preflight:14 wejść i10 konfiguracji zgodne z bieżącym manifestem. Test-first dwóch przyrostów zapisany w work-log.

[Runtime trzech przypiętych rekordów](documented-names-runtime.json):16 rozwiniętych analiz i32 oceny, po2 odmowy w obu wariantach; wszystkie14 rozwinięć de:S pozostają unresolved przez niezależne luki. Łącznie klucze:ibn reject,de unresolved. To nie delta finalnej listy. Powtórny zapis0nowych analiz/ocen, logiczna treść identyczna, FK/integrityOK,4zapytania explain live/zapis zgodne.

[Runtime wpływu filtrów](persisted-filter-impact-runtime.json): dwa identyczne raporty z każdej z dwóch baz readonly, fizyczne hashe przed/po takie same. Większa historyczna projekcja:219713 analiz,213636 kluczy; BROAD37809 odmów analiz i36778 kluczy, STANDARD61815 i59417. Nie przeliczono jej politykąv14 i nie dopisano nowych ocen; raport mierzy zapisane powody tej bazy. Bieżąca mała projekcja:2 odmowy analiz i1klucza w obu wariantach.

Raport sprawdza komplet obu wariantów, hash i zgodność statusów powodów oraz dokładny multizbiór powodów membership z warstwami. Poprawny hash z podmienionym ID reguły w samym membership też powoduje odmowę. Unknown nie jest filtrem odrzucającym i nie znika pod znaną odmową. Stan wydaniowy pozostaje INCOMPLETE.
