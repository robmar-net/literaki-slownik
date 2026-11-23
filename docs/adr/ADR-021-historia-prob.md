# ADR-021: historia prób w manifeście, pod pieczęcią, poza K8

**Status:** zaakceptowana 2026-11-23 (decyzja agenta). Zadanie #22.

## TL;DR
Manifest przebiegu ma na poziomie głównym `build_attempts` i `resume`. Pola są w rdzeniu pieczęci `verify`,
ale nie wchodzą do `logical_content` ani `canonical-index`, więc K8 ich nie porównuje. `verify` i `export`
pokazują skrót `build_history`. Test „wznowiony = świeży” dowodzi, że wznowienie nie zmienia wyniku.

## Kontekst
Zniknięcie T7 przerywa A i B naraz, w tym samym etapie. Para nie złapie błędu wznowienia wspólnego dla obu
stron. Wcześniej wznowienie było widać tylko w work-logu. `manifest_core_sha256` obejmuje cały manifest poza
`readiness`, `verification` i `export`.

## Decyzje
- `build_attempts`: lista `{attempt, started, ended, first_stage, last_stage, outcome, exit_code}`,
  `outcome` ∈ `complete`, `incomplete`, `interrupted`, `failed`. `resume`: `{resumed, count}`.
  Bez komunikatów błędów i ścieżek. Historia nie leży w `stages`.
- `SEAL_EXCLUDED` bez zmian: zmiana historii po `verify` blokuje `export` (5).
- `explain` zwraca z `stages` tylko statusy, więc K7 nie zależy od historii ani od czasów.
- `verify` (JSON i tekst) i `release-manifest.json` (`source_run.build_history`) mają skrót: `resumed`,
  `resume_count`, `attempts`, `stages`, `outcomes`, `exit_codes`, `resumed_from`.
- Raporty kanoniczne nie mają już `new_candidates`, `new_analyses`, `new_decisions`.
- Test przerywa build na każdej granicy etapu, w środku `import_kwjp`, `constructions` i `links` oraz między
  raportami (błąd I/O i `os._exit`), wznawia i porównuje z świeżym: `logical_content_report`,
  `canonical-index`, `lists/*.txt`. Para wznowiony + świeży przechodzi `verify`.

Odchylenie od lokalnego brzmienia 5B („poza zapieczętowanym rdzeniem”): wyłączenie historii z pieczęci
pozwoliłoby ją zmienić po `verify`. Rdzeń pieczęci nie jest porównywany między A i B, więc para działa.

Odrzucone: sam test bez historii; reguła w `verify` wymagająca świeżego partnera.

## Otwarte pytania / ryzyka
- Mały zestaw testowy nie pokazuje efektów skali.
