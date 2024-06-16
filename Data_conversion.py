import Scraper as sf
import pandas as pd
from tqdm import tqdm
import importlib
importlib.reload(sf)


def football_to_csv():
    '''Scrape the data from the website and save it to a csv file.
      The function scrapes the data for the Champions League from 1992 to 2022
      '''
    list_of_rounds = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', '1', '2', '3', '4', '1RH', '1RR', '1RE', '2RH', '2RR','AFH', 'AFR', 'VFH', 'VF', 'VFR', 'HF', 'HFH', 'HFR', 'FF']
    full_years = ['1992', '1993', '1994', '1995', '1996', '1997', '1998', '1999', '2000', '2001', '2002', '2003', '2004', '2005', '2006', 
                  '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022','2023']
    Champions_League = pd.DataFrame()

    # Scrape the data for the Champions League from 1992 to 2023
    for year in tqdm(full_years):
        # Scrape the data for each round in the list
        for round in tqdm(list_of_rounds):
            df = sf.scrape_football(year, round)
            if df is not None:
                Champions_League = pd.concat([Champions_League, df], ignore_index=True)

    Champions_League.to_csv('Datasets/Champions_League.csv', index=False)

def flights_to_csv():
    '''Scrape the data from the website and save it to a csv file.
      The function scrapes the data for the celebrities in the lists
      '''
    url_type = ['taylor-swift-n898ts/', 'taylor-swift-n621mm/', 'elon-musk-n628ts/','donald-trump-n757af/', 'michael-bloomberg-n5mv/', 'michael-bloomberg-n47eg/', 'nike-corporation-n6453/', 'drake-n767cj/', 'kylie-jenner-n810kj/', 'kim-kardashian-n1980k/']
    celebrity_list = ['Taylor Swift Plane 1', 'Taylor Swift Plane 2','Elon Musk', 'Donald Trump', 'Michael Bloomberg Plane 1', 'Michael Bloomberg Plane 2', 'Nike Corporation', 'Drake', 'Kylie Jenner', 'Kim Kardashian']
    Jets = pd.DataFrame()

    # Scrape the data for the celebrities in the list
    for index, url_type in tqdm(enumerate(url_type)):
        df = sf.scrape_jet(url_type, celebrity_list[index])
        Jets = pd.concat([Jets, df], ignore_index=True)

    Jets.to_csv('Datasets/Jets.csv', index=False)
    

# Uncomment the function you want to run

# football_to_csv()
# flights_to_csv()