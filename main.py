from scraper import *
from model import *

def main():
    # Request input form user if data is not downloaded:
    downloaded = ''
    while downloaded.lower() != 'y' and downloaded.lower() != 'n':
        downloaded = input('Would you like to download the data? (y/n): ')
    
    if downloaded.lower() == 'y':
        download_mvp_votings()
    
    # Scrape MVP Voting Data
    parse_mvp_votings()

if __name__ == '__main__':
    main()