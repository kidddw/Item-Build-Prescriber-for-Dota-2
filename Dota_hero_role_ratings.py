#!/usr/bin/python -tt
 
"""
  Build table of hero role stats   
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


def clean_string(string):
    string = string.lower()
    string = string.replace(" ", "-")
    string = string.replace("'", "")
    return string


# =========================================================================== #
# Get data for top players 
# =========================================================================== #

# hero names
hero_names = ['Abaddon', 'Alchemist', 'Ancient Apparition', 'Anti-Mage', 'Arc Warden', 'Axe', 'Bane', 'Batrider', 'Beastmaster', 'Bloodseeker', 'Bounty Hunter', 'Brewmaster', 'Bristleback', 'Broodmother', 'Centaur Warrunner', 'Chaos Knight', 'Chen', 'Clinkz', 'Clockwerk', 'Crystal Maiden', 'Dark Seer', 'Dark Willow', 'Dazzle', 'Death Prophet', 'Disruptor', 'Doom', 'Dragon Knight', 'Drow Ranger', 'Earth Spirit', 'Earthshaker', 'Elder Titan', 'Ember Spirit', 'Enchantress', 'Enigma', 'Faceless Void', 'Gyrocopter', 'Huskar', 'Invoker', 'Io', 'Jakiro', 'Juggernaut', 'Keeper of the Light', 'Kunkka', 'Legion Commander', 'Leshrac', 'Lich', 'Lifestealer', 'Lina', 'Lion', 'Lone Druid', 'Luna', 'Lycan', 'Magnus', 'Medusa', 'Meepo', 'Mirana', 'Monkey King', 'Morphling', 'Naga Siren', 'Nature\'s Prophet', 'Necrophos', 'Night Stalker', 'Nyx Assassin', 'Ogre Magi', 'Omniknight', 'Oracle', 'Outworld Devourer', 'Pangolier', 'Phantom Assassin', 'Phantom Lancer', 'Phoenix', 'Puck', 'Pudge', 'Pugna', 'Queen of Pain', 'Razor', 'Riki', 'Rubick', 'Sand King', 'Shadow Demon', 'Shadow Fiend', 'Shadow Shaman', 'Silencer', 'Skywrath Mage', 'Slardar', 'Slark', 'Sniper', 'Spectre', 'Spirit Breaker', 'Storm Spirit', 'Sven', 'Techies', 'Templar Assassin', 'Terrorblade', 'Tidehunter', 'Timbersaw', 'Tinker', 'Tiny', 'Treant Protector', 'Troll Warlord', 'Tusk', 'Underlord', 'Undying', 'Ursa', 'Vengeful Spirit', 'Venomancer', 'Viper', 'Visage', 'Warlock', 'Weaver', 'Windranger', 'Winter Wyvern', 'Witch Doctor', 'Wraith King', 'Zeus']


strength_heroes = ['Earthshaker', 'Sven', 'Tiny', 'Kunkka', 'Beastmaster', 'Dragon Knight', 'Clockwerk', 'Omniknight', 'Huskar', 'Alchemist', 'Brewmaster', 'Treant Protector', 'Io', 'Centaur Warrunner', 'Timbersaw', 'Bristleback', 'Tusk', 'Elder Titan', 'Legion Commander', 'Earth Spirit', 'Phoenix', 'Axe', 'Pudge', 'Sand King', 'Slardar', 'Tidehunter', 'Wraith King', 'Lifestealer', 'Night Stalker', 'Doom', 'Spirit Breaker', 'Lycan', 'Chaos Knight', 'Undying', 'Magnus', 'Abaddon', 'Underlord']

agility_heroes = ['Anti-Mage', 'Drow Ranger', 'Juggernaut', 'Mirana', 'Morphling', 'Phantom Lancer', 'Vengeful Spirit', 'Riki', 'Sniper', 'Templar Assassin', 'Luna', 'Bounty Hunter', 'Ursa', 'Gyrocopter', 'Lone Druid', 'Naga Siren', 'Troll Warlord', 'Ember Spirit', 'Monkey King', 'Pangolier', 'Bloodseeker', 'Shadow Fiend', 'Razor', 'Venomancer', 'Faceless Void', 'Phantom Assassin', 'Viper', 'Clinkz', 'Broodmother', 'Weaver', 'Spectre', 'Meepo', 'Nyx Assassin', 'Slark', 'Medusa', 'Terrorblade', 'Arc Warden']

intelligence_heroes = ['Ancient Apparition', 'Bane', 'Batrider', 'Chen', 'Crystal Maiden', 'Dark Seer', 'Dark Willow', 'Dazzle', 'Death Prophet', 'Disruptor', 'Enchantress', 'Enigma', 'Invoker', 'Jakiro', 'Keeper of the Light', 'Leshrac', 'Lich', 'Lina', 'Lion', 'Nature\'s Prophet', 'Necrophos', 'Ogre Magi', 'Oracle', 'Outworld Devourer', 'Puck', 'Pugna', 'Queen of Pain', 'Rubick', 'Shadow Demon', 'Shadow Shaman', 'Silencer', 'Skywrath Mage', 'Storm Spirit', 'Techies', 'Tinker', 'Visage', 'Warlock', 'Windranger', 'Winter Wyvern', 'Witch Doctor', 'Zeus']

melee_heroes = ['Earthshaker', 'Sven', 'Tiny', 'Kunkka', 'Beastmaster', 'Dragon Knight', 'Clockwerk', 'Omniknight', 'Alchemist', 'Brewmaster', 'Treant Protector', 'Centaur Warrunner', 'Timbersaw', 'Bristleback', 'Tusk', 'Elder Titan', 'Legion Commander', 'Earth Spirit', 'Axe', 'Pudge', 'Sand King', 'Slardar', 'Tidehunter', 'Wraith King', 'Lifestealer', 'Night Stalker', 'Doom', 'Spirit Breaker', 'Lycan', 'Chaos Knight', 'Undying', 'Magnus', 'Abaddon', 'Underlord', 'Anti-Mage', 'Juggernaut', 'Phantom Lancer', 'Riki', 'Bounty Hunter', 'Ursa', 'Naga Siren', 'Ember Spirit', 'Monkey King', 'Pangolier', 'Bloodseeker', 'Faceless Void', 'Phantom Assassin', 'Broodmother','Spectre', 'Meepo', 'Nyx Assassin', 'Slark', 'Terrorblade', 'Ogre Magi', 'Dark Seer']

range_heroes = ['Ancient Apparition', 'Arc Warden', 'Bane', 'Batrider', 'Chen', 'Clinkz', 'Crystal Maiden', 'Dark Willow', 'Dazzle', 'Death Prophet', 'Disruptor', 'Drow Ranger', 'Enchantress', 'Enigma', 'Gyrocopter', 'Huskar', 'Invoker', 'Io', 'Jakiro', 'Keeper of the Light', 'Leshrac', 'Lich', 'Lina', 'Lion', 'Lone Druid', 'Luna', 'Medusa', 'Mirana', 'Morphling', 'Nature\'s Prophet', 'Necrophos', 'Oracle', 'Outworld Devourer', 'Phoenix', 'Puck', 'Pugna', 'Queen of Pain', 'Razor', 'Rubick', 'Shadow Demon', 'Shadow Fiend', 'Shadow Shaman', 'Silencer', 'Skywrath Mage', 'Sniper', 'Storm Spirit','Techies', 'Templar Assassin', 'Tinker', 'Troll Warlord', 'Vengeful Spirit', 'Venomancer', 'Viper', 'Visage', 'Warlock', 'Weaver', 'Windranger', 'Winter Wyvern', 'Witch Doctor', 'Zeus']


# roles
roles = ['carry', 'nuker', 'initiator', 'disabler', 'durable', 'escape', 'support', 'pusher', 'jungler']

# column titles
column_titles = ['primary-attribute', 'attack-type'] + roles


hero_names = [clean_string(name) for name in hero_names]
#print hero_names

# initialize dataframe, xlsx spreadsheet file
df_stats = pd.DataFrame(columns = column_titles)
df_stats = df_stats.reindex(hero_names, fill_value = 0)
writer = pd.ExcelWriter('Dota_hero_stats.xlsx')


# specify page
hero_role_page = 'http://liquipedia.net/dota2/Hero_Roles'

# parse the html using beautiful soup
soup = read_page(hero_role_page)

# split the page into segments for each heading
heading_segments = re.split(r'class="mw-headline"', str(soup))

# designate segments for each role
role_segments_dict = {}
for segment in heading_segments:
    tuples = re.findall(r'(id=")(\w+)(")', segment) 
    if len(tuples) > 0:
        title = tuples[0][1].lower()
        if title in roles:
            role_segments_dict[title] = segment

# assign role ratings to characters within dataframe 
for role in roles:
    print role
    hero_groups = re.split(r'colspan', role_segments_dict[role])
    for i in range(1,4):
        tuples = re.findall(r'(title=")([^"]+)', hero_groups[i]) 
        if len(tuples) > 0: 
            for tuple in tuples:
                name = clean_string(tuple[1])
                df_stats.loc[[name],[role]] = 4 - i

# primary attribute
df_stats.loc[[clean_string(name) for name in strength_heroes],['primary-attribute']] = 1
df_stats.loc[[clean_string(name) for name in agility_heroes],['primary-attribute']] = 2
df_stats.loc[[clean_string(name) for name in intelligence_heroes],['primary-attribute']] = 3

# attack type
df_stats.loc[[clean_string(name) for name in melee_heroes],['attack-type']] = 1
df_stats.loc[[clean_string(name) for name in range_heroes],['attack-type']] = 2




df_stats.to_excel(writer,'Sheet1')
writer.save()































