# -*- coding: utf-8 -*-
"""
Created on Fri Jan 29 10:37:47 2016

@author: jussi
"""

from pandas import DataFrame

class html():

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

    def doc_terminator(self):
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
        return self.doc_header() + self.sec_tiedot() + self.doc_terminator()

    def excel(self, fn):
        """ Export report to Excel (filename fn) TODO"""
        # example (two columns:)
        # df = DataFrame( {'Item': list_items, 'Value': list_values} )
        # df.to_excel('test.xlsx', sheet_name='sheet1', index=False)
        
        
        
           
    

     
     
     
 


