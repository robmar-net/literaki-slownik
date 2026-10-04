# Odtwarzanie audytu źródeł

## TL;DR
Raporty, skrypty, konfiguracje i manifesty są w Git.
Duże wejścia i pliki robocze pozostają w ignorowanym `cache/`.
Pierwszy etap wykonuje audyt i pilotaż; nie buduje słowników produkcyjnych.

## Key Decisions
- Uruchamiaj polecenia z katalogu głównego `literaki-slownik`.
- Używaj przypiętych plików i sprawdzaj SHA256 z rejestru przed interpretacją wyników.
- NKJP pozostaje zablokowany dla generatora i pilotażu; jego pomiar techniczny jest odrębnym audytem.

## Open Questions / Risks
- Środowisko pomiaru opisuje manifest; do skryptów potrzebne są Python 3.11+ i systemowy `sort`.
- Sortowanie SGJP używa tymczasowych plików i pamięci; wymagane jest kilka GB wolnego miejsca. Nie zmierzono minimalnego zapotrzebowania RAM.
- Publikacja repozytorium nie zmienia warunków źródeł; zachowuj noty i atrybucje.

## Materiał wejściowy

[Specyfikacja v3](literaki-niezalezne-slowniki-prompt-v3.md) jest kopią pliku użytkownika bez zmian bajtowych. Zakres bieżącego etapu wyznacza rozdział 15.

[Raport audytu](../.maister/tasks/research/2026-10-04-audyt-zrodel-polskich-slownikow/outputs/research-report.md) odsyła do wszystkich rejestrów i wyników.

## SGJP i KWJP

```sh
mkdir -p cache/sgjp
curl -fL https://download.sgjp.pl/morfeusz/20260823/sgjp-20260823.tab.gz -o cache/sgjp/sgjp-20260823.tab.gz
shasum -a 256 cache/sgjp/sgjp-20260823.tab.gz
python3 scripts/audit_sgjp.py cache/sgjp/sgjp-20260823.tab.gz .maister/tasks/research/2026-10-04-audyt-zrodel-polskich-slownikow/analysis/findings/sgjp-stats.json
python3 scripts/audit_kwjp.py --fetch
python3 scripts/pilot_links.py
python3 .maister/tasks/research/2026-10-04-audyt-zrodel-polskich-slownikow/analysis/findings/sgjp-rules-probe.py
python3 -m unittest discover -s scripts -p 'test_audit_sgjp.py'
```

Oczekiwany SHA256 eksportu SGJP: `3b2ee079143bc95186370fd528735779c4ba62f4ce14e30cf6622ceb566e9810`.

KWJP pobierany jest z commitu `26d82bd8b906dfed1cfcf8f903b1650b56daeabf`. Skrypt sprawdza hashe już istniejących plików z rejestrem i przelicza wszystkie 13 list. Bez `--fetch` działa na lokalnym cache. Dokumentacja, reguły programu i licencje mają własne adresy oraz hashe w rejestrach — nie są pobierane przez skrypt pilotażu.

## NKJP: tylko techniczna reprodukcja audytu

Poniższy krok nie nadaje źródłu statusu ALLOWED. Nie łącz danych z SGJP/KWJP ani nie publikuj listy źródłowej, dopóki warunki nie zostaną wyjaśnione zgodnie ze specyfikacją.

```sh
mkdir -p cache/nkjp
curl -fL 'https://zil.ipipan.waw.pl/NKJPNGrams?action=AttachFile&do=get&target=1grams.gz' -o cache/nkjp/1grams.gz
shasum -a 256 cache/nkjp/1grams.gz
python3 scripts/audit_nkjp.py cache/nkjp/1grams.gz .maister/tasks/research/2026-10-04-audyt-zrodel-polskich-slownikow/analysis/findings/nkjp-statistics.json
```

Oczekiwany SHA256: `73af49094621b2f86b594beba783c14aee8c8212f1aff3d61f281ab5d99e3dc9`.

## Co wersjonujemy

- `docs/`: specyfikacja wejściowa i dokumentacja pracy.
- `.maister/config.yml`, `.maister/docs/`, `.maister/tasks/`: konfiguracja, stan, plany, raporty, dowody pomiarów, manifesty i dashboard.
- `scripts/`, `config/`: odtwarzalne obliczenia i jawna polityka scenariusza.
- Wymagane noty źródeł oraz informacja o zmianach w artefaktach pochodnych.

`cache/`, `tmp/`, `data/raw/`, `data/work/`, środowiska wirtualne i pliki narzędziowe są ignorowane. Nie ignorujemy globalnie `.maister/` ani plików JSON/Markdown. Zmiany dotyczące badanego procesu commitujemy w tym repozytorium.
