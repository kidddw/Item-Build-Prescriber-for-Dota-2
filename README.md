# Item-Build-Prescriber-for-Dota-2
Code written in Phyton which determines optimal character customizations determined by team composition for matches in the video game Dota 2. Tens of thousands of match data scraped from online databases using the Beautiful Soup package and organizaed in a Pandas dataframe. This data is then cleaned and reformatted for compatibility with the Neural Net Solver code.

Step 1: Run the code Dota_webscraper.py which uses the Beautiful Soup package to scrape match data from www.dotabuff.com. This data is compiled into a Pandas dataframe and is output as an Excel compatible file, Dota_raw_data.xlsx. 

Step 2: Run the code Dota_data_processing.py with the file Dota_raw_data.xlsx in the present working directory. This code cleans the data by removing anomolies and incpomplete entries. The information is then rewritten into a binary format which is output as an Excel compatible file, Dota_binary_data.xlsx, and as training data files, training_x.dat and training_y.dat, which are compatible with the Neural Net Solver code, neuralnet.py.

Step 3: Run the code neuralnet.py with the files training_x.dat, training_y.dat, and arch.dat (architecture of neural net) in the present working directory. This trains the network weights using backpropagation and conjugate gradient. 
