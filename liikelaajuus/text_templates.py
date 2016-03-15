# -*- coding: utf-8 -*-
"""
Created on Tue Mar 01 12:37:26 2016

Template for liikelaajuus report.

Report text is delimited into sections. If a section has fields (variables), 
at least one of them must have corresponding data, otherwise the section 
will not be printed. Sections without variables are always printed.

@author: jussi (jnu@iki.fi)
"""


# section delimiter
delimiter = '#' 

# raw report text
report_ = u"""

LIIKELAAJUUDET JA VOIMAT

#Patient code: {TiedotID}
Patient name: {TiedotNimi}
Social security number: {TiedotHetu}
Diagnosis: {TiedotDiag}
Date of gait analysis: {TiedotPvm} 
#Kommentit: {cmtTiedot}#

ANTROPOMETRISET MITAT:
Alaraajat: {AntropAlaraajaOik} / {AntropAlaraajaVas}
Nilkat: {AntropNilkkaOik} / {AntropNilkkaVas}
Polvet: {AntropPolviOik} / {AntropPolviVas}
Paino: {AntropPaino}
Pituus: {AntropPituus}
SIAS: {AntropSIAS}
#Kommentit: {cmtAntrop}#

#MITTAAJAT:
{TiedotMittaajat}#

[Tulosyy]
Tehtiin kävelyanalyysitutkimus 3D-liikeanalyysilaitteistolla sekä liikerata- ja manuaaliset lihasvoimamittaukset.
Tehdyt toimenpiteet:
Apuvälineet:

[Testaus- ja arviointitulokset]
Seisoma-asento:
Kävely:

Kävelyanalyysin pohjalta kävelyn ongelmia/johtopäätökset ovat:

NIVELTEN PASSIIVISET LIIKELAAJUUDET (oikea/vasen):

LONKKA: #Thomasin testi (vapaasti) {LonkkaEkstensioVapOik}/{LonkkaEkstensioVapVas}. #Thomasin testi (avustettuna) {LonkkaEkstensioAvOik}/{LonkkaEkstensioAvVas}. #Thomasin testi (polvi 90°) {LonkkaEkstensioPolvi90Oik}/{LonkkaEkstensioPolvi90Vas}.#
#Koukistus {LonkkaFleksioOik}/{LonkkaFleksioVas}. #Loitonnus (lonkka 0°, polvi 90°) {LonkkaAbduktioLonkka0Polvi90Oik}/{LonkkaAbduktioLonkka0Polvi90Vas}. #Loitonnus (lonkka 0°, polvi 0°) {LonkkaAbduktioLonkka0Oik}/{LonkkaAbduktioLonkka0Vas}. #
#Loitonnus (lonkka 90°) {LonkkaAbduktioLonkkaFleksOik}/{LonkkaAbduktioLonkkaFleksVas}. #Lähennys {LonkkaAdduktioOik}/{LonkkaAdduktioVas}. #Sisäkierto {LonkkaSisakiertoOik}/{LonkkaSisakiertoVas}. #Ulkokierto {LonkkaUlkokiertoOik}/{LonkkaUlkokiertoVas}. # 
#Kommentit: {cmtLonkkaPROM}#

POLVI: #Ojennus (vapaasti) {PolviEkstensioVapOik}/{PolviEkstensioVapVas}. #Ojennus (avustettuna) {PolviEkstensioAvOik}/{PolviEkstensioAvVas}. #Koukistus (vatsamakuu) {PolviFleksioVatsamakuuOik}/{PolviFleksioVatsamakuuVas}. #
#Koukistus (selinmakuu) {PolviFleksioSelinmakuuOik}/{PolviFleksioSelinmakuuVas}. #Popliteakulma {PolviPopliteaVastakkLonkka0Oik}/{PolviPopliteaVastakkLonkka0Vas}, popliteakulma (true) {PolviPopliteaVastakkLonkka90Oik}/{PolviPopliteaVastakkLonkka90Vas}. # 
#Kommentit: {cmtPolviPROM}#

NILKKA: #Koukistus (polvi 90°) {NilkkaDorsifPolvi90PROMOik}/{NilkkaDorsifPolvi90PROMVas}. #Koukistus (polvi 0°) {NilkkaDorsifPolvi0PROMOik}/{NilkkaDorsifPolvi0PROMVas}. #Ojennus {NilkkaPlantaarifleksioPROMOik}/{NilkkaPlantaarifleksioPROMVas}. #
#Kommentit: {cmtNilkkaPROM}#

AKTIIVISET LIIKELAAJUUDET: 

NILKKA: 
#Koukistus (polvi 90°) {NilkkaDorsifPolvi90AROMOik}/{NilkkaDorsifPolvi90AROMVas}. #(eversio {NilkkaDorsifPolvi90AROMEversioOik}/{NilkkaDorsifPolvi90AROMEversioVas}). #Koukistus (polvi 0°) {NilkkaDorsifPolvi0AROMOik}/{NilkkaDorsifPolvi0AROMVas}. #(eversio {NilkkaDorsifPolvi0AROMEversioOik}/{NilkkaDorsifPolvi0AROMEversioVas}). #Ojennus {NilkkaPlantaarifleksioAROMOik}/{NilkkaPlantaarifleksioAROMVas}. #
#Kommentit: {cmtNilkkaAROM}#

LUISET VIRHEASENNOT: 
#Lonkan anteversio {VirheasAnteversioOik}/{VirheasAnteversioVas}. #Jalkaterä-reisi -kulma {VirheasJalkaReisiOik}/{VirheasJalkaReisiVas}. #Jalkaterän etu- takaosan kulma {VirheasJalkateraEtuTakaOik}/{VirheasJalkateraEtuTakaVas}. #
#Bimalleoli -akseli {VirheasBimalleoliOik}/{VirheasBimalleoliVas}. #2nd toe test {Virheas2ndtoeOik}/{Virheas2ndtoeVas}. #Patella alta {VirheasPatellaAltaOik}/{VirheasPatellaAltaVas}. #Polven valgus {PolvenValgusOik}/{PolvenValgusVas}. #Q-kulma {QkulmaOik}/{QkulmaVas}. #

#Kommentit: {cmtVirheas}#

MUITA MITTAUKSIA:
#Extensor lag {LonkkaExtLagOik}/{LonkkaExtLagVas}. #Confusion test: {NilkkaConfusionOik}/{NilkkaConfusionVas}. #Ober test {LonkkaOberOik}/{LonkkaOberVas}. #Tasapaino: yhdellä jalalla seisominen {TasapOik}/{TasapVas}. #
#Kommentit (lonkka): {cmtLonkkaMuut}
#Kommentit (tasapaino): {cmtTasap}#

JALKATERÄ KUORMITTAMATTOMANA (+ = lievä, ++ = kohtalainen, +++ = voimakas): 
#Subtalar neutraali-asento: {JalkatSubtalarOik}/{JalkatSubtalarVas}. #Takaosan asento {JalkatTakaosanAsentoOik}/{JalkatTakaosanAsentoVas}. #Takaosan liike eversioon {JalkatTakaosanLiikeEversioOik}/{JalkatTakaosanLiikeEversioVas}. #
#Takaosan liike inversioon {JalkatTakaosanLiikeInversioOik}/{JalkatTakaosanLiikeInversioVas}. #Med. holvikaari {JalkatHolvikaariOik}/{JalkatHolvikaariVas}. #Keskiosan liike {JalkatKeskiosanliikeOik}/{JalkatKeskiosanliikeVas}. #Etuosan asento 1: {JalkatEtuosanAsento1Oik}/{JalkatEtuosanAsento1Vas}. #  
#Etuosan asento 2: {JalkatEtuosanAsento2Oik}/{JalkatEtuosanAsento2Vas}. #1. säde: {Jalkat1sadeOik}/{Jalkat1sadeVas}. #1 MTP dorsifleksio {Jalkat1MTPojennusOik}/{Jalkat1MTPojennusVas}. #Vaivaisenluu {JalkatVaivaisenluuOik}/{JalkatVaivaisenluuVas}. #
#Kovettumat: {JalkatKovettumatOik}/{JalkatKovettumatVas}. #
#Kommentit (jalkaterä): {cmtJalkateraKuormittamattomana}#

JALKATERÄ KUORMITETTUNA (+ = lievä, ++ = kohtalainen, +++ = voimakas):
#Takaosan (kantaluun) asento {JalkatTakaosanAsentoKuormOik}/{JalkatTakaosanAsentoKuormVas}. #Keskiosan asento {JalkatKeskiosanAsentoKuormOik}/{JalkatKeskiosanAsentoKuormVas}. #Etuosan asento 1: {JalkatEtuosanAsento1KuormOik}/{JalkatEtuosanAsento1KuormVas}, etuosan asento 2: {JalkatEtuosanAsento2KuormOik}/{JalkatEtuosanAsento2KuormVas}. #
#Takaosan kierto {JalkatTakaosanKiertoKuormOik}/{JalkatTakaosanKiertoKuormVas}. #Coleman's block test: {JalkatColemanOik}/{JalkatColemanVas}. #Feissin linja: {JalkatFeissinLinjaOik} / {JalkatFeissinLinjaVas}. #
#Painelevy mitattu: {Painelevy}#
#Kommentit (jalkaterä): {cmtJalkateraKuormitettuna}#

ALARAAJOJEN SPASTISUUS:

CATCH: #Lonkan adduktorit {LonkkaAdduktoritCatchOik}/{LonkkaAdduktoritCatchVas}. #Hamstringit {PolviHamstringCatchOik}/{PolviHamstringCatchVas}. #Rectus femorikset {PolviRectusCatchOik}/{PolviRectusCatchVas}. #Soleukset {NilkkaSoleusCatchOik}/{NilkkaSoleusCatchVas}.# (klonus {NilkkaSoleusKlonusOik}/{NilkkaSoleusKlonusVas}). #
#Gastrocnemiukset {NilkkaGastroCatchOik}/{NilkkaGastroCatchVas}. #(klonus {NilkkaGastroKlonusOik}/{NilkkaGastroKlonusVas}). #
#Kommentit (lonkka): {cmtLonkkaSpast}#
#Kommentit (nilkka): {cmtNilkkaSpast}#
#Kommentit (polvi): {cmtPolviSpast}#


MODIFIED ASHWORTH: #Lonkan koukistajat {LonkkaFleksioModAOik}/{LonkkaFleksioModAVas}. #Lonkan ojentajat {LonkkaEkstensioModAOik}/{LonkkaEkstensioModAVas}. #Lonkan lähentäjät {LonkkaAdduktoritModAOik}/{LonkkaAdduktoritModAVas}. #Hamstringit {PolviHamstringModAOik}/{PolviHamstringModAVas}. #
#Rectus femoris {PolviRectusModAOik}/{PolviRectusModAVas}. #Lonkan sisäkierto {LonkkaSisakiertoModAOik}/{LonkkaSisakiertoModAVas}. #Lonkan ulkokierto {LonkkaUlkokiertoModAOik}/{LonkkaUlkokiertoModAVas}. #Soleus {NilkkaSoleusModAOik}/{NilkkaSoleusModAVas}. #Gastrocnemius {NilkkaGastroModAOik}/{NilkkaGastroModAVas}. #
Kommentit:

MANUAALISESTI MITATUT LIHASVOIMAT (oikea/vasen):
Asteikko: 0-5, missä 5 on vahvin ja 3 voittaa painovoiman. Selektiivisyys, missä 
0=kokonaisliikemalli, 1=osittain eriytynyt ja 2=eriytynyt koko liikelaajuudella:  

#Lonkan ojennus (polvi 0°) {VoimaLonkkaEkstensioPolvi0Oik}/{VoimaLonkkaEkstensioPolvi0Vas}#({SelLonkkaEkstensioPolvi0Oik}/{SelLonkkaEkstensioPolvi0Vas})#. #Lonkan ojennus (polvi 90°) {VoimaLonkkaEkstensioPolvi90Oik}/{VoimaLonkkaEkstensioPolvi90Vas}({SelLonkkaEkstensioPolvi90Oik}/{SelLonkkaEkstensioPolvi90Vas}). #Lonkan koukistus {VoimaLonkkaFleksioOik}/{VoimaLonkkaFleksioVas}({SelLonkkaFleksioOik}/{SelLonkkaFleksioVas}). #Loitonnus, lonkka 0° {VoimaLonkkaAbduktioLonkka0Oik}/{VoimaLonkkaAbduktioLonkka0Vas}({SelLonkkaAbduktioLonkka0Oik}/{SelLonkkaAbduktioLonkka0Vas}). #
#Loitonnus, lonkka fleksiossa {VoimaLonkkaAbduktioLonkkaFleksOik}/{VoimaLonkkaAbduktioLonkkaFleksVas}. #Lähennys {VoimaLonkkaAdduktioOik}/{VoimaLonkkaAdduktioVas}({SelLonkkaAdduktioOik}/{SelLonkkaAdduktioVas}). #Lonkan ulkokierto {VoimaLonkkaUlkokiertoOik}/{VoimaLonkkaUlkokiertoVas}({SelLonkkaUlkokiertoOik}/{SelLonkkaUlkokiertoVas}). #
#Lonkan sisäkierto {VoimaLonkkaSisakiertoOik}/{VoimaLonkkaSisakiertoVas}({SelLonkkaSisakiertoOik}/{SelLonkkaSisakiertoVas}). #Polven ojennus {VoimaPolviEkstensioOik}/{VoimaPolviEkstensioVas}({SelPolviEkstensioOik}/{SelPolviEkstensioVas}). #Polven koukistus {VoimaPolviFleksioOik}/{VoimaPolviFleksioVas}({SelPolviFleksioOik}{SelPolviFleksioVas}). #Nilkan koukistus {VoimaTibialisAnteriorOik}/{VoimaTibialisAnteriorVas}({SelTibialisAnteriorOik}/{SelTibialisAnteriorVas}). #
#Nilkan ojennus (gastrocnemius) {VoimaGastroOik}/{VoimaGastroVas}({SelGastroOik}/{SelGastroVas}). #Nilkan ojennus (soleus) {VoimaSoleusOik}/{VoimaSoleusVas}({SelSoleusOik}/{SelSoleusVas}). #
#Inversio {VoimaTibialisPosteriorOik}/{VoimaTibialisPosteriorVas}({SelTibialisPosteriorOik}/{SelTibialisPosteriorVas}). #Eversio {VoimaPeroneusOik}/{VoimaPeroneusVas}({SelPeroneusOik}/{SelPeroneusVas}). #Isovarpaan ojennus {VoimaExtHallucisLongusOik}/{VoimaExtHallucisLongusVas}({SelExtHallucisLongusOik}/{SelExtHallucisLongusVas}). #
#Isovarpaan koukistus {VoimaFlexHallucisLongusOik}/{VoimaFlexHallucisLongusVas}({SelFlexHallucisLongusOik}/{SelFlexHallucisLongusVas}). #Varpaiden (2-5) ojennus {Voima25OjennusOik}/{Voima25OjennusVas}({Sel25OjennusOik}{Sel25OjennusVas}). #
#Varpaiden (2-5) koukistus {Voima25KoukistusOik}/{Voima25KoukistusVas}({Sel25KoukistusOik}/{Sel25KoukistusVas}). #Suorat vatsalihakset {VoimaVatsaSuorat}. #Vinot vatsalihakset {VoimaVatsaVinotOik}/{VoimaVatsaVinotVas}. #Selkälihakset {VoimaSelka}. # 
#Kommentit (voimat): {cmtVoima1}
{cmtVoima2}#


[Suunnitelma/pohdinta]

(Johtopäätökset)
Pääpulmat:
Suositukset:


, fysioterapeutti
Liikelaboratorio
HYKS, Lastenlinna

Jakelu:

Kotiin 2kpl, joista toinen kuntouttavalle fysioterapeutille.
.LL14
"""


report = report_.split(delimiter)

