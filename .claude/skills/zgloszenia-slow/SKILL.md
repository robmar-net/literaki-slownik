---
name: zgloszenia-slow
description: Sesja zgłoszeń słów od graczy Literaków — pobranie nowych zgłoszeń z kopii bazy, przyczyna każdego (explain), luki systemowe, wpis na wiki „Zgłoszone braki” i komentarz w #18.
---

# Sesja zgłoszeń słów

Wykonaj [docs/runbook-zgloszenia.md](../../../docs/runbook-zgloszenia.md) krok po kroku, w tej kolejności.

Twarde zasady:
- Uwag gracza i loginów nigdy nie publikuj: ani na wiki, ani w tickecie, ani w commicie.
- Nie czytaj `OPS_SECRET` ani innych sekretów. Dane bierz z `~/Literaki-backups`.
- Surowe dane tylko w `tmp/`; po sesji je usuń.
- Listy nie zmieniasz. Dopisanie lub usunięcie słowa proponujesz użytkownikowi.
- Pisz po polsku, bardzo zwięźle.

Na koniec podaj użytkownikowi: ile zgłoszeń, przyczyny, luki, propozycje do decyzji, link do strony wiki.
