import requests
import time
from pathlib import Path
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO

# Basketball Reference crawl delay is 3 seconds
crawl_delay = 3
years = range(1991, 2024)
mvp_save_dir = Path('data') / 'mvp_votings'
pstats_save_dir = Path('data') / 'player_stats'


def download_mvp_votings():
    """
    Goes through range of years 1991 to 2023 on the MVP Votings page on Basketball Reference
    and downloads the HTML data locally

    Args: None

    Action: Downloads data into "data/mvp_votings/*.html"
    """
    # Taking in years 1991 to 2023, as 2023 year has just finished
    # base url: https://www.basketball-reference.com/awards/awards_{year}.html
    # where {year} is the year the NBA MVP was awarded
    for year in years:
        print(f'Downloading MVP votings for {year}')
        url = f'https://www.basketball-reference.com/awards/awards_{year}.html'
        r = requests.get(url=url)
        web_content = r.content.decode('utf-8')
        save_file = mvp_save_dir / f'awards_{year}.html'
        with open(save_file, 'w') as f:
            f.write(web_content)
        time.sleep(crawl_delay)

def parse_mvp_votings():
    """
    Parses the MVP tables from the locally downloaded HTML data.

    Args: None

    Actions: Combines MVP table data from 1991 to 2023 and stores it in "data/mvp_votings/mvps.csv"
    """
    dfs = []
    for year in years:
        # Creating BeautifulSoup for data
        content = open(f'data/mvp_votings/awards_{year}.html')
        soup = BeautifulSoup(content, 'html.parser')
        table = soup.find('table', attrs={'id': 'mvp'})

        # Removing overheader
        overheader = table.find('tr', attrs={'class':'over_header'})
        overheader.extract()
        
        df = pd.read_html(table.prettify())[0]
        dfs.append(df)
    
    mvps = pd.concat(dfs)
    mvps.to_csv(mvp_save_dir / 'mvps.csv')

def download_player_stats():
    url = 'https://www.basketball-reference.com/leagues/NBA_2023_per_game.html'
    r = requests.get(url=url)
    web_content = r.content.decode('utf-8')
    save_file = pstats_save_dir / 'test.html'
    with open(save_file, 'w') as f:
        f.write(web_content)

download_player_stats()