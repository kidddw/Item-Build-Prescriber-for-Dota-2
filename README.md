# Item-Build-Prescriber-for-Dota-2
Code written in Phyton which determines optimal character customizations determined by team composition for matches in the video game Dota 2. Tens of thousands of match data scraped from online databases using the Beautiful Soup package and organizaed in a Pandas dataframe. This data is then cleaned and reformatted for compatibility with the custom built neuralnet package.

For the primary use as item prescriber:
Running the file Dota_item_prescriber_gui.py (Dota_item_prescriber_gui_win.py for Windows) brings up a GUI built with the Tkinter package. Users select the ten heroes in the match of interest and then choose the "Get Items" button in order to print prescribed items. Can run Dota_item_prescriber.py for terminal entry of heros and output. Note: For Windows, must have anaconda installed, or some other means of executing python scripts.

Must be included in the present working directory: 
item_list.txt: a list of all items (in alphabetical order) which may be potential outputs. 
weights.dat: trained weights which describe the mapping from input hero configuration to output item list




Other code included in this repository:

Dota_webscraper.py:
Uses the Beautiful Soup package to iteratively read html's from the webiste dotabuff.com. Loops over top 500 players and each of their matches since the last major patch date. Information is gathered into a Pandas dataframe and printed to an excel compatible file, Dota_raw_data.xlsx.

Dota_data_procecessing.py:
Reads in the spreadsheet file Dota_raw_data.xlsx as a pandas dataframe. First, this data is cleaned, eliminating matches that contain incomplete or anomalous data. This data may then be transformed into two possible formats: (1) representation of player hero and team heroes using stats related to these heroes roles and properties as available on the dota 2 home webpage, output as Dota_stats_data.xlsx. (2) a binary representation which uses column titles for all possible player heroes, player team heroes, and opponent team heroes -- 1 indicates that this hero is present in the current match, and 0 indicates that hero is not present. This format is output as Dota_binary_data.xlsx and is expected when using the following code for neural net classification. Each format includes information on items present in match using the binary mapping to names. 

neuralnet.py:
The latest artificial neural net package (similar to MLPClassifier from scikit_learn). Used to train weights related to mapping heroes in match to items used. Generates weights.dat which contains this result.

conj_grad.py:
The latest conjugate gradient package used as an option in neuralnet.py










