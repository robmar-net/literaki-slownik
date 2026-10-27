# Metoda E3: LLM jako oceniający istniejące leksemy (opis i koszt, bez wywołań)

## TL;DR
- LLM ocenia każdy leksem z bazy (np. 0–3 na temat). Nie dodaje słów. Tak każe prompt v3 (w. 418–422).
- Do oceny: 212 728 leksemów SGJP z formą w STANDARD v31; z tego 56 354 lematów jest w KWJP100.
- Szacunek tokenów na temat: ~1,7 mln wejścia i ~1,3 mln wyjścia (całość) albo ~0,45 / ~0,34 mln (tylko lematy z KWJP100). Ceny nie podaję — niezweryfikowane.
- Główne ryzyka: warunki użycia wyniku u dostawcy, brak powtarzalności, wieloznaczność. Odpowiedź: zapisany wynik jako artefakt, ocena próbek przez człowieka.
- Jako jedyna z trzech metod może sięgnąć po słowa podstawowe (`kotwica`, `pług`, `ułamek`), których nie dają etykiety SGJP ani n-gramy.

## Key Decisions
- Nie wywołałem żadnego płatnego API (polecenie zadania).
- Kandydaci = leksemy SGJP, nie formy. Formy dołączamy potem z bazy (prompt v3, w. 412).
- Liczby tokenów to szacunek z założeń niżej, nie pomiar tokenizera.

## Open Questions / Risks
- Ceny modeli: nie sprawdzone w źródle. Trzeba je odczytać z cennika dostawcy w dniu decyzji.
- Warunki dostawcy co do wyników (prawa do wyniku, publikacja na CC BY / BSD-2) — do sprawdzenia przed użyciem; projekt publikuje listy.
- Wybór modelu i dostawcy to nowa zależność — decyzja z właścicielem (AGENTS.md: nowe źródła nie są delegowane).

## Liczby wejściowe (`counts.py`)
Skrypt: `/private/tmp/claude-501/-Users-robmar-Projects-Literaki/7eed58b5-7e1f-4a3f-8359-d9bc24330c2b/scratchpad/metody/counts.py` (strumień `cache/sgjp/sgjp-20260823.tab.gz` × `data/work/release-LL-PL-v30/LL-PL-STANDARD.txt`, 8 s).
- Formy STANDARD v31: 3 092 240.
- Leksemy SGJP z ≥1 formą w STANDARD: 212 728 (lematów bazowych 209 733).
- Z nich w liście lematów KWJP100 (próg 5): 56 354.
- Części mowy (pierwszy tag): rzeczownik 103 355, przymiotnik 57 703, przysłówek 23 438.

## Metoda
1. Wsad: 200 leksemów na zapytanie, każdy z lematem, częścią mowy i numerem homonimu SGJP.
2. Polecenie: „oceń 0–3, czy słowo należy do tematu X; 0 jeśli nie; zwróć tylko id i ocenę”. Opis tematu + 5 przykładów z rdzenia SGJP i 5 przeciw.
3. Temperatura 0; trzy przebiegi albo trzy modele; zgodność = niepewność.
4. Wynik zapisany jako plik (model, wersja, data, prompt, konfiguracja, surowe odpowiedzi, ocena). Dalej używamy tylko zapisanego pliku (prompt v3, w. 420).
5. Kontrola: rdzeń SGJP jako pozytywy (odzysk powinien być wysoki), losowe leksemy jako tło, lista oczywistych słów z rundy 1, próbka 50–100 na temat oceniona przez człowieka.
6. Tańszy wariant: najpierw jeden przebieg „wszystkie tematy naraz”, potem dokładna ocena tylko dla leksemów z oceną > 0.

## Szacunek tokenów
Założenia: lemat po polsku ~3–4 tokeny, z id i separatorem ~5; polecenie ~600 tokenów na wsad 200 (~3 na leksem); odpowiedź ~6 tokenów na leksem i temat; ~25 tokenów na leksem dla 10 tematów naraz. Bez tokenów „myślenia”.

| Zakres | Leksemy | Wejście | Wyjście |
|---|---:|---:|---:|
| 1 temat, całość | 212 728 | ~1,7 mln | ~1,3 mln |
| 1 temat, tylko KWJP100 | 56 354 | ~0,45 mln | ~0,34 mln |
| 10 tematów naraz, całość | 212 728 | ~1,7 mln | ~5,3 mln |
| ×3 przebiegi (niepewność) | — | ×3 | ×3 |

Koszt = tokeny wejścia × cena wejścia + tokeny wyjścia × cena wyjścia. Ceny niezweryfikowane — nie podaję kwot.
Alternatywa bez opłat za tokeny: model o otwartych wagach na Macu. Koszt to czas maszyny; licencję wag trzeba sprawdzić osobno.

## Ryzyka
- **Warunki wyniku.** Wynik modelu staje się częścią publikowanej listy. Trzeba sprawdzić warunki dostawcy lub licencję wag i zapisać je jak warunki źródła.
- **Powtarzalność.** Modele są wycofywane i zmieniane; temperatura 0 nie gwarantuje tego samego wyniku. Ratunek: zapisany wynik jest źródłem prawdy, nie ponowne wywołanie.
- **Wieloznaczność.** LLM oceni lemat po najczęstszym znaczeniu (`pole`, `liczba`, `kot`). Trzeba podać numer homonimu i część mowy; wynik i tak ma niepewność.
- **Stronniczość.** Model może zawyżać słowa popularne i zaniżać rzadkie terminy — dlatego kontrola na rdzeniu SGJP.
- **Granica roli.** LLM nie decyduje o dopuszczalności i nie dostarcza form. Ocenia tylko leksemy z bazy (prompt v3, w. 418).
- **Koszt rośnie z tematami.** 10 tematów × 3 przebiegi to ~15 mln tokenów wyjścia przy pełnej bazie; prefiltr (KWJP100 albo jeden przebieg zbiorczy) tnie to ~4×.
