# Podsumowanie: źródła nowych słów (#16)

## TL;DR
- Rzetelne rejestry nowych słów (OJ UW, WSJP PAN) nie mają licencji na dane, więc służą tylko jako dowód ręczny. Źródłem leksemów zostaje SGJP i nasz suplement.
- Nowe słowa wykrywamy w korpusach z czystą licencją: PPC (do X 2026), ParlaMint-PL, Leipzig news, oraz w parze NKJP→KWJP dla lat 2011–2020. Łącznie ok. 875 kandydatów spoza SGJP z korpusów po 2019 i 374 z pary NKJP→KWJP, z czego ok. 300 słów wartych gry.
- Proces: przegląd co kwartał, poza buildem, karta kandydata i decyzja użytkownika o każdym słowie, wejście przez suplement v2.
- „Wulwa”: w żadnym czystym źródle; odłożona do osobnego badania o języku potocznym i świadomych zmianach językowych.

## Kluczowe decyzje (użytkownik, 2026-11-03)
- D1-A: słowa spoza SGJP przez suplement v2, słowo po słowie (próba: antyszczepionkowiec).
- D2-A: SGJP 20261018 osobno (+muralista, muralistka).
- D3-A: ADR — NKJP 1grams także do miary wzrostu, poza buildem.
- D4-A: PPC, ParlaMint, Leipzig tylko poza buildem; PPC do źródeł projektu.
- P1-B: przegląd kwartalny z odświeżeniem PPC; pierwsza paczka (~300) w częściach.
- D5: wulwa — osobne badanie.
- Uwagi: przymiotniki od nazw miejsc dopuszczalne (RJP 2026 s. 51); leki i terminy fachowe tylko, gdy weszły do języka potocznego; kandydaci tylko z PPC bez wymogu drugiego korpusu, w 3 warstwach (projekt, ADR-017).

## Otwarte pytania i ryzyka
- Trafności to oceny agenta bez konkordancji; pierwsze paczki je zweryfikują.
- Filtr leków i angielskich ciągów jest flagą do strojenia.
- Słowa potoczne i internetowe (wulwa, ghosting, cringe, boomer) są poza zasięgiem tych korpusów.

## Artefakty
- Raport: `outputs/research-report.md`; alternatywy: `outputs/solution-exploration.md`; pomiar zysku: `analysis/findings/korpusy-04-zysk.md`; projekt: `outputs/high-level-design.md`; decyzje: `outputs/decision-log.md` (ADR-014–018, szkice).

## Następne kroki
1. Zadanie developerskie: wdrożenie wg projektu (ADR-014–018, suplement v2, manifest wykrywania, wiki). Najpierw D2 (SGJP 20261018) osobno.
2. Nowe badanie: źródła języka potocznego i świadomych zmian językowych (przypadek wulwy).
