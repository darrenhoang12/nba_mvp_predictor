import requests
import platform
import os
import time
from pathlib import Path
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
from selenium import webdriver
from selenium.webdriver.common.by import By

# Basketball Reference crawl delay is 3 seconds
crawl_delay = 3
years = range(1991, 2024)
mvp_save_dir = Path('data') / 'mvp_votings'
pstats_save_dir = Path('data') / 'player_stats'
team_record_save_dir = Path('data') / 'team_records'


def download_mvp_votings():
    """
    Goes through range of years 1991 to 2023 on the MVP Votings page on Basketball Reference
    and downloads the HTML data locally

    Args: None

    Action: Downloads data locally
    """
    raw_mvp_save_dir = mvp_save_dir / 'raw'
    if not os.path.exists(raw_mvp_save_dir):
        os.makedirs(raw_mvp_save_dir)

    # Taking in years 1991 to 2023, as 2023 year has just finished
    # base url: https://www.basketball-reference.com/awards/awards_{year}.html
    # where {year} is the year the NBA MVP was awarded
    for year in years:
        print(f'Downloading MVP votings from {year}')
        url = f'https://www.basketball-reference.com/awards/awards_{year}.html'
        r = requests.get(url=url)
        web_content = r.content.decode('utf-8')
        save_file = raw_mvp_save_dir / f'awards_{year}.html'
        with open(save_file, 'w', encoding='utf-8') as f:
            f.write(web_content)
        time.sleep(crawl_delay)

def parse_mvp_votings():
    """
    Parses the MVP tables from the locally downloaded HTML data.

    Args: None

    Actions: Combines MVP table data from 1991 to 2023 and stores it
    """
    dfs = []
    for year in years:
        print(f'Parsing MVP votings from {year}')
        # Creating BeautifulSoup for data
        content = open(mvp_save_dir / 'raw' / f'awards_{year}.html', 'r', encoding='utf-8')
        soup = BeautifulSoup(content, 'html.parser')
        table = soup.find('table', attrs={'id': 'mvp'})

        # Removing overheader
        overheader = table.find('tr', attrs={'class':'over_header'})
        overheader.extract()
        
        df = pd.read_html(table.prettify())[0]
        df['year']= year
        dfs.append(df)
        content.close()
    
    mvps = pd.concat(dfs)
    processed_mvp_save_dir = mvp_save_dir / 'processed'
    if not os.path.exists(processed_mvp_save_dir):
        os.makedirs(processed_mvp_save_dir)
    mvps.to_csv(processed_mvp_save_dir / 'mvps.csv', index=False)
    
def download_player_stats():
    """
    Downloads individual player stats

    Args: None

    Actions: Downloads HTML data of individual player stats from 1991 to 2023 locally
    """
    # Starting selenium driver with Safari (only on OSX)
    # Utilize Chrome for all others...
    if platform.system() == 'Windows':
        driver = webdriver.Chrome()
    else:
        driver = webdriver.Safari()
    raw_pstats_save_dir = pstats_save_dir / 'raw'
    if not os.path.exists(raw_pstats_save_dir):
        os.makedirs(raw_pstats_save_dir)

    for year in years:
        print(f'Downloading player stats from {year}')
        url = f'https://www.basketball-reference.com/leagues/NBA_{year}_per_game.html'
        driver.get(url)
        driver.execute_script("window.scrollTo(1, document.body.scrollHeight)")
        time.sleep(3)

        table = driver.find_element(By.TAG_NAME, 'table')
        html_table_content = table.get_attribute('outerHTML')
        save_file = raw_pstats_save_dir / f'player_stats_{year}.html'
        with open(save_file, 'w', encoding='utf-8') as f:
            f.write(html_table_content)

def parse_player_stats():
    """
    Parses player stats from locally downloaded html files

    Args: None

    Actions: Combines year to year data from player stats into a dataframe and saves it locally

    ## NOTE: The dataframe will not match the number of players in the league due to trades.
    ## Players that are traded will have multiple rows for their stats representing each team they played on.
    """
    dfs = []
    for year in years:
        print(f'Parsing player stats from {year}')
        content = open(pstats_save_dir / 'raw' / f'player_stats_{year}.html', 'r', encoding='utf-8')
        table = BeautifulSoup(content, 'html.parser')

        # Removes the extra headers
        extra_headers = table.find_all('tr', attrs={'class': 'thead'})
        for extra in extra_headers:
            extra.extract()
        df = pd.read_html(table.prettify())[0]
        df['year'] = year
        dfs.append(df)
        content.close()
    
    player_stats = pd.concat(dfs)
    processed_pstats_save_dir = pstats_save_dir / 'processed'
    if not os.path.exists(processed_pstats_save_dir):
        os.makedirs(processed_pstats_save_dir)
    player_stats.to_csv(processed_pstats_save_dir/ 'player_stats.csv', index=False)


def download_team_records():
    """
    Downloads team records locally

    Args: None

    Actions: Downloads year to year team record HTML data locally
    """
    raw_team_record_save_dir = team_record_save_dir / 'raw'
    if not os.path.exists(raw_team_record_save_dir):
        os.makedirs(raw_team_record_save_dir)
    for year in years:
        print(f'Downloading team records from {year}')
        url = f'https://www.basketball-reference.com/leagues/NBA_{year}_standings.html'
        r = requests.get(url)
        web_content = r.content.decode('utf-8')
        save_file = raw_team_record_save_dir / f'team_records_{year}.html'
        with open(save_file, 'w', encoding='utf-8') as f:
            f.write(web_content)
        time.sleep(crawl_delay)

def parse_team_records():
    """
    Parses team records from locally downloaded html files

    Args: None

    Actions: Combines year to year team record data into a single dataframe and saves it locally
    """
    dfs = []
    for year in years:
        print(f'Parsing team records from {year}')
        content = open(team_record_save_dir / 'raw' / f'team_records_{year}.html', 'r', encoding='utf-8')
        soup = BeautifulSoup(content, 'html.parser')
        for extra in soup.find_all('tr', attrs={'class': 'thead'}):
            extra.extract()

        eastern_conf_standings_table = soup.find('table', attrs={'id': 'divs_standings_E'})
        eastern_conf_df = pd.read_html(eastern_conf_standings_table.prettify())[0]
        eastern_conf_df['year'] = year
        eastern_conf_df.rename(columns={'Eastern Conference': 'team_name'}, inplace=True)
        
        western_conf_standings_table = soup.find('table', attrs={'id': 'divs_standings_W'})
        western_conf_df = pd.read_html(western_conf_standings_table.prettify())[0]
        western_conf_df['year'] = year
        western_conf_df.rename(columns={'Western Conference': 'team_name'}, inplace=True)

        dfs.append(eastern_conf_df)
        dfs.append(western_conf_df)
    
    team_records = pd.concat(dfs)
    processed_team_record_save_dir = team_record_save_dir / 'processed'
    if not os.path.exists(processed_team_record_save_dir):
        os.makedirs(processed_team_record_save_dir)
    team_records.to_csv(processed_team_record_save_dir / 'team_records.csv', index=False)
