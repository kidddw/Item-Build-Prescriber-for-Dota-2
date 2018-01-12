# Item-Build-Prescriber-for-Dota-2
Code written in Phyton which determines optimal character customizations determined by team composition for matches in the video game Dota 2. Tens of thousands of match data scraped from online databases using the Beautiful Soup package and organizaed in a Pandas dataframe. This data is then cleaned and reformatted for compatibility with the custom built neuralnet package.

For use as item prescriber:
Download the file gui_item_prescriber.zip. Currently arranged for use in Linux. For windows, must uncomment two lines marked by "# FOR WINDOWS" and comment out the line marked "# FOR LINUX". For Windows, must have anaconda installed, or some other means of executing python scripts. 

Running the file Dota_item_prescriber.py brings up a GUI built with the Tkinter package. Users select the ten heroes in the match of interest and then choose the "Get Items" button in order to print prescribed items. 

Other code included in this repository:
Dota_webscraper.py:




