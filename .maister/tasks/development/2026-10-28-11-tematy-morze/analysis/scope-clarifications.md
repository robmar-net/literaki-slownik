# Decyzje zakresu (faza 2)

## TL;DR
Operator rozstrzygnął 6 spraw 2026-10-28. Przegląd R2 obejmuje 90 słów (30 na warstwę). Progi bramki są takie jak w projekcie. T3 zostaje z 4821, żeglugę śródlądową mierzymy. Dodatków ręcznych nie ma. T2 ma 6 korzeni. Listę 37 słów przypinamy bez zmian.

## Kluczowe decyzje
- **R2: 30 słów na warstwę, razem 90.** Jest to więcej niż „30 słów” w D3. Operator wybrał to świadomie, a progi zostają jak w projekcie.
- **Progi bramki jak w projekcie:**
  - test 37 słów: co najmniej 70% w liście;
  - T1: co najmniej 27/30;
  - T2: co najmniej 20/30, najwyżej 3 błędne;
  - T3: co najmniej 20/30;
  - zgodność z agentem: co najmniej 80%.

  Werdykt brzmi „dalej”, „popraw” albo „stop”. Ostateczną decyzję i tak podejmuje operator.
- **IATE 4821 zostaje.** Raport podaje udział terminów śródlądowych i ich przykłady, a LIMITATIONS to opisuje. Wykluczenia trafią do konfiguracji tematu dopiero po przeglądzie.
- **v1 bez dodatków ręcznych.** Słowa „sztorm” nie dodajemy ręcznie.
- **Korzenie T2:** 7354, 2149, 4511, 6214, 14136 („żegluga 1”) i 14515 („żeglarstwo 1”). Bez wykluczeń poddrzew w v1.
- **Lista 37 słów** trafia do repo bez zmian i nie poprawiamy jej po wynikach:
  kotwica, kil, maszt, żagiel, ster, bosman, rufa, burta, pokład, statek, okręt, marynarz, jacht, sztorm, kambuz, bandera, reja, bom, fok, szalupa, kuter, rybak, mesa, kabestan, sternik, cumować, halsować, falochron, nabrzeże, kuk, bakburta, sterburta, grot, achtersztag, knaga, szkuta, trał.

## Otwarte pytania / ryzyka
- Przegląd 90 słów to większy nakład pracy dla operatora.
- `quality._config` przyjmuje dziś próbę 30 na warstwę. To pasuje do R2. Próba agenta (50 na warstwę) potrzebuje osobnej ścieżki.
