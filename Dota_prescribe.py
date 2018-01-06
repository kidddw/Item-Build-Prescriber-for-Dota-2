#!/usr/bin/python -tt

# read input from user and return prescribed items and skill tree

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import neuralnet as ann




def clean_string(string):
    string = string.lower()
    string = string.replace(" ", "-")
    string = string.replace("'", "")
    return string



# =========================================================================== #
# Determinine list of names
# =========================================================================== #

## read in raw data spreadsheet
#xl = pd.ExcelFile("Dota_binary_data.xlsx")
#df_matches = xl.parse("Sheet1")

#column_titles = list(df_matches.columns.values)

#file_name = 'name_library.dat'
#f = open(file_name, 'w')
#for title in column_titles:
#    f.write(title + ' ')

#sys.exit()

file_name = 'name_library.dat'
f = open(file_name, 'rU')
library = f.read()
column_titles = library.split()
 
#print column_titles

hero_names = [ title[7:] for title in column_titles if title[:7] == 'player-' and title != 'player-team']
#print hero_names

item_names = [ title for title in column_titles if title[:7] != 'player-' and title[:8] != 'radiant-' and title[:5] != 'dire' and title[:6] != 'level-']
#print item_names

print len(hero_names), ' heroes'
print len(item_names), ' items'


# =========================================================================== #
# Read hero names from user
# =========================================================================== #

radiant_heroes = []
for i in range(1,6):
    name = str()
    while name not in hero_names or name in radiant_heroes:
        text = raw_input("input radiant hero " + str(i) + " (include yourself)\n")
        name = clean_string(text)
#        if name in hero_names: continue
        if name not in hero_names: 
            print "Name not in library of hero names. Please try again. \n" 
        if name in radiant_heroes: 
            print "This hero has already been entered. Please try again. \n" 
        print
    radiant_heroes.append(name)

print "=== Radiant team assigned === \n \n"

dire_heroes = []
for i in range(1,6):
    name = str()
    while name not in hero_names or name in dire_heroes:
        text = raw_input("input dire hero " + str(i) + " (include yourself)\n")
        name = clean_string(text)
        if name not in hero_names: 
            print "Name not in library of hero names. Please try again. \n" 
        if name in dire_heroes: 
            print "This hero has already been entered. Please try again. \n" 
        print
    dire_heroes.append(name)

print "=== Dire team assigned === \n \n"

name = str()
while name not in hero_names or name not in (radiant_heroes + dire_heroes):
    text = raw_input("input your hero \n")
    name = clean_string(text)
    if name not in hero_names: 
        print "Name not in library of hero names. Please try again. \n" 
    if name not in (radiant_heroes + dire_heroes): 
        print "This hero is not being used by either team. Please try again. \n" 

print
print "All heroes entered. \n Prescribing items... \n" 

    




# =========================================================================== #
# Feed Forward in neural net
# =========================================================================== #








# =========================================================================== #
# Print Items
# =========================================================================== #









# =========================================================================== #
# Print Skills
# =========================================================================== #

























