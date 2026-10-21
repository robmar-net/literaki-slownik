# Metoda POP0, dane i historia decyzji

## TL;DR
POP0 wybiera leksemy, po czym bierze ich pełne formy i konstrukcje należące do STANDARD.
Można dodać selekcję form, lecz obecny filtr klas nie obejmuje konstrukcji.
Próg POP0 nie jest skalibrowany na znajomości słów przez ludzi.

## Key Decisions
- Analiza bazuje na kodzie `4f74b42fb4b6d3c256e079f30eebc6cac8d782a9`, zgodnym z odczytanym remote main.
- Nowy POP00 byłby osobnym wariantem; nie odwraca wcześniejszych decyzji dla POP0.

## Open Questions / Risks
- Przynależność napisu do STANDARD nie oznacza akceptacji każdej jego interpretacji.
- Filtr form może całkowicie usunąć niektóre leksemy; trzeba to jawnie rozliczyć.

## Dowody w kodzie
Ścieżki względem korzenia repozytorium:

| Źródło | Ustalenie |
|---|---|
| `config/generator/pop.json:2–28` | pop-v3, pełne formy, konstrukcje, reguła i, średnia log-IPM KWJP/NKJP, próg POP0 0,57370099 |
| `literaki_slownik/pop.py:287–312` | `load_forms` bierze formy STANDARD związane z leksemem; alternatywna reguła ii wymaga akceptacji konkretnej analizy |
| `literaki_slownik/pop.py:315–342` | konstrukcje wiążą się z leksemem składnika |
| `literaki_slownik/pop.py:1172–1253` | klasy voc/impt/participle/person-1-2; alternatywna interpretacja może zachować formę; konstrukcje omijają ten filtr |
| `literaki_slownik/pop.py:1637–1658` | wybór form po wyborze leksemów, kontrola POP0 ⊆ POP ⊆ STANDARD |
| `literaki_slownik/pop.py:1899–1904` | luka mowy potocznej i segmentacja zrobił+em |
| `literaki_slownik/schema.sql:11–43` | surface_form, lexeme, interpretation; konstrukcje mają expanded_tag |
| `tests/test_pop.py:530–554` | testy klas, wieloznaczności i konstrukcji |
| `tests/test_pop_v3.py:278–301` | odtwarzanie list i stałe progi |

Testy przeczytano, nie uruchamiano pełnego suite: badanie nie zmienia generatora.
Odtwarzalność skryptu badawczego jest sprawdzana osobno.

## Wydanie i historia
[Wydanie pop-v3](https://github.com/robmar-net/literaki-slownik/releases/tag/pop-v3),
opublikowane 2026-10-14 00:39:57 UTC, ma 388 763 formy POP0 i 13 896 leksemów.
Lokalny gzip ma hash zgodny z digestem assetu GitHub:
`34be65fa6db34e98c8029a3fba716a23995250fc94fea5b8ab911a8802b22df4`.
Pakiet lokalny `data/work/pop-v3-20261014-022011-a/reports/thresholds.json`
podaje 11 638 jednostek rankingu i 15 893 konstrukcje poza formami podstawowymi.

`docs/adr/ADR-008-pop-v3-staly-prog.md:18–28,45–50` wyjaśnia, że stałe odtwarzają dawne cięcia,
nie granice znajomości. Dług kalibracji pozostaje w [issue #6](https://github.com/robmar-net/literaki-slownik/issues/6).
Starsze README, indeks i runbook mają nieaktualne opisy statusu; bieżący kod i wydanie rozstrzygają ten konflikt.

`docs/adr/ADR-007-metoda-pop-v1.md:20–25,96` dokumentuje wybór pełnej odmiany i pozostawienie
form nijakich pierwszej/drugiej osoby. Historyczny pomiar POP z limitem 40 tys. leksemów
usuwał około 45% form po wyłączeniu czterech klas, tracąc 4,28% masy NKJP.
To **nie wynik dla obecnego POP0**. Źródło:
`.maister/tasks/development/2026-10-11-slowniki-pop-pop0/analysis/pop-measure-report.md:38–53`.

Wcześniejszy research rozcinał progiem częstości zwyczajne paradygmaty, np. desperacja/desperacji.
Źródło: `.maister/tasks/research/2026-10-12-standard-formy-dawne/outputs/research-report.md:55–79`.
Tam chodziło o STANDARD, tu o znajomość: przykład pokazuje mechanizm błędu, nie narzuca polityki POP00.

## Dostępne wejścia
- `reports/units.json`: `units[*].members_in.POP0`, identyfikatory `lemma_id@source_id`.
- `data/work/lists-v31-20261012-162111-a/build.sqlite`: powiązania form, tagi, konstrukcje.
- `cache/kwjp/kwjp100-slowa-orth-{all,fikcja,fakt,publicystyka}.csv.gz`: zapis, freq, ipm, ARF, DP.
- Warianty orth_lc mieszają wielkość liter; użyte tylko jako kontrola czułości.
- NKJP dostępny i dopuszczony zgodnie z ADR-006; nie publikujemy surowych danych ani liczników NKJP.
  W tym pilotażu mierzymy KWJP, a NKJP bierze udział tylko w odziedziczonym wyborze leksemów POP0.

Audyt niezależnego agenta zweryfikowano przez odczyt kodu, testów, ADR i wskazanych historycznych tabel.
