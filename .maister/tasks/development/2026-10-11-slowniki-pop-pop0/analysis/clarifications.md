# Doprecyzowania (faza 1)

## TL;DR
Właściciel, 2026-10-11: POP to leksemy z typowymi formami, rozmiar wg pokrycia tekstów, tylko korpusy (lukę potoczną mierzymy), jedno zadanie od pomiaru do wydania.

## Key Decisions
- Jednostka: leksem z typowymi formami — które formy są typowe, ustalamy pomiarem.
- Rozmiar POP: wg pokrycia tekstów (np. 98–99% wystąpień); pomiar pokaże liczbę leksemów.
- Słowa potoczne: bez ręcznych dodatków; mierzymy, ile wypada, decyzja potem.
- Zakres: pomiar → decyzje właściciela → implementacja, odbiór i wydanie w tym zadaniu.

## Open Questions / Risks
- Rozmiar POP0 („rząd wielkości mniejszy”) — do pomiaru.
- Reguła czyszczenia NKJP (audyt: nie usuwać interpunkcji; ADR-006/ATTRIBUTIONS: usuwamy) — do rozstrzygnięcia w specyfikacji.
