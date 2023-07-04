from scraper import *
from model import *

def main():
    """
    Scrape from Basketball Reference Database:
        MVP Voting Data
        Individual Player Statistics
        Team Records
    """
    MVP_data = input('Do you want to download MVP voting data? (y/n): ')
    while MVP_data.lower() != 'y' and MVP_data.lower() != 'n':
        MVP_data = input('Invalid input. Please enter (y/n): ')
    if MVP_data.lower() == 'y':
        download_mvp_votings()
        parse_mvp_votings()
    
    pstats_data = input('Do you want to download player stats data? (y/n): ')
    while pstats_data.lower() != 'y' and pstats_data.lower() != 'n':
        pstats_data = input('Invalid input. Please enter (y/n): ')
    if pstats_data.lower() == 'y':
        download_player_stats()
        parse_player_stats()

    team_record_data = input('Do you want to download team record data? (y/n): ')
    while team_record_data.lower() != 'y' and team_record_data.lower() != 'n':
        team_record_data = input('Invalid input. Please enter (y/n): ')
    if team_record_data.lower() != 'y':
        download_team_records()
        parse_team_records()
    

if __name__ == '__main__':
    main()