import os
import sys
import spotipy
import spotipy.util as util
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

scope = 'user-library-read user-library-modify user-read-playback-state playlist-read-private playlist-modify-private' # Spotify Scopes
scopes = ['https://www.googleapis.com/auth/youtube.readonly'] # YouTube Scopes

if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    print("Usage: %s username" % (sys.argv[0],))
    sys.exit()

CLIENT_ID = 'YOUR CLIENT ID'
CLIENT_SECRET = 'YOUR CLIENT SECRET'
REDIRECT_URI = 'http://localhost:8888/callback'

token = util.prompt_for_user_token(username, scope, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)

if token:
    sp = spotipy.Spotify(auth=token)
    saved_tracks = sp.current_user_saved_tracks()
    playlists = sp.current_user_playlists()

    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    api_service_name = 'youtube'
    api_version = 'v3'
    client_secrets_file = r"PATH TO JSON FILE"

    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)

    request = youtube.playlistItems().list(
        part="snippet,contentDetails",
        maxResults=25,
        playlistId='ID OF PLAYLIST'
    )
    response = request.execute()

    songs = []
    limit = response['pageInfo']['totalResults']

    for song in range(limit):
        songs.append(response['items'][song]['snippet']['title'])

    uris = []

    for i in range(len(songs)):
        song = sp.search(q=songs[i], type='track', limit=1)
        uri = song['tracks']['items'][0]['uri']
        uris.append(uri)

    sp.current_user_saved_tracks_add(uris)
else:
    print("Can't get token for", username)
