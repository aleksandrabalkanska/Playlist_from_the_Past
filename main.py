from bs4 import BeautifulSoup
import spotipy
import requests
import os

CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = "http://127.0.0.1:8888/callback"
BILLBOARD_URL = "https://www.billboard.com/charts/hot-100"

# Authenticate Spotify and Get User Info

sp = spotipy.Spotify(
    auth_manager=spotipy.SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope="playlist-modify-private",
        cache_path="token.txt"
    )
)

user_id = sp.current_user()["id"]


# User Input
DATE = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")


# Get Billboard Song List
response = requests.get(url=f"{BILLBOARD_URL}/{DATE}")

billboard_webpage = response.text
soup = BeautifulSoup(billboard_webpage, "html.parser")

# Featured song
featured_song = soup.find(name="h3", class_="c-title a-no-trucate a-font-primary-bold-s u-letter-spacing-0021 "
                                            "u-font-size-23@tablet lrv-u-font-size-16 u-line-height-125 "
                                            "u-line-height-normal@mobile-max a-truncate-ellipsis u-max-width-245 "
                                            "u-max-width-230@tablet-only u-letter-spacing-0028@tablet",
                          id="title-of-a-story").getText().strip()

featured_artist = soup.find(name="span", class_="c-label a-no-trucate a-font-primary-s lrv-u-font-size-14@mobile-max "
                                                "u-line-height-normal@mobile-max u-letter-spacing-0021 "
                                                "lrv-u-display-block a-truncate-ellipsis-2line u-max-width-330 "
                                                "u-max-width-230@tablet-only u-font-size-20@tablet").getText().strip()

# Get the full list
titles_full_list = soup.find_all(name="h3", class_="c-title a-no-trucate a-font-primary-bold-s u-letter-spacing-0021 "
                                                   "lrv-u-font-size-18@tablet lrv-u-font-size-16 u-line-height-125 "
                                                   "u-line-height-normal@mobile-max a-truncate-ellipsis u-max-width-330"
                                                   " u-max-width-230@tablet-only", id="title-of-a-story")

artists_full_list = soup.find_all(name="span", class_="c-label a-no-trucate a-font-primary-s "
                                                      "lrv-u-font-size-14@mobile-max u-line-height-normal@mobile-max "
                                                      "u-letter-spacing-0021 lrv-u-display-block "
                                                      "a-truncate-ellipsis-2line u-max-width-330 "
                                                      "u-max-width-230@tablet-only")

song_titles = [title.getText().strip() for title in titles_full_list]
song_titles.insert(0, featured_song)
song_artists = [name.getText().strip() for name in artists_full_list]
song_artists.insert(0, featured_artist)

tracks = dict(zip(song_titles, song_artists))

# Search for song URI
song_uris = []
for title, artist in tracks.items():
    song = sp.search(q=f"track:{title}  artist:{artist}", type="track", limit=1, offset=0, market=None)
    try:
        uri = song["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{title} by {artist} is not on Spotify!")


# Create a Playlist
new_playlist = sp.user_playlist_create(
    user_id,
    f"{DATE} Billboard 100",
    public=False,
    collaborative=False,
    description=f"The top 100 songs on Billboard on {DATE}")


playlist_id = new_playlist['id']

# Add Songs to the Playlist
sp.playlist_add_items(playlist_id=playlist_id, items=song_uris, position=None)
