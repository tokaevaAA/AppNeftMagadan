import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pickle
import plotly.express as px
import sys

from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Ridge
from sklearn.linear_model import ElasticNet
from sklearn.metrics import accuracy_score
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor

import warnings
warnings.filterwarnings('ignore')

print("hello")

complexity_columns = ['X', 'Y', 'Z', 'NTG', 'Number_of_intervals', 'Lateral_Heterogenity']
scrutiny_columns = ['X', 'Y', 'Z', 'Seismica', 'GIS', 'Kern', 'Fluid', 'Perforation', 'WTA']
grid_std_columns = ['X', 'Y', 'h', 'Column', 'Row']
grid_mean_columns = ['X', 'Y', 'mean', 'Column', 'Row']
std_mean_columns = ['X', 'Y', 'Z', 'std', 'mean']
mean_test_columns = ['X', 'Y', 'Z', 'mean']


def read_file(name, skip, columns):
    """Read file, parse it into pandas dataframe

    :param name: filename
    :param skip: number of rows to skip
    :param columns: column names
    :return: obtained dataframe
    """
    data = pd.read_csv(name, sep=' ', skiprows=skip, header=None)
    data.dropna(axis=1, inplace=True)
    data.columns = columns
    return data

level_of_complexity86_train = read_file("Level_of_complexity_train.txt", 12, complexity_columns)
level_of_scrutiny86_train = read_file("Level_of_scrutiny_train.txt", 15, scrutiny_columns)
std_mean76_train = read_file("ThickEff_wells", 11, std_mean_columns)

grid_std_train = pd.read_csv("Target_std_train.txt", sep=' ', skiprows=20, header=None, names=grid_std_columns)
grid_std_train.drop_duplicates(subset=['X', 'Y'], inplace=True)
grid_mean_train = pd.read_csv("ThickEff_mean", skiprows=20, sep=' ', header=None, names=grid_mean_columns)
grid_mean_train.drop_duplicates(subset=['X', 'Y'], inplace=True)

level_of_complexity25_test = read_file("{}".format(sys.argv[1]), 12, complexity_columns)
level_of_scrutiny25_test = read_file("{}".format(sys.argv[2]), 15, scrutiny_columns)
grid_mean_test = pd.read_csv("{}".format(sys.argv[3]), skiprows=20, sep=' ', header=None, names=grid_mean_columns)


def parse(filename, cols):
    df = pd.read_csv(filename, skiprows=9, sep='\t')
    df = df.applymap(lambda row: row.split(' ')[:4])
    for i, col in enumerate(cols):
        df[col] = df['END HEADER'].apply(lambda row: row[i]).values
    df.drop(columns='END HEADER', inplace=True)
    return df

#mean25_test = parse("App/server/uploads/{}".format(sys.argv[3]), mean_test_columns)


scrutiny_complexity86_train = level_of_scrutiny86_train.merge(level_of_complexity86_train, how='left', on=['X', 'Y', 'Z'])

def interpolate_scrutiny_to_grid(model, params, level_of_scrutiny, X_test):
    """Interpolate [Seismica, GIS, Kern, Fluid, Perforation, WTA, complexities] to grid

    :param model: model to train
    :param params: model parameters grid
    :param level_of_scrutiny: training set containing points and their labels
    :param X_test: test set containing grid of points
    :return: dataframe of grid points and their labels, array of trained models
    """
    df_scrutiny_grid, mas_of_models = X_test.copy(), []
    
    X_train = level_of_scrutiny.iloc[:, [0, 1]]
    for i in range(3, len(level_of_scrutiny.columns)):
        y_train = level_of_scrutiny.iloc[:, i]
        searcher = GridSearchCV(model, params, verbose=1, cv=5)
        searcher.fit(X_train, y_train)
        y_pred = searcher.best_estimator_.predict(X_test)
        mas_of_models.append(searcher.best_params_)
        df_scrutiny_grid[level_of_scrutiny.columns.values[i]] = y_pred

    return df_scrutiny_grid, mas_of_models


model = ElasticNet()
params = {
    'alpha': [1e-2, 1e-1, 1],
    'l1_ratio': [1e-2, 1e-1, 1],
    'normalize': [True]
}

df_features_on_grid_from_grid_mean_train, mas_of_models = interpolate_scrutiny_to_grid(model, params,\
                                                                                       scrutiny_complexity86_train, grid_mean_train.iloc[:, :2])

filename = 'features_to_std.sav'

clf_loaded = pickle.load(open(filename, 'rb'))

scrutiny_complexity25_test = level_of_scrutiny25_test.merge(level_of_complexity25_test, how='left', on=['X', 'Y', 'Z'])

X_train = scrutiny_complexity25_test.iloc[:, [0, 1]]
X_test = grid_mean_test.iloc[:, [0, 1]]

df_features_on_grid_from_grid_mean_test = X_test.copy()

for i in range(3, len(scrutiny_complexity25_test.columns)):
    model = ElasticNet(**mas_of_models[i-3])
    model.fit(X_train, scrutiny_complexity25_test.iloc[:, i])
    y_pred = model.predict(X_test)
    df_features_on_grid_from_grid_mean_test[scrutiny_complexity25_test.columns.values[i]] = y_pred

test = df_features_on_grid_from_grid_mean_test.merge(grid_mean_test, how='inner', on=['X', 'Y']).drop(columns=['Column', 'Row'])
result = clf_loaded.predict(test)

INF = 1e8

def distance(lhs_x, lhs_y, rhs_x, rhs_y):
    return np.sqrt((lhs_x - rhs_x) ** 2 + (lhs_y - rhs_y) ** 2)

def minimum_distance(pts_x, pts_y, pt_x, pt_y):
    answer = INF
    for i in range(len(pts_x)):
        dist = distance(pts_x[i], pts_y[i], pt_x, pt_y)
        if dist < answer:
            answer = dist
    return answer

def get_three_points(pts_x, pts_y, border=10000):
    cur_pts_x, cur_pts_y = [], []
    for i in range(len(pts_x)):
        if minimum_distance(cur_pts_x, cur_pts_y, pts_x[i], pts_y[i]) > border:
            cur_pts_x.append(pts_x[i])
            cur_pts_y.append(pts_y[i])
        if len(cur_pts_x) == 3:
            break
    return cur_pts_x, cur_pts_y


new_df = grid_mean_test
new_df['h_predicted'] = result
fig = plt.figure(figsize=(12,12))
ax1 = fig.add_subplot(211)
ax2 = fig.add_subplot(212)

ax1.scatter(new_df["X"], new_df["Y"], c=new_df["mean"])
ax1.scatter(level_of_complexity25_test['X'], level_of_complexity25_test['Y'], color='red', label='given_wells')
ax1.set_title('Mean_grid_test')
df_three_points = new_df.iloc[new_df['mean'].values.argsort()[::-1],:]
pts_x, pts_y = get_three_points(df_three_points['X'].values, df_three_points['Y'].values)
ax1.scatter(pts_x, pts_y, color='black', label='max mean')
ax1.legend()

for i in range(3):
    ax1.annotate('{}0{}'.format(i + 1, i + 1), (pts_x[i], pts_y[i]))

ax2.scatter(new_df["X"], new_df["Y"], c=new_df["h_predicted"])
ax2.scatter(level_of_complexity25_test['X'], level_of_complexity25_test['Y'], color='red', label='given_wells')
df_three_points = new_df.iloc[result.argsort()[::-1],:]
pts_x, pts_y = get_three_points(df_three_points['X'].values, df_three_points['Y'].values)
ax2.scatter(pts_x, pts_y, color='purple', label='max std')

for i in range(3):
    ax2.annotate('{}R'.format(i + 1), (pts_x[i], pts_y[i]))

ax2.set_title('Std predicted')
ax2.legend()

plt.savefig('result.png')
