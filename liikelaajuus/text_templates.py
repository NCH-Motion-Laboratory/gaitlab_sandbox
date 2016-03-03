# -*- coding: utf-8 -*-
"""
Created on Tue Mar 01 12:37:26 2016

Report text is delimited into sections. If a section has fields (variables), 
at least one of them must have corresponding data, otherwise the section 
will not be printed. Sections without variables are always printed.

@author: jussi (jnu@iki.fi)
"""

# section delimiter
delimiter = '#' 

# raw report text
report_ = u"""

Patient code: {TiedotID}
Patient name: {TiedotNimi}
Social security number: {TiedotHetu}
Diagnosis: {TiedotDiag}
Date of gait analysis: {TiedotPvm} 

[Tulosyy]
Tehtiin kävelyanalyysi-tutkimus 3D liikeanalyysilaitteistolla sekä liikerata- ja manuaaliset lihasvoimamittaukset 
Tehdyt toimenpiteet..
Apuvälineet..

[Testaus- ja arviointitulokset]
Seisoma-asento:
Kävely:

Kävelyanalyysin pohjalta kävelyn ongelmia/johtopäätökset ovat:

NIVELTEN PASSIIVISET LIIKELAAJUUDET (oikea/vasen):

LONKKA: #Thomasin testi (vapaasti) {LonkkaEkstensioVapOik}°/{LonkkaEkstensioVapVas}°,# Thomasin testi (avustettuna) {LonkkaEkstensioAvOik}°/{LonkkaEkstensioAvVas}°#, Thomasin testi (polvi 90°) {LonkkaEkstensioPolvi90Oik}°/{LonkkaEkstensioPolvi90Vas}°. 
Koukistus {LonkkaFleksioOik}°/{LonkkaFleksioVas}°. Loitonnus (lonkka 0°, polvi 90°) {LonkkaAbduktioLonkka0Polvi90Oik}°/{LonkkaAbduktioLonkka0Polvi90Vas}°, loitonnus (lonkka 0°, polvi 0°) {LonkkaAbduktioLonkka0Oik}°/{LonkkaAbduktioLonkka0Vas}°,
loitonnus (lonkka 90°) {LonkkaAbduktioLonkkaFleksOik}°/{LonkkaAbduktioLonkkaFleksVas}°. Lähennys {LonkkaAdduktioOik}°/{LonkkaAdduktioVas}°. Sisäkierto {LonkkaSisakiertoOik}°/{LonkkaSisakiertoVas}°. Ulkokierto {LonkkaUlkokiertoOik}°/{LonkkaUlkokiertoVas}°.
Kommentit: {cmtLonkka}

['POLVI: Ojennus (vapaasti) {PolviEkstensioVapOik}°/{PolviEkstensioVapVas}°], ojennus (avustettuna) {PolviEkstensioAvOik}°/{PolviEkstensioAvVas}°. Koukistus (vatsamakuu) {LonkkaPolviFleksioVatsamakuuOik}°/{LonkkaPolviFleksioVatsamakuuOik}°, 
koukistus (selinmakuu) {PolviFleksioSelinmakuuOik}°/{PolviFleksioSelinmakuuVas}°. Popliteakulma {PolviPopliteaVastakkLonkka0Oik}°/{PolviPopliteaVastakkLonkka0Vas}°, popliteakulma (true) {csbPolviPopliteaVastakkLonkka90Oik}°/{csbPolviPopliteaVastakkLonkka90Vas}°. 
Kommentit: {cmtPolvi}

NILKKA: Koukistus (polvi 90°) x°/x°, koukistus (polvi 0°) x°/x°. Ojennus x°/x°. 
Kommentit: {cmtNilkka}

AKTIIVISET LIIKELAAJUUDET: 

NILKKA: Koukistus (polvi 90°) x°/x°, koukistus (polvi 0°) x°/x°. Nilkan ojennus x°/x°.
Kommentit:

LUISET VIRHEASENNOT: 
Lonkan anteversio x°/x°. Jalkaterä-reisi kulma x°/x°, jalkaterän etu- takaosan kulma x°/x°. 
Bimalleoli -akseli x°/x°, 2nd toe test x°/x°.  Patella alta xcm/xcm. 
Kommentit: 

MUITA MITTAUKSIA:
Extensor lag x°/x°. Confusion test x/x. Ober test x°/x°. Tasapaino: yhdellä jalalla seisominen xs/xs.

JALKATERÄ KUORMITTAMATTOMANA (+ = lievä, ++ = kohtalainen, +++ = voimakas): 
Subtalar neutraali asento x/x. Kantaluun asento x/x. Takaosan liike eversioon x/x. 
Takaosan liike inversioon x/x. Med.holvikaari x/x. Keskiosan liike x/x. Etuosan asento 1 x/x. 
Etuosan asento 2 x/x. 1. säde x/x. 1 MTP dorsifleksio x°/x°. Vaivasenluu x/x.  Kovettumat x/x.
Kommentit:

JALKATERÄ KUORMITETTUNA (+ = lievä, ++ = kohtalainen, +++ = voimakas):
Takaosan (kantaluun) asento x/x. Keskiosan asento x/x. Etuosan asento 1 x/x, etuosan asento 2 x/x.
Coleman’s block test x/x. 
Kommentit:

ALARAAJOJEN SPASTISUUS:

CATCH: Lonkan adduktorit x°/x°. Hamstringit x°/x°. Rectus femorikset x°/x°. Soleukset x°/x°, (klonus x/x). 
Gastrocnemiukset x°/x°, (klonus x/x).
Kommentit:

MODIFIED ASHWORTH: Lonkan koukistajat x°/x°, lonkan lähentäjät x°/x°, hamstringit x°/x°, rectus femoris x°/x°, 
tibialis posterior x°/x°, soleus x°/x°, gastrocnemius x°/x°. 
Kommentit:

MANUAALISESTI MITATUT LIHASVOIMAT (oikea/vasen):
Asteikko: 0-5, missä 5 on vahvin ja 3 voittaa painovoiman: Lonkan ojennus (polvi 0°) x/x, 
lonkan ojennus (polvi 90°) x/x. Lonkan koukistus x/x. Loitonnus x/x. Lähennys x/x. Lonkan ulkokierto x/x. 
Lonkan sisäkierto x/x. Polven ojennus x/x. Polven koukistus x/x. Nilkan koukistus x/x. Nilkan ojennus x/x. 
Inversio x/x. Eversio x/x. Isovarpaan ojennus x/x. Isovarpaan koukistus x/x. Varpaiden (2-5) ojennus x/x. 
Varpaiden (2-5) koukistus x/x. Suorat vatsalihakset x, vinot vatsalihakset x/x. Selkälihakset x. 
Kommentit:

[Suunnitelma/pohdinta]

(Johtopäätökset)
Pääpulmat..
Suositukset..


, fysioterapeutti
Liikelaboratorio
HYKS, Lastenlinna

Jakelu:

Kotiin 2kpl, joista toinen kuntouttavalle fysioterapeutille.
.LL14

"""


report = report_.split(delimiter)

