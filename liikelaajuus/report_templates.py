# -*- coding: utf-8 -*-
"""
Created on Fri Jan 29 10:37:47 2016

@author: jussi
"""

class movement_report():
    """ Make a report based on given data. """

    def __init__(self, data):
        self.data = data
        # these are magic values for entries not measured
        self.LN_NONE = ''
        self.SP_NONE = -181
        self.CB_NONE = "Ei mitattu"
        self.TE_NONE = ''
        # translate special default (unmeasured) values to None
        for key in self.data:
            if key[:2] == 'sp' and data[key] == self.SP_NONE:
                self.data[key] == None
            if key[:2] == 'cb' and data[key] == self.CB_NONE:
                self.data[key] == None
        self.data['separator'] = '---'

    def text(self):
        """ Generate a text report (multiline string) """
        return u"""{separator}
Päivämäärä: {lnTiedotPvm}
Potilaskoodi: {lnTiedotID}
Potilaan nimi: {lnTiedotNimi}
Henkilötunnus: {lnTiedotHetu}
Diagnoosi: {lnTiedotDiag}
Mittaajat: {lnTiedotMittaajat}
Kommentit:\n{cmtTiedot}
{separator}
""".format(**self.data)
           
    

     
     
     
 


