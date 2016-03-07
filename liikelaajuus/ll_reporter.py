# -*- coding: utf-8 -*-
"""
Created on Fri Jan 29 10:37:47 2016

Create liikelaajuus report.

@author: jussi
"""

#from pandas import DataFrame

import html_templates
import text_templates
import string        
        

class text():
    
    def __init__(self, data):
        self.data = data
        self.not_measured = u'Ei mitattu'
        self.delimiter = '#'  # report 'chunk' delimiter

    def get_field(self, s):
        """ Return all fields in a format string. """
        fi = string.Formatter()
        pit = fi.parse(s)  # returns parser generator
        for items in pit:
            if items[1]:
                yield items[1]  # = the field
        
    def cond_format(self, s, di, empty=None):
        """ Conditionally format string s using dict di: if all field values
        equal the 'empty' value, return empty string. """
        flds = list(self.get_field(s))
        if not flds or any([di[fld] != empty for fld in flds]):
            return s.format(**di)
        else:
            return ''
        
    def make_text_report(self):
        """ Generates the main text report. """
        report = text_templates.report

        # debug: check which fields are (not) present in report
        flds_report = set(self.get_field(''.join(report)))
        flds_data = set(self.data.keys())
        flds_cmn = flds_data.intersection(flds_report)
        extra_in_rep = flds_report - flds_cmn
        not_in_rep = flds_data - flds_cmn
        print('Keys in report but not in data:', extra_in_rep)
        print('Keys in data but not in report:', not_in_rep)
        
        # format fields and join. cond_format skips chunks with no data
        return ''.join([self.cond_format(s, self.data, self.not_measured) for s in report])

    def make_text_list(self):
        """ Make a simple list of all variables + values. """
        li = []
        for key in sorted(self.data):
            li.append(key+':'+unicode(self.data[key])+'\n')
        return u''.join(li)

    def excel(self, fn):
        """ Export report to Excel (filename fn) TODO"""
        # example (two columns:)
        # df = DataFrame( {'Item': list_items, 'Value': list_values} )
        # df.to_excel('test.xlsx', sheet_name='sheet1', index=False)
        





class html():
    
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

    def make_html(self):
        # TODO: for key in html_templates.sections...
        return html_templates.header + self.sec_tiedot() + html_templates.footer

        
        
           
    

     
     
     
 


