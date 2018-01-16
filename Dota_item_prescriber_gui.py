#!/usr/bin/python -tt

import sys
import numpy as np
#from neuralnet import MLPClassifier
from Tkinter import *
from PIL import ImageTk, Image
import sklearn.neural_network as sklann
import pickle


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


def get_hero_names():
    strength_radiant_heroes = ['Earthshaker', 'Sven', 'Tiny', 'Kunkka', 'Beastmaster', 'Dragon Knight', 'Clockwerk', 'Omniknight', 'Huskar', 'Alchemist', 'Brewmaster', 'Treant Protector', 'Io', 'Centaur Warrunner', 'Timbersaw', 'Bristleback', 'Tusk', 'Elder Titan', 'Legion Commander', 'Earth Spirit', 'Phoenix']
    strength_dire_heroes = ['Axe', 'Pudge', 'Sand King', 'Slardar', 'Tidehunter', 'Wraith King', 'Lifestealer', 'Night Stalker', 'Doom', 'Spirit Breaker', 'Lycan', 'Chaos Knight', 'Undying', 'Magnus', 'Abaddon', 'Underlord']
    agility_radiant_heroes = ['Anti-Mage', 'Drow Ranger', 'Juggernaut', 'Mirana', 'Morphling', 'Phantom Lancer', 'Vengeful Spirit', 'Riki', 'Sniper', 'Templar Assassin', 'Luna', 'Bounty Hunter', 'Ursa', 'Gyrocopter', 'Lone Druid', 'Naga Siren', 'Troll Warlord', 'Ember Spirit', 'Monkey King', 'Pangolier']
    agility_dire_heroes = ['Bloodseeker', 'Shadow Fiend', 'Razor', 'Venomancer', 'Faceless Void', 'Phantom Assassin', 'Viper', 'Clinkz', 'Broodmother', 'Weaver', 'Spectre', 'Meepo', 'Nyx Assassin', 'Slark', 'Medusa', 'Terrorblade', 'Arc Warden']
    intelligence_radiant_heroes = ['Crystal Maiden', 'Puck', 'Storm Spirit', 'Windranger', 'Zeus', 'Lina', 'Shadow Shaman', 'Tinker', 'Nature\'s Prophet', 'Enchantress', 'Jakiro', 'Chen', 'Silencer', 'Ogre Magi', 'Rubick', 'Disruptor', 'Keeper of the Light', 'Skywrath Mage', 'Oracle', 'Techies', 'Dark Willow']
    intelligence_dire_heroes = ['Bane', 'Lich', 'Lion', 'Witch Doctor', 'Enigma', 'Necrophos', 'Warlock', 'Queen of Pain', 'Death Prophet', 'Pugna', 'Dazzle', 'Leshrac', 'Dark Seer', 'Batrider', 'Ancient Apparition', 'Invoker', 'Outworld Devourer', 'Shadow Demon', 'Visage', 'Winter Wyvern']
    hero_groups = [strength_radiant_heroes, strength_dire_heroes, agility_radiant_heroes, agility_dire_heroes, intelligence_radiant_heroes, intelligence_dire_heroes]
    return hero_groups
    


#=====================================================

class MyFirstGUI:
    def __init__(self, master):
        self.master = master
        master.title("Dota 2 Item Prescriber")

        background = Image.open("./images/bg_03.jpg")
        w = background.size[0]
        h = background.size[1]
#        logo_image = Image.open("./images/dota_logo.png")
#        background.paste(logo_image, (int(w/1.77), h/4), logo_image)
        background_image = ImageTk.PhotoImage(background)

        master.geometry('%dx%d+0+0' % (int(w*0.75),h))
        bg_label = Label(master, image=background_image)
        bg_label.image = background_image
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)


        self.player_hero = str()
        self.player_team_heroes = []
        self.opponent_team_heroes = []
        self.player_count = 0

        file_name = 'item_list.txt'
        f = open(file_name, 'rU')
        library = f.read()
        item_names = library.split()
        self.item_names = [ name[5:] for name in item_names]

        hero_groups = get_hero_names()
        self.hero_list = list(sum(hero_groups, []))
        self.hero_names = sorted([clean_string(name) for name in self.hero_list])

        #==================================#
        # Listboxes
        #==================================#
        text = Entry(master)
        self.listbox1 = Listbox(master)
        self.listbox1.config(height=1, bd=2)
#        self.listbox1.grid(row=12, column=0, columnspan=4, rowspan = 1)
        self.listbox1.grid(row=1, column=13, columnspan=4, rowspan = 1, padx=28, pady=2)
        self.listbox2 = Listbox(master)
        self.listbox2.config(height=4, bd=2)
        self.listbox2.grid(row=3, column=13, columnspan=4, rowspan = 2, padx=28, pady=2)
        self.listbox3 = Listbox(master)
        self.listbox3.config(height=5, bd=2)
        self.listbox3.grid(row=2, column=17, columnspan=4, rowspan = 2, padx=28, pady=2)

        self.listbox4 = Listbox(master)
        self.scrollbar4 = Scrollbar(master, orient=VERTICAL)
        self.listbox4.config(height=2, width=45, bd=2, yscrollcommand=self.scrollbar4.set)
        self.listbox4.grid(row=5, column=13, columnspan=6, rowspan = 1, padx=28, pady=2)
        self.scrollbar4.configure(command=self.listbox4.yview)
        self.scrollbar4.grid(row=5, column=19, rowspan=1, sticky=NS, pady=2)

        self.listbox5 = Listbox(master)
        self.scrollbar5 = Scrollbar(master, orient=VERTICAL)
        self.listbox5.config(height=7, bd=2, yscrollcommand=self.scrollbar5.set)
        self.listbox5.grid(row=7, column=15, columnspan=4, rowspan = 3, padx=28, pady=2)
        self.scrollbar5.configure(command=self.listbox5.yview)
        self.scrollbar5.grid(row=7, column=18, rowspan=3, sticky=NS)

        #==================================#
        # Hero Buttons
        #==================================#
        self.hero_buttons = []
        self.hero_photos = []
        actions = []
        for idx, hero in enumerate(self.hero_list):
            action = lambda x = hero: self.assign_hero(x)
            self.hero_buttons.append(Button(master, text=clean_string(hero), command = action))
            self.hero_photos.append(ImageTk.PhotoImage(Image.open("./images/" + clean_string_for_shell(hero) + "_sb.png"))) 
            self.hero_buttons[-1].config(image=self.hero_photos[-1], bg="black", bd=1, highlightbackground='black', highlightthickness=2, overrelief=GROOVE, cursor="plus")
            # locations in grid
            if hero in hero_groups[0]:
                index = hero_groups[0].index(hero)
                row_index = index / 4
                col_index = index % 4
            if hero in hero_groups[1]:
                index = hero_groups[1].index(hero)
                row_index = 6 + index / 4
                col_index = index % 4
            if hero in hero_groups[2]: 
                index = hero_groups[2].index(hero)
                row_index = index / 4
                col_index = 4 + index % 4
            if hero in hero_groups[3]:
                index = hero_groups[3].index(hero)
                row_index = 6 + index / 4
                col_index = 4 + index % 4
            if hero in hero_groups[4]:
                index = hero_groups[4].index(hero)
                row_index = index / 4
                col_index = 8 + index % 4
            if hero in hero_groups[5]:
                index = hero_groups[5].index(hero)
                row_index = 6 + index / 4
                col_index = 8 + index % 4
            self.hero_buttons[-1].grid(row=row_index, column=col_index, padx=2, pady=2)

        #==================================#
        # Utility buttons
        #==================================#
        self.button_items = Button(master, text='Get Items', command = self.prescribe_items)
        self.button_items.grid(row = 8, column = 12, columnspan = 4)

        self.button_reset = Button(master, text='Reset', command = self.reset)
        self.button_reset.config(width=20)
        self.button_reset.grid(row = 10, column = 15, rowspan=1, columnspan=3)

        #==================================#
        # Text Labels
        #==================================#
        self.label1 = Label(master, text="Player Hero")
        self.label1.config(bd=2, highlightbackground='black', highlightthickness=2)
        self.label1.grid(row=0, column=13, columnspan=4, padx=8, pady=2)
        self.label2 = Label(master, text="Player Team Heroes")
        self.label2.grid(row=2, column=13, columnspan=4, padx=8, pady=2)
        self.label2.config(bd=2, highlightbackground='black', highlightthickness=2)
        self.label3 = Label(master, text="Opponent Team Heroes")
        self.label3.grid(row=1, column=17, columnspan=4, padx=8, pady=2)
        self.label3.config(bd=2, highlightbackground='black', highlightthickness=2)

        master.bind('<Button-1>', self.keep_flat)






    def keep_flat(self, event):       # on click,
        if event.widget in self.hero_buttons: # if the click came from a hero button
            event.widget.config(relief=FLAT, highlightbackground='red') # enforce an option


    def assign_hero(self, hero_name_print):
        name = clean_string(hero_name_print)
        if name not in self.hero_names:  
            self.listbox4.insert(END, "Name not in library of hero names. Please try again. \n")
            self.listbox4.yview(END) 
        elif name in self.opponent_team_heroes or name in self.player_team_heroes or name == self.player_hero:
            self.listbox4.insert(END, "This hero has already been entered. Please try again. \n") 
            self.listbox4.yview(END) 
        else:
            if self.player_count == 0:
                self.player_hero = name
                self.listbox1.insert(END, hero_name_print)
                self.player_count = self.player_count + 1
            elif self.player_count >= 1 and self.player_count <= 4:
                self.player_team_heroes.append(name)
                self.listbox2.insert(END, hero_name_print)
                self.player_count = self.player_count + 1
            elif self.player_count >= 5 and self.player_count <= 9:
                self.opponent_team_heroes.append(name)
                self.listbox3.insert(END, hero_name_print)
                self.player_count = self.player_count + 1
            else: 
                self.listbox4.insert(END, "Already entered all heroes. \n")
                self.listbox4.yview(END)


    def prescribe_items(self):
        if len(self.opponent_team_heroes) != 5:
            self.listbox4.insert(END, "Not all heroes assigned.") 
            return
        # Create vector for feeding forward
        input_list = [0] * len(self.hero_names) *3 
        for idx, name in enumerate(self.hero_names):
            if name == self.player_hero:
                input_list[idx] = 1
        for idx, name in enumerate(self.hero_names):
            if name in self.player_team_heroes:
                input_list[idx + len(self.hero_names)] = 1
        for idx, name in enumerate(self.hero_names):
            if name in self.opponent_team_heroes:
                input_list[idx + len(self.hero_names) * 2] = 1
        # Feed forward in neural net
        input_X = [input_list]
        filename = 'finalized_model.sav'
        loaded_model = pickle.load(open(filename, 'rb'))
        prediction = loaded_model.predict(input_X)[0]
#        # Feed forward in neural net
#        input_X = np.matrix([input_list])
#        clf = MLPClassifier(hidden_layer_sizes=(250,))
#        clf.read_weights(input_X.shape[1], len(self.item_names))
#        prediction = clf.predict(input_X, threshold = 0.3)
        # Print resulting items
        for idx, item in enumerate(self.item_names):
            if prediction[idx] == 1:
                self.listbox5.insert(END, self.item_names[idx]) 


    def reset(self):
        self.player_hero = str()
        self.player_team_heroes = []
        self.opponent_team_heroes = []
        self.player_count = 0
        self.listbox1.delete(0, END)
        self.listbox2.delete(0, END)
        self.listbox3.delete(0, END)
        self.listbox4.delete(0, END)
        self.listbox5.delete(0, END)
        for button in self.hero_buttons:
            button.config(relief=RAISED, overrelief=GROOVE, highlightbackground='black')


#=====================================================





if __name__ == '__main__':

    root = Tk()
    my_gui = MyFirstGUI(root)
    root.mainloop()
















