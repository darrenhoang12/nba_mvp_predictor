import os
import pandas as pd
from pathlib import Path

mvp_votings_save_path = Path('data') / 'mvp_votings' / 'processed'
player_stats_path = Path('data') / 'player_stats' / 'processed'
team_record_save_path = Path('data') / 'team_records' / 'processed'
merged_save_path = Path('data') / 'merged'

def merge_pstats_team_records():
    """
    Does minimal cleaning of player stats and team records data and merges them
    """
    
    # Adds column to team_records dataframe that indicates if the team made the playoffs
    # Removes symbols from the team_name such as * or the placement standings of the team
    team_records = pd.read_csv(team_record_save_path / 'team_records.csv')
    team_records['playoffs'] = False
    for idx, team_name in enumerate(team_records['team_name']):
        if '*' in team_name:
            team_records.at[idx, 'playoffs'] = True
        parenthesis_idx = team_name.find('(')
        if parenthesis_idx != -1:
            team_name = team_name[:parenthesis_idx]
        team_name = team_name.replace('*', '').rstrip()
        team_records.at[idx, 'team_name'] = team_name

    # Replaces CHO with CHH (both team abbreviations represent the Charlottle Hornets, just in different years)
    # Removes players with TOT (Total) meaning they have been traded during that season.
    #   *Historically, all players who have been traded in the middle of the season have never won MVP
    player_stats = pd.read_csv(player_stats_path / 'player_stats.csv')
    player_stats['Tm'].replace('CHO', 'CHH', inplace=True)
    player_stats = player_stats[player_stats.Tm != 'TOT']
    
    # Creates mapping for the full name of the team and the abbreviations. We will be using the abbreviations
    team_names = sorted(team_records['team_name'].unique())
    team_abbreviations = sorted(player_stats['Tm'].unique())
    
    # Some of the sorted abbreviations do not match up with the full team names, so we fix it here
    nok_index, nop_index = team_abbreviations.index('NOK'), team_abbreviations.index('NOP')
    team_abbreviations[nop_index], team_abbreviations[nok_index] = team_abbreviations[nok_index], team_abbreviations[nop_index]
    wsb_index, was_index = team_abbreviations.index('WSB'), team_abbreviations.index('WAS')
    team_abbreviations[wsb_index], team_abbreviations[was_index] = team_abbreviations[was_index], team_abbreviations[wsb_index]
    team_name_map = dict(zip(team_names, team_abbreviations))

    # Replaces the team_records team names with the abbreviations
    cleaned_team_record_names = []
    for team_name in team_records['team_name']:
        cleaned_team_record_names.append(team_name_map[team_name])
    team_records['team_name'] = cleaned_team_record_names
    
    # Merge together the team_records and player_stats
    merged_df = player_stats.merge(team_records, left_on=['Tm', 'year'], right_on=['team_name', 'year'])

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
    
    Other criteria:
        There has only been one MVP that did not make the playoffs
        (Handled earlier) Players who have been traded while the season was ongoing has never won MVP

    """
    merged_df = pd.read_csv(merged_save_path / 'uncleaned_merged.csv')
    merged_df = merged_df[merged_df.playoffs == True]
    merged_df = merged_df[merged_df.G > 49]
    merged_df = merged_df[merged_df.PTS > 13.8]
    merged_df = merged_df[merged_df.FGA > 10.9]
    merged_df = merged_df[merged_df.TRB > 3.3]
    merged_df = merged_df[merged_df.AST > 1.3]
    merged_df = merged_df[merged_df['FG%'] > 0.378]
    merged_df = merged_df[merged_df.MP > 30.4]

    # Player name cleanup
    player_names = []
    for pname in merged_df['Player']:
        pname = pname.replace('*', '')
        pname = pname.rstrip()
        player_names.append(pname)

    # Replacing "null" values to keep things consistent
    merged_df['Player'] = player_names
    merged_df['GB'].replace('—', '0', inplace=True)
    merged_df['GB'] = pd.to_numeric(merged_df['GB'])

    # Dropping low-information columns
    merged_df.drop(columns=['Rk', 'playoffs', 'team_name'], inplace=True)


    merged_df.to_csv(merged_save_path / 'player_data.csv', index=False)

merge_pstats_team_records()
clean_merged_df()