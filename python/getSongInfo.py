import logging
import spotipy
import spotipy.util as util

import requests
from io import BytesIO
from PIL import Image

def getSongInfo(username, token_path):
  scope = 'user-read-currently-playing'
  token = util.prompt_for_user_token(username, scope, cache_path=token_path)

  if token:
      sp = spotipy.Spotify(auth=token)
      result = sp.current_user_playing_track()
    
      if result is None:
         #print("No song playing")
         return [None, None]
      else:
        if result["currently_playing_type"] == "episode":
          return [None,None] # Podcasts don't have cover art available in currently used API
        song = result["item"]["name"]
        imageURL = result["item"]["album"]["images"][0]["url"]
        return [song, imageURL]
  else:
      print("Can't get token for", username)
      return None
  
