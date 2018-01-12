#!/usr/bin/python -tt

import sys
import numpy as np
from neuralnet import MLPClassifier
from Tkinter import *
#from PIL import ImageTk, Image # FOR WINDOWS


def Button1():
	listbox.insert(END, "button1 pressed")

def assign_hero(hero_name_print):
    global player_count
    global player_hero
    name = clean_string(hero_name_print)
    if player_count == 0:
        if name not in hero_names:  
            listbox4.insert(END, "Name not in library of hero names. Please try again. \n")
        else:
            player_hero = name
            listbox1.insert(END, hero_name_print)
            player_count = player_count + 1
    elif player_count >= 1 and player_count <= 4:
        if name not in hero_names: 
            listbox4.insert(END, "Name not in library of hero names. Please try again. \n")
        elif name in player_team_heroes or name == player_hero: 
            listbox4.insert(END, "This hero has already been entered. Please try again. \n") 
        else:
            player_team_heroes.append(name)
            listbox2.insert(END, hero_name_print)
            player_count = player_count + 1
    elif player_count >= 5 and player_count <= 9:
        if name not in hero_names: 
            listbox4.insert(END, "Name not in library of hero names. Please try again. \n")
        elif name in opponent_team_heroes or name in player_team_heroes or name == player_hero: 
            listbox4.insert(END, "This hero has already been entered. Please try again. \n") 
        else:
            opponent_team_heroes.append(name)
            listbox3.insert(END, hero_name_print)
            player_count = player_count + 1
    else: 
        listbox4.insert(END, "Already entered all heroes. \n") 


def clean_string(string):
    string = string.lower()
    string = string.replace(" ", "-")
    string = string.replace("'", "")
    return string


def clean_string_for_shell(string):
    string = string.lower()
    string = string.replace(" ", "_")
    string = string.replace("'", "")
    return string


def prescribe_items(player, player_team, opponent_team):
    global hero_names
    global item_names

    if len(opponent_team) != 5:
        listbox4.insert(END, "Not all heroes assigned.") 
        return

    # Create vector for feeding forward
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

    # Feed forward in neural net
    clf = MLPClassifier(hidden_layer_sizes=(250,))
    clf.read_weights(input_X.shape[1], len(item_names))
    prediction = clf.predict(input_X)

    # Print resulting items
    for idx, item in enumerate(item_names):
        if prediction[idx] == 1:
            listbox5.insert(END, item_names[idx]) 




if __name__ == '__main__':

  root = Tk()

  player_hero = str()
  player_team_heroes = []
  opponent_team_heroes = []
  player_count = 0

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
  hero_names = [clean_string(name) for name in hero_list]
  print hero_names
  hero_names = sorted([clean_string(name) for name in hero_list])
  print hero_names


  # Hero Buttons

  hero_buttons = []
  hero_photos = []
  actions = []
  for idx, hero in enumerate(hero_list):
      action = lambda x = hero: assign_hero(x)
      hero_buttons.append(Button(root, text=clean_string(hero), command = action))
      hero_photos.append(PhotoImage(file="./images/" + clean_string_for_shell(hero) + "_sb.png"))  # FOR LINUX
#      hero_photos.append(ImageTk.PhotoImage(Image.open("./images/" + clean_string_for_shell(hero) + "_sb.png")))  # FOR WINDOWS
      hero_buttons[-1].config(image=hero_photos[-1],width="59",height="33",activebackground="black",bg="black", bd=0)
      # locations in grid
      if hero in strength_radiant_heroes:
          index = strength_radiant_heroes.index(hero)
          row_index = index / 4
          col_index = index % 4
      if hero in strength_dire_heroes:
          index = strength_dire_heroes.index(hero)
          row_index = 6 + index / 4
          col_index = index % 4
      if hero in agility_radiant_heroes: 
          index = agility_radiant_heroes.index(hero)
          row_index = index / 4
          col_index = 4 + index % 4
      if hero in agility_dire_heroes:
          index = agility_dire_heroes.index(hero)
          row_index = 6 + index / 4
          col_index = 4 + index % 4
      if hero in intelligence_radiant_heroes:
          index = intelligence_radiant_heroes.index(hero)
          row_index = index / 4
          col_index = 8 + index % 4
      if hero in intelligence_dire_heroes:
          index = intelligence_dire_heroes.index(hero)
          row_index = 6 + index / 4
          col_index = 8 + index % 4
      hero_buttons[-1].grid(row=row_index, column=col_index)


  action = lambda x = player_hero, y = player_team_heroes, z = opponent_team_heroes: prescribe_items(x, y, z)
  button_items = Button(root, text='Get Items', command = action)
  button_items.grid(row = 12, column = 8, columnspan = 4)


  text = Entry(root)
  scrollbar = Scrollbar(root, orient=VERTICAL)
  listbox1 = Listbox(root)
  listbox1.config(height=1)
  listbox2 = Listbox(root)
  listbox2.config(height=4)
  listbox3 = Listbox(root)
  listbox3.config(height=5)
  listbox4 = Listbox(root)
  listbox4.config(height=4)
  listbox5 = Listbox(root)
  listbox5.config(height=6)
  scrollbar.configure(command=listbox1.yview)
  scrollbar.configure(command=listbox4.yview)


  listbox1.grid(row=12, column=0, columnspan=4, rowspan = 1)
  listbox2.grid(row=14, column=0, columnspan=4, rowspan = 4)
  listbox3.grid(row=13, column=4, columnspan=4, rowspan = 5)
  listbox4.grid(row=18, column=0, columnspan=8, rowspan = 4)
  listbox5.grid(row=13, column=8, columnspan=4, rowspan = 6)

  Label(root, text="Player Hero").grid(row=11, column=0, columnspan=4)
  Label(root, text="Player Team Heroes").grid(row=13, column=0, columnspan=4)
  Label(root, text="Opponent Team Heroes").grid(row=12, column=4, columnspan=4)

  root.mainloop()
















