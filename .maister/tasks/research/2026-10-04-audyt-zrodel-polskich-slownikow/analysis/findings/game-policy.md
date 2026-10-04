# Parametry gry użyte w audycie

## TL;DR
Badany profil używa 32 polskich liter, normalizacji NFC i długości 2–15.
Ograniczenia growe są filtrem eksportu, nie powodem usuwania surowych danych SGJP.
Blank nie występuje jako znak w słowie.

## Key Decisions
- Publiczny pakiet płytek potwierdza 32 litery z count>0; q/v/x mają count=0.
- Oryginalna wielkość liter pozostaje w danych; lowercase tworzy osobny klucz dopiero do agregacji.

## Open Questions / Risks
- Parametry dotyczą odczytanej wersji gry, a nie uniwersalnej normy słownikowej.
- Pełna polityka ortograficzna (zwłaszcza nowe przepisy, skrótowce i konstrukcje z partykułami) wymaga oddzielnego doprecyzowania przed wydaniem.

## Dowody
[Publiczny pakiet PL](https://literaki.fly.dev/packs/pl.json), SHA256 w [rejestrze](supplementary-sources.json), potwierdza alfabet aąbcćdeęfghijklłmnńoóprsśtuwyzźż, planszę literaki-15x15, stojak7 i premię50. Identyfikator blanku: oddzielne pole blank=true i pusty napis; nie eksportujemy pustej litery do alfabetu.

Długość co najmniej2, plansza15 oraz zakaz deklarowania blanku jako litery count=0 zostały dodatkowo sprawdzone w dostępnych lokalnie regułach projektu Literaki Lounge: rules/words.go, rules/board.go, rules/validate.go, rewizja b601c4d41eac2f9f5d944b2471fd7f77a6cd6f9b. Repozytorium aplikacji jest prywatne: nie przeniesiono jego kodu, list słów ani dokumentacji do publicznego projektu; publiczny czytelnik nie może sam sprawdzić tych trzech plików. To ograniczenie weryfikowalności źródła reguł. Sam identyfikator planszy potwierdza publicznie rozmiar, nie wszystkie reguły silnika.

Konfiguracja [audit-policy.json](../../../../../../config/audit-policy.json) zapisuje założenia pomiaru. Źródłowe formy ponad15 znaków zachowujemy w bazie surowej. Żadnych myślników, spacji, apostrofów ani kropek nie usuwamy z napisu, żeby uzyskać dopuszczalne słowo.
