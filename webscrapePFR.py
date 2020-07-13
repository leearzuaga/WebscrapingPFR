import requests
from bs4 import BeautifulSoup as BS 
import pandas as pd 
from sys import argv

letter_url = 'https://www.pro-football-reference.com/players/{letter}/'
players_url = 'https://www.pro-football-reference.com/players/{letter}/{player_code}.htm'


player_first_name = input("What is the player's first name? ")
player_last_name = input("What is the player's last name ")
inputted_player_name = player_first_name + " " + player_last_name

# Archived page is organized by player last name

letter_to_request = player_last_name[0].upper()
letter_url = letter_url.format(letter = letter_to_request)

res = requests.get(letter_url)
soup = BS(res.content, 'lxml')
section = soup.find(id = "all_players")
p_tags = section.find_all('p')
a_tags = [p.find('a', href = True) for p in p_tags]

for a in a_tags:
    player_name = a.contents[0]
    player_code = a.get('href').split('/')[-1].split('.')[0]
    if player_name.strip() == inputted_player_name:
        player_url = players_url.format(letter=letter_to_request, player_code=player_code)
        res = requests.get(player_url)
        soup = BS(res.content, 'html.parser')
        table = soup.find('table')
        table_id = table.get('id')
        table = str(table)

        df = pd.read_html(table)[0]
        if df.columns.nlevels > 1:
            df.columns = df.columns.droplevel(level=0)
        
        df.fillna(0, inplace=True)

        df['Year'] = df['Year'].apply(lambda x: x.split('*')[0])

        columns_to_drop = []

        print(table_id)

        if table_id == 'passing':

            df.rename({
                'Yds': 'PassingYds',
                'Yds.1': 'YdsLostToSacks'
            }, axis=1, inplace=True)

            columns_to_drop = [
                'TD%', 'Int%', 'Y/A', 'AY/A', 'Y/C', 'Y/G', 'NY/A', 'ANY/A', 'Sk%', 'AV'
            ]

        if table_id == 'receiving_and_rushing':
            df['ReceivingYds'] = df['Yds'].iloc[:,0]
            df['RushingYds'] = df['Yds'].iloc[:, 1]
            df['Receiving1D'] = df['1D'].iloc[:, 0]
            df['Rushing1D'] = df['1D'].iloc[:, 1]
            df['RecevingTD'] = df['TD'].iloc[:, 0]
            df['RushingTD'] = df['TD'].iloc[:, 1]

            columns_to_drop = [
            'Yds', 'Y/G', 'Y/A', 'R/G', 'Y/Tch', 'YScm', 'Ctch%', 'Y/Tgt', 'Y/R', 'A/G', '1D', 'RRTD', 'TD'
            ]

        if table_id == 'rushing_and_receiving':
            df['ReceivingYds'] = df['Yds'].iloc[:,1]
            df['RushingYds'] = df['Yds'].iloc[:, 0]
            df['Receiving1D'] = df['1D'].iloc[:, 1]
            df['Rushing1D'] = df['1D'].iloc[:, 0]
            df['RecevingTD'] = df['TD'].iloc[:, 1]
            df['RushingTD'] = df['TD'].iloc[:, 0]

            columns_to_drop = [
            'Yds', 'Y/G', 'Y/A', 'R/G', 'Y/Tch', 'YScm', 'Ctch%', 'Y/Tgt', 'Y/R', 'A/G', '1D', 'RRTD', 'TD'
            ]

        df.drop(columns_to_drop, axis=1, inplace=True)    

        try:
            if argv[1] == '--save':
                filename = (player_first_name+player_last_name).upper() + '.csv'
                df.to_csv('data/{}'.format(filename)) # saves to a folder called data.
        except IndexError:
            print(df.tail())

        break