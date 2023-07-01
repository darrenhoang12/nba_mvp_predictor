import requests
import time
from pathlib import Path

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
