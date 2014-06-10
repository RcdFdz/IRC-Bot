import httplib2
import os
import sys
import urllib
import urllib2
import json

from threading import Thread
from time import sleep
from apiclient.discovery import build
from apiclient.errors import HttpError
import oauth2client.client
from oauth2client.file import Storage
from oauth2client.tools import argparser, run

CLIENT_ID = \
    '457076916341-ef3993fg95uq0l73dqjgenjeeaf4ncod.apps.googleusercontent.com'
CLIENT_SECRET = 'CgabyarFxqZl4xjXGlRBXeiV'

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account.

YOUTUBE_SCOPE = 'https://www.googleapis.com/auth/youtube'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

def sendPost(values, url):
    req = urllib2.Request(url, urllib.urlencode(values))
    res = urllib2.urlopen(req)
    file = open('./credentials_token.json', 'w+')
    print >> file, res.read()

def newToken():
    url = 'https://accounts.google.com/o/oauth2/device/code'
    values = {'client_id': CLIENT_ID, 'scope': YOUTUBE_SCOPE}

    req = urllib2.Request(url, urllib.urlencode(values))
    res = urllib2.urlopen(req)

    jRes = json.loads(res.read())

    for i in jRes:
        print i, jRes[i]

    sleep(20)

    res = sendPost({
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': jRes['device_code'],
        'grant_type': 'http://oauth.net/grant_type/device/1.0'
        }, 'https://accounts.google.com/o/oauth2/token')

def refreshCredentials(jsonData):
  url = 'https://accounts.google.com/o/oauth2/token'
  values = {
    'refresh_token': jsonData['refresh_token'],
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'grant_type': 'refresh_token'
    }

  req = urllib2.Request(url, urllib.urlencode(values))
  res = urllib2.urlopen(req)

  return json.loads(res.read())

def get_authenticated_service():
    if not os.path.isfile('credentials_token.json'):
        newToken()

    jsonFile = open('./credentials_token.json')
    jsonStr = str(jsonFile.read())
    jsonData = json.loads(jsonStr)

    jsonData = refreshCredentials(jsonData)

    credentials = \
        oauth2client.client.AccessTokenCredentials(
            jsonData['access_token'],
            'Mozilla/5.0 (X11; Linux x86_64; rv:24.0) Gecko/20140429 Firefox/24.0 Iceweasel/24.5.0'
            )

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                 http=credentials.authorize(httplib2.Http()))


def add_video_to_playlist(youtube, videoID, playlistID):
    add_video_request = youtube.playlistItems().insert(part='snippet',
            body={'snippet': {'playlistId': playlistID,
            'resourceId': {'kind': 'youtube#video',
            'videoId': videoID}}}).execute()
def add_video(video):
  youtube = get_authenticated_service()
  add_video_to_playlist(youtube,video,"PL2IdNrgv1PcmTC4BWvrep-3U3uam1D9Yc")

def existVideo(hash):
  youtube = get_authenticated_service()
  jsonData = json.dumps(youtube.videos().list(part='snippet', id = hash).execute())
  jsonData = json.loads(jsonData)

  return (jsonData['pageInfo']['totalResults'] > 0)

def info_video(hash):
  youtube = get_authenticated_service()
  jsonData = json.dumps(youtube.videos().list(part='snippet', id = hash).execute())
  jsonData = json.loads(jsonData)

  return jsonData['items'][0]['snippet']['title']

if __name__ == '__main__':
  main()
