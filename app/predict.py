from orm_model import Song
import pandas as pd
from sklearn.linear_model import LinearRegression
import pickle
import sqlite3

con = sqlite3.connect("spotify_db.sqlite3") # DB
cur = con.cursor()

target = 'is_recommended' # The target variable is whether or not the song should be recommended or not

user_selected_songs_db = cur.execute("SELECT * FROM Song;") # All of the songs entered in by the user through the app

train = pd.DataFrame(user_selected_songs_db, columns=[ # Renaming the columns, because importing the sqlite3 database simply names them '1...2...3...4...'
    'id', 'name', 'energy', 'key', 'loudness', 'mode',
    'speechiness', 'acousticness', 'instrumentalness',
    'liveness', 'valence', 'tempo'
])

train = train[[ # Reordering columns to match testing data
    'name', 'id', 'acousticness',
    'energy', 'tempo', 'instrumentalness', 'key', 'liveness',
    'loudness', 'mode', 'valence', 'speechiness']]

train['is_recommended'] = 1 # The songs that the user has entered in *are* recommended. We train a model using their songs, then predict "is_recommended" for the big dataset with 160K songs (test)

master_song_db = cur.execute("SELECT * FROM data;") # 'data' is a table with 160K existing songs

test = pd.DataFrame(master_song_db, columns=[ # Renaming columns
    'name', 'id', 'acousticness', 'danceability', 'duration_ms',
    'energy', 'tempo', 'instrumentalness', 'key', 'liveness',
    'loudness', 'mode', 'valence', 'speechiness'
])
test['is_recommended'] = pd.Series() # Create a blank 'is_recommended' column for our test dataset

X_train = train.drop(columns=[target, 'name', 'id']) # Drop high cardinality columns? Not sure, was erroring out so this is something I tried.
y_train = train[target]
X_test = test.drop(columns=[target, 'duration_ms', 'danceability']) # Drop target and also the columns we don't have in our training data
y_test = test[target]

model = LinearRegression()

model.fit(X = X_train, y = y_train)

print(model.score(X_test, y_test))
