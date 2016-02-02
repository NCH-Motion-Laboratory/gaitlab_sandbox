# -*- coding: utf-8 -*-
"""
Created on Fri Jan 29 10:37:47 2016

@author: jussi
"""

class movement_report():
    """ Liikelaajuus (movement range) report based on given data. """

    def __init__(self, data):
        self.data = data

    def header(self):
        """ Start of report, basic data (name etc.) """
        return """---
Päivämäärä: {lnTiedotPvm}
Potilaskoodi: {lnTiedotID}
Potilaan nimi: {lnTiedotNimi}
Henkilötunnus: {lnTiedotHetu}
Diagnoosi: {lnTiedotDiag}
Mittaajat: {lnTiedotMittaajat}
Kommentit: {cmtTiedot}
---
""".format(**self.data)
           
    def textual(self):
        return self.header()
    

     
     
     
 


