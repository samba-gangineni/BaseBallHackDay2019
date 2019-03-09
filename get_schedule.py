# Importing the required libraries
import http.client
import json

# Establishing the connection
conn = http.client.HTTPSConnection("api.sportradar.us")

config_file = json.load(open('config.json','r'))
my_key = config_file.get("my_key")

# Requesting the data
conn.request("GET","/mlb-t6/games/2019/REG/schedule.xml?api_key={}".format(my_key))

# Reading in the data
res = conn.getresponse()
data = res.read()

# Saving the response
with open('schedule.xml','wb') as f:
    f.write(data)