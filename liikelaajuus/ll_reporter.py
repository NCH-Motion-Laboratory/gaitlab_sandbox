# -*- coding: utf-8 -*-
"""
Created on Fri Jan 29 10:37:47 2016

Create liikelaajuus report.

@author: jussi
"""

#from pandas import DataFrame

import html_templates
#import text_templates


class text():
    """ Make a text report. """
    def __init__(self, data):
        self.data = data
        
    def make(self):
        li = []
        for key in sorted(self.data):
            li.append(key+':'+unicode(self.data[key])+'\n')
        return u''.join(li)

class html():
    
    """ Make an html report. """

    def __init__(self, data):
        self.data = data
        
    def multiline_to_html(self, str):
        """ Convert multiline string to html """
        html_output = []
        for li in str.splitlines():
            html_output.append('<p>'+li+'</p>')
        return ''.join(html_output)
        
    def format_comments(self, comments):
        """ Make given comments field (multiline string) into HTML """
        if comments:
            return u'<h2>Kommentit</h2>'+'\n'+self.multiline_to_html(comments)
        else:
            return ''

    def html_table(self, data):
        """ Make a multicolumn html table. data is a list of rows
        (list of lists of str). """
        table = ['<table style="width:100%">']
        for row in data:
            table.append['<tr>']
            for item in row:
                table.append('<td>'+item+'</td>')
            table.append['</tr>']
        table.append['</table>']
        return ''.join(table)
        
    def format_section(self, sec):
        # format html for given section & add comments field
        return html_templates.section[sec].format(**self.data)

    def make(self):
        # TODO: for key in html_templates.sections...
        return html_templates.header + self.sec_tiedot() + html_templates.footer

    def excel(self, fn):
        """ Export report to Excel (filename fn) TODO"""
        # example (two columns:)
        # df = DataFrame( {'Item': list_items, 'Value': list_values} )
        # df.to_excel('test.xlsx', sheet_name='sheet1', index=False)
        
        
        
           
    

     
     
     
 


