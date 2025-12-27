from io import StringIO
import requests
import pandas as pd
import os
from bs4 import BeautifulSoup
import time
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

url = "https://en.wikipedia.org/wiki/List_of_most-streamed_songs_on_Spotify"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}

response = requests.get(url, headers=headers)

tablas = pd.read_html(StringIO(response.text))
df = tablas[0]

df = df[['Rank', 'Song', 'Artist(s)', 'Streams (billions)', 'Release date']]

df = tablas[0][['Rank', 'Song', 'Artist(s)', 'Streams (billions)', 'Release date']].copy()

df.columns = ['rank', 'song', 'artist', 'streams', 'release_date']

df['streams'] = (
    df['streams']
    .astype(str)
    .str.extract(r'(\d+\.?\d*)')
    .astype(float)
)

df = df.dropna(subset=['streams'])
df = df[df['rank'].str.isnumeric()]
df['rank'] = df['rank'].astype(int)



conn = sqlite3.connect("spotify.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS most_streamed_songs (
    rank INTEGER,
    song TEXT,
    artist TEXT,
    streams REAL,
    release_date TEXT
)
""")

for _, row in df.iterrows():
    cursor.execute("""
    INSERT INTO most_streamed_songs (rank, song, artist, streams, release_date)
    VALUES (?, ?, ?, ?, ?)
    """, (
        int(row["rank"]),
        row["song"],
        row["artist"],
        float(row["streams"]),
        row["release_date"]
    ))
conn.commit()
conn.close()

print("datos Guardados")

top10 = df.sort_values(by="streams", ascending=False).head(10)

plt.figure()
plt.barh(top10["song"], top10["streams"])
plt.xlabel("streams (billions)")
plt.ylabel("Las mejores 10")
plt.gca().invert_yaxis()
plt.show()


df['artist'].value_counts().head(10).plot(kind='bar')

plt.hist(df["streams"], bins=10)
plt.xlabel("Streams (billions)")
plt.ylabel("Cantidad de canciones")
plt.show()
