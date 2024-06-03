ROUTER_PROMPT = """
**INSTRUKCIJE:**
Tvoj zadatak je da na osnovu datog pitanja korisnika odlucis koji zakon ili zakoni su potrebni da bi se odgovorilo na korisnikovo pitanje.
Ponudjeni zakoni i njihova objasnjenja su sledeci:
- zakon_o_radu
 - Zakon o radu Republike Srbije reguliše radne odnose između zaposlenih i poslodavaca. Definiše prava i obaveze obe strane, uključujući radno vreme, odmore i druga odsustva i uslove za otkaz ugovora o radu. Zakon takođe obuhvata pravila vezana za ugovore o radu, minimalnu zaradu, kao i mere zaštite na radu. Osim toga, predviđa mehanizme za rešavanje radnih sporova.
- zakon_o_porezu_na_dohodak_gradjana
 - Zakon o porezu na dohodak građana reguliše način oporezivanja porezom na dohodak građana, u šta spadaju zarada, prihodi od samostalnih delatnosti, prihodi od kapitala, nepokretnosti i slično. Zakon detaljno opisuje koji sve prihodi su oporezivi ovim porezom, kao i poreske stope, osnovice, određena poreska oslobođenja i olakšice za određene kategorije građana.
- zakon_o_zastiti_podataka_o_licnosti
 - Zakon o zaštiti podataka o ličnosti štiti prava građana na privatnost njihovih ličnih podataka. Obavezuje sve organizacije koje obrađuju lične podatke da to čine transparentno, zakonito i u skladu sa definisanim svrhama. Zakon definiše prava lica na pristup, ispravku, brisanje i prenos svojih podataka o ličnosti. Takođe, ustanovljava Poverenika za informacije od javnog značaja i zaštitu podataka o ličnosti kao regulatorno telo koje nadzire primenu zakona.
- zakon_o_zastiti_potrosaca
 - Zakon o zaštiti potrošača osigurava da potrošači u Srbiji imaju prava na sigurnost i kvalitet proizvoda i usluga. Zakon propisuje obaveze trgovaca u pogledu pravilnog informisanja potrošača o proizvodima, uslugama, cenama i pravu na reklamaciju. Takođe, uključuje prava potrošača na odustanak od kupovine unutar određenog roka i prava u slučaju neispravnosti proizvoda kao i prava koja su vezana za ugovore na daljinu. 
- porodicni_zakon
 - Porodični zakon reguliše pravne odnose unutar porodice, uključujući brak, roditeljstvo, starateljstvo, hraniteljstvo i usvojenje. Zakon definiše prava i obaveze bračnih partnera, kao i prava dece i roditeljske odgovornosti. Takođe se bavi pitanjima nasleđivanja i alimentacije. 
- nema_zakona
 - Korisnikovo pitanje ne odgovara ni jednom zakonu.

**FORMAT ODGOVORA:**
- Odgovor vratiti u JSON formatu koji moze da se učita sa json.loads().
- Imena zakona mogu biti samo sledeca: zakon_o_radu, zakon_o_porezu_na_dohodak_gradjana, zakon_o_zastiti_podataka_o_licnosti, zakon_o_zastiti_potrosaca, porodicni_zakon, nema_zakona.
- Jedno pitanje korisnika moze da se odnosi na vise zakona.
- Vrati zakone koji mogu da pomognu prilikom generisanja odgovora.
- Ukoliko korisnikovo pitanje ne odgovara ni jednom zakonu vrati listu sa generickim stringom: ["nema_zakona"].

**PRIMER ODGOVORA:**
{{
    response: ["ime_zakona"]
}}
"""

USER_QUERY = """
**PITANJE KORISINKA:**
{query}
"""

ROUTER_PROMPT_ENG = """
Your task is to decide which law or laws are needed to answer the user's question based on the given question.
The provided laws and their explanations are as follows:
- labor_law
 - The Labor Law of the Republic of Serbia regulates labor relations between employees and employers. It defines the rights and obligations of both parties, including working hours, leaves, and conditions for termination of employment contracts. The law also covers rules related to employment contracts, minimum wage, and workplace safety measures. Additionally, it provides mechanisms for resolving labor disputes.
- personal_income_tax_law
 - The Personal Income Tax Law regulates the taxation of citizens' income, including salaries, self-employment income, capital income, real estate income, and more. The law details which incomes are taxable, as well as tax rates, bases, certain tax exemptions, and reliefs for specific categories of citizens.
- personal_data_protection_law
 - The Personal Data Protection Law protects citizens' rights to the privacy of their personal data. It obligates all organizations processing personal data to do so transparently, legally, and in accordance with defined purposes. The law defines the rights of individuals to access, correct, delete, and transfer their personal data. It also establishes the Commissioner for Information of Public Importance and Personal Data Protection as the regulatory body overseeing the law's implementation.
- consumer_protection_law
 - The Consumer Protection Law ensures that consumers in Serbia have rights to the safety and quality of products and services. The law prescribes the obligations of traders regarding the proper information of consumers about products, services, prices, and the right to file complaints. It also includes consumers' rights to withdraw from a purchase within a specified period and rights in case of defective products as well as rights related to distance contracts.
- family_law
 - The Family Law regulates legal relations within the family, including marriage, parenthood, guardianship, foster care, and adoption. The law defines the rights and obligations of spouses, as well as children's rights and parental responsibilities. It also addresses issues of inheritance and alimony.
- no_law
 - The user's question does not correspond to any law.

**RESPONSE FORMAT:**
- Return the response in JSON format that can be loaded with json.loads().
- The names of the laws can only be the following: labor_law, personal_income_tax_law, personal_data_protection_law, consumer_protection_law, family_law, no_law.
- A user's question can relate to multiple laws.
- Return the laws that can help in generating the answer.
- If the user's question does not correspond to any law, return a list with the generic string: ["no_law"].
- Example JSON response:

{{
    "response": ["law_name"]
}}

**USER'S QUESTION:**
{query}
"""


DEFAULT_ROUTER_RESPONSE = "nema_zakona"
