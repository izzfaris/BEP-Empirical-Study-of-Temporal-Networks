import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from selenium import webdriver



def scrape_football(year, Round):
    '''Scrape the football data from the website and return a dataframe with the data.
        Input: year - the year of the competition, Round - the round of the competition
        Output: a dataframe with the football data'''

    # Define headers for the HTTP request
    headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    }

    # Construct the URL for the request
    url = 'https://www.transfermarkt.com/uefa-champions-league/spieltag/pokalwettbewerb/CL/plus/0?saison_id='+ year + '&gruppe=' + Round

    # Send the HTTP request and get the response
    response = requests.get(url, headers=headers)

    # Parse the HTML content of the response
    soup = BeautifulSoup(response.content, 'html.parser')

    # Define the classes of the HTML elements to extract
    classes = {'Date': 'zentriert no-border', #td
               'Home Team' : 'rechts hauptlink no-border-rechts hide-for-small spieltagsansicht-vereinsname', #td
               'Away Team' : 'hauptlink no-border-links no-border-rechts hide-for-small spieltagsansicht-vereinsname', #td
               'Result': 'matchresult finished' #span
               }

    # Extract the dates, home teams, away teams, and results
    date = [element.text.strip() for element in soup.find_all('td', class_=classes["Date"])]
    home_team = [element.text.strip() for element in soup.find_all('td', class_=classes['Home Team'])]
    away_team = [element.text.strip() for element in soup.find_all('td', class_=classes['Away Team'])]
    result = [element.text.strip() for element in soup.find_all('span', class_=classes['Result'])]

    # Extract the scores and scorers
    allHscoresheet, allAscoresheet, allHscorer, allAscorer = scores(soup)

    # Define the mapping from round codes to stage names
    stage_mapping = {
        'AFH': 'Last 16 Leg 1',
        'AFR': 'Last 16 Leg 2',
        '1RH': 'First Round Leg 1',
        '1RR': 'First Round Leg 2',
        '1RE': 'First Round Replay',
        '2RH': 'Second Round Leg 1',
        '2RR': 'Second Round Leg 2',
        'VFH': 'Quarter Finals Leg 1',
        'VFR': 'Quarter Finals Leg 2',
        'VF': 'Quarter Finals',
        'HFH': 'Semi Finals Leg 1',
        'HFR': 'Semi Finals Leg 2',
        'HF': 'Semi Finals',
        'FF': 'Final'
    }
    
    # Get the stage name for the current round
    stage = stage_mapping.get(Round, 'Group ' + Round)
    
    # Create a dataframe with the extracted data
    df = pd.DataFrame({
        'Date': date, 
        'Home Team': home_team, 
        'Away Team': away_team, 
        'Result': result, 
        'Stage': stage, 
        'Scoresheet_Home' : allHscoresheet, 
        'Scorer_Home' : allHscorer, 
        'Scoresheet_Away' : allAscoresheet, 
        'Scorer_Away' : allAscorer
    })
    
    # Return the dataframe
    return df


def scores(soup): #Used in scrape_football function
    '''Extract the scores and scorers from the website and return a list of scores and scorers for each team.
        This is used in the scrape_football function.
        Input: soup - the BeautifulSoup object
        Output: Lists of scores and scorers for each team.
    '''

    # Find all tables with a specific style attribute
    specific_table = soup.find_all('table', attrs={'style': "border-top: 0 !important;"})

    # Initialize lists to store scores and scorers for home and away teams
    allHscoresheet = []
    allAscoresheet = []
    allHscorer = []
    allAscorer = []

    # For each table
    for table in specific_table:
        # Initialize lists to store scores and scorers for home and away teams in the current table
        Hscoresheet = []
        Ascoresheet = []
        Hscorer = []
        Ascorer = []

        # Find all rows with a specific class attribute
        rows = table.find_all('tr', class_ = "no-border spieltagsansicht-aktionen")

        # For each row
        for row in rows:
            # Find all cells with specific class attributes
            home = row.find_all('td', class_ = 'zentriert no-border-links')
            away = row.find_all('td', class_ = 'zentriert no-border-rechts')
            homeScorer = row.find_all('td', class_ = 'rechts no-border-rechts spieltagsansicht')
            awayScorer = row.find_all('td', class_ = 'links no-border-links spieltagsansicht')
            
            # For each home cell
            for Hscore in home:
                # Find the previous sibling cell with a specific class attribute
                goal = Hscore.find_previous_sibling('td').find('span', {'class': ['icons_sprite icon-tor-formation', 'icons_sprite icon-elfmeter-formation', 'icons_sprite icon-eigentor-formation']})

                # If the cell exists
                if goal:
                    # Extract the text from the cell and strip whitespace
                    score = Hscore.text.strip()

                    # If the text exists
                    if score:
                        # Add the text to the list of home scores
                        Hscoresheet.append(score)
            
            # Similar process is repeated for away cells, home scorers and away scorers

        # Add the lists of scores and scorers for the current table to the overall lists
        allHscoresheet.append(Hscoresheet)
        allAscoresheet.append(Ascoresheet)
        allHscorer.append(Hscorer)
        allAscorer.append(Ascorer)

    # Return the lists of scores and scorers for each team
    return allHscoresheet, allAscoresheet, allHscorer, allAscorer


def scrape_jet(url, celebrity):
    '''Scrape the data from the website and return a dataframe with the data.
        Input: url - the url of the website, celebrity - the celebrity name
        Output: a dataframe with the data'''
    
    url = 'https://celebrityprivatejettracker.com/' + url
    # specify the path to your webdriver
    driver = webdriver.Chrome()

    # get the page
    driver.get(url)

    # let JavaScript load
    driver.implicitly_wait(10)

    # get the source code
    html = driver.page_source

    # parse the source code
    soup = BeautifulSoup(html, 'html.parser')
    classes = ['trlight', 'trdark']
    # find the table
    specific_table = soup.find('div', id='table3')
    mini_t = specific_table.find('table', class_='tabledata flighttable w70p')
    rows = mini_t.find_all('tr', class_ = classes)

    all_data = []
    for row in rows:
        # Find all td tags within the row
        data = []
        for td in row.find_all('td'):
            for span in td.find_all('span'):
                span.decompose()  # remove the span tag and its content
            data.append(td.text.strip())  # append the text of td after removing span
        # Clean elements 4 and 5
        if len(data) >= 6:  # Check if there are at least 6 elements
            data[4] = data[4].replace('\xa0', ' ')
            data[5] = data[5].replace('\xa0', ' ')
        all_data.append(data)

    all_data = all_data[:-1]

    # close the driver
    driver.quit()

    df = pd.DataFrame(all_data, columns=['Date', 'Departure', 'Arrival', 'Distance', 'Flight Time', 'Fuel', 'Carbon Emissions'])
    df['Celebrity'] = celebrity

    return df


