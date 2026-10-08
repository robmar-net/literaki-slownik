# Runda 3: macierz klas, warunki gry i aktywacja polityki (decyzje agenta)

## TL;DR
Właściciel 2026-10-08 przekazał pozostałe decyzje G3/G4 agentowi: „podejmij najrozsądniejsze, w razie czego potem je zmienimy i ponowimy pracę”. Podjęto cztery decyzje:
- zamknięta macierz 34 klas SGJP;
- warunki gry z opublikowanych zasad Literaków;
- zarejestrowany zbiór konstruktorów jako zamknięty zakres pierwszego wydania;
- aktywacja polityki: zastępcze „unresolved” zamieniono na jawne reguły.

Build domyka teraz etapy i zapisuje listy `lists/broad.txt` i `lists/standard.txt`, jeśli nic nie zostaje nierozstrzygnięte. Odbiór wydania nadal robi `verify` (K1–K10) w G8.

Wszystkie decyzje są odwracalne. Każda jest regułą w kodzie lub wpisem w konfiguracji z testem; zmiana oznacza poprawkę i nowy build. Polityka: `approved-conditions-v24`.

## Key Decisions
- **Warunki gry z opublikowanych zasad.** [Zasady Literaków na kurnik.pl](https://www.kurnik.pl/literaki/zasady.phtml) mówią: „Za poprawne uważa się wszystkie słowa występujące w słownikach ortograficznych, języka polskiego, poprawnej polszczyzny bądź wyrazów obcych i ich wszystkie prawidłowe formy gramatyczne (odmiany) z wyjątkiem słów zaczynających się wielką literą, skrótów i słów z łącznikiem lub apostrofem”. Mapowanie na istniejące reguły:
  - wielka litera → `game-required-uppercase-v1`, `game-proper-name-class-v1`, reguły mieszkańców;
  - skróty → `game-abbreviation-v1` (klasa `brev`);
  - łącznik i apostrof → profil liter (tylko 32 litery, bez usuwania znaków);
  - formy odmienione → pełne paradygmaty SGJP i zatwierdzone konstrukcje;
  - niesamodzielne segmenty (`aglt`, `adja`, `pacta`, `numcomp`, `ń`) nie są słowami słownikowymi; samodzielnie występują tylko w konstrukcji albo z łącznikiem → `game-dependent-segment-v1`.

  Polityki redakcyjnej SJP.pl nie przejmujemy (zgodnie ze specyfikacją). Nowa reguła `game-documented-conditions-v1` (accept) zastępuje `game-metadata-not-complete-v1`. Zamyka to pending `documented_game_conditions_without_sjp_editorial_source_policy`.
- **Macierz 34 klas** (`CLASS_MATRIX` w `literaki_slownik/policy.py`):
  - `word`: adj, adjc, adjp, adv, bedzie, comp, cond, conj, depr, fin, frag, ger, imps, impt, inf, interj, num, pact, pant, part, pcon, ppas, ppron12, ppron3, praet, pred, prep, subst, winien — oceniane dalej zwykłymi warunkami;
  - `bound`: adja, pacta, numcomp, aglt — odmowa w grze, mogą być składnikami konstrukcji;
  - `abbreviation`: brev — odmowa.

  Klasa spoza macierzy dostaje w `coverage.json` `UNKNOWN_CLASS` i blokuje odbiór (K4). Ortografia: podstawą jest przypięty SGJP 2026-08 plus udokumentowane odstępstwa normy 2026 (jeśliby/jeżeliby, nazwy mieszkańców). Zamyka to pending `full_category_and_orthography_matrix`. Nowa reguła `linguistic-policy-active-v1` (accept) zastępuje `linguistic-policy-not-active-v1`.
- **Etykieta bez znanego warunku daje unresolved** (`linguistic-unknown-qualifier-v1`). Aktywacja odsłoniła lukę: analiza z nieznaną etykietą przechodziłaby po cichu, bo wcześniej maskowało ją zastępcze unresolved. W przypiętym SGJP dotyczy to tylko `pisane_łącznie_z_przyimkiem` (2 rekordy `ń`, już z niezależną odmową). Nowa etykieta w przyszłym eksporcie zablokuje etap decisions.
- **Konstrukcje.** Zarejestrowane konstruktory (`CONFIRMED_CONSTRUCTOR_RULES`, 9 reguł) to zamknięty zakres pierwszego wydania. Etap constructions kończy się `complete`, a `full_constructions_pending=false`. Nowe klasy konstrukcji to rozszerzenie kolejnego wydania.
- **Build:**
  - etapy constructions, decisions, links i reports kończą się `complete`, jeśli dane na to pozwalają;
  - decisions zostaje `pending`, gdy jakakolwiek analiza ma członkostwo unresolved; wtedy listy nie powstają;
  - flagi `*_pending` w raportach są liczone z danych, a nie wpisane na sztywno;
  - readiness pozostaje INCOMPLETE do `verify`.

## Open Questions / Risks
- **Zakres gry.** Kurnik dopuszcza słowa ze słowników wyrazów obcych. SGJP ich nie obejmuje w całości, więc nasza lista jest węższa. To ograniczenie źródła, a nie reguła.
- **Kwalifikatory.** Formy z kwalifikatorami opisowymi (`pot.`, `wulg.`, `reg.`) są dopuszczone zgodnie z wcześniejszymi decyzjami A. Kurnik nie wyklucza ich osobno.
- **Wyrazy niesamodzielne.** adjp i frag dopuszczono warunkowo (rundy 1–2), co zgadza się z brakiem takiego wyjątku w zasadach Kurnika.
- **Pierwszy prawdziwy wynik da nowy pełny build** (około 8 h), potem przegląd próbek i odbiór G8. Nierozstrzygnięcia pod niezależną odmową (`pisane_łącznie_z_przyimkiem`, mieszane nazwy) trzeba udokumentować w `release.json` (`known_limitations`) przed verify.

## Testy
- `tests/test_agent_decisions_round3.py`: 6 testów, w tym zgodność macierzy z regułami gry i blokada klasy spoza macierzy.
- Około 35 asercji, które zakładały stan sprzed aktywacji, odwrócono. Każdą sprawdzono: wynik accept wynika z braku innych reguł, a nie z przeoczenia.
- Testy nieukończonego przebiegu używają prawdziwego unresolved (nieznana etykieta w fiksturze), a nie podrobionego manifestu.
- Wynik: 265/265 + audit 5/5. Mutacje 6/6 czerwone.
