# Decyzja: wykrzykniki z SGJP bez znaczenia (#15)

## TL;DR
- Użytkownik wybrał 2026-11-06 **wariant 1**: z STANDARD wykluczamy tylko dwie analizy SGJP, `up up interj` i `ou ou interj`. Ubytek wynosi 2 formy.
- Zmianę wdrażamy **przy następnej budowie list**. Do tego czasu listy, generator i wiki zostają bez zmian.

## Kluczowe decyzje
- Wykluczenie obejmuje dokładne analizy (forma, lemat, `interj`), a nie same formy. Nie ma nowej reguły, bo kryterium „obce > interj” trafiłoby też w au, hoc, kaput, pull i salam.
- Pozostałe 60 kandydatów z grupy B zostaje na liście.
- Nie przejmujemy polityki SJP.pl (AGENTS.md). SJP.pl i Wikisłownik były tylko miarą i notą do omówienia.

## Do zrobienia przy następnej budowie
- Dodać listę wykluczeń dokładnych analiz w `config/generator/`, w kształcie podobnym do `standard-age-exceptions.json`, z odsyłaczem do #15 i do tej decyzji.
- Kontrola po budowie: w STANDARD nie ma `up` ani `ou`, a pozostałe wykrzykniki zostają. Liczba form spada o 2 względem poprzedniej budowy, o ile inne zmiany w niej tego nie zaburzą.
- Na stronie wiki z kryteriami dopisać zdanie o wyjątku.

## Otwarte pytania
- Brak.
