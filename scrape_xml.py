# Import the files
import xml.etree.ElementTree as ET
import pandas as pd

# Get the unique teams
def unique_teams(this_is_root):
    teams = []
    for team in this_is_root.getiterator("{http://feed.elasticstats.com/schema/baseball/v6/schedule.xsd}home"):
        teams.append(team.attrib['name'])
    for team in this_is_root.getiterator("{http://feed.elasticstats.com/schema/baseball/v6/schedule.xsd}away"):
        teams.append(team.attrib['name'])
    return list(set(teams)-set(['American League','National League']))

# Get the unique dates
def unique_dates(this_is_root):
    dates = []
    for schedule_date in this_is_root.getiterator("{http://feed.elasticstats.com/schema/baseball/v6/schedule.xsd}game"):
        dates.append(schedule_date.attrib['scheduled'][:10])
    
    return list(set(dates))

# Create a data structure of all matchups corresponding to date
def create_matchups(this_is_tree):
    list_of_matches = []
    for i in this_is_tree.findall(".//{http://feed.elasticstats.com/schema/baseball/v6/schedule.xsd}game"):
        temp_list = []
        temp_list.append(i.attrib['scheduled'][:10])
        for child in i:
            if child.tag=="{http://feed.elasticstats.com/schema/baseball/v6/schedule.xsd}home" or child.tag=="{http://feed.elasticstats.com/schema/baseball/v6/schedule.xsd}away":
                temp_list.append(child.attrib["name"])
        list_of_matches.append(temp_list)
    return list_of_matches

def main():
    # Reading in the data
    tree = ET.parse('schedule_2018.xml')
    root = tree.getroot()
    # game = tree.get
    
    # Get the unique teams
    uniq_teams = unique_teams(root)
    
    # Creating the dictionary of the league for lookup's
    uniq_teams_dict = {}
    for i in range(0,len(uniq_teams)):
        uniq_teams_dict[uniq_teams[i]] = i

    # Get the unique dates
    uniq_dates = unique_dates(root)
    print(uniq_dates)
    
    # creating the matchups
    list_of_matches = create_matchups(tree)

    # Creating the data frame
    df = pd.DataFrame(list_of_matches, columns=["Date","Home","Away"])
    df.to_csv('schedule_2018.csv',header=True,index=False,mode='w')

if __name__ == "__main__":
    main()