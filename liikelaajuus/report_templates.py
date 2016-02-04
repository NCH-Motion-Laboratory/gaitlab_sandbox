# -*- coding: utf-8 -*-
"""
Created on Fri Jan 29 10:37:47 2016

@author: jussi
"""

from pandas import DataFrame

    
class html_report():

    def __init__(self, data):
        self.data = data
        
    def doc_header(self):
        return """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" /> 
</head>
<body>
"""

    def doc_terminate(self):
        return """
</body>
</html>
"""
        
    def sec_tiedot(self):
        return """
<h2>Potilaan tiedot</h2>
<table style="width:100%">
  <tr>
    <td>Potilaskoodi</td>
    <td>{lnTiedotID}</td> 
  </tr>
  <tr>
    <td>Potilaan nimi</td>
    <td>{lnTiedotNimi}</td> 
  </tr>
  <tr>
    <td>Henkilötunnus</td>
    <td>{lnTiedotHetu}</td> 
  </tr>
</table>
""".format(**self.data)


    def make(self):
        return self.doc_header() + self.sec_tiedot() + self.doc_terminate()

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
        self.data['ITEM_SEP'] = '\t'
        self.data['SECTION_SEP'] = ''
        
    def docx(self):
        """ Generate a Word report """

    def html(self):
        rep = html_report(self.data)
        return rep.make()

    def text(self):
        """ Generate a text report (multiline string) """
        return u"""{SECTION_SEP}
Päivämäärä{ITEM_SEP}{lnTiedotPvm}
Potilaskoodi{ITEM_SEP}{lnTiedotID}
Potilaan nimi{ITEM_SEP}{lnTiedotNimi}
Henkilötunnus{ITEM_SEP}{lnTiedotHetu}
Diagnoosi{ITEM_SEP}{lnTiedotDiag}
Mittaajat{ITEM_SEP}{lnTiedotMittaajat}
Kommentit:\n{cmtTiedot}
{SECTION_SEP}
""".format(**self.data)

    def excel(self, fn):
        """ Export report to Excel (filename fn) """
        # example (two columns:)
        # df = DataFrame( {'Item': list_items, 'Value': list_values} )
        # df.to_excel('test.xlsx', sheet_name='sheet1', index=False)
        
        
        
           
    

     
     
     
 


