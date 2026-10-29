# Raport bramki: TEMATY „morze” (#11)

## TL;DR
- Pakiet `tematy-v1-20261029-a`: 964 leksemy, 10 883 formy. Dwie budowy są identyczne (SHA256SUMS `724f2e81…30a9`). Checker: PASS.
- Operator przyjął wszystkie 87 słów przeglądu R2.
- Werdykt automatyczny to „popraw”. Powodem jest tylko zgodność agenta z operatorem (47/87, kappa 0). Wszystkie progi trafności są spełnione.

## Kluczowe decyzje
- Ocena operatora (2026-10-29): „trudno rozdzielić morze i żeglugę, ja bym wszystkie słowa z listy przyjął”. Zapisano 87 × tak.
- Agent oceniał wąsko (tylko „morze”). Operator ocenia szeroko (morze i żegluga). Stąd brak zgodności.

## Otwarte pytania
- Decyzja bramki: dalej, popraw albo stop (grupa 15).
- Czy dodać 6 brakujących słów ręcznie w v2? W v1 lista dodatków musi być pusta.

## Przecięcia (leksemy)
| warstwa | leksemy | ∩ POP | ∩ POP00 |
|---|---|---|---|
| T1 | 246 | 60 (24,4%) | 4 (1,6%) |
| T2 | 691 | 347 (50,2%) | 99 (14,3%) |
| T3 | 27 | 20 (74,1%) | 7 (25,9%) |
| razem | 964 | 427 (44,3%) | 110 (11,4%) |

Formy: 10 883. W POP jest 3 961 (36,4%), w POP00 1 042 (9,6%). Po warstwach: T1 768/91, T2 3 094/896, T3 179/73.

## Diagnostyka (kandydaci → BROAD → STANDARD)
- Leksemy: T1 254 → 249 → 246; T2 708 → 706 → 691; T3 28 → 27 → 27; razem 990 → 982 → 964.
- Formy: 11 588 → 11 165 → 10 883.
- Przykłady odrzuconych są w `reports/` pakietu.

## Kontrole
- **Pokrycie T2:** 866 lematów po domknięciu (864 po zmianie na małe litery). Audyt podał 874, ale liczył też lematy z łącznikiem i kropką.
- **Żegluga śródlądowa (IATE 4821):** 0 z 74 kandydatów T3 i 0 z 27 wpisów.
- **Test 37 słów:** 31/37, PASS (próg 0,70). Brakuje: sztorm, rybak, cumować, falochron, nabrzeże, trał.

## Przegląd R2
| warstwa | operator: tak / N | agent: tak / N | próg |
|---|---|---|---|
| T1 | 30/30 | 46/50 | ≥ 0,90 |
| T2 | 30/30 | 21/50 (23 nie) | ≥ 2/3; nie ≤ 0,10 |
| T3 | 27/27 | 9/27 (14 nie) | ≥ 2/3 |

Zgodność agenta z operatorem: 47/87, kappa 0, próg 0,80. Ten próg nie jest spełniony.

Agent odrzucał słowa takie jak `bananowiec`, `bungee`, `stojan`, `rozrusznik` (T2) i `agent`, `dyplom`, `klasyfikacja` (T3).

## Werdykt automatyczny
„popraw”. Niespełniony jest tylko próg zgodności. „stop” może wybrać tylko operator.

Plik: `verification/review-check.json`.

## Poprawka v2 (grupa 16, 2026-10-29)
- Temat `morze-v2`: 6 ręcznych dodatków w warstwie D (sztorm, rybak, cumować, falochron, nabrzeże, trał).
- Pakiet `tematy-v2-20261029-a` = `-b` (SHA256SUMS `037ec490…7cec5`), checker PASS. Kod: 2bd0dab, a633136.
- 970 leksemów (T1 246, T2 691, T3 27, D 6), 11 035 form. ∩ POP 432 (44,5%), ∩ POP00 113 (11,6%).
- Test 37 słów: 37/37.
- Próba R2 bez zmian (`sample_sha256` `95179d52…`); oceny agenta i operatora przepięte na v2: `verification/tematy-morze-v2-review.json`, `review-check-v2.json`.
- Werdykt automatyczny nadal „popraw” tylko przez zgodność 47/87. Operator: metoda się sprawdziła; ocena wspólna z tematami #12.
