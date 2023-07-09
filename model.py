import numpy as np
import pandas as pd
from pathlib import Path
import pickle 

from sklearn.svm import SVR
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import ElasticNet
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import AdaBoostRegressor
from sklearn.ensemble import GradientBoostingRegressor

from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score

years = list(range(1991, 2023))
model_path = Path('models')

def get_metrics(y_test: pd.Series, y_pred: pd.Series, metrics_df: pd.DataFrame, model: str, year: int):
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


def SVM_model(data: pd.DataFrame, metrics_df: pd.DataFrame, years_to_test: list):
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
    num_seasons = 1
    for test_year in years_to_test:
        train = data[data['year'] != test_year]
        test = data[data['year'] == test_year]

        X_tr = train.drop(columns=['mvp_share', 'mvp_rank', 'first_place_votes', 'year'])
        y_tr = train['mvp_share']

        X_te = test.drop(columns=['mvp_share', 'mvp_rank', 'first_place_votes', 'year'])
        y_te = test['mvp_share']

        scaler = StandardScaler()
        X_tr_num = X_tr.select_dtypes(exclude=['object'])
        X_te_num = X_te.select_dtypes(exclude=['object'])

        X_tr[X_tr_num.columns] = scaler.fit_transform(X_tr_num)
        X_te[X_te_num.columns] = scaler.transform(X_te_num)

        encoder = LabelEncoder()
        X_tr_cat = X_tr.select_dtypes(include=['object'])
        categorical_cols = X_tr_cat.columns
        for col in categorical_cols:
            X_tr[col] = encoder.fit_transform(X_tr[col])
            X_te[col] = encoder.fit_transform(X_te[col])

        param_grid = {'C': [0.001,0.01,0.1,0.5,1],
                      'kernel': ['linear','rbf'],
                      'gamma': ['scale','auto'],
                      'degree': [2,3,4],
                      'epsilon': [0.1,0.5,1]
                      }
        
        svr_model = SVR()
        grid = GridSearchCV(svr_model, param_grid, verbose=10)
        grid.fit(X_tr, y_tr)

        print(grid.best_params_)

        model = SVR(**grid.best_params_)
        model.fit(X_tr, y_tr)

        with open(model_path / f'SVM_{years_to_test}.dat', 'wb') as f:
           pickle.dump(model, f)

        y_pred = model.predict(X_te)

        metrics_df = get_metrics(y_te, y_pred, metrics_df, 'SVR', test_year)

    
    return metrics_df
