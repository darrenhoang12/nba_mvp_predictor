from scraper import *
from model import *

def main():
    # Request input form user if data is not downloaded:
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

    

    

if __name__ == '__main__':
    main()