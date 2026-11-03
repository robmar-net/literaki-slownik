# Synteza: źródła słów potocznych i świadomych zmian językowych

## TL;DR
- **Nie ma jednego dobrego źródła.** Dowód składa się z trzech części: redagowany słownik (Dobry słownik, ręcznie), sieć ogólna (FineWeb-2/HPLT, tylko liczby) i małe korpusy z czystą licencją (BAN-PL, dyskusje plwiki). Napisy dają najmocniejszy sygnał, ale nie mają licencji tekstu.
- **Wulwa ma dowód.** Jest w Dobrym słowniku (od I–II 2024), w wolnym tezaurusie DS, w sieci (6 hostów z lat 2018–2024), w dyskusjach plwiki (2023) i w napisach 2022–2023. Wniosek #16 „nie ma w żadnym źródle” był błędny (swiadoma-01). Przy progu Z2 wulwa jest blisko progu (b) i prawdopodobnie przechodzi przez (c).
- **Common Crawl potwierdza, ale nie odkrywa.** Jako źródło nowych słów potocznych daje głównie terminy, spam i handel; słów potocznych jest ok. 4% (ccrawl-03). Do karty kandydata się nadaje, do automatycznej listy nie.
- Liczby z sieci są **przed filtrem opt-out**, a część z danych pośrednich. Dziś 34 ze 100 największych hostów blokuje CCBot (ccrawl-04).

## Kluczowe decyzje
- Proponuję: sieć tylko jako **liczby w karcie** (art. 26³ pr. aut.), bez kontekstów w repo; napisy tylko lokalnie; „zmiana świadoma” jako **typ dowodu Z2**, nie warstwa; tezaurus DS jako sygnał lokalny, bez importu; zaimki.pl bez użycia.
- Wszystkie te punkty to decyzje użytkownika. Lista D1–D10 jest w raporcie (`outputs/research-report.md`, § Decyzje).

## Otwarte pytania i ryzyka
- **Cytaty już w publicznym repo.** `potoczne-01` i `potoczne-03` zawierają krótkie zdania z napisów i z kafeteria.pl. Są już w `origin/main` (commity `2d14fa6`…`719ce1a`). To kłóci się z zaleceniem `ccrawl-01` i `metoda-01`: konteksty tylko lokalnie. Do decyzji: usunąć je i zastąpić opisem.
- Liczba form ghostingu: 4 w `kontrole.json` i 9 we wzorze `ranking` (metoda-04). Liczby ghostingu w `ccrawl-02` i `potoczne-03` mogą być zaniżone.
- Prawo TDM to odczyt zbieracza, nie porada prawna (ccrawl-01).

---

## 1. Pytanie badawcze
Skąd literaki-slownik może brać wiarygodne dowody na słowa potoczne, internetowe i świadome zmiany językowe, których nie widać w PPC, ParlaMint i Leipzig? (planning/research-brief.md)

## 2. Podsumowanie
Zbieracze ocenili 18 nowych źródeł potocznych (potoczne-01), dwa zbiory Common Crawl z analizą prawa (ccrawl-01..04), Dobry słownik, zaimki.pl, RJP, poradnie, 5 publikacji i plebiscyty (swiadoma-01..03). Kategoria metody opisała bramki B1–B8, nowe pola karty i typ „zmiana świadoma” (metoda-01..05).

Wynik dzieli się na dwie ścieżki. **Słowa potoczne** (cringe, boomer, ghosting) widać w sieci i w napisach, ale z dużym szumem znaczeniowym: ghosting w sieci to w większości „anti-ghosting” monitorów (ccrawl-02), a boomer to też guma do żucia, manicure i nicki (potoczne-03, ccrawl-02). Bez filtra znaczeń liczby wprowadzają w błąd. **Świadome zmiany** (wulwa, feminatywy, słowa transpłciowości) mają dowód w redagowanym słowniku DS. Mają też rzadkie, ale niezależne użycie w sieci. Częstość jest za mała dla progów potocznych (Z3), więc potrzebny jest osobny, niższy próg (Z2).

Licencja jest głównym ograniczeniem. Czystą licencję tekstu i daty ma niewiele źródeł (BAN-PL, dyskusje plwiki). Źródło z najmocniejszym sygnałem (OpenSubtitles) nie ma licencji tekstu. Common Crawl daje się liczyć lokalnie na podstawie art. 26³, ale wiąże opt-out, a dziś duża część dużych portali TDM zastrzega.

## 3. Analiza krzyżowa

### 3.1 Ustalenia potwierdzone przez kilka źródeł (pewność wysoka)
| Ustalenie | Źródła |
|---|---|
| Wulwa jest używana w znaczeniu anatomii człowieka od ok. 2018–2022 | DS (swiadoma-01), CC 6 hostów 2018–2024 (ccrawl-02), plwiki dyskusje 2023 (potoczne-03), napisy 2022–2023 (potoczne-03), kampanie od 2022 (swiadoma-03) |
| Wulwy nie widać w korpusach prasowych i parlamentarnych | Leipzig 0 (metoda-05), KWJP/PPC/ParlaMint 0 z #16 (metoda-02), publikacje naukowe 0 (swiadoma-03) |
| Kontrole dodatnie datują się poprawnie | lockdown 0 przed 2020 w FW2 (ccrawl-02); hejt rośnie w plwiki (potoczne-03) |
| Podział w czasie jest konieczny | mono OpenSubtitles bez dat: hejt 0, lockdown 0 przy 235 mln słów (potoczne-03); FW2 wg lat (ccrawl-02) |
| SJP.pl prawie nie skaża próbki sieciowej | ≤0,008% dok. z hosta sjp.pl, 0 trafień kontroli (ccrawl-02); brak zbioru sjp.pl w SpeakLeash (potoczne-01) |
| B3 (mała litera) najlepiej odcina angielski | metoda-05 (0/20 słów angielskich); ccrawl-02 (`cap` osobno) |
| SGJP przyjmuje feminatywy pojedynczo | psycholożka, muralistka w 20261018 (swiadoma-04, metoda-02) |

### 3.2 Sprzeczności i niespójności
| # | Sprzeczność | Pliki | Wyjaśnienie / skutek |
|---|---|---|---|
| S1 | **Wulwa: Leipzig 0 vs sieć 6 hostów** | metoda-05 vs ccrawl-02 | Nie ma sprzeczności co do faktu. Wiadomości nie piszą o anatomii, sieć tak. Skutek: progi kalibrowane na Leipzig nie nadają się dla typu „zmiana świadoma”. |
| S2 | **Ghosting: 4 formy vs 9 form** | `kontrole.json` (metoda-04) vs wzór `ranking` | metoda-05 liczyła 9 form. ccrawl-02 i potoczne-03 liczyły formy z `kontrole.json`, więc ghosting może być tam zaniżony (brak l.mn.). Przeliczyć z 9 formami. |
| S3 | **ccrawl-03 na danych pośrednich** | ccrawl-03 (~535 mln słów: FW2 ~165 + HPLT ~370) vs ccrawl-02 (662,7 mln) | Liczby 6 239 form i 314 grup nie są końcowe. Hosty zaniżone (limit 12 na kawałek). Rząd wielkości wg autora bez zmian. |
| S4 | **Liczby sprzed filtra opt-out** | ccrawl-02, ccrawl-03 vs ccrawl-04 | 34/100 największych hostów blokuje CCBot (37,6% ich dok.). Po filtrze liczby spadną, zwłaszcza dla słów z portali. |
| S5 | **Wulwa #16: HPLT 19 vs teraz 3** | ccrawl-02 (kolumna #16) | 19 to wzorzec prefiksowy (`wulw*`, z zoologią). Dokładne formy: 2 w #16. Nie mieszać tych liczb. |
| S6 | **Trzy różne filtry „tekst angielski”** | potoczne-03 (≥2 słowa stop i przewaga), ccrawl-02 (>2% tokenów), metoda-01 B4 (przewaga funkcyjnych) | Liczby z różnych źródeł nie są w pełni porównywalne. Ujednolicić B4 przed wdrożeniem. |
| S7 | **Progi rozrzutu: B6 ≥10 hostów vs Z2(b) ≥5 hostów vs ccrawl-03 ≥5 hostów** | metoda-01, metoda-02, ccrawl-03 | Celowe różnice, ale nienazwane. Wymaga jednej tabeli progów. |
| S8 | **„ministra”: RJP „nietypowa” vs DS ją ma (2024)** | swiadoma-02 vs swiadoma-04 | Kandydat ma sprzeczny dowód normatywny. Karta musi pokazać oba. |
| S9 | **Konteksty w repo** | ccrawl-01, metoda-01 (tylko lokalnie) vs potoczne-01/03 (cytaty z napisów i forum w pliku) | Pliki są już w `origin/main`. Decyzja D10. |
| S10 | **Wulwa w plwiki: 7 vs 158** | potoczne-03 | 7 to dyskusje (świadoma zmiana), 158 to artykuły (głównie zoologia, narząd dwuparców). Słowo ma drugie, starsze znaczenie. |

### 3.3 Pewność
- **Wysoka:** obecność wulwy w DS i w tezaurusie DS (pliki, SHA256, wiersze); licencje z cytatami (potoczne-02, ccrawl-01); stan SGJP dla kandydatów (swiadoma-04, metoda-04); kalibracja v2 na Leipzig (metoda-05).
- **Średnia:** liczby kontroli w sieci (próbka 8×, nie 10×; przed opt-out; ghosting zaniżony); ekstrapolacje (przedziały Poissona, ccrawl-02); szum ccrawl-03 (ręczna ocena 150 grup).
- **Niska:** ocena prawna dla napisów i forów; skutki OQL; czy art. 26³ liczy stan opt-out w dniu naszego pobrania (ccrawl-04).

## 4. Wzorce i motywy

| Wzorzec | Opis | Dowody | Zasięg |
|---|---|---|---|
| W1. Licencja odwrotnie proporcjonalna do sygnału | Im lepszy sygnał potoczny, tym gorsza licencja | Napisy: 7/7 kontroli, brak licencji; BAN-PL: CC BY, ale 0,71 mln słów; Common Voice: CC0, 0 trafień (potoczne-01, -03) | wszystkie kategorie |
| W2. Opakowanie ≠ tekst | Licencja zbioru (ODC-By, CC0, MIT) nie obejmuje tekstu autorów | FineWeb-2, HPLT (ccrawl-01), SpeakLeash MIT (potoczne-02) | potwierdza zasadę z #16 |
| W3. Szum znaczeniowy w słowach angielskich | Ten sam ciąg ma inne znaczenia | ghosting = monitor (ccrawl-02), boomer = guma, manicure, okręt, nick (potoczne-03, ccrawl-02), cringe = tytuły | wszystkie kontrole celu |
| W4. Redagowany słownik wyprzedza korpusy | DS ma hasła na lata przed korpusami prasowymi | lockdown 2020, boomer 2022, wulwa 2024, cringe 2024 (swiadoma-01) | świadoma zmiana i potoczne |
| W5. Słowo istnieje, ale z innym znaczeniem | Homografy i stare znaczenia | wulwa zoologiczna (potoczne-03), bumer m3 w SGJP (metoda-04), Wulw jako nazwa (metoda-02) | kilka kandydatów |
| W6. Generowanie wg wzoru ≠ użycie | Lista wzorcowa daje słowa bez użycia | 270 form `-lożka` w tezaurusie (angelolożka), neutratywy zaimki.pl (swiadoma-02, -04) | feminatywy |
| W7. Sieć widzi terminy, nie potoczność | Nowe formy w CC to głównie terminy i handel | 45% terminy, 4% potoczne, 25% spam (ccrawl-03) | wykrywanie |
| W8. Opt-out rośnie po crawlu | Strony zastrzegają TDM po zebraniu danych | 34/100 CCBot, 8/200 jawny tekst TDM, 0/200 TDMRep (ccrawl-04) | CC, fora |

## 5. Kluczowe spostrzeżenia

**I1. Dowód potoczny i dowód świadomej zmiany wymagają innych progów.** Wulwa w sieci ma 0,006–0,016 ipm (ccrawl-02), a szkic B7 to ≥0,05 ipm i ≥20 trafień (metoda-01). Pod Z3 odpada, jak przewidział metoda-02. Pod Z2(b) spełnia warunek ≥5 hostów (6), ale nie ≥10 trafień (3+3 w próbce). Z2(c) (publikacja redagowana) jest prawdopodobnie spełniony przez „Seksuologię Polską” 2015 i wysokieobcasy.pl 2022, cytowane w DS. Tych tekstów nikt nie sprawdził bezpośrednio. Pewność: średnia.

**I2. Napisy to najlepszy detektor, ale słaby dowód.** Mają wszystkie kontrole (potoczne-03), ale: brak licencji tekstu, duplikaty wersji (trzeba liczyć filmy, nie zdania), tłumaczenia z angielskiego (kalka tłumacza). Nadają się do kolejki, nie do karty. Pewność: wysoka co do sygnału, niska co do prawa.

**I3. Common Crawl to potwierdzenie dla podejrzanego słowa.** Ekstrapolacja daje setki–tysiące trafień dla każdej kontroli w całym zbiorze (ccrawl-02), a próbka 1–2 mld słów z filtrem znaczenia wystarczy do kart. Wykrywanie wymaga filtra spamu, którego nie ma (ccrawl-03). Pewność: średnia.

**I4. Gra sama zawęża decyzję.** B1 (alfabet) odcina `cringe'owy`, `vlog`, `quiz` (metoda-04). Pole „nowe formy w grze” pokazuje, że `bumer` m1 dodaje 1 formę, `boomer` 11, a `ministra` tylko 4 nowe formy (metoda-03, swiadoma-04). Decyzja użytkownika dotyczy więc mniej form, niż wygląda. Pewność: wysoka.

**I5. Feminatywy to największa i najtańsza pula, ale z pułapką wzoru.** Tezaurus DS ma 1761 haseł bez lematu w SGJP (w tym 270 na `-lożka`). DS ma 5448 haseł bez formy w SGJP, a DS ∩ zaimki.pl daje 122 feminatywy spoza SGJP (swiadoma-01, -04). Część to formy wzorcowe bez użycia. Pewność: wysoka co do liczb, średnia co do jakości.

**I6. Ryzyko SJP.pl jest małe we wszystkich nowych źródłach.** Sieć ≤0,008% dok. (ccrawl-02). DS: ryzyko niskie, niezerowe (redaktor zaczynał od SJP.pl; tezaurus z OpenThesaurus). `pl_PL.dic` z `.oxt` odpada (swiadoma-01). Pewność: średnia.

## 6. Zależności
```
kandydat (kolejka: ręczna, DS, tezaurus, napisy, CC, plebiscyt)
   └─► karta (metoda-03)
         ├─ typ dowodu: korpus | potoczne | zmiana_swiadoma | reczny
         ├─ bramki B1–B8 (metoda-01) ← progi v2 (metoda-05)
         ├─ liczby: CC (po opt-out, ccrawl-04), BAN-PL, plwiki, napisy (lokalnie)
         ├─ dowód ręczny: DS (URL + data), RJP (reguła klasy), publikacja (DOI)
         └─ wpływ: nowe formy w grze (SGJP 20261018, wzór fleksji)
               └─► decyzja użytkownika ─► suplement v2 (D1-A, ADR-016)
```
- Opt-out (ccrawl-04) blokuje publikację liczb z CC, dopóki nie ma listy hostów albo sprawdzenia hostów dowodów kandydata.
- Wzór fleksji (metoda-04) jest potrzebny przed liczeniem B5a (ghosting: 9 form).
- Tezaurus DS jest kwartalny, więc pasuje do rytmu ADR-018.

## 7. Luki i niepewności
- Pomiary częściowe: kafeteria 13%, plwiki 54%, HPLT `7_1` przerwany po 40 mln słów, próbka CC 8× zamiast 10× (potoczne-03, ccrawl-02).
- Brak pomiaru kandydatów świadomej zmiany w sieci (transpłciowy, tranzycja, chirurżka, kardiolożka; placeholder w swiadoma-05).
- Brak liczenia filmów (IMDb ID) zamiast zdań w napisach.
- Nie sprawdzono regulaminów forów (kafeteria) ani regulaminów hostów dowodów w CC.
- Wayback był niedostępny, więc datę dodania wulwy do DS oparto na blogu DS.
- Teksty cytowane w DS jako użycie wulwy („Seksuologia Polska” 2015, wysokieobcasy.pl) nie zostały przeczytane bezpośrednio.
- `metoda-*` mają placeholdery „[do uzupełnienia z ccrawl/potoczne]”. Synteza wypełnia je w raporcie (§ 6.4), ale pliki zostały bez zmian.
- Plan przewidywał `outputs/podsumowanie.md` i szkice ADR. Ta synteza ich nie tworzy.

## 8. Synteza wg ram (mieszane: literatura + technika)

**Stan obecny (#16).** PPC, ParlaMint i Leipzig dobrze wykrywają słowa prasowe. Potoczne i świadome zmiany mają w nich 0–6 trafień (metoda-05).

**Porównanie źródeł.**
| Źródło | Sygnał | Licencja tekstu | Daty | Rola |
|---|---|---|---|---|
| OpenSubtitles 2022–2023 | najmocniejszy (7/7) | brak | rok filmu | detektor lokalny |
| BAN-PL | wysoki ipm cringe/boomer | CC BY 4.0, „strictly for research”, hasło | okres zbioru | liczby w karcie |
| plwiki dyskusje | niski | CC BY-SA 4.0 | rok podpisu | liczby i cytat |
| FineWeb-2 / HPLT | średni, duży szum | brak (opakowanie ODC-By / CC0) | rok crawla | liczby w karcie po opt-out |
| fora SpeakLeash | słaby, stara treść | brak („conditional”) | brak | odłożyć |
| Dobry słownik | hasła wyprzedzają korpusy | prawa zastrzeżone | id, lastmod | dowód ręczny |
| tezaurus DS | lista | GPL-2.0+ / LGPL 2.1 | kwartalnie | sygnał lokalny |
| zaimki.pl | normatywny | OQL v1.4 | brak | bez użycia |
| RJP, poradnie | reguła | prawa zastrzeżone | daty | uzasadnienie klasy |

**Kompromisy.** Liczby bez kontekstów są bezpieczniejsze prawnie, ale nie da się ich zweryfikować z repo. Dlatego potrzebny jest dowód ręczny (URL + data + opis) przy każdej karcie.

**Dopasowanie do projektu.** Pasuje model z #16: wykrywanie poza buildem, karta i decyzja słowo po słowie. Nie pasuje automatyczna warstwa z sieci (W7) ani import list (W6, copyleft, OQL).

## 9. Wnioski
**Główne**
1. Dla słów potocznych: CC (liczby, po opt-out) + BAN-PL i plwiki (czyste) + napisy jako detektor lokalny. Pewność: średnia.
2. Dla świadomych zmian: typ dowodu Z2 z DS jako dowodem ręcznym. Wulwa ma drogę dowodu. Pewność: średnia–wysoka.
3. Common Crawl nie zastąpi przeglądu ręcznego: ok. 4% grup to słowa potoczne. Pewność: średnia.

**Dodatkowe**
- Pole „nowe formy w grze” zmniejsza wagę wielu decyzji (bumer, ministra).
- Wzrost użycia feminatywów w ogłoszeniach po art. 183ca § 3 KP (od 24.12.2025) to przewidywanie, nie pomiar (swiadoma-02).

**Rekomendacje:** w raporcie (`outputs/research-report.md`, § 9).
