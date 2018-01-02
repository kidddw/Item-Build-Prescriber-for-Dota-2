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
#writer = pd.ExcelWriter('Dota_binary_data.xlsx')
writer = pd.ExcelWriter('output2.xlsx')


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


























