#!/usr/bin/python -tt

#need to fix issue of not using all hero names in each column


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

hero_names = [ title[7:] for title in column_titles if title[:7] == 'player-']
item_names = [ title[5:] for title in column_titles if title[:5] == 'item-']

print len(hero_names), ' heroes'
print len(item_names), ' items'


# =========================================================================== #
# Read hero names from user
# =========================================================================== #

name = str()
while name not in hero_names:
    text = raw_input("input your hero \n")
    name = clean_string(text)
    if name not in hero_names: 
        print "Name not in library of hero names. Please try again. \n"  
player_hero = name

print "=== Player hero assigned === \n \n"

player_team_heroes = []
for i in range(1,5):
    name = str()
    while name not in hero_names or name in radiant_heroes or name == player_hero:
        text = raw_input("input hero on your team " + str(i) + "/4 (do not include yourself)\n")
        name = clean_string(text)
        if name not in radiant_hero_names: 
            print "Name not in library of hero names. Please try again. \n" 
        if name in radiant_heroes: 
            print "This hero has already been entered. Please try again. \n" 
        if name == player_hero:
            print "Do not include yourself"
        print
    player_team_heroes.append(name)

print "=== Player team assigned === \n \n"

opponent_team_heroes = []
for i in range(1,6):
    name = str()
    while name not in hero_names or name in radiant_heroes or name in dire_heroes:
        text = raw_input("input hero on opposite team " + str(i) + "/5\n")
        name = clean_string(text)
        if name not in dire_hero_names: 
            print "Name not in library of hero names. Please try again. \n" 
        if name in dire_heroes or name in radiant_heroes: 
            print "This hero has already been entered. Please try again. \n" 
        print
    opponent_team_heroes.append(name)

print "=== Opposing team assigned === \n \n"

print
print "All heroes entered. \n Prescribing items... \n" 


# =========================================================================== #
# Create vector for feeding forward
# =========================================================================== #

input_list = [0] * len(hero_names) *3 

for idx, name in enumerate(hero_names):
    if name == player_hero:
        input_list[idx] = 1

for idx, name in enumerate(hero_names):
    if name in player_team_heroes:
        input_list[idx + len(hero_names)] = 1

for idx, name in enumerate(hero_names):
    if name in opponent_team_heroes:
        input_list[idx + len(hero_names) * 2] = 1

input_X = np.matrix([input_list])



# =========================================================================== #
# Feed forward in neural net
# =========================================================================== #

Y_dimension = len(item_names) + 25 * 4
arch = ([input_X.shape[1]] + ann.import_architecture('arch.dat') + [Y_dimension])
Theta_matrices = ann.import_weights(arch, 2)
prediction = ann.make_prediction(Theta_matrices, input_X)[0]
print prediction
print len(prediction)


# =========================================================================== #
# Print Items
# =========================================================================== #

print
for idx, item in enumerate(item_names):
    if prediction[idx] == 1:
        print item_names[idx] + "\n"
print

# =========================================================================== #
# Print Skills
# =========================================================================== #

ind = len(item_names)
for level in range(25):
    for skill in range(4):
        if prediction[ind] == 1:
            print "level " + str(level + 1) + ": skill " + str(skill + 1) 
        ind = ind + 1























