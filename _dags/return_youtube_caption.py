# -*- coding: utf-8 -*-

# Sample Python code for youtube.captions.insert
# NOTES:
# 1. This sample code uploads a file and can't be executed via this interface.
#    To test this code, you must run it locally using your own API credentials.
#    See: https://developers.google.com/explorer-help/guides/code_samples#python
# 2. This example makes a simple upload request. We recommend that you consider
#    using resumable uploads instead, particularly if you are transferring large
#    files or there's a high likelihood of a network interruption or other
#    transmission failure. To learn more about resumable uploads, see:
#    https://developers.google.com/api-client-library/python/guide/media_upload

import os

import googleapiclient.discovery

from googleapiclient.http import MediaFileUpload

from google.oauth2.credentials import Credentials

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = "YOUR_API_KEY"

jh_key = ""
refresh_token = ""

client_id = ""
client_secret = ""
token_uri = "https://accounts.google.com/o/oauth2/token"
scopes = ""
credentials = Credentials(youtube_auth.auth_token, youtube_auth.refresh_token, client_id=client_id, client_secret=client_secret, token_uri=token_uri)

youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)

yt_video_id = "LX9fmVc-6Ej2Y2jZ81nVAs"
VTTfile = "./{0}_en.vtt".format(yt_video_id)
request = youtube.captions().insert(
    part="snippet",
    access_token=jh_key,
    body={
        "snippet": {
        "language": "en-US",
        "name": "MyApp by MyDomain",
        "videoId": yt_video_id,

        "isDraft": False
        }
    },
    
    # TODO: For this request to work, you must replace "YOUR_FILE"
    #       with a pointer to the actual file you are uploading.
    media_body=MediaFileUpload(VTTfile)
)
response = request.execute()

print(response)