# Formy niezalecane — decyzja przed aktywacją filtra

## TL;DR
SGJP rozróżnia `niepopr.` (niepoprawne) i `niezal.` (niezalecane).
Eksport 20260823 ma 2 330 rekordów z `niezal.`, 1 970 oryginalnych napisów i 83 pełne identyfikatory leksemów.
Nie jest to liczba słów, które przybędą lub znikną z listy: obowiązują inne filtry i niezależne analizy.
Użytkownik zatwierdził A: samo niezalecanie nie odrzuca w BROAD ani STANDARD. Warunek jest zaimplementowany i widoczny w diagnostycznym explain.

## Key Decisions
- Nie utożsamiamy niezalecania z niepoprawnością. Oznaczenia rozstrzyga [oficjalny wykaz SGJP](https://sgjp.pl/oznaczenia/).
- Dla decyzji używamy własnego przypiętego eksportu SGJP; nie korzystamy z list ani werdyktów SJP.pl.
- Pozostałe zasady gry i profil pozostają niezmienione. Archaiczność, nazwa własna czy skrót są oceniane oddzielnie.

## Open Questions / Risks
- Same liczniki ekspozycji nie stanowią końcowej delty list. Np. `ciesz` i `żeż` mają także inne analizy.
- Aktywacja pełnej tabeli etykiet nadal wymaga domknięcia pozostałych klas.

## Przykłady ze źródła

| Napis | Leksem | Kwalifikator |
|---|---|---|
| kakaa | kakao | niezal. |
| kocy | koc | niezal.,pot. |
| kowboi | kowboj | niezal. |
| przywilei | przywilej | niezal. |
| turniei | turniej | niezal. |

Rozliczenie pól: `niezal.` 1 513, `daw.,niezal.` 461, `niezal.,przest.` 228, `niezal.,rzad.` 127, `niezal.,pot.` 1; razem 2 330. Odczyt readonly z pełnego `sgjp_record`, warunek `instr(qualifiers,'niezal.')>0`. Liczby dotyczą zapisanych pól źródłowych, bez rozbijania przecinków na alternatywne sensy. SHA256 eksportu: `3b2ee079143bc95186370fd528735779c4ba62f4ce14e30cf6622ceb566e9810`.

## Warianty do wyboru

**A — rekomendowany:** `niezal.` samo nie odrzuca w BROAD ani STANDARD. Inne warunki nadal obowiązują; forma historyczna może być wykluczona ze STANDARD, a skrót lub nazwa z gry. Odpowiada to szerokiemu zakresowi współczesnej polszczyzny; użytkownik może spotkać formy niepreferowane przez autorów SGJP.

**B:** `niezal.` samo odrzuca daną interpretację w STANDARD, ale nie w BROAD. STANDARD będzie bardziej restrykcyjny normatywnie, nawet dla części współczesnych wariantów. Zbieżny napis może pozostać dzięki innej poprawnej analizie bez tego kwalifikatora.

W obu wariantach niepoprawność jest oddzielną kategorią. Nie przyjmujemy wnioskowania „niezalecane = niepoprawne”. Decyzja A została zatwierdzona przez użytkownika; implementacja zachowuje pozostałe warunki jako osobne oceny.

## Zatwierdzenie i implementacja

Użytkownik wybrał A. `disrecommended_checks` obsługuje pięć audytowanych dosłownych etykiet zawierających niezalecanie, bez rozbijania przecinków na sensy. Jest to tylko warunek niezalecania: np. historyczność daw.,niezal. nadal wymaga osobnej oceny. Pełny odczyt wszystkich 2 330 rekordów potwierdził widoczność tego warunku; nie nadaje on akceptacji całej analizie.
