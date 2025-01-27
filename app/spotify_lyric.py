# -*- coding: utf-8 -*-
"""spotify_lyric.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1XhHnvU6VTMXzKvGQG9pkv1oSyaHAHK9v
"""

#Loveline Toussaint
#In addition to song picker, 
#this is an example of using data analytic systems to observe
#verbose commanilities within lyrics.
#Playlists can be build based on lyric or word sequence similarities.

pip install lyricsgenius

pip install squarify

pip install spotipy

import pandas as pd
import  spotipy
import numpy as np
from spotipy.oauth2 import SpotifyClientCredentials
import lyricsgenius
pd.options.display.max_columns =120

genius = lyricsgenius.Genius("BUkmtTfW3vA3IXWyxDyRUc4IHLKMq2LciCMZ-2B47lCx5Q-fx4q3LIOUIoDEZWCi")

#analyze to find songs based artist, inputed word category ,
# and most popular to from play list
#if popularity more than 60 add to dictionary 
#top 20 popular list (break after 20 items in list)

#Spotify Api to query and search songs:
spot = spotipy.Spotify(auth_manager= SpotifyClientCredentials(client_id= "d23859ad966640b8a5784a9b860a0c15", 
                                                                client_secret ="5d1ff1d3aced430b922ab6bf4e603f87"))

#This function will be used to inquiry the random artist list from user
def getArtistqur():
  artistList =[]
  #Ask user to input at upto ten artists
  for x in range(10):
    print("Insert the name of an artist (up to ten)")
    uptake = input()
    artistList.append(uptake)
  return artistList

#this function will search through spotify API for most
# popular songs from each artist
#It create a new playlist of the song of the most popular song for each artist

def popularSonglist(artistsLi):
  listIndex = artistsLi.copy()
  topSong = {}
  for x in listIndex:
    best = spot.search(q=x, limit =1)
    for idx, track in enumerate(best['tracks']['items']):
      topSong[x] = [track['name'], track['popularity']]
  return topSong;

playlist = popularSonglist(getArtistqur())

playlist

#create bar graph of top ten playlist

topSixxr = pd.DataFrame(playlist.items(),columns = ['Artist', 'Popularity'])
topSixxr

list_popu =[]
for x in playlist:
  list_popu.append(playlist[x][1])

fig,ax = plt.subplots(figsize =(11,11))
plt.bar(playlist.keys(),list_popu, color =['blue','green'])
ax.set_title('Artist Popularity based on top Song')
ax.set_xlabel('Artist')
ax.set_ylabel('Popularity')

#function to tokenize for lyric similarity
#tokenize and look for lyric similarities within playlist 
#than append top 5 songs on popularity

#next function will take the songs on the list
#get the lyrics of the songs
#and compare the similarities within the lyrics of the songs on top6 lists

import matplotlib.pyplot as plt
import seaborn as sns

import spacy 
from spacy.tokenizer import Tokenizer
import en_core_web_sm
from collections import Counter
import pandas as pd
import squarify

nlp = en_core_web_sm.load()
stop_list = list(nlp.Defaults.stop_words)

def lyricCompariable(songDict):
  dicSong = songDict.copy()
  lyricDoc =[]
  tokens_noStop =[]
  for xc in dicSong:
    artist=xc
    song_title = dicSong[artist][0]
    lyric_song= genius.search_song(song_title,artist)
    lyric_ryme = lyric_song.lyrics #we will tokenize
    lymric =nlp(lyric_ryme)
    lyricDoc.append([artist, lymric])
    for token in lymric:
       if(token.is_stop == False) & (token.is_punct == False):
          tokens_noStop.append(token.text.lower())
       tokens_dict = Counter(tokens_noStop)
       tokens_wc = pd.DataFrame(list(tokens_dict.items()), columns= ['words', 'count'])
       tokens_wc['rank'] = tokens_wc['count'].rank(method ='first', ascending = False)
       total = tokens_wc['count'].sum()
       tokens_wc['pct_total'] = tokens_wc['count'].apply(lambda x: (x/total)*100)
    print(artist)
    print(tokens_wc.head(15))
    squarify.plot(sizes = tokens_wc['pct_total'], label=tokens_wc['words'], alpha = 1)
    plt.axis('off')
    plt.figure(figsize=(10,15))
    plt.show()
    plt.clf()

lyricCompariable(playlist)

#then neural LSTM of lyrics of top popular song

lyric = genius.search_song(playlist["JCole"][0],'JCole')
lymr = lyric.lyrics

lymr
lymr = lymr.replace('\r\n',' ')

sonrs = list(set(lymr))
char_int = {c: i for i, c in enumerate(sonrs)}
int_char = {i: c for i, c in enumerate(sonrs)}
print('The number of unique chararcters in the lyric: ', len(sonrs))

maxlen = 50
step = 5
encoded = [char_int[c] for c in lymr]
sequnce =[]
next_char = []

for i in range(0, len(encoded) - maxlen, step):
  sequnce.append(encoded[i: i +maxlen])
  next_char.append(encoded[i + maxlen])
print('Sequences: ', len(sequnce))

import tensorflow as tf
from tensorflow.keras.preprocessing import sequence
seq = tf.keras.preprocessing.sequence.pad_sequences(sequnce,maxlen = 50)
import numpy as numy

x = numy.zeros((len(sequnce),maxlen,len(sonrs)), dtype = numy.bool)
y = numy.zeros((len(sequnce), len(sonrs)), dtype = numy.bool)

for i, seqence in enumerate(sequnce):
    for t, char in enumerate(seqence):
        x[i,t,char] = 1

    y[i, next_char[i]] = 1

from keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM
from tensorflow.keras.layers import Bidirectional, Embedding

model = Sequential()
model.add(Embedding(output_dim = 64, input_dim = len(sonrs)))
model.add(Bidirectional(LSTM(64)))
model.add(Dense(len(sonrs), activation = 'softmax'))

model.compile(loss = 'categorical_crossentropy', optimizer = 'adam')

model.fit(seq, y, batch_size = 32,
          epochs = 5, verbose = 2)

def generate_text(model, seed, length):

  encoded = [char_int[c] for c in seed]

  generated = ''
  generated += seed
  model.reset_states()

  start_index = 0 

  for _ in range(length):

      sample = encoded[start_index:start_index+10]      
      sample = np.array(sample)
      sample = np.expand_dims(sample,0)

      pred = model.predict(sample)
      pred = tf.squeeze(pred, 0)
      next_char = np.argmax(pred)
      encoded.append(next_char)
      generated += int_char[next_char]

      start_index += 1

  return generated

seed_text = lymr[0:150]
#A portion of the lyrics was used to apply within the function to 
#predict, or generate the lyrics

generate_text(model,seed_text,500)