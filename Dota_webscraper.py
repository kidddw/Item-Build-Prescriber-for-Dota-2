#!/usr/bin/python -tt
 
"""Dota Webscraper   

   - Import match data from www.dotabuff.com
   - Latest 50 matches frome the currently highest rated players
   - Info on
       - Player Name
       - Match Index (for url identification)
       - Result (Win / Loss)
       - Match Duration
       - Player Hero 
       - List of Heroes on Both Teams
       - List of Final Items used by Player
       - List of Skills Chosen at Each Level

   - html read via Beautiful Soup
   - html parsed via regular expression searches
   - data dumped into a pandas dataframe and written to excel spreadsheet file
"""

# import libraries
import urllib2
from bs4 import BeautifulSoup
import time
import sys
import re
import numpy as np
import pandas as pd



def read_page(url):
    """
       Given input "url", return html as text file via Beautiful Soup
    """ 
    # change user agent string
    hdr = { 'User-Agent' : 'Dota bot' }
    req = urllib2.Request(url, headers = hdr)
    resolve_redirects(req)

    # query the website and return the html to the variable 'page'
    page = urllib2.urlopen(req).read()

    # parse the html using beautiful soup and store in variable 'soup'
    return BeautifulSoup(page, 'html.parser')


def resolve_redirects(url):
    """
       If site returns error code 429, wait 5 seconds and try again
    """ 
    try:
        return urllib2.urlopen(url).geturl()
    except urllib2.HTTPError as e:
        print e.code
        if e.code == 429:
             time.sleep(5);
             return resolve_redirects(url)
        raise
    print 'what?'


def print_warning(player, url, message):
    """
       Print a warning message related to a match with questionable data
    """ 
    warning_file.write(player + '\n')
    warning_file.write(url + '\n')
    warning_file.write(message + '\n')
    warning_file.write('\n')


def get_column_labels():
    """
       Return column labels used in spreadsheet
    """ 
    column_labels = ['Player Name', 'Match Index', 'Result', 'Match Duration', 'Player Hero', 'Player Team']
    for i in range(5):
        column_labels.append('Radiant Hero ' + str(i+1))
    for i in range(5):
        column_labels.append('Dire Hero ' + str(i+1))
    for i in range(5):
        column_labels.append('Player Item ' + str(i+1))
    for i in range(25):
        column_labels.append('Skill Level ' + str(i+1))
    return column_labels


def get_info_list(player_name, match_index, match_result, match_duration, 
                  player_hero, player_team, radiant_heroes, dire_heroes, skill_levels):
    """
       Return data associated with specific columns
       Note: must match order used in "get_column_labels"
    """ 
    info = [player_name, match_index, match_result, match_duration, player_hero, player_team]
    for i in range(5):
        info.append(radiant_heroes[i])
    for i in range(5):
        info.append(dire_heroes[i])
    for i in range(5):
        info.append(item_names[i])
    for i in range(25):
        not_found = True
        for j in range(4):
            if (i+1) in skill_levels[j]: 
                info.append(j+1)
                not_found = False
        if not_found: info.append(0)
    return info


def get_num_date(date):
    """
       Return a numerical value for the date 
       input (tuple of ints): day (ex. 2), month (ex. 12), year (ex. 2017)
    """
    day = date[0]
    month = date[1]
    year = date[2]
    days_index = 10000 * year + 100 * month + day
    return days_index

    
def date_string(date):
    string = str(date[1]) + '/' + str(date[0]) + '/' + str(date[2])
    return string


def get_num_month(month_abb):
    if month_abb == 'Jan': month = 1
    if month_abb == 'Feb': month = 2
    if month_abb == 'Mar': month = 3
    if month_abb == 'Apr': month = 4
    if month_abb == 'May': month = 5
    if month_abb == 'Jun': month = 6
    if month_abb == 'Jul': month = 7
    if month_abb == 'Aug': month = 8
    if month_abb == 'Sep': month = 9
    if month_abb == 'Oct': month = 10
    if month_abb == 'Nov': month = 11
    if month_abb == 'Dec': month = 12
    return month



# =========================================================================== #
# Get data for top players 
# =========================================================================== #

# initialize dataframe, xlsx spreadsheet file, and warning log file
df_matches = pd.DataFrame(columns=get_column_labels())
writer = pd.ExcelWriter('Dota_raw_data.xlsx')
warning_file = open('warnings.log', 'w')

# number of player pages (50 per)
num_player_pages = 10
# number of match pages (50 per)
num_match_pages = 10

# skip matches before most recent patch date (Day, Month, Year)
patch_date = (17, 11, 2017)

print


# =========================================================================== #
# Get indices of top {50 x num_pages} players
# =========================================================================== #
ind = -1
player_names = []
player_indices = []
player_names_dict = {}
for i in range(1,num_player_pages+1):

    print 'reading leaderboard page ' + str(i)

    # specify the url
    leaderboard_page = 'https://www.dotabuff.com/players/leaderboard?page=' + str(i)

    # parse the html using beautiful soup
    soup = read_page(leaderboard_page)

    # get names of each player
    tuples = re.findall(r'(data-value=")([^"]+)(")', str(soup)) 
    for tuple in tuples:
        player_names.append(tuple[1])

    # search for player indices
    tuples = re.findall(r'(link-type-player" href="/players/)(\d+)', str(soup)) 
    for tuple in tuples:
        ind = ind + 1
        player_indices.append(tuple[1])
        player_names_dict[tuple[1]] = player_names[ind]

print


for player_index in player_indices:

    # =========================================================================== #
    # Get indices of matches since latest patch (max of {50 x num_match_pages})
    # =========================================================================== #
    match_indices = []

    # get player name
    player_name = player_names_dict[player_index]

    dates = []
    match_dates = {}
    dates_ind = -1
    before_patch = True

    match_page_index = 0
    while before_patch and (match_page_index + 1) <= num_match_pages:

        match_page_index = match_page_index + 1

        print 'reading matches page ' + str(match_page_index) + ' of ' + player_name

        # specify the url
        matches_page = 'https://www.dotabuff.com/players/' + str(player_index) + '/matches?enhance=overview&page=' + str(match_page_index)

        # parse the html using beautiful soup
        soup = read_page(matches_page)

        # split into segments around the body of the page
        body_segments = re.split(r'tbody', str(soup))

        # determine the dates of each match -- return as tuple: Day, Month, Year
        tuples = re.findall(r'(datetime="[^"]+" title="\w\w\w,\s)(\d\d)(\s)(\w\w\w)(\s)(\d\d\d\d)', body_segments[3]) 
        for tuple in tuples:
            dates.append((int(tuple[1]), get_num_month(tuple[3]), int(tuple[5])))

        # determine match indices and define dictionary for dates of each match index
        tuples = re.findall(r'(<a href="/matches/)(\d+)', str(soup)) 
        for tuple in tuples:
            dates_ind = dates_ind + 1
            match_indices.append(tuple[1])
            match_dates[tuple[1]] = dates[dates_ind]

        # if last match occured before patch date, stop reading match list pages
        last_match_index = match_indices[-1]
        if get_num_date(match_dates[last_match_index]) <= get_num_date(patch_date): 
            before_patch = False


    # =========================================================================== #
    # Get features from each match
    # =========================================================================== #
    for match_index in match_indices:

        # check if match occured after patch date
        if get_num_date(match_dates[match_index]) <= get_num_date(patch_date): continue

        # specify the url
        match_page = 'https://www.dotabuff.com/matches/' + str(match_index) + '/builds'

        # parse the html using beautiful soup
        soup = read_page(match_page)

        # separate html by segments related to each player
        player_segments = re.split(r'performance-artifact', str(soup))

        # =========================================================================== #
        # Get list of heroes 
        # =========================================================================== #

        # get heroes in match
        hero_index = -1
        heroes = []
        player_team = 'none'
        player_hero = 'none'
        player_info = 'none'
        for segment in player_segments:
            hero_index = hero_index + 1

            # skip first segment which is header info
            if hero_index == 0: continue

            # read hero names from segments
            tuples = re.findall(r'(href="/heroes/)([\w-]+)', segment) 
            if len(tuples) < 1 or len(tuples[0]) < 2: print_warning(player_name, match_page, 'no hero name')
            else: heroes.append(tuples[0][1])

            # choose segment related to specified player as 'player_info'
            if re.search(player_index, segment):
                player_info = segment
                if not(len(tuples) < 1 or len(tuples[0]) < 2): player_hero = tuples[0][1]
                if hero_index <= 5: player_team = 'radiant'
                else: player_team = 'dire'
       
        # separate into Radiant (first 5) and Dire (latter 5) and sort alphabetically
        radiant_heroes = heroes[:5]
        radiant_heroes.sort()
        dire_heroes = heroes[5:]
        dire_heroes.sort() 

        # replace all missing heroes with string label "none"
        while len(radiant_heroes) < 5:
            radiant_heroes.append('none')
        while len(dire_heroes) < 5:
            dire_heroes.append('none')


        # =========================================================================== #
        # Get win/loss result
        # =========================================================================== #

        tuples = re.findall(r'(match-result team )(\w+)', str(soup)) 
        if len(tuples) != 1: print_warning(player_name, match_page, 'too many/few win statements found')
        else: winning_team = tuples[0][1]
        if player_team == winning_team: match_result = 'win'
        else: match_result = 'loss'


        # =========================================================================== #
        # Get match duration
        # =========================================================================== #
        
        tuples = re.findall(r'(duration">)([\d:]+)(<)', str(soup)) 
        if len(tuples) != 1: print_warning(player_name, match_page, 'match duration not found')
        else: match_duration = tuples[0][1]
        if len(match_duration) == 5: match_duration = '0:' + match_duration


        # =========================================================================== #
        # Get (final build) items as 'item_names'
        # =========================================================================== #

        # separate final build items from all items bought (using skills section identifier)
        item_grouping_segments = re.split(r'skill-choices', player_info)

        # separate player segment by (final build) item
        item_segments = re.split(r'image-container-bigicon', item_grouping_segments[0])

        # identify (final build) item names
        item_names = []
        for item in item_segments:
            tuples = re.findall(r'(/items/)([\w-]+)(/)', item)
            if len(tuples) > 1: print_warning(player_name, match_page, 'too many items found')
            if len(tuples) == 1: item_names.append(tuples[0][1])
        if len(item_names) == 0: print_warning(player_name, match_page, 'no items found')
        item_names.sort()

        # add string label "none" for no item appearing
        while len(item_names) < 5:
            item_names.append('none')


        # =========================================================================== #
        # Get skill choices
        # =========================================================================== #

        # separate player segment by skill
        skill_segments = re.split(r'class="skill"', player_info)

        # identify levels at which given skill was selected as 'skill_levels'
        # list of lists -- first index is which skill, second is a list of 
        #     levels that skill was chosen at
        skill_levels = []
        for skill in skill_segments:
            
            # determine at what levels this skill was chosen      
            tuples = re.findall(r'(class="entry\s)(\w+)(")', skill) 
            levels_chosen = []
            level = 0
            for tuple in tuples:
                level = level + 1
                if tuple[1] == 'choice': levels_chosen.append(level)

            if len(tuples) == 25: skill_levels.append(levels_chosen) 

        # add empty list for a skill that was never taken
        while len(skill_levels) < 4:
            skill_levels.append([])  


        # =========================================================================== #
        # Append new match data to dataframe and update Excel spreadsheet file
        # =========================================================================== #

        print player_name, player_hero, date_string(match_dates[match_index])
        print match_page
        print

        match_data = get_info_list(player_name, match_index, match_result, match_duration, 
                                   player_hero, player_team, radiant_heroes, dire_heroes, skill_levels)
        df_match = pd.DataFrame([match_data], columns = get_column_labels())
        df_matches = df_matches.append(df_match, ignore_index = True)

    df_matches.to_excel(writer,'Sheet1')
    writer.save()



    








