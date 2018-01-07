#!/usr/bin/python -tt

# list of outliers:
#     - there are not 18 skill choices (match ended too soon)
#     - no final items (sold before end of game)
#     - some final items carried? (before end of game)
#     - some final items sold/bought (before end of game)  


# import libraries
import sys
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def get_h_m_s(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)


def summarize(df, name):
    tot_matches = len(df.index)
    print name
    print str(tot_matches) + ' matches analyzed' 
    print str(len(df['Player Name'].unique())) + ' players'
    print str(len(df['Player Hero'].unique())) + ' unique heroes used by players'
    print 'average match duration: ' + get_h_m_s(df['Match Duration sec'].mean())
    print


def clean_string(string):
    string = string.lower()
    string = string.replace(" ", "-")
    string = string.replace("'", "")
    return string


def determine_heroes_binary(row, hero_names):
    """
    Read in contents of row (all rows at once passed in as a Series)
    (1) determine the Player Team
    (2) determine the 4 hero names from that team that are not redundant with the player's hero
        and return the 5 hero names of the other team
    (3) return the tuple of binary information regarding the player hero, player's team's heroes 
        and opponent team's heroes
    """
    # define radiant team heroes and dire team heroes
    radiant_heroes = []
    dire_heroes = []
    for i in range(1,6):
        radiant_heroes.append(row['Radiant Hero ' + str(i)])
        dire_heroes.append(row['Dire Hero ' + str(i)])
    # define player team heroes (length 4) and opponent team heroes (length 5)
    if row["Player Team"] == 'radiant':
        radiant_heroes.remove(row['Player Hero'])
        player_team_heroes = radiant_heroes
        opponent_team_heroes = dire_heroes
    if row["Player Team"] == 'dire':
        dire_heroes.remove(row['Player Hero'])
        player_team_heroes = dire_heroes
        opponent_team_heroes = radiant_heroes

    player_hero_options = [0] * len(hero_names)
    for idx, name in enumerate(hero_names):
        if name == row['Player Hero']:
            player_hero_options[idx] = 1 
    player_team_options = [0] * len(hero_names)
    for idx, name in enumerate(hero_names):
        if name in player_team_heroes:
            player_team_options[idx] = 1
    opponent_team_options = [0] * len(hero_names)
    for idx, name in enumerate(hero_names):
        if name in opponent_team_heroes:
            opponent_team_options[idx] = 1 
    final_hero_options = tuple(player_hero_options + player_team_options + opponent_team_options)

    return final_hero_options


# =========================================================================== #
# =========================================================================== #


# get lists of common column label groupings
radiant_columns = []
dire_columns = []
item_columns = []
skill_columns = []
for i in range(5): 
    item_columns.append('Player Item ' + str(i+1))
    radiant_columns.append('Radiant Hero ' + str(i+1))
    dire_columns.append('Dire Hero ' + str(i+1))
for i in range(25):
    skill_columns.append('Skill Level ' + str(i+1))


# initialize excel spreadsheet for binary data
writer = pd.ExcelWriter('Dota_binary_data.xlsx')
#writer = pd.ExcelWriter('output2.xlsx')


# =========================================================================== #
# Import Raw Data DataFrame
# =========================================================================== #

# read in raw data spreadsheet
xl = pd.ExcelFile("Dota_raw_data.xlsx")
df_raw = xl.parse("Sheet1")
print

# get column of match durations in seconds for simple computing 
seconds = []
for duration in df_raw['Match Duration'].tolist():
    seconds.append((duration.hour * 60 + duration.minute) * 60 + duration.second)
df_raw['Match Duration sec'] = seconds

# print facts about data set
summarize(df_raw, 'Raw Data')

hero_names = ['Abaddon', 'Alchemist', 'Ancient Apparition', 'Anti-Mage', 'Arc Warden', 'Axe', 'Bane', 'Batrider', 'Beastmaster', 'Bloodseeker', 'Bounty Hunter', 'Brewmaster', 'Bristleback', 'Broodmother', 'Centaur Warrunner', 'Chaos Knight', 'Chen', 'Clinkz', 'Clockwerk', 'Crystal Maiden', 'Dark Seer', 'Dark Willow', 'Dazzle', 'Death Prophet', 'Disruptor', 'Doom', 'Dragon Knight', 'Drow Ranger', 'Earth Spirit', 'Earthshaker', 'Elder Titan', 'Ember Spirit', 'Enchantress', 'Enigma', 'Faceless Void', 'Gyrocopter', 'Huskar', 'Invoker', 'Io', 'Jakiro', 'Juggernaut', 'Keeper of the Light', 'Kunkka', 'Legion Commander', 'Leshrac', 'Lich', 'Lifestealer', 'Lina', 'Lion', 'Lone Druid', 'Luna', 'Lycan', 'Magnus', 'Medusa', 'Meepo', 'Mirana', 'Monkey King', 'Morphling', 'Naga Siren', 'Nature\'s Prophet', 'Necrophos', 'Night Stalker', 'Nyx Assassin', 'Ogre Magi', 'Omniknight', 'Oracle', 'Outworld Devourer', 'Pangolier', 'Phantom Assassin', 'Phantom Lancer', 'Phoenix', 'Puck', 'Pudge', 'Pugna', 'Queen of Pain', 'Razor', 'Riki', 'Rubick', 'Sand King', 'Shadow Demon', 'Shadow Fiend', 'Shadow Shaman', 'Silencer', 'Skywrath Mage', 'Slardar', 'Slark', 'Sniper', 'Spectre', 'Spirit Breaker', 'Storm Spirit', 'Sven', 'Techies', 'Templar Assassin', 'Terrorblade', 'Tidehunter', 'Timbersaw', 'Tinker', 'Tiny', 'Treant Protector', 'Troll Warlord', 'Tusk', 'Underlord', 'Undying', 'Ursa', 'Vengeful Spirit', 'Venomancer', 'Viper', 'Visage', 'Warlock', 'Weaver', 'Windranger', 'Winter Wyvern', 'Witch Doctor', 'Wraith King', 'Zeus']

hero_names = [clean_string(name) for name in hero_names]

# =========================================================================== #
# Remove incomplete date
# =========================================================================== #

df_clean = df_raw.copy()

# remove losses
df_clean = df_clean.drop(df_clean[df_clean['Result'] != 'win'].index)

# remove matches where a skill was not selected at 18
df_clean = df_clean.drop(df_clean[df_clean['Skill Level 18'] == 0].index)

# remove matches where there are not five player items present
for i in range(5):
    column_name = 'Player Item ' + str(i+1)
    df_clean = df_clean.drop(df_clean[df_clean[column_name] == 'none'].index)

# remove matches where there are not 10 heroes 
for i in range(5):
    column_name = 'Radiant Hero ' + str(i+1)
    df_clean = df_clean.drop(df_clean[df_clean[column_name] == 'none'].index)
    column_name = 'Dire Hero ' + str(i+1)
    df_clean = df_clean.drop(df_clean[df_clean[column_name] == 'none'].index)

# remove matches where there are only three or less unique items (can only have one duplicate item)
df_items = df_clean[item_columns]
df_clean = df_clean.drop(df_items[df_items.apply(pd.Series.nunique, axis = 1) <= 3].index)

# print facts about data set
summarize(df_clean, 'Cleaned Data')




# =========================================================================== #
# =========================================================================== #
# Translate Data into Binary Table
# =========================================================================== #
# =========================================================================== #

# COLUMNS: 
#     player-team:       1 for radiant, 0 for dire
#     player-{hero}:     1 for player was this hero
#     radiant-{hero}:    1 for radiant team used this hero
#     dire-{hero}:       1 for dire team used this hero
#     {item}:            1 for player finished with this item
#     level-{}-skill-{}: 1 for player chose this skill at this level


# COLUMNS: 
#     player-{hero}:        1 for player was this hero
#     player-team-{hero}:   1 for radiant team used this hero
#     opponent-team-{hero}: 1 for dire team used this hero
#     {item}:               1 for player finished with this item
#     level-{}-skill-{}:    1 for player chose this skill at this level





# =========================================================================== #
# # Get new column headers
# =========================================================================== #

unique_items = np.unique(df_clean[item_columns].values).tolist()
skill_options = []
for i in range(25):
    for j in range(4):
        column_header = 'level-' + str(i+1) + '-skill-' + str(j+1)
        skill_options.append(column_header) 

hero_name_headers = ['player-' + s for s in hero_names] + ['player-team-' + s for s in hero_names] + ['opponent-team-' + s for s in hero_names]
new_column_headers = hero_name_headers + unique_items + skill_options

num_features = len(hero_names) * 3
num_classes = len(unique_items + skill_options)
print 'number of features: ', num_features
print 'number of classes: ', num_classes
print




# =========================================================================== #
# Reformat data into new table
# =========================================================================== #

new_columns_tuple_series = zip(*df_clean.apply(determine_heroes_binary, args = (hero_names,), axis = 1))
for idx, header in enumerate(hero_name_headers):
    df_clean[header] = new_columns_tuple_series[idx]

#df_matches_b = df_clean.loc[:, ["player-primary-attribute"]]

# update excel spreadsheet file
df_clean.to_excel(writer,'Sheet1')
writer.save()

sys.exit()




# =========================================================================== #
# Reformat data into new table
# =========================================================================== #

# initialize binary dataframe
df_matches_b = pd.DataFrame(columns = new_column_headers)

# Form new rows using Binary indicators 
for index, row in df_clean.iterrows():
    print index
    new_row = [0] * len(new_column_headers)

    if row['Player Team'] == 'radiant': new_row[0] = 1

    ind = 0
    for hero in unique_player_hero:
        ind = ind + 1
        if hero == ('player-' + row['Player Hero']): new_row[ind] = 1

    for hero in unique_radiant:
        ind = ind + 1
        if hero in ['radiant-' + s for s in row[radiant_columns].values]: new_row[ind] = 1

    for hero in unique_dire:
        ind = ind + 1
        if hero in ['dire-' + s for s in row[dire_columns].values]: new_row[ind] = 1

    for item in unique_items:
        ind = ind + 1
        if item in row[item_columns].values: new_row[ind] = 1

    for level in range(25):
        column_header = 'Skill Level ' + str(level+1)
        for skill in range(4):
            ind = ind + 1
            if (skill + 1) == row[column_header]: new_row[ind] = 1
        
    df_match_b = pd.DataFrame([new_row], columns = new_column_headers)

    # append new row to new binary dataframe
    df_matches_b = df_matches_b.append(df_match_b, ignore_index = True)


# update excel spreadsheet file
df_matches_b.to_excel(writer,'Sheet1')
writer.save()




# =========================================================================== #
# Write Contents Into X data and Y data files for use with neural net solver
# =========================================================================== #

#  Xmat: (numpy matrix) matrix with rows as data points and 
#      columns as features
#  Ymat: (numpy matrix) matrix with rows as data points and 
#      columns as classes


x_fname = 'training_x.dat'
y_fname = 'training_y.dat'

x_out = open(x_fname, 'w')
y_out = open(y_fname, 'w')

for i in range(len(df_matches_b.index)):
    for j in range(len(new_column_headers)):
        if j <= (num_features - 1):
            # X data
            x_out.write(str(df_matches_b.iloc[i,j]) + ' ')

        if j > (num_features - 1):
            # Y data
            y_out.write(str(df_matches_b.iloc[i,j]) + ' ')

    x_out.write('\n')
    y_out.write('\n')


# =========================================================================== #
# Try summing up item usage report
# =========================================================================== #

writer2 = pd.ExcelWriter('count.xlsx')
print df_matches_b.sum(axis=1)
df_count = df_matches_b.sum(axis=1)
df_count.to_excel(writer2,'Sheet1')
writer2.save()




















