import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from selenium import webdriver



def scrape_football(year, Round):

    '''Scrape the football data from the website and return a dataframe with the data.'''

    headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    }

    url = 'https://www.transfermarkt.com/uefa-champions-league/spieltag/pokalwettbewerb/CL/plus/0?saison_id='+ year + '&gruppe=' + Round

    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.content, 'html.parser')

    classes = {'Date': 'zentriert no-border', #td
               'Home Team' : 'rechts hauptlink no-border-rechts hide-for-small spieltagsansicht-vereinsname', #td
               'Away Team' : 'hauptlink no-border-links no-border-rechts hide-for-small spieltagsansicht-vereinsname', #td
               'Result': 'matchresult finished' #span
               }

    date = soup.find_all('td', class_=classes['Date'])
    date = [element.text.strip() for element in soup.find_all('td', class_=classes["Date"])]
    date_pattern = r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+\d{4}\b'
    date = [re.search(date_pattern, d).group(0) for d in date if re.search(date_pattern, d)]

    home_team = soup.find_all('td', class_=classes['Home Team'])
    home_team = [element.text.strip() for element in home_team]

    away_team = soup.find_all('td', class_=classes['Away Team'])
    away_team = [element.text.strip() for element in away_team]

    result = soup.find_all('span', class_=classes['Result'])
    result = [element.text.strip() for element in result]

    allHscoresheet, allAscoresheet, allHscorer, allAscorer = scores(soup)

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
    
    stage = stage_mapping.get(Round, 'Group ' + Round)
    
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
    
    return df


def scores(soup):
    
    '''Extract the scores and scorers from the website and return a list of scores and scorers for each team.
        This is used in the scrape_football function.
    '''

    specific_table = soup.find_all('table', attrs={'style': "border-top: 0 !important;"})

    allHscoresheet = []
    allAscoresheet = []
    allHscorer = []
    allAscorer = []

    for table in specific_table:

        Hscoresheet = []
        Ascoresheet = []
        Hscorer = []
        Ascorer = []
        rows = table.find_all('tr', class_ = "no-border spieltagsansicht-aktionen")
        for row in rows:
                # Extract cells from the row
                home = row.find_all('td', class_ = 'zentriert no-border-links')
                away = row.find_all('td', class_ = 'zentriert no-border-rechts')
                homeScorer = row.find_all('td', class_ = 'rechts no-border-rechts spieltagsansicht')
                awayScorer = row.find_all('td', class_ = 'links no-border-links spieltagsansicht')
                
                for Hscore in home:
                    goal = Hscore.find_previous_sibling('td').find('span', {'class': ['icons_sprite icon-tor-formation', 'icons_sprite icon-elfmeter-formation', 'icons_sprite icon-eigentor-formation']})
                    if goal:
                        score = Hscore.text.strip()
                        if score:
                            Hscoresheet.append(score)
                        
                for Ascore in away:
                    goal = Ascore.find_next_sibling('td').find('span', {'class': ['icons_sprite icon-tor-formation', 'icons_sprite icon-elfmeter-formation', 'icons_sprite icon-eigentor-formation']})
                    if goal:
                        score = Ascore.text.strip()
                        if score:
                            Ascoresheet.append(score)

                for h in homeScorer:
                    goal = h.find('span', {'class': ['icons_sprite icon-tor-formation', 'icons_sprite icon-elfmeter-formation', 'icons_sprite icon-eigentor-formation']})
                    if goal:
                        Hscorer.append(h.find('a').text.strip())
                
                for a in awayScorer:
                    goal = a.find('span', {'class': ['icons_sprite icon-tor-formation', 'icons_sprite icon-elfmeter-formation', 'icons_sprite icon-eigentor-formation']})
                    if goal:
                        Ascorer.append(a.find('a').text.strip())

        allHscoresheet.append(Hscoresheet)
        allAscoresheet.append(Ascoresheet)
        allHscorer.append(Hscorer)
        allAscorer.append(Ascorer)

    return allHscoresheet, allAscoresheet, allHscorer, allAscorer


def scrape_jet(url, celebrity):
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


