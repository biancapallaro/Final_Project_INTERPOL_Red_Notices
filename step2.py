import os
import json

list_results = []
# Fetch all the files inside the folder
for filename in os.listdir('./jsons'):
    print("we are going to read", filename)
    # https://stackabuse.com/reading-and-writing-json-to-a-file-in-python/
    # Open the file in (r) reading mode
    with open('./jsons/' + filename, 'r') as f:
        # Read the file in json format. Json load allows you to transfrom your results into a json. 
        #It reads it as a json. 
        data = json.load(f)
        # Loop through all the data and append
        for result in data:
           list_results.append(result)

print(list_results)
print(len(list_results))

import pandas as pd
df = pd.DataFrame(list_results)

df.to_csv(r'/Users/biancapallaro/Desktop/NEW_PROJECT/jsons_new_new.csv', index = False, header=True)