ROUTER_PROMPT = """
Tvoj zadatak je da na osnovu datog pitanja korisnika odlucis koji zakon ili zakoni su potrebni da bi se odgovorilo na korisnikovo pitanje.
Ponudjeni zakoni i njihova objasnjenja su sledeci:
- zakon_o_radu
 - Zakon o radu Republike Srbije reguliše radne odnose između zaposlenih i poslodavaca. Definiše prava i obaveze obe strane, uključujući radno vreme, odmore i druga odsustva i uslove za otkaz ugovora o radu. Zakon takođe obuhvata pravila vezana za ugovore o radu, minimalnu zaradu, kao i mere zaštite na radu. Osim toga, predviđa mehanizme za rešavanje radnih sporova.
- zakon_o_porezu_na_dohodak_gradjana
 - Zakon o porezu na dohodak građana reguliše način oporezivanja porezom na dohodak građana, u šta spadaju zarada, prihodi od samostalnih delatnosti, prihodi od kapitala, nepokretnosti i slično. Zakon detaljno opisuje koji sve prihodi su oporezivi ovim porezom, kao i poreske stope, osnovice, određena poreska oslobođenja i olakšice za određene kategorije građana.
- zakon_o_zastiti_podataka_o_licnosti
 - Zakon o zaštiti podataka o ličnosti štiti prava građana na privatnost njihovih ličnih podataka. Obavezuje sve organizacije koje obrađuju lične podatke da to čine transparentno, zakonito i u skladu sa definisanim svrhama. Zakon definiše prava lica na pristup, ispravku, brisanje i prenos svojih podataka o ličnosti. Takođe, ustanovljava Poverenika za informacije od javnog značaja i zaštitu podataka o ličnosti kao regulatorno telo koje nadzire primenu zakona.
- zakon_o_zastiti_potrosaca
 - Zakon o zaštiti potrošača osigurava da potrošači u Srbiji imaju prava na sigurnost i kvalitet proizvoda i usluga. Zakon propisuje obaveze trgovaca u pogledu pravilnog informisanja potrošača o proizvodima, uslugama, cenama i pravu na reklamaciju. Takođe, uključuje prava potrošača na odustanak od kupovine unutar određenog roka i prava u slučaju neispravnosti proizvoda. 
- porodicni_zakon
 - Porodični zakon reguliše pravne odnose unutar porodice, uključujući brak, roditeljstvo, starateljstvo, hraniteljstvo i usvojenje. Zakon definiše prava i obaveze bračnih partnera, kao i prava dece i roditeljske odgovornosti. Takođe se bavi pitanjima nasleđivanja i alimentacije. 
- nema_zakona
 - Korisnikovo pitanje ne odgovara ni jednom zakonu.

**FORMAT ODGOVORA:**
- Odgovor vratiti u JSON formatu koji moze da se ucita sa json.loads().
- Imena zakona mogu biti samo sledeca: zakon_o_radu, zakon_o_porezu_na_dohodak_gradjana, zakon_o_zastiti_podataka_o_licnosti, zakon_o_zastiti_potrosaca, porodicni_zakon, nema_zakona.
- Jedno pitanje korisnika moze da se odnosi na vise zakona.
- Ukoliko korisnikovo pitanje ne odgovara ni jednom zakonu vrati listu sa generickim stringom: ["nema_zakona"].
- Primer JSON odgovora:

{{
    response: ["ime_zakona"]
}}

**PITANJE KORISINKA:**
{query}
"""

DEFAULT_ROUTER_RESPONSE = "nema_zakona"
