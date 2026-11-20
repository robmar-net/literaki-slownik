# Runbook: zgłoszenia słów od graczy

## TL;DR
Gracze zgłaszają słowa z karty słowa w grze: brakujące, niedopuszczalne, złe objaśnienie, inne. Serwer zbiera je w tabeli `dictionary_reports` ([runbook serwera](https://github.com/robmar-net/Literaki-server/blob/main/docs/standards/operations/deployment/1960-dictionary-reports.md), repo prywatne). Sesja: pobrać nowe zgłoszenia, ustalić przyczynę każdego, poszukać luki systemowej, wpisać wynik na wiki [Zgłoszone braki](https://github.com/robmar-net/literaki-slownik/wiki/Zgloszone-braki). Proces analizy: [#18](https://github.com/robmar-net/literaki-slownik/issues/18).

**Zgłoszenie nie dopisuje słowa.** Zmiana listy to decyzja użytkownika, potem build i wydanie (`AGENTS.md`).

## Key Decisions
- **Źródło: dzienna kopia bazy** `~/Literaki-backups/literaki-<UTC>.db` (najwyżej dobę stara). Nie CSV z `/ops`: ten wymaga `OPS_SECRET`, a sekretów nie czytamy.
- **Prywatność.** Uwagi gracza i login czytamy tylko lokalnie. Na wiki, w tickecie i w commicie: słowo, rodzaj, słownik, dzień, liczba zgłoszeń, przyczyna, stan. Nigdy uwagi, nigdy login, nigdy `account_id`.
- **Surowe dane tylko w `tmp/`** (w `.gitignore`). Po sesji kasujemy pliki z uwagami.
- **Przyczyna z artefaktu**, nie z pamięci: lista przebiegu i `explain`.
- Zgłoszenia testowe (np. „smoke test”) pomijamy.

## Słowniki gry → przebiegi

| `lexicon_ids` | wydanie | przebieg w `data/work/` |
|---|---|---|
| `pl-standard-20261109` | LL-PL v31 (SGJP 20261018) | `lists-v32-20261104-161601-a` |
| `pl-standard-20261014` | starsze; sprawdzamy na bieżącym v31 | jw. |

Nowe wydanie w grze dopisuje tu wiersz.

## Procedura
1. **Pobierz nowe zgłoszenia.** Datę „Przejrzane do” weź ze strony wiki.
   ```bash
   DB=$(ls -t ~/Literaki-backups/literaki-*.db | head -1)
   OD='2026-11-18 03:21:54'   # "Przejrzane do" z wiki, UTC
   mkdir -p tmp/zgloszenia-$(date +%Y%m%d)
   sqlite3 -readonly -separator ' | ' "$DB" \
     "select datetime(at/1000,'unixepoch'), word, kind, lexicon_ids, notes
        from dictionary_reports where at > strftime('%s','$OD')*1000 order by at;" \
     > tmp/zgloszenia-$(date +%Y%m%d)/zgloszenia.txt
   ```
2. **Sprawdź listy.** `grep -cx <słowo> data/work/<przebieg>/lists/standard.txt` i `broad.txt`.
3. **Ustal przyczynę.** `python3 -m literaki_slownik explain --run-dir data/work/<przebieg> --word <słowo> --variant standard`. Jedno słowo trwa ok. 5 min: puść pętlę w tle (`nohup … & disown`), wynik do `tmp/`. Szukaj reguły z „odrzucone” w każdej analizie. Brak analiz = brak w SGJP.
4. **Oceń zgłoszenie** (uwagi czytaj lokalnie):
   - `missing`: czy słowo jest poprawne; którą regułą odpadło; czy reguła działa tu dobrze;
   - `not_allowed`: skąd słowo jest na liście (lemat, kwalifikatory); czy powinno zostać;
   - stan: „poza listą — słusznie”, „do decyzji”, „luka: #N”.
5. **Szukaj luki systemowej.** Kilka słów z jednego powodu, albo reguła, która odcina pospolite słowo, to luka. Podepnij pod ticket (#4 dawność, #5 nie-, #15 wykrzykniki, #16 nowe słowa, #17 skróty) albo załóż nowy.
6. **Wiki.** Dopisz wiersze do [Zgłoszone braki](https://github.com/robmar-net/literaki-slownik/wiki/Zgloszone-braki): to samo słowo = jeden wiersz, rośnie licznik. Ustaw „Przejrzane do” na czas ostatniego zgłoszenia. Wiersz w `Historia-zmian`. Commit i push wiki ([runbook wiki](runbook-wiki.md), krok 5).
7. **Ticket.** Krótki komentarz w #18: data, liczba zgłoszeń, wnioski, nowe tickety.
8. **Decyzje.** Propozycje dopisania lub usunięcia słów przedstaw użytkownikowi z przykładami i wpływem. Bez decyzji listy się nie zmieniają.
9. **Sprzątanie.** `rm tmp/zgloszenia-*/zgloszenia.txt`.

## Ryzyka
- Kopia bazy może być sprzed doby: zgłoszenia z ostatnich godzin wejdą do następnej sesji.
- Serwer trzyma zgłoszenie 180 dni. Sesja rzadsza niż co pół roku gubi zgłoszenia.
- `explain` liczy bieżącym kodem; gdy wersja kodu różni się od przebiegu, opieraj się na listach przebiegu.
