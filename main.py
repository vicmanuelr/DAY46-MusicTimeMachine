from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pprint
import time
import os

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REDIRECT_URL = "https://localhost:8888/callback"
# -------------------------- WEB SCRAPING -----------------------------------------#


date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")
URL = f"https://www.billboard.com/charts/hot-100/{date}/"
year = int(date.split("-")[0])

response = requests.get(URL)
response.raise_for_status()
web_html = response.text

soup = BeautifulSoup(web_html, "html.parser")

name_results = soup.select(selector=("div ul li ul li h3"))
song_names = [result.text.strip() for result in name_results]

artist_results = soup.select(selector=("span.c-label.a-no-trucate.a-font-primary-s"))
artists = [song.text.strip() for song in artist_results]


# -------------------------- SPOTIFY PLAYLIST CREATION -----------------------------------------#

# Authenticating via oauth
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, scope="playlist-modify-private", redirect_uri=REDIRECT_URL,
                                 show_dialog=True, cache_path="token.txt"))


user_id = sp.current_user()["id"]

# getting_songs_uri
songs_uri = []
for song in song_names:
    try:
        uri = sp.search(q=f"{song} year:{year-1}-{year}", type="track", limit=1)["tracks"]["items"][0]["uri"]
        time.sleep(1)
    except KeyError:
        pass
    except IndexError:
        pass
    else:
        songs_uri.append(uri)


# creating the playlist
new_playlist = sp.user_playlist_create(user=user_id, name=f"Top 100 Billboard {date}", public="false", description=f"Hot-100 songs by billboard week {date}")
playlist_id = new_playlist["id"]
sp.playlist_add_items(playlist_id=playlist_id, items=songs_uri)