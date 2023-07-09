from scraper import *
from model import *

def download_data():
    """
    Scrape from Basketball Reference Database:
        MVP Voting Data
        Individual Player Statistics
        Team Records
    """

    download_mvp_votings()
    parse_mvp_votings()

    download_player_stats()
    parse_player_stats()

    download_team_records()
    parse_team_records()
    

if __name__ == '__main__':
    download_data()