from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth

CLIENT_ID = "**********************************"
CLIENT_SECRET = "*******************************"


# Scraping Billboard 100
date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")


response = requests.get("https://www.billboard.com/charts/hot-100/" + date)
soup = BeautifulSoup(response.text, 'html.parser')


# List of songs
song_list_raw = soup.select(selector="div ul li ul li h3")
song_list = []
for s in range(99):
    song_list.append(song_list_raw[s].getText().replace('\n', ''))


# List of artists
span_class = "c-label a-no-trucate a-font-primary-s lrv-u-font-size-14@mobile-max u-line-height-normal@mobile-max u-letter-spacing-0021 lrv-u-display-block a-truncate-ellipsis-2line u-max-width-330 u-max-width-230@tablet-only"
artist_list_raw = soup.select(selector="div ul li ul li span", class_=span_class)
artist_list = []
for a in range(0, 700, 7):
    '''
    I know this is not great code, kind of creative haha. The output I got from web-scraping (soup.select above), the artists were every 7 lines apart . This was my solution (to iterate every 7 lines), and works. If someone is reading this, maybe you have a better solution? 
    '''
    artist_list.append(artist_list_raw[a].getText().replace('\n', ''))



# Zip songs and artists
songs_artists = list(zip(song_list, artist_list))


# Spotify Authentication
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri="http://localhost:8888/callback",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        show_dialog=True,
        cache_path="token.txt"
    )
)
user_id = sp.current_user()["id"]
print(user_id)


# Searching Spotify for songs by TITLE AND ARTIST!
song_uris = []
for n in range(99):
    result = sp.search(q=f"track:{songs_artists[n][0]} artist:{songs_artists[n][1]}", type="track")  #
    print(result)
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{songs_artists[n][0]} doesn't exist in Spotify. Skipped.")


# Creating a new private playlist in Spotify
playlist = sp.user_playlist_create(user=user_id, name=f"{date} Billboard 100", public=False)
print(playlist)

# Adding songs found into the new playlist
sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)


print(songs_artists)
