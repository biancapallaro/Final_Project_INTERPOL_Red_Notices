#My website is https://www.interpol.int/en/How-we-work/Notices/View-Red-Notices. If you go to 
#Network you can find a hidden API. The main challenge is that the max results is always 160. 

import requests
from bs4 import BeautifulSoup
import json 

#Scraping through the country drop down menu to get the country names and codes
my_url = "https://www.interpol.int/en/How-we-work/Notices/View-Red-Notices"
raw_html = requests.get(my_url).content
soup_doc = BeautifulSoup(raw_html, "html.parser")
print(type(soup_doc))

#Created a list of dictionaries with country code + country name
codes = soup_doc.find(class_="generalForm__selectArea")
countries= []
for code in codes.find_all('option')[1:]:
    country = {}
    country['country_code'] = code['value']
    country['country_name'] = code.text
    countries.append(country)
#If I would want to get a dataframe of this I could just do:
#import pandas as pd
#df2 = pd.DataFrame(countries)

#I now created a list with only the codes of the countries because that is what I need to include as a 
#parameter in my url. 

codes = soup_doc.find(class_="generalForm__selectArea")
list_codes = []
for code in codes.find_all('option')[1:]:
    country_code = code['value']
    list_codes.append(country_code)
print(len(list_codes))

#I now looped through each country using the list I created before. 
# Like I said, the maximum number of results the website allows you to get is 160. But, there are some countries who have more 
#fugitives than 160. We can know this because the hidden api allows you to see the total number. So, in those cases, I had to use another filter as a parameter in the url: AGE. 
#If the number of results for a country is larger than 160. Loop through a specific age range: from 0 to 100 counting by 2. 
#Also, because my original code kept breaking because the INTERPOl website took too long to provide the requests. 
#So, after consulting with TA's, stackoverflow, developer friends, the best option was to go saving the results from each country into my computer as a json file. 
#in my computer and do a loop to keep asking INTERPOL (at least 5 times) for the results in case the file of that country is not in my computer.


import requests
import time
import os.path 
#I'm going to use os.path library to check if the file already exists or not in my folder. 

for country in list_codes:
#This will create the variable of the json file name (one for each country). 
    file_name = f'./jsons/{country}.json'

#I'm going to say: if the file for that country already exists, do nothing with that country and continue with the next country. 
#https://stackoverflow.com/questions/82831/how-do-i-check-whether-a-file-exists-without-exceptions

    if os.path.isfile(file_name):
        print("This country already exists in my folder:", country, "continue with the next country")
        continue

    print("We are now going to process the following country:", country)

#So, if it continues with the next country because that file is not my computer, I will get the total number of people for that country and the results. 
    time.sleep(1)
    url = f"https://ws-public.interpol.int/notices/v1/red?nationality={country}&resultPerPage=160"
    response = requests.get(url, allow_redirects=True)
    data = response.json()
    total = data['total']
    notices= data['_embedded']['notices']
#Now we will use the total variable to see if it has more than 160 results. 
    if total<=160:
        print("This country has less than 160 results")
#If it has less than 160 results, we can easily get the information and save it into our JSON folder.
#Now I will create the file in my computer. "Open" crates the file and writes it. 
#w means writing. f means file. https://www.pythonforbeginners.com/files/reading-and-writing-files-in-python. I'm using "with" because every file I open, I will need to close it. 
        with open(file_name, 'w') as f:    
#This will convert the list of dictionaries we got from the country to a json format and we write it into the file. 
            f.write(json.dumps(notices, indent=4))
            print("It was correctly converted and written in the file")
    else:
        print("This country has more than 160 results")
#If the country has 160 or more results I will have to filter by age range and get those results. 
        age_filters = range(0, 100, 2) 
#I will use a range of age that goes from 0 to 100 counting by 2
        country_notices= []
#create an empty list to add all the different age ranges dictionaries into one for each country.
        for age_min in age_filters:
            time.sleep(1)
            age_max = age_min + 2
            print(age_min, age_max)
#The url accepts two parameters: age max and min. In this case for each number that goes from 1 to 100, age_max will be the number + 4
            try_times = 5
#We are going to try to search for the results 5 times because it keeps breaking. We are going to try until it works.
            for i in range(try_times):
                try:
                    print("We are going to try for the first time")
                    url2= f"https://ws-public.interpol.int/notices/v1/red?&nationality={country}&ageMin={age_min}&ageMax={age_max}&resultPerPage=160"
                    response= requests.get(url2, allow_redirects=True)
                    data_countries_more_160 = response.json()
                    notices_countries_more_160 = data_countries_more_160['_embedded']['notices']
                    country_notices.extend(notices_countries_more_160)
                    break
#When append() method adds its argument as a single element to the end of a list, the length of the list itself will increase by one. Whereas extend() method iterates over its argument adding each element to the list, extending the list
                except:
                    print: "It broke. But we will keep trying"
        
            with open(file_name, 'w') as f:
                f.write(json.dumps(country_notices, indent = 4))
                print("It was correctly converted and written in the file")

