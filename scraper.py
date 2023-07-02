import requests
import time
from pathlib import Path
from bs4 import BeautifulSoup
import pandas as pd

# Basketball Reference crawl delay is 3 seconds
crawl_delay = 3

def download_mvp_votings():
    """

    """
    # Taking in years 1991 to 2023, as 2023 year has just finished
    save_dir = Path('data') / 'mvp_votings'
    years = range(1991, 2024)
    # base url: https://www.basketball-reference.com/awards/awards_{year}.html
    # where {year} is the year the NBA MVP was awarded
    for year in years:
        print(f'Downloading MVP votings for {year}')
        url = f'https://www.basketball-reference.com/awards/awards_{year}.html'
        r = requests.get(url=url)
        web_content = r.content.decode('utf-8')
        save_file = save_dir / f'awards_{year}.html'
        with open(save_file, 'w') as f:
            f.write(web_content)
        time.sleep(crawl_delay)

def parse_mvp_votings():
    """

    """
    # Creating BeautifulSoup for data
    content = open('data/mvp_votings/awards_2023.html')
    soup = BeautifulSoup(content, 'html.parser')
    table = soup.find('table', attrs={'id': 'mvp'})

    data = []

    # Removing overheader and taking column names
    table_header = table.thead.extract()
    over_header = table_header.find('tr', attrs={'class': 'over_header'})
    over_header.extract()
    headers = [col.text.strip() for col in table_header.find_all('th')]

    # Looping through rows in the table
    table_body = table.find('tbody')
    for row in table_body.find_all('tr'):
        # Rank isn't nested within <td></td>, instead <th></th>
        row_data = []
        rank = row.find('th').text.strip()
        row_data.append(rank)
        # Find all other data values
        cols = row.find_all('td')
        for c in cols:
            row_data.append(c.text.strip())
        data.append(row_data)
    
    df = pd.DataFrame(data, columns=headers)
    print(df.head())

parse_mvp_votings()