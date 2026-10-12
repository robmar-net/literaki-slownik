"""Własne notatki z ręcznego przeglądu KWJP. Nie jest to klasyfikator ani polityka."""
import collections
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
TASK = Path(__file__).resolve().parents[1]
OUT = TASK / 'analysis/findings/round2'
# Każdą niepustą odpowiedź przeczytano: pierwsze 3 konteksty, wyjątki niżej do 10.
# Notatka dotyczy obejrzanych kontekstów, nigdy wszystkich trafień danego słowa.
NOTES = '''
gojowi|historyczne|Opis stosunków społecznych i proza historyczna; obecność słowa, bez dowodu neutralnego rejestru.
konsultorzy|autorskie|Biografia i prasa; doradcy. Pierwsze dwa trafienia z jednego dokumentu.
opłotkiem|literackie|Pojedyncze poetyckie użycie ogrodzenia; brak podstaw do oceny całego paradygmatu.
franciszkana|niepewne|Żartobliwy opis wyglądu; nietypowy wariant nazwy zakonnika wymaga osobnej oceny.
nieutytułowaną|autorskie|Opis kobiety bez tytułu w książce historycznej; historyczny temat nie oznacza dawnej gramatyki.
onemu|stylizacja|Dawny cytat i stylizowana proza; brak zwykłego użycia w odczytanej części.
niezbędnikiem|autorskie|Narzędzie fajkowe i przenośny poradnik; trzecie trafienie dotyczy nazwy publikacji.
ośmset|stylizacja|Wszystkie 5 trafień w jednym dokumencie, Matka Makryna; stylizowana pisownia liczebnika.
ciżbą|literackie|Proza o wyraźnie podwyższonym rejestrze; nie dowodzi neutralności ani nieistnienia żywego użycia.
księżny|stylizacja|5 trafień: dawna odmiana w prozie historycznej, także nazwy postaci literackich.
wiela|regionalne|10 odczytanych trafień w śląskich dialogach dwóch powieści; nie są neutralną polszczyzną. Sam regionalizm nie jest automatycznym zakazem STANDARD.
ośm|stylizacja|Pierwsze 3 trafienia w Matce Makrynie; wariant osiem, nie dowód zwykłej współczesnej odmiany.
eksplikacją|autorskie|Krytyka literacka i rozważanie filozoficzne; rejestr specjalistyczny/książkowy.
bębniarzem|autorskie|Muzyka jazzowa, wykonawcy; dwa pierwsze użycia w tej samej książce.
rozbójnikami|mieszane|Dawny cytat, dialog i opis historii; różne funkcje jednego napisu.
surdutów|historyczne|Opisy ubioru, w tym cytaty; współczesność nazwy trzeba oddzielić od wieku stroju.
poniektóre|mieszane|Cytat i autorskie opisy; słowo nacechowane, nie tylko dawna mowa.
dwoiły|autorskie|Frazeologizm oraz opis roślin; nie tylko jedno znaczenie czasownika.
sotnię|mieszane|Współczesna metafora polityczna i odniesienie do organizacji historycznej.
prawili|mieszane|Autorska narracja i dawne/dialektalne cytaty.
powiadacie|mieszane|Współczesny zwrot do redakcji oraz cytaty; żywy zabieg retoryczny.
rozgorzało|autorskie|Powstanie, uczucie i starcie; także przenośne użycie.
służebnic|mieszane|Opis instytucji religijnych i nazwa zgromadzenia; ocena zależy od znaczenia i nazwy.
inszą|stylizacja|Cytaty i historyczna receptura; odczytane konteksty nie dowodzą neutralnego wariantu inna.
wojaż|autorskie|Podróż wojskowa, wyjazd firmowy i opis podróży; żywe użycia książkowe/żartobliwe.
kurtyzanę|mieszane|Reportaż o procedurach hotelowych, opis roli scenicznej i historyczny dialog.
denominacja|mieszane|Waluta oraz wyznanie; licznik jednego lematu obejmuje różne znaczenia.
familiach|mieszane|Znaczenie nazwiska/rodziny i współczesne rodziny morsujących; data wydania 2021 nie jest datą pierwszej publikacji.
odstawce|autorskie|Statek, polityka i sytuacja postaci; głównie utrwalone wyrażenie.
preferująca|autorskie|Tekst o polityce, proza i organizacja nauki; zwykłe użycie imiesłowu.
zwierzchnością|mieszane|Zwierzchnictwo kościelne, dawny cytat, przenośny opis zachowania.
nierządnicę|mieszane|Objaśnienie greckiego słowa i silnie nacechowane dialogi; nie dowodzi neutralności.
kajet|mieszane|Żartobliwy komentarz sportowy oraz proza; WSJP oznacza leksem jako przestarzały.
zbójca|historyczne|Pierwsze 3 trafienia w jednej powieści historycznej; silna koncentracja źródła.
lazarety|historyczne|Opisy historii szpitali wojskowych, w tym cytat.
niezbędników|autorskie|Przybory fajkowe, fotograficzne i przenośna potrzeba; różne żywe znaczenia.
klasztora|frazeologia|Dwa użycia stylizowane i trzy przysłowiowe; SGJP oznacza tę końcówkę jako dawną.
rarytasu|mieszane|Nazwa przysmaku oraz dwukrotnie składnik tytułu publikacji.
poniektórym|mieszane|Przytoczenie i autorska narracja; żywy nacechowany zaimek.
warzonych|autorskie|Piwo, zioła i miód pitny; należy rozdzielić znaczenia gotowania i produkcji napojów.
sierocińcem|mieszane|Historia ewakuacji oraz dialog powieściowy; współczesne użycie przy przest. w WSJP.
siedm|stylizacja|Baśń, dawny cytat i Matka Makryna; dawny wariant liczebnika.
kajety|historyczne|Reportaż i proza o dawnych realiach; sama data nowej książki nie wystarcza.
solennym|autorskie|Opis śpiewu, zapewnienia i stylu akademickiego; książkowe użycia.
oberżę|historyczne|Dawne podróże, proza historyczna i biografia artysty.
bursę|mieszane|Internat oraz pojemnik liturgiczny; ten sam napis nie dowodzi tego samego znaczenia.
gojem|mieszane|Opis religijny, proza i współczesne porównanie; nacechowanie nie równa się dawności.
diariuszu|autorskie|Krytyka literacka i opis dziennika; żywe użycie książkowe.
marnotrawne|mieszane|Dialog i analityczny opis eksperymentów/potrzeb; nie tylko przypowieść.
monastyrze|mieszane|Powieść historyczna i współczesny reportaż podróżny.
oberża|mieszane|Tytuł filmu oraz opis współczesnego lokalu i historii domu.
mokradle|autorskie|Cytat poezji, współczesny reportaż z quadem i proza; liczba pojedyncza ma realne użycie.
szacownemu|autorskie|Współczesny komentarz i dialogi; nacechowanie grzecznościowe/ironiczne.
pachołkowie|mieszane|Historyczne realia oraz pogardliwy opis pomocników.
sztorcem|mieszane|Opis autorski i dwa cytaty poezji; nie utożsamiać z całym paradygmatem sztorc.
rarytasami|mieszane|Lasy, kulinarny cytat i przedmioty antykwaryczne; żywa metafora.
marnotrawnych|autorskie|Religijne odwołanie, potoczna obelga i przenośny powrót.
konkludowała|autorskie|Czasownik w narracji komentującej cudzą wypowiedź; cytowany jest wniosek, nie sama forma czasownika.
kinematografów|cytaty|Pierwsze 3 trafienia w dawnych przytoczeniach; brak zwykłego autorskiego użycia w tej części.
donacje|autorskie|Historyczne nadania i darowizny do instytucji; potencjalnie różne zakresy znaczenia.
marnotrawna|autorskie|Metafora pamięci i współczesna córka marnotrawna.
pomsta|cytaty|Pierwsze 3 trafienia powtarzają biblijną formułę w jednej powieści.
wysługę|frazeologia|Współczesne i historyczne świadczenia za wysługę lat.
zbój|autorskie|Opis postaci i metafora zabawki; wyraz ekspresywny.
letnisk|mieszane|Opis dawnych miejsc wypoczynku i cytowane rozkłady komunikacji.
atencja|autorskie|Dziennik podróży i polityka strategiczna; uwaga/szacunek.
ócz|mieszane|Cytaty i nacechowana narracja; źródłowo dawny wariant oczu, nie dowód neutralnej odmiany.
admiratorem|autorskie|Opisy współczesnych i historycznych zwolenników; rejestr książkowy.
wyedukowani|autorskie|Współczesne grupy społeczne i pracownicy.
desperację|mieszane|Dawne przytoczenie oraz współczesny opis migrantów i filozofii.
bębniarzy|autorskie|Koncert, wspomnienie muzyków oraz proza.
wynegocjowanym|autorskie|Polityka i opis warunków; zwykła forma imiesłowu.
pryncypiami|autorskie|Zasady polityczne, religijne i moralne; rejestr książkowy.
włościanie|historyczne|Historia polowań i dziesięcin oraz dawny cytat.
monastyczne|historyczne|Autorski opis historii religii i tytuł reguł; nie dawna fleksja.
powiadała|autorskie|Wprowadzenie cudzej wypowiedzi i legenda; żywy czasownik narracji.
obyczajność|mieszane|Autorski opis prawa i kultury oraz dawny antysemicki cytat.
bębniarze|autorskie|Muzycy we współczesnym reportażu i recenzji, także tag artykułu.
wolontariacką|autorskie|Kampania i praca społeczna; wyraźne użycia współczesne.
zapowiednika|autorskie|Specjalistyczny opis rezerwatu; 3 pierwsze trafienia w jednym artykule.
wynegocjowaniu|autorskie|Umowa z wydawcą, polityka i bezpieczeństwo; zwykły odsłownik.
cześci|blad_lub_cytat|Wszystkie 5: cztery prawdopodobne błędy zapisu części i tytuł dawnego wiersza; automatyczna anotacja cześć zaciera różnicę.
władna|autorskie|Uprawnienia instytucji oraz przenośne możliwości poezji/postaci.
zelotów|mieszane|Współczesna metafora żarliwości i historyczne stronnictwo.
jagnięcinę|autorskie|Restauracja, zakupy i gotowanie; zwykła współczesna nazwa mięsa.
reintegrację|autorskie|Współczesna polityka postsowiecka; termin specjalistyczny.
pierworodnej|mieszane|Pierwsza córka i przenośne znaczenie pierwotności.
szczętu|frazeologia|Utrwalone do szczętu; brak dowodu całej odmiany rzeczownika.
maluczkimi|mieszane|Religijna metafora i opis pogardy społecznej; żywy nacechowany wyraz.
atencji|autorskie|Szacunek/uwaga w eseju, opisie życia i polityce.
surdutach|mieszane|Dawne ubrania, poezja i proza historyczna.
nominuje|autorskie|Nagroda architektoniczna, antysemicka metafora i nagrody muzyczne; zwykłe użycie czasownika.
konfuzja|autorskie|Zdezorientowanie autora oraz konflikt polityczny.
zeloty|mieszane|Współczesny aktywista technologiczny i historyczne stronnictwo.
sotnie|mieszane|Współczesne zorganizowane grupy i opisy działań UPA.
atencję|autorskie|Uwaga strategiczna/militarna i okazywanie względów.
dystrykt|mieszane|Okupacyjny podział i współczesny rejon kultury oraz administracja zagraniczna.
napitkiem|autorskie|Nacechowana nazwa napoju; także opis literatury.
salonki|mieszane|Scena filmowa, współczesny zapis rozmowy i proza historyczna.
postura|autorskie|Budowa ciała oraz szczególna technika unieruchomienia; różne znaczenia.
utytułowane|autorskie|Nagrody filmowe i sportowe oraz dyplomy; odnowione/rozszerzone znaczenia.
forpocztę|autorskie|Przenośne opisy organizacji i przyrody oraz oddział wojskowy.
naście|autorskie|Potoczny opis liczby lat w wywiadzie, podziękowaniu i reportażu.
forpoczta|autorskie|Przenośne użycie w polityce i opisie przyrody.
destynacja|mieszane|Dwa metajęzykowe przytoczenia oraz autorskie użycie; samo omawianie wyrazu nie wystarczy.
spękane|autorskie|Opis ścian, dzieł i skóry; zwykły imiesłów.
guwernantką|historyczne|Biografie i dawna edukacja; wiek instytucji oddzielny od współczesności nazwy.
guwernantek|historyczne|Historia cukru, biografia i dawna edukacja.
mezalianse|autorskie|Rodzinne zdarzenia i żartobliwe porównanie par; żywe użycie przenośne.
uzurpację|autorskie|Rozważania o przyrodzie i sporze narodowym; rejestr książkowy.
możnego|historyczne|Rody historyczne i opis społeczny; nie dowodzi neutralności współczesnego tytułu.
insurekcyjnej|autorskie|Krytyka kultury i współczesna polityka historyczna.
edukować|autorskie|Kultura, zdrowie i instytucje; żywe użycie.
okazjonalnie|autorskie|Wystawianie sztuk, palenie i przesył gazu; zwykły przysłówek.
ubezpieczyciel|autorskie|Ubezpieczenie podróży, firma i rozliczenie świadczenia.
skarbówka|autorskie|Potoczna nazwa urzędu w autorskich tekstach.
negocjatorów|autorskie|Opisy rokowań; historia zdarzeń nie czyni odmiany dawną.
konfuzji|autorskie|Żywe użycie książkowe w kilku kontekstach.
pospołu|mieszane|Dawny cytat i autorskie narracje; żywe użycie książkowe.
fantazmatem|autorskie|Wszystkie pierwsze 3 w jednym eseju; specjalistyczny rejestr.
fantazmatów|autorskie|Eseje o sztuce i literaturze.
pryncypiów|autorskie|Zasady polityczne/społeczne; rejestr książkowy.
umór|frazeologia|Na umór: zwykłe narracje i cytat; nie do umoru i nie dowód umorach.
cykliści|mieszane|Historia wojska/sportu i współczesny komentarz polityczny.
preferowany|autorskie|Sztuka, kultura i osobiste upodobania; żywy imiesłów.
familii|autorskie|Rodzina w biografii i opisie literackim; człon tej samej rodziny co odrzucone familia.
szata|autorskie|Oprawa książki, ubiór i metafora wina.
dyktatowi|autorskie|Polityka i zależność artystyczna; różne dziedziny.
proweniencji|autorskie|Pochodzenie polityczne i literackie; książkowość.
dostawczym|autorskie|Samochód w reportażu, poradniku i prozie.
wieczerzy|mieszane|Biblijne odniesienia oraz współczesny posiłek w reportażu.
wynegocjować|autorskie|Polityka i zakup urządzenia; zwykły czasownik.
gawiedź|autorskie|Nacechowana nazwa grupy w historii, reportażu i wspomnieniu.
preferowanych|autorskie|Marketing, polityka i gospodarka; zwykły imiesłów.
rozpuku|frazeologia|Do rozpuku w żywej narracji; nie dowód swobodnego rzeczownika.
sek|obcy_dowod|10 odczytanych: 8 skrótów sekund i 2 urwane wyrazy. Żaden nie dowodzi rzeczownika przyjmowanego w bazie. Nie oceniono pozostałych 293 trafień.
dystryktu|historyczne|3 pierwsze w jednym dokumencie o okupacji; nie dowodzą całego zakresu współczesnego leksemu.
przekąsem|frazeologia|Z przekąsem w autorskiej narracji; żywe utrwalone użycie.
szatę|mieszane|Metafora, ubiór religijny i historyczna opowieść.
włościach|mieszane|Opis malarstwa, biografii i literatury; rejestr książkowy/historyczny.
adwersarza|autorskie|Sztuka i polityka; żywe użycie książkowe.
zasadny|autorskie|Ocena lęku i argumentu; zwykły przymiotnik.
ekscytacja|autorskie|Stan poznawczy i relacje; ta sama rodzina co odrzucone ekscytacją.
doradztwem|autorskie|Inwestycje, polityka i kultura.
sklepikarz|mieszane|Zwykłe opisy osób i dawny cytat.
edukowanie|autorskie|Historia idei, współczesna edukacja i zdrowie.
potańcówki|mieszane|Wspomnienia, cytat i opis lokalu.
obliguje|autorskie|Prawo i zobowiązania umowne; żywy czasownik.
schadzek|autorskie|Spotkania miłosne i opis literatury.
kurortach|autorskie|Porównanie, historia handlu i współczesny reportaż.
finalny|autorskie|Smak, strategia i historia instytucji; żywy przymiotnik.
szacownych|autorskie|Komentarz o lekarzach, dawne postaci i budowle; nie tylko cytaty.
garsonierę|autorskie|Współczesne mieszkanie oraz opis rynku historycznego.
opierunku|frazeologia|Wikt i opierunek w kilku narracjach; nie dowodzi swobodnego pełnego paradygmatu.
zagustował|autorskie|Współczesna polityka, wspomnienie i dialog.
pojmano|mieszane|Historia i współczesne porwanie w Syrii w 2013.
przywdziania|autorskie|Strój, proza i koszulka reprezentacji; żywe książkowe użycie.
hulaką|mieszane|Biografia, dawny cytat i opis postaci; ekspresywność.
dramę|mieszane|Konflikt pracowniczy, religijne zdarzenie i ćwiczenie teatralne; odnowione znaczenia.
frukta|autorskie|Korzyści i owoce w eseju; świadomie nacechowane użycie.
glanc|frazeologia|Na glanc w zwykłej narracji i dialogu.
sztobrów|autorskie|3 pierwsze w jednym poradniku uprawy; współczesny termin fachowy.
natenczas|autorskie|Nacechowana autorska narracja, także opis ochrony przyrody; nie tylko dawny cytat.
upakowanych|autorskie|Współczesny opis anatomii; zwykły imiesłów.
prowadzać|mieszane|Dawny cytat i współczesna narracja o osobach i zwierzęciu.
pojazdowej|autorskie|Mechanika, opinia sądowa i technika; żywy termin.
zafrasowany|autorskie|Postać, klient i piłkarz; autorskie określenie stanu.
ferowania|frazeologia|Ferowanie sądów/wyroków w autorskich analizach.
nawarzył|frazeologia|Nawarzyć piwa jako metafora problemu; rozdzielony aglutynant w jednym wyniku.
guwerner|mieszane|Historia oraz współczesny dialog powieściowy; potrzebne rozstrzygnięcie zakresu znaczenia.
harcówki|autorskie|Harcerstwo, powieść i pamiątka wyprawy; współczesna instytucja.
rzyć|cytaty|Odczytane fragmenty to list/wiersz i metajęzykowe omówienie; regionalizm nie jest sam w sobie zakazem.
sposobiła|mieszane|Autorski opis pracy i historii oraz stylizacja; rozdzielone -m w konkordancji.
ruchawka|mieszane|Historia i metajęzykowy komentarz; współczesność neutralnego znaczenia nieustalona.
warzyć|mieszane|Opis gotowania oraz dawne cytaty/realia; rozdzielić od warzenia piwa dziś.
giezła|mieszane|Strój kelnerów i proza historyczna/fantasy; dawny przedmiot nadal można nazywać.
podołku|autorskie|Telefon i opis pozycji ciała, obok dawnego cytatu; żywa forma.
suweniry|autorskie|Esej, współczesne podróże i proza historyczna.
aeroplany|historyczne|Cytat i proza o dawnych samolotach; nacechowana dawna nazwa.
aktuariusz|autorskie|Ubezpieczenia i zawody regulowane; mocny dowód żywego fachowego znaczenia.
spożytkuje|autorskie|Pieniądze i jedzenie; zwykła forma czasownika.
półsiostry|autorskie|Wszystkie 3 w jednym reportażu o ustalaniu pokrewieństwa.
szewronu|autorskie|Współczesne logo samochodu; może być inne znaczenie niż dawne oznaczenie munduru.
przekupniów|mieszane|Metafora turystów, Biblia i opis targu.
moderowana|autorskie|Proces polityczny, obyczaj i współczesna dyskusja; żywy imiesłów.
przywdziewał|autorskie|Strój i metafora; jeden wynik z odłączonym -em.
dobywał|mieszane|Szabla, dźwięk i zapach; inne zakresy znaczenia.
ubogaci|autorskie|Żart, dialog o twórczości i komentarz o dziecku; żywe nacechowane użycie.
zdradliwie|mieszane|Autorskie opisy i dawny cytat; przysłówek żywy.
zamtuz|mieszane|Metajęzykowe wyliczenie i proza historyczna; brak neutralnego użycia w tej części.
aeroplanów|historyczne|Biografia, historyczne konstrukcje samolotów i proza.
żeż|obcy_dowod|10 trafień partykuły/wykrzyknienia, nie rozkaźnika dawnego żec, którego dotyczy analizowany kandydat.
aliści|mieszane|Dawny styl listu i współczesny komentarz literacki; nie da się zrównać każdego użycia z cytatem.
desperacja|autorskie|Współczesne eseje i biografia; żywe znaczenie rozpaczy.
dinozaur|autorskie|Porównanie oraz metafora człowieka z minionej epoki; nie dowodzi dawności leksemu.
dżdżu|frazeologia|Jak kania dżdżu w żywej prozie niefikcjonalnej; nie dowodzi swobodnego paradygmatu deszcz.
familia|mieszane|Dwa polskie użycia rodziny oraz cytat hiszpański; napis nie wystarcza.
generyczny|autorskie|3 trafienia: proza i dwa teksty informatyczne; żywe fachowe/przenośne użycia.
industrialny|autorskie|Esej historyczny i współczesny krajobraz; znaczenie przemysłowy.
iże|stylizacja|Pierwsze 3 trafienia z jednej powieści; nie dowodzą neutralnego współczesnego spójnika.
jakoż|mieszane|Dawny list oraz dwie autorskie wypowiedzi eseistyczne; źródła nie pozwalają mówić wyłącznie o cytatach.
kalkulatorzy|historyczne|Jedno wyliczenie dawnego personelu; żywe osobowe znaczenie istnieje osobno w WSJP.
nazad|autorskie|Nacechowana narracja i utrwalone tam/w te i nazad; współczesne użycie istnieje.
niezbędnik|autorskie|Narzędzie fajkowe, wyposażenie turystyczne i zbiór notatek.
odzienie|autorskie|Opis strojów religijnych i szkolnych; dawna etykieta WSJP nie równa się brakowi użycia.
surdut|mieszane|Historyczny strój, kostium sceniczny i współczesne wspomnienie muzyka.
trzykroć|mieszane|Dwa cytaty poezji oraz żartobliwe autorskie użycie.
wolontariacki|autorskie|Dwa trafienia jednego reportażu o współczesnej Ukrainie.
'''

notes = {}
for line in NOTES.strip().splitlines():
    w, category, note = line.split('|', 2)
    assert w not in notes
    notes[w] = (category, note)
raw = json.loads((ROOT/'tmp/research-issue4/kwjp-live-raw.json').read_text())
sample = json.loads((OUT/'sample-forms.json').read_text())['cases']
sample_map = {x['word']: x['stratum'] for x in sample}
accepted = set(json.loads((OUT/'current-override.json').read_text())['sample'])
outside = {x['word'] for x in json.loads((OUT/'controls.json').read_text())['rejected_outside_lemma30_with_nf_evidence']}
review = []
extended = {'sek', 'cześci', 'żeż', 'klasztora', 'ośmset', 'księżny', 'wiela'}
for x in raw:
    w = x['word']
    assert x['total'] is not None
    if x['total']:
        assert w in notes, w
        category, note = notes[w]
    else:
        category, note = 'brak_trafien', 'Wyszukiwarka nie zwróciła dokładnego napisu. To brak dowodu w tej sondzie, nie rozstrzygnięcie dopuszczalności.'
    inspected = x['rows'][:10 if w in extended else 3]
    review.append({'word': w, 'lane': sample_map.get(w, 'current_accepted' if w in accepted else 'outside_lemma30' if w in outside else 'diagnostic'),
                   'total_live': x['total'], 'inspected': len(inspected),
                   'documents_inspected': sorted({r['document_id'] for r in inspected}),
                   'category': category, 'note': note, 'eligibility_decision': None, 'url': x['url']})
assert set(notes) == {x['word'] for x in raw if x['total']}, set(notes)-{x['word'] for x in raw}
summary = {'queries':len(review), 'positive_queries':sum(x['total_live']>0 for x in review),
           'inspected_contexts':sum(x['inspected'] for x in review),
           'sample_strata':{s: {'sample':sum(x['lane']==s for x in review), 'positive':sum(x['lane']==s and x['total_live']>0 for x in review)} for s in sorted(set(sample_map.values()))}}
(OUT/'live-review.json').write_text(json.dumps({'method':'Jeden badacz. Wszystkie 257 odpowiedzi; pierwsze 3 konteksty każdej niepustej odpowiedzi, 7 jawnych rozszerzeń do 10. Kolejność wyszukiwarki nie jest losowa. Ocena dotyczy użycia, nie dopuszczalności.', 'summary':summary,'cases':review},ensure_ascii=False,indent=2)+'\n')
print(summary)
