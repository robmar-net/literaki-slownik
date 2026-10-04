# Kontrola oryginalnych danych SGJP przed dalszą implementacją

## TL;DR
Oryginalna baza SGJP ma membership SJPDor. Opublikowany tekstowy eksport Morfeusza tego pola nie ma.
Nasza baza zachowała wszystkie pięć surowych pól z każdego z 7 458 520 wierszy; żadnych metadanych nie zgubiono w imporcie.
Sprawdzono także inwentarz oryginalnego archiwum źródeł oraz kod formatu binarnego.


> Sprostowanie po rozmowie z użytkownikiem: wymaganie filtra SJPDor i późniejszego niezależnego opracowania nie było uzgodnione. Wyniki audytu pozostają aktualne; wcześniejszy opis ich konieczności nie jest bieżącą polityką generatora. Zob. [wyjaśnienie](source-policy-clarification.md).

## Key Decisions
- Oddzielamy macierzystą bazę internetową SGJP od jej publicznego eksportu Morfeusza oraz naszego importu SQLite.
- Brak pola pochodzenia w eksporcie nie oznacza braku tego pola w bazie źródłowej ani niezależnego opracowania hasła.
- Nie aktywowano nowych danych, nie zmieniono importera ani reguł gry.

## Open Questions / Risks
- Nadal potrzebny jest dopuszczony artefakt membership/proweniencji zgodny z wersją eksportu; obecność metadanych w bazie nie gwarantuje publicznego pliku do pobrania.
- Stan redakcyjny, data i brak markera nie dowodzą niezależnego opracowania.
- Pobranie całego pakietu binarnego było ograniczone timeoutem. Wniosek o jego reprezentacji jest oparty na kodzie przypiętego kompilatora; nie deklarujemy pełnej inspekcji niepobranego archiwum.

## Oryginalny tekst kontra nasza baza
Odczytano gzip UTF-8 od początku, cały 28-wierszowy nagłówek i wszystkie rekordy do końca. Każdy wiersz ma dokładnie pięć pól. Porównano każde pole z `sgjp_record`, bez normalizacji, przy sortowaniu po source_id/row_number; równość wszystkich wierszy oraz brak dodatkowych rekordów potwierdzone. Kontrola trwała 14,12 s. W tagach, nazwach i kwalifikatorach nie występuje marker SJPDor. Nie jest to próba kilku słów ani kontrola samej liczby rekordów.

[Pełny raport](original-package-audit.json) zawiera hashe oryginalnego gzipu i archiwum, jednostki oraz wyniki. Kontrola użyła `gzip.open(..., encoding='utf-8', newline='')`, podziału TAB po usunięciu wyłącznie końca wiersza oraz zapytania `SELECT form,lemma,tag,names,qualifiers FROM sgjp_record WHERE source_id=? ORDER BY row_number` w połączeniu SQLite mode=ro. Surowego pliku i historycznej bazy nie zmieniano.

## Pozostałe pliki oryginalnego pakietu
Archiwum morfeusz-src-20260823.tar.gz ma 406 zwykłych plików. Sprawdzono nazwy wszystkich członków, pliki formatów/tagsetów i kod ścieżki kompilacji. Nie znaleziono w inwentarzu pliku metadanych membership/redakcji SGJP. Dodatki, emoji, reguły segmentacji i fikstury testowe nie są eksportem internetowej bazy haseł. Nazwy plików PoliMorf odnotowano wyłącznie w inwentarzu; ich danych leksykalnych nie czytano ani nie użyto.

`buildDict.sh` buduje słownik z tekstowego SGJP, dodatków/emoji, tagsetu i reguł segmentacji. `convertinput.py:55–76` czyta formę, lemat, tag, nazwę i kwalifikator; `encode.py:178–226` koduje ich reprezentację; `serializer.py:86–103,155–181` zapisuje identyfikator/copyright, tagset, nazwy, kwalifikatory i segmentację. Ta ścieżka nie dodaje membership SJPDor ani historii redakcyjnej. Hashe przeczytanych plików są w raporcie. To dowód formatu, bez deklarowania odczytu każdego rekordu binarnego.

## Macierzysta baza SGJP
[Oficjalna instrukcja](https://sgjp.pl/instrukcja/), ogólna informacja o leksemie, opisuje marker pochodzenia SJPDor. Przypięty model Kuźni `61daf78`, metoda sgjp_info, pobiera membership z relacji vocabularies. Oficjalny eksport Morfeusza jest więc reprezentacją ograniczonego zestawu danych. Nie wolno z braku tego pola w jego pięciu kolumnach wywnioskować, że informacji nie przechowuje źródłowa baza.
