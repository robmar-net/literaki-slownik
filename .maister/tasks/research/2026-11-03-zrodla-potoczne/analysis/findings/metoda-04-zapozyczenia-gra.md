# metoda: zapożyczenia angielskie i zgodność z regułami gry (pomiar SGJP 20261018)

## TL;DR
- **SGJP przyjmuje obie pisownie, gdy obie są w użyciu.** Pary w eksporcie: spoiler/spojler, mail/mejl/e-mail, lunch/lancz, camping/kemping, podcast/podkast, quiz/kwiz, hacker/haker, manager/menedżer/menadżer, dżinsy/jeansy. Reguła dla nas: **każda pisownia to osobna decyzja z własnym dowodem**. Nie dopisujemy pisowni bez użycia.
- **Wzory odmiany dla kontroli są w SGJP:** `boomer` → wzór `hejter`/`youtuber`/`influencer` (m1 + depr m2, 11 form); `ghosting` → `ranking`/`stalking` (m3, 9 form; wszystkie 187 rzeczowników na `-ing` mają D. `-u` i N. `-iem`); `cringe` → nieodmienny jak `cool`/`trendy`/`okej` (przymiotnik, 1 forma; w SGJP 77 nieodmiennych przymiotników) albo `selfie` (n, 1 forma).
- **Gra odcina sama:** 366 lematów SGJP ma q/v/x, 302 myślnik, 85 ma formy z apostrofem (`deadline’u`). Takie formy odpadają na `profile-pl-alphabet-v1`. Więc `cringe’owy`, `cringe-owy`, `vlog`, `e-mail` nie wejdą, nawet z dowodem. Liczymy je tylko jako dowód leksemu.
- **Homograf:** `bumer` jest w SGJP jako m3 (10 form). Spolszczony `bumer` m1 dodałby do gry 1 formę (`bumerzy`). `boomer` dodałby 11.

## Kluczowe decyzje
- **R1. Pisownia oryginalna i spolszczona to osobne leksemy.** Każda musi sama przejść bramki z `metoda-01`. Karta wspólna, werdykty osobne.
- **R2. Odmiana według wzoru z SGJP z tą samą końcówką i klasą** (ADR-016). Dla zapożyczeń wzór wybieramy z tabeli w § 2. Alternacje z wzoru (`tweet` → `tweecie`, `hejt` → `hejcie`) przechodzą razem z nim.
- **R3. Forma z apostrofem, myślnikiem lub q/v/x nie wchodzi.** Jeśli w użyciu jest tylko taki zapis (np. `cringe’owy`), słowo czeka na zapis grywalny z własnym dowodem (`krindżowy`, `cringeowy`).
- **R4. Nieodmienne zapożyczenia są dopuszczalne** (precedens: cool, trendy, okej, fair, online, selfie). Dla nich bramka B5b (polski kontekst), nie B5a.
- **R5. Przymiotnik od marki tak, rzeczownik-marka nie.** SGJP ma `facebookowy`, `instagramowy`, `tiktokowy` i pospolity `fejsbuk`. Nie ma pospolitego `instagram`, `tiktok`, `youtube`. Rzeczownik od marki wchodzi tylko jako pospolity, pisany małą literą, z flagą `marka` i decyzją.
- **R6. Litery:** po NFC i małych literach tylko `aąbcćdeęfghijklłmnńoóprsśtuwyzźż` (`ALPHABET` w `policy.py`). Kandydaci wielką literą (nazwy) odpadają na B3, a nie dopiero w buildzie.

## Otwarte pytania i ryzyka
- Rodzaj `cringe`: przymiotnik nieodmienny („to jest cringe”) czy rzeczownik n? Dla gry to ta sama jedna forma. Dla wzoru i tagów trzeba wybrać. Proponuję oba, jak `cool` ma `adj` i `adv`. Decyzja użytkownika.
- `krindż`: odmienny (krindżu, krindżem)? Wtedy wzór m3 na `-ż` (np. `garaż`). Liczby: [do uzupełnienia z ccrawl/potoczne].
- Flaga `angielski-wygląd` (`ee`, `oo`, `sh`, `th`, `gh`, końcowe `w`) trafia w 3 092 lematy SGJP, w tym 2 697 z ≥ 5 formami (np. `audiobook`, `bazooka`, `biathlon`, ale też polskie `aktyw`, `badziew`). Dlatego to tylko flaga, nigdy cięcie.

---

## 1. Jak SGJP 20261018 notuje zapożyczenia (lematy pospolite)

| Lemat | Klasa (rodzaj) | Form | Kwalif. | Uwagi |
|---|---|---|---|---|
| hejt | subst m3 | 10 | — | `hejcie` (Ms., W.); osobno `hejt` interj `gwar.,rzad.` |
| hejter | subst m1 + depr m2 | 11 | `pot.` | `hejterzy` i `hejtery` |
| hejtować | czasownik | 101 | `pot.` | |
| lajk | subst m2/m3 | 10 | — | `lajkować` 101 form, `pot.` |
| mem | subst m3 | 10 | — | `memowy` 12 |
| spoiler / spojler | subst m3 | 10 / 10 | — | dwie pisownie; brak `spoilerować` |
| fejk | subst m2/m3 | 10 | `pot.` | `fejkowy` 12; brak `fake` |
| mail / mejl / e-mail | subst m2/m3 | 11 / 11 / 11 | `pot.` | `e-mail` niegrywalny (myślnik) |
| selfie | subst n | 1 | — | nieodmienne |
| cool, trendy | adj (+ adv) | 1 | `pot.` | nieodmienne |
| okej, fair | adj, adv (+ interj) | 1 | — | nieodmienne |
| youtuber, influencer, hipster, stalker, spamer | subst m1 + depr m2 | 11 | — | wzór dla `boomer` |
| ranking, stalking, mobbing, coaching, briefing | subst m3 | 9 | — | wzór dla `ghosting` |
| lockdown | subst m3 | 10 | — | jest w SGJP (kontrola dodatnia) |
| tweet | subst m2/m3 | 11 | — | `tweecie` |
| start-up | subst m3 | 10 | — | tylko z myślnikiem; brak `startup` |
| quiz / kwiz | subst m3 | 10 / 10 | — | `quiz` niegrywalny (q) |
| bumer | subst m3 | 10 | — | homograf dla `boomer` |
| brak w SGJP | — | — | — | boomer, ghosting, cringe, krindż, hype/hajp, gamer/gejmer, emoji, hashtag (jest `hasztag`), streamować, vlog/wlog, deepfake, chatbot |

„Form” to liczba różnych form (bez powtórzeń przy różnych tagach). Kolumna „Kwalif.” podaje kwalifikatory z kolumny 5 eksportu.

## 2. Wzory dla kandydatów z kontroli

| Kandydat | Wzór SGJP | Formy według wzoru | Nowe w grze |
|---|---|---|---|
| boomer | hejter (m1, depr m2) | boomer, boomera, boomerach, boomerami, boomerem, boomerom, boomerowi, boomery, boomerze, boomerzy, boomerów | 11 |
| bumer (m1) | hejter | jak wyżej z `bumer-` | 1 (`bumerzy`); reszta jest w SGJP jako m3 |
| ghosting | ranking (m3) | ghosting, ghostingu, ghostingowi, ghostingiem, ghostingi, ghostingów, ghostingom, ghostingami, ghostingach | 9 |
| cringe | cool (adj) / selfie (n) | cringe | 1 |
| wulwa | malwa, salwa (f) | 10 form (metoda-02) | 10 |

- `kontrole.json` z #16 ma dla `ghosting` tylko 4 formy (l. poj.). Do liczenia w zbiorach sieciowych trzeba użyć pełnego wzoru `ranking` (9 form). Inaczej B5a zaniży odmianę.
- Wzór `hejter` daje `boomery` jako depr m2. To forma deprecjatywna SGJP; przechodzi razem ze wzorem.

## 3. Polonizacje i warianty: reguła wyboru
1. Policz osobno każdą pisownię (oryginał, spolszczenie, wielka litera, z myślnikiem, z apostrofem).
2. Każda pisownia grywalna z B1–B7 → osobny kandydat w tej samej karcie.
3. Pisownia niegrywalna → tylko liczba w karcie (dowód, że leksem żyje).
4. Spolszczenie, które jest homografem SGJP (`bumer`), dostaje flagę i wpływ „nowe formy w grze”. Wtedy użytkownik widzi, że decyzja zmienia prawie nic w grze.
5. Nie tworzymy spolszczeń z reguły (`łikend`, `kołczing`, `gejmer` nie wchodzą bez własnego użycia). To ta sama zasada co zakaz formacji z reguły (§2.4).

## Pliki
`/private/tmp/claude-501/-Users-robmar-Projects-Literaki/3ae5c44e-c8df-4ef9-924a-bcb0e5eaf7f8/scratchpad/potoczne/metoda/`:
`scripts/sgjp_zapozyczenia.py` → `sgjp-zapozyczenia.json` (słowa, statystyki, `-ing`, nieodmienne), `scripts/sgjp_szczegoly.py` → `sgjp-szczegoly.json` (apostrofy, pełne paradygmaty wzorów, `angielski-wygląd`), `scripts/sgjp_swiadoma.sh` (feminatywy, wzory dla wulwy). Wejście: `nowe-slowa/neolog/sgjp/sgjp-20261018.tab.gz`.
