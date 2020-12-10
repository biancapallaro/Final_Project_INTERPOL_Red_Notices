#!/usr/bin/env python
# coding: utf-8

# # SECOND PART: IMPORT, CLEAN AND CREATE THE DATABASE FOR THE MAP

# In[ ]:


import pandas as pd
import numpy as np
import datetime as DT
import io

pd.set_option("display.max_columns", 200)
pd.set_option("display.max_colwidth", 200)


# In[2]:


#Import csv with notices
df = pd.read_csv("jsons_new.csv")


# In[3]:


df.head()


# In[4]:


#Expand the dataframe so that each item in the list nationalities gets its own row
from ast import literal_eval
df['nationalities'] = df['nationalities'].apply(literal_eval)
df.explode('nationalities')


# In[5]:


df2 = df.explode('nationalities')


# In[6]:


df2.head()


# In[7]:


#Checking the types
df2.dtypes


# In[8]:


#See if the there is any null date of birth because I will have travel when transforming into age
df2[df2.date_of_birth.isnull()]


# In[9]:


#Drop null value
df2 = df2.dropna(subset=['date_of_birth'])


# In[10]:


#Transfromed the date of birth into date format
df2.date_of_birth = pd.to_datetime(df['date_of_birth'])


# In[11]:


df2.head()


# In[12]:


#Check
df2.dtypes


# In[13]:


#Transfrom birth of date into age
now = pd.Timestamp('now')
df2['age'] = (now - df2['date_of_birth']).astype('<m8[Y]')
df2.head()


# In[14]:


#Get rid of the zero on age by transforming float into integer
df2['age'] = df2.age.round(0).astype(int)


# In[15]:


#Get rid of the caps
df2.forename = df.forename.str.title()
df2.head()


# In[16]:


#Get rid of the caps
df2.name = df.name.str.title()
df2.head()


# In[17]:


#Sort by age 
df3 = df2.sort_values(by=['age'], ascending=True).reset_index(drop=True)
df3.head()


# In[18]:


#Moving the values from the two right columns into a new column
#One that human readers can understand
df3["string"] = df3['forename'] + ' ' + df3['name'] + " - Age: " + df3["age"].map(str)
df3.head()


# In[19]:


#Check for nulls. 
df3[df3.string.isnull()]  


# In[20]:


# If I didn't do this, then the lambda thing wouldn’t work. 
df3 = df3.dropna(subset=['string'])


# In[21]:


#Html and groupby nationalities. Create properties article.
output = df3.groupby('nationalities')['string'].apply(lambda x: "<div id='notices'><P>%s</P></div>" % '</p><p> '.join(x)).reset_index(name='properties.article')
output


# In[22]:


#Check result
output.iloc[3]['properties.article']


# In[23]:


#Create properties headline for the map
results = df3.groupby('nationalities')['forename'].nunique().reset_index(name='properties.headline')
results


# In[24]:


#Merge
output = output.merge(results, how='left', on='nationalities')


# In[25]:


output


# In[59]:


#Just create properties color
output['properties.color'] = "#000066"
output.head()


# # GET COUNTRY NAMES - I wasn't sure if I would merge geojson by country code or country name. So I brought the country name from the interpol site just in case

# In[27]:


import requests
from bs4 import BeautifulSoup

my_url = "https://www.interpol.int/en/How-we-work/Notices/View-Red-Notices"
raw_html = requests.get(my_url).content
soup_doc = BeautifulSoup(raw_html, "html.parser")
print(type(soup_doc))
codes = soup_doc.find(class_="generalForm__selectArea")
countries= []
for code in codes.find_all('option')[1:]:
    country = {}
    country['country_code'] = code['value']
    country['country_name'] = code.text
    countries.append(country)
print(countries)


# In[28]:


#Created a dataframe from the list of dictionaries
import pandas as pd
df6 = pd.DataFrame(countries)
df6.head(25)


# In[29]:


#Merge the country name on the dataframe I was building for the map
df7 = df6.merge(output, left_on='country_code', right_on='nationalities')
df7 = df7.drop(columns=['country_code'])
df7


# # geojson > pandas > mapbox

# In[30]:


import requests
import json
import numpy as np
import pandas as pd
from pandas import json_normalize


# In[31]:


#Load the geojson file Exported from Mapshaper
with open('ne_50m_admin_0_countries.json') as json_data:
    geometry_data = json.load(json_data)


# In[32]:


df = pd.DataFrame.from_dict(json_normalize(geometry_data['features']), orient='columns')


# In[33]:


df.head()


# In[34]:


#Merge geojson with the dataframe I built for the map
df8 = df7.merge(df, left_on='nationalities', right_on='properties.ISO_A2')
df8.head()


# In[35]:


#Sort by country name
df8 = df8.sort_values(by='country_name', ascending=True, ignore_index=True)


# In[36]:


df8.head()


# In[37]:


#Created a new dataframe with the columns I wanted to use. 
df9 = df8[['country_name','nationalities','properties.article','properties.headline','properties.color','type','geometry.type','geometry.coordinates','properties.ISO_A2']]
df9


# In[40]:


#Added the country name to the properties.headline
df9['properties.headline2'] =  df9["country_name"] + ": " + df9["properties.headline"].map(str)


# In[48]:


#Renamed the columns
df9 = df9.rename(columns={'properties.headline': 'count', 'properties.headline2': 'properties.headline'})


# In[49]:


df9.head()


# In[50]:


#Created a function to include color ranges on my map
def by_color(cell):
    num = int(cell)
    if 0 < num < 101:
        return "#ece2f0"
    elif 100 < num < 500 :
        return "#a6bddb"
    else:
        return "#1c9099"


# In[51]:


df9['properties.color'] = df9['count'].apply(by_color)


# In[52]:


#Started the process of exporting the json file for my map. 
ok_json = json.loads(df9.to_json(orient='records'))


# In[53]:


ok_json


# In[54]:


def process_to_geojson(file):
    geo_data = {"type": "FeatureCollection", "features":[]}
    for row in file:
        this_dict = {"type": "Feature", "properties":{}, "geometry": {}}
        for key, value in row.items():
            key_names = key.split('.')
            if key_names[0] == 'geometry':
                this_dict['geometry'][key_names[1]] = value
            if str(key_names[0]) == 'properties':
                this_dict['properties'][key_names[1]] = value
        geo_data['features'].append(this_dict)
    return geo_data


# In[55]:


geo_format = process_to_geojson(ok_json)


# In[56]:


geo_format


# In[57]:


#Variable name
with open('geo-data.js', 'w') as outfile:
    outfile.write("var infoData = ")
#geojson output
with open('geo-data.js', 'a') as outfile:
    json.dump(geo_format, outfile)


# In[ ]:




