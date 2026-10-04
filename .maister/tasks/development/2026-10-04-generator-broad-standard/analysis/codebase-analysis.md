# Analiza repozytorium przed implementacją generatora

## TL;DR

Repozytorium zawiera skrypty audytu i zatwierdzony projekt, bez pakietu generatora.
Parsery i niezmienniki audytu można wykorzystać jako wzorce, lecz ich wyjścia są związane z zamrożonym raportem.
Potrzebny jest nowy modułowy kod z jawnymi ścieżkami i bazą przebiegu; audyt pozostaje odtwarzalny.
Baseline: pięć istniejących testów SGJP przechodzi.

## Key Decisions

- Interpretacja zadania: implementacja zatwierdzonego G1/N1/C1, wraz z zadaniami dowodowymi potrzebnymi do pełnego odbioru.
- Nowe zadanie development korzysta z research jako wejścia; nie wznawia go i nie zmienia jego stanu.
- Badano niezależnie przepływy kodu oraz luki dowodowe. Koordynator zweryfikował wyniki odczytem kodu i artefaktów.

## Open Questions / Risks

- Konserwatywnego przesiewu `audit-policy.json` nie wolno użyć jako finalnej polityki.
- Pozostają luki semantyki etykiet, skrótowców, fleksji, konstrukcji i ortografii; mogą blokować pełne wydanie.
- Brak obecnie testów importerów KWJP, bazy, linkera, CLI, awarii i eksportu.

## Zakres i źródła

Analiza dotyczy repo `literaki-slownik`, nie aplikacji Literaki-server. Badane wejście: [zatwierdzony projekt](../../../research/2026-10-04-audyt-zrodel-polskich-slownikow/outputs/high-level-design.md), [przekazanie](../../../research/2026-10-04-audyt-zrodel-polskich-slownikow/outputs/research-handoff.md), skrypty, konfiguracja, testy i dokumentacja.

| Plik / symbol | Obserwacja |
|---|---|
| `scripts/audit_sgjp.py:22` / records | UTF-8 gzip, koniec nagłówka, pięć pól. Sortuje przez systemowy sort i zapisuje cache względem cwd; nie jest czystym parserem |
| `scripts/audit_sgjp.py:46` / audit | Agregaty w pamięci, pełne ID lematu, NFC/lower, maski jednej interpretacji. Deduplikacja w grupach dopiero w audit |
| `scripts/audit_sgjp.py:94–120` | Rozdzielanie etykiet dla statystyk oraz przesiew wielkich liter/mieszanek to scenariusz audytu, nie finalna semantyka |
| `scripts/audit_kwjp.py:38` / rows | Puste nagłówki zastępuje nazwami zależnymi od nazwy pliku; waliduje przez assert, które znika przy python -O |
| `scripts/audit_kwjp.py:51` / inspect | Zachowuje miary i kontroluje format; wartości float służą statystykom, nie są jedynym źródłowym zapisem |
| `scripts/audit_kwjp.py:136` / main | Przypięty commit, SHA256 i blob Git; globalne CACHE/OUT i pobieranie przez curl |
| `scripts/pilot_links.py:21` / main | Jawny pilot 13 form/12 lematów, kandydaci lemma/POS, bez dzielenia F; nie jest pełnym linkerem |
| `scripts/test_audit_sgjp.py:17` / AuditSgjpTests | Pięć syntetycznych kontroli z izolowanym cwd/cache; dobry wzorzec testów niezmienników |
| `config/audit-policy.json` | Wersjonowany scenariusz przesiewu, jawnie nieprodukcyjny |
| `.gitignore` | Cache, dane robocze, środowiska i pliki tymczasowe ignorowane; proces Maister wersjonowany |

## Obecny przepływ

```text
audyt SGJP: gzip -> kontrola formatu -> sort -> statystyki/maski -> JSON raportu
audyt KWJP: cache/pobranie -> kontrola hashy -> CSV -> statystyki -> JSON/rejestr
pilot: wybrane rekordy SGJP + listy KWJP -> kandydaci/statusy -> JSON ilustracyjny
```

Wyjścia KWJP i pilota są na stałe skierowane do poprzedniego zadania research. Ponowne użycie main z nowego generatora mogłoby nadpisać zamrożone artefakty. Nie stwierdzono istniejącej warstwy SQLite, mechanizmu decyzji źródłowych, rekonstrukcji produkcyjnych ani zamrażania kandydatów.

## Wzorce i zależności

Można adaptować jawne UTF-8/gzip/CSV, kontrolę hashy, zachowanie surowych rekordów, pełnego ID homonimu, niezmiennik jednej interpretacji i brak imputacji zera. Walidacja generatora musi używać jawnych wyjątków i typu źródła, zamiast zależeć od nazwy pliku lub assert. Dane korpusowe pozostają przy własnej jednostce; kandydat dopasowania nie dowodzi tożsamości znaczenia.

Skrypty używają biblioteki standardowej Pythona, audyt dodatkowo systemowego sort i curl. Dokumentacja określa Python 3.11+. Brak pyproject, zewnętrznych zależności, CI i standardów w `.maister/docs/standards/` potwierdzony inwentaryzacją. Obowiązują reguły AGENTS.md i zatwierdzona specyfikacja. Brak agentów specjalistycznych `.codex/agents/` potwierdzony odczytem; wymagane fazy prowadzi koordynator.

## Testy i dostęp do danych

Baseline `python3 -m unittest discover -s scripts -p 'test_audit_sgjp.py'`: 5/5 OK. Kontrole obejmują spójność całej polityki jednej interpretacji, homonim nazwy/pospolitego słowa, em, łącznik i deduplikację. Nie uruchamiano ponownie skryptów zapisujących wyniki audytu.

Wejścia SGJP i KWJP są w lokalnym cache. Rejestry i manifesty wskazują ich dokładne wersje i sumy; generator musi sprawdzać je przed użyciem. Artefakty research i hashe zamrożonych skryptów/wyników zweryfikowano przed rozpoczęciem.

## Następne kroki i wynik

Uszczegółowić kontrakty nowych wejść/wyjść, reguł i macierzy odbioru w specyfikacji, z osobnymi zadaniami dowodowymi. Zachować oryginalne skrypty i ich manifest; kod generatora tworzyć z jawnymi parametrami, bez pobierania danych podczas importu modułu. Szczegółowy plan wymaga następnych faz i bramek development.

```text
status: completed
summary: istnieją wzorce audytu, brak generatora; wskazano punkty adaptacji i luki
files_found: 7 skryptów Python, konfiguracja, AGENTS, docs i artefakty research
complexity: high
risk_level: high — integralność danych i kwalifikowanie słowników
```
