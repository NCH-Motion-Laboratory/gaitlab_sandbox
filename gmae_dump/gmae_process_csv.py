#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
"""
Created on Wed Dec 10 13:11:57 2014

@author: jussi
"""

"""
GMAE conversion project:
Process .csv files created by AccessDump.py, to create neatly 
formatted output.

bash loop to get pdf output from all files:
for file in *mdb; do ./gmae_process_csv.py "$file" |enscript -p -|ps2pdf - "$file".pdf; done
for file in *mdb; do ./gmae_process_csv.py "$file" >"${file%%.*}".txt; done


AccessDump.py takes a .mdb file (one per patient) and writes various .csv.
"""


import csv
import sys, subprocess, os

if len(sys.argv) != 2 :
    sys.exit('Need exactly 1 argument (name of MDB file)')
    
DATABASE = sys.argv[1]

# Get the list of table names with "mdb-tables"
table_names = subprocess.Popen(["mdb-tables", "-1", DATABASE], 
                               stdout=subprocess.PIPE).communicate()[0]
tables = table_names.split('\n')
if tables != ['AssessmentInfo', 'BaseInfo', 'ItemInfo', 'Report', 'Therapists', '']:
    raise Exception('Unexpected tables in MDB file')

# Dump each table as a CSV file using "mdb-export",
# converting " " in table names to "_" for the CSV filenames.
for table in tables:
    if table != '':
        filename = table.replace(" ","_") + ".csv"
        file = open(filename, 'w')
        #print("Dumping " + table)
        contents = subprocess.Popen(["mdb-export", DATABASE, table],
                                    stdout=subprocess.PIPE).communicate()[0]
        file.write(contents)
        file.close()

#print('GMAE result sheet, converted from original mdb data by gmae_process_csv.py')

print()
# Therapist(s)        
with open('Therapists.csv') as csvfile:
    csvreader=csv.DictReader(csvfile)
    print('Therapist(s):',end=' ')
    for row in csvreader:
        print(row['TherapistID'])
print()

# name, DOB, Type of CP, etc.
with open('BaseInfo.csv') as csvfile:
    csvreader=csv.DictReader(csvfile)
    template = '{0:15} {1:25} {2:20} {3:8} {4:14} {5:8}'
    print(template.format('ID','Name','Date of birth','CP type','Distribution',
                          'Gender'))
    for row in csvreader:
        print(template.format(row['UniqueID'],
                              row['FirstName'].capitalize()+' '
                              +row['LastName'].capitalize(),
                              row['DOB'],row['TypeCP'],row['Distribution'],
                                row['Gender']))
print('\nAssessments by date:\n')
"""
Assessment scores. First column contains the item numbers. Following
columns have the corresponding assessment for each date.
"""
with open('AssessmentInfo.csv') as csvfile:
    csvreader=csv.reader(csvfile)
    asslist = []
    for row in csvreader:
        asslist.append(row)
    nitems = len(asslist[0])
    nrows = len(asslist)
    for k in range(nitems):
        for l in range(nrows):
            print('{0:25}'.format(asslist[l][k]),end='')
        print()

# delete intermediate csv files        
for table in tables:
    if table != '':
        filename = table.replace(" ","_") + ".csv"
        os.remove(filename)
        
        
"""        
# Assessment descriptions: ItemInfo.csv
with open('ItemInfo.csv') as csvfile:
    csvreader=csv.reader(csvfile)
    for row in csvreader:
        print(', '.join(row))
"""
        


