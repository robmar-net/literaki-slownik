# Porównanie z SJP.pl: listy v25 (benchmark, nie wejście)

## TL;DR
Porównano zamrożone listy BROAD i STANDARD z buildu `lists-v25-20261008-071320-a` z listą SJP.pl `20260820`, której dziś używa gra. Porównanie zrobiono na prośbę właściciela przed eksportem, żeby wiedzieć, gdzie stoimy. Listy nie zostały zmienione, a dane SJP.pl nie wracają do budowy.

**Stan:**
- BROAD obejmuje **80,9%** słów SJP; STANDARD **77,8%**.
- Ważone frekwencją KWJP, czyli tym, jak często słowa występują w tekstach, BROAD pokrywa **93,0%**, a SJP **95,4%**.
- Prawie cała ta różnica to dwa słowa: **`się` i `siebie` nie istnieją w przypiętym eksporcie SGJP** (2,45% wszystkich wystąpień). Bez tej luki BROAD pokrywałby teksty na poziomie 95,4%, czyli jak SJP.
- 98% słów SJP, których nam brakuje, nie występuje w KWJP ani razu. To głównie rzadkie formy i zapożyczenia spoza SGJP.

**Znalezione błędy i luki, do decyzji przed eksportem:**
1. Brak `się` i `siebie` w źródle.
2. 189 samodzielnych tematów czasu przeszłego w formie `agl` (`mogł`, `niosł`, `dorosł`) przechodzi jako słowa.
3. Skróty zapisane w SGJP także jako rzeczowniki (`nr`, `dr`, `km`, `pkt`, `płk`) przechodzą.
4. Przesiew mieszkańców odrzuca kilka nie-mieszkańców (`sielanka`, `powodzianin`).
5. STANDARD odrzuca częste słowa oznaczone w SGJP jako dawne (`wraz`, `ponoć`, `ilekroć`, `ukradkiem`).

## Wejścia i zakres
- **Listy** (sha256):
  - BROAD `02fbb67b…a106` (3 469 938 słów);
  - STANDARD `42227a74…4b8b` (3 081 120 słów);
  - polityka `approved-conditions-v25`.
- **SJP.pl:** lista growa `20260820` (3 240 471 słów, licencja CC BY 4.0). Odczytano ją bezstratnie z `lexicons/pl-sjp-20260820.dawg` serwera gry (sha256 zrzutu `2a593404…70b8`).
- **Frekwencje:** KWJP `kwjp100-slowa-orth_lc-all`: 345 357 form, 73,2 mln wystąpień.
- **Zakres porównania:** 32 litery profilu, długość 2–15.
  - Poza zakresem jest 777 słów SJP z literami x, v i q (np. `aerobox`, `accusativus`).
  - Nasze listy w całości mieszczą się w zakresie.
- **Narzędzie:** `scripts/benchmark_sjp.py` (tylko odczyt, 1 294 s). Wynik JSON z próbkami słów zostaje lokalnie w `tmp/benchmark/`.

## Wyniki

| | BROAD | STANDARD | SJP |
|---|---:|---:|---:|
| słowa (w zakresie) | 3 469 938 | 3 081 120 | 3 239 694 |
| wspólne z SJP | 2 619 378 | 2 520 345 | — |
| tylko SJP | 620 316 | 719 349 | — |
| tylko u nas | 850 560 | 560 775 | — |
| Jaccard | 0,640 | 0,663 | — |
| pokrycie słów SJP | 80,9% | 77,8% | — |
| nasze słowa potwierdzone przez SJP | 75,5% | 81,8% | — |
| **pokrycie wystąpień KWJP** | **93,0%** | **92,8%** | **95,4%** |

**Frekwencja różnic** (liczba wystąpień w KWJP):

| zbiór | 0 | 1–9 | 10–99 | 100–999 | ≥1000 |
|---|---:|---:|---:|---:|---:|
| tylko SJP (vs BROAD) | 614 976 | 2 703 | 2 343 | 273 | 21 |
| tylko BROAD | 848 548 | 780 | 1 013 | 191 | 28 |
| w SJP i BROAD, nie w STANDARD | 96 436 | 1 055 | 1 386 | 144 | 12 |

**Długości:**
- Wśród krótkich słów, ważnych w grze, różnice są niewielkie:
  - 2 litery: 111 wspólnych, 23 tylko w SJP, 18 tylko u nas;
  - 3 litery: 1 368 wspólnych, 247 tylko w SJP, 176 tylko u nas.
- Od 6 liter BROAD jest większy od SJP, głównie przez formy dawne i rzadkie oraz pełne paradygmaty.

## Dlaczego brakuje słów SJP (620 316 względem BROAD)
- **609 231 (98,2%) nie ma w SGJP ani w naszych konstrukcjach.** To luka źródła, a nie decyzja reguł.
  - 605 325 z nich ma w KWJP frekwencję 0.
  - Najczęstsze z nich: `się` (1,73 mln wystąpień) i `siebie` (58 tys.).
  - Dalej głównie wtrącenia angielskie (`play`, `sorry`, `home`, `free`), wykrzykniki (`hmm`, `bla`), skrótowce (`eko`) i rzadkie zapożyczenia.
- **11 085 odrzuciły nasze reguły:**

| reguła wspólna dla wszystkich analiz | słowa | najczęstsze |
|---|---:|---|
| nazwa własna, wymagana wielka litera | 7 933 | ewa, janusz, kraków, wanda, europa |
| niesamodzielny segment (`adja`) | 1 950 | owocowo, kolejowo, biurowo |
| wymagana wielka litera | 572 | włoch, włochy, sowieci, hiszpanie |
| przesiew mieszkańców `-anin/-anka` | 304 | **sielanka**, **powodzian**, paryżanki, zakopianki |
| złożenie z ruchomą końcówką | 113 | toby, alboby |
| różne reguły w różnych analizach | 112 | al, ibn, warszawianka, krakus |
| forma niepoprawna (SGJP) | 65 | branzlowali |
| skrót (`brev`) | 5 | mm, oo, ko |

Zasady Kurnika wykluczają wielką literę i skróty, więc te odmowy są zgodne z regułami gry. SJP growy przyjmuje część takich słów małą literą jako pospolite, np. `ewa` czy `włoch`. Wyjątek stanowi przesiew mieszkańców: `sielanka` (idylla) i `powodzianin` (ofiara powodzi) to błędy listy wyjątków R1.

## STANDARD względem SJP (99 033 słów w SJP i BROAD, poza STANDARD)
- 95 239 odpada przez `linguistic-historical-form-v1`, czyli kwalifikatory SGJP `daw.` i `przest.`.
- 97% z nich ma w KWJP frekwencję 0.
- Problemem jest około 1,5 tys. słów częstych, które SGJP opisuje jako dawny leksem, choć żyją we współczesnym użyciu:
  - `wraz` (18 095 wystąpień; w SGJP `wraz:D adv daw.`);
  - `ponoć` (`przest.`);
  - `ilekroć`, `powiada`;
  - `ukradkiem` (w SGJP tylko narzędnik `ukradek`, `daw.`);
  - `przekąsem`, `omacku`, `poprzek`, `hospicjum`, `uniwersum`.

## Co mamy, a SJP nie ma (850 560 w BROAD)
- **99,8% ma frekwencję 0.** To pełne paradygmaty SGJP:
  - rzeczowniki 237 tys.;
  - czasowniki: praet 128 tys., cond 110 tys.;
  - przymiotniki i imiesłowy.
- Na formach są kwalifikatory `daw.` (213 tys.), `przest.` (67 tys.), `rzad.` (46 tys.), `indyw.` (18 tys.) i `gwar.` (14 tys.).
- 18 688 słów pochodzi wyłącznie z konstrukcji.
- **Poprawne homonimy pisane małą literą**, których SJP growy nie ma: `warszawa` (samochód), `ford`, `toyota`, `audi`, `paweł`, `niemcy` (`pot.`). Według zasad pisowni nazwy wyrobów pisze się małą literą.
- **Błędy u nas:**
  - **Tematy `agl`:** 189 słów (160 w STANDARD), np. `mogł`, `niosł`, `dorosł`, `miotł`. Analiza `praet:...:agl` to temat dla końcówki (`mogł-em`), który nie występuje samodzielnie. Macierz klas traktuje `praet` jako słowo bez rozróżnienia `agl`/`nagl`.
  - **Skróty jako rzeczowniki:** SGJP ma obok `brev` osobne hasła rzeczownikowe dla `nr`, `dr`, `km`, `pkt`, `płk`, `ppłk`, `abp`, `bp`, `szer`, `woj`, `ul`, `tłum`, `reż`. Nasza reguła skrótów obejmuje tylko klasę `brev`. Wśród lematów zbieżnych z formami `brev` są też zwykłe słowa (`dom`, `gen`, `cal`, `jon`), więc samo zbieżności nie wystarczy. Potrzebna jest zamknięta lista lub kryterium.
  - Skrótowce `sms` i `bmw` SGJP opisuje jako zwykłe rzeczowniki. Według zasad Kurnika skrótowiec to skrót, więc wymaga decyzji.

## Rekomendacje (do decyzji, przed eksportem)
1. **`się`/`siebie`:** dodać je jako udokumentowane uzupełnienie. Są w SGJP online i w RJP, a brakuje ich tylko w eksporcie TSV. Uzupełnienie trzeba oprzeć na niezależnym dowodzie, a nie na liście SJP. To nowa pozycja źródłowa, więc wymaga właściciela.
2. **Tematy `agl`:** w grze odrzucać `praet:*:agl` jako segment niesamodzielny. Formy z końcówką (`mogłem`) pozostają.
3. **Skróty-rzeczowniki:** zamknięta lista haseł SGJP, które są skrótami (brak samogłoski albo hasło bliźniacze do `brev` o tym samym rozwinięciu), odrzucana w grze tak jak `brev`.
4. **R1:** przejrzeć przesiew `-anin/-anka` według frekwencji KWJP i dopisać wyjątki (`sielanka`, `powodzianin`, ewentualnie `zakopianka`).
5. **STANDARD i formy dawne:** nie odrzucać w STANDARD słów z wyraźnym współczesnym użyciem w KWJP, mimo etykiety `daw.`/`przest.`. Próg trzeba zamrozić przed ponownym porównaniem. KWJP jest niezależnym dowodem, a SJP nie jest kryterium.

Zmiany robimy w nowej wersji polityki z testami, potem nowy build i ponowny benchmark tym samym skryptem. Nie kopiujemy brakujących słów z SJP.pl.

## Ograniczenia pomiaru
- Frekwencja KWJP to próbka tekstów, a nie znajomość słów przez graczy.
- Brak w KWJP nie oznacza błędności słowa.
- Nie mierzono jeszcze wpływu na rozgrywkę (stojaki, siódemki, punktacja); to kolejny krok planu C.
