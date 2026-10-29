# Instrukcja oceny agenta — #14, R2 (kopia z #13)

Jedna instrukcja dla 9 tematów. Oceniasz jeden temat w jednej sesji.

## Co czytasz

Tylko dwa pliki:

1. tę instrukcję;
2. `.maister/tasks/development/2026-10-29-14-tematy-przed-wydaniem/analysis/do-oceny-<id>.json` swojego tematu.

Nie czytasz innych plików, ocen innych tematów ani kodu. Nie szukasz w sieci.

## Co oceniasz

Każdą pozycję z `items` w pliku `do-oceny-<id>.json` (#14: tylko pozycje nowe w próbie v3; reszta ocen przechodzi z #13). Słowo opisuje
`selected_unit`:

- `lemat`, `formy`, `czesci_mowy`;
- `znaczenie`: skąd słowo trafiło do tematu. `T1` to kwalifikator słownikowy (np. `mikol.`,
  `med.`), `T2` to synset plWordNetu (`<id> <lemat> <nr znaczenia>`); w v2 nie ma T3;
- `wieloznaczny`: czy lemat ma też znaczenia spoza tematu.

Pytanie brzmi: **czy gracz uznałby to słowo za słowo z tego tematu?**

## Oceny

- **„tak”**: słowo jest związane z tematem w szerokim sensie: rzeczy, czynności, ludzie,
  miejsca, cechy, żargon. Wystarczy jedno zwykłe znaczenie związane z tematem.
- **„nie”**: brak rozsądnego związku z tematem w żadnym znaczeniu.
- **„niepewne”**: związek tylko w rzadkim, specjalistycznym albo przenośnym znaczeniu.

Zasady:

- Lemat wspólny z innym tematem zostaje. „Pomidor” jest „tak” w roślinach i w kuchni.
  Nie obniżaj oceny za to, że słowo pasuje też gdzie indziej.
- Wieloznaczność nie obniża oceny, jeśli znaczenie tematyczne jest zwykłe.
- Każda ocena ma powód: jedno krótkie zdanie po polsku, bez cytowania tej instrukcji.
- Oceniasz słowo, nie źródło. Nie zgaduj, co chce usłyszeć budowa.
- Nie wymieniasz żadnej gry słownej poza Literakami i Kurnikiem.

## Granice tematów

Decyzje operatora (`clarifications.md`, `scope-clarifications.md`):

- **grzyby**: grzyby, porosty, pleśnie, grzybobranie. Choroby grzybicze ludzi i zwierząt
  (grzybica) należą do medycyny: tu „nie”.
- **pogoda**: zjawiska atmosferyczne, klimat, pory roku, meteorologia, przyrządy pogodowe.
- **matematyka**: pojęcia, działania, figury, liczby, jednostki rachunkowe, logika formalna.
- **muzyka**: instrumenty, gatunki, teoria, wykonawcy. Taniec (tańce, kroki, choreografia)
  należy do muzyki: „tak”.
- **sport**: dyscypliny, sprzęt, zawodnicy, zawody. Gry, szachy i karty (figury, zagrania,
  terminy) należą do sportu: „tak”.
- **kuchnia**: potrawy, produkty, przyprawy, naczynia, sposoby przyrządzania. Napoje, także
  alkoholowe, należą do kuchni: „tak”.
- **rośliny**: gatunki, części i organy roślin, uprawa, botanika.
- **zwierzęta**: gatunki, grupy, budowa i zachowanie zwierząt, hodowla. Zwierzęta wymarłe
  i dinozaury (`paleont.`) to „tak”. Gwara łowiecka (`łow.`, np. nazwy części ciała
  zwierzyny w języku myśliwych) to „nie”. Człowiek i hominidy to nie zwierzęta w tym
  temacie: „nie”.
- **medycyna**: choroby (też grzybica), objawy, leki, zabiegi, anatomia człowieka, zawody
  medyczne. Organy i części roślin to nie medycyna: „nie”.

## Wynik

Plik `.maister/tasks/development/2026-10-29-14-tematy-przed-wydaniem/analysis/nowe-oceny-<id>.json`,
gdzie `<id>` to: matematyka albo medycyna.
Kodowanie UTF-8, poprawny JSON:

```json
{
  "reviewer": "agent (Claude)",
  "reviewed_at": "2026-10-29T12:00:00Z",
  "oceny": {
    "<key 1 z do-oceny>": {"ocena": "tak", "powod": "jedno krótkie zdanie"},
    "<key 2 z do-oceny>": {"ocena": "nie", "powod": "jedno krótkie zdanie"}
  }
}
```

Wymagania (skrypt zapisu odrzuca plik, który ich nie spełnia):

- dokładnie trzy klucze najwyższego poziomu: `reviewer`, `reviewed_at`, `oceny`;
- `reviewed_at` w UTC, format `RRRR-MM-DDTGG:MM:SSZ`;
- w `oceny` są **wszystkie** wartości `key` z `items` pliku `do-oceny-<id>.json` i **żadnych innych**; klucz
  przepisujesz dokładnie, z dopiskiem `:Sm1` i `@sgjp-…`;
- każda wartość ma dokładnie dwa pola: `ocena` z `"tak"`, `"nie"`, `"niepewne"` oraz
  niepusty `powod`.

Warstwy (`T1`, `T2`) dopisuje skrypt z próby. Ty ich nie podajesz.
