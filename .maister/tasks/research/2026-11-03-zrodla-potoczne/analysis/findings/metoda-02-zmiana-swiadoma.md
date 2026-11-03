# metoda: typ „zmiana świadoma” (wulwa)

## TL;DR
- „Zmiana świadoma” to **osobny typ dowodu**, nie warstwa liczbowa. Słowo jest proponowane celowo (anatomia bez wartościowania, feminatywy, język niebinarny) i opisane w redagowanym źródle, np. Dobry Słownik. Częstość jest mała z definicji, więc progi z warstwy potocznej by je wycięły.
- Rekomendacja (do decyzji użytkownika): **Z2 = dowód ręczny ze źródła świadomej zmiany + minimalny niezależny dowód użycia**. Sam wpis w słowniku propozycji to za mało, bo lista gry ma opisywać użycie. Próg użycia jest jednak dużo niższy niż w warstwie potocznej.
- Zakres jest mały. SGJP 20261018 ma już wiele feminatywów i słów tej grupy: gościni, naukowczyni, psycholożka, pedagożka, filolożka, architektka, niebinarny, niebinarność (pomiar niżej). Wulwa i część nowszych form nie są w SGJP.
- Licencja i redakcja źródeł: [do uzupełnienia z swiadoma].

## Kluczowe decyzje
- **Dowód ręczny = link + data odczytu + krótki opis hasła własnymi słowami.** Bez kopiowania haseł i danych, jak OJ UW w #16. Jeśli źródło ma licencję danych, nadal tylko dowód (nie źródło leksemów).
- **Minimalny dowód użycia (Z2):** spełniony jest jeden z warunków:
  - (a) ≥ 3 użycia w korpusie z licencją (PPC, ParlaMint, Leipzig, KWJP), poza cytatem samego słownika;
  - (b) w zbiorze sieciowym ≥ 5 hostów niezależnych od źródła świadomej zmiany i od SJP.pl, ≥ 10 trafień, B1–B5 z `metoda-01`;
  - (c) użycie w publikacji redagowanej (poradnik medyczny, podręcznik, publikacja naukowa, komunikat instytucji), link + data odczytu.
- **Wzór fleksji jak każde słowo** (ADR-016). Słowo musi mieć pełny paradygmat SGJP i przejść te same reguły gry.
- **Bez kwalifikatora w suplemencie.** Typ dowodu zapisujemy w rejestrze decyzji i w pliku dowodów, nie w kolumnie kwalifikatorów. Pusty kwalifikator daje słowu te same filtry co leksemowi SGJP.

## Otwarte pytania i ryzyka
- Czy użytkownik przyjmuje Z2, czy woli Z1 (sam dowód ręczny)? Przy Z1 lista może zawierać słowa, których nikt nie używa. Przy Z3 (progi potoczne) wulwa pewnie odpadnie.
- Liczby użycia wulwy w sieci: [do uzupełnienia z ccrawl/potoczne]. W #16: KWJP 0, PPC 0, ParlaMint 0, Leipzig 0. NKJP ma 4× `wulw` i 2× `wulwa`, ale #16 ocenił je jako nazwisko. Więc warunek (a) dziś nie jest spełniony.
- Słownik świadomej zmiany może być jedynym miejscem użycia. Wtedy B8 wyklucza go z liczenia i zostają (b) lub (c).
- Ryzyko polityczne: lista nie może wyglądać na opowiedzenie się po jednej stronie. Ten sam próg dla każdego słowa tego typu, też dla słów z przeciwnych środowisk.

---

## 1. Definicja i granice
- **Wchodzi do typu:** słowo, które redagowane źródło świadomej zmiany zaleca w miejsce innego słowa albo jako nowe (wulwa zamiast srom w sensie „całość narządów zewnętrznych”, feminatyw, forma niebinarna).
- **Nie wchodzi:** zwykły neologizm prasowy (warstwy z #16), potocznizm (warstwa potoczna), formy zaimkowe lub końcówki, które nie są nowym leksemem (np. formy czasownika w rodzaju niebinarnym) — to zmiana fleksji SGJP, osobny temat poza #16.
- Typ jest atrybutem dowodu, nie leksemu. Słowo może mieć oba: dowód świadomej zmiany i liczby z warstwy potocznej.

## 2. Opcje

| Opcja | Dowód | Za | Przeciw | Wulwa dziś |
|---|---|---|---|---|
| Z1 | tylko dowód ręczny ze źródła | proste; pasuje do uwagi użytkownika z D5 | lista może mieć słowa bez użycia; jedno źródło decyduje | przechodzi |
| **Z2 (rekomendacja)** | dowód ręczny + minimalny niezależny dowód użycia | słowo opisuje użycie; niski próg nie wycina celu | trzeba policzyć użycia poza źródłem | [do uzupełnienia z ccrawl/potoczne] |
| Z3 | progi warstwy potocznej (B1–B7) | jeden mechanizm | wycina rzadkie słowa celowe | prawdopodobnie odpada |

## 3. Co już jest w SGJP 20261018 (pomiar)
Skrypt: `/private/tmp/claude-501/-Users-robmar-Projects-Literaki/3ae5c44e-c8df-4ef9-924a-bcb0e5eaf7f8/scratchpad/potoczne/metoda/scripts/sgjp_swiadoma.sh` (awk na `sgjp-20261018.tab.gz`, dokładne lematy).

| W SGJP | Brak w SGJP |
|---|---|
| gościni, naukowczyni, psycholożka, pedagożka, filolożka, architektka, niebinarny, niebinarność; srom (`anat.`), łechtaczka (`anat.`) | wulwa, chirurżka, ministra (jako f), transpłciowy, cispłciowy |

Wniosek: duża część feminatywów jest już w SGJP. Typ „zmiana świadoma” obejmie kilka–kilkanaście leksemów na kwartał, nie setki. Wystarczy przegląd ręczny.

## 4. Wzór fleksji dla wulwy
- Rzeczownik f, temat zakończony na `-lw-`. Wzory w SGJP z tą samą odmianą: **malwa** (`bot.`, 11 wierszy), **salwa** (11 wierszy).
- Formy według wzoru: wulwa, wulwy, wulwie, wulwę, wulwą, wulwo, wulw, wulwom, wulwami, wulwach (10 form; zgodne z ręczną listą w `nowe-slowa/kontrole.json`).
- Wszystkie litery są w alfabecie gry. Oryginał łaciński/angielski `vulva` odpada na B1 (litera v).
- Homograf: SGJP ma `Wulw` jako nazwę własną (z `sgjp_prefix` w `kontrole.json`), nie pospolitą. Flaga `homograf-SGJP` nie dotyczy wersji małą literą.

## 5. Kroki dla kandydata tego typu
1. Wpis źródła: nazwa, URL hasła, data odczytu, kto redaguje, licencja (lub „brak licencji, tylko dowód ręczny”).
2. Opis hasła własnymi słowami (1–2 zdania), bez kopiowania definicji.
3. Dowód użycia (a/b/c z Kluczowych decyzji), z liczbami lub linkiem.
4. Wzór fleksji i pełna lista form.
5. Karta jak w `metoda-03-karta.md`, z polem `typ: zmiana_swiadoma`.
6. Decyzja użytkownika. W rejestrze: typ dowodu i wynik Z2.
