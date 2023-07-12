import pandas as pd
from model import *
from pathlib import Path

def main():
    # Testing 2023
    player_data = pd.read_csv(Path('data') / 'merged' / 'player_data.csv')

    seasons_to_test = [2022]
    metrics_df = pd.DataFrame()

    metrics_df = SVM_model(player_data, metrics_df, seasons_to_test)
    max_idx = metrics_df['RMSE'].idxmax()
    print(metrics_df.iloc[max_idx])



if __name__ == '__main__':
    main()