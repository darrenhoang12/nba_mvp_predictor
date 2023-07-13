import os
import pandas as pd
from pathlib import Path

mvp_votings_save_path = Path('data') / 'mvp_votings' / 'processed' / 'mvps.csv'
player_stats_save_path = Path('data') / 'player_stats' / 'processed' / 'player_stats.csv'
team_record_save_path = Path('data') / 'team_records' / 'processed' / 'team_records.csv'
adv_stats_save_path = Path('data') / 'advanced_stats' / 'processed' / 'adv_stats.csv'
merged_save_path = Path('data') / 'merged'

def merge_data():
    """
    Does minimal cleaning of player stats and team records data and merges them
    """
    
    # Adds column to team_records dataframe that indicates if the team made the playoffs
    # Removes symbols from the team_name such as * or the placement standings of the team
    team_records = pd.read_csv(team_record_save_path)
    team_records['playoffs'] = False
    for idx, team_name in enumerate(team_records['Tm']):
        if '*' in team_name:
            team_records.at[idx, 'playoffs'] = True
        parenthesis_idx = team_name.find('(')
        if parenthesis_idx != -1:
            team_name = team_name[:parenthesis_idx]
        team_name = team_name.replace('*', '').rstrip()
        team_records.at[idx, 'Tm'] = team_name

    # Replaces CHO with CHH (both team abbreviations represent the Charlottle Hornets, just in different years)
    # Removes players with TOT (Total) meaning they have been traded during that season.
    #   *Historically, all players who have been traded in the middle of the season have never won MVP
    player_stats = pd.read_csv(player_stats_save_path)
    player_stats['Tm'].replace('CHO', 'CHH', inplace=True)
    player_stats = player_stats[player_stats.Tm != 'TOT']
    
    # Creates mapping for the full name of the team and the abbreviations. We will be using the abbreviations
    team_names = sorted(team_records['Tm'].unique())
    team_abbreviations = sorted(player_stats['Tm'].unique())
    
    # Some of the sorted abbreviations do not match up with the full team names, so we fix it here
    if 'NOK' in team_abbreviations and 'NOP' in team_abbreviations:
        nok_index, nop_index = team_abbreviations.index('NOK'), team_abbreviations.index('NOP')
        team_abbreviations[nop_index], team_abbreviations[nok_index] = team_abbreviations[nok_index], team_abbreviations[nop_index]
    if 'WSB' in team_abbreviations and 'WAS' in team_abbreviations:
        wsb_index, was_index = team_abbreviations.index('WSB'), team_abbreviations.index('WAS')
        team_abbreviations[wsb_index], team_abbreviations[was_index] = team_abbreviations[was_index], team_abbreviations[wsb_index]
    team_name_map = dict(zip(team_names, team_abbreviations))

    # Replaces the team_records team names with the abbreviations
    cleaned_team_record_names = []
    for team_name in team_records['Tm']:
        cleaned_team_record_names.append(team_name_map[team_name])
    team_records['Tm'] = cleaned_team_record_names

    adv_stats = pd.read_csv(adv_stats_save_path)
    adv_stats = adv_stats.drop(columns=['Rk', 'Pos', 'Age', 'Tm', 'G', 'MP'])
    
    # Merge together the team_records and player_stats
    pstats_and_team_records = pd.merge(player_stats,
                                       team_records[['Tm', 'year', 'W/L%', 'playoffs']],
                                       on=['Tm', 'year'],
                                       how='left')
    
    adv_stats_merged = pd.merge(pstats_and_team_records,
                                adv_stats,
                                on=['Player', 'year'],
                                how='left')

    # Merge the MVP votings data into team_records and player_stats
    mvp_votings = pd.read_csv(mvp_votings_save_path)
    merged_df = pd.merge(adv_stats_merged,
                         mvp_votings[['Player', 'year', 'Share', 'Rank', 'First']],
                         on=['Player', 'year'],
                         how='left')
    
    
    if not os.path.exists(merged_save_path):
        os.makedirs(merged_save_path)
    merged_df.to_csv(merged_save_path / 'uncleaned_merged.csv', index=False)

def clean_merged_df():
    """
    Establishing the minimum criteria for an MVP (via StatMuse)
        Games Played (GP)    | 49
        PTS and FGA          | 13.8 & 10.9
        Rebounds (TRB)       | 3.3
        Assists (AST)        | 1.3
        FG%                  | 0.378
        Min Played (MP)      | 30.4
        PER                  | 18.1
    
    Other criteria:
        There has only been one MVP that did not make the playoffs
        (Handled earlier) Players who have been traded while the season was ongoing has never won MVP

    """
    merged_df = pd.read_csv(merged_save_path / 'uncleaned_merged.csv')
    merged_df = merged_df[merged_df.G >= 49]
    merged_df = merged_df[merged_df.PTS >= 13.8]
    merged_df = merged_df[merged_df.FGA >= 10.9]
    merged_df = merged_df[merged_df.TRB >= 3.3]
    merged_df = merged_df[merged_df.AST >= 1.3]
    merged_df = merged_df[merged_df['FG%'] >= 0.378]
    merged_df = merged_df[merged_df.MP >= 30.4]
    merged_df = merged_df[merged_df.PER >= 18.1]

    # Player name cleanup
    player_names = []
    for pname in merged_df['Player']:
        pname = pname.replace('*', '')
        pname = pname.rstrip()
        player_names.append(pname)

    # Replacing "null" values to keep things consistent
    merged_df['Player'] = player_names

    # Dropping low-information columns
    merged_df.drop(columns=['Rk', 'playoffs', 'Tm', 'Pos'], inplace=True)

    merged_df.rename(columns={'Share': 'mvp_share', 'Rank': 'mvp_rank', 'First': 'first_place_votes'}, inplace=True)
    merged_df.columns = merged_df.columns.str.lower()
    
    # Filling columns that have NaN values with '0'
    #   - 3p%: Some players (Big men) do not shoot 3 pointers
    #   - mvp_share: Number of received MVP votes / Number of total MVP Votes
    #   - mvp_rank: final MVP rankings
    #   - first_place_votes: number of first place votes
    merged_df.fillna(0, inplace=True)
    print(merged_df.info())
    merged_df.to_csv(merged_save_path / 'player_data.csv', index=False)
