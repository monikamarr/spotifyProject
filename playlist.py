import spotipy
from dotenv import dotenv_values
import openai
import json
import argparse

config = dotenv_values(".env")

openai.api_key = config["openai_api_key"]

parser = argparse.ArgumentParser(description="Single command line playlist utility")

parser.add_argument("-p", type=str, default="happy songs", help="The prompt to retrieve names of songs")
parser.add_argument("-n", type=int, default=3, help="The prompt to retrieve number of songs")


args = parser.parse_args()


def get_playlist(prompt, count=3):
    example_json = """
    [
        {"song": "Psycho Killer", "by": "Talking Heads"},
        {"song": "Glass Onion", "by": "The Beatles"},
        {"song": "White Wedding", "by": "Billy Idol"}
    ]
        """
    messages = [
        {"role": "system", "content": """Generate a list of songs to listen based on a text prompt.
        Return a JSON array where each element follows this format: {"song": <song_title>, "by": <by>. Absolutely do not include anything before or after your JSON response}
        """},
        {"role": "user", "content": "Genrate a list of 3 Spotify songs based on this prompt: super sad songs. absolutely do not include anything before or after your JSON response!"},
        {"role": "assistant", "content": example_json},
        {"role": "user", "content": f"Generate a list of {count} songs based on this prompt: {prompt}. absolutely do not include anything before or after your JSON response!"},
    ]
    response = openai.ChatCompletion.create(
        messages=messages,
        model="gpt-3.5-turbo",
        max_tokens=200
    )
    playlist = json.loads(response["choices"][0]["message"]["content"])
    return playlist


# playlist = get_playlist(args.p, 2)
playlist = get_playlist(args.p, 3)
print(playlist)

project = spotipy.Spotify(
    auth_manager=spotipy.SpotifyOAuth(
        client_id=config["spotify_client_id"],
        client_secret=config["spotify_client_secret"],
        redirect_uri="http://localhost:8080",
        scope="playlist-modify-private"
    )
)

current_user = project.current_user()
track_id = []
# print(current_user)
assert current_user is not None

for item in playlist:
    by, song = item["by"], item["song"]
    query = f"{song} {by}"
    result = project.search(q=query, type="track", limit=10)
    # id of the first search found -- list
    track_id.append(result["tracks"]["items"][0]["id"])


create_playlist = project.user_playlist_create(
    current_user["id"],
    public=False,
    name=args.p
)

project.user_playlist_add_tracks(current_user["id"], create_playlist["id"], track_id)