import numpy as np
import pandas as pd
from pathlib import Path
import pickle

import matplotlib.pyplot as plt

from sklearn.svm import SVR
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import ElasticNet
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import AdaBoostRegressor
from sklearn.ensemble import GradientBoostingRegressor

from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score

model_path = Path('models')

def get_metrics(y_test: pd.Series, y_pred: np.array, metrics_df: pd.DataFrame, model: str, year: int):
    """
    Obtains metrics for given model
    Args:
        y_test: actual y data
        y_pred: predicted y data
        metrics_df: overall metrics dataframe for all models
        model: name of the model
        year: the year tested
    Returns:
        metrics_df: the overall metrics dataframe for all the models so far, 
                    with a row representing the new data added.
    """
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    dict_metrics = {'Model': [model],
                    'Year': [year],
                    'RMSE': [rmse],
                    'R2': [r2]}
    
    curr_metrics = pd.DataFrame(data=dict_metrics)
    metrics_df = pd.concat([metrics_df, curr_metrics])

    return metrics_df

def display_mvp_race_results(actual: pd.Series, predicted: np.array, model: str, player_names: list):
    display_df_actual = pd.DataFrame()
    display_df_pred = pd.DataFrame()
    actual = list(actual)
    for i in range(len(actual)):
        mvp_shares_actual = {'Player (Actual)': [player_names[i]],
                             'MVP Share (Actual)': [actual[i]],
                            }
        mvp_shares_pred = {f'Player ({model})': [player_names[i]],
                           f'MVP Share ({model})': [predicted[i]]
                           }
        
        curr_race_actual = pd.DataFrame(data=mvp_shares_actual)
        display_df_actual = pd.concat([display_df_actual, curr_race_actual])

        curr_race_pred = pd.DataFrame(data=mvp_shares_pred)
        display_df_pred = pd.concat([display_df_pred, curr_race_pred])

    display_df_actual = display_df_actual.sort_values('MVP Share (Actual)', ascending=False)
    display_df_pred = display_df_pred.sort_values(f'MVP Share ({model})', ascending=False)
    
    display_df = pd.concat([display_df_actual.head(3), display_df_pred.head(3)], axis=1)
    print(display_df.head(3))

def svm_model(data: pd.DataFrame, metrics_df: pd.DataFrame, years_to_test: list):
    """
    Training a SVM regressor
    
    Args:
        data: the cleaned player data found earlier
        metrics_df: the overall metrics dataframe for all the metrics found so far in each model
        years_to_test: a list of years to test against
    Returns:
        metrics_df: the overall metrics dataframe for all the models so far, including the metrics 
                    for each year in years_to_test
    """
    for test_year in years_to_test:
        train = data[data['year'] != test_year]
        test = data[data['year'] == test_year]

        player_names = list(test['player'])

        X_tr = train.drop(columns=['mvp_share', 'mvp_rank', 'first_place_votes', 'year', 'player'])
        y_tr = train['mvp_share']

        X_te = test.drop(columns=['mvp_share', 'mvp_rank', 'first_place_votes', 'year', 'player'])
        y_te = test['mvp_share']

        scaler = StandardScaler()
        X_tr = scaler.fit_transform(X_tr)
        X_te = scaler.transform(X_te)

        param_grid = {'C': [0.001,0.01,0.1,0.5,1,2,5],
                      'kernel': ['linear','rbf', 'poly'],
                      'gamma': ['scale','auto'],
                      'degree': [2,3,4],
                      'epsilon': [0.1,0.5,1]
                      }

        svr_model = SVR()
        grid = GridSearchCV(svr_model, param_grid)
        grid.fit(X_tr, y_tr)
        model = SVR(**grid.best_params_)
        model.fit(X_tr, y_tr)
        y_pred = model.predict(X_te)

        print(grid.best_params_)

        plt.scatter(list(range(len(y_pred))), y_pred, label='predicted')
        plt.scatter(list(range(len(y_te))), y_te, label='actual')
        plt.legend()
        plt.title('Support Vector Regression')
        plt.show()

        metrics_df = get_metrics(y_te, y_pred,  metrics_df, 'SVR', test_year)
        display_mvp_race_results(y_te, y_pred, 'SVR', player_names)

        with open(model_path / f'SVM_{years_to_test}.dat', 'wb') as f:
           pickle.dump(model, f)
    
    return metrics_df


def random_forest_model(data: pd.DataFrame, metrics_df: pd.DataFrame, years_to_test: list):
    """
    """
    for test_year in years_to_test:
        train = data[data['year'] != test_year]
        test = data[data['year'] == test_year]

        player_names = list(test['player'])

        X_tr = train.drop(columns=['mvp_share', 'mvp_rank', 'first_place_votes', 'year', 'player'])
        y_tr = train['mvp_share']

        X_te = test.drop(columns=['mvp_share', 'mvp_rank', 'first_place_votes', 'year', 'player'])
        y_te = test['mvp_share']

        scaler = StandardScaler()
        X_tr = scaler.fit_transform(X_tr)
        X_te = scaler.transform(X_te)

        param_grid = {'n_estimators': [15,25,50,64,100,150,200],
                      'max_features': [2,3,4,5],
                      'bootstrap': [True, False],
                      'oob_score': [True]
                     }
        
        rfc = RandomForestRegressor()
        grid = GridSearchCV(rfc, param_grid)
        grid.fit(X_tr, y_tr)
        model = RandomForestRegressor(**grid.best_params_)
        model.fit(X_tr, y_tr)
        y_pred = model.predict(X_te)

        print(grid.best_params_)

        plt.scatter(list(range(len(y_pred))), y_pred, label='predicted')
        plt.scatter(list(range(len(y_te))), y_te, label='actual')
        plt.legend()
        plt.title('Random Forest')
        plt.show()

        metrics_df = get_metrics(y_te, y_pred,  metrics_df, 'Random Forest', test_year)
        display_mvp_race_results(y_te, y_pred, 'Random Forest', player_names)

        with open(model_path / f'random_forest_{years_to_test}.dat', 'wb') as f:
           pickle.dump(model, f)
    
    return metrics_df

def elastic_net_model(data: pd.DataFrame, metrics_df: pd.DataFrame, years_to_test: list):
    """
    """
    for test_year in years_to_test:
        train = data[data['year'] != test_year]
        test = data[data['year'] == test_year]
        
        player_names = list(test['player'])

        X_tr = train.drop(columns=['mvp_share', 'mvp_rank', 'first_place_votes', 'year', 'player'])
        y_tr = train['mvp_share']

        X_te = test.drop(columns=['mvp_share', 'mvp_rank', 'first_place_votes', 'year', 'player'])
        y_te = test['mvp_share']

        scaler = StandardScaler()
        X_tr = scaler.fit_transform(X_tr)
        X_te = scaler.transform(X_te)

        param_grid = {'alpha':[0.01,0.1,1.,5.,10.,50.,100.],
                      'l1_ratio':[0.01,0.1,0.5,0.7,0.95,0.99,1]
                      }

        en_model = ElasticNet()
        grid = GridSearchCV(en_model, param_grid)
        grid.fit(X_tr, y_tr)
        model = ElasticNet(**grid.best_params_)
        model.fit(X_tr, y_tr)
        y_pred = model.predict(X_te)

        print(grid.best_params_)

        plt.scatter(list(range(len(y_pred))), y_pred, label='predicted')
        plt.scatter(list(range(len(y_te))), y_te, label='actual')
        plt.legend()
        plt.title('ElasticNet')
        plt.show()

        metrics_df = get_metrics(y_te, y_pred,  metrics_df, 'ElasticNet', test_year)
        display_mvp_race_results(y_te, y_pred, 'ElasticNet', player_names)
        with open(model_path / f'elastic_net_{years_to_test}.dat', 'wb') as f:
           pickle.dump(model, f)
    
    return metrics_df

def adaboost_model(data: pd.DataFrame, metrics_df: pd.DataFrame, years_to_test: list):
    """
    """
    for test_year in years_to_test:
        train = data[data['year'] != test_year]
        test = data[data['year'] == test_year]

        player_names = list(test['player'])

        X_tr = train.drop(columns=['mvp_share', 'mvp_rank', 'first_place_votes', 'year', 'player'])
        y_tr = train['mvp_share']

        X_te = test.drop(columns=['mvp_share', 'mvp_rank', 'first_place_votes', 'year', 'player'])
        y_te = test['mvp_share']

        scaler = StandardScaler()
        X_tr = scaler.fit_transform(X_tr)
        X_te = scaler.transform(X_te)

        param_grid = {'n_estimators': [5,10,20,30,40,50,100],
                       'learning_rate': [0.01,0.05,0.1,0.2,0.5]}

        ada_model = AdaBoostRegressor()
        grid = GridSearchCV(ada_model, param_grid)
        grid.fit(X_tr, y_tr)
        model = AdaBoostRegressor(**grid.best_params_)
        model.fit(X_tr, y_tr)
        y_pred = model.predict(X_te)

        print(grid.best_params_)

        plt.scatter(list(range(len(y_pred))), y_pred, label='predicted')
        plt.scatter(list(range(len(y_te))), y_te, label='actual')
        plt.legend()
        plt.title('AdaBoost')
        plt.show()

        metrics_df = get_metrics(y_te, y_pred,  metrics_df, 'AdaBoost', test_year)
        display_mvp_race_results(y_te, y_pred, 'AdaBoost', player_names)

        with open(model_path / f'adaboost_{years_to_test}.dat', 'wb') as f:
           pickle.dump(model, f)
    
    return metrics_df

def gradientboost_model(data: pd.DataFrame, metrics_df: pd.DataFrame, years_to_test: list):
    for test_year in years_to_test:
        train = data[data['year'] != test_year]
        test = data[data['year'] == test_year]

        player_names = list(test['player'])

        X_tr = train.drop(columns=['mvp_share', 'mvp_rank', 'first_place_votes', 'year', 'player'])
        y_tr = train['mvp_share']

        X_te = test.drop(columns=['mvp_share', 'mvp_rank', 'first_place_votes', 'year', 'player'])
        y_te = test['mvp_share']

        scaler = StandardScaler()
        X_tr = scaler.fit_transform(X_tr)
        X_te = scaler.transform(X_te)

        param_grid = {'n_estimators': [10,20,30,40,50],
                      'learning_rate': [0.01,0.05,0.1,0.2,0.5],
                      'max_depth': [3,4,5]}

        grad_model = GradientBoostingRegressor()
        grid = GridSearchCV(grad_model, param_grid)
        grid.fit(X_tr, y_tr)
        model = GradientBoostingRegressor(**grid.best_params_)
        model.fit(X_tr, y_tr)
        y_pred = model.predict(X_te)

        print(grid.best_params_)

        plt.scatter(list(range(len(y_pred))), y_pred, label='predicted')
        plt.scatter(list(range(len(y_te))), y_te, label='actual')
        plt.legend()
        plt.title('GradientBoost')
        plt.show()

        metrics_df = get_metrics(y_te, y_pred,  metrics_df, 'GradientBoost', test_year)
        display_mvp_race_results(y_te, y_pred, 'GradientBoost', player_names)
        with open(model_path / f'gradboost_{years_to_test}.dat', 'wb') as f:
           pickle.dump(model, f)
    
    return metrics_df
