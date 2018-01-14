#!/usr/bin/python -tt

#need to fix issue of not using all hero names in each column


# read input from user and return prescribed items and skill tree

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from neuralnet import MLPClassifier




def clean_string(string):
    string = string.lower()
    string = string.replace(" ", "-")
    string = string.replace("'", "")
    return string



# =========================================================================== #
# Determinine list of names
# =========================================================================== #

first_time = False

file_name = 'item_list.txt'
f = open(file_name, 'rU')
library = f.read()
item_names = library.split()
item_names = [ name[5:] for name in item_names]

strength_radiant_heroes = ['Earthshaker', 'Sven', 'Tiny', 'Kunkka', 'Beastmaster', 'Dragon Knight', 'Clockwerk', 'Omniknight', 'Huskar', 'Alchemist', 'Brewmaster', 'Treant Protector', 'Io', 'Centaur Warrunner', 'Timbersaw', 'Bristleback', 'Tusk', 'Elder Titan', 'Legion Commander', 'Earth Spirit', 'Phoenix']

strength_dire_heroes = ['Axe', 'Pudge', 'Sand King', 'Slardar', 'Tidehunter', 'Wraith King', 'Lifestealer', 'Night Stalker', 'Doom', 'Spirit Breaker', 'Lycan', 'Chaos Knight', 'Undying', 'Magnus', 'Abaddon', 'Underlord']

agility_radiant_heroes = ['Anti-Mage', 'Drow Ranger', 'Juggernaut', 'Mirana', 'Morphling', 'Phantom Lancer', 'Vengeful Spirit', 'Riki', 'Sniper', 'Templar Assassin', 'Luna', 'Bounty Hunter', 'Ursa', 'Gyrocopter', 'Lone Druid', 'Naga Siren', 'Troll Warlord', 'Ember Spirit', 'Monkey King', 'Pangolier']

agility_dire_heroes = ['Bloodseeker', 'Shadow Fiend', 'Razor', 'Venomancer', 'Faceless Void', 'Phantom Assassin', 'Viper', 'Clinkz', 'Broodmother', 'Weaver', 'Spectre', 'Meepo', 'Nyx Assassin', 'Slark', 'Medusa', 'Terrorblade', 'Arc Warden']

intelligence_radiant_heroes = ['Crystal Maiden', 'Puck', 'Storm Spirit', 'Windranger', 'Zeus', 'Lina', 'Shadow Shaman', 'Tinker', 'Nature\'s Prophet', 'Enchantress', 'Jakiro', 'Chen', 'Silencer', 'Ogre Magi', 'Rubick', 'Disruptor', 'Keeper of the Light', 'Skywrath Mage', 'Oracle', 'Techies', 'Dark Willow']

intelligence_dire_heroes = ['Bane', 'Lich', 'Lion', 'Witch Doctor', 'Enigma', 'Necrophos', 'Warlock', 'Queen of Pain', 'Death Prophet', 'Pugna', 'Dazzle', 'Leshrac', 'Dark Seer', 'Batrider', 'Ancient Apparition', 'Invoker', 'Outworld Devourer', 'Shadow Demon', 'Visage', 'Winter Wyvern']

hero_list = strength_radiant_heroes + strength_dire_heroes + agility_radiant_heroes + agility_dire_heroes + intelligence_radiant_heroes + intelligence_dire_heroes
hero_names = sorted([clean_string(name) for name in hero_list])

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
    while name not in hero_names or name in player_team_heroes or name == player_hero:
        text = raw_input("input hero on your team " + str(i) + "/4 (do not include yourself)\n")
        name = clean_string(text)
        if name not in hero_names: 
            print "Name not in library of hero names. Please try again. \n" 
        if name in player_team_heroes: 
            print "This hero has already been entered. Please try again. \n" 
        if name == player_hero:
            print "Do not include yourself"
        print
    player_team_heroes.append(name)

print "=== Player team assigned === \n \n"

opponent_team_heroes = []
for i in range(1,6):
    name = str()
    while name not in hero_names or name in opponent_team_heroes or name in player_team_heroes or name == player_hero:
        text = raw_input("input hero on opposite team " + str(i) + "/5\n")
        name = clean_string(text)
        if name not in hero_names: 
            print "Name not in library of hero names. Please try again. \n" 
        if name in opponent_team_heroes or name in player_team_heroes: 
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

skill_columns = 0 # 100 if using skills
Y_dimension = len(item_names) + skill_columns
clf = MLPClassifier(lambda_reg=(10.0**0.5), hidden_layer_sizes=(250,), tol=0.005, cg_solver='fmin_cg')

clf.read_weights(input_X.shape[1], Y_dimension)
prediction = clf.predict(input_X)


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
if skill_columns > 0:
    for level in range(25):
        for skill in range(4):
            if prediction[ind] == 1:
                print "level " + str(level + 1) + ": skill " + str(skill + 1) 
            ind = ind + 1























