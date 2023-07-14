import pandas as pd
from model import *
from pathlib import Path

def main():
    """
    Trains all models to predict on a list of years and saves the model locally
    """
    player_data = pd.read_csv(Path('data') / 'merged' / 'player_data.csv')

    seasons_to_test = [2022]
    metrics_df = pd.DataFrame()

    metrics_df = svm_model(player_data, metrics_df, seasons_to_test)
    metrics_df = random_forest_model(player_data, metrics_df, seasons_to_test)
    metrics_df = elastic_net_model(player_data, metrics_df, seasons_to_test)
    metrics_df = adaboost_model(player_data, metrics_df, seasons_to_test)
    metrics_df = gradientboost_model(player_data, metrics_df, seasons_to_test)

    print(metrics_df)



if __name__ == '__main__':
    main()