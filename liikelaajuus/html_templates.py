# -*- coding: utf-8 -*-
"""
Created on Fri Feb 05 13:28:25 2016

HTML templates for liikelaajuus report

@author: jussi (jnu@iki.fi)
"""


sections= {}

header = u"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" /> 
</head>
<body>
<h1>Kävelyanalyysi</h1>
"""

footer = u"""
</body>
</html>
"""

sections['Tiedot'] = u"""
<h2>Potilaan tiedot</h2>
<table style="width:100%">
  <tr>
    <td>Potilaan nimi</td>
    <td>{lnTiedotNimi}</td> 
  </tr>
  <tr>
    <td>Potilaskoodi</td>
    <td>{lnTiedotID}</td> 
  </tr>
  <tr>
    <td>Päivämäärä</td>
    <td>{lnTiedotPvm}</td> 
  </tr>
  <tr>
    <td>Diagnoosi</td>
    <td>{lnTiedotDiag}</td> 
  </tr>
  <tr>
    <td>Henkilötunnus</td>
    <td>{lnTiedotHetu}</td> 
  </tr>
  <tr>
    <td>Mittaajat</td>
    <td>{lnTiedotMittaajat}</td> 
  </tr>
</table>"""


sections['Nivelten_p'] = u"""
<h2>Nivelten passiiviset liikelaajuudet</h2>
<h3>Lonkka</h3>
<table style="width:100%">
  <tr>
    <td>Potilaan nimi</td>
    <td>{lnTiedotNimi}</td> 
  </tr>
  <tr>"""


