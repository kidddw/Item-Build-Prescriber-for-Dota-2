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


def determine_items_skills_binary(row, items_list):
    item_columns = []
    skill_columns = []
    for i in range(1, 6): 
        item_columns.append('Player Item ' + str(i))
    for i in range(1, 26):
        skill_columns.append('Skill Level ' + str(i))

    item_options = [0] * len(items_list)
    for idx, item in enumerate(items_list):
        if item in row[item_columns].values: item_options[idx] = 1

    ind = 0
    skill_options = [0] * 25 * 4
    for level in range(25):
        column_header = 'Skill Level ' + str(level+1)
        for skill in range(1,5):
            if row[column_header] == skill: skill_options[ind] = 1
            ind = ind + 1
    final_item_skill_options = tuple(item_options + skill_options)
    return final_item_skill_options


# =========================================================================== #
# =========================================================================== #
# =========================================================================== #
# =========================================================================== #


if len(sys.argv) != 2:
    print 'usage: ./Dota_data_processing.py <run type>'
    print 'run type 1: use stats format for training'
    print 'run type 2: use binary format for training'
    sys.exit(1)
run_type = int(sys.argv[1])
use_binary = False
use_stats = False
if run_type == 1: use_stats = True
if run_type == 2: use_binary = True


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
if use_binary: writer = pd.ExcelWriter('Dota_binary_data.xlsx')
if use_stats: writer = pd.ExcelWriter('Dota_stats_data.xlsx')


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


if use_stats:
# =========================================================================== #
# =========================================================================== #
# Translate Data into Match Stats Table
# =========================================================================== #
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

    print "=== using stats format ==="

    # read in hero stats spreadsheet
    xl = pd.ExcelFile("Dota_hero_stats.xlsx")
    df_hero_stats = xl.parse("Sheet1")


    # =========================================================================== #
    # Get new column headers
    # =========================================================================== #

    roles = ['carry', 'nuker', 'initiator', 'disabler', 'durable', 'escape', 'support', 'pusher', 'jungler']
    hero_types = ['melee', 'range','strength', 'agility', 'intelligence']
    player_columns = ['player-primary-attribute', 'player-attack-type'] + ['player-' + s for s in roles]
    player_team_types = ['player-team-' + s + '-score' for s in hero_types]
    player_team_roles = ['player-team-' + s for s in roles]
    opponent_team_types = ['opponent-team-' + s + '-score' for s in hero_types]
    opponent_team_roles = ['opponent-team-' + s for s in roles]

    unique_items = np.unique(df_clean[item_columns].values).tolist()
    items_headers = ['item-' + s for s in unique_items]
    skill_options = []
    for i in range(25):
        for j in range(4):
            column_header = 'level-' + str(i+1) + '-skill-' + str(j+1)
            skill_options.append(column_header) 
    skill_options = [] # comment out if wanting to traing for skills

    team_columns = player_team_types + player_team_roles + opponent_team_types + opponent_team_roles
    hero_stats_headers = player_columns + team_columns
    item_skills_headers = items_headers + skill_options
    new_column_headers = hero_stats_headers + item_skills_headers

    # Print number of features and number of classes
    num_features = len(hero_stats_headers)
    num_classes = len(item_skills_headers)
    print 'number of features: ', num_features
    print 'number of classes: ', num_classes
    print

    # =========================================================================== #
    # Reformat data into new table
    # =========================================================================== #

    df_clean["player-primary-attribute"] = df_clean["Player Hero"].apply(determine_player_hero_stats, args = (df_hero_stats,'primary-attribute'))
    df_clean["player-attack-type"] = df_clean["Player Hero"].apply(determine_player_hero_stats, args = (df_hero_stats,'attack-type'))
    for role in roles:
        df_clean[("player-" + role)] = df_clean["Player Hero"].apply(determine_player_hero_stats, args = (df_hero_stats,(role)))

    new_team_columns_tup_series = zip(*df_clean.apply(determine_player_team_stats, args = (df_hero_stats,), axis = 1))
    for idx, header in enumerate(team_columns):
        df_clean[header] = new_team_columns_tup_series[idx]

    new_items_skills_tup_series = zip(*df_clean.apply(determine_items_skills_binary, args = (unique_items,), axis = 1))
    for idx, header in enumerate(item_skills_headers):
        df_clean[header] = new_items_skills_tup_series[idx]

    df_matches_s = df_clean.loc[:, new_column_headers]

    # update excel spreadsheet file
    df_matches_s.to_excel(writer,'Sheet1')
    writer.save()



if use_binary: 
# =========================================================================== #
# =========================================================================== #
# Translate Data into Binary Table
# =========================================================================== #
# =========================================================================== #

# COLUMNS: 
#     player-{hero}:        1 for player was this hero
#     player-team-{hero}:   1 for radiant team used this hero
#     opponent-team-{hero}: 1 for dire team used this hero
#     {item}:               1 for player finished with this item
#     level-{}-skill-{}:    1 for player chose this skill at this level


# =========================================================================== #
# # Get new column headers
# =========================================================================== #

    print "=== using binary format ==="

    unique_items = np.unique(df_clean[item_columns].values).tolist()
    items_headers = ['item-' + s for s in unique_items]
    skill_options = []
    for i in range(25):
        for j in range(4):
            column_header = 'level-' + str(i+1) + '-skill-' + str(j+1)
            skill_options.append(column_header) 
    skill_options = [] # comment out if wanting to traing for skills


    hero_name_headers = ['player-' + s for s in hero_names] + ['player-team-' + s for s in hero_names] + ['opponent-team-' + s for s in hero_names]
    item_skills_headers = items_headers + skill_options
    new_column_headers = hero_name_headers + item_skills_headers

    num_features = len(hero_name_headers)
    num_classes = len(item_skills_headers)
    print 'number of features: ', num_features
    print 'number of classes: ', num_classes
    print

    # =========================================================================== #
    # Reformat data into new table
    # =========================================================================== #

    new_hero_names_tup_series = zip(*df_clean.apply(determine_heroes_binary, args = (hero_names,), axis = 1))
    for idx, header in enumerate(hero_name_headers):
        df_clean[header] = new_hero_names_tup_series[idx]

    new_items_skills_tup_series = zip(*df_clean.apply(determine_items_skills_binary, args = (unique_items,), axis = 1))
    for idx, header in enumerate(item_skills_headers):
        df_clean[header] = new_items_skills_tup_series[idx]

    df_matches_b = df_clean.loc[:, new_column_headers]

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

if use_binary: df_format = df_matches_b
if use_stats: df_format = df_matches_s

for i in range(len(df_format.index)):
    for j in range(len(new_column_headers)):
        if j <= (num_features - 1):
            # X data
            x_out.write(str(df_format.iloc[i,j]) + ' ')

        if j > (num_features - 1):
            # Y data
            y_out.write(str(df_format.iloc[i,j]) + ' ')

    x_out.write('\n')
    y_out.write('\n')


# =========================================================================== #
# Sum up item usage report
# =========================================================================== #

if use_binary: df_format = df_matches_b
if use_stats: df_format = df_matches_s

item_use_fname = 'item_usage.dat'
item_use_file = open(item_use_fname, 'w')

item_counts_dict = dict(zip(unique_items, df_format[items_headers].sum(axis=0).tolist()))
for key, value in sorted(item_counts_dict.iteritems(), key=lambda (k,v): (v,k)):
    item_use_file.write("%s: %s \n" % (key, value))




















