# Predicting the NBA MVP
In this project, we will scrape NBA player data from [Basketball Reference](www.basketball-reference.com) and use it to build a model that will be able to accurately predict the MVP of each season. Basketball Reference has well-structured and formatted historical data on the NBA up to the present.
#
## Requirements
This project is done with Python 3.9+ with the following additionally downloaded packages:
* beautifulsoup4
* selenium
* pandas
* scikit-learn
* matplotlib

These packages can be downloaded in ~/env/requirements.txt for pip or ~/env/nba.yml to create a conda environment.
#
## Scraping Data
We will focus on three specific types of pages when scraping:
* The information on the MVP race of each season
* The statistics of each individual player in the league that season
* The team records of each season

**The crawl delay on Basketball Reference is 3 seconds.**
<br />

Downloading simple HTML websites were done using the `requests` package. However, we ran into a problem while scraping the player stats webpages using requests, as it did not collect the HTML content for all the players. Thus, we used the `selenium` package to download the content from these pages. After collecting this content, we used `beautifulsoup4` package to scrape the targeted tables and store them into csv files.
#
## Data Treatment
After obtaining our data for the mvp race, player statistics, and team records, we are ready to clean it in preparation for machine learning.

We start by joining our data all into an overall dataframe. There were a couple caveats when cleaning:
* The team names in team records were full names, such as 'Los Angeles Lakers', while the team names associated with each player in player stats and the mvp race data were abbreviated, such as 'LAL'.
* The Charlotte Hornets had two abbreivations, CHO and CHH, we will default to CHH.
* Add a column that represents if a player made the playoffs or not. Remove players on teams that did not make the playoffs.
* Some players play on multiple teams in a single season. Historically, players who have been traded in the middle of the season have never won an MVP award, so we will remove this from the data.
* We will only take a couple of the data columns from the MVP race data.
    * MVP Share - The amount of votes received / The total amount of votes
    * First Place Votes - The number of first place MVP votes received
    * MVP Rank - The MVP rank of the player
    * Win Share / 48 - How much a player contributed to a win per 48 minutes (one game).

### Establishing Minimum Requirements for an MVP
There is a minimum requirement for each stat that a player has to reach in order to win the MVP race. Of course, players have to go above and beyond to win the MVP, but theses stats represent the lowest averages and statistics by an MVP in the NBA's history. This data was found through StatMuse.
* Games Played: **49 GP** by Karl Malone
* Points Per Game and Field Goals Attempted: **13.8 PPG and 10.9 FGA** by Wes Unseld
* Total Rebounds: **3.3 REB** by Steve Nash
* Assists: **1.3 AST** by Moses Malone
* Field Goal Percentage: **37.8 FG%** by Bob Cousy
* Minutes played: **30.4 MP** by Giannis Antetokounmpo
* One one player, Kareem Abdul Jabbar, in NBA history has won the MVP while not making the playoffs
#
## Modeling
TO-DO





