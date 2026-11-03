# docs: KWJP, NKJP, Słowosieć i wcześniejsze braki w SGJP

## TL;DR
- KWJP100 to 100 mln słów z lat 2011–2020: książki i prasa, bez internetu i mowy. Lista frekwencyjna obejmuje tylko jednostki z co najmniej 5 wystąpieniami. Lematy koryguje słownik Morfeusza SGJP. Słowo spoza SGJP dostaje lemat z sieci neuronowej, więc jego „brak w lematach” może być artefaktem.
- NKJP to 300 mln słów, teksty do 2010 roku. 1-gramy są zapisane małymi literami i nie mają progu.
- Słowosieć: lokalnie nie ma udokumentowanej polityki pokrycia. ADR-011 opisuje tylko, co z niej bierzemy.
- Precedens: suplement dopuszcza wyłącznie słowa obecne w opisie SGJP i w KWJP (się/siebie). Słowa, których nie ma w samym SGJP, zapisano jako „lukę źródła” i odłożono (`antydumpingowy`). Prompt v3 zabrania dopisywania słów dlatego, że są w SJP.pl.

## Kluczowe decyzje
- Za dokumenty projektu uznano `docs/literaki-niezalezne-slowniki-prompt-v3.md`, `AGENTS.md`, decyzję rundy 4 i benchmarki v25–v29.
- Czy „wulwa” spełnia warunki suplementu: ten plik zbiera tylko kryteria. Liczby ma podać zbieracz `local`.

## Otwarte pytania
- Zakresu leksykalnego Słowosieci 4.5 i znaczenia `lexicalunit.status` nie opisano w żadnym lokalnym dokumencie. ADR-011: „Znaczenie `lexicalunit.status` (0–5) jest nieudokumentowane”.
- Nie wiadomo, czy dodanie „wulwy” mieściłoby się w precedensie rundy 4. Precedens wymagał obecności w opisie SGJP. Według stanu z eksportu „wulwy” w SGJP nie ma.

## 1. KWJP (`cache/kwjp/article.pdf`, Kieraś i in., *Język Polski* CV 2)
- Rozmiar: „korpus zrównoważony (100 mln słów) oraz korpus niezrównoważony (ponad 1,4 mld słów)”. (s. 6)
- Skład: „Do KWJP nie włączono więc tekstów stricte internetowych – forów, blogów, wpisów z sieci społecznościowych”, nie ma też mowy. Weszły „tylko pełne teksty książek napisanych oryginalnie po polsku”. Z prasy pominięto ogłoszenia i reklamy. (s. 7)
- Gatunki: „30 procent (fikcja), 35 procent (fakt) i 35 procent (publicystyka)”. „Fakt” obejmuje m.in. poradniki i teksty popularnonaukowe i naukowe. (s. 8)
- Lematyzacja: „W przetwarzaniu KWJP zastosowano więc dodatkowy etap, na którym lematy są korygowane słownikowo, jeśli tylko dana forma występuje w słowniku Morfeusza SGJP”. Przy tagerze neuronowym „możliwe jest pojawienie się lematów zupełnie nieprawdopodobnych fleksyjnie”. (s. 11–12)
- Listy (`cache/kwjp/lists-doc.html`): „ograniczone do jednostek, które wystąpiły co najmniej 5 razy w całym korpusie”. Zawierają „wyłącznie słowa zapisane literami alfabetu łacińskiego”. Zebrano je „mechanicznie … mogą zatem zawierać błędy”.
- **Wniosek:** jeśli „wulwa” ma w KWJP mniej niż 5 wystąpień, nie będzie jej na żadnej liście. Gdy ma więcej, a SGJP jej nie zna, jej lemat może być inny niż „wulwa”. Dlatego trzeba sprawdzić listę form (`orth_lc`), nie tylko lematów. Korpus bez internetu i z małą ilością tekstów medycznych zaniża częstość terminów anatomicznych. To wniosek z opisu składu, nie pomiar.

## 2. NKJP
- Rozmiar i zakres: „korpus zrównoważony o wielkości 300 milionów słów oraz wielki korpus niezrównoważony o wielkości 1,8 miliarda słów”. Zbiór obejmuje „teksty powstałe do 2010 roku” i jest „zamrożony” (`article.pdf`, s. 6). Ma podkorpus mowy i tekstów internetowych, łącznie ok. 15% (s. 7).
- N-gramy (`cache/nkjp/nkjp-page.html`): „extracted from the balanced subcorpus of National Corpus of Polish (300M tokens) … Each unigram is maximum continuous chunk of non-whitespace lower-case characters. The resource contains all unique N-grams”. Licencja CC-BY.
- **Wniosek:** 1-gramy NKJP nie mają progu, więc zero znaczy brak w zrównoważonym NKJP. Każdą formę trzeba liczyć osobno, bo to formy, nie lematy.

## 3. PoliMorf: SGJP połączony z SJP.pl
- `cache/sgjp-docs/Morfeusz2.pdf` (wstęp): Polimorf to słownik „łączący SGJP z obszernymi, ale słabiej dopracowanymi w zakresie informacji gramatycznej danymi społecznościowego słownika SJP.pl”.
- `cache/sgjp-docs/release.html`: wydanie 20260823 ma też `polimorf-20260823.tab.gz`. Nie ma go w `cache/sgjp/`.
- Prompt v3, l. 83: „nie używaj PoliMorfa ani innych zasobów o udokumentowanym pochodzeniu od SJP.pl jako wejść konstrukcyjnych”.
- **Wniosek:** gdyby „wulwa” była w PoliMorfie, wskazywałoby to na pochodzenie z SJP.pl, a nie z SGJP. Jako wejście PoliMorf jest zakazany.

## 4. Słowosieć 4.5 (`docs/adr/ADR-011-zrodla-slowosiec-iate.md`)
- Zrzut `wordnet_work_4_5.zip` to robocza baza edytorska z datą 2021-07-23. ADR wybiera relacje 11, 25 i 27 oraz części mowy 1–4. Kody 5–8 to angielski Princeton WordNet. `status`: „bez filtra”.
- Pochodna `plwn45-tematy.sqlite` ma wszystkie 514 016 jednostek `lexicalunit`, czyli pełny zestaw lematów.
- Wcześniejsze badanie (`.maister/tasks/research/2026-10-27-slowniki-tematyczne/analysis/findings/wide-plwordnet-licencja-i-dane.md`): 4.5 ma 194 787 polskich lematów. Słowosieć ma „kwalifikatory rejestru (`og.`, `specj.`)”, ale nie ma dziedzin. Najnowsze wydanie to 5.0, dostępne „po weryfikacji zgłoszenia”, czyli dla nas niedostępne.
- **Nieudokumentowane:** zasady doboru lematów Słowosieci. W cache i w docs nie ma opisu polityki pokrycia. Ustalić można tylko, że „wulwodynia” jest, a „wulwy” nie ma (pomiar zbieracza `local`). Wyjaśnienie tego braku wymaga źródeł zewnętrznych albo zostaje hipotezą.

## 5. Jak projekt traktował dotąd braki w SGJP
### Zasady
- Prompt v3 §2.4, l. 63: podstawą BROAD są „**leksemy udokumentowane w danych SGJP udostępnionych z Morfeuszem**”.
- §2.3, l. 56: STANDARD zachowuje „terminologię fachową i naukową” i wulgaryzmy, więc termin anatomiczny nie odpada z powodu dziedziny.
- §3.1, l. 77: „nie wykorzystuj SJP.pl do pozyskiwania leksemów, form, reguł …”.
- §3.2, l. 97–98: poprawka po benchmarku musi mieć „uzasadnienie w źródłach przyjętych do konstrukcji … niezależne od samej obecności słowa w SJP.pl”. Musi też dotyczyć „ogólnej reguły, a nie dopisania słów z listy różnic”.
- `AGENTS.md`, l. 17: decyzje zmieniające skład omawia się z użytkownikiem i pokazuje „przykłady, alternatywy i przewidywany wpływ”.

### Runda 4: jedyny wpis suplementu
Decyzja: `.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/round4-sjp-benchmark-fixes-decision.md`.
- Powód: przypięty eksport „nie zawiera ani jednego wiersza z lematem `się` lub `siebie`”. W KWJP lemat `siebie` ma 211 982 wystąpienia, a `się` 1 733 236. Plik suplementu dodaje, że słowa są „obecne w opisie SGJP i w KWJP”.
- Zakres: wyłącznie 4 formy w tagsecie SGJP. „Z listy SJP nie skopiowano żadnego słowa.”
- Szukanie podobnych przypadków objęło lematy KWJP z co najmniej 30 wystąpieniami. „Brakuje natomiast przymiotników przedrostkowych, których nie ma **w samym SGJP**, nie tylko w eksporcie (`antydumpingowy`, …). To osobna luka źródła; wymagałaby konstruktora lub nowego źródła i nie wchodzi w tę rundę.” Reszta braków to „wtrącenia obce, literówki korpusu i nazwy własne”.
- Wycofanie: usuwa się wiersz z `sgjp-supplement.tab` i robi nowy build.

### Benchmarki
- `sjp-benchmark-v25.md`: 98,2% słów SJP brakujących w BROAD „nie ma w SGJP ani w naszych konstrukcjach. To luka źródła, a nie decyzja reguł”. 605 325 z nich ma w KWJP frekwencję 0.
- `sjp-benchmark-v27.md` i `-v29.md`, sekcja „Otwarte”: „Luki źródła: przymiotniki z przedrostkiem (`antydumpingowy`), pospolite homonimy nazw własnych (`janusz`, `kraków` od „krak”)”. Te sprawy nadal są otwarte.
- `source-extension-decision.md` (wariant A): nowe źródła dopuszczono tylko jako dowody „dla jednostek/konstrukcji z istniejących leksemów SGJP. Nie rozszerzać zasobu leksemów”.

### Wniosek dla „wulwy”
- Jeśli sgjp.pl potwierdzi brak, „wulwa” jest w tej samej klasie co `antydumpingowy`: nie ma jej w samym SGJP, nie tylko w eksporcie. Sprawdza to zbieracz `external`. Precedens się/siebie to inny przypadek, bo te słowa są w opisie SGJP i są częste w KWJP.
- Dodanie „wulwy” byłoby pierwszym leksemem spoza SGJP. Wymaga to decyzji użytkownika o rozszerzeniu zasobu leksemów (por. wariant A „nie rozszerzać zasobu leksemów”).
- Uzasadnienie musiałoby pochodzić z KWJP, NKJP albo innego dopuszczonego źródła, nie z SJP.pl (§3.2). Najlepiej jako reguła ogólna, nie jedno słowo.
