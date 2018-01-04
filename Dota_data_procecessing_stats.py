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


def determine_player_hero_stats(name, hero_stats, column_title):
    return hero_stats.loc[name, column_title] 

def determine_team_primary_attributes(names, hero_stats, column_title):
    if column_title == 'strength': i = 1
    if column_title == 'agility': i = 2
    if column_title == 'intelligence': i = 3
    ind = 0
    for name in names:
        if hero_stats.loc[name,'primary-ability'] == i: ind = ind + 1 
    return ind

def determine_team_attack_types(names, hero_stats, column_title):
    if column_title == 'melee': i = 1
    if column_title == 'range': i = 2
    ind = 0
    for name in names:
        if hero_stats.loc[name,'attack-type'] == i: ind = ind + 1 
    return ind

def determine_team_roles(names, hero_stats, column_title):
    ind = 0
    for name in names:
         ind = ind + hero_stats.loc[name,column_title] 
    return ind

def determine_player_team_stats(row, hero_stats):
    """
    Read in contents of row (all rows at once passed in as a Series)
    (1) determine the Player Team
    (2) return the 4 hero names from that team that are not redundant with the player's hero
        and return the 5 hero names of the other team
    (3) determine sum stats of each team
    (4) output these stats in the following order:
        player team {melee, range, strength, agility, intelligence}, opponent team {...}
        return tuple of length 10
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
    # sum number of each hero type amongst teams using hero_stats
    for idx, team in enumerate([player_team_heroes, opponent_team_heroes]):
        melee_count = 0
        range_count = 0
        strength_count = 0
        agility_count = 0
        intelligence_count = 0
        role_count = [0]*9
        for name in team:
            if hero_stats.loc[name,'attack-type'] == 1: melee_count = melee_count + 1
            if hero_stats.loc[name,'attack-type'] == 2: range_count = range_count + 1
            if hero_stats.loc[name,'primary-attribute'] == 1: strength_count = strength_count + 1
            if hero_stats.loc[name,'primary-attribute'] == 2: agility_count = agility_count + 1
            if hero_stats.loc[name,'primary-attribute'] == 3: intelligence_count = intelligence_count + 1
            for role_idx, role in enumerate(roles):
                role_count[role_idx] = role_count[role_idx] + hero_stats.loc[name,role]
        team_stats = [melee_count, range_count, strength_count, agility_count, intelligence_count] + role_count
        if idx == 0: player_team_stats = team_stats
        if idx == 1: opponent_team_stats = team_stats
    final_stats = tuple(player_team_stats + opponent_team_stats)
    return final_stats



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
writer = pd.ExcelWriter('Dota_stats_data.xlsx')


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


# =========================================================================== #
# Remove incomplete data
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
# Translate Data into Match Stats Table
# =========================================================================== #

# COLUMNS:
#     player-primary-ability           : 1 for strength, 2 for agility, 3 for intelligence
#     player-attack-type               : 1 for melee, 2 for range
#     player-{role}                    : rating between 0-3 for each role
#     player-team-strength-score       : composite number of strength users
#     player-team-agility-score        : composite number of agility users
#     player-team-intelligence-score   : composite number of intelligence users
#     player-team-melee-score          : composite number of melee users
#     player-team-range-score          : composite number of range users
#     player-team-{role}               : composite role scores
#     opponent-team-strength-score     : composite number of strength users
#     opponent-team-agility-score      : composite number of agility users
#     opponent-team-intelligence-score : composite number of intelligence users
#     opponent-team-melee-score        : composite number of melee users
#     opponent-team-range-score        : composite number of range users
#     opponent-team-{role}             : composite role scores

#     {item}:                          : 1 for player finished with this item
#     level-{}-skill-{}                : 1 for player chose this skill at this level


# read in hero stats spreadsheet
xl = pd.ExcelFile("Dota_hero_stats.xlsx")
df_hero_stats = xl.parse("Sheet1")


# Get new column headers

# roles
roles = ['carry', 'nuker', 'initiator', 'disabler', 'durable', 'escape', 'support', 'pusher', 'jungler']
hero_types = ['melee', 'range','strength', 'agility', 'intelligence']

player_columns = ['player-primary-attribute', 'player-attack-type'] + ['player-' + s for s in roles]
player_team_roles = ['player-team-' + s for s in roles]
player_team_types = ['player-team-' + s + '-score' for s in hero_types]
opponent_team_roles = ['opponent-team-' + s for s in roles]
opponent_team_types = ['opponent-team-' + s + '-score' for s in hero_types]
team_columns = player_team_types + player_team_roles + opponent_team_types + opponent_team_roles

unique_items = np.unique(df_clean[item_columns].values).tolist()
skill_options = []
for i in range(25):
    for j in range(4):
        column_header = 'level-' + str(i+1) + '-skill-' + str(j+1)
        skill_options.append(column_header) 

new_column_headers = player_columns + player_team_roles + player_team_types + opponent_team_roles + opponent_team_types + unique_items + skill_options

# Print number of features and number of classes
num_features = len(player_columns + player_team_roles + player_team_types + opponent_team_roles + opponent_team_types)
num_classes = len(unique_items + skill_options)
print 'number of features: ', num_features
print 'number of classes: ', num_classes
print

# for each row, take Player Team (radiant / dire) and determine the set of 5 columns to work from. Then eliminate the entry redundant with Player Hero. Return the remaining 4 enties. 


df_clean["player-primary-attribute"] = df_clean["Player Hero"].apply(determine_player_hero_stats, args = (df_hero_stats,'primary-attribute'))
df_clean["player-attack-type"] = df_clean["Player Hero"].apply(determine_player_hero_stats, args = (df_hero_stats,'attack-type'))
for role in roles:
    df_clean[("player-" + role)] = df_clean["Player Hero"].apply(determine_player_hero_stats, args = (df_hero_stats,(role)))

#for hero_type in hero_types:
print len(zip(*df_clean.apply(determine_player_team_stats, args = (df_hero_stats,), axis = 1)))


df_clean[team_columns[0]], df_clean[team_columns[1]], df_clean[team_columns[2]], df_clean[team_columns[3]], \
df_clean[team_columns[4]], df_clean[team_columns[5]], df_clean[team_columns[6]], df_clean[team_columns[7]], \
df_clean[team_columns[8]], df_clean[team_columns[9]], df_clean[team_columns[10]], df_clean[team_columns[11]], \
df_clean[team_columns[12]], df_clean[team_columns[13]], \
df_clean[team_columns[14]], df_clean[team_columns[15]], df_clean[team_columns[16]], df_clean[team_columns[17]], \
df_clean[team_columns[18]], df_clean[team_columns[19]], df_clean[team_columns[20]], df_clean[team_columns[21]], \
df_clean[team_columns[22]], df_clean[team_columns[23]], df_clean[team_columns[24]], df_clean[team_columns[25]], \
df_clean[team_columns[26]], df_clean[team_columns[27]] = zip(*df_clean.apply(determine_player_team_stats, args = (df_hero_stats,), axis = 1))







df_matches_s = df_clean.loc[:, ["player-primary-attribute"]]


writer = pd.ExcelWriter('Dota_stats_test.xlsx')
df_clean.to_excel(writer,'Sheet1')
writer.save()

sys.exit()












# =========================================================================== #
# Translate Data into Binary Table
# =========================================================================== #

# COLUMNS: 
#     player-team:       1 for radiant, 0 for dire
#     player-{hero}:     1 for player was this hero
#     radiant-{hero}:    1 for radiant team used this hero
#     dire-{hero}:       1 for dire team used this hero
#     {item}:            1 for player finished with this item
#     level-{}-skill-{}: 1 for player chose this skill at this level


# Get new column headers
unique_player_hero = np.unique(df_clean['Player Hero'].values).tolist()
unique_player_hero = ['player-' + s for s in unique_player_hero]
unique_radiant = np.unique(df_clean[radiant_columns].values).tolist()
unique_radiant = ['radiant-' + s for s in unique_radiant]
unique_dire = np.unique(df_clean[dire_columns].values).tolist()
unique_dire = ['dire-' + s for s in unique_dire]
unique_items = np.unique(df_clean[item_columns].values).tolist()
skill_options = []
for i in range(25):
    for j in range(4):
        column_header = 'level-' + str(i+1) + '-skill-' + str(j+1)
        skill_options.append(column_header) 

new_column_headers = ['player-team'] + unique_player_hero + unique_radiant + unique_dire + unique_items + skill_options

num_features = 1 + len(unique_player_hero + unique_radiant + unique_dire)
num_classes = len(unique_items + skill_options)
print 'number of features: ', num_features
print 'number of classes: ', num_classes
print


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


























