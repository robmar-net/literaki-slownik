"""Jawne notatki ręcznej oceny konkordancji; nie jest to klasyfikator języka."""
import collections
import json
from pathlib import Path

TASK = Path(__file__).resolve().parents[1]
ROOT = TASK.parents[3]
OUT = TASK / 'analysis/findings/round3'
TMP = ROOT / 'tmp/research-issue4'

def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')

UNSUPPORTED = {
 'bad':'Angielskie wyrażenia i cytaty; nie potwierdzają polskiego dawnego rzeczownika bad.',
 'dag':'Jednostka masy w przepisach; nie dopełniacz liczby mnogiej rzeczownika daga.',
 'dyr':'Skrót dyrektora; nie dawne wykrzyknienie.',
 'reż':'Skrót reżysera; nie rzeczownik oznaczający żyto.',
 'sek':'Osiem skrótów sekund i dwa urwane wyrazy; brak dowodu dawnego rzeczownika.',
 'sie':'Błędne lub gwarowe się, niemiecki zaimek i fragmenty adresów; nie przymiotnik si.',
 'sui':'Łacińskie formuły; nie odmiana suja.',
 'um':'Portugalskie wyrażenia w jednej książce; nie polski dawny rzeczownik.',
 'moko':'Maoryskie tatuaże w jednej książce; nie wołacz od moka. Żywy obcy napis wymaga odrębnej oceny.',
 'wiosenno':'Człon złożenia wiosenno-letni; nie samodzielny przysłówek.',
 'świąteczno':'Człon przymiotników złożonych; nie samodzielny przysłówek.',
 'tem':'Portugalski wyraz, dawne tym i stylizowany zapis poza tem; nie dopełniacz liczby mnogiej tema.',
}
PHRASES = {
 'bakier':'na bakier','ciemku':'po ciemku','kryjomu':'po kryjomu','niemiara':'co niemiara',
 'omacku':'po omacku','opak':'na opak','pastwę':'na pastwę','podzięce':'w podzięce',
 'poliszynela':'tajemnica poliszynela','pomstę':'wołać o pomstę; także nacechowane użycia',
 'poprzek':'w poprzek','przeciwka':'z przeciwka','przekąsem':'z przekąsem',
 'półgłosem':'utrwalony przysłówek półgłosem','rozpuku':'do rozpuku',
 'rozsypce':'w rozsypce / ulec rozsypce','sztok':'w sztok','sztorc':'na sztorc',
 'laty':'przed laty','słowy':'innymi słowy','trosze':'po trosze','ukradkiem':'przysłówkowe ukradkiem',
 'umór':'na umór','ustanku':'bez ustanku','zabój':'na zabój','zowąd':'ni stąd, ni zowąd',
 'wtóre':'po wtóre','sukurs':'sukurs, głównie przyjść w sukurs','asumpt':'dać asumpt',
 'niwie':'na niwie; obok cytatu poetyckiego','pardonu':'bez pardonu',
 'ki':'ki diabeł / ki czort','lubością':'z lubością','kwinkunksie':'w kwinkunksie',
 'podorędziu':'na podorędziu','szczętem':'ze szczętem','szczętu':'do szczętu',
}
UNCERTAIN = {
 'alkowy':'Użycia o dawnym wnętrzu i żartobliwe; dalsza kontrola rejestru i zakresu znaczenia.',
 'bohemy':'Historyczne środowiska artystów; temat historyczny nie przesądza dawności słowa.',
 'cyklistów':'Wybrane użycia dotyczą historycznych formacji; nie rozstrzygają całego zakresu.',
 'cykliści':'Jest dzisiejsze użycie o rowerzystach, ale drugi kontekst historyczny; potrzebna kontrola rejestru.',
 'dystryktu':'Pierwsza strona skupiona w jednej książce z historycznym cytatem.',
 'goj':'Użycia współczesne, częściowo przytoczenie obcego terminu; zakres do dalszej oceny.',
 'gojów':'Wybrane użycia w historycznych przytoczeniach.',
 'insurekcji':'Dzisiejsza narracja o dawnych powstaniach; potrzebna odrębna ocena rejestru.',
 'karmicieli':'Pierwsza strona skupiona w jednej książce o historycznym zajęciu.',
 'maluczkich':'Współczesne zsubstantywizowane maluczcy; brak podstaw do całego przymiotnika i stopniowania.',
 'możni':'Możni świata lub dawne elity; nie dowodzi czasownika możnić ani wszystkich znaczeń przymiotnika.',
 'możnych':'Użycie rzeczownikowe; nie dowodzi całego zakresu przymiotnika.',
 'nieumiarkowania':'Żywe pojęcie nadmiaru; odrębne mapowanie rzeczownika i czasownika umiarkować.',
 'niewiast':'Cytaty religijne i dawny rejestr; granica stylizacji nierozstrzygnięta.',
 'niewiasta':'Religijne i nacechowane współczesne użycia; granica stylizacji nierozstrzygnięta.',
 'niewiasty':'Jest współczesne ironiczne użycie; nie daje samo decyzji dla całej odmiany.',
 'onych':'Współczesne zsubstantywizowane oni obok dawnej stylizacji; nie dowód dawnego on:A.',
 'pardon':'Przytoczenia obcej formuły grzecznościowej; osobno bez pardonu.',
 'peregrynacji':'Żywe książkowe podróże; zakres pozostaje kandydatem, bez pełnej kontroli odmiany.',
 'pierwej':'Użycie podniosłe obok dawnego cytatu; granica archaizacji do decyzji.',
 'pleban':'Historyczny kontekst i dawne cytaty; rejestr wymaga dalszej oceny.',
 'plebana':'Historyczny kontekst i dawne cytaty; rejestr wymaga dalszej oceny.',
 'potańcówki':'Narracja o dawnych zabawach; nie oznacza automatycznie dawności słowa.',
 'premium':'Współczesny modyfikator jakości/statusu; nie dowodzi dawnego rzeczownika i premiów.',
 'pątnicy':'Dzisiejsza pielgrzymka i proza historyczna; nie dowodzi żeńskiej pątnicy.',
 'pątników':'Pierwsza strona skupiona w jednym przewodniku.',
 'sierociniec':'WSJP również przest.; współczesna narracja nie rozstrzyga konfliktu rejestru.',
 'sierocińca':'WSJP również przest.; współczesna narracja nie rozstrzyga konfliktu rejestru.',
 'sierocińcu':'WSJP również przest.; współczesna narracja nie rozstrzyga konfliktu rejestru.',
 'takowe':'Nacechowany zaimek w dzisiejszej narracji; granica archaizacji do decyzji.',
 'takowego':'Nacechowany zaimek w dzisiejszej narracji; granica archaizacji do decyzji.',
 'takowy':'Nacechowany zaimek w dzisiejszej narracji; granica archaizacji do decyzji.',
 'takowych':'Nacechowany zaimek w dzisiejszej narracji; granica archaizacji do decyzji.',
 'wieczerza':'Dawny opis i tytuł dzieła; sam napis nie potwierdza też czasownika wieczerzać.',
 'wieczerzy':'Występuje dzisiejsza uroczysta kolacja, obok tytułów i historii.',
 'wieczerzę':'Dzisiejsza wieczerza wigilijna, obok tytułu obrazu; potrzebna ocena zakresu.',
 'włości':'Użycie przenośne i historyczna posiadłość; osobno dawna prowincja włość.',
 'włościach':'Użycie przenośne i historyczna posiadłość; osobno dawna prowincja włość.',
 'włościan':'Historyczni chłopi; temat i wiek słowa wymagają rozdzielenia.',
 'wychudzone':'Żywy opis stanu; do sprawdzenia zakres czasownika i usamodzielnionego przymiotnika.',
 'wychudzony':'Żywy opis stanu; do sprawdzenia zakres czasownika i usamodzielnionego przymiotnika.',
 'wymagalności':'Żywy termin; czytnik ma odrębny rzeczownik odprzymiotnikowy. Mapowanie niezamknięte.',
 'zapowiedników':'Pierwsza strona z tego samego artykułu co wcześniejsze zapowiednika.',
 'zaślubin':'Historyczne zdarzenia i przytoczenia; zakres dzisiejszego użycia do oceny.',
 'zaślubiny':'Proza i metafora; zakres dzisiejszego uroczystego rejestru do oceny.',
 'zewnętrzność':'Termin filozoficzny, cytat i narracja; dwa rekordy źródłowe wymagają mapowania.',
 'zgliszcza':'Liczba mnoga nie rozstrzyga pojedynczego zgliszcze.',
 'zgliszczach':'Liczba mnoga nie rozstrzyga pojedynczego zgliszcze.',
 'zwierzchności':'Żywy opis podporządkowania; odrębne hasła źródłowe wymagają mapowania.',
 'zwierzchność':'Żywy opis podporządkowania; odrębne hasła źródłowe wymagają mapowania.',
 'szuwarem':'Jedno trafienie przytaczające dawny opis budynku. Inne znaczenie i źródło niż współczesny opis roślinności w WSJP.',
}
SPECIAL = {
 'ludzko':'Wśród 10 kontekstów są człony złożeń i stare cytaty, ale też samodzielny dzisiejszy przysłówek (wiersze 2, 6–9). Nie wolno odrzucić całego napisu.',
 'łże':'Wśród członów łże-elity itp. jest współczesna forma czasownika łgać. Nie dowodzi rzeczownika łeż.',
 'nader':'Żywy przysłówek/partykuła; nie dowodzi rzeczowników nadra i nadro.',
 'wraz':'Żywy przysłówek/przyimek; nie dowodzi rzeczownika wraz.',
 'utytułowany':'Żywy imiesłów związany z nagrodami; nie dowodzi dawnego samodzielnego rzeczownika.',
 'utytułowanych':'Żywy imiesłów; nie dowodzi dawnych rzeczowników utytułowany/utytułowana.',
 'obcesowo':'Żywy stopień równy; dowód nie rozstrzyga dawnych form stopnia wyższego.',
 'znajomo':'Żywy stopień równy; dowód nie rozstrzyga dawnych form stopnia wyższego.',
 'przystoi':'Żywe bezosobowe przystoi; nie uzasadnia osobowych przystoimy/przystoisz.',
 'odstawkę':'Na odstawkę; nie uzasadnia samodzielnego rzeczownika w całej odmianie.',
 'pryncypium':'Pierwszy tekst przytacza Kanta; drugi zawiera autorskie użycie zasady. Zakres liczby pojedynczej wspiera też WSJP, obok wcześniejszych różnych tekstów z liczbą mnogą.',
}

def selected(rows):
    indices=[]; seen=set()
    for i,r in enumerate(rows):
        if r['document_id'] not in seen:
            seen.add(r['document_id']); indices.append(i)
            if len(indices)==2: break
    return indices

def main():
    raw=json.loads((TMP/'round3-kwjp-raw.json').read_text())
    analyses=json.loads((OUT/'current-analyses.json').read_text())
    byword=collections.defaultdict(list)
    for row in analyses: byword[row[0]].append(row[1:])
    expanded=set(UNSUPPORTED)|{'ludzko','premium','onych','łże'}
    cases=[]
    for r in raw:
        w=r['word']; ix=list(range(len(r['rows']))) if w in expanded else selected(r['rows'])
        status='live_in_selected_contexts'
        note='Wybrane konteksty zawierają autorskie użycie w dzisiejszej narracji; ocena pełnego zakresu rodziny jest osobnym krokiem.'
        if w in UNSUPPORTED: status='accepted_analysis_not_supported';note=UNSUPPORTED[w]
        elif w in PHRASES: status='limited_construction';note='Potwierdzona konstrukcja: '+PHRASES[w]+'. Nie przenosić dowodu na swobodną odmianę rzeczownika.'
        elif w in UNCERTAIN: status='scope_or_register_unresolved';note=UNCERTAIN[w]
        elif w in SPECIAL: status='mixed_scoped_evidence';note=SPECIAL[w]
        elif not ix: status='no_hit';note='Brak wyniku dokładnej formy; nie jest dowodem niepoprawności regularnej odmiany.'
        elif len({r['rows'][i]['document_id'] for i in ix})<2:status='one_document_only';note='Dostępna sonda nie daje użyć w różnych tekstach; ocena wymaga pozostałych dowodów.'
        cases.append({'word':w,'current_dependent':w in byword,'status':status,'note':note,
          'accepted_analyses':byword.get(w,[]),'url':r['url'],'total_hits':r['total'],
          'reviewed_rows':[{'index':i,**{k:r['rows'][i][k] for k in ('document_id','sentence','date','metadata')}} for i in ix]})
    save('context-review.json',{'method':'Pierwsze dwa różne identyfikatory dokumentu w pierwszych 10 trafieniach; 16 wskazanych przypadków: wszystkie pierwsze 10. Dobór celowy, bez estymacji błędu populacji. Jeden badacz.',
      'queries':len(cases),'reviewed_contexts':sum(len(r['reviewed_rows']) for r in cases),
      'expanded_words':sorted(expanded),'current_words':len(byword),'cases':cases})
    save('current-review.json',{'words':len(byword),'status_counts':dict(collections.Counter(r['status'] for r in cases if r['current_dependent'])),
      'unsupported_evidence_words':sorted(UNSUPPORTED),'automatic_removal':False,
      'cases':[r for r in cases if r['current_dependent']]})
    print('contexts',sum(len(r['reviewed_rows']) for r in cases),'current',len(byword))

if __name__=='__main__': main()
