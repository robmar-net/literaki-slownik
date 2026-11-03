# metoda: nowe pola karty kandydata

## TL;DR
- Karta z #16 zostaje. Dochodzą trzy bloki: **pochodzenie i typ dowodu**, **lejek szumu** (ile trafień zostaje po każdej bramce) i **rodzina pisowni** (oryginał, spolszczenie, warianty niegrywalne).
- Najważniejsze nowe pole to **„nowe formy w grze”**: ile form naprawdę przybędzie po odjęciu form już obecnych w SGJP. Dla `bumer` (m3 jest w SGJP) jest to 1 forma, dla `boomer` 11.
- Z sieci karta pokazuje tylko liczby. Przykłady zdań: z korpusów z #16 albo link z datą odczytu. Co wolno pokazać z sieci: [do uzupełnienia z ccrawl].

## Kluczowe decyzje
- Jedna karta na **rodzinę pisowni**, osobny werdykt dla każdej pisowni. Precedens SGJP: obie pisownie są leksemami (spoiler/spojler, mail/mejl, lunch/lancz, camping/kemping, podcast/podkast, quiz/kwiz, hacker/haker).
- Typ dowodu to pole wyliczeniowe: `korpus` (#16), `potoczne` (ta warstwa), `zmiana_swiadoma`, `reczny`. Kandydat może mieć kilka typów.
- Kwalifikator w suplemencie zostaje pusty (ADR-016). Rejestr decyzji zapisuje typ dowodu i „rejestr: potoczny”, jeśli użytkownik tak oceni. `pot.` i tak nie wyklucza (`usage_checks` w `policy.py`).

## Otwarte pytania i ryzyka
- Czy karta ma pokazywać udział SJP.pl (B8) liczbą, czy tylko „wykluczono”? Proponuję liczbę: to kontrola, że nie przenosimy jego wyboru.
- Karta rośnie. Na jednym ekranie trzeba skrócić blok liczb rocznych do zbiorów, które mają trafienia.

---

## Pola (nowe oznaczone ★)

| Blok | Pole | Przykład (boomer) |
|---|---|---|
| tożsamość | lemat do decyzji, klasa, rodzaj | boomer, subst, m1 (+ depr m2) |
| ★ tożsamość | typ dowodu | `potoczne` |
| ★ rodzina pisowni | warianty i liczby każdego | boomer [..], bumer [..] (m1), BOOMER (wielkie) [..] |
| ★ rodzina pisowni | warianty niegrywalne (myślnik, apostrof, q/v/x) | — (dla cringe: cringe’owy, cringe-owy [..]) |
| ★ homograf | forma już w SGJP jako inny leksem | bumer m3 (10 form) |
| liczby | rocznie w każdym korpusie #16, KWJP F, NKJP | KWJP 5, NKJP 10, PPC 0, Leipzig 20 (2018–2024) |
| ★ liczby | w każdym zbiorze nieformalnym: trafienia, dokumenty, hosty, ipm | [do uzupełnienia z ccrawl/potoczne] |
| ★ lejek | surowe → B3 mała litera → B4 dokument polski → B5 odmiana/kontekst → B6 hosty | [do uzupełnienia z ccrawl/potoczne] |
| ★ odmiana | udział form nie-podstawowych; lista form z liczbami | [..]; boomerzy [..], boomera [..] |
| ★ hosty | liczba, udział największego, udział `sjp.pl` i stron „znaczenie słowa” (B8) | [..] |
| wzrost | g, pierwszy rok ≥ 5 trafień | tylko informacja |
| Słowosieć | tak/nie, **tylko pos 1–4** (polskie LU) | nie (boomer jest tylko jako LU angielska, pos 6) |
| dowód ręczny | OJ UW, WSJP, ★ źródło świadomej zmiany: link + data odczytu | — |
| przykłady | ≤ 2 krótkie, z atrybucją, tylko z dozwolonych źródeł | Leipzig (CC BY 4.0) |
| flagi | `angielski-wygląd`, `marka`, `wariant-pisowni`, `homograf-SGJP`, `wulg.` | `wariant-pisowni`, `homograf-SGJP` |
| fleksja | wzór SGJP i pełna lista form | wzór `hejter` (m1 + depr m2, 12 wierszy, 11 form) |
| ★ wpływ | **nowe formy w grze** (po odjęciu SGJP), osobno STANDARD i BROAD | boomer +11; bumer m1 +1 (`bumerzy`) |
| ★ zmiana świadoma | źródło, redakcja, licencja, opis hasła własnymi słowami, wynik Z2 (a/b/c) | — |

## Uwagi
- Słowosieć: w #16 `boomer`, `cringe` i `lockdown` są w niej tylko jako jednostki angielskie (pos 5–6 w `kontrole.json`). Dopasowanie bez filtra pos dałoby fałszywe „tak”. Zostaje reguła z #16: pos 1–4.
- „Nowe formy w grze” liczy się na zbiorze form po filtrach gry (alfabet, mała litera, długość), a nie na liczbie wierszy wzoru. Wiersze z tą samą formą i różnym tagiem to jedna forma.
