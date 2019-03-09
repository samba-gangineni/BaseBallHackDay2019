# Importing the required libraries
import http.client
import json
import pandas as pd
import xml.etree.ElementTree as ET
import time

# Get the result
def get_result(tree):
    score = 0
    for i in tree.findall("{http://feed.elasticstats.com/schema/baseball/v6/game.xsd}home"):
        home_team = i.attrib['name']
        score+=int(i.attrib['runs'])

    for i in tree.findall("{http://feed.elasticstats.com/schema/baseball/v6/game.xsd}away"):
        away_team= i.attrib['name']
        score-=int(i.attrib['runs'])

    if score>0:
        return home_team
    elif score==0:
        return "tie"
    else:
        return away_team

# Establishing the connection
conn = http.client.HTTPSConnection("api.sportradar.us")

config_file = json.load(open('config.json','r'))
my_key = config_file.get("my_key")

# Get the data frame of 100 matches
df = pd.read_csv('schedule_2018.csv')
df = df.loc[:50]
id_s = df['Id'].tolist()

# Requesting the data
results = []
for i in id_s:
    conn.request("GET","/mlb-t6/games/{}/boxscore.xml?api_key={}".format(i,my_key))
    # Reading in the data
    res = conn.getresponse()
    data = res.read()
    tree = ET.fromstring(data)
    result = get_result(tree)
    results.append(result)
    time.sleep(10)


# Adding the column to the data frame
df['Results'] = results
print(df.head())
df.to_csv('results_2018.csv',header=True,index=False,mode='w')